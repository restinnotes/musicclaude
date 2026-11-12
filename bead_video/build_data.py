"""Shared timing + text data for both video versions.

Segment times come from the earlier production run's measure alignment of the same
Lipatti recording (signal QA PASS). Bead text is copied verbatim from the bead chain's
final synth outputs; paragraph display windows are split proportionally to length.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = Path(r"D:\music-experience-pipeline\runs\production\frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b")
CHAIN = Path(r"D:\musicclaude\bead_chain")
AUDIO = Path(r"D:\Barcarolle in F-Sharp Major Op 60 [ABQyjwRKJ-I]_trimmed.opus")
BG = RUN / "music" / "visualization" / "text_free_master.mp4"
DURATION = 504.0

align = {int(k): v for k, v in json.loads((RUN / "music/alignment/measure_alignment.json").read_text(encoding="utf-8")).items()}
segs = json.loads((CHAIN / "inputs/structure.json").read_text(encoding="utf-8"))["frozen_segments"]

out = []
for i, (mm, label) in enumerate(segs):
    sid = f"S{i+1:02d}"
    a, b = (int(x) for x in mm.split("-"))
    start = align[a]
    end = align.get(b + 1, DURATION)
    d = json.loads((CHAIN / "runs/final/synth" / f"{sid}.parsed.json").read_text(encoding="utf-8"))
    rb = d["reader_bead"]
    paras = [p.strip() for p in rb["body"].split("\n") if p.strip()]
    # proportional windows, with a short title-only lead-in
    lead = min(2.0, (end - start) * 0.08)
    total = sum(len(p) for p in paras)
    t = start + lead
    windows = []
    for p in paras:
        dur = (end - start - lead) * len(p) / total
        windows.append({"text": p, "start": round(t, 3), "end": round(t + dur, 3)})
        t += dur
    out.append({"id": sid, "measures": mm.replace("-", "–"), "label": label, "start": start, "end": end,
                "title": rb["title"], "paragraphs": windows})

data = {"audio": str(AUDIO), "background": str(BG), "duration": DURATION, "fps": 30, "segments": out,
        "credits": "Chopin · Barcarolle Op.60 · Dinu Lipatti"}
(ROOT / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
for s in out:
    rates = [len(p["text"]) / (p["end"] - p["start"]) for p in s["paragraphs"]]
    print(s["id"], s["measures"], f"{s['start']:.1f}-{s['end']:.1f}s", len(s["paragraphs"]), "段", f"最快 {max(rates):.1f} 字/秒")
