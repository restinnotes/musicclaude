"""Capture each required offline command's exact stdout/stderr bytes and exit status."""
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
COMMANDS = (
    ("run144_tests", "tools/tests/test_run144_e7_flash_diag_r5.py", ()),
    ("run145_tests", "tools/tests/test_run145_thread_resume_r5.py", ()),
    ("run144_real", "runs/run144_e7_flash_diag_r5/go.py", ("--real",)),
    ("run145_strict", "runs/run145_thread_resume_r5/go.py", ("--strict",)),
    ("run145_real", "runs/run145_thread_resume_r5/go.py", ("--real",)),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    prior = [int(path.name.split("-")[-1]) for path in EVIDENCE.glob("attempt-*")
             if path.is_dir() and path.name.split("-")[-1].isdigit()]
    attempt_id = max(prior, default=0) + 1
    attempt_dir = EVIDENCE / ("attempt-%03d" % attempt_id)
    attempt_dir.mkdir()
    safe_env = {key: os.environ[key] for key in
                ("PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT") if key in os.environ}
    results = []
    for label, relative, extra in COMMANDS:
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(ROOT / relative), *extra]
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
        stdout_name, stderr_name = label + ".stdout.bin", label + ".stderr.bin"
        (attempt_dir / stdout_name).write_bytes(stdout)
        (attempt_dir / stderr_name).write_bytes(stderr)
        results.append({"label": label, "argv": argv, "cwd": str(ROOT),
                        "returncode": returncode, "timed_out": timed_out,
                        "elapsed_seconds": elapsed,
                        "stdout_file": stdout_name, "stdout_bytes": len(stdout),
                        "stdout_sha256": sha256(stdout),
                        "stderr_file": stderr_name, "stderr_bytes": len(stderr),
                        "stderr_sha256": sha256(stderr)})
        print(json.dumps({"attempt": attempt_id, "label": label, "returncode": returncode,
                          "timed_out": timed_out, "elapsed_seconds": elapsed,
                          "stdout_bytes": len(stdout), "stderr_bytes": len(stderr)},
                         ensure_ascii=True), flush=True)
    metadata = {"attempt": attempt_id, "python": sys.executable,
                "runtime_flags": ["-X", "utf8", "-I", "-B"],
                "network": "not used", "provider_or_model_cli_invocations": 0,
                "commands": results}
    raw = (json.dumps(metadata, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("utf-8")
    (attempt_dir / "commands.json").write_bytes(raw)
    print(json.dumps({"attempt": attempt_id, "evidence_dir": str(attempt_dir),
                      "all_expected_rc": all(
                          not row["timed_out"] and row["returncode"] == expected
                          for row, expected in zip(results, (0, 0, 3, 0, 3)))},
                     ensure_ascii=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
