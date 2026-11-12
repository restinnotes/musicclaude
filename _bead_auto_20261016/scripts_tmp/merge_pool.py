import json, re

out = "D:/musicclaude/_bead_auto_20261016/out"
short = json.load(open("D:/musicclaude/_bead_pub_20261015/out/STEP3_inputs/A_frozen_shortlist.json", encoding="utf-8"))
meta = {}
for i, e in enumerate(short, start=1):
    uid = f"A{i:02d}"
    model = {1: "gpt56w", 2: "gpt56w", 3: "gflash", 4: "muse", 5: "opus", 6: "grok", 7: "gflash_web", 8: "luna", 9: "opus_web", 10: "sol61_cx_web", 11: "V2A基线(gflash_web执行)"}[i]
    p = e["path"]
    if "A-int__" in p:
        chan = "int"
    elif "A-web__" in p:
        chan = "web"
    else:
        chan = "orig"
    meta[uid] = {"model": model, "channel": chan, "path": "music_work_since_1008v3_20261009/runs/" + e["path"], "bytes": e["bytes"], "sha256": e["sha256"]}

b1 = json.load(open(f"{out}/STEP3_parsed_b1.json", encoding="utf-8"))
a7 = json.load(open(f"{out}/STEP3_parsed_A07.json", encoding="utf-8"))
a8 = json.load(open(f"{out}/STEP3_parsed_A08.json", encoding="utf-8"))

SEGS = [("S01", "1-3", "序奏"), ("S02", "4-16", "第1主題"), ("S03", "17-23", "間句"), ("S04", "24-34", "第1主題（確保）"), ("S05", "35-39", "間句"), ("S06", "40-50", "第2主題前半"), ("S07", "51-61", "第2主題前半（確保）"), ("S08", "62-71", "第2主題後半"), ("S09", "72-77", "間句"), ("S10", "78-83", "挿入句"), ("S11", "84-92", "第1主題（再現）"), ("S12", "93-102", "第2主題後半（再現）"), ("S13", "103-110", "第2主題前半（再現）"), ("S14", "111-116", "終結句")]

def norm_entry(uid, cat, detail=None):
    axx = uid.split("-")[0]
    m = meta.get(axx, {})
    e = {"UID": uid, "归类": cat, "来源模型": m.get("model", ""), "通道": m.get("channel", ""), "路径": m.get("path", ""), "sha256": m.get("sha256", "")}
    if isinstance(detail, dict):
        for k in ("原文", "原文摘句", "原始小节范围", "判定说明", "归类", "类别"):
            if k in detail:
                e[k] = detail[k]
    return e

pool = {}
# S01-S14: b1 refs (PRIMARY/CROSS/UNCERTAIN split) + a7/a8 entries (use 归类/类别 field)
for s, rng, label in SEGS:
    seg = {"segment": s, "range": rng, "label": label, "PRIMARY": [], "CROSS_SEGMENT": [], "UNCERTAIN": []}
    b = b1.get(s, {})
    if isinstance(b, dict):
        for cat in ("PRIMARY", "CROSS_SEGMENT", "UNCERTAIN"):
            for uid in b.get(cat, []):
                seg[cat].append(norm_entry(uid, cat))
    for src in (a7, a8):
        for ent in src.get(s, []):
            cat = ent.get("归类") or ent.get("类别") or "CROSS_SEGMENT"
            if cat not in ("PRIMARY", "CROSS_SEGMENT", "UNCERTAIN"):
                cat = "CROSS_SEGMENT"
            seg[cat].append(norm_entry(ent.get("UID", "?"), cat, ent))
    pool[s] = seg

for k in ("UNRESOLVED", "OUT_OF_RANGE", "LONG_RANGE"):
    lst = []
    b = b1.get(k, [])
    if isinstance(b, list):
        for uid in b:
            lst.append(norm_entry(uid, k))
    for src in (a7, a8):
        for ent in src.get(k, []):
            lst.append(norm_entry(ent.get("UID", "?"), k, ent))
    pool[k] = lst

pool["_meta"] = {
    "work": "肖邦《船歌》升F大调 Op.60（116小节）",
    "frozen_segments": "C2=朝山奈津子/PTNA 2008 セクション十四段（S01-S14），不得更改",
    "sources": meta,
    "coverage": "A01-A05(int全)+A07(web gflash)+A08(web luna)=8件完整归段；A06(web gpt56w)仅部分示例、A09(web opus)A10(web sol61)A11(orig V2A)未归段，见缺口声明",
    "missing": ["A06 gpt56w/web 仅拿到部分示例回包未完整归段", "A09 opus_web 未归段", "A10 sol61_cx_web 未归段", "A11 orig V2A 未归段"],
    "no_fabrication": True,
}

json.dump(pool, open(f"{out}/A_POOL_MAP.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# stats for review
lines = []
for s, rng, label in SEGS:
    seg = pool[s]
    lines.append((s, rng, label, len(seg["PRIMARY"]), len(seg["CROSS_SEGMENT"]), len(seg["UNCERTAIN"])))
json.dump(lines, open(f"{out}/STEP3_segstats.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
unres = [e["UID"] for e in pool["UNRESOLVED"]]
print("seg stats:")
for s, rng, label, p, c, u in lines:
    print(f"{s} {rng}{label}: P={p} C={c} U={u}")
print("UNRESOLVED:", len(unres), unres)
print("OUT_OF_RANGE:", len(pool["OUT_OF_RANGE"]))
print("LONG_RANGE:", len(pool["LONG_RANGE"]))
uniq = set()
for s, rng, label in SEGS:
    for cat in ("PRIMARY", "CROSS_SEGMENT", "UNCERTAIN"):
        for e in pool[s][cat]:
            uniq.add(e["UID"])
for k in ("UNRESOLVED", "OUT_OF_RANGE", "LONG_RANGE"):
    for e in pool[k]:
        uniq.add(e["UID"])
print("unique units:", len(uniq))
import collections
print(collections.Counter(u.split("-")[0] for u in uniq))
