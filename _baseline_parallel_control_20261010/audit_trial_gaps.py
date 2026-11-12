import json, os
from pathlib import Path
w = Path(r"D:\musicclaude\_dl_latest_zip_work")
rows = []
for m in ("gpt6w", "gpt56w"):
    base = w / "results" / "trials" / m
    if not base.exists():
        continue
    for job in sorted(os.listdir(base)):
        jb = base / job
        if not jb.is_dir():
            continue
        for f in sorted(jb.glob("r*.meta.json")):
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
            except Exception as e:
                meta = {"_read_error": str(e)}
            rows.append((m, job, f.stem.replace(".meta", ""), meta))
from collections import Counter
c = Counter()
for m, j, r, meta in rows:
    st = meta.get("status", "?")
    ok = meta.get("completed", None)
    c[(m, str(ok), str(st))] += 1
print("total metas:", len(rows))
for k, v in sorted(c.items()):
    print(k, v)
plan = json.loads((w / "jobs" / "repetition_plan.json").read_text())
jobs = [j["job_id"] for j in plan["jobs"]]
print("jobs:", jobs)
have = {}
for m, j, r, meta in rows:
    have.setdefault((m, j), set()).add(r)
for j in jobs:
    for m in ("gpt6w", "gpt56w"):
        got = sorted(have.get((m, j), []))
        print(m, j, got)
