"""Judge the screen plan from join.py against a mechanical baseline (user 10-23: 对接的头号标准是整体性). Baseline = the
"parallel tracks" layout: each section shows its line items first, then every bead item in bar order. A judge that cannot
prefer a real plan over the baseline on 整体性 is not usable. Both rendered without ids; a reason for every score. 2 judges x 2 orders.
usage: python joinjudge.py <T> <op60|op61>   -> evaluations/beam/<T>/joinjudge.json"""
import json, random, sys
import beam, evo, join, node2b, seq

P = ("你是一位独立评审。我们在为{WORK}做一部随音乐播放的讲解视频。每段音乐播放时，屏幕上有两种文字：**线**（说明他此刻为什么会这样，"
     "理由来自前面的经历）和**珠子**（听这段音乐写下的感受，逐字原文；“也可以听成”是和某颗珠子不能同时成立的另一种听法）。"
     "下面是同一份材料的 {N} 种排法（{LABELS}），内容完全一样，只是每段在屏幕上怎样展开不同。\n\n"
     "评什么（每项 1–10 分，都写理由，引用具体的段）：\n"
     "1. **整体性（最重要）**：读一段，像不像同一件事——线说为什么、珠子说此刻是什么样——还是两块各说各的、要自己来回比对？\n"
     "2. **线和珠子贴不贴**：每一屏里，线和它旁边的珠子是不是在说同一刻的同一件事？有没有硬凑在一起的？\n"
     "3. **珠子的多样性**：珠子有没有被线压成一种听法？“也可以听成”有没有被串进线的故事、变成一个人接连发生的事？\n"
     "4. **好不好读**：每一屏的量是否合适，先后是否顺？\n\n"
     "最后只输出一个 ```json 代码块：\n"
     '{"ranking": ["排法A"], "layouts": {"排法A": {"wholeness": {"score": 1, "why": "…"}, "fit": {"score": 1, "why": "…"}, '
     '"diversity": {"score": 1, "why": "…"}, "readable": {"score": 1, "why": "…"}, "overall": {"score": 1, "why": "…"}}}}\n'
     "（ranking 包含全部，不许并列。）\n\n{BODY}")


def baseline(T, work):
    g = json.loads((beam.OUT / T / "graph.json").read_text(encoding="utf-8")); out = []
    for seg, sec in zip(g["segments"], beam.SECS):
        out.append(f"## {seg['bars']}\n")
        out += [f"> **线**　{it['text']}" for it in seg["items"]] + [""]
        its = join.bead_items(work, sec)
        def start(x):
            try:
                return int(str(x["bars"]).replace("约", "").split("–")[0].split("；")[0])
            except ValueError:
                return 0
        for it in sorted(its, key=start):
            out.append(f"- {it['text']}" + ("　（也可以听成）" if it["alt_of"] or it["role"] == "另一种理解" else ""))
        out.append("")
    return "\n".join(out)


def plan_text(T):
    t = (beam.OUT / T / "join.md").read_text(encoding="utf-8")
    return t[t.index("\n---\n"):]   # drop the header (center + legend) so both layouts look alike


if __name__ == "__main__":
    T, work = sys.argv[1], sys.argv[2]
    beam.setup(work)
    vers = {"plan": plan_text(T), "baseline": baseline(T, work)}
    keys = list(vers); labs = [f"排法{chr(65 + i)}" for i in range(len(keys))]; jobs = []; maps = {}
    for jn, w in (("gpt6", "g6"), ("gpt56", "g56")):
        for s in (1, 2):
            order = keys[:]; random.Random(f"jj{T}{jn}{s}").shuffle(order)
            body = "\n\n".join(f"# {lab}\n\n{vers[k]}" for lab, k in zip(labs, order))
            rid = f"jj{T}_{jn}_{s}"; maps[rid] = dict(zip(labs, order))
            if not evo.done(rid):
                jobs.append(node2b.job(rid, beam.fill(P, work, N=len(keys), LABELS="、".join(labs), BODY=body), {"stage": "joinjudge"}, w=w))
    evo.run_parallel(jobs, 4)
    res = {}
    for rid, mp in maps.items():
        r = seq.parse(evo.output(rid)) or {}
        res[rid] = {"ranking": [mp.get(x, x) for x in r.get("ranking", [])], "layouts": {mp.get(k, k): v for k, v in (r.get("layouts") or {}).items()}}
    (beam.OUT / T / "joinjudge.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for rid, r in res.items():
        print(rid, r["ranking"], {k: {m: (v.get(m) or {}).get("score") for m in ("wholeness", "fit", "diversity", "readable", "overall")}
                                 for k, v in r["layouts"].items()}, flush=True)
