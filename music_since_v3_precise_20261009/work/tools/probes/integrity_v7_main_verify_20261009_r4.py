"""Keep Popen a class while checking exact local argv and native audit evidence."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


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

    class GuardedPopen(original_popen):
        def __init__(self, *args, **kwargs):
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
                super().__init__(*args, **kwargs)
            finally:
                authorization = None

    sys.addaudithook(audit)
    subprocess.Popen = GuardedPopen
    return allowed, original_popen, queue_script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    r3 = load(Path(__file__).with_name("integrity_v7_main_verify_20261009_r3.py"), "retained_v7_r3_probe")
    if args.worker:
        r3.install_worker_guard = install_worker_guard
        return r3.worker(root)
    if args.out_dir is None:
        parser.error("--out-dir is required outside worker mode")
    base = load(Path(__file__).with_name("integrity_v7_main_verify_20261009_r2.py"), "retained_v7_r2_probe")
    out = args.out_dir.resolve()
    out.mkdir(parents=False, exist_ok=False)

    def historical_snapshot():
        paths = [Path(__file__).with_name("integrity_v7_main_verify_20261009_" + revision + ".py")
                 for revision in ("r2", "r3")]
        for revision in ("r2", "r3"):
            folder = root / ("notes/research/integrity_v7_main_verify_20261009_" + revision)
            paths.extend(path for path in folder.iterdir() if path.is_file())
        return {str(path.relative_to(root)): base.sha(path.read_bytes()) for path in paths}

    history_before = historical_snapshot()
    protected_before = base.source_hashes(root)
    base.save(out / "protected_before.json", protected_before)
    r2_report_path = root / "notes/research/integrity_v7_main_verify_20261009_r2/report.json"
    r2_report = json.loads(r2_report_path.read_bytes())
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
    history_after = historical_snapshot()
    report = {"schema": "integrity-v7-main-isolated-offline/4", "date": "2026-10-09",
              "change": "Probe only: keep Popen a class; preserve exact vector/native-command authorization and six negative controls.",
              "r2_error_classification": "PROBE_WINDOWS_AUDIT_SHAPE_ERROR_NOT_V7_REGRESSION",
              "r3_error_classification": "PROBE_POPEN_FUNCTION_BREAKS_ASYNCIO_SUBCLASS_IMPORT; SUITE_NOT_STARTED",
              "command": command, "protected_unchanged": protected_before == protected_after,
              "historical_probe_evidence_unchanged": history_before == history_after,
              "r2_report_sha256": base.sha(r2_report_path.read_bytes()),
              "retained_challenges": r2_report["commands"][1]["result"]["checks"],
              "challenges_rerun": False, "music_acceptance": "NOT_PERFORMED",
              "production_ready": False, "main_disposition": "NOT_ACCEPTED_CONFIRMED_V7_GAPS_REMAIN",
              "limits": r2_report["limits"]}
    base.save(out / "report.json", report)
    print(json.dumps({"command": command, "protected_unchanged": report["protected_unchanged"],
                      "historical_probe_evidence_unchanged": report["historical_probe_evidence_unchanged"],
                      "disposition": report["main_disposition"]}, ensure_ascii=False, allow_nan=False))
    return 0 if rc == 0 and not timed_out and report["protected_unchanged"] and report["historical_probe_evidence_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
