#!/usr/bin/env python3
"""No-model hidden-spawn verification (r01 fix proof).

Spawns REAL child processes through the same hidden_popen_kwargs() +
direct-interpreter path pipeline.py now uses, but NEVER submits a model
request:
  1. venv python -I -c echo (fast, proves flags on a real child)
  2. gpt2_cli.py check --help-equivalent? No: run `check` (local-only,
     no browser, no model call) to prove the real CLI entry spawns hidden.

Checks: CREATE_NO_WINDOW set, DETACHED absent, STARTUPINFO SW_HIDE,
child exit captured, no .cmd/cmd.exe in argv.
Writes hidden_spawn_test.json into run-v2/.
"""
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAFECHAIN = Path(r"D:\musicclaude\gpt2agent-safechain")
GPT2_PY = SAFECHAIN / ".venv-local" / "Scripts" / "python.exe"
GPT2_CLI = SAFECHAIN / "tools" / "chatgpt_web" / "gpt2_cli.py"
OUT = HERE / "run-v2" / "hidden_spawn_test.json"

sys.path.insert(0, str(HERE))
import importlib.util

spec = importlib.util.spec_from_file_location("pipeline_mod", HERE / "pipeline.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

results = {"utc": datetime.now(timezone.utc).isoformat(), "tests": []}


def rec(name, ok, detail=""):
    results["tests"].append({"name": name, "ok": bool(ok), "detail": detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}", flush=True)


kw = mod.hidden_popen_kwargs()
rec("create_no_window_set",
    (kw.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0)) != 0,
    f"flags={kw.get('creationflags')}")
rec("no_detached_process",
    not (kw.get("creationflags", 0) & getattr(subprocess, "DETACHED_PROCESS", 0)),
    "DETACHED must stay clear or CREATE_NO_WINDOW is ignored")
si = kw.get("startupinfo")
rec("startupinfo_swhide",
    si is not None and (si.dwFlags & subprocess.STARTF_USESHOWWINDOW) != 0,
    "STARTUPINFO SW_HIDE present")

# 1) real child via identical kwargs (no model, no network).
# NOTE: GPT2_PY is itself the interpreter binary (spawned as argv[0]),
# never passed as a script to another python.
t0 = time.monotonic()
p = subprocess.Popen([str(GPT2_PY), "-I", "-c",
                       "import sys; print('hidden-child-ok'); print('ERR-LINE', file=sys.stderr)"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                      encoding="utf-8", errors="replace", **mod.hidden_popen_kwargs())
so, se = p.communicate(timeout=60)
rec("real_child_echo", p.returncode == 0 and "hidden-child-ok" in so,
    f"rc={p.returncode} elapsed={round(time.monotonic()-t0,2)}s out={so.strip()[:40]!r}")

# 2) real CLI entry, local-only `check` (no browser, no model submission).
# Same argv shape + cwd the scheduler uses; -I is intentionally ABSENT
# (r01 lesson: -I strips the script dir and breaks `import headless_client`).
t0 = time.monotonic()
argv = [str(GPT2_PY), str(GPT2_CLI), "check"]
rec("no_cmd_exe_in_argv", not any(a.lower().endswith((".cmd", ".bat")) or "cmd.exe" in a.lower() for a in argv),
    f"argv0={Path(argv[0]).name} argv1={Path(argv[1]).name}")
p2 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       cwd=str(SAFECHAIN),
                       encoding="utf-8", errors="replace", **mod.hidden_popen_kwargs())
so2, se2 = p2.communicate(timeout=120)
try:
    payload = json.loads((so2 or "").strip().lstrip("\ufeff"))
    looks_local = isinstance(payload, dict) and "docker_ready" in payload
except Exception:
    payload, looks_local = None, False
rec("real_cli_check_hidden", looks_local,
    f"rc={p2.returncode} elapsed={round(time.monotonic()-t0,1)}s docker_ready={(payload or {}).get('docker_ready')}")

results["all_ok"] = all(t["ok"] for t in results["tests"])
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"WROTE {OUT} all_ok={results['all_ok']}", flush=True)
raise SystemExit(0 if results["all_ok"] else 1)
