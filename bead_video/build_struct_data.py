"""Display plan (gpt3 display stage) + measure alignment -> timed data for the STRUCT-driven video.
Usage: python build_struct_data.py <display_tag>
No text is written or edited here; only measure->seconds conversion and timing layout.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAIN = Path(r"D:\musicclaude\bead_chain")
RUN = Path(r"D:\music-experience-pipeline\runs\production\frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b")
TAG = sys.argv[1] if len(sys.argv) > 1 else "disp1"
DURATION = 504.0

align = {int(k): v for k, v in json.loads((RUN / "music/alignment/measure_alignment.json").read_text(encoding="utf-8")).items()}
segs = json.loads((CHAIN / "inputs/structure.json").read_text(encoding="utf-8"))["frozen_segments"]


def span(s):
    m = re.findall(r"\d+", s or "")
    return (int(m[0]), int(m[-1])) if m else None


out = []
for i, (mm, label) in enumerate(segs):
    sid = f"S{i+1:02d}"
    a, b = (int(x) for x in mm.split("-"))
    s0, s1 = align[a], align.get(b + 1, DURATION)
    p = CHAIN / "runs" / TAG / "display" / f"{sid}.parsed.json"
    syn = json.loads((CHAIN / "runs/final/synth" / f"{sid}.parsed.json").read_text(encoding="utf-8"))
    seg = {"id": sid, "measures": mm.replace("-", "–"), "label": label, "start": s0, "end": s1,
           "title": syn["reader_bead"]["title"], "steps": [], "base": [], "readings": [], "carryover": []}
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        steps = d.get("steps", [])
        starts = []
        for st in steps:
            sp = span(st.get("measures")) or (a, b)
            starts.append(align.get(max(a, min(sp[0], b)), s0))
        starts[0] = s0
        for k, st in enumerate(steps):
            t0 = starts[k]
            t1 = starts[k + 1] if k + 1 < len(steps) else s1
            if t1 <= t0:
                t1 = t0 + 0.5
            seg["steps"].append({"measures": st.get("measures"), "start": t0, "end": t1, "music": st.get("music", ""),
                                 "now": st.get("now", []), "also": st.get("also", [])})
        seg["base"] = d.get("base", [])
        seg["carryover"] = d.get("carryover", [])
        rs = d.get("readings", [])
        # readings rotate through the whole segment, one at a time
        if rs:
            w = (s1 - s0) / len(rs)
            seg["readings"] = [{**r, "start": s0 + j * w, "end": s0 + (j + 1) * w, "n": j + 1, "of": len(rs)} for j, r in enumerate(rs)]
    out.append(seg)

data = {"duration": DURATION, "fps": 30, "credits": "Chopin · Barcarolle Op.60 · Dinu Lipatti",
        "measures": sorted([[k, v] for k, v in align.items()]), "segments": out}
(ROOT / "remotion_b/src/struct.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
for s in out:
    print(s["id"], len(s["steps"]), "步", sum(len(x["now"]) + len(x["also"]) for x in s["steps"]), "+", len(s["base"]), "底色", len(s["readings"]), "读法")
