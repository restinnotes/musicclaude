"""10-27 relaunch with the 8-hour plan: gpt3 up to 2 in flight (GPT3_SLOTS=2), 5.6 checks on MimicGate, both pieces at once.
1. wait for the orphaned gpt3 call of syP3a_op60_S01_A (its caller was stopped) and recover its answer from the job dir;
2. start synth op60; 3. wait for pool3 op61 to finish, then start synth op61."""
import json, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JOBS = Path("D:/musicclaude/gpt2agent-safechain/runs/gpt3")
ENV = {**os.environ, "THREAD_ROUTE": "gpt3s", "THREAD_ROUTE_G56": "mimic", "GPT3_SLOTS": "2"}


def alive(pattern):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          f"(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {{ $_.CommandLine -match '{pattern}' }}).Count"],
                         capture_output=True, text=True).stdout.strip()
    return out not in ("", "0")


def recover(rid):
    d = ROOT / "runs" / rid; msg = (d / "input.txt").read_text(encoding="utf-8").strip()
    for j in sorted(JOBS.glob("pro-bridge-2026102*"), reverse=True)[:40]:
        try:
            if (j / "prompt.txt").read_text(encoding="utf-8-sig").strip() != msg:
                continue
            r = json.loads((j / "result.json").read_text(encoding="utf-8"))
            resp = (j / "response.txt").read_text(encoding="utf-8-sig")
        except Exception:
            continue
        if str(r.get("ok")) == "True" and r.get("model") == "gpt-6-thinking" and resp.strip():
            (d / "output.txt").write_text(resp, encoding="utf-8")
            (d / "call.log").write_text(json.dumps({"run_id": rid, "recovered_from_job": str(j), "model": r.get("model"),
                                                    "thinking_effort": r.get("thinkingEffort")}, ensure_ascii=False, indent=1), encoding="utf-8")
            print("recovered", rid, "from", j.name, flush=True); return True
    print("no recoverable job for", rid, flush=True); return False


def start(work, log):
    subprocess.Popen([sys.executable, "-u", "synth3.py", "P3a", work, "P26"], cwd=ROOT, env=ENV,
                     stdout=open(ROOT / "runs" / log, "a", encoding="utf-8"), stderr=subprocess.STDOUT)
    print("started synth", work, flush=True)


if __name__ == "__main__":
    while alive("syP3a_op60_S01_A"):
        time.sleep(15)
    recover("syP3a_op60_S01_A")
    start("op60", "SYN3_op60.log")
    while alive("pool3.py P26 op61"):
        time.sleep(30)
    start("op61", "SYN3_op61.log")
