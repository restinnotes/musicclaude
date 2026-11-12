"""Held-out test on Op.61 with the node-2 recipe frozen on Op.60 (no retuning on Op.61):
  baseline : P0 as-is (note clause)                                 x3
  recipe   : P0 + one-sentence Center distilled from Op.61 beads + "no preface" line, for the 3 candidates covering the
             most segments                                          x3 each
Step 'centers' runs center_from_beads on the Op.61 beads; step 'gen' writes; ids h61_<variant>_r<j>.
usage: python hold61.py centers | gen
"""
import json, sys
import centers, evo, gen, node2b

P0 = gen.render("P0", "op61", "note")
LAST = "最后给我一篇鲜活的文章 能够合理化每个段落的情绪 即为什么在当前段落会感受到这个"
assert LAST in P0

if __name__ == "__main__":
    if sys.argv[1] == "centers":
        centers.find("c61", 2, "op61")
        sys.exit()
    cands = json.loads((evo.ROOT / "evaluations" / "centers" / "c61.json").read_text(encoding="utf-8"))
    top = sorted(range(len(cands)), key=lambda i: -cands[i]["segments_covered"])[:3]
    (evo.ROOT / "evaluations" / "centers" / "c61_used.json").write_text(
        json.dumps([{"k": i + 1, **cands[i]} for i in top], ensure_ascii=False, indent=1), encoding="utf-8")
    jobs = []
    for j in range(1, 4):
        jobs.append(node2b.job(f"h61_P0_r{j}", P0, {"stage": "hold61", "variant": "P0"}))
        for i in top:
            m = P0.replace(LAST, f"这一次，Thread 所围绕的那件事（Center）是：{cands[i]['center']}\n\n{node2b.NOPRE}\n\n" + LAST)
            jobs.append(node2b.job(f"h61_cn{i + 1}_r{j}", m, {"stage": "hold61", "variant": "cn", "center": i + 1}))
    jobs = [(r, f) for r, f in jobs if not evo.done(r)]
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 12)
