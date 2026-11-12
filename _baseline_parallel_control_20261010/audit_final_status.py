import json, os, hashlib
from pathlib import Path
w = Path(r"D:\musicclaude\_dl_latest_zip_work")

def final_meta(model, job, rnd):
    """Return (status, completed, path) of the final (non-attempt) meta for model/job/rXX."""
    p = w / "results" / "trials" / model / job / (rnd + ".meta.json")
    if not p.exists():
        return ("MISSING_FILE", None, str(p))
    try:
        meta = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return ("UNREADABLE", None, str(p))
    return (meta.get("status", "?"), meta.get("completed", None), str(p))

plan = json.loads((w / "jobs" / "repetition_plan.json").read_text())
jobs = [j["job_id"] for j in plan["jobs"]]
print("=== BASE r01-r05 final status ===")
base_rows = []
for j in jobs:
    for m in ("gpt6w", "gpt56w"):
        for r in ("r01", "r02", "r03", "r04", "r05"):
            st, ok, _ = final_meta(m, j, r)
            base_rows.append((m, j, r, st, ok))
            if not (ok is True and st == "success"):
                print("NEEDS:", m, j, r, st, ok)
n_ok = sum(1 for x in base_rows if x[4] is True and x[3] == "success")
print("base success:", n_ok, "/", len(base_rows))
print("=== EXT r06-r08 for C02/C11/C23 ===")
for j in ("C02", "C11", "C23"):
    for m in ("gpt6w", "gpt56w"):
        for r in ("r06", "r07", "r08"):
            st, ok, _ = final_meta(m, j, r)
            print(m, j, r, st, ok)
print("=== REVIEWS ===")
rm = json.loads((w / "jobs" / "reviews" / "review_manifest.json").read_text())
print("manifest type:", type(rm), "keys:", list(rm.keys())[:10] if isinstance(rm, dict) else len(rm))
