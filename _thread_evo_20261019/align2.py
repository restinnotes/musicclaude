"""Thread–bead alignment (user 10-22: "先做对接吧"). Inputs: the Thread graph v6 (reorganized, judged) and the bead graph
(bead pipeline STRUCT cut into verbatim items, kinds audited). Links stay inside a segment; no text on either side changes.
  link types: 呈现 — the bead item is the felt form of what the thread item says (P0 Outer: the relation made perceivable)
              对照 — the bead feels different but holds at the same time (kept: heterogeneity, not an error)
  every thread item gets approximate bars; beads linked to nothing are kept and listed with their role (multiplicity rule);
  notes may not turn music into the reason ("因为音乐……所以他……" is banned — Thread is self-driven).
Outputs: evaluations/align2/al_<w>.json + _view.md (timeline per segment: thread and bead items interleaved by bars).
usage: python align2.py build | view"""
import json, re, sys
from collections import Counter
import evo, beadgraph2 as bg

OUT = evo.ROOT / "evaluations" / "align2"
THREAD = {"op60": "tg43_n8_op60_r1_r1_fix_final_o1_o2_final", "op61": "tg43_n8_op61_r2_r2_final_o1_o2b_final"}
P = ("下面是同一首曲子的两份材料，按段落对齐。\n"
     "- 线：每段几条条目（编号 T…），讲这个人此刻怎样、为什么会这样（理由来自他前面的经历），不讲音乐。\n"
     "- 珠子：每段几颗珠子（B1、B2……），每颗拆成几条（例如 B2.3），讲此刻听到什么、像什么、身体和心里有什么感觉，带小节。"
     "每颗珠子标了角色；标“另一种理解”的珠子，和它所替代的那颗不能同时成立。\n\n"
     "任务：只在同一段里连线，不改两边的任何文字。\n"
     "1. 对线的每一条，找出这一段里和它对应的珠子条目（0 到 3 条），标类型：\n"
     "   - 呈现：这条珠子是线所说的这一刻状态的可感形态——听到的、看到的、身体感觉到的；\n"
     "   - 对照：这条珠子的感受和线说的不一样，但两者可以同时成立（例如线里他在为难，珠子却是一阵单纯的甜）。不要回避这种情况，它正是两条链各自保留的东西。\n"
     "   没有真正的对应就留空，不要硬配。note 只能说“这一刻他这样，听起来是这样”，不能把音乐写成他这样的原因（不能写“因为音乐……所以他……”）。\n"
     "2. 给线的每一条定一个大致的小节（必须在这一段的小节范围内）：依据它配上的珠子条目的小节，或者它在这一段推进中的位置。\n"
     "3. 每段写 free_beads：没有配给任何线条目的珠子条目编号。它们照样保留，不要因为和线的理解不一致就去掉。\n\n"
     "只输出一个 ```json 代码块：{\"segments\": [{\"bars\": \"1–3\", \"thread\": [{\"id\": \"T1\", \"bars\": \"1–2\", "
     "\"links\": [{\"bead\": \"B1.2\", \"type\": \"呈现\", \"note\": \"…\"}]}], \"free_beads\": [\"B3.1\"]}]}\n\n")


ROLE = {"演奏条件": "另一侧面"}   # user 10-21: nothing in the product is about the performance; the experience inside stays


def role(bead):
    return ROLE.get(bead["role"], bead["role"])


# v2 (first run, 01:46): Op.60 gave 62 of 73 thread items the maximum 3 links, reused 41 bead items (one up to 4 times),
# and both pieces linked 另一种理解 beads as 呈现 of the thread (7 + 9), chaining an alternative reading into the story.
P2 = P.replace("1. 对线的每一条，找出这一段里和它对应的珠子条目（0 到 3 条），标类型：\n",
               "1. 对线的每一条，找出这一段里和它对应的珠子条目（通常 0 到 2 条），标类型。宁可少配，不要为了每条都有而硬配。"
               "每条珠子最多配给一条线（同一句珠子在视频里只出现一次）。\n", 1)
P2 = P2.replace("   没有真正的对应就留空，不要硬配。",
                "   标“另一种理解”的珠子是另一种听法，不能当成线所说状态的“呈现”：它只能标“对照”，或者留在 free_beads 里。\n"
                "   没有真正的对应就留空，不要硬配。", 1)
assert P2.count("每条珠子最多配给一条线") == 1 and P2.count("不能当成线所说状态的") == 1
# v3 (AJ61: v2 assigned bars that ran backwards in 4 segments and paired T22@144–147 with a bead at m.116; judged last)
P3 = P2.replace("2. 给线的每一条定一个大致的小节（必须在这一段的小节范围内）：依据它配上的珠子条目的小节，或者它在这一段推进中的位置。\n",
                "2. 给线的每一条定一个大致的小节（必须在这一段的小节范围内）。线的顺序就是事情发生的顺序，不能改：后一条的起始小节不能早于前一条。"
                "依据它配上的珠子条目的小节和它在这一段推进中的位置；配给它的珠子，小节必须和它定的小节重叠。不要把好几条连续的心理变化都压在同一个小节范围里。\n", 1)
assert P3 != P2


# v4 = revise v3 with the judges' notes (AJ6xc: v3 won both but under-linked — 8–14 missed links per judge, many 主体验 beads
# left free after v2's "宁可少配"; some 呈现 should be 对照; whole thread lines pinned to single bars; twice an alternative
# reading and the bead it replaces were linked to the same thread item)
REV = ("下面是一份线与珠子的对接（JSON），以及几位评审对它逐条提出的问题。请据此修改这份对接，输出修改后的完整 JSON（格式不变）。\n规则：\n"
       "- 两边的文字都不改，只改连线、类型和小节。\n"
       "- 每段主体验那颗珠子是这一段最主要的听感，原则上要配给某一条线；其他珠子有真正的对应就配上，不要因为怕硬配就大量留空。每条珠子仍然最多配给一条线。\n"
       "- 话题相近不等于呈现：珠子不是线所说状态的可感形态时，改标对照或不配。\n"
       "- 同一条线不能同时配“另一种理解”和它所替代的那颗珠子。“另一种理解”只能标对照或留在 free_beads。\n"
       "- 线的顺序不能变，后一条的起始小节不能早于前一条；线的小节给一个范围，不要把一整句钉在单独一个小节上；配给它的珠子小节要和它重叠。\n"
       "- 评审的意见如果和这些规则冲突，以规则为准；你认为评审说得不对的，可以不改。\n\n")


def load(w):
    t = json.loads((evo.ROOT / "evaluations" / "tgraph4" / f"{THREAD[w]}.json").read_text(encoding="utf-8"))
    b = json.loads((bg.OUT / f"bg2_{w}_fixed.json").read_text(encoding="utf-8"))["items"]
    st = {s["segment"]: s for s in bg.struct(w)}
    return t, b, st


def material(w):
    t, b, st = load(w); out = []; tmap, bmap = {}, {}
    for i, (seg, s) in enumerate(zip(st, t["segments"])):
        S = st[seg]; out.append(f"## {s['bars']}（{seg}·他和那件事：{s.get('relation')}）\n线：")
        for k, it in enumerate(s["items"]):
            tid = f"T{len(tmap) + 1}"; tmap[tid] = (s["bars"], it); out.append(f"{tid}：{it['text']}")
        out.append("珠子：")
        rel = {r["b"]: f"（{r['type']} {r['a']}）" for r in S.get("relations") or [] if r["type"] == "另一种理解"}
        for bead in S["beads"]:
            out.append(f"{bead['id']}｜{role(bead)}{rel.get(bead['id'], '')}")
            for k, it in enumerate(b.get(seg, {}).get(bead["id"], [])):
                bid = f"{bead['id']}.{k + 1}"; bmap[(s["bars"], bid)] = (seg, bead, it)
                out.append(f"  {bid}（{it.get('bars')}·{it.get('kind')}）{it.get('text_display') or it['text']}")
        out.append("")
    return "\n".join(out), tmap, bmap


def rng(b):
    m = re.findall(r"\d+", b or ""); return (int(m[0]), int(m[-1])) if m else (None, None)


def check(a, w):
    _, tmap, bmap = material(w); res = Counter(); bad = []; music = []; mains = []
    seen_t = set()
    for s in a["segments"]:
        lo, hi = rng(s["bars"]); linked = set()
        for x in s.get("thread") or []:
            seen_t.add(x["id"]); res["thread"] += 1
            if x["id"] not in tmap or tmap[x["id"]][0] != s["bars"]:
                bad.append(f"{s['bars']} thread {x['id']}")
            a1, b1 = rng(x.get("bars"))
            if a1 is None or a1 < lo or b1 > hi:
                bad.append(f"{s['bars']} {x['id']} bars {x.get('bars')}")
            for l in x.get("links") or []:
                res[l.get("type")] += 1; linked.add(l.get("bead"))
                if (s["bars"], l.get("bead")) not in bmap:
                    bad.append(f"{s['bars']} bead {l.get('bead')}")
                if re.search(r"因为[^。；]{0,20}(音乐|旋律|和声|声音|琶音|颤音|主题)|音乐[^。；]{0,10}(让|使|令)他", l.get("note", "")):
                    music.append(f"{s['bars']} {x['id']}: {l.get('note')}")
        beads_here = {bid for (bars, bid) in bmap if bars == s["bars"]}
        free = set(s.get("free_beads") or [])
        res["bead_items"] += len(beads_here); res["linked_bead_items"] += len(linked & beads_here)
        missing = beads_here - linked - free
        if missing:
            bad.append(f"{s['bars']} beads neither linked nor free: {sorted(missing)[:6]}")
        main = [bid for (bars, bid), (seg, bead, it) in bmap.items() if bars == s["bars"] and bead["role"] == "主体验"]
        if main and not (set(main) & linked):
            mains.append(s["bars"])
    res["thread_missing"] = len(set(tmap) - seen_t)
    use = Counter((s["bars"], l.get("bead")) for s in a["segments"] for x in s.get("thread") or [] for l in x.get("links") or [])
    alt = [f"{s['bars']} {x['id']}⇢{l.get('bead')}" for s in a["segments"] for x in s.get("thread") or [] for l in x.get("links") or []
           if l.get("type") == "呈现" and (s["bars"], l.get("bead")) in bmap and bmap[(s["bars"], l.get("bead"))][1]["role"] == "另一种理解"]
    return {"counts": dict(res), "bad": bad, "music_as_cause": music, "segments_main_bead_unlinked": mains,
            "bead_reused": sum(v > 1 for v in use.values()), "alt_as_presentation": alt,
            "links_per_item": dict(Counter(len(x.get("links") or []) for s in a["segments"] for x in s.get("thread") or [])),
            "bars_backwards": [s["bars"] for s in a["segments"] if any((rng(x.get("bars"))[0] or 0) < (rng(y.get("bars"))[0] or 0)
                                                                    for y, x in zip(s.get("thread") or [], (s.get("thread") or [])[1:]))],
            "link_bars_mismatch": [f"{s['bars']} {x['id']}〔{x.get('bars')}〕⇢{l.get('bead')}〔{bmap[(s['bars'], l.get('bead'))][2].get('bars')}〕"
                                   for s in a["segments"] for x in s.get("thread") or [] for l in x.get("links") or []
                                   if (s["bars"], l.get("bead")) in bmap and not (lambda t, b: t[0] is None or b[0] is None or (b[0] <= t[1] + 1 and b[1] >= t[0] - 1))(
                                       rng(x.get("bars")), rng(bmap[(s["bars"], l.get("bead"))][2].get("bars")))]}


def view(a, w):
    _, tmap, bmap = material(w); t, b, st = load(w); segs = {s["bars"]: s for s in t["segments"]}
    md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜线与珠子对接（时间线）", "",
          f"**Center：**{t['center']}", "",
          "每段按小节排：**线**（他此刻怎样、为什么）和 珠子（此刻听到、感到什么）交错出现。线条目下的 ⇢ 是配给它的珠子：呈现 = 可感形态；对照 = 感受不同但同时成立。"
          "最后列出没配上线的珠子（照样保留）。", ""]
    for s in a["segments"]:
        S = segs.get(s["bars"], {}); md += [f"### {s['bars']}　（{S.get('relation')}）", ""]
        rows = []
        for x in s.get("thread") or []:
            if x["id"] in tmap:
                rows.append((rng(x.get("bars"))[0] or 0, 0, x))
        for x in rows:   # thread order is the spine: never re-sort by bars (AJ61: re-sorting by bad bars scrambled the line)
            it = tmap[x[2]["id"]][1]; md.append(f"- **〔{x[2].get('bars')}〕{it['text']}**")
            for l in x[2].get("links") or []:
                bi = bmap.get((s["bars"], l.get("bead")))
                if bi:
                    seg, bead, item = bi
                    tag = "≠ 也可以听成" if l.get("type") == "另一种理解" else f"⇢ {l.get('type')}"
                    md.append(f"  - {tag}｜{l.get('bead')}·{role(bead)}·{item.get('kind')}（{item.get('bars')}）{item.get('text_display') or item['text']}")
        free = [f for f in s.get("free_beads") or [] if (s["bars"], f) in bmap]
        if free:
            md.append("- 其余珠子（未配线，照样保留）：")
            for f in free:
                seg, bead, item = bmap[(s["bars"], f)]
                md.append(f"  - {f}·{role(bead)}·{item.get('kind')}（{item.get('bars')}）{item.get('text_display') or item['text']}")
        md.append("")
    return "\n".join(md)


def baseline(w):
    """Sanity anchor for the judge: thread items spread evenly over the segment's bars, each linked to up to two bead items
    whose bars overlap its slice (all 呈现). No model. A judge that cannot tell this from a real alignment is not usable."""
    _, tmap, bmap = material(w); t, _, _ = load(w); out = {"segments": []}
    for s in t["segments"]:
        lo, hi = rng(s["bars"]); tids = [k for k, (b, _) in tmap.items() if b == s["bars"]]; n = max(1, len(tids))
        beads = [(bid, rng(item.get("bars"))) for (b, bid), (_, _, item) in bmap.items() if b == s["bars"]]; used = set(); rows = []
        for i, tid in enumerate(tids):
            a = lo + (hi - lo + 1) * i // n; z = max(a, lo + (hi - lo + 1) * (i + 1) // n - 1)
            hit = [bid for bid, (x, y) in beads if x is not None and x <= z and y >= a and bid not in used][:2]; used |= set(hit)
            rows.append({"id": tid, "bars": f"{a}–{z}" if z > a else str(a), "links": [{"bead": h, "type": "呈现", "note": ""} for h in hit]})
        out["segments"].append({"bars": s["bars"], "thread": rows, "free_beads": [bid for bid, _ in beads if bid not in used]})
    return out


def fix_alt(a, w):
    """AJ60d: v4 spread 另一种理解 beads over later thread items, turning an alternative reading into the next step of the
    story (40–50: 'pure pastoral' then 'lonely sensual drift'). Deterministic fix: an alternative's items move to the thread
    item that holds the bead it replaces, typed 另一种理解 (shown as 也可以听成, same moment); if that bead is unlinked, to free."""
    _, tmap, bmap = material(w); _, _, st = load(w); moved = 0
    for s in a["segments"]:
        seg = next(((v[0]) for (b, _), v in bmap.items() if b == s["bars"]), None)
        rel = {}
        for r in (st.get(seg, {}).get("relations") or []):
            if r["type"] == "另一种理解":
                rel.setdefault(r["b"], set()).add(r["a"]); rel.setdefault(r["a"], set()).add(r["b"])
        alts = {bead["id"] for (b, _), (_, bead, _) in bmap.items() if b == s["bars"] and bead["role"] == "另一种理解"}
        holder = {}
        for x in s.get("thread") or []:
            for l in x.get("links") or []:
                bead = l.get("bead", "").split(".")[0]
                if bead not in alts:
                    holder.setdefault(bead, x)
        for x in s.get("thread") or []:
            keep = []
            for l in x.get("links") or []:
                bead = l.get("bead", "").split(".")[0]
                if bead in alts:
                    target = next((holder[c] for c in sorted(rel.get(bead, ())) if c in holder), None)
                    if target is not None:
                        target.setdefault("alts", []).append({**l, "type": "另一种理解"}); moved += 1
                    else:
                        s.setdefault("free_beads", []).append(l.get("bead")); moved += 1
                else:
                    keep.append(l)
            x["links"] = keep
        for x in s.get("thread") or []:
            x["links"] = x.get("links", []) + x.pop("alts", [])
    return moved


JUDGE = "judge_align_v1"


def judge(eid, w, names, shuffles=2):
    import random, statistics
    tpl = evo.rd(evo.ROOT / "prompts" / f"{JUDGE}.md"); mat = material(w)[0]
    texts = {n: (OUT / f"{v}_view.md").read_text(encoding="utf-8") for n, v in names.items()}
    plan, jobs = {}, []
    for m in ("gpt6", "gpt56"):
        for k in range(1, shuffles + 1):
            ns = list(names); random.Random(f"{eid}{m}{k}").shuffle(ns); labels = {f"时间线{chr(65 + i)}": n for i, n in enumerate(ns)}
            rid = f"aj_{eid}_{m}_s{k}"; plan[rid] = labels
            msg = (tpl.replace("{WORK}", bg.struct(w)[0].get("work", "Op.60" if w == "op60" else "Op.61")).replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels))
                   + "\n\n========== 原材料（线和珠子） ==========\n" + mat + "".join(f"\n\n========== {lab} ==========\n{texts[n]}" for lab, n in labels.items()))
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, prompt_text=tpl[:400], model=evo.G6 if m == "gpt6" else evo.G56, meta={"stage": "align_judge"}))))
    evo.run_parallel(jobs, 4)
    rows = []
    for rid, labels in plan.items():
        r = evo.output(rid)
        if not r:
            continue
        j = evo.parse_json(r); rk = j.get("ranking", [])
        for lab, n in labels.items():
            g = (j.get("timelines") or {}).get(lab) or {}
            rows.append({"run": rid, "name": n, "rank": rk.index(lab) + 1 if lab in rk else None, **g})
    (OUT / f"{eid}_judge.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    keys = ("thread_spine", "presentation_fit", "contrast_vs_conflict", "timing", "bead_diversity", "one_moment_two_sides", "alive", "glance", "overall")
    for n in names:
        rs = [x for x in rows if x["name"] == n]
        if rs:
            print(n, "rank", [x["rank"] for x in rs], " ".join(f"{k}={statistics.mean(x[k] for x in rs if isinstance(x.get(k), (int, float))):.1f}" for k in keys if any(isinstance(x.get(k), (int, float)) for x in rs)), flush=True)


if __name__ == "__main__":
    ph = sys.argv[1]; OUT.mkdir(parents=True, exist_ok=True)
    if ph == "baseline":
        for w in THREAD:
            a = baseline(w); a["check"] = check(a, w)
            (OUT / f"al_{w}_base.json").write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"al_{w}_base_view.md").write_text(view(a, w), encoding="utf-8"); print(w, a["check"]["counts"])
        sys.exit()
    if ph == "revise":   # revise <w> <from suffix> <to suffix> <judge eid> <name in eval>
        w, src, dst, eid, name = sys.argv[2:7]
        a = json.loads((OUT / f"al_{w}{src}.json").read_text(encoding="utf-8")); a.pop("check", None)
        rows = [x for x in json.loads((OUT / f"{eid}_judge.json").read_text(encoding="utf-8")) if x["name"] == name]
        notes = "\n".join(f"- [{k}] {t}" for x in rows for k in ("forced_links", "missed_links", "conflicts", "timing_issues") for t in x.get(k) or [])
        rid = f"al2rev_{w}{dst}"
        if not evo.done(rid):
            evo.call(rid, REV + "========== 原材料 ==========\n" + material(w)[0] + "\n\n========== 现在的对接 ==========\n```json\n"
                     + json.dumps(a, ensure_ascii=False) + "\n```\n\n========== 评审意见 ==========\n" + notes, prompt_text=REV, model=evo.G6, meta={"stage": "align2_revise"})
        b = evo.parse_json(evo.output(rid)); b["check"] = check(b, w)
        (OUT / f"al_{w}{dst}.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"al_{w}{dst}_view.md").write_text(view(b, w), encoding="utf-8")
        c = b["check"]; print(w, dst, c["counts"], "bad", c["bad"][:3], "backwards", c["bars_backwards"], "mismatch", len(c["link_bars_mismatch"]),
                              "reused", c["bead_reused"], "alt", len(c["alt_as_presentation"]), "mains", c["segments_main_bead_unlinked"], flush=True)
        sys.exit()
    if ph == "fixalt":   # fixalt <w> <from suffix> <to suffix>
        w, src, dst = sys.argv[2:5]
        a = json.loads((OUT / f"al_{w}{src}.json").read_text(encoding="utf-8")); a.pop("check", None); n = fix_alt(a, w); a["check"] = check(a, w)
        (OUT / f"al_{w}{dst}.json").write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"al_{w}{dst}_view.md").write_text(view(a, w), encoding="utf-8")
        c = a["check"]; print(w, dst, "moved", n, c["counts"], "bad", c["bad"][:3], "backwards", c["bars_backwards"], "reused", c["bead_reused"], flush=True)
        sys.exit()
    if ph == "judge":   # judge <eid> <w> name=view_stem,...
        judge(sys.argv[2], sys.argv[3], dict(x.split("=", 1) for x in sys.argv[4].split(",")))
        sys.exit()
    pre, prompt, suf = {"build": ("al2", P, ""), "show": ("al2", P, ""), "build2": ("al2b", P2, "_b"), "show2": ("al2b", P2, "_b"),
                        "build3": ("al2c", P3, "_c"), "show3": ("al2c", P3, "_c")}[ph]
    if ph in ("build", "build2", "build3"):
        jobs = []
        for w in THREAD:
            mat = material(w)[0]
            if not evo.done(f"{pre}_{w}"):
                jobs.append((f"{pre}_{w}", (lambda w=w, mat=mat: evo.call(f"{pre}_{w}", prompt + mat, prompt_text=prompt, model=evo.G6, meta={"stage": pre}))))
        evo.run_parallel(jobs, 2)
    for w in THREAD:
        if evo.done(f"{pre}_{w}"):
            a = evo.parse_json(evo.output(f"{pre}_{w}")); a["check"] = check(a, w)
            (OUT / f"al_{w}{suf}.json").write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"al_{w}{suf}_view.md").write_text(view(a, w), encoding="utf-8")
            print(w, suf, json.dumps(a["check"], ensure_ascii=False)[:900], flush=True)
