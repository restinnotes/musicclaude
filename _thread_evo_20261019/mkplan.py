"""Write evaluations/<eid>/plan.json: each judge sees every draft once, in blocks of k drafts + one anchor.
usage: python mkplan.py <eid> <anchor> <k> name1,name2,...   (anchor: B0 or a run id)"""
import json, os, random, sys
eid, anchor, k, names = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4].split(",")
plan = {}
for jn in ["gpt6", "gpt56"]:
    r = random.Random(f"{eid}{jn}"); m = names[:]; r.shuffle(m)
    pad = (-len(m)) % k
    m += r.sample(m[:-k], pad) if pad else []
    for bi in range(len(m) // k):
        grp = m[bi * k:bi * k + k] + [anchor]; random.Random(f"{eid}{jn}{bi}").shuffle(grp)
        plan[f"b{bi + 1:02d}_{jn}"] = {"judge": jn, "map": {f"文章{chr(65 + i)}": n for i, n in enumerate(grp)}}
os.makedirs(f"evaluations/{eid}", exist_ok=True)
json.dump(plan, open(f"evaluations/{eid}/plan.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(eid, len(names), "drafts", len(plan), "blocks")
