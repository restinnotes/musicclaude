"""Run one gpt3 call per segment. Usage: python run.py S01 S02 ...  (or 'all'); --par N"""
import json, subprocess, sys, time, threading
from pathlib import Path

W = Path(__file__).resolve().parent.parent
GPT3 = r"D:\musicclaude\gpt2agent-safechain\bin\gpt3.cmd"
segs = json.load(open(W / "input" / "structure.json", encoding="utf-8"))["frozen_segments"]
SEGS = {f"S{i+1:02d}": (mm, lab) for i, (mm, lab) in enumerate(segs)}
tpl = (W / "prompts" / "TEMPLATE.md").read_text(encoding="utf-8")

args = [a for a in sys.argv[1:] if not a.startswith("--")]
par = int(next((a.split("=")[1] for a in sys.argv[1:] if a.startswith("--par=")), "4"))
todo = list(SEGS) if args == ["all"] else args
todo = [s for s in todo if not (W / "out" / f"{s}.result.json").exists()]

def save(seg, job):
    job = Path(job)
    resp = (job / "response.txt").read_text(encoding="utf-8")
    meta = json.loads((job / "result.json").read_text(encoding="utf-8")).get("metadata", {})
    (W / "out" / f"{seg}.response.txt").write_text(resp, encoding="utf-8")
    (W / "out" / f"{seg}.result.json").write_text(json.dumps({"segment": seg, "job_directory": str(job), "metadata": meta}, ensure_ascii=False, indent=1), encoding="utf-8")


sem = threading.Semaphore(par)
start_lock = threading.Lock()
last_start = [0.0]


def run(seg):
    mm, lab = SEGS[seg]
    p = W / "prompts" / f"{seg}.txt"
    p.write_text(tpl.replace("{SEG}", seg).replace("{MM}", mm.replace("-", "–")).replace("{LABEL}", lab), encoding="utf-8")
    with sem:
        with start_lock:
            wait = 7 - (time.time() - last_start[0])
            if wait > 0:
                time.sleep(wait)
            last_start[0] = time.time()
        t0 = time.time()
        cp = subprocess.run([GPT3, "ask", "--file", str(p), "--attach", str(W / "input_bundle.zip"), "--json"],
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        dt = time.time() - t0
    (W / "out" / f"{seg}.raw_stdout.txt").write_text(cp.stdout, encoding="utf-8")
    (W / "out" / f"{seg}.stderr.txt").write_text(cp.stderr, encoding="utf-8")
    try:
        r = json.loads(cp.stdout)
    except Exception:
        r = None
    ok = cp.returncode == 0 and r and r.get("completed")
    if ok:
        save(seg, r["metadata"]["job_directory"])
    print(f"{seg} rc={cp.returncode} ok={bool(ok)} {dt:.0f}s", flush=True)


ts = [threading.Thread(target=run, args=(s,)) for s in todo]
for t in ts:
    t.start()
for t in ts:
    t.join()
