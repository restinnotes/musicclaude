# -*- coding: utf-8 -*-
r"""Merge STEP4-v3 bead lanes (14 GPT-6w per-segment responses) into deliverable
files. Sections per response: '## ① 内部完整珠子' (full internal bead,
verbatim) and '## ② 读者版完整珠子原文' (reader text inside <box>...</box>).
Extracts SRC-…-U# citation IDs from the internal bead for the traceability
table and verifies every cited uid exists in A36_units.json.
Outputs (under out\):
  BEADS_v3_INTERNAL.md   per segment verbatim internal bead + section source lists
  READER_v3.md           per segment reader text (box content verbatim)
  BEAD_TRACE_v3.md       uid-level traceability (cited / head-only / global / dropped)
Run after all 14 lanes finish; --partial to inspect landed lanes only.
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

R = r"D:\musicclaude\_bead_auto_20261016"
BEADS = os.path.join(R, "step4_out", "beads")
OUT = os.path.join(R, "out")
SEGMENTS = [("S%02d" % i, r) for i, r in [
    (1, "mm.1-3 序奏"), (2, "mm.4-16 第1主題"), (3, "mm.17-23 間句"),
    (4, "mm.24-34 第1主題(確保)"), (5, "mm.35-39 間句"), (6, "mm.40-50 第2主題前半"),
    (7, "mm.51-61 第2主題前半(確保)"), (8, "mm.62-71 第2主題後半"), (9, "mm.72-77 間句"),
    (10, "mm.78-83 挿入句"), (11, "mm.84-92 第1主題(再現)"), (12, "mm.93-102 第2主題後半(再現)"),
    (13, "mm.103-110 第2主題前半(再現)"), (14, "mm.111-116 終結句")]]

UNITS = json.load(open(os.path.join(OUT, "A36_units.json"), encoding="utf-8"))
ALLUID = set()
for d in UNITS["sources"].values():
    for u in d["units"]:
        ALLUID.add(u["uid"])
MAP = json.load(open(os.path.join(OUT, "A_POOL_MAP_v3.json"), encoding="utf-8"))
SRCID = re.compile(r"SRC-[a-z0-9_-]+?-U\d+\b", re.IGNORECASE)
SEC1 = re.compile(r"^#{1,2}\s*①", re.M)
SEC2 = re.compile(r"^#{1,2}\s*②", re.M)

res = {}
missing = []
for sid, label in SEGMENTS:
    p = os.path.join(BEADS, "STEP4_%s.md" % sid)
    if not os.path.isfile(p):
        missing.append(sid); continue
    t = open(p, encoding="utf-8").read().lstrip("﻿")
    m1 = SEC1.search(t); m2 = SEC2.search(t)
    if not m1 or not m2 or m2.start() <= m1.start():
        print(f"{sid}: SECTION ANCHORS NOT FOUND (internal={bool(m1)} reader={bool(m2)})"); sys.exit(2)
    internal = t[m1.start():m2.start()].strip()
    reader = t[m2.start():].strip()
    ids = sorted(set(SRCID.findall(internal)))
    bad = [i for i in ids if i not in ALLUID]
    if bad:
        print(f"{sid}: !! cited uids NOT in A36_units: {bad}")
    res[sid] = {"label": label, "internal": internal, "reader": reader,
                "ids": ids, "chars": len(t), "ids_chars": None}

partial = "--partial" in sys.argv
n_ok = len(res)
if missing and not partial:
    print("lanes not landed:", missing); sys.exit(3)
print(f"lanes landed: {n_ok}/14 ({','.join(missing) or 'none'} missing)")

# ---------- reader file ----------
L = ["# READER_v3 — C2 冻结十四段读者正文（GPT-6w 原样，珠子②节逐字）", ""]
L.append("> 本轮 14 段珠子的读者版摘集。框内文字未改一字；每段首行是珠子自带标题。来源与取舍见 BEAD_TRACE_v3.md。")
for sid, label in SEGMENTS:
    if sid not in res:
        if partial:
            L.append(f"## {sid} {label}")
            L.append(""); L.append("（车道未返）"); L.append("")
        continue
    body = res[sid]["reader"]
    b0 = body.find("<box"); b1 = body.rfind("</box>")
    note = ""
    if b0 >= 0 and b1 > b0:
        inner = body[b0: b1 + 6]
    else:
        inner = body
        m = re.search(r"<box[^>]*>(.*)", body, re.S)
        inner = m.group(1) if m else body
        note = " [box-tag-unclosed, body-intact-verbatim]"
    L.append(f"## {sid} {label}{note}")
    L.append("")
    L.append(inner)
    L.append("")
open(os.path.join(OUT, "READER_v3.md"), "w", encoding="utf-8").write("\n".join(L))

# ---------- internal file ----------
L = ["# BEADS_v3_INTERNAL — 14 段内部完整珠子（STEP4-v3，GPT-6w 原样，未改一字）", ""]
L.append("> 来源：step4_out\\beads\\STEP4_SXX.md 的 ① 节。每段末附本珠子内部引用的 SRC 单元清单（机器抽取）。")
for sid, label in SEGMENTS:
    if sid not in res:
        if partial:
            L.append(f"## {sid} {label}")
            L.append(""); L.append("（车道未返）"); L.append("")
        continue
    r = res[sid]
    L.append(f"## {sid} {label} （response {r['chars']} chars，引用单元 {len(r['ids'])} 个）")
    L.append("")
    L.append(r["internal"])
    L.append("")
    L.append("<sup>本珠引用单元：" + "、".join(r["ids"]) if r["ids"] else "<sup>本珠引用单元：（未标出）" )
    L.append("</sup>")
    L.append("")
open(os.path.join(OUT, "BEADS_v3_INTERNAL.md"), "w", encoding="utf-8").write("\n".join(L))

# ---------- trace ----------
L = ["# BEAD_TRACE_v3 — 珠子↔Pool单元溯源", ""]
L.append("| 段 | 珠子引用单元数 | 引用单元（去重机器抽取） |")
L.append("|---|---|---|")
for sid, _ in SEGMENTS:
    if sid not in res:
        continue
    L.append(f"| {sid} | {len(res[sid]['ids'])} | {'，'.join(res[sid]['ids']) or '—'} |")
L.append("")
cited = {}
for sid, r in res.items():
    for u in r["ids"]:
        cited.setdefault(u, set()).add(sid)
slot_of = {uid: e["slot"] for uid, e in MAP["units"].items()}
L.append("## 单元覆盖统计")
L.append("| Slot | 单元数 | 被珠子引用过 |")
L.append("|---|---|---|")
for slot in ("PRIMARY", "CROSS", "GLOBAL", "DROP", "UNCERTAIN", "UNRESOLVED"):
    uslot = [u for u, s in slot_of.items() if s == slot]
    hit = [u for u in uslot if u in cited]
    L.append(f"| {slot} | {len(uslot)} | {len(hit)} |")
L.append("")
L.append("附注：GLOBAL 未随车道收录（见 _ATTACH_LAYOUT_v3.1.md），DROP/UNCERTAIN 按评审剔除/留存台账；引用以珠子内部标注的 SRC id 为准。")
open(os.path.join(OUT, "BEAD_TRACE_v3.md"), "w", encoding="utf-8").write("\n".join(L))
print("written READER_v3.md / BEADS_v3_INTERNAL.md / BEAD_TRACE_v3.md")
