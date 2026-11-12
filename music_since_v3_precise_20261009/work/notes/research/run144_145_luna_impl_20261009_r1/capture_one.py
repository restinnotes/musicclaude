"""Capture one selected offline regression command without replacing prior attempts."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
COMMANDS = {
    "run144_tests": ("tools/tests/test_run144_e7_flash_diag_r5.py", ()),
    "run145_tests": ("tools/tests/test_run145_thread_resume_r5.py", ()),
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        raise SystemExit("choose run144_tests or run145_tests")
    prior = [int(path.name.split("-")[-1]) for path in EVIDENCE.glob("attempt-*")
             if path.is_dir() and path.name.split("-")[-1].isdigit()]
    attempt_id = max(prior, default=0) + 1
    attempt_dir = EVIDENCE / ("attempt-%03d" % attempt_id)
    attempt_dir.mkdir()
    label = sys.argv[1]
    relative, extra = COMMANDS[label]
    argv = [sys.executable, "-X", "utf8", "-I", "-B", str(ROOT / relative), *extra]
    safe_env = {key: os.environ[key] for key in
                ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT") if key in os.environ}
    started = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(argv, cwd=ROOT, env=safe_env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=300, check=False)
        stdout, stderr, returncode = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode("utf-8")
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode("utf-8")
        returncode = None
    elapsed = round(time.monotonic() - started, 3)
    (attempt_dir / (label + ".stdout.bin")).write_bytes(stdout)
    (attempt_dir / (label + ".stderr.bin")).write_bytes(stderr)
    row = {"label": label, "argv": argv, "cwd": str(ROOT), "returncode": returncode,
           "timed_out": timed_out, "elapsed_seconds": elapsed,
           "stdout_file": label + ".stdout.bin", "stdout_bytes": len(stdout),
           "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
           "stderr_file": label + ".stderr.bin", "stderr_bytes": len(stderr),
           "stderr_sha256": hashlib.sha256(stderr).hexdigest()}
    metadata = {"attempt": attempt_id, "python": sys.executable,
                "runtime_flags": ["-X", "utf8", "-I", "-B"],
                "network": "not used", "provider_or_model_cli_invocations": 0,
                "commands": [row]}
    (attempt_dir / "commands.json").write_bytes(
        (json.dumps(metadata, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps({"attempt": attempt_id, "label": label, "returncode": returncode,
                      "timed_out": timed_out, "elapsed_seconds": elapsed,
                      "evidence_dir": str(attempt_dir)}, ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
