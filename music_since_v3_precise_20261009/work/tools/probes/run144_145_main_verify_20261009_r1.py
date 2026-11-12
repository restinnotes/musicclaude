"""Main-session finite offline verification. No provider, model CLI, or network."""
from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
import shutil
import socket
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


def guard(out):
    blocked = {"process": 0, "network": 0, "write": 0}
    original = subprocess.Popen
    def writable(value):
        return isinstance(value, int) or Path(os.fsdecode(value)).resolve().is_relative_to(out.resolve())
    def audit(event, args):
        if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp"):
            blocked["process"] += 1
            raise RuntimeError("offline verification blocked every child/native process")
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.bind"):
            blocked["network"] += 1
            raise RuntimeError("offline verification blocked network")
        paths = []
        if event == "open":
            path, mode, flags = args
            if ((isinstance(mode, str) and any(c in mode for c in "wax+")) or
                    flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                paths = [path]
        elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"):
            paths = [args[0]]
        elif event in ("os.rename", "os.link", "os.symlink"):
            paths = list(args[:2])
        if any(not writable(path) for path in paths):
            blocked["write"] += 1
            raise RuntimeError("offline verification blocked historical/out-of-scope write")
    class BlockedPopen(original):
        def __init__(self, *args, **kwargs):
            blocked["process"] += 1
            raise RuntimeError("offline verification blocked every process vector")
    sys.addaudithook(audit)
    subprocess.Popen = BlockedPopen
    return blocked, original


def negatives(root, original):
    rows = []
    cases = [
        ("model_cli_blocked", lambda: subprocess.Popen(["FICTIONAL_MODEL_CLI"])),
        ("isolated_python_still_blocked", lambda: subprocess.Popen([sys.executable, "-I", "-B", "-c", "pass"])),
        ("native_popen_bypass_blocked", lambda: original([sys.executable, "-I", "-B", "-c", "pass"])),
        ("shell_blocked", lambda: os.system("FICTIONAL_MODEL_CLI")),
        ("network_dns_blocked", lambda: socket.getaddrinfo("offline.invalid", 443)),
        ("historical_report_write_blocked", lambda: (root / "notes/research/run144_145_luna_impl_20261009_r1/report.json").open("wb")),
    ]
    for name, invoke in cases:
        try:
            result = invoke()
        except RuntimeError:
            rows.append({"check": name, "passed": True})
        else:
            if isinstance(result, original):
                result.kill()
                result.communicate()
            elif hasattr(result, "close"):
                result.close()
            rows.append({"check": name, "passed": False})
    return rows


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []
    def addSuccess(self, test):
        self.rows.append({"test": test.id(), "status": "PASS"})
        super().addSuccess(test)
    def addFailure(self, test, err):
        self.rows.append({"test": test.id(), "status": "FAIL"})
        super().addFailure(test, err)
    def addError(self, test, err):
        self.rows.append({"test": test.id(), "status": "ERROR"})
        super().addError(test, err)


def receipt145_challenges(f, root):
    g = f.GO
    template_path = root / g["TEMPLATE_PATHS"]["ident"]
    pack = g["build_ident_musepack"](template_path.read_text(encoding="utf-8"),
        "MOCK_ONLY exact statement", 19, "ident:main-type-negative", sha(template_path.read_bytes()))
    output = json.dumps({"guess": "说不准", "confidence": 50, "also_fits": [],
        "why": "“MOCK_ONLY exact statement” is a synthetic citation."}, ensure_ascii=False)
    raw = output.encode("utf-8")
    identity = pack["requested_identity"]
    receipt = {"receipt_schema": "muse_archive_receipt_v1", "attestation_class": "TEST_ONLY",
        "verified": True, "bytes_verified": True, "source_bound": True,
        "task_id": pack["task_id"], "logical_task_id": pack["logical_task_id"], "request_id": pack["request_id"],
        "target": pack["target"], "source_sha256": pack["source"]["sha256"],
        "template_sha256": pack["template"]["sha256"], "mapping_sha256": g["sha256_text"](g["canonical_json"](pack["mapping"])),
        "seed": pack["seed"], "prompt_sha256": pack["prompt_sha256"], "raw_response_sha256": sha(raw),
        "raw_response_size": len(raw), "terminal_status": "completed", "terminal_id": "TEST_ONLY_main_terminal",
        "requested_provider": identity["provider"], "requested_model": identity["model"],
        "requested_transport": identity["transport"], "reported_provider": identity["provider"],
        "reported_model": identity["model"], "reported_transport": identity["transport"],
        "actual_provider": identity["provider"], "actual_model": identity["model"], "actual_transport": identity["transport"]}
    result = {"task_id": pack["task_id"], "logical_task_id": pack["logical_task_id"], "request_id": pack["request_id"],
        "provider": "Muse", "model": "external Muse", "transport": "mcp", "raw_response": output}
    rows = []
    for field, value in [(None, None)] + [(key, value) for key in ("verified", "bytes_verified", "source_bound") for value in (1, 1.0)]:
        changed = dict(receipt)
        if field:
            changed[field] = value
        try:
            normalized = g["validate_muse_return"](pack, result, lambda _pack, _raw: changed)
            accepted, error = True, None
        except g["IntegrityError"] as exc:
            accepted, error, normalized = False, str(exc), None
        rows.append({"check": "run145_receipt_positive" if field is None else "run145_receipt_exact_bool_" + field + "_" + repr(value),
            "passed": accepted if field is None else not accepted, "accepted": accepted,
            "mutation_field": field, "mutation_value": value, "exception": error,
            "full_ingestion_entry": "validate_muse_return", "real_return_count": normalized.get("real_return_count") if normalized else None,
            "limit": "Injected TEST_ONLY verifier receipt; no actual service attestation or model invocation."})
    return rows


def receipt144_challenges(f, out):
    cls = f.Run144Tests
    cls.setUpClass()
    try:
        g, captured = cls.go, {}
        original = g.validate_external_review_results
        def capture(pack, results, expected_model, transport_verifier=None):
            if not captured and callable(transport_verifier):
                cloned = copy.deepcopy(results)
                receipts = {}
                for index, result in enumerate(results):
                    paths = {key: Path(value) for key, value in result["artifacts"].items()}
                    meta = g.read_json(paths["meta"])
                    terminal = g.read_json(paths["terminal"])
                    receipts[result["task_id"]] = transport_verifier(result, meta, terminal, paths["output"].read_bytes())
                    folder = out / "preserved_fixture" / str(index)
                    folder.mkdir(parents=True)
                    for key, source in paths.items():
                        destination = folder / source.name
                        shutil.copyfile(source, destination)
                        cloned[index]["artifacts"][key] = str(destination)
                captured.update(pack=copy.deepcopy(pack), results=cloned, model=expected_model, receipts=receipts)
            return original(pack, results, expected_model, transport_verifier)
        case = cls("test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections")
        with mock.patch.object(g, "validate_external_review_results", side_effect=capture):
            case.test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections()
        case.doCleanups()
        rows = []
        for field, value in [(None, None)] + [(key, value) for key in ("verified", "source_bound") for value in (1, 1.0)]:
            receipts = copy.deepcopy(captured["receipts"])
            if field:
                for receipt in receipts.values():
                    receipt[field] = value
            def verifier(result, _meta, _terminal, _raw):
                return receipts[result["task_id"]]
            try:
                normalized = original(captured["pack"], captured["results"], captured["model"], verifier)
                accepted, error = True, None
            except g.IntegrityError as exc:
                accepted, error, normalized = False, str(exc), None
            rows.append({"check": "run144_receipt_positive" if field is None else "run144_receipt_exact_bool_" + field + "_" + repr(value),
                "passed": accepted if field is None else not accepted, "accepted": accepted,
                "mutation_field": field, "mutation_value": value, "exception": error,
                "full_ingestion_entry": "validate_external_review_results", "normalized_rows": len(normalized) if normalized else 0,
                "all_real_return_counts_zero": bool(normalized and all(row["real_return_count"] == 0 for row in normalized)),
                "limit": "Injected TEST_ONLY verifier receipts; no actual service attestation or model invocation."})
        return rows
    finally:
        cls.tearDownClass()


def worker(root, out, mode):
    scratch = out / "scratch"
    scratch.mkdir()
    tempfile.tempdir = str(scratch)
    blocked, original = guard(out)
    negative = negatives(root, original)
    f144 = load(root / "tools/tests/test_run144_e7_flash_diag_r5.py", "main_run144_fixtures")
    f145 = load(root / "tools/tests/test_run145_thread_resume_r5.py", "main_run145_fixtures")
    data = {"schema": "run144145-main-worker/1", "guard_negatives": negative, "mode": mode,
        "real_model_submissions": 0, "provider_or_model_cli_invocations": 0, "music_acceptance": "NOT_PERFORMED"}
    if mode == "suites":
        captured = []
        original_mock = f145.GO["run_mock"]
        def observe(*args, **kwargs):
            result = original_mock(*args, **kwargs)
            captured.append({key: result[key] for key in ("first_run_mock_submissions", "second_run_reused", "second_run_new_submissions",
                "nlv_match_tasks_first_run", "nlv_match_tasks_reverified_second_run", "center_match_lineage_count",
                "musepack_count", "ident_pair_count", "compare_pair_count", "music_acceptance")})
            return result
        f145.GO["run_mock"] = observe
        suites = []
        for module in (f144, f145):
            result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(unittest.defaultTestLoader.loadTestsFromModule(module))
            suites.append({"module": module.__name__, "tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "was_successful": result.wasSuccessful(), "tests": result.rows})
        data.update(suites=suites, run144_first_full_mock_submissions=f144.Run144Tests.first_result["new_mock_submissions"],
            run145_observed_full_mock=captured, was_successful=all(row["was_successful"] for row in suites))
    elif mode == "challenges":
        checks = receipt145_challenges(f145, root) + receipt144_challenges(f144, out)
        data.update(checks=checks, was_successful=all(row["passed"] for row in checks),
            disposition="Record malformed-receipt false accepts as findings; do not weaken expectations.")
    else:
        go144 = load(root / "runs/run144_e7_flash_diag_r5/go.py", "main_preflight144")
        stdout = []
        import io
        for label, callback, expected in (("run144_real", lambda: go144.main(["--real"]), 3),
            ("run145_strict", lambda: f145.GO["main"](["--strict"]), 0),
            ("run145_real", lambda: f145.GO["main"](["--real"]), 3)):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                rc = callback()
            raw = stream.getvalue().encode("utf-8")
            (out / (label + ".stdout.bin")).open("xb").write(raw)
            stdout.append({"label": label, "returncode": rc, "expected_returncode": expected, "passed": rc == expected,
                "stdout_sha256": sha(raw), "stdout_bytes": len(raw)})
        data.update(preflights=stdout, was_successful=all(row["passed"] for row in stdout))
    data["guard_blocked_counts"] = blocked
    data["guard_scope"] = "Python audit hook plus class-preserving process block; finite mock protection, not OS sandbox or malicious native-code containment."
    save(out / "worker_report.json", data)
    print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    return 0 if data["was_successful"] and all(row["passed"] for row in negative) and blocked == {"process": 4, "network": 1, "write": 1} else 1


def snapshot(root):
    base = load(Path(__file__).with_name("integrity_v7_main_verify_20261009_r2.py"), "main_protected_snapshot")
    rows = base.source_hashes(root)
    before = json.loads((root / "notes/research/run144_145_luna_impl_20261009_r1/protected_before.json").read_bytes())
    paths = [root / path for path in before["fixed_protected_files"]]
    for directory in ("run141_thread_resume_r3", "run142_e7_flash_diag_r4", "run143_thread_resume_r4", "run144_e7_flash_diag_r5", "run145_thread_resume_r5"):
        paths.extend(p for p in (root / "runs" / directory).rglob("*") if p.is_file())
    for version in ("v4", "v5", "v6", "v7", "v8"):
        paths.extend(root / ("tools/" + prefix + "_" + version + ".py") for prefix in ("execution_integrity", "gpt2_adapter", "runner", "experiment_calls"))
        paths.append(root / ("tools/tests/test_execution_integrity_" + version + ".py"))
    paths.extend(root / ("tools/tests/test_run" + number + "_" + rest + ".py") for number, rest in (("144", "e7_flash_diag_r5"), ("145", "thread_resume_r5")))
    paths.extend(p for p in (root / "notes/research/run144_145_luna_impl_20261009_r1").rglob("*") if p.is_file())
    for path in paths:
        rows[path.relative_to(root).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha(path.read_bytes())} if path.is_file() else {"missing": True}
    return rows


def evidence_parity(root):
    directory = root / "notes/research/run144_145_luna_impl_20261009_r1"
    rows, manifests = [], []
    for attempt in sorted(directory.glob("attempt-*/commands.json")):
        commands = json.loads(attempt.read_bytes())
        if isinstance(commands, dict):
            commands = commands.get("commands", [])
        for command in commands:
            for channel in ("stdout", "stderr"):
                path = attempt.parent / command[channel + "_file"]
                raw = path.read_bytes()
                rows.append({"attempt": attempt.parent.name, "command": command["label"], "channel": channel,
                    "matches": sha(raw) == command[channel + "_sha256"] and len(raw) == command[channel + "_bytes"],
                    "returncode": command["returncode"], "timed_out": command["timed_out"]})
    for directory_name, test_name in (("run144_e7_flash_diag_r5", "test_run144_e7_flash_diag_r5.py"),
            ("run145_thread_resume_r5", "test_run145_thread_resume_r5.py")):
        manifest = json.loads((root / "runs" / directory_name / "manifest.json").read_bytes())
        artifacts = manifest["artifacts"]
        expected = {"runs/" + directory_name + "/go.py": artifacts["go_py_sha256"],
            "runs/" + directory_name + "/README.md": artifacts["readme_sha256"],
            "tools/tests/" + test_name: artifacts["test_py_sha256"], **manifest["frozen_input_sha256"]}
        manifests.append({"run": directory_name, "checks": [{"path": path, "matches": sha((root / path).read_bytes()) == digest} for path, digest in expected.items()]})
    old = json.loads((directory / "protected_before.json").read_bytes())
    after = json.loads((directory / "protected_after.json").read_bytes())
    pairs = {key: old[key] == after[key] for key in ("fixed_protected_files", "old_run_inventories", "presence_only_probes")}
    current = []
    for path, value in after["fixed_protected_files"].items():
        p = root / path
        actual = {"present": True, "sha256": sha(p.read_bytes()), "size": p.stat().st_size} if p.is_file() else {"present": False}
        current.append({"path": path, "matches": actual == value})
    return {"attempt_log_checks": rows, "manifest_checks": manifests, "implementation_protected_before_after": pairs,
        "implementation_protected_fixed_current": current,
        "limit": "Current disk/log hashes and recorded before/after comparisons; not service authentication or proof of unrecorded historical actions."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--worker", choices=("suites", "challenges", "preflight"))
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out_dir.resolve()
    if args.worker:
        return worker(root, out, args.worker)
    out.mkdir(parents=False, exist_ok=False)
    before = snapshot(root)
    save(out / "protected_before.json", before)
    report = {"schema": "run144145-main-isolated-offline/1", "date": "2026-10-09", "probe_sha256": sha(Path(__file__).read_bytes()),
        "evidence_parity": evidence_parity(root), "commands": [], "music_acceptance": "NOT_PERFORMED", "production_ready": False,
        "independent_review": "PENDING_AT_PROBE_CREATION", "real_gate_changed": False, "two_w_hold_changed": False}
    for mode in ("suites", "challenges", "preflight"):
        child_out = out / mode
        child_out.mkdir()
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(Path(__file__).resolve()), "--root", str(root), "--out-dir", str(child_out), "--worker", mode]
        started = time.monotonic()
        try:
            completed = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
            raw_out, raw_err, rc, timed = completed.stdout, completed.stderr, completed.returncode, False
        except subprocess.TimeoutExpired as exc:
            raw_out, raw_err, rc, timed = exc.stdout or b"", exc.stderr or b"", None, True
        (child_out / "stdout.bin").open("xb").write(raw_out)
        (child_out / "stderr.bin").open("xb").write(raw_err)
        row = {"mode": mode, "argv": argv, "returncode": rc, "timed_out": timed, "elapsed_seconds": round(time.monotonic() - started, 3),
            "stdout_sha256": sha(raw_out), "stderr_sha256": sha(raw_err), "stdout_bytes": len(raw_out), "stderr_bytes": len(raw_err)}
        path = child_out / "worker_report.json"
        if path.is_file():
            row["result"] = json.loads(path.read_bytes())
        report["commands"].append(row)
    after = snapshot(root)
    save(out / "protected_after.json", after)
    report["protected_unchanged"] = before == after
    report["changed_protected_paths"] = [path for path in sorted(set(before) | set(after)) if before.get(path) != after.get(path)]
    report["main_disposition"] = "OBSERVED_RESULTS_REQUIRE_MAIN_REVIEW; FAILURES_RETAINED; NO_REAL_OR_MUSIC_ACCEPTANCE"
    save(out / "report.json", report)
    print(json.dumps({"output": str(out), "commands": [{key: row[key] for key in ("mode", "returncode", "timed_out", "elapsed_seconds")} for row in report["commands"]],
        "protected_unchanged": report["protected_unchanged"], "production_ready": False}, ensure_ascii=False))
    return 0 if before == after and all(row["returncode"] == 0 for row in report["commands"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
