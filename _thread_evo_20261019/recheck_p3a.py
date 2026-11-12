"""10-27 晚校准：P3a 里检查判合格的 8 段，把当时发给检查的原文原样交给现在的 gpt3 g56（max）再判一次，
看 P4a 合格段变少是不是检查变严造成的。ids: rcP3a_<work>_<sec>"""
import json, re
import evo, node2b
SEGS = [("op60", "S02", "B2"), ("op60", "S03", "B2"), ("op60", "S08", "B2"), ("op60", "S09", "B2"), ("op60", "S10", "B"),
        ("op61", "S09", "B"), ("op61", "S12", "B"), ("op61", "S13", "B")]
jobs = []
for w, s, b in SEGS:
    msg = (evo.RUNS / f"syP3a_{w}_{s}_{b}" / "input.txt").read_text(encoding="utf-8")
    msg = msg.replace(evo.NO_WEB, "")
    if not evo.done(f"rcP3a_{w}_{s}"):
        jobs.append(node2b.job(f"rcP3a_{w}_{s}", msg, {"stage": "recheck"}, w="g56"))
evo.run_parallel(jobs, 8)
for w, s, b in SEGS:
    try:
        j = evo.parse_json(evo.output(f"rcP3a_{w}_{s}"))
        print(w, s, "现在的检查 pass =", j.get("pass"), "|", (j.get("reason") or "")[:150], flush=True)
    except Exception as e:
        print(w, s, "无结果", e, flush=True)
