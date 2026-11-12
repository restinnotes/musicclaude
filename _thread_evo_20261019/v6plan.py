"""10-29 (user: "我们要做的 就是一篇文章能用最少的人话能够解释清楚所有珠子 我不觉得这里四个维度的component是互相冲突的").
Two steps per segment, aimed at the single goal (fewest plain words that explain every bead, the line standing on its own):
  PLAN  (sees beads, v6's segment, the current segment, the line so far, the checklist items): list the fewest psychological
        causes that together give every bead (main / in-segment change / other facet; not 另一种理解) a reason; one cause may
        cover many beads; no images, bodily sensations or sound descriptions in a cause; reuse v6's content where it is a valid cause.
  WRITE (does NOT see beads): turn the causes into the fewest line items in his own plain words, readable alone, ← where an
        earlier item is the real reason. Bead claims (explains) come from the causes each item uses.
Segments run in parallel; the line so far = base version's earlier segments. ids: pl_<w>_<sec>_<T>, wr_<w>_<sec>_<T>.
usage: python v6plan.py <base> <out>  -> evaluations/v6fix/<w>_<out>.json/.md"""
import json, sys
import covjudge, draft10, evo, v6fix as V

PLAN = """下面是肖邦{NAME}的一条“线”（Thread，一个人在这首曲子里经历的一件事）的前面各段，第 {SEC} 段（第 {BARS} 小节）原来那一版（v6）和现在这一版，以及另一批人听这一段写下的听感记录（珠子）。

线会和珠子并排展示：珠子写此刻听到、感到的具体样子；线要用他自己的经历，说出他此刻为什么会这样。我们的目标是：用最少的话，把这一段每一颗珠子的感受为什么此刻出现解释清楚，而且只读线也能读通。

这一步先不写句子，只列出这一段需要的原因：
- 每个原因是他心里的一件事：他想要什么、怕什么、发现了什么、前面哪件事让此刻不一样了。它来自线前面已经确立的经历，或这一段新发生的心理变化；
- 原因越少越好。一个原因尽量解释好几颗珠子；但主体验、段内变化、另一侧面的每一颗都要有着落（“另一种理解”不用）；
- 原因里不能出现珠子里的画面、身体感受、声音描写、比喻——只写心理。也不要把感受本身当原因（“因为他很舍不得，所以舍不得”不算）；
- 下面“清单”里是 v6 这一段已经说清的实质内容，它们本身就是成立的原因时，优先用；
- 不新增前史、外部事件、具体的人物关系或场景；全曲一直成立的背景（他在乎、对方心意未知、时间在走）不能单独当此刻的原因，要说出它此刻因为前面哪一步变了才起作用。

【线的前面各段】（方括号里是条目编号）
{PREV}

【这一段 v6 原来的样子】
{V6SEG}

【这一段现在的样子】
{CUR}

【这一段的珠子】
{BEADS}

【清单：v6 这一段的实质内容】
{LIST}

只输出 json：
```json
{{"causes": [{{"id": "c1", "cause": "一句平常话，只写心理", "from": ["S03-2"], "explains": ["B1", "B3"]}}],
 "unexplained": [{{"bead": "B4", "why": "……"}}]}}
```"""
WRITE = """下面是肖邦{NAME}的一条“线”（Thread，一个人在这首曲子里经历的一件事）的前面各段，以及第 {SEC} 段（第 {BARS} 小节）要写的几个原因。请把这一段写出来。

要求：
- 只用下面这些原因，不加别的；条目越少越好：一条可以写一个原因，也可以把两个连着的原因写进一句；
- 用他自己的平常话，像一个人在讲自己的事：直接说他在想什么、怕什么、想要什么；不写总结句、不写整整齐齐的对照句、不由作者替他宣布“他终于明白”；
- 只读这条线就要能读通：他此刻为什么这样，前因要在线里看得出来；原因来自前面某一条时，用跨段箭头指回那一条（from 写那一条的编号），关系取 提供理由、说明、限制、动摇、唤起、改写、失效、仍在起作用 之一；只连真正的前因；
- 不写声音、画面、身体感受的描写；
- 这一段他和整件事的关系：{REL}（沿用）。

【线的前面各段】（方括号里是条目编号）
{PREV}

【这一段要写的原因】
{CAUSES}

只输出 json：
```json
{{"items": [{{"id": "{SEC}-1", "text": "……", "key": "两到八个字，取自这一条原文", "follows": false, "causes": ["c1"]}}],
 "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}]}}
```"""


def main(base, out):
    for w in ("op60", "op61"):
        g = V.graph_of(w, base); g6 = V.v6(w); segs = {s["id"]: s for s in draft10.segs(w)}
        K = json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]

        def one(i):
            s = g["segments"][i]; sec = s["sec"]
            prev = V.view({"center": "", "segments": g["segments"][:i]}, ids=True, center=False) if i else "（这是第一段）"
            msg = PLAN.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], PREV=prev,
                              V6SEG=V.view({"center": "", "segments": [g6["segments"][i]]}, center=False, head=False),
                              CUR=V.view({"center": "", "segments": [s]}, center=False, head=False), BEADS=V.beads(w, sec),
                              LIST="\n".join(f"- {k['what']}" for k in K if k["sec"] == sec) or "（无）")
            rp = f"pl_{w}_{sec}_{out}"
            if not evo.done(rp):
                evo.call(rp, msg, model=evo.G6, meta={"stage": "v6-plan"})
            p = V.parse(rp) or {}
            cs = p.get("causes") or []
            if not cs:
                return sec, None
            ctext = "\n".join(f"- {c.get('id')}：{c.get('cause', '')}" + (f"（接在前面的 {'、'.join(c.get('from') or [])}）" if c.get("from") else "") for c in cs)
            mw = WRITE.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), PREV=prev, CAUSES=ctext)
            rw = f"wr_{w}_{sec}_{out}"
            if not evo.done(rw):
                evo.call(rw, mw, model=evo.G6, meta={"stage": "v6-write"})
            e = V.parse(rw) or {}
            if not isinstance(e.get("items"), list) or not e["items"]:
                return sec, None
            cmap = {c.get("id"): [str(b).split("-")[-1] for b in c.get("explains") or []] for c in cs}
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = s.get("relation")
            for it, raw in zip(ns["items"], e["items"]):
                it["explains"] = sorted({b for c in raw.get("causes") or [] for b in cmap.get(c, [])})
            return sec, (ns, {"plan": p, "write": e})
        res = evo.run_parallel([(s["sec"], (lambda i=i: one(i))) for i, s in enumerate(g["segments"])], 14)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        newsegs = []
        for s in g["segments"]:
            got = (res.get(s["sec"]) or (None, None))[1]
            if not got:
                print(w, s["sec"], "没有结果，保留原样", flush=True); newsegs.append(s); continue
            ns, rec = got; newsegs.append(ns); rows[s["sec"]] = {"edit": rec["write"], "plan": rec["plan"], "check": None, "notes": [], "revised": False}
            print(f"{w} {s['sec']}: 原因 {len(rec['plan'].get('causes') or [])} 个 | {len(s['items'])} 条 → {len(ns['items'])} 条 | "
                  f"{sum(len(x['text']) for x in s['items'])} 字 → {sum(len(x['text']) for x in ns['items'])} 字 | 解释不了 {[u.get('bead') for u in rec['plan'].get('unexplained') or []]}", flush=True)
        G = V.tidy({"center": g["center"], "segments": newsegs})
        json.dump({"graph": G, "rows": rows, "base": f"{base} 先列原因再写"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
