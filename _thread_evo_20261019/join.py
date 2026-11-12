"""Joining the finished line graph with the beads into a per-section screen plan (user 10-23: "你这个做完就正好把对接也自己想办法
做了"). Earlier alignment (align2, F round) linked every line item to bead sentences as 呈现/对照 and pinned line items to bars:
forced links, readers jumping between two texts, no 整体性. Now the line was written per section *to explain this section's
beads*, so joining only decides how one section unfolds on screen:
  - each state shows the line item(s) and the bead items that this line item explains, together (one thing: why + what);
  - every bead item appears once, verbatim, never filtered by the line; 另一种理解 beads go to a "也可以听成" state next to the
    bead they replace, never into the story; bead items the line does not explain still appear (as their own state);
  - line items keep their order and get no bars; bead items with specific bars keep bar order.
One call per section (sections are independent once the graph is fixed), then a mechanical check. Baseline for the judge:
line items first, then all bead items in bar order (the "parallel tracks" layout).
ids: jn<T>_<sec>.  usage: python join.py <T> <op60|op61>   -> evaluations/beam/<T>/join.json, join.md"""
import json, re, sys
import beam, evo, node2b, seq

BG = {"op60": "bg2_op60_fixed.json", "op61": "bg2_op61_fixed.json"}

P = ("我们在为{WORK}做一部随音乐播放的讲解视频。每一段音乐播放时，屏幕上有两种文字：\n"
     "- **线**：说明他此刻为什么会这样，理由来自前面的经历（已经写好，下面给出这一段的条目）。\n"
     "- **珠子**：另一位作者听这段音乐写下的感受，逐字原文，拆成一条条（编号如 B1.2）。\n"
     "线是照着这一段的珠子写的，用来说明这些感受为什么此刻出现。\n\n"
     "请设计第 {BARS} 小节这一段在屏幕上怎样展开，目标是**整体性**：观众读到的是同一件事——线说为什么，珠子说此刻是什么样——"
     "而不是两块各说各的内容，也不用在两边之间来回比对。\n"
     "要求：\n"
     "1. 用几个先后出现的屏幕状态（states）。每个状态写：此刻显示哪条线（line，编号；一条线可以在后面几个状态里继续留着）、"
     "此刻新出现哪些珠子条目（beads），以及观众此刻在理解什么（note，一句话）。\n"
     "2. 一条线和它所说明的珠子放在同一个或相邻的状态里。线条目按原顺序出现，不要给线定小节。\n"
     "3. 每一条珠子都必须出现且只出现一次，原文不改，不能因为和线不合就省掉；线没有说明的珠子，照样放进某个状态（可以不配线）。"
     "珠子里写明了具体小节的，按小节先后出现。\n"
     "4. 标着【另一种听法】的珠子不进线的故事：把它放进一个单独的“也可以听成”状态（alt=true），紧挨着它所替代的那颗珠子。\n"
     "5. 状态不要太碎：一般 2–5 个。\n"
     "6. 另外写出 explains：每条线说明的是哪几颗珠子（写到 B1 这一级即可），并用一句话说理由；说明不了的珠子写进 unexplained 并说理由。\n\n"
     "最后只输出一个 ```json 代码块：\n"
     '{"states": [{"line": ["S04-1"], "beads": ["B1.1", "B1.2"], "alt": false, "note": "…"}], '
     '"explains": [{"line": "S04-1", "beads": ["B1"], "why": "…"}], "unexplained": [{"bead": "B3", "why": "…"}]}\n\n'
     "# 前一段的线（供衔接）\n{PREV}\n\n# 这一段的线\n{LINE}\n\n# 这一段的珠子\n{BEADS}")


def bead_items(work, sec):
    bg = json.loads((evo.ROOT / "evaluations" / "beadgraph" / BG[work]).read_text(encoding="utf-8"))["items"][sec]
    st = json.loads((seq.STRUCT / f"{sec}.json").read_text(encoding="utf-8"))
    role = {b["id"]: b["role"] for b in st["beads"]}
    alt_of = {}   # bead -> the bead it cannot hold together with (STRUCT relation 另一种理解); role-less pairs: b is the alternative of a
    for r in st.get("relations") or []:
        if r.get("type") == "另一种理解":
            a, b = r.get("a"), r.get("b")
            if role.get(a) == "另一种理解":
                alt_of.setdefault(a, b)
            else:
                alt_of.setdefault(b, a)
    out = []
    for bid, its in bg.items():
        for i, it in enumerate(its):
            out.append({"id": f"{bid}.{i + 1}", "bead": bid, "role": role.get(bid, ""), "alt_of": alt_of.get(bid),
                        "bars": it.get("bars") or "", "kind": it.get("kind") or "", "text": it.get("text_display") or it["text"]})
    return out


def bead_block(items):
    lines = []
    for it in items:
        r = it["role"]
        tag = (f"另一种听法，和 {it['alt_of']} 不能同时成立" if it["alt_of"] else "另一种听法") if (r == "另一种理解" or it["alt_of"]) else r
        lines.append(f"- {it['id']}【{tag}】（{it['bars']}·{it['kind']}）{it['text']}")
    return "\n".join(lines)


def line_block(seg, allseg):
    by = {it["id"]: (s["bars"], it) for s in allseg for it in s["items"]}; out = []
    for i, it in enumerate(seg["items"]):
        out.append(f"- {it['id']}：{'→ ' if it.get('follows') and i else ''}{it['text']}")
        for b in seg.get("because") or []:
            if b["to"] == it["id"] and b["from"] in by:
                out.append(f"    ← {b['rel']}：（{by[b['from']][0]}）「{by[b['from']][1].get('key') or ''}」")
    return "\n".join(out)


def check(plan, seg, items):
    ids = [x["id"] for x in items]; seen = [b for s in plan.get("states") or [] for b in s.get("beads") or []]
    own = {it["id"] for it in seg["items"]}
    lines = [l for s in plan.get("states") or [] for l in s.get("line") or [] if l in own]   # the previous section's line may be carried
    first = []
    for l in lines:
        if l not in first:
            first.append(l)
    return {"missing_beads": [i for i in ids if i not in seen], "dup_beads": sorted({b for b in seen if seen.count(b) > 1}),
            "unknown_beads": [b for b in seen if b not in ids], "missing_lines": [it["id"] for it in seg["items"] if it["id"] not in lines],
            "line_order_ok": first == [it["id"] for it in seg["items"] if it["id"] in first]}


def render(T, work, plans):
    g = json.loads((beam.OUT / T / "graph.json").read_text(encoding="utf-8"))
    md = [f"# {beam.CFG[work]['Op']}｜线与珠子：每段在屏幕上怎样展开（{T}）\n",
          f"**Center：**{g.get('center')}\n",
          "每段若干屏：**线**（为什么）和它所说明的**珠子**（此刻是什么样，原文）同屏出现；“也可以听成”是和某颗珠子不能同时成立的另一种听法。\n"]
    for seg, sec in zip(g["segments"], beam.SECS):
        items = {x["id"]: x for x in bead_items(work, sec)}
        lt = {it["id"]: it["text"] for s2 in g["segments"] for it in s2["items"]}   # a state may carry the previous section's line
        plan = plans.get(sec) or {}
        md.append(f"\n---\n\n## {seg['bars']}　（{seg.get('relation')}）\n")
        shown = set(); last = None
        for k, s in enumerate(plan.get("states") or []):
            md.append(f"**屏 {k + 1}{'　也可以听成' if s.get('alt') else ''}**\n")   # the planner's note stays in join.json (less to read)
            # the line region persists on screen (round 4: advisors saw screens with beads but no line): a state without
            # its own line keeps the last line shown, marked (续)
            for l in (s.get("line") or ([] if s.get("alt") else [last] if last else [])):
                own = l.startswith(sec + "-")
                md.append(f"> **线**　{lt.get(l, l)}" + ("　<small>(续)</small>" if l in shown else "" if own else "　<small>(承上段)</small>"))
                shown.add(l); last = l
            if s.get("line") or (last and not s.get("alt")):
                md.append("")
            for b in s.get("beads") or []:
                if b in items:
                    md.append(f"- {items[b]['text']}　<small>{items[b]['bars']}</small>")
            md.append("")
    (beam.OUT / T / "join.md").write_text("\n".join(md), encoding="utf-8")
    return beam.OUT / T / "join.md"


if __name__ == "__main__":
    T, work = sys.argv[1], sys.argv[2]
    beam.setup(work)
    g = json.loads((beam.OUT / T / "graph.json").read_text(encoding="utf-8"))
    jobs = []
    for i, (seg, sec) in enumerate(zip(g["segments"], beam.SECS)):
        rid = f"jn{T}_{sec}"
        if evo.done(rid):
            continue
        prev = line_block(g["segments"][i - 1], g["segments"]) if i else "（这是第一段）"
        m = beam.fill(P, work, BARS=seg["bars"], PREV=prev, LINE=line_block(seg, g["segments"]), BEADS=bead_block(bead_items(work, sec)))
        jobs.append(node2b.job(rid, m, {"stage": "join", "sec": sec}, w="g6"))
    evo.run_parallel(jobs, 7)
    plans, checks = {}, {}
    for seg, sec in zip(g["segments"], beam.SECS):
        r = seq.parse(evo.output(f"jn{T}_{sec}")) or {}
        plans[sec] = r; checks[sec] = check(r, seg, bead_items(work, sec))
    (beam.OUT / T / "join.json").write_text(json.dumps({"plans": plans, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {s: c for s, c in checks.items() if c["missing_beads"] or c["dup_beads"] or c["unknown_beads"] or c["missing_lines"] or not c["line_order_ok"]}
    print(T, "join checks: bad sections", len(bad), json.dumps(bad, ensure_ascii=False)[:800], flush=True)
    print(render(T, work, plans), flush=True)
