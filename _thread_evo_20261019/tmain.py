"""Approach 1b: main line sourced from the 24 T research documents (longitudinal listening research, no Muse),
full Thread written WITHOUT beads (beads are strung on later by align/fuse). Prompt = P0 unchanged + research note.
usage: python tmain.py <n>   -> runs/tm_P0_op60_r<j>/
"""
import sys, zipfile
from pathlib import Path
import evo, gen

TDIR = Path("D:/musicclaude/_thread_20261018/inputs/T")
NOTE = ("\n\n---\n附件 T_research.zip 里有 {k} 份独立的纵向聆听研究（不同模型分别在查资料与不查资料的条件下完成）。"
        "它们讨论这首曲子从头到尾在处理什么、前面怎样改变后面。你可以从中取用、组合或反驳，也可以不用；"
        "它们不是必须复述的结论。\n")

if __name__ == "__main__":
    n = int(sys.argv[1])
    files = sorted(TDIR.glob("T-*.md"))
    assert files and not any("muse" in f.name.lower() for f in files)
    z = evo.ROOT / "inputs" / "T_research.zip"
    if not z.exists():
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.write(f, f"T/{f.name}")
    msg = gen.render("P0", "op60", "orig") + NOTE.format(k=len(files))
    jobs = [(f"tm_P0_op60_r{j}", (lambda j=j: evo.call(f"tm_P0_op60_r{j}", msg, prompt_text=msg, attach=[z],
                                                     meta={"stage": "generate", "prompt_version": "P0", "condition": "T"})))
            for j in range(1, n + 1)]
    evo.run_parallel(jobs, n)
