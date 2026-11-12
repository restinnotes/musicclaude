"""Compress the line by rewriting it in plain words (the line is the model's own text, so rewriting is allowed; beads
are never rewritten). Prompts are deliberately minimal (user 10-21: "用人话简单不损失内容").
  P  : 用人话简单地重写，不损失内容
  PL : P + 全文约 N 字
run ids: pl_<P|PL>_<thread>_r<j>
"""
import arts, evo, node2b

THREADS = {"op60": ["n6_op60_IB_own_r1", "n7_op60_IA_rs_r1"], "op61": ["n6_op61_IA_rs_r2", "n7_op61_IA_c4_r1"]}
N = {"op60": 1000, "op61": 1200}
P = "用人话简单地重写下面这篇文章，不损失内容。保留原来的分段标题。只输出重写后的文章。\n\n"
PL = "用人话简单地重写下面这篇文章，不损失内容，全文约 {N} 字。保留原来的分段标题。只输出重写后的文章。\n\n"

if __name__ == "__main__":
    jobs = []
    for w, ts in THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(t))
            for v, tpl in (("P", P), ("PL", PL.replace("{N}", str(N[w])))):
                for j in (1, 2):
                    rid = f"pl_{v}_{t}_r{j}"
                    if not evo.done(rid):
                        jobs.append(node2b.job(rid, tpl + src, {"stage": "plain", "variant": v, "thread": t, "work": w}))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 16)
