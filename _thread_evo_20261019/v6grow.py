"""10-31 (user: the line reads like blind back-and-forth in a maze, not DFS). A measurement "line alone" never had: does the
line explore with a direction or circle? The judge sees ONLY the line. Per segment: compared with what came before, is he in a
new place (a new way tried, a new limit found, a new understanding carried) or re-tuning the same dilemma (新 / 重复); when he
returns to an earlier place, is it clear what he brings back (带着新东西 / 原样回来 / 不是回返); does the amount of
deliberation fit the segment's label (相符 / 不符 — e.g. 没在想 but full of weighing). Whole: 有方向的探索 / 来回打转 / 介于之间.
ids: gr_<w>_<j>_<tag>.  usage: python v6grow.py <tag> [...] -> evaluations/v6fix/grow_<tag>.json/.md"""
import json, sys
from collections import Counter
import covjudge, evo, v6fix as V

P = """下面是一条“线”（Thread）：一个人在肖邦{NAME}里经历的一件事，按段写成条目。只给你这条线。每段标了他和整件事（Center）的关系：还说不清 / 正在面对 / 没在想。〔〕里是这条提到的前文。

我们想知道：这条线读起来，是一场有方向的探索——他试一种办法，走到它不管用的地方，带着这个认识再试下一种；还是在迷宫里来回打转——同一个两难一会儿这样、一会儿那样地反复微调。
注意：回到以前的地方本身不是毛病，探索也会退回来；要看的是回来时有没有带着新东西。情绪上没有解决、结尾不圆满也不是毛病。戏剧化、主观、只讲一个故事都不算缺点。

请逐段判断：
1. step：和前面相比，他这一段是到了新的地方（试了新办法、碰到新的限制、有了新的认识），还是在同一个两难上重复或微调？新 / 重复。写一句理由，说出新在哪里或重复了哪一段。
2. back：如果这一段回到了以前到过的状态，回来时是否看得出他带着什么新的认识？带着新东西 / 原样回来 / 不是回返。
3. density：这一段里他想事情、权衡的多少，和这一段的标签是否相符（例如标“没在想”，却满是权衡）？相符 / 不符。
最后整体判断：有方向的探索 / 来回打转 / 介于之间，并写出最像打转的两三处。

【线】
{LINE}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "step": "新", "step_why": "……", "back": "不是回返", "density": "相符"}}],
 "whole": "介于之间", "whole_why": "……", "loops": ["……"]}}
```"""


def run(tags):
    for T in tags:
        jobs = []
        for w in ("op60", "op61"):
            g = V.v6(w) if T == "v6" else V.graph_of(w, T)
            for j, m in V.JUDGES.items():
                rid = f"gr_{w}_{j}_{T}"
                if not evo.done(rid):
                    jobs.append((rid, (lambda rid=rid, m=m, w=w, g=g: evo.call(rid, P.format(NAME=covjudge.NAME[w], LINE=V.view(g, ids=True, center=True)),
                                                                                 model=m, meta={"stage": "v6-grow"}))))
        evo.run_parallel(jobs, 4)
        res, md = {}, [f"# 有方向的探索还是来回打转：{T}", ""]
        for w in ("op60", "op61"):
            for j in V.JUDGES:
                e = V.parse(f"gr_{w}_{j}_{T}") or {}
                S = e.get("sections") or []
                c = {k: dict(Counter(s.get(k) for s in S)) for k in ("step", "back", "density")}
                res[f"{w}_{j}"] = {"n": len(S), **c, "whole": e.get("whole"), "whole_why": e.get("whole_why"), "loops": e.get("loops")}
                print(T, w, j, "段", len(S), "| 新", c["step"].get("新", 0), "重复", c["step"].get("重复", 0),
                      "| 回返带新东西", c["back"].get("带着新东西", 0), "原样回来", c["back"].get("原样回来", 0),
                      "| 密度不符", c["density"].get("不符", 0), "| 整体", e.get("whole"), flush=True)
                md += [f"## {w} · {'gpt-6' if j == 'g6' else '5.6'}", "", f"整体：**{e.get('whole')}**。{e.get('whole_why', '')}", "",
                       "最像打转：" + "；".join(e.get("loops") or []), ""]
                md += [f"- {s.get('sec')}：{s.get('step')}（{s.get('back')}，密度{s.get('density')}）{s.get('step_why', '')}" for s in S] + [""]
        (V.OUT / f"grow_{T}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        (V.OUT / f"grow_{T}.md").write_text("\n".join(md), encoding="utf-8")


if __name__ == "__main__":
    run(sys.argv[1:])
