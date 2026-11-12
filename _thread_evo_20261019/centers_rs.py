"""Route A Center candidates from research (user 10-21: focus on the Thread; the Op.61 doing/dreaming Center beat
exile/belonging 9.0 vs 4.0 under judge_spec_v2, so Center choice matters most). No beads.
P0 Center: what matters to him + what makes it hard to settle; must NOT preview the route or the final answer.
ids: crs_<work> -> evaluations/centers/rs_<work>.json (list of {center, matters, hard, basis})"""
import json, sys
import centers, evo, seg

P = ("请先查阅关于{WORK}的可靠资料：写作背景、作曲家当时的处境、演奏家和研究者通常怎样理解它（包括常见的解读框架）、它的曲式和段落之间的关系。"
     "然后为这首曲子的「线」（Thread）提出 6 个彼此真正不同的候选 Center。\n"
     "Center 的定义（必须严格遵守）：说清楚共同的困扰——什么对这个人重要（matters），又是什么使它难以安顿（hard）。"
     "它不预告发展的路线和最后的回答：不要写他后来怎样、最后怎样、学会了什么。\n"
     "每个候选都要能贯穿下面这些段落、让每一段的情绪都能从这件事和前面的经历里得到解释：{SEG}\n"
     "用人话，不用“归属、安顿、边界、张力”这类抽象词堆砌；不要编具体情节。basis 写一两句：它依据了哪些资料或哪种常见理解，以及为什么它能贯穿这些段落。\n"
     "只输出一个 ```json 代码块：{\"candidates\": [{\"center\": \"一句话（matters + hard 合起来）\", \"matters\": \"…\", \"hard\": \"…\", \"basis\": \"…\"}]}")

if __name__ == "__main__":
    jobs = []
    for w in ("op60", "op61"):
        msg = P.replace("{WORK}", centers.WORKNAME[w]).replace("{SEG}", seg.clause(seg.load(w), "note"))
        jobs.append((f"crs_{w}", (lambda w=w, msg=msg: evo.call(f"crs_{w}", msg, prompt_text=P, meta={"stage": "center_research", "work": w}))))
    evo.run_parallel(jobs, 2)
    for w in ("op60", "op61"):
        r = evo.output(f"crs_{w}")
        if r:
            c = evo.parse_json(r)["candidates"]
            (evo.ROOT / "evaluations" / "centers" / f"rs_{w}.json").write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
            for k, x in enumerate(c, 1):
                print(w, k, x["center"])
