"""Main-session isolated offline verification; providers and network stay blocked."""
from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


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


def source_hashes(root):
    relatives = [
        "tools/execution_integrity.py", "tools/execution_integrity_v3.py",
        "tools/execution_integrity_v4.py", "tools/execution_integrity_v5.py",
        "tools/execution_integrity_v6.py", "tools/execution_integrity_v7.py",
        "tools/gpt2_adapter_v7.py", "tools/runner_v7.py", "tools/experiment_calls_v7.py",
        "tools/runner.py", "tools/tests/test_execution_integrity_v4.py",
        "tools/tests/test_execution_integrity_v7.py", "CLAUDE.md", "notes/ACTIVE_HANDOFF.md",
        "runs/run124_render/surface__B__gpt56w__op60.md",
        "reference/PRODUCT_CONSTITUTION_V2.md",
        "notes/chat_findings_20261005/music_pipeline_chat_findings_20261005/06_ACCEPTANCE_CRITERIA.md",
    ]
    for directory in (root / "prompts", root / "runs/_call_slots"):
        if directory.is_dir():
            relatives.extend(path.relative_to(root).as_posix()
                             for path in directory.rglob("*") if path.is_file())
    records = {}
    for relative in sorted(set(relatives)):
        path = root / relative
        records[relative] = ({"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())}
                             if path.is_file() else {"missing": True})
    return records


def install_worker_guard(tools):
    allowed = []
    python_path = Path(sys.executable).resolve()
    queue_script = ("import sys;sys.path.insert(0,sys.argv[1]);"
                    "import execution_integrity_v7 as I;assert not I.queue_open(sys.argv[2])")

    def guard(event, args):
        if event.startswith("socket.") and event in (
                "socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.bind"):
            raise RuntimeError("offline probe blocked network operation")
        if event in ("os.system", "os.posix_spawn", "os.posix_spawnp"):
            raise RuntimeError("offline probe blocked external shell/spawn")
        if event != "subprocess.Popen":
            return
        executable, argv, _, _ = args
        permitted = (
            isinstance(argv, (list, tuple)) and len(argv) == 8
            and Path(executable).resolve() == python_path
            and Path(argv[0]).resolve() == python_path
            and list(argv[1:4]) == ["-B", "-I", "-c"]
            and argv[4] == queue_script and Path(argv[5]).resolve() == tools.resolve()
            and Path(argv[6]).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
        )
        # subprocess uses seven arguments here: executable plus six arguments.
        permitted = (
            isinstance(argv, (list, tuple)) and len(argv) == 7
            and Path(executable).resolve() == python_path
            and Path(argv[0]).resolve() == python_path
            and list(argv[1:4]) == ["-B", "-I", "-c"]
            and argv[4] == queue_script and Path(argv[5]).resolve() == tools.resolve()
            and Path(argv[6]).resolve().is_relative_to(Path(tempfile.gettempdir()).resolve())
        )
        if not permitted:
            raise RuntimeError("offline probe blocked non-allowlisted subprocess")
        allowed.append({"kind": "isolated_local_readonly_queue_check", "argv_shape_verified": True})

    sys.addaudithook(guard)
    return allowed


def assertions(root):
    def inventory(path):
        source = path.read_text(encoding="utf-8")
        result = {}
        for cls in ast.parse(source).body:
            if not isinstance(cls, ast.ClassDef):
                continue
            for node in cls.body:
                if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                    continue
                calls = [call for call in ast.walk(node) if isinstance(call, ast.Call)
                         and isinstance(call.func, ast.Attribute)
                         and isinstance(call.func.value, ast.Name)
                         and call.func.value.id == "self" and call.func.attr.startswith("assert")]
                result[cls.name + "." + node.name] = {
                    "line": node.lineno,
                    "assertions": [ast.get_source_segment(source, call) for call in calls],
                    "ast": ast.dump(node, include_attributes=False),
                }
        return result
    old = inventory(root / "tools/tests/test_execution_integrity_v4.py")
    new = inventory(root / "tools/tests/test_execution_integrity_v7.py")
    rows = []
    for name, original in sorted(old.items()):
        current = new.get(name)
        normalized = original["ast"].replace("execution_integrity_v4", "execution_integrity_v7")
        normalized = normalized.replace("inflight_v4", "inflight_v7")
        normalized_assertions = [text.replace("execution_integrity_v4", "execution_integrity_v7")
                                 .replace("inflight_v4", "inflight_v7")
                                 for text in original["assertions"]]
        missing = ([] if current is None else
                   [text for text in normalized_assertions if text not in current["assertions"]])
        if current is None:
            disposition = "MISSING_TEST"
        elif normalized == current["ast"]:
            disposition = "EXACT_AST_AFTER_VERSION_NAMESPACE_SUBSTITUTION"
        elif not missing:
            disposition = "ALL_OLD_ASSERTION_EXPRESSIONS_RETAINED_BODY_CHANGED"
        else:
            disposition = "REQUIRES_EXPLICIT_BEHAVIOR_MAPPING"
        rows.append({"test": name, "old_line": original["line"],
                     "new_line": current["line"] if current else None,
                     "old_assertions": original["assertions"],
                     "new_assertions": current["assertions"] if current else [],
                     "old_assertions_not_textually_retained": missing,
                     "disposition": disposition})
    return {"old_count": len(old), "new_count": len(new), "mapping": rows,
            "limit": "Assertion expressions and AST compare are supporting evidence, not fixture-equivalence or acceptance by themselves."}


def challenges(f):
    I, R, E, A = f.I, f.R, f.E, f.A
    rows = []

    @contextlib.contextmanager
    def fixture(cls=f.RunnerFixture):
        case = cls("runTest")
        case.setUp()
        try:
            yield case
        finally:
            case.doCleanups()

    def artifact_snapshot(folder):
        return {path.relative_to(folder).as_posix(): sha(path.read_bytes())
                for path in folder.rglob("*") if path.is_file()
                and path.name != "cache_why_exact.json"}

    with fixture() as case:
        folder = case.root / "default-stop"
        args = (folder, "why", "MOCK_ONLY", "luna_noweb", "immutable synthetic input",
                lambda text: (None, "synthetic complete parse failure"), [2], "v7-main-fixture")
        first = E.call(*args, max_attempts=2)
        before = artifact_snapshot(folder)
        second = E.call(*args, max_attempts=2)
        rows.append({"check": "complete_parse_failure_same_slot_rerun",
                     "passed": not first["parse_ok"] and not second["parse_ok"]
                     and case.process.call_count == 1 and before == artifact_snapshot(folder),
                     "mock_process_calls": case.process.call_count,
                     "second_new_model_submissions": second["new_model_submissions"],
                     "original_attempt_artifacts_unchanged": before == artifact_snapshot(folder)})

    with fixture() as case:
        folder = case.root / "current-identity"
        args = (folder, "why", "MOCK_ONLY", "luna_noweb", "immutable synthetic input",
                lambda text: ({"value": text}, None), [2], "v7-main-fixture")
        E.call(*args, max_attempts=1)
        before = artifact_snapshot(folder)
        for label, index, value in (("changed_model", 3, "gflash"),
                                    ("changed_version", 7, "different-version")):
            modified = list(args)
            modified[index] = value
            count_before = case.process.call_count
            try:
                E.call(*modified, max_attempts=1)
                rejected, exception = False, None
            except I.ArtifactConflict as exc:
                rejected, exception = True, type(exc).__name__
            rows.append({"check": label, "passed": rejected
                         and case.process.call_count == count_before
                         and before == artifact_snapshot(folder), "rejected": rejected,
                         "exception": exception, "new_mock_process_calls": case.process.call_count - count_before,
                         "attempt_artifacts_unchanged": before == artifact_snapshot(folder)})

    with fixture() as case:
        folder = case.root / "budget-over-limit"
        try:
            result = E.call(folder, "why", "MOCK_ONLY", "luna_noweb", "same frozen synthetic input",
                            lambda text: (None, "synthetic parse failure"), [2], "v7-budget-fixture",
                            max_attempts=3, allow_new_sample_on_parse_failure=True,
                            new_sample_reason="explicit mock-only diagnostic",
                            new_sampling_key="declared-second-sample")
            rejected, exception = False, None
        except ValueError as exc:
            result, rejected, exception = None, True, type(exc).__name__
        rows.append({"check": "explicit_resample_budget_above_two",
                     "contract": "Explicit resample budget must be exact int <= 2, otherwise reject before a process.",
                     "passed": rejected and case.process.call_count == 0,
                     "rejected": rejected, "exception": exception,
                     "mock_process_calls": case.process.call_count,
                     "new_sample_taken": result.get("new_sample_taken") if result else False,
                     "finding": None if rejected else "Budget=3 accepted although the declared explicit-resample contract caps it at 2."})

    with fixture(f.GPT2ExperimentGapTests) as case:
        identity = case._identity()
        producer = identity["producer"]
        proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                 "provider_error_type": "ProviderError", "phase": "pre_submit", "retryable": True,
                 "ambiguous": False, "submit_callback_reached": False, "model_request_sent": False,
                 "automatic_retry": False, "request_identity_sha256": I.identity_digest(identity),
                 "producer_identity_sha256": I.identity_digest(producer),
                 "source_files": producer["active_provider_sources"]["files"]}
        base = {"status": "failed", "failure_phase": "pre_submit", "retry_safe": True,
                "queue_stop": False, "terminal_verified": False,
                "submission_state": "proven_not_submitted", "pre_submit_proof": proof}
        rows.append({"check": "source_bound_proof_positive_mock_control",
                     "passed": I.verify_pre_submit_proof(base, identity),
                     "limit": "Synthetic proof; no actual CLI proof producer was exercised."})
        for key in ("retryable", "ambiguous", "submit_callback_reached", "model_request_sent", "automatic_retry"):
            altered = json.loads(json.dumps(base))
            altered["pre_submit_proof"][key] = int(altered["pre_submit_proof"][key])
            accepted = I.verify_pre_submit_proof(altered, identity)
            rows.append({"check": "integer_in_boolean_proof_" + key,
                         "passed": not accepted, "accepted": accepted,
                         "supplied_type": "int", "finding": "Non-boolean proof flag accepted." if accepted else None,
                         "mock_process_calls": case.process.call_count})

    with fixture() as case:
        folder = case.root / "ambiguous-stop"
        case.process.side_effect = subprocess.TimeoutExpired("mock-provider", 1, output=b"partial")
        args = (folder, "why", "MOCK_ONLY", "luna_noweb", "immutable synthetic input",
                lambda text: ({"value": text}, None), [2], "v7-main-ambiguous")
        first = E.call(*args, max_attempts=2)
        case.process.side_effect = None
        second = E.call(*args, max_attempts=2)
        different = E.call(case.root / "different-run", "why", "OTHER_MOCK", "luna_noweb",
                           "different synthetic input", lambda text: ({"value": text}, None), [3],
                           "v7-main-ambiguous", max_attempts=2)
        rows.append({"check": "ambiguous_hold_blocks_same_and_different_local_run",
                     "passed": first["queue_stop"] and second["queue_stop"]
                     and different["queue_stop"] and case.process.call_count == 1,
                     "mock_process_calls": case.process.call_count,
                     "second_new_model_submissions": second["new_model_submissions"],
                     "different_run_new_model_submissions": different["new_model_submissions"]})

    return rows


def worker(root, mode):
    tools = root / "tools"
    allowed = install_worker_guard(tools)
    sys.path.insert(0, str(tools))
    f = load(tools / "tests/test_execution_integrity_v7.py", "main_v7_fixtures")
    if f.I.REAL_EXECUTION_APPROVED is not False:
        raise RuntimeError("persistent v7 real gate is not closed")
    if mode == "suite":
        suite = unittest.defaultTestLoader.loadTestsFromModule(f)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        data = {"tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "was_successful": result.wasSuccessful()}
    else:
        data = {"checks": challenges(f)}
    if f.I.REAL_EXECUTION_APPROVED is not False:
        raise RuntimeError("mock fixture left the real gate changed")
    data.update(provider_processes="mocked; unallowlisted real spawn blocked by Python audit hook",
                model_cli_invocations=0, real_model_submissions=0,
                local_readonly_queue_children=allowed, real_gate_after=False,
                limit="Local isolated mock evidence, not backend attestation or music acceptance.")
    print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    return 0 if mode != "suite" or data["was_successful"] else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--worker", choices=("suite", "challenges"))
    args = parser.parse_args()
    root = args.root.resolve()
    if args.worker:
        return worker(root, args.worker)
    if args.out_dir is None:
        parser.error("--out-dir is required outside worker mode")
    out = args.out_dir.resolve()
    out.mkdir(parents=False, exist_ok=False)
    before = source_hashes(root)
    save(out / "protected_before.json", before)
    report = {"schema": "integrity-v7-main-isolated-offline/2", "date": "2026-10-09",
              "commands": [], "assertion_mapping": assertions(root),
              "music_acceptance": "NOT_PERFORMED", "production_ready": False,
              "real_gate_changed": False, "two_w_hold_changed": False}
    claimed = json.loads((root / "notes/research/integrity_v7_luna_impl_20261009_r1/report.json").read_bytes())
    report["implementation_claim_parity"] = {
        relative: {"reported_sha256": expected, "current_sha256": sha((root / relative).read_bytes()),
                   "matches": expected == sha((root / relative).read_bytes())}
        for relative, expected in claimed["implementation_sha256"].items()}
    report["agent_stream_hash_parity"] = {
        relative: {"matches": expected == sha((root / "notes/research/integrity_v7_luna_impl_20261009_r1" / relative).read_bytes())}
        for relative, expected in claimed["report_artifact_sha256"].items()}
    for mode in ("suite", "challenges"):
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(Path(__file__).resolve()),
                "--root", str(root), "--worker", mode]
        start = time.monotonic()
        try:
            process = subprocess.run(argv, cwd=root.parent.parent, capture_output=True, timeout=180)
            stdout, stderr, rc, timeout = process.stdout, process.stderr, process.returncode, False
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, rc, timeout = exc.stdout or b"", exc.stderr or b"", None, True
        for name, raw in (("stdout", stdout), ("stderr", stderr)):
            with (out / (mode + "." + name + ".txt")).open("xb") as stream:
                stream.write(raw)
        command = {"mode": mode, "argv": argv, "returncode": rc, "timed_out": timeout,
                   "elapsed_seconds": round(time.monotonic() - start, 3),
                   "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
                   "stdout_sha256": sha(stdout), "stderr_sha256": sha(stderr)}
        try:
            command["result"] = json.loads(stdout.decode("utf-8"))
        except (ValueError, UnicodeError):
            command["result_parse_error"] = True
        report["commands"].append(command)
    after = source_hashes(root)
    save(out / "protected_after.json", after)
    report["protected_unchanged"] = before == after
    report["changed_protected_paths"] = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
    report["main_disposition"] = "NOT_ACCEPTED_PENDING_CONFIRMED_GAPS_AND_INDEPENDENT_REVIEW"
    report["limits"] = ["SHA is local consistency, not remote authentication.",
                        "Real CLI event/proof compatibility and remote input normalization remain unverified.",
                        "Private config, external services, Docker and all three music acceptances remain unverified."]
    save(out / "report.json", report)
    print(json.dumps({"commands": report["commands"], "protected_unchanged": before == after,
                      "disposition": report["main_disposition"]}, ensure_ascii=False, allow_nan=False))
    return 0 if before == after and all(row["returncode"] == 0 and not row["timed_out"] for row in report["commands"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
