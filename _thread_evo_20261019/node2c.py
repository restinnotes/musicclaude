"""Node 2 round N3: stability of the best direction (P0 + one-sentence bead-derived Center, no bead text).
Centers #2, #5, #6 (stable in N1/N2) x variants base / cn (no preface) x 4 samples, GPT-6. run ids n3_<var><k>_r<j>"""
import evo, node2, node2b
jobs = []
for k in (2, 5, 6):
    for var, m in (("c", node2b.base(k)), ("cn", node2b.with_line(node2b.base(k), node2b.NOPRE))):
        for j in range(1, 5):
            rid = f"n3_{var}{k}_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, m, {"stage": "n3", "variant": var, "center": k}))
print(len(jobs), "jobs", flush=True)
evo.run_parallel(jobs, 12)
