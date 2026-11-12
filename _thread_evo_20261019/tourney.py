"""Center tournament: one draft per candidate Center (P0 + Center + no-preface, no bead text), judged by v4;
the winning Center is the one to use. usage: python tourney.py <work> <centers_tag>  -> runs/t_<tag>_<k>"""
import json, sys
import evo, gen, node2b
work, tag = sys.argv[1], sys.argv[2]
P0 = gen.render("P0", work, "note")
LAST = "最后给我一篇鲜活的文章 能够合理化每个段落的情绪 即为什么在当前段落会感受到这个"
cands = json.loads((evo.ROOT / "evaluations" / "centers" / f"{tag}.json").read_text(encoding="utf-8"))
jobs = []
for k, c in enumerate(cands, 1):
    m = P0.replace(LAST, f"这一次，Thread 所围绕的那件事（Center）是：{c['center']}\n\n{node2b.NOPRE}\n\n" + LAST)
    for j in (1, 2):
        rid = f"tn_{tag}_{k}_r{j}"
        if not evo.done(rid):
            jobs.append(node2b.job(rid, m, {"stage": "tourney", "work": work, "center": k}))
print(len(jobs), "jobs", flush=True)
evo.run_parallel(jobs, 12)
