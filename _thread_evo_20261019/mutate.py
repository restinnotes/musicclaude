"""Prompt self-mutation: GPT-6 Max (gpt3) reads the current prompt + anonymized blind-judge diagnosis, proposes 3 rewrites.
usage: python mutate.py <base_version> <diagnosis.md> <tag> <n_calls>
Extracted candidates -> prompt_versions/cand_<tag>_<call>_<k>.txt (placeholders verified)."""
import re, sys
import evo
base, diag, tag, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
tpl = evo.rd(evo.ROOT / "prompts" / "mutate_v1.md")
msg = tpl.replace("{PROMPT}", evo.rd(evo.ROOT / "prompt_versions" / f"{base}.txt").strip()).replace("{DIAGNOSIS}", evo.rd(diag).strip())
jobs = [(f"mut_{tag}_{i}", (lambda i=i: evo.call(f"mut_{tag}_{i}", msg, prompt_text=tpl, meta={"stage": "mutate", "base": base}))) for i in range(1, n + 1)]
evo.run_parallel(jobs, n)
for i in range(1, n + 1):
    r = evo.output(f"mut_{tag}_{i}") or ""
    blocks = re.findall(r"```text\s*\n(.*?)```", r, re.S)
    for k, b in enumerate(blocks, 1):
        ok = "{WORK_SHORT}" in b and "{SEG}" in b
        p = evo.ROOT / "prompt_versions" / f"cand_{tag}_{i}_{k}.txt"
        p.write_text(b.strip() + "\n", encoding="utf-8")
        print(p.name, len(b), "placeholders ok" if ok else "MISSING PLACEHOLDERS")
