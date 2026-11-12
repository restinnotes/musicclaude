"""10-29: second writing pass on the w28 cause plans (pl_<w>_<sec>_<plan>). Reading w28: the causes were right but the writing step
turned each segment into one or two long paragraphs (v6's short-item form lost), mixed 我/他/你, and restated the same carried
causes (不催对方 / 不是他能决定) in almost every segment. Here the segments are written IN ORDER, each seeing the new line so far:
third person 他, one item = one thing in one sentence, → for items led by the previous one, a cause already said earlier is not
said again — an arrow points back to that item and the item says only what is new now; untouched carried causes go to ⟲.
ids: w2_<w>_<sec>_<out>.  usage: python v6plan2.py <base> <plan_tag> <out>"""
import json, os, sys
import covjudge, draft10, evo, v6fix as V

WRITE = """下面是肖邦{NAME}的一条“线”（Thread，一个人在这首曲子里经历的一件事，按段写成关系图）已经写好的前面各段，以及第 {SEC} 段（第 {BARS} 小节）要写进去的几个原因。请把这一段写成关系图的条目。

这条线会和另一批人写的听感记录并排展示，那些记录写此刻听到、感到的样子；线只负责说出他自己的原因。只读这条线也要能读通。

写法：
- 用第三人称“他”；
- 每条一句话：一个原因，连同它此刻带来的变化，可以写在同一句里；不要把好几件事塞进一条长句，也不要把一件事拆成好几条。由上一条直接引出的，follows 写 true；
- 条目越少越好，这一段最多 {MAXN} 条（原来的版本是 {MAXN} 条）；
- 前面各段已经说过的东西，这里不要再说一遍。某个原因就是前面某一条说过的，用跨段箭头指回那一条（from 写它的编号，rel 取 提供理由、说明、限制、动摇、唤起、改写、失效 之一），条目里只写它此刻带来的新东西；前面的东西此刻仍在起作用、但没有新变化，就加一个 rel 为“仍在起作用”的箭头（to 写本段第一条），不写成条目；
- 只连真正的前因：读线的人能看出前面那件事为什么让此刻这样；箭头宁少勿多，一般一段不超过三个；
- 用他自己的平常话：直接说他在想什么、怕什么、想要什么；不写总结句、整齐的对照句，不由作者替他宣布“他终于明白”；
- 不写声音、画面、身体感受的描写；不新增原因以外的东西。
这一段他和整件事的关系：{REL}。

【线已经写好的前面各段】（方括号里是条目编号）
{PREV}

【这一段要写的原因】（括号里是这个原因接着的前面那件事，按原来的说法写出，请在上面找到对应的条目）
{CAUSES}

只输出 json：
```json
{{"items": [{{"id": "{SEC}-1", "text": "……", "key": "两到八个字，取自这一条原文", "follows": false, "causes": ["c1"]}}],
 "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}]}}
```"""


def main(base, plan, out):
    import v6plan
    for w in ("op60", "op61"):                 # 10-29 23:00 gpt3 blocked mid-plan: make the missing cause plans first (same PLAN prompt)
        g = V.graph_of(w, base); g6 = V.v6(w)
        K = json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]
        jobs = []
        for i, s in enumerate(g["segments"]):
            rp = f"pl_{w}_{s['sec']}_{plan}"
            if evo.done(rp):
                continue
            prev = V.view({"center": "", "segments": g["segments"][:i]}, ids=True, center=False) if i else "（这是第一段）"
            msg = v6plan.PLAN.format(NAME=covjudge.NAME[w], SEC=s["sec"], BARS=s["bars"], PREV=prev,
                                     V6SEG=V.view({"center": "", "segments": [g6["segments"][i]]}, center=False, head=False),
                                     CUR=V.view({"center": "", "segments": [s]}, center=False, head=False), BEADS=V.beads(w, s["sec"]),
                                     LIST="\n".join(f"- {k['what']}" for k in K if k["sec"] == s["sec"]) or "（无）")
            jobs.append((rp, lambda rp=rp, msg=msg: evo.call(rp, msg, model=evo.G6, meta={"stage": "v6-plan"})))
        if os.environ.get("PROBE_ONE") and jobs:     # 10-30 user: retry gpt3 every 55 min with a single real call
            jobs[0][1](); sys.exit(0 if evo.done(jobs[0][0]) else 3)
        evo.run_parallel(jobs, int(os.environ.get("PLAN_PAR", "5")))

    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}
        oldtext = {it["id"]: it["text"] for s in g["segments"] for it in s["items"]}
        done = {"center": g["center"], "segments": []}; rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        for s in g["segments"]:
            sec = s["sec"]; p = V.parse(f"pl_{w}_{sec}_{plan}") or {}; cs = p.get("causes") or []
            if not cs:
                print(w, sec, "没有原因清单，保留原样", flush=True); done["segments"].append(s); V.tidy(done); continue
            ctext = "\n".join(f"- {c.get('id')}：{c.get('cause', '')}"
                              + ("（接着前面：" + "；".join(f"「{oldtext[f]}」" for f in c.get("from") or [] if f in oldtext) + "）"
                                 if any(f in oldtext for f in c.get("from") or []) else "") for c in cs)
            prev = V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）"
            rid = f"w2_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, WRITE.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), PREV=prev, CAUSES=ctext, MAXN=len(V.v6(w)['segments'][[x['sec'] for x in V.v6(w)['segments']].index(sec)]['items'])),
                         model=evo.G6, meta={"stage": "v6-write2"})
            e = V.parse(rid) or {}
            if not isinstance(e.get("items"), list) or not e["items"]:
                print(w, sec, "没有结果，保留原样", flush=True); done["segments"].append(s); V.tidy(done); continue
            cmap = {c.get("id"): [str(b).split("-")[-1] for b in c.get("explains") or []] for c in cs}
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = s.get("relation")
            for it, raw in zip(ns["items"], e["items"]):
                it["explains"] = sorted({b for c in raw.get("causes") or [] for b in cmap.get(c, [])})
            done["segments"].append(ns); V.tidy(done)
            rows[sec] = {"edit": e, "plan": p, "check": None, "notes": [], "revised": False}
            print(f"{w} {sec}: 原因 {len(cs)} | {len(s['items'])} 条 → {len(ns['items'])} 条 | {sum(len(x['text']) for x in s['items'])} 字 → "
                  f"{sum(len(x['text']) for x in ns['items'])} 字 | 箭头 {len(ns['because'])}", flush=True)
        json.dump({"graph": done, "rows": rows, "base": f"{base} 先列原因（{plan}）再按顺序写"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(done), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
