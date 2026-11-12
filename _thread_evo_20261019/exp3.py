"""Round E3: spread the best E2 combination (X2X3X6: monologue + no-explaining + sound-anchored) over more
bead-derived centers and two writers (GPT-6 via gpt3, Gemini 3.8 Flash via opencode).
Centers: C1..C6 from evaluations/centers/c1.json (C3 is the template "舍不得", kept as a control) + PD (own line).
run ids: e3_<base>_<writer>_r<j>
"""
import sys
import centers, evo, exp, exp2

for k in range(1, 7):
    exp.BLOCK[f"C{k}"] = centers.block(exp.CANDS[k - 1])

if __name__ == "__main__":
    n = int(sys.argv[1])
    jobs = []
    for base in ("C1", "C2", "C3", "C4", "C5", "C6", "PD"):
        m = exp2.msg(base, "X2X3X6")
        for j in range(1, n + 1):
            for w in ("g6", "gem"):
                rid = f"e3_{base}_{w}_r{j}"
                if evo.done(rid):
                    continue
                meta = {"stage": "e3", "base": base, "variant": "X2X3X6", "writer": w}
                if w == "g6":
                    jobs.append((rid, lambda rid=rid, m=m, meta=meta: evo.call(rid, m, prompt_text=m[:4000], meta=meta)))
                else:
                    jobs.append((rid, lambda rid=rid, m=m, meta=meta: evo.call_gemini(rid, m, prompt_text=m[:4000], meta=meta)))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 12)
