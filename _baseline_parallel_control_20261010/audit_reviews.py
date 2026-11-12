import json, os
from pathlib import Path
w = Path(r"D:\musicclaude\_dl_latest_zip_work")
rm = json.loads((w / "jobs" / "reviews" / "review_manifest.json").read_text())
jobs = rm["jobs"]
print("review jobs:", len(jobs))
from collections import Counter
c = Counter()
missing = []
for j in jobs:
    jid = j.get("job_id") or j.get("id")
    kind = j.get("kind")
    judge = j.get("judge_model") or j.get("judge")
    d = w / "results" / "reviews" / judge if judge else None
    found = None
    if d and d.exists():
        for f in d.iterdir():
            if f.is_dir() and (jid in f.name):
                found = str(f)
                break
        if found is None:
            for f in sorted(d.rglob("*.meta.json")):
                if jid in str(f):
                    found = str(f)
                    break
    # check canonical meta path variants
    cands = []
    if judge:
        cands.append(w / "results" / "reviews" / judge / jid / "review.meta.json")
    if found is None:
        missing.append((kind, judge, jid))
    c[(kind, judge)] += 1
print("by kind/judge:", dict(c))
print("missing:", len(missing))
for m in missing:
    print("MISS:", m)
