"""Repair only the local Windows audit seam; retain the failed r2 evidence."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


BASE_NAME = "integrity_v7_main_verify_20261009_r2.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def install_worker_guard(tools):
    allowed = []
    original_popen = subprocess.Popen
    python_path = Path(sys.executable).resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    queue_script = ("import sys;sys.path.insert(0,sys.argv[1]);"
                    "import execution_integrity_v7 as I;assert not I.queue_open(sys.argv[2])")
    authorization = None

    def valid_vector(argv):
        if not isinstance(argv, (list, tuple)) or len(argv) != 7:
            return False
        if not all(isinstance(value, str) for value in argv):
            return False
        hold = Path(argv[6]).resolve()
        return (Path(argv[0]).resolve() == python_path
                and list(argv[1:4]) == ["-B", "-I", "-c"]
                and argv[4] == queue_script
                and Path(argv[5]).resolve() == tools.resolve()
                and hold.name == "queue_hold.json"
                and hold.parent.name == "provider"
                and hold.parents[2] == temp_root)

    def audit(event, args):
        nonlocal authorization
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.bind"):
            raise RuntimeError("offline probe blocked network operation")
        if event in ("os.system", "os.posix_spawn", "os.posix_spawnp"):
            raise RuntimeError("offline probe blocked external shell/spawn")
        if event != "subprocess.Popen":
            return
        executable, native_args, cwd, env = args
        current = authorization
        authorization = None
        if current is None or cwd is not None or env is not None:
            raise RuntimeError("offline probe blocked unauthorized native subprocess")
        vector, native_command = current
        executable_ok = executable is None or Path(executable).resolve() == python_path
        args_ok = (native_args == native_command if os.name == "nt"
                   else isinstance(native_args, (list, tuple)) and list(native_args) == vector)
        if not executable_ok or not args_ok:
            raise RuntimeError("offline probe blocked mismatched native subprocess")
        allowed.append({"kind": "isolated_local_readonly_queue_check",
                        "vector_and_native_command_verified": True,
                        "native_shape": "windows_command_line" if os.name == "nt" else "argv"})

    def guarded_popen(*args, **kwargs):
        nonlocal authorization
        if (len(args) != 1 or not valid_vector(args[0])
                or set(kwargs) != {"stdout", "stderr"}
                or kwargs["stdout"] != subprocess.PIPE or kwargs["stderr"] != subprocess.PIPE):
            raise RuntimeError("offline probe blocked non-allowlisted subprocess vector/options")
        if authorization is not None:
            raise RuntimeError("offline probe blocked overlapping subprocess authorization")
        vector = list(args[0])
        authorization = (vector, subprocess.list2cmdline(vector))
        try:
            return original_popen(*args, **kwargs)
        finally:
            authorization = None

    sys.addaudithook(audit)
    subprocess.Popen = guarded_popen
    return allowed, original_popen, queue_script


def guard_negatives(tools, original_popen, queue_script):
    rows = []
    with tempfile.TemporaryDirectory() as temp:
        valid = [sys.executable, "-B", "-I", "-c", queue_script, str(tools),
                 str(Path(temp) / "provider/queue_hold.json")]
        cases = []
        wrong = valid.copy()
        wrong[0] = "FICTIONAL_MODEL_CLI"
        cases.append(("model_cli_vector_blocked", lambda: subprocess.Popen(wrong, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        changed_script = valid.copy()
        changed_script[4] = "raise SystemExit(0)"
        cases.append(("different_python_script_blocked", lambda: subprocess.Popen(changed_script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        no_isolation = valid.copy()
        no_isolation[2] = "-u"
        cases.append(("missing_isolation_blocked", lambda: subprocess.Popen(no_isolation, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        changed_hold = valid.copy()
        changed_hold[6] = str(Path(temp) / "provider/different.json")
        cases.append(("different_hold_shape_blocked", lambda: subprocess.Popen(changed_hold, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        cases.append(("shell_option_blocked", lambda: subprocess.Popen(valid, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)))
        cases.append(("direct_native_bypass_blocked", lambda: original_popen(valid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)))
        for name, invoke in cases:
            try:
                process = invoke()
            except RuntimeError:
                rows.append({"check": name, "passed": True, "spawned": False})
            else:
                process.kill()
                process.communicate()
                rows.append({"check": name, "passed": False, "spawned": True})
    return rows


def worker(root):
    tools = root / "tools"
    allowed, original_popen, queue_script = install_worker_guard(tools)
    sys.path.insert(0, str(tools))
    fixture = load(tools / "tests/test_execution_integrity_v7.py", "main_v7_r3_fixtures")
    if fixture.I.REAL_EXECUTION_APPROVED is not False:
        raise RuntimeError("persistent v7 real gate is not closed")
    negatives = guard_negatives(tools, original_popen, queue_script)
    suite = unittest.defaultTestLoader.loadTestsFromModule(fixture)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    gate_closed = fixture.I.REAL_EXECUTION_APPROVED is False
    data = {"tests_run": result.testsRun, "failures": len(result.failures),
            "errors": len(result.errors), "was_successful": result.wasSuccessful(),
            "guard_negative_checks": negatives, "local_readonly_queue_children": allowed,
            "real_gate_after": fixture.I.REAL_EXECUTION_APPROVED,
            "model_cli_invocations": 0, "real_model_submissions": 0,
            "limit": "Finite local audit/mock evidence; not backend attestation or music acceptance."}
    print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    return 0 if (result.wasSuccessful() and gate_closed
                 and all(row["passed"] for row in negatives) and len(allowed) == 1) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.worker:
        return worker(root)
    if args.out_dir is None:
        parser.error("--out-dir is required outside worker mode")
    base = load(Path(__file__).with_name(BASE_NAME), "retained_v7_r2_probe")
    out = args.out_dir.resolve()
    out.mkdir(parents=False, exist_ok=False)
    r2_dir = root / "notes/research/integrity_v7_main_verify_20261009_r2"
    r2_before = {path.name: base.sha(path.read_bytes()) for path in r2_dir.iterdir() if path.is_file()}
    protected_before = base.source_hashes(root)
    base.save(out / "protected_before.json", protected_before)
    r2_report = json.loads((r2_dir / "report.json").read_bytes())
    argv = [sys.executable, "-X", "utf8", "-I", "-B", str(Path(__file__).resolve()),
            "--root", str(root), "--worker"]
    started = time.monotonic()
    try:
        process = subprocess.run(argv, cwd=root.parent.parent, capture_output=True, timeout=180)
        stdout, stderr, rc, timed_out = process.stdout, process.stderr, process.returncode, False
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, rc, timed_out = exc.stdout or b"", exc.stderr or b"", None, True
    for name, raw in (("stdout", stdout), ("stderr", stderr)):
        with (out / ("suite." + name + ".txt")).open("xb") as stream:
            stream.write(raw)
    command = {"argv": argv, "returncode": rc, "timed_out": timed_out,
               "elapsed_seconds": round(time.monotonic() - started, 3),
               "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
               "stdout_sha256": base.sha(stdout), "stderr_sha256": base.sha(stderr)}
    try:
        command["result"] = json.loads(stdout.decode("utf-8"))
    except (ValueError, UnicodeError):
        command["result_parse_error"] = True
    protected_after = base.source_hashes(root)
    base.save(out / "protected_after.json", protected_after)
    r2_after = {path.name: base.sha(path.read_bytes()) for path in r2_dir.iterdir() if path.is_file()}
    report = {"schema": "integrity-v7-main-isolated-offline/3", "date": "2026-10-09",
              "change": "Only the probe Windows audit seam: exact original vector plus exact native command; no broad subprocess exemption.",
              "r2_error_classification": "PROBE_WINDOWS_AUDIT_SHAPE_ERROR_NOT_V7_REGRESSION",
              "source_evidence": "Python312/Lib/subprocess.py:1450-1462,1534 converts argv to list2cmdline and audits executable=None when not explicitly supplied.",
              "command": command, "protected_unchanged": protected_before == protected_after,
              "r2_evidence_unchanged": r2_before == r2_after,
              "r2_report_sha256": base.sha((r2_dir / "report.json").read_bytes()),
              "retained_challenges": r2_report["commands"][1]["result"]["checks"],
              "challenges_rerun": False, "music_acceptance": "NOT_PERFORMED",
              "production_ready": False, "main_disposition": "NOT_ACCEPTED_CONFIRMED_V7_GAPS_REMAIN",
              "limits": r2_report["limits"]}
    base.save(out / "report.json", report)
    print(json.dumps({"command": command, "protected_unchanged": report["protected_unchanged"],
                      "r2_evidence_unchanged": report["r2_evidence_unchanged"],
                      "disposition": report["main_disposition"]}, ensure_ascii=False, allow_nan=False))
    return 0 if rc == 0 and not timed_out and report["protected_unchanged"] and report["r2_evidence_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
