"""Node 2 (Thread only) experiments, round N1. No bead text is given to the writer; beads join at nodes 3-4.
  P0     : P0 as-is (B0 generator), more samples for the reference distribution
  P0c<k> : P0 + one-sentence Center distilled from beads (candidate k), no bead text, no evidence quotes
  P0x    : P0 + "no preface/thesis, no abstract motion words" (keeps the why-now logic)
  P0 on GPT-5.6 and Gemini (writer variable)
run ids: n1_<variant>_<writer>_r<j>
"""
import json, sys
import evo, gen

P0 = gen.render("P0", "op60", "note")
LAST = "最后给我一篇鲜活的文章 能够合理化每个段落的情绪 即为什么在当前段落会感受到这个"
assert LAST in P0
CANDS = json.loads((evo.ROOT / "evaluations" / "centers" / "c1.json").read_text(encoding="utf-8"))
XLINE = ("直接从第一段开始写，不要在正文前先宣布全篇的主题或结论。不要用“摇曳”“托举”“悬着”“敞开”“更有分量”“终于”"
         "这类抽象的运动或状态词代替真正的理由；每段为什么会有这样的感受，要说出具体是前面哪一段的哪种经历、此刻音乐里发生了什么。")


def variants():
    v = {"P0": P0, "P0x": P0.replace(LAST, XLINE + "\n\n" + LAST)}
    for k in (1, 2, 4, 5, 6):
        c = CANDS[k - 1]["center"]
        v[f"P0c{k}"] = P0.replace(LAST, f"这一次，Thread 所围绕的那件事（Center）是：{c}\n\n" + LAST)
    return v


if __name__ == "__main__":
    n = int(sys.argv[1])
    V = variants(); jobs = []
    plan = [(name, "g6", n) for name in V] + [("P0", "g56", n), ("P0", "gem", n), ("P0x", "gem", n)]
    for name, w, k in plan:
        for j in range(1, k + 1):
            rid = f"n1_{name}_{w}_r{j}"
            if evo.done(rid):
                continue
            m = V[name]; meta = {"stage": "node2", "variant": name, "writer": w}
            if w == "gem":
                jobs.append((rid, lambda rid=rid, m=m, meta=meta: evo.call_gemini_direct(rid, m, prompt_text=m, meta=meta)))
            else:
                model = evo.G6 if w == "g6" else evo.G56
                jobs.append((rid, lambda rid=rid, m=m, meta=meta, model=model: evo.call(rid, m, prompt_text=m, model=model, meta=meta)))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 12)
