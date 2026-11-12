"""Recover answers of gpt3 calls whose scheduler was stopped while the call itself kept running.
Only accepts a job whose own terminal verification passed with the expected model/max/temporary/unpersonalized.
Usage: python recover.py <stage> <name> [<name> ...]   (waits until each job finishes)"""
import json, sys, time
from pathlib import Path
import thr

stage, names = sys.argv[1], sys.argv[2:]
for name in names:
    pt = (thr.RUNS / stage / f"{name}.prompt.txt").read_text(encoding="utf-8")
    job = Path(thr.find_job(pt, time.time() - 6 * 3600))
    while not (job / "terminal-verification.json").exists() or not (job / "result.json").exists():
        time.sleep(20)
    time.sleep(5)
    tv = json.loads((job / "terminal-verification.json").read_text(encoding="utf-8"))
    r = json.loads((job / "result.json").read_text(encoding="utf-8"))
    fm = (tv.get("final_messages") or [{}])[0]
    ok = (tv.get("terminal_completion_verified") and r.get("temporary") and r.get("unpersonalized")
          and fm.get("model") == r.get("model") and fm.get("effort") == "max")
    rec = {"stage": stage, "name": name, "recovered_from_job": str(job), "completed": bool(ok), "model": r.get("model"),
           "effort": fm.get("effort"), "temporary": r.get("temporary"), "unpersonalized": r.get("unpersonalized"),
           "session_handle": None, "note": "scheduler stopped mid-call; answer recovered from gpt3 evidence after its own terminal verification"}
    thr.log(rec)
    if not ok:
        print(name, "NOT VERIFIED", tv.get("checks")); continue
    resp = (job / "response.txt").read_text(encoding="utf-8")
    (thr.RUNS / stage / f"{name}.response.txt").write_text(resp, encoding="utf-8")
    (thr.RUNS / stage / f"{name}.meta.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, "recovered", thr.finish_json(stage, name, (resp, None)))
