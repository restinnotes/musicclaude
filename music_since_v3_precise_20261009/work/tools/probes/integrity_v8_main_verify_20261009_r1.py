"""Main offline verification; preserve old evidence and permit one exact queue child."""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def install_guard(tools, out):
    allowed, blocked_writes = [], []
    original_popen = subprocess.Popen
    python = Path(sys.executable).resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    queue_script = "import sys;sys.path.insert(0,sys.argv[1]);import execution_integrity_v8 as I;assert not I.queue_open(sys.argv[2])"
    authorization = None

    def valid_vector(argv):
        if not isinstance(argv, (list, tuple)) or len(argv) != 9:
            return False
        if not all(isinstance(value, str) for value in argv):
            return False
        hold = Path(argv[8]).resolve()
        return (Path(argv[0]).resolve() == python
                and list(argv[1:6]) == ["-X", "utf8", "-I", "-B", "-c"]
                and argv[6] == queue_script and Path(argv[7]).resolve() == tools.resolve()
                and hold.name == "queue_hold.json" and hold.parent.name == "provider"
                and hold.parents[2] == temp_root)

    def permitted_write(value):
        if isinstance(value, int):
            return True
        path = Path(os.fsdecode(value)).resolve()
        return path.is_relative_to(out.resolve()) or path.is_relative_to(temp_root)

    def assert_write(value):
        if not permitted_write(value):
            blocked_writes.append("outside_new_output_or_temporary_directory")
            raise RuntimeError("offline probe blocked historical/out-of-scope write")

    def audit(event, args):
        nonlocal authorization
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.bind"):
            raise RuntimeError("offline probe blocked network")
        if event in ("os.system", "os.posix_spawn", "os.posix_spawnp"):
            raise RuntimeError("offline probe blocked shell/spawn")
        if event == "open":
            path, mode, flags = args
            if ((isinstance(mode, str) and any(c in mode for c in "wax+"))
                    or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                assert_write(path)
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
            assert_write(args[0])
        elif event in ("os.rename", "os.link", "os.symlink"):
            assert_write(args[0])
            assert_write(args[1])
        if event != "subprocess.Popen":
            return
        executable, native_args, cwd, env = args
        current, authorization = authorization, None
        if current is None or cwd is not None or env is not None:
            raise RuntimeError("offline probe blocked unauthorized native process")
        vector, native_command = current
        executable_ok = executable is None or Path(executable).resolve() == python
        args_ok = (native_args == native_command if os.name == "nt"
                   else isinstance(native_args, (list, tuple)) and list(native_args) == vector)
        if not executable_ok or not args_ok:
            raise RuntimeError("offline probe blocked native process mismatch")
        allowed.append({"kind": "isolated_local_readonly_queue_check",
                        "vector_and_native_command_verified": True,
                        "native_shape": "windows_command_line" if os.name == "nt" else "argv"})

    class GuardedPopen(original_popen):
        def __init__(self, *args, **kwargs):
            nonlocal authorization
            if (len(args) != 1 or not valid_vector(args[0])
                    or set(kwargs) != {"stdout", "stderr"}
                    or kwargs["stdout"] != subprocess.PIPE or kwargs["stderr"] != subprocess.PIPE):
                raise RuntimeError("offline probe blocked process vector/options")
            if authorization is not None:
                raise RuntimeError("offline probe blocked overlapping process authorization")
            vector = list(args[0])
            authorization = (vector, subprocess.list2cmdline(vector))
            try:
                super().__init__(*args, **kwargs)
            finally:
                authorization = None

    sys.addaudithook(audit)
    subprocess.Popen = GuardedPopen
    return allowed, blocked_writes, original_popen, queue_script


def guard_negatives(tools, original_popen, queue_script, root):
    rows = []
    with tempfile.TemporaryDirectory() as temp:
        valid = [sys.executable, "-X", "utf8", "-I", "-B", "-c", queue_script,
                 str(tools), str(Path(temp) / "provider/queue_hold.json")]
        wrong = valid.copy()
        wrong[0] = "FICTIONAL_MODEL_CLI"
        changed_script = valid.copy()
        changed_script[6] = "raise SystemExit(0)"
        no_isolation = valid.copy()
        no_isolation[3] = "-u"
        changed_hold = valid.copy()
        changed_hold[8] = str(Path(temp) / "provider/different.json")
        cases = [
            ("model_cli_vector_blocked", lambda: subprocess.Popen(wrong, stdout=subprocess.PIPE, stderr=subprocess.PIPE)),
            ("different_python_script_blocked", lambda: subprocess.Popen(changed_script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)),
            ("missing_isolation_blocked", lambda: subprocess.Popen(no_isolation, stdout=subprocess.PIPE, stderr=subprocess.PIPE)),
            ("different_hold_shape_blocked", lambda: subprocess.Popen(changed_hold, stdout=subprocess.PIPE, stderr=subprocess.PIPE)),
            ("shell_option_blocked", lambda: subprocess.Popen(valid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)),
            ("direct_native_bypass_blocked", lambda: original_popen(valid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)),
            ("historical_report_write_blocked", lambda: (root / "notes/research/integrity_v8_luna_impl_20261009_r1/queue_child_run.json").open("wb")),
        ]
        for name, invoke in cases:
            try:
                result = invoke()
            except RuntimeError:
                rows.append({"check": name, "passed": True, "spawned": False})
            else:
                if isinstance(result, original_popen):
                    result.kill()
                    result.communicate()
                else:
                    result.close()
                rows.append({"check": name, "passed": False})
    return rows


class QueueReportParent:
    def __init__(self, out):
        self.out = out

    def __truediv__(self, relative):
        if relative != "notes/research/integrity_v8_luna_impl_20261009_r1":
            raise RuntimeError("unexpected test report locator")
        return self.out


class TestToolsLocator:
    """Only __str__ and the one report-parent expression occur in the frozen test."""
    def __init__(self, tools, out):
        self.tools = tools
        self.parent = QueueReportParent(out)

    def __str__(self):
        return str(self.tools)


@contextlib.contextmanager
def case_fixture(cls):
    case = cls("runTest")
    case.setUp()
    try:
        yield case
    finally:
        case.doCleanups()


def adapter_challenges(f):
    I, A, E = f.I, f.A, f.E
    rows = []
    with case_fixture(f.GPT2ExperimentGapTests) as case:
        calls = []

        def safe_then_success(argv, **kwargs):
            calls.append(list(argv))
            if len(calls) > 1:
                return subprocess.CompletedProcess(argv, 0, f.payload(), b"")
            prompt = Path(argv[argv.index("--file") + 1])
            pending = I._read_json_object(prompt.parent.parent / "pending" / (prompt.stem + ".json"), "mock pending")
            identity = pending["request_identity"]
            proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                     "provider_error_type": "ProviderError", "phase": "pre_submit", "retryable": True,
                     "ambiguous": False, "submit_callback_reached": False, "model_request_sent": False,
                     "automatic_retry": False, "request_identity_sha256": I.identity_digest(identity),
                     "producer_identity_sha256": I.identity_digest(identity["producer"]),
                     "source_files": identity["producer"]["active_provider_sources"]["files"]}
            body = {"completed": False, "automatic_retry": False, "phase": "pre_submit",
                    "error_code": "headless_runner_or_evidence_failed", "model_request_sent": False,
                    "pre_submit_proof": proof}
            return subprocess.CompletedProcess(argv, 1, b"", json.dumps(body).encode("utf-8"))

        case.process.side_effect = safe_then_success
        out = case.root / "through-adapter"
        args = (out, "why", "MOCK_ONLY", "gpt56w", "same frozen synthetic input",
                lambda text: ({"value": text}, None), [2], "v8-main-through-adapter")
        first = E.call(*args)
        artifacts = {p.relative_to(out).as_posix(): sha(p.read_bytes()) for p in out.rglob("*")
                     if p.is_file() and p.name != "cache_why_exact.json"}
        second = E.call(*args)
        after = {p.relative_to(out).as_posix(): sha(p.read_bytes()) for p in out.rglob("*")
                 if p.is_file() and p.name != "cache_why_exact.json"}
        metas = [I._read_json_object(p, "test meta") for p in sorted((out / "meta").glob("*.json"))]
        rows.append({"check": "source_bound_transport_through_actual_adapter_mock_then_disk_reuse",
                     "passed": first["parse_ok"] and second["parse_ok"] and len(first["attempts"]) == 2
                     and len(calls) == 2 and first["new_model_submissions"] == 1
                     and second["new_model_submissions"] == 0 and artifacts == after
                     and len({m["request_identity"]["sampling_key"] for m in metas}) == 1
                     and I.queue_open(A.HOLD_FILE),
                     "mock_cli_process_calls": len(calls), "first_new_model_submissions": first["new_model_submissions"],
                     "second_new_model_submissions": second["new_model_submissions"],
                     "same_sampling_identity": len({m["request_identity"]["sampling_key"] for m in metas}) == 1,
                     "immutable_artifacts_unchanged": artifacts == after})
    with case_fixture(f.V8RegressionTests) as case:
        meta, identity = case._valid_pre_submit()
        envelope = {"completed": False, "automatic_retry": False, "phase": "pre_submit",
                    "error_code": "headless_runner_or_evidence_failed", "model_request_sent": False,
                    "pre_submit_proof": meta["pre_submit_proof"]}
        for field in ("retryable", "ambiguous", "submit_callback_reached", "model_request_sent", "automatic_retry"):
            altered = json.loads(json.dumps(envelope))
            altered["pre_submit_proof"][field] = int(altered["pre_submit_proof"][field])
            rows.append({"check": "adapter_rejects_integer_proof_" + field,
                         "passed": A.pre_submit_payload(altered, identity) is False})
        for budget in (1, 3, 4, 2.0, True):
            target = case.root / ("invalid-budget-" + str(budget))
            try:
                E.call(target, "why", "MOCK_ONLY", "gpt56w", "synthetic input", lambda text: (None, "bad"),
                       [2], "v8-exact2", max_attempts=budget, allow_new_sample_on_parse_failure=True,
                       new_sample_reason="mock-only explicit reason", new_sampling_key="second")
            except ValueError:
                rejected = True
            else:
                rejected = False
            rows.append({"check": "exact2_optin_budget_reject_" + repr(budget),
                         "passed": rejected and not target.exists() and case.provider_process.call_count == 0
                         and case.runner_process.call_count == 0, "no_output_directory_created": not target.exists()})
    return rows


def worker(root, out, mode):
    tools = root / "tools"
    allowed, blocked, original, script = install_guard(tools, out)
    sys.path.insert(0, str(tools))
    f = load(tools / "tests/test_execution_integrity_v8.py", "main_v8_fixtures")
    if f.I.REAL_EXECUTION_APPROVED is not False:
        raise RuntimeError("persistent real gate not closed")
    negatives = guard_negatives(tools, original, script, root)
    data = {"guard_negative_checks": negatives}
    if mode == "suite":
        f.TOOLS = TestToolsLocator(tools, out)
        suite = unittest.defaultTestLoader.loadTestsFromModule(f)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        data.update(tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                    was_successful=result.wasSuccessful(),
                    report_locator_seam="process-local TOOLS proxy: real child tools path unchanged; only exact report-parent expression redirects to this new output directory")
    else:
        base = load(Path(__file__).with_name("integrity_v7_main_verify_20261009_r2.py"), "retained_main_challenges")
        data["checks"] = base.challenges(f) + adapter_challenges(f)
        data["was_successful"] = all(row["passed"] for row in data["checks"])
    data.update(local_readonly_queue_children=allowed, blocked_write_count=len(blocked),
                real_gate_after=f.I.REAL_EXECUTION_APPROVED, real_model_submissions=0, model_cli_invocations=0,
                music_acceptance="NOT_PERFORMED", limit="Finite isolated mock evidence; not backend attestation or production acceptance.")
    print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    expected_children = 1 if mode == "suite" else 0
    return 0 if (data["was_successful"] and f.I.REAL_EXECUTION_APPROVED is False
                 and all(row["passed"] for row in negatives) and len(allowed) == expected_children
                 and len(blocked) == 1) else 1


def assertion_mapping(root):
    def inventory(version):
        source = (root / ("tools/tests/test_execution_integrity_" + version + ".py")).read_text(encoding="utf-8")
        found = {}
        for cls in ast.parse(source).body:
            if isinstance(cls, ast.ClassDef):
                for node in cls.body:
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                        calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                                 and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                                 and n.func.value.id == "self" and n.func.attr.startswith("assert")]
                        found[cls.name + "." + node.name] = {"line": node.lineno,
                            "ast": ast.dump(node, include_attributes=False),
                            "assertions": [ast.dump(n, include_attributes=False) for n in calls]}
        return found
    old, prior, current = inventory("v4"), inventory("v7"), inventory("v8")
    mappings = []
    for version, original in (("v4", old), ("v7", prior)):
        rows = []
        for name, before in sorted(original.items()):
            after = current.get(name)
            normalize = lambda text: text.replace("execution_integrity_" + version, "execution_integrity_v8").replace("inflight_" + version, "inflight_v8")
            assertions = [normalize(value) for value in before["assertions"]]
            missing = [value for value in assertions if not after or value not in after["assertions"]]
            rows.append({"test": name, "old_line": before["line"], "v8_line": after["line"] if after else None,
                         "old_assertion_count": len(assertions), "v8_assertion_count": len(after["assertions"]) if after else 0,
                         "old_assertions_not_retained": missing,
                         "body_same_after_namespace": bool(after and normalize(before["ast"]) == after["ast"]),
                         "limit": "AST/expressions only; changed fixture or test body still requires semantic review."})
        mappings.append({"source": version, "methods": len(original), "mapping": rows})
    return {"v4_methods": len(old), "v7_methods": len(prior), "v8_methods": len(current), "mappings": mappings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--worker", choices=("suite", "challenges"))
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out_dir.resolve()
    if args.worker:
        return worker(root, out, args.worker)
    out.mkdir(parents=False, exist_ok=False)
    base = load(Path(__file__).with_name("integrity_v7_main_verify_20261009_r2.py"), "retained_main_snapshot")

    def snapshot():
        records = base.source_hashes(root)
        paths = []
        for version in ("v4", "v5", "v6", "v7", "v8"):
            paths += [root / ("tools/" + prefix + "_" + version + ".py")
                      for prefix in ("execution_integrity", "gpt2_adapter", "runner", "experiment_calls")]
            paths.append(root / ("tools/tests/test_execution_integrity_" + version + ".py"))
        for name in ("integrity_v7_luna_impl_20261009_r1", "integrity_v8_luna_impl_20261009_r1",
                     "integrity_v7_main_verify_20261009_r2", "integrity_v7_main_verify_20261009_r3",
                     "integrity_v7_main_verify_20261009_r4"):
            paths.extend(p for p in (root / "notes/research" / name).rglob("*") if p.is_file())
        for path in paths:
            records[path.relative_to(root).as_posix()] = ({"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                                                         if path.is_file() else {"missing": True})
        return records

    before = snapshot()
    save(out / "protected_before.json", before)
    report = {"schema": "integrity-v8-main-isolated-offline/1", "date": "2026-10-09", "commands": [],
              "assertion_mapping": assertion_mapping(root), "music_acceptance": "NOT_PERFORMED", "production_ready": False,
              "independent_review": "PENDING", "real_gate_changed": False, "two_w_hold_changed": False}
    claimed = json.loads((root / "notes/research/integrity_v8_luna_impl_20261009_r1/report.json").read_bytes())
    report["source_hash_parity"] = {relative: {"matches": expected == sha((root / relative).read_bytes())}
                                    for relative, expected in claimed["implementation"]["source_sha256"].items()}
    report["implementation_artifact_hash_parity"] = {
        relative: {"matches": expected == sha((root / relative).read_bytes())}
        for relative, expected in claimed["report_artifact_sha256"].items()}
    protected_before = json.loads((root / claimed["protected_before_after"]["before_file"]).read_bytes())
    protected_after = json.loads((root / claimed["protected_before_after"]["after_file"]).read_bytes())
    before_index = {row["path"]: row for row in protected_before["files"]}
    protected_rows = []
    for row in protected_after["files"]:
        path, original = root / row["path"], before_index.get(row["path"])
        protected_rows.append({"path": row["path"], "before_baseline_available": original is not None,
            "baseline_fields_match": bool(original and original["exists"] == row["before_exists"]
                                         and original["sha256"] == row["before_sha256"]),
            "after_internal_matches": row["before_exists"] == row["after_exists"] and row["before_sha256"] == row["after_sha256"],
            "current_matches_after": row["after_exists"] == path.is_file()
                and (not path.is_file() or row["after_sha256"] == sha(path.read_bytes()))})
    report["agent_protected_schema_aware"] = {"before_rows": len(protected_before["files"]),
        "after_rows": len(protected_after["files"]), "after_unique_paths": len({r["path"] for r in protected_after["files"]}),
        "rows": protected_rows, "limit": "Additional after-only entries have no contemporaneous before baseline; duplicate entries do not count as distinct protected files."}
    incident = json.loads((root / "notes/research/integrity_v8_luna_impl_20261009_r1/scope_incident.json").read_bytes())
    report["scope_incident"] = {"currently_out_of_root_file_exists": Path(incident["out_of_root_generated_file"]).exists(),
                               "cleanup_is_implementation_report_not_main_action": True,
                               "historical_creation_and_cleanup_scope_independently_verified": False}
    for mode in ("suite", "challenges"):
        worker_out = out / mode
        worker_out.mkdir()
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(Path(__file__).resolve()),
                "--root", str(root), "--out-dir", str(worker_out), "--worker", mode]
        start = time.monotonic()
        try:
            cp = subprocess.run(argv, cwd=root.parent.parent, capture_output=True, timeout=180)
            stdout, stderr, rc, timed_out = cp.stdout, cp.stderr, cp.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, rc, timed_out = exc.stdout or b"", exc.stderr or b"", None, True
        for name, raw in (("stdout", stdout), ("stderr", stderr)):
            with (out / (mode + "." + name + ".txt")).open("xb") as stream:
                stream.write(raw)
        command = {"mode": mode, "argv": argv, "returncode": rc, "timed_out": timed_out,
                   "elapsed_seconds": round(time.monotonic() - start, 3), "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
                   "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)}
        try:
            command["result"] = json.loads(stdout.decode("utf-8"))
        except (ValueError, UnicodeError):
            command["result_parse_error"] = True
        report["commands"].append(command)
    after = snapshot()
    save(out / "protected_after.json", after)
    report["protected_unchanged"] = before == after
    report["changed_protected_paths"] = [p for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    report["main_disposition"] = "OFFLINE_DYNAMIC_CHECKS_RECORDED_NOT_ACCEPTED_PENDING_INDEPENDENT_REVIEW_AND_REAL_CONTRACTS"
    report["limits"] = ["Synthetic/source-bound consistency is not remote authentication.",
                        "Real CLI event/proof producer, remote normalization, private configuration and external service remain unverified.",
                        "Scope incident historical cleanup is not independently established; schema-aware agent protection counts are limited.",
                        "No music or production acceptance."]
    save(out / "report.json", report)
    print(json.dumps({"commands": report["commands"], "protected_unchanged": before == after,
                      "disposition": report["main_disposition"]}, ensure_ascii=False, allow_nan=False))
    return 0 if before == after and all(c["returncode"] == 0 and not c["timed_out"] for c in report["commands"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
