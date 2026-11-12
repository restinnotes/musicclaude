"""Round E2: combinations around X2 (first-person monologue), which read best in E1 by my own reading.
  X2X6 : monologue + each segment anchored on what is heard right now (whisper-to-listener)
  X2X3 : monologue + no-explaining rule
  X2X3X6 : all three
  X2 with GPT-5.6 and Gemini as writers (model variable)
Bases C4 and C6 (bead-derived centers) and PD (own line); n per cell from argv.
run ids: e2_<base>_<variant>_r<j>
"""
import sys
import evo, exp

ANCHOR = ("每一段都从这一刻耳朵里正在发生的声音开始——什么回来了、什么撤走了、什么没落下——"
          "再让“我”在这声音里想起、感到、说出什么；声音和念头要在同一刻发生。")


def msg(base, var):
    parts = [exp.X["X2"]]
    if "X3" in var:
        parts.append(exp.X["X3"])
    if "X6" in var:
        parts.append(ANCHOR)
    p = exp.P0.replace(exp.OLD_LAST, "\n\n".join(parts) + "\n\n" + exp.OLD_LAST)
    b = ("\n\n" + exp.BLOCK[base]) if exp.BLOCK[base] else ""
    return p + b + exp.MAT


if __name__ == "__main__":
    n = int(sys.argv[1])
    jobs = []
    for base in ("C4", "C6", "PD"):
        for var in ("X2X6", "X2X3", "X2X3X6"):
            for j in range(1, n + 1):
                rid = f"e2_{base}_{var}_r{j}"
                m = msg(base, var)
                if not evo.done(rid):
                    jobs.append((rid, lambda rid=rid, m=m, base=base, var=var: evo.call(rid, m, prompt_text=m[:4000], meta={"stage": "e2", "base": base, "variant": var})))
    m = msg("C4", "X2")
    for j in range(1, n + 1):
        jobs.append((f"e2_C4_X2m56_r{j}", lambda j=j: evo.call(f"e2_C4_X2m56_r{j}", m, prompt_text=m[:4000], model=evo.G56, meta={"stage": "e2", "base": "C4", "variant": "X2_gpt56"})))
        jobs.append((f"e2_C4_X2gem_r{j}", lambda j=j: evo.call_gemini(f"e2_C4_X2gem_r{j}", m, prompt_text=m[:4000], meta={"stage": "e2", "base": "C4", "variant": "X2_gemini"})))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 12)
