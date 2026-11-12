"""Stage 2b: fused rewrite (Thread + beads + alignment table -> one full text per segment). GPT-6 via gpt3.
usage: python fuse.py <work> <name,...>   (requires evaluations/align/<name>.json from align.py)
Outputs runs/f_<name>/output.txt
"""
import json, sys
import align, arts, evo, seg

if __name__ == "__main__":
    work, names = sys.argv[1], sys.argv[2].split(",")
    btxt, _ = align.beads_text()
    d = seg.load(work)
    tpl = evo.rd(evo.ROOT / "prompts" / "fuse_v1.md")
    jobs = []
    for n in names:
        aj = evo.ROOT / "evaluations" / "align" / f"{n}.md"
        if not aj.exists():
            print(n, "no alignment yet"); continue
        thread = arts.b0() if n == "B0" else arts.clean(evo.output(n))
        msg = (tpl.replace("{WORK}", d["work"]).replace("{NSEG}", str(len(d["segments"])))
               .replace("{THREAD}", thread).replace("{BEADS}", btxt).replace("{ALIGN}", evo.rd(aj)))
        jobs.append((f"f_{n}", (lambda n=n, msg=msg: evo.call(f"f_{n}", msg, prompt_text=tpl, meta={"stage": "fuse", "source": n}))))
    evo.run_parallel(jobs, 6)
