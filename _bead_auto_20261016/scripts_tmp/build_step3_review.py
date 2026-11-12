# -*- coding: utf-8 -*-
"""Build STEP3-v3 review prompts as TWO split files (A/B) when the judgment
corpus exceeds one --file budget. Case-level greedy split by rendered size so
union of the two outputs covers every case exactly once. Judgment cases
verbatim: (A) NO_RANGE units, (B) OUT_OF_BOUNDS units, (C) long-span cross
units (>=6 segs or >=40 bars), (D) one compact row per normal cross unit
(flag-only; rows split like cases). Mechanical PRIMARY/CROSS stays
authoritative. Guards: each file <= 62000 chars, else hard error."""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

OUT = r"D:\musicclaude\_bead_auto_20261016\out"
SEGMENTS = [
    ("S01", 1, 3, "序奏"), ("S02", 4, 16, "第1主題"), ("S03", 17, 23, "間句"),
    ("S04", 24, 34, "第1主題（確保）"), ("S05", 35, 39, "間句"), ("S06", 40, 50, "第2主題前半"),
    ("S07", 51, 61, "第2主題前半（確保）"), ("S08", 62, 71, "第2主題後半"), ("S09", 72, 77, "間句"),
    ("S10", 78, 83, "挿入句"), ("S11", 84, 92, "第1主題（再現）"), ("S12", 93, 102, "第2主題後半（再現）"),
    ("S13", 103, 110, "第2主題前半（再現）"), ("S14", 111, 116, "終結句"),
]
LEDGER = json.load(open(os.path.join(OUT, "A36_LEDGER.json"), encoding="utf-8"))
UNITS = json.load(open(os.path.join(OUT, "A36_units.json"), encoding="utf-8"))
PRE = json.load(open(os.path.join(OUT, "A_POOL_MAP_v3_prejson.json"), encoding="utf-8"))

srcmeta = {}
for a in LEDGER["adopted"]:
    srcmeta[a["src_id"]] = {
        "model": a.get("model_name") or a.get("model_key"),
        "run": a.get("run") or a.get("job_id"),
        "channel": a.get("channel"),
        "paths": (a.get("path") and os.path.relpath(a["path"], r"D:\musicclaude")) or "?",
        "chars": a.get("chars") or 0,
    }

lookup = {}
for src, d in UNITS["sources"].items():
    for u in d["units"]:
        lookup[u["uid"]] = {"src": src, "u": u}

def covered_segs(ranges):
    hits = set()
    for sid, a_, b_, _ in SEGMENTS:
        for r in ranges:
            if not (r[1] < a_ or r[0] > b_):
                hits.add(sid)
    return sorted(hits)

def rng_str(rs):
    return ", ".join(rs) if rs else "（无）"

def block(uid, ranges_str, titles, text, note_line=None):
    src = uid.rsplit("-U", 1)[0]
    m = srcmeta.get(src, {})
    L = ["===== %s | %s | %s | %s | 路径：%s" % (
        uid, m.get("model") or "?", m.get("channel") or "?", m.get("run") or "?", m.get("paths"))]
    if titles:
        L.append("继承标题：" + " ＋ ".join(titles))
    L.append("标注小节范围：" + ranges_str)
    if note_line:
        L.append(note_line)
    L.append(text)
    return "\n".join(L)

def preamble(part_no, n_parts):
    L = ["【STEP3-v3·A 原文归段复核（分片 %d/%d；机械归段已完成，此处只做语义判定）】" % (part_no, n_parts),
         "",
         "作品：肖邦《船歌》升F大调 Op.60（单乐章，共116小节）",
         "",
         "已冻结的文献结构段（不得更改；机械映射以逐字范围为准）："]
    for s, a_, b_, name in SEGMENTS:
        L.append("%s %d–%d %s" % (s, a_, b_, name))
    L += ["", "来源清单（36 份已采用研究；A 原文已由确定性切分器切成带 UID 的单元）："]
    for src in sorted(srcmeta):
        m = srcmeta[src]
        L.append("[%s] %s | %s | %s | %s | %d chars" % (src, m["model"], m["run"], m["channel"], m["paths"], m["chars"]))
    L += ["", "切分与机械映射规则回顾（这些不需要判定）:",
          "- 单元头行内所有 mm.X[-Y] 记号＝该单元的原始小节范围（多范围保留）。",
          "- 完全落在某一段 → PRIMARY 该段；与多段有交集 → 每段各留一条 CROSS，不剪断。",
          "- 无小节记号 → NO_RANGE；任一范围端点>116 → OUT_OF_BOUNDS。",
          "- 复核绝不修改任何 A 原文文字，只决定单元去向。",
          "",
          "任务：只对下列判断用例给出判定（两个分片互不重叠；只判定本片里出现的 uid；另一片不知情，不猜测、不补全）。"]
    return "\n".join(L)

l4 = """输出（只能输出一个 ```json 代码块，代码块外不要有文字）：```json
{"NR": {"<uid>": "GLOBAL|UNCERTAIN|DROP|RANGE:mm.a-b"},
 "OOB": {"<uid>": "DROP|KEEP_GLOBAL|RANGE:mm.a-b"},
 "C":   {"<uid>": "SPLIT_AS_GLOBAL|OK_CROSS|DROP|NARROW:mm.a-b"},
 "D_flags": {"<uid>": "NARROW:mm.a-b|OK_CROSS|SPLIT_AS_GLOBAL|DROP"},
 "_notes": "≤300字中文，说明无法判定或有疑虑的单元及理由"}
```"""

def render_cases(cases):
    """cases: list of (cat, uid, text) -> one '## ' section per category."""
    L = []
    cat_names = {"NR": ("## A 部分：NO_RANGE 单元（逐条全文）→ 每条一个判定",
                        "可选值：GLOBAL（整曲全局底色/总述，进每段附件第五部分，不进读者正文）｜UNCERTAIN（无法确定，只留内部台账）｜DROP（与本批 A 素材无关或无内容价值，从 Pool 剔除）｜RANGE:mm.a-b（正文其实自带可靠小节信息；给出正确范围后按机械规则重新映射）"),
                 "OOB": ("## B 部分：OUT_OF_BOUNDS 单元（逐条全文；范围中含>116的小节号）→ 每条一个判定",
                         "可选值：DROP（无价值或错乱）｜KEEP_GLOBAL（材料本身是全局性叙述，按 GLOBAL 进入第五部分）｜RANGE:mm.a-b（能指出其中可靠的≤116子范围，之后机械重映射）"),
                 "C":  ("## C 部分：长跨度 CROSS 单元（覆盖≥6段或跨≥40小节，可能是整曲后见之明叙述）→ 每条一个判定",
                        "可选值：SPLIT_AS_GLOBAL（内容是整曲后见之明的评论/总结，按 GLOBAL 处理）｜OK_CROSS（确实是跨段连续叙述，保留在标注各段）｜DROP（与其他单元重复且无独特措辞）｜NARROW:mm.a-b（实际只属于这个小节范围，之后机械重映射）"),
                 "D":  ("## D 部分：其余 CROSS 单元逐条紧凑表（只挑出有问题的）",
                        "只在发现『范围与该单元正文自己的 mm 说法矛盾』或『明显整曲叙述被误标于某段』时，才在输出里给该 uid 判定（NARROW:mm.a-b 或 OK_CROSS 或 SPLIT_AS_GLOBAL 或 DROP）；没问题的不要出现在输出。uid | 覆盖段 | 范围 | 头行（截断显示）")}
    seen_cats = []
    for cat, uid, text in cases:
        if cat not in seen_cats:
            seen_cats.append(cat)
            L.append("")
            L.append(cat_names[cat][0])
            L.append(cat_names[cat][1])
        L.append(text)
    return "\n".join(L)

pool = PRE["pool"]
cases = []   # (cat, uid, rendered_text)
for e in pool["NO_RANGE"]:
    if e["uid"] not in lookup:
        continue
    u = lookup[e["uid"]]["u"]
    cases.append(("NR", e["uid"], block(e["uid"], rng_str(e["ranges"]), None, u["text"])))
nNR = sum(1 for c in cases if c[0] == "NR")

for e in pool["OUT_OF_BOUNDS"]:
    if e["uid"] not in lookup:
        continue
    u = lookup[e["uid"]]["u"]
    cases.append(("OOB", e["uid"], block(e["uid"], rng_str(e["ranges"]), None, u["text"])))
nOOB = sum(1 for c in cases if c[0] == "OOB")

cross_entries = []
for src, d in UNITS["sources"].items():
    for u in d["units"]:
        if u.get("flags") and any(f in ("no_range", "out_of_bounds") for f in u["flags"]):
            continue
        if u["range_main"] is None:
            continue
        segs = covered_segs([[r[0], r[1]] for r in u["ranges"]])
        if len(segs) >= 2:
            span = u["range_main"][1] - u["range_main"][0] + 1
            cross_entries.append({
                "uid": u["uid"], "segs": segs, "span": span,
                "long": (len(segs) >= 6 or span >= 40),
                "ranges": ["%d-%d" % (r[0], r[1]) for r in u["ranges"]],
                "titles": u.get("title_inherited", []),
            })
long_units = [c for c in cross_entries if c["long"]]
other_cross = [c for c in cross_entries if not c["long"]]
for e in long_units:
    u = lookup[e["uid"]]["u"]
    cases.append(("C", e["uid"],
                  block(e["uid"], rng_str(e["ranges"]), e["titles"], u["text"],
                        note_line="覆盖段：" + ",".join(e["segs"]))))
nC = len(long_units)

split_of = []  # kept for readability; actual mapping is part_map below
for e in other_cross:
    u = lookup[e["uid"]]["u"]
    row = "%s | %s | %s | %s" % (e["uid"], ",".join(e["segs"]), rng_str(e["ranges"]), u["head_line"][:90])
    cases.append(("D", e["uid"], row))
nD = len(other_cross)

# ---- greedy split by rendered size ----
corp = [len(t) for _, _, t in cases]
tot = sum(corp)
half = tot / 2.0
cut, acc = len(cases), 0
for i, sz in enumerate(corp):
    acc += sz
    if acc >= half:
        cut = i + 1
        break

files = [[], []]
for i, c in enumerate(cases):
    files[0 if i < cut else 1].append(c)

os.makedirs(os.path.join(OUT, "STEP3_inputs"), exist_ok=True)
sizes = []
for pi in (0, 1):
    ptext = preamble(pi + 1, 2) + "\n" + render_cases(files[pi]) + "\n"
    ptext += "\n" + l4 + "\n"
    ptext += "\n硬性约束：绝不编造小节归属；对不上就 UNCERTAIN（D 中不确定就不输出该项）；不新增或改写任何 A 原文；本任务只是归段复核，不生成珠子。\n"
    if len(ptext) > 62000:
        print(f"!! part {pi+1} OVER BUDGET: {len(ptext)}")
        sys.exit(2)
    p = os.path.join(OUT, "STEP3_inputs", "STEP3_review_prompt_%s.txt" % ("AB"[pi]))
    open(p, "w", encoding="utf-8").write(ptext)
    sizes.append((p, len(ptext), len(files[pi])))

for p, ln, nc in sizes:
    print("written %s chars=%d cases=%d" % (p, ln, nc))
print(f"split at case {cut}/{len(cases)}; NR={nNR} OOB={nOOB} C={nC} D={nD} corpus={tot}")
