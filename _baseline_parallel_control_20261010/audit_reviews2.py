import json
from pathlib import Path
w = Path(r"D:\musicclaude\_dl_latest_zip_work")
rm = json.loads((w / "jobs" / "reviews" / "review_manifest.json").read_text())
needs = []
ok = 0
for j in rm["jobs"]:
    jid = j["job_id"]
    judge = j["judge_model"]
    p = w / "results" / "reviews" / judge / (jid + ".meta.json")
    if not p.exists():
        needs.append((jid, judge, "MISSING_META"))
        continue
    try:
        meta = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        needs.append((jid, judge, "UNREADABLE " + str(e)))
        continue
    if meta.get("completed") is True and meta.get("status") == "success":
        ok += 1
    else:
        needs.append((jid, judge, str(meta.get("status"))))
print("review success:", ok, "/", len(rm["jobs"]))
for n in needs:
    print("NEEDS:", n)
