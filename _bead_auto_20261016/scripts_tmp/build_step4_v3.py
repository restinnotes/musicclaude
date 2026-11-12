# -*- coding: utf-8 -*-
"""Render 14 STEP4-v3 prompts (template 04 verbatim + reviewed A-pool attach).
Attach layout follows previous round's structure 一–五, but units are proper:
  一 PRIMARY verbatim units; 二 CROSS verbatim (full text reappears per segment);
  三 UNCERTAIN head-only; 四 per-source provenance tables; 五 GLOBAL preamble text.
{{PUBLISHED_STRUCTURE_CONTEXT}} extracted verbatim from previous round prompts.
Guard: prompt file must stay <=62000 chars (gpt2 --file limit 65536).
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\musicclaude\_bead_auto_20261016"
OUT = os.path.join(ROOT, "out")
PREV = os.path.join(OUT, "STEP4_inputs")
TEMPLATE = open(os.path.join(
    ROOT, "music_bead_published_structure_only_20261015", "prompts",
    "04_固定乐段Aonly珠子.txt"), encoding="utf-8").read()
SEGMENTS = [
    ("S01", 1, 3, "序奏"), ("S02", 4, 16, "第1主題"), ("S03", 17, 23, "間句"),
    ("S04", 24, 34, "第1主題（確保）"), ("S05", 35, 39, "間句"), ("S06", 40, 50, "第2主題前半"),
    ("S07", 51, 61, "第2主題前半（確保）"), ("S08", 62, 71, "第2主題後半"), ("S09", 72, 77, "間句"),
    ("S10", 78, 83, "挿入句"), ("S11", 84, 92, "第1主題（再現）"), ("S12", 93, 102, "第2主題後半（再現）"),
    ("S13", 103, 110, "第2主題前半（再現）"), ("S14", 111, 116, "終結句"),
]
MAP = json.load(open(os.path.join(OUT, "A_POOL_MAP_v3.json"), encoding="utf-8"))
LEDGER = json.load(open(os.path.join(OUT, "A36_LEDGER.json"), encoding="utf-8"))
ALLUNITS = json.load(open(os.path.join(OUT, "A36_units.json"), encoding="utf-8"))

unit_text = {}
for src, d in ALLUNITS["sources"].items():
    for u in d["units"]:
        unit_text[u["uid"]] = u

srcmeta = {}
for a in LEDGER["adopted"]:
    srcmeta[a["src_id"]] = {
        "model": a.get("model_name") or a.get("model_key") or "?",
        "channel": a.get("channel") or ("int" if "-int" in (a.get("group") or "") else "web"),
        "runjob": (a.get("run") + " s" + str(a.get("sample", ""))) if a.get("run") else (a.get("job_id") or "?"),
        "path": (a.get("path") and os.path.relpath(a["path"], r"D:\musicclaude")) or "?",
        "sha": (a.get("sha256") or "")[:12],
    }

def prev_context(sid):
    p = os.path.join(PREV, f"STEP4_prompt_{sid}.txt")
    if not os.path.isfile(p):
        raise SystemExit(f"missing previous prompt {p}")
    t = open(p, encoding="utf-8").read()
    i = t.find("本段在文献中的结构标签及可核对位置（不要求自行读谱）：")
    if i < 0:
        raise SystemExit(f"no context marker in {p}")
    i += len("本段在文献中的结构标签及可核对位置（不要求自行读谱）：")
    j = t.find("\n你负责整理", i)
    ctx = t[i:j].strip("\n")
    return ctx.strip()

def unit_head(uid, cross_note=""):
    e = MAP["units"][uid]
    src = e["src"]
    m = srcmeta.get(src, {})
    rng = ", ".join(e["ranges"]) if e["ranges"] else "（无）"
    head = f"[{uid}｜{m.get('model')}｜{m.get('channel')}｜{m.get('runjob')}] 范围：{rng}"
    if cross_note:
        head += f"｜{cross_note}"
    if e.get("title_inherited"):
        head += "（继承标题：" + " ＋ ".join(e["title_inherited"]) + "）"
    return head

def unit_block(uid, cross_note=""):
    return unit_head(uid, cross_note) + "\n" + unit_text[uid]["text"].rstrip()

WIDE_T = 4
COVERAGE = {}   # cross uid -> sorted segs, from final map (review reroutes included)
for uid, e in MAP["units"].items():
    if e["slot"] == "CROSS" and e.get("segs"):
        COVERAGE[uid] = list(e["segs"])

def render(sid, a, b, label, wide_t=WIDE_T):
    segentries = [e for e in MAP["segments"][sid]["entries"]]
    prims = [e for e in segentries if e["slot"] == "PRIMARY"]
    cross = [e for e in segentries if e["slot"] == "CROSS"]
    unc = MAP["uncertain"]
    glob_l = MAP["global"]
    drop = MAP["drop"]
    A = []
    A.append(f"【STEP4·本段A Pool附件 · {sid} mm.{a}-{b} {label} · 复核后摘录，未改一字】")
    A.append(f"来源：A_POOL_MAP_v3.json（36份已采用研究全部入库；本附件含 PRIMARY {len(prims)} 条＋CROSS {len(cross)} 条（≤3段者全文在覆盖的各段逐字重复；≥4段的WIDE条仅在首个覆盖段全文，其余覆盖段只留头行）"
             f"；全局底色 GLOBAL 共 {len(glob_l)} 条未随本段收录（单提示字节上限，全量逐字见 A_POOL_MAP_v3.json 台账；本段珠子不得引用、不得自行编造整曲总述）；"
             f"NOT-COUNTED 不采样：DROP 共 {len(drop)} 条已剔除）。模型身份只作来源元数据，不作风格权重。")
    A.append("")
    A.append(f"===== 一、本段PRIMARY逐条（共{len(prims)}条；全文verbatim，首行为单元自带标题行） =====")
    if prims:
        for e in prims:
            A.append("")
            A.append(unit_block(e["uid"]))
    else:
        A.append("（本段无PRIMARY条目）")
    A.append("")
    A.append(f"===== 二、本段CROSS_SEGMENT逐条（共{len(cross)}条；覆盖≤{wide_t-1}段者全文逐字出现，WIDE条（≥{wide_t}段）仅首个覆盖段全文） =====")
    kept_c = 0; marked_c = 0
    if cross:
        for e in cross:
            segs = COVERAGE.get(e["uid"]) or e.get("segs") or []
            A.append("")
            if len(segs) >= wide_t and sid != (segs[0] if segs else sid):
                m = unit_head(e["uid"])
                A.append(m + f"｜WIDE跨段条：全文逐字收录于{segs[0]}附件，本段不重复收录全文；本段珠子不得引用或扩写该单元正文")
                marked_c += 1
            else:
                A.append(unit_block(e["uid"], cross_note="覆盖段：" + ",".join(segs)))
                kept_c += 1
    else:
        A.append("（本段无CROSS条目）")
    A.append("")
    A.append(f"===== 三、UNCERTAIN 内部台账（共{len(unc)}条；仅头部与范围，全文不进附件；读者正文不得使用这批材料） =====")
    if unc:
        for e in unc:
            A.append(f"- {e['uid']}（来源{e['src']}）范围：{', '.join(e['ranges']) or '（无）'}")
    else:
        A.append("（无）")
    A.append("")
    A.append("===== 四、本段素材来源清单（每行的UID＝本段附件中出现过的单元） =====")
    used = []
    seen = set()
    for e in prims + cross:
        if e["uid"] not in seen:
            seen.add(e["uid"])
            used.append(e)
    per_src = {}
    for e in used:
        per_src.setdefault(e["src"], []).append(e["uid"])
    if per_src:
        for src in sorted(per_src):
            m = srcmeta.get(src, {})
            A.append(f"[{src}] {m.get('model')}｜{m.get('channel')}｜{m.get('runjob')}｜SHA256校验前12位:{m.get('sha')}")
            A.append(f"  本段UID：{','.join(sorted(set(per_src[src])))}")
    else:
        A.append("（无素材来源）")
    A.append("")
    A.append(f"===== 五、全局底色（GLOBAL，共{len(glob_l)}条；未随本段收录，全量逐字文本见台账 A_POOL_MAP_v3.json 的 global 部分；本段珠子不得使用全局条目内容） =====")
    A.append("（按单提示字节上限收纳策略，本段仅登记全局条目计数与其台账章节；珠子写作只依据上面一、二部分的可见条目。）")
    return "\n".join(A)

os.makedirs(os.path.join(OUT, "STEP4_inputs_v3"), exist_ok=True)
lens = []
for sid, a, b, label in SEGMENTS:
    ctx = prev_context(sid)
    attach = render(sid, a, b, label)
    fb = ""
    segid = f"{sid} mm.{a}-{b} {label}（C2冻结十四段之一，S01–S14连续覆盖1–116无重叠）"
    def compose(att):
        return (TEMPLATE
                .replace("{{WORK}}", "肖邦《船歌》升F大调 Op.60（Frederic Chopin – Barcarolle in F-sharp major, Op. 60；116小节，单乐章）")
                .replace("{{SEGMENT_ID_AND_RANGE}}", segid)
                .replace("{{A_POOL}}", f"见随附附件ATTACH_{sid}_Apool.txt（全文附后以备核对）：\n\n" + att)
                .replace("{{PUBLISHED_STRUCTURE_CONTEXT}}", ctx))
    prompt = compose(attach)
    if len(prompt.encode("utf-8")) > 60000:   # proven-pass point is 60,111B on disk
        attach = render(sid, a, b, label, wide_t=3)
        prompt = compose(attach)
        fb = " FALLBACK wide_t=3"
    p = os.path.join(OUT, "STEP4_inputs_v3", f"STEP4_prompt_{sid}.txt")
    open(p, "w", encoding="utf-8").write(prompt)
    pb = len(prompt.encode("utf-8")); ab = len(attach.encode("utf-8"))
    lens.append((sid, ab, pb))
    print(f"{sid} attach={ab:6d}B prompt={pb:6d}B" + (" !!OVER" if pb > 62000 else "") + fb)
mx = max(lens, key=lambda t: t[2])
print(f"written 14 prompts; max {mx[0]} prompt={mx[2]}B")
if mx[2] > 62000:
    print("!! PROMPT OVER BUDGET (bytes) — trim required before gpt2 call")
    sys.exit(2)
