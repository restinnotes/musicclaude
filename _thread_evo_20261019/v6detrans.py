"""10-29 (user: the line read alone must stand on its own, not translate the beads). The "trans" measurement (v6alone.py) found
w24 retells beads far more than v6 (items retelling or mixing: Op.60 44-48% -> 54-58%, Op.61 31% -> 52-64%). This pass rewrites
only the flagged items, per segment, WITHOUT showing the beads (as v6 was written): keep his own reasons, drop sensation/image
wording, if nothing is left find the reason in the line's own history or delete the item; optional arrows may go.
Flagged = 复述珠子 by either judge, or 两者都有 by both. ids: dt_<w>_<sec>_<T>.
usage: python v6detrans.py <base> <out>  -> evaluations/v6fix/<w>_<out>.json/.md"""
import json, sys
import covjudge, draft10, evo, v6fix as V

FORM = ("关系图的写法：每段先标他和 Center 的关系（还说不清 / 正在面对 / 没在想）；条目前的 → 表示由上一条引出（follows: true）；"
        "← 是跨段箭头，from 写前面某段某一条的编号，rel 取 提供理由、说明、限制、动摇、唤起、改写、失效、仍在起作用；key 是两到八个字、取自这一条原文的关键词。")
P = """下面是一条“线”（Thread）——一个人在肖邦{NAME}里经历的一件事，按段写成关系图——以及评审对其中第 {SEC} 段（第 {BARS} 小节）的意见。

这条线会和另一批人写的听感记录（珠子）并排展示：珠子写的是听这段音乐时的感受、画面、身体反应。所以线不需要再描写这些；线要做的是用他自己的经历说出他此刻为什么会这样——理由来自线前面他经历过、想过、发现过的事。只读这条线、不看任何听感记录，也要能读通。

评审指出这一段有几条在复述听感记录：把听音乐时的感受、画面、身体反应换个说法写进了线，而不是说他自己的原因（下面列出条目和评审说它复述了什么）。请重写这些条目：
- 保留其中属于他自己的原因、想法和变化；
- 去掉只是描写感受、画面、身体反应的部分（例如“身体先绷紧”“心里一松”“轻得不稳”“盼这一刻慢些”这类只说感觉的话），除非它是他心里真的发生的变化，而且说出了为什么；
- 去掉以后如果这一条没剩下他自己的原因，就从线前文已经确立的经历里找出他此刻为什么会这样，用一句平常话说出来；实在找不到，就删掉这一条；
- 没被指出的条目一字不动；不新增前史、外部事件、具体的人物关系或场景；条数不增加；用他自己的平常话，不写总结句。
跨段箭头只保留真正的前因（读线的人能看出前面那件事为什么让此刻这样）；评审判为“可有可无”的可以去掉。

{FORM}

【线全文】（方括号里是条目编号）
{LINE}

【这一段现在的样子】
{CUR}

【评审指出在复述听感的条目】
{FLAGS}

【评审判为可有可无的箭头（指向这些条目）】
{ARROWS}

只输出这一段的 json：
```json
{{"relation": "正在面对", "items": [{{"id": "{SEC}-1", "text": "……", "key": "……", "follows": false}}],
 "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}],
 "changes": [{{"id": "{SEC}-2", "what": "改写", "why": "……"}}]}}
```"""


def flags(w, base):
    per = {}
    for j in V.JUDGES:
        for x in (V.parse(f"tr_{w}_{j}_{base}") or {}).get("items") or []:
            per.setdefault(x.get("id"), {})[j] = x
    pick = {i: d for i, d in per.items() if any(v.get("label") == "复述珠子" for v in d.values())
            or all(d.get(j, {}).get("label") == "两者都有" for j in V.JUDGES)}
    arrows = {}
    for j in V.JUDGES:
        for s in (V.parse(f"al_{w}_{j}_{base}") or {}).get("sections") or []:
            for a in s.get("arrows") or []:
                if a.get("label") == "可有可无":
                    arrows.setdefault(a.get("to"), []).append(a.get("why", ""))
    return pick, arrows


def main(base, out):
    for w in ("op60", "op61"):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}
        pick, arrows = flags(w, base)
        old = {it["id"]: it for s in g["segments"] for it in s["items"]}
        jobs = {}
        for s in g["segments"]:
            sec = s["sec"]; ids = [it["id"] for it in s["items"]]
            fl = [i for i in ids if i in pick]
            if not fl:
                continue
            ftxt = "\n".join(f"- [{i}] {old[i]['text']}\n  评审说："
                             + "；".join(f"{v.get('label')}（{v.get('bead', '')}）{v.get('why', '')}" for v in pick[i].values()) for i in fl)
            atxt = "\n".join(f"- 指向 [{k}]：{'；'.join(v)}" for k, v in arrows.items() if k in ids) or "（无）"
            msg = P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], FORM=FORM, LINE=V.view(g, ids=True),
                           CUR=V.view({"center": "", "segments": [s]}, ids=True, center=False), FLAGS=ftxt, ARROWS=atxt)
            rid = f"dt_{w}_{sec}_{out}"
            jobs[sec] = rid
            if not evo.done(rid):
                jobs[sec] = (rid, msg)
        todo = [(v[0], (lambda rid=v[0], msg=v[1]: evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-detrans"}))) for v in jobs.values() if isinstance(v, tuple)]
        evo.run_parallel(todo, 14)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        newsegs = []
        for s in g["segments"]:
            sec = s["sec"]; rid = jobs.get(sec); rid = rid[0] if isinstance(rid, tuple) else rid
            e = V.parse(rid) if rid else None
            if not e or not isinstance(e.get("items"), list):
                if rid:
                    print(w, sec, "去翻译没有结果，保留原样", flush=True)
                newsegs.append(s); continue
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = e.get("relation") or s.get("relation")
            for it in ns["items"]:                      # bead claims survive with the item id; new items claim nothing
                it["explains"] = old.get(it["id"], {}).get("explains", []) if it["text"] else []
            newsegs.append(ns)
            print(f"{w} {sec}: {len(s['items'])} 条 → {len(ns['items'])} 条 | 箭头 {len(s['because'])} → {len(ns['because'])} | 改 {sum(1 for c in e.get('changes') or [] if c.get('what') != '不动')}", flush=True)
        G = V.tidy({"center": g["center"], "segments": newsegs})
        json.dump({"graph": G, "rows": rows, "base": f"{base} 去翻译"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
