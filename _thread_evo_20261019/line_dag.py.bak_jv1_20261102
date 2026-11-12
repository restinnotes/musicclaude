"""10-31: does a Center that names its domain give a legible line? DAG N05 (line8: spine -> article, P0 + Center, no beads)
run with the new N04 Center (center_dag.py; per work the new-process candidate with the highest overall score: same rule for
both works), 2 runs each; then a blind legibility judge reads the old article (current Center, n8_<w>_r<best>) and the new
ones: from the article alone, can you say what he is doing, what he longs for, what the matter is about? + overall.
ids: ln_<w>_r<j> / lna_<w>_r<j> (spine), lj_<w>_<judge>.   usage: python line_dag.py lines | judge"""
import json, random, sys
import evo, gen, line8, node2b, node2i, center_dag

import os
LV = os.environ.get("LDV", "")          # 10-31: LDV=2 -> Center v2 (center_dag CDV=2), 3 runs, ids ln2_/lna2_/lj2_
W = ("op60", "op61"); R = (1, 2, 3) if LV else (1, 2)
OLD_ART = {"op60": "n8_op60_r1", "op61": "n8_op61_r2"}      # the drafts the current lines (v6) were built from


def new_center(w):
    """highest overall among the new-process candidates (fit judges' mean) -- read from the report table"""
    rows = [l.split("|") for l in (center_dag.OUT / f"{w}{LV}.md").read_text(encoding="utf-8").splitlines() if l.startswith("| N")]
    best = max(rows, key=lambda r: float(r[7]))
    return best[8].strip()


def base(w, c):
    p = gen.render("P0", w, "note")
    return p.replace(node2i.LAST, f"这一次，Thread 所围绕的那件事（Center）是：{c}\n"
                                  "这是读者回头看整首时，把各段组织起来的那件事；不是他一开始就清楚知道的事，也不是每一段都要回应的题目。\n\n" + node2i.LAST)


JUDGE = """下面是为肖邦{NAME}写的几篇“线”：一个人在这首曲子里经历的一件事，按段落写成文章（读者只读这篇，不看任何别的材料）。
请你只读文字本身，对每一篇回答：
1. 他在做什么：读完能不能说出他实际在做的是什么事（不要求职业、地名这类外部细节，但要说得出是哪一类事、对着什么或谁）？
2. 他向往或舍不得的是什么：能不能说出具体是什么？
3. 这件事是关于什么的：能不能用一句平常话说出整篇讲的是什么人生处境？
每项给 清楚 / 模糊 / 说不出，并引用一句最能说明你判断的原文。再用两三句话复述这篇的故事；最后给 legible（1–10：只读这篇，读者能不能明白这个人经历了什么）和 overall（1–10：作为这首曲子的线有多好；写得戏剧化、立场鲜明不算缺点）。

{ARTS}

只输出 json：
```json
{{"articles": [{{"id": "文章A", "doing": "清楚", "doing_quote": "…", "longing": "模糊", "longing_quote": "…", "about": "说不出", "about_quote": "…", "story": "…", "legible": 0, "overall": 0}}]}}
```"""

if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "lines":
        C = {w: new_center(w) for w in W}; print(C, flush=True)
        (center_dag.OUT / f"chosen{LV}.json").write_text(json.dumps(C, ensure_ascii=False, indent=1), encoding="utf-8")
        evo.run_parallel([node2b.job(f"lna{LV}_{w}_r{j}", base(w, C[w]) + "\n\n---\n" + line8.SPINE, {"stage": "dag_n05_spine", "work": w})
                          for w in W for j in R if not evo.done(f"lna{LV}_{w}_r{j}")], 4)
        evo.run_parallel([node2b.job(f"ln{LV}_{w}_r{j}", base(w, C[w]) + "\n\n---\n" + line8.LAY.replace("{SPINE}", evo.output(f"lna{LV}_{w}_r{j}")), {"stage": "dag_n05", "work": w})
                          for w in W for j in R if evo.done(f"lna{LV}_{w}_r{j}") and not evo.done(f"ln{LV}_{w}_r{j}")], 4)
        print({f"ln{LV}_{w}_r{j}": evo.done(f"ln{LV}_{w}_r{j}") for w in W for j in R})
    elif ph == "judge":
        import covjudge
        jobs, maps = [], {}
        for w in W:
            ns = [OLD_ART[w]] + [f"ln{LV}_{w}_r{j}" for j in R if evo.done(f"ln{LV}_{w}_r{j}")]
            for jn, model in (("g6", evo.G6), ("g56", evo.G56)):
                m = ns[:]; random.Random(f"lj{w}{jn}").shuffle(m)
                mp = {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}; maps[f"lj{LV}_{w}_{jn}"] = mp
                arts = "\n\n".join(f"【{k}】\n{evo.output(n)}" for k, n in mp.items())
                rid = f"lj{LV}_{w}_{jn}"
                jobs.append((rid, (lambda rid=rid, msg=JUDGE.format(NAME=covjudge.NAME[w], ARTS=arts), model=model: evo.call(rid, msg, model=model, meta={"stage": "dag_legible"}))))
        evo.run_parallel(jobs, 4)
        md = ["# 只读文章：看不看得懂（旧 Center 文章 vs 新 Center 文章）", ""]
        for rid, mp in maps.items():
            e = evo.parse_json(evo.output(rid) or "{}") or {}
            md += [f"## {rid}", "", "| 文章 | 来源 | 在做什么 | 向往什么 | 关于什么 | 看得懂 | 总体 | 复述 |", "|---|---|---|---|---|---|---|---|"]
            for a in e.get("articles") or []:
                src = mp.get(a.get("id"), "?"); tag = "旧 Center" if src.startswith("n8_") or src.startswith("ln_") else "新 Center"
                md.append(f"| {a.get('id')} | {tag}（{src}） | {a.get('doing')} | {a.get('longing')} | {a.get('about')} | {a.get('legible')} | {a.get('overall')} | {a.get('story', '')} |")
            md.append("")
        (center_dag.OUT / f"legible{LV}.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md))
