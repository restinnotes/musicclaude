"""Re-judge the corrected drafts with the OLD judge that gave N8 its 9.0 (judge_spec_v3 via calib.py, beads attached as
reference) — user 10-23: "N8 was rated very high before; how would that judge rate the corrected drafts vs N8?".
Every block holds the N8 winner n8_op60_r1 as anchor + one d9L, one d9S, one d9LC draft. All drafts are rendered with the
same "**第a—b小节**" headings (d9L/d9S drafts use other layouts) so layout cannot sway the judge.
usage: python oldjudge.py   -> evaluations/C9{A,B,C}/rows.json"""
import json, random
import calib, causal, draftjudge, evo, segcheck

BLOCKS = {"C9A": ["n8_op60_r1", "d9L_op60_r1", "d9S_op60_r1", "d9LC_op60_r1"],
          "C9B": ["n8_op60_r1", "d9L_op60_r2", "d9S_op60_r2", "d9LC_op60_r2"],
          "C9C": ["n8_op60_r1", "d9L_op60_r3", "d9S_op60_r3", "d9LC_op60_r3"]}


def uniform(n):
    segs = segcheck.seg.load("op60")["segments"]
    return "\n\n".join(f"**第{s['start']}—{s['end']}小节**\n\n{t}" for s, t in zip(segs, draftjudge.sections(n)))


if __name__ == "__main__":
    causal.text = uniform
    calib.JV[0] = "judge_spec_v3"
    import threading
    ths = []
    import sys
    only = sys.argv[1:] or list(BLOCKS)
    for eid, names in BLOCKS.items():
        if eid not in only:
            continue
        d = calib.EV / eid; d.mkdir(parents=True, exist_ok=True); plan = {}
        for jn in ("gpt6", "gpt56"):
            for s in (1, 2):
                m = names[:]; random.Random(f"{eid}{jn}{s}").shuffle(m)
                plan[f"s{s}_{jn}"] = {"judge": jn, "map": {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}}
        (d / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
        t = threading.Thread(target=calib.run, args=(eid, "op60", names, 2, ["gpt6", "gpt56"], 4)); t.start(); ths.append(t)
    for t in ths:
        t.join()
    for eid in only:
        rows = json.loads((calib.EV / eid / "rows.json").read_text(encoding="utf-8"))
        agg = {}
        for r in rows:
            agg.setdefault(r["name"], []).append(r.get("overall"))
        print(eid, {k: v for k, v in agg.items()}, flush=True)
