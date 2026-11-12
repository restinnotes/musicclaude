import json

out = "D:/musicclaude/_bead_auto_20261016/out"
pool = json.load(open(f"{out}/A_POOL_MAP.json", encoding="utf-8"))

# batch-UID -> frozen-shortlist UID
conv = {"A01": "A01", "A02": "A03", "A03": "A04", "A04": "A05", "A05": "A06", "A07": "A07", "A08": "A08"}
src = pool["_meta"]["sources"]

def fix_uid(uid):
    axx, rest = uid.split("-", 1)
    return conv.get(axx, axx) + "-" + rest

def fix_entry(e):
    e["UID"] = fix_uid(e["UID"])
    axx = e["UID"].split("-")[0]
    m = src.get(axx, {})
    e["来源模型"] = m.get("model", "")
    e["通道"] = m.get("channel", "")
    e["路径"] = m.get("path", "")
    e["sha256"] = m.get("sha256", "")
    return e

for s in [f"S{i:02d}" for i in range(1, 15)]:
    for cat in ("PRIMARY", "CROSS_SEGMENT", "UNCERTAIN"):
        pool[s][cat] = [fix_entry(e) for e in pool[s][cat]]
for k in ("UNRESOLVED", "OUT_OF_RANGE", "LONG_RANGE"):
    pool[k] = [fix_entry(e) for e in pool[k]]

pool["_meta"]["uid_note"] = "批1回包内编号A01-A05对应冻结清单第1、3、4、5、6件，已转换为清单口径A01/A03/A04/A05/A06；A07/A08即清单第7/8件。"
pool["_meta"]["coverage"] = "清单11件中已完整归段7件：A01(gpt56w/int)+A03(gflash/int)+A04(muse/int)+A05(opus/int)+A06(grok/int)+A07(gflash_web/web)+A08(luna/web)；缺口4件：A02(gpt56w/web半成品)+A09(opus_web)+A10(sol61_cx_web)+A11(orig V2A)。"

json.dump(pool, open(f"{out}/A_POOL_MAP.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

uniq = set()
for s in [f"S{i:02d}" for i in range(1, 15)]:
    for cat in ("PRIMARY", "CROSS_SEGMENT", "UNCERTAIN"):
        for e in pool[s][cat]:
            uniq.add(e["UID"])
for k in ("UNRESOLVED", "OUT_OF_RANGE", "LONG_RANGE"):
    for e in pool[k]:
        uniq.add(e["UID"])
import collections
print("unique units:", len(uniq))
print(collections.Counter(u.split("-")[0] for u in uniq))
print("UNRESOLVED:", sorted(u for u in uniq if pool["_meta"] and u in [x["UID"] for x in pool["UNRESOLVED"]]))
for s in [f"S{i:02d}" for i in range(1, 15)]:
    seg = pool[s]
    print(s, f"P={len(seg['PRIMARY'])} C={len(seg['CROSS_SEGMENT'])} U={len(seg['UNCERTAIN'])}")
print("OOR:", len(pool["OUT_OF_RANGE"]), "LR:", len(pool["LONG_RANGE"]))
