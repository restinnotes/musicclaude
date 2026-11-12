"""Structured product for the video step (user 10-21): per piece one JSON =
  center + per segment {bars, show{headline, link}, beads{verbatim[], condensed[]}, internal{headline, because, revises, toward, weight}}
plus a rendered markdown (show layer + beads; internal layer in a separate file).
usage: python final.py <tl_prefix: tl|tl2> -> deliverable/<work>_<thread>.json/.md"""
import json, re, sys
from pathlib import Path
import evo, plain

DEL = evo.ROOT / "deliverable"


def build(pfx, t, w):
    tl = json.loads((evo.ROOT / "evaluations" / "twolayer" / f"{pfx}_{t}_r1.json").read_text(encoding="utf-8"))
    line = f"{pfx}s_{t}_r1"
    V = {s["id"]: s["bead"] for s in json.loads((evo.ROOT / "evaluations" / "asm2" / f"V_{line}.json").read_text(encoding="utf-8"))["segments"]}
    P = {s["id"]: s["bead"] for s in json.loads((evo.ROOT / "evaluations" / "asm2" / f"P_{line}.json").read_text(encoding="utf-8"))["segments"]}
    segs = []
    for i, s in enumerate(tl["segments"], 1):
        sid = f"S{i:02d}"
        segs.append({"id": sid, "bars": s["bars"], "show": s["show"], "beads": {"verbatim": V.get(sid, []), "condensed": P.get(sid, [])},
                     "internal": s["internal"]})
    doc = {"work": w, "line_source": t, "show_source": f"{pfx}_{t}_r1", "center": tl["center"], "internal_center": tl.get("internal_center"),
           "arc": tl.get("arc"), "segments": segs,
           "notes": {"beads.condensed": "实验：珠子压成要点（改写），待用户决定是否允许", "beads.verbatim": "逐字原句（模型按与线相合挑选）"}}
    DEL.mkdir(exist_ok=True)
    (DEL / f"{w}_{t}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# {w}｜成品（显示层 + 珠子）", "", f"**{doc['center']}**", ""]
    for s in segs:
        md += [f"### {s['bars']}", "", f"**{s['show']['headline']}**"] + ([s["show"]["link"]] if s["show"]["link"] else []) + [""]
        md += [f"> {b}" for b in s["beads"]["condensed"]] + [""]
    (DEL / f"{w}_{t}_成品_珠子压成要点.md").write_text("\n".join(md), encoding="utf-8")
    md2 = [x if not x.startswith("> ") else x for x in md]
    md2 = [f"# {w}｜成品（显示层 + 逐字珠子原句）", "", f"**{doc['center']}**", ""]
    for s in segs:
        md2 += [f"### {s['bars']}", "", f"**{s['show']['headline']}**"] + ([s["show"]["link"]] if s["show"]["link"] else []) + [""]
        md2 += [f"> {b}" for b in s["beads"]["verbatim"]] + [""]
    (DEL / f"{w}_{t}_成品_珠子逐字原句.md").write_text("\n".join(md2), encoding="utf-8")
    print(w, t, len(segs), "segments", len("\n".join(md)), "chars (condensed)", len("\n".join(md2)), "chars (verbatim)")


if __name__ == "__main__":
    pfx = sys.argv[1] if len(sys.argv) > 1 else "tl"
    for w, ts in plain.THREADS.items():
        for t in ts:
            build(pfx, t, w)
