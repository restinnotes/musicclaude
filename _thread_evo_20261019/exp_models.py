"""E1 model variable: identical C4/base message to GPT-5.6 (gpt3) and Gemini 3.8 Flash (opencode, offline)."""
import evo, exp
m = exp.msg("C4", "base")
jobs = []
for j in (1, 2):
    jobs.append((f"e1_C4_m56_r{j}", lambda j=j: evo.call(f"e1_C4_m56_r{j}", m, prompt_text=m[:4000], model=evo.G56, meta={"stage": "e1", "base": "C4", "variant": "model_gpt56"})))
    jobs.append((f"e1_C4_mgem_r{j}", lambda j=j: evo.call_gemini(f"e1_C4_mgem_r{j}", m, prompt_text=m[:4000], meta={"stage": "e1", "base": "C4", "variant": "model_gemini"})))
evo.run_parallel(jobs, 4)
