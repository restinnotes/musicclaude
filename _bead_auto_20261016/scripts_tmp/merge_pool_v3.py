# -*- coding: utf-8 -*-
"""Merge STEP3-v3 review verdicts into final A_POOL_MAP_v3.json.
Mechanical pre-map stays authoritative for PRIMARY/ordinary CROSS. Review
verdicts (NR/OOB/C/D) may reroute a unit to GLOBAL/UNCERTAIN/DROP, or give an
explicit RANGE/NARROW which is re-mapped with the same deterministic rules.
Outputs: A_POOL_MAP_v3.json + A_POOL_REVIEW.md (中文).
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

OUT = r"D:\musicclaude\_bead_auto_20261016\out"
SEGMENTS = [
    ("S01", 1, 3), ("S02", 4, 16), ("S03", 17, 23), ("S04", 24, 34),
    ("S05", 35, 39), ("S06", 40, 50), ("S07", 51, 61), ("S08", 62, 71),
    ("S09", 72, 77), ("S10", 78, 83), ("S11", 84, 92), ("S12", 93, 102),
    ("S13", 103, 110), ("S14", 111, 116),
]
PRE = json.load(open(os.path.join(OUT, "A_POOL_MAP_v3_prejson.json"), encoding="utf-8"))
UNITS = json.load(open(os.path.join(OUT, "A36_units.json"), encoding="utf-8"))

RANGEV = re.compile(r"^(?:RANGE|NARROW):mm\.?(\d{1,3})-(\d{1,3})$")

def covered(rng):
    return sorted(sid for sid, a, b in SEGMENTS if not (rng[1] < a or rng[0] > b))

def contained(rng):
    return sorted(sid for sid, a, b in SEGMENTS if rng[0] >= a and rng[1] <= b)

def remap(rng):
    iv = contained(rng)
    if len(iv) == 1:
        return {"slot": "PRIMARY", "seg": iv[0]}
    cv = covered(rng)
    if len(cv) == 0:
        return {"slot": "UNRESOLVED"}
    return {"slot": "CROSS", "segs": cv}

# ---------- parse review verdicts (split A/B) ----------
def parse_verdicts(raw_path):
    if not os.path.isfile(raw_path):
        print(f"missing {raw_path} — run BOTH gpt2 review lanes first.")
        sys.exit(1)
    RJ = json.load(open(raw_path, encoding="utf-8"))
    resp = RJ.get("response") or RJ.get("text") or ""
    for blk in re.findall(r"```[\s\S]*?```", resp):
        body = blk[3:-3].strip()
        if body.startswith("json"):
            body = body[4:].strip()
        try:
            cand = json.loads(body)
        except Exception:
            i, j = body.find("{"), body.rfind("}")
            if i < 0 or j <= i:
                continue
            try:
                cand = json.loads(body[i:j + 1])
            except Exception:
                continue
        if isinstance(cand, dict) and ("NR" in cand or "OOB" in cand or "C" in cand or "D_flags" in cand):
            return cand, resp
    print(f"NO REVIEW VERDICTS PARSED in {raw_path}. Response head:\n", resp[:1000])
    sys.exit(1)

overrides = {}
seen_uid = {}
notes_parts = []
for _s in ("A", "B", "C"):
    rawp = os.path.join(OUT, "STEP3_inputs", "step3_review_raw_%s.json" % _s)
    verdicts, resp = parse_verdicts(rawp)
    notes_parts.append(("分片%s" % _s, verdicts.get("_notes", "")))
    pairs = [(key, "bucket:" + key) for key in ("NR", "OOB")]
    for key, tag in pairs:
        for uid, v in (verdicts.get(key) or {}).items():
            entry = (tag, str(v).strip(), "step3_review_raw_%s.json" % _s)
            if uid in seen_uid:
                print(f"!! uid judged twice across parts: {uid} {seen_uid[uid]} vs {entry} — keeping first")
                continue
            seen_uid[uid] = entry
            overrides[uid] = (entry[0], entry[1])
    for cid in ("C", "D_flags"):
        for uid, v in (verdicts.get(cid) or {}).items():
            tag = ("cross-long" if cid == "C" else "cross-other", "step3_review_raw_%s.json" % _s)
            if uid in seen_uid:
                print(f"!! uid judged twice across parts: {uid} {seen_uid[uid]} vs {v} — keeping first")
                continue
            seen_uid[uid] = (tag[0], "", tag[1])
            overrides[uid] = (tag[0], str(v).strip())
notes = "\n\n".join(f"{tag}：{n}" if n else f"{tag}：（无）" for tag, n in notes_parts)

# ---------- mechanical slot lookup (uid -> slot dict) ----------
mech = {}
for sid, _, _ in SEGMENTS:
    for e in PRE["pool"][sid]["primary"]:
        mech[e["uid"]] = {"slot": "PRIMARY", "seg": sid}
cross_segs = {}
for sid, _, _ in SEGMENTS:
    for e in PRE["pool"][sid]["cross"]:
        cross_segs.setdefault(e["uid"], set()).add(sid)
for uid, segset in cross_segs.items():
    mech[uid] = {"slot": "CROSS", "segs": sorted(segset)}

# ---------- final assignment ----------
final = {}
seg_data = {sid: {"primary": [], "cross": []} for sid, _, _ in SEGMENTS}
buckets = {"GLOBAL": [], "UNCERTAIN": [], "DROP": [], "UNRESOLVED": []}
applied = {}

for src, d in UNITS["sources"].items():
    for u in d["units"]:
        uid = u["uid"]
        verdict = (overrides.get(uid) or (None, None))[1]
        if verdict:
            if RANGEV.match(verdict):
                mm = RANGEV.match(verdict)
                a, b = int(mm.group(1)), int(mm.group(2))
                if a < 1 or b > 116 or a > b:
                    slot = {"slot": "UNRESOLVED", "verdict_range": [a, b]}
                else:
                    slot = remap((a, b))
                    slot["verdict_range"] = [a, b]
            elif verdict in ("GLOBAL", "KEEP_GLOBAL", "SPLIT_AS_GLOBAL"):
                slot = {"slot": "GLOBAL"}
            elif verdict == "OK_CROSS":
                m0 = mech.get(uid)
                slot = dict(m0) if m0 else {"slot": "UNRESOLVED", "verdict_raw": verdict}
            elif verdict == "UNCERTAIN":
                slot = {"slot": "UNCERTAIN"}
            elif verdict == "DROP":
                slot = {"slot": "DROP"}
            else:
                print(f"UNEXPECTED verdict {uid}: {verdict!r} -> UNCERTAIN")
                slot = {"slot": "UNCERTAIN", "verdict_raw": verdict}
        else:
            m0 = mech.get(uid)
            slot = dict(m0) if m0 else {"slot": "UNRESOLVED"}
        eout = {"src": src, "uid": uid,
                "ranges": ["%d-%d" % (r[0], r[1]) for r in u["ranges"]],
                "chars": u["chars"], "kind": u["kind"]}
        if u.get("title_inherited"):
            eout["title_inherited"] = u["title_inherited"]
        eout["slot"] = slot["slot"]
        for k in ("seg", "segs", "verdict_range", "verdict_raw"):
            if k in slot:
                eout[k] = slot[k]
        final[uid] = eout
        s = slot["slot"]
        applied[s] = applied.get(s, 0) + 1
        if s == "PRIMARY":
            seg_data[slot["seg"]]["primary"].append(eout)
        elif s == "CROSS":
            for sid in slot["segs"]:
                seg_data[sid]["cross"].append(eout)
        elif s in buckets:
            buckets[s].append(eout)

# ---------- coverage audit ----------
n_units = sum(len(d["units"]) for d in UNITS["sources"].values())
assert n_units == len(final), f"coverage delta: units={n_units} finals={len(final)}"
# PRIMARY must appear in exactly its own seg; CROSS exactly len(segs) times
problems = []
for uid, e in final.items():
    if e["slot"] == "PRIMARY":
        n = sum(1 for e2 in seg_data[e["seg"]]["primary"] if e2["uid"] == uid)
        if n != 1:
            problems.append((uid, "primary-place", n))
    elif e["slot"] == "CROSS":
        n = sum(1 for sid in seg_data for e2 in seg_data[sid]["cross"] if e2["uid"] == uid)
        if n != len(e["segs"]):
            problems.append((uid, "cross-place", n, len(e["segs"])))
out = {"_meta": {"generator": "merge_pool_v3.py",
                 "review_raw": "step3_review_raw_A.json + step3_review_raw_B.json + step3_review_raw_C.json",
                 "segments": [[s, a, b] for s, a, b in SEGMENTS],
                 "slots": applied,
                 "placement_problems": problems},
        "segments": {sid: {"ranges": [a, b],
                           "entries": seg_data[sid]["primary"] + seg_data[sid]["cross"]}
                     for sid, a, b in SEGMENTS},
        "global": buckets["GLOBAL"], "uncertain": buckets["UNCERTAIN"],
        "drop": buckets["DROP"], "unresolved": buckets["UNRESOLVED"],
        "units": final, "review_notes": notes}
json.dump(out, open(os.path.join(OUT, "A_POOL_MAP_v3.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---------- 中文复核说明 ----------
L = ["# A_POOL_REVIEW v3（复核说明与去向台账）", ""]
L.append(f"审阅输出：`step3_review_raw_A.json` + `step3_review_raw_B.json` + `step3_review_raw_C.json`（分片 A/B/C，判定集互不重叠）；机械映射：`A_POOL_MAP_v3_prejson.json`。审阅只做语义判定与长跨度归类；机械 PRIMARY/普通 CROSS 未复判定，以逐字范围为准。")
L.append("")
L.append("## 判定统计")
L.append("| 槽位 | 说明 | 条数 |")
L.append("|---|---|---|")
desc = {"PRIMARY": "完全落在一段", "CROSS": "跨段连续叙述（每段各留一条，全文重复出现）",
        "GLOBAL": "整曲全局底色（进每段附件第五部分，不进读者正文）",
        "UNCERTAIN": "无法确定（仅内部台账）", "DROP": "从 Pool 剔除",
        "UNRESOLVED": "机械与复核后仍无位置（需人工查看）"}
for k in ("PRIMARY", "CROSS", "GLOBAL", "UNCERTAIN", "DROP", "UNRESOLVED"):
    L.append(f"| {k} | {desc[k]} | {applied.get(k, 0)} |")
L.append(f"| **合计（=单元数）** | | **{n_units}** |")
L.append("")
L.append(f"覆盖核查：全部 {n_units} 个单元各占一个最终槽位（断言通过）。放置问题条数：{len(problems)}。")
for p in problems[:20]:
    L.append(f"- {p}")
L.append("")
L.append("## 审阅者备注（原样）")
L.append("")
L.append("（无）" if not notes else notes)
L.append("")
L.append("## 重定向单元（机械初判 → 复核后最终）")
L.append("")
if overrides:
    for uid in sorted(overrides):
        e = final[uid]
        tail = ""
        if e["slot"] == "PRIMARY":
            tail = e.get("seg", "")
        elif e["slot"] == "CROSS":
            tail = ",".join(e.get("segs", []))
        vr = f"（复核范围 {e['verdict_range']}）" if "verdict_range" in e else ""
        L.append(f"- {uid}：复核判定 `{overrides[uid][1]}` → **{e['slot']}** {tail} {vr}".rstrip())
L.append("")
L.append("## 去向台账（全单元，36 份来源全部列出）")
L.append("")
for src, d in UNITS["sources"].items():
    L.append(f"### {src}")
    for u in d["units"]:
        uid = u["uid"]
        e = final[uid]
        tail = ""
        if e["slot"] == "PRIMARY":
            tail = e.get("seg", "")
        elif e["slot"] == "CROSS":
            tail = ",".join(e.get("segs", []))
        vr = f"（复核范围 {e['verdict_range']}）" if "verdict_range" in e else ""
        L.append(f"- {uid} {' '.join(e['ranges']) or '—'} → **{e['slot']}** {tail} {vr}".rstrip())
open(os.path.join(OUT, "A_POOL_REVIEW.md"), "w", encoding="utf-8").write("\n".join(L))
print("slots:", applied, "problems:", problems)
print("written A_POOL_MAP_v3.json + A_POOL_REVIEW.md")
