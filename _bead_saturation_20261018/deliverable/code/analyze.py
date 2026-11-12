"""Deterministic analysis of the saturation experiment (no model calls, no text edits).

Writes runs/analysis/curves.json and runs/analysis/checks.json.
Coverage curve: reviewer's own experience list (rev1, in-segment only) weighted 核心=3 / 有价值=2 / 次要=1;
a ladder step counts an experience fully if rev2 lists it in `covers`, half if in `partial`.
"""
import json, re, sys
from pathlib import Path
import sat

OUT = sat.RUNS / "analysis"; OUT.mkdir(parents=True, exist_ok=True)
W = {"核心": 3, "有价值": 2, "次要": 1}
READ_CPS = 5.0  # comfortable on-screen Chinese reading speed, chars/second (rough)


def span(s):
    m = re.findall(r"\d+", s or ""); return (int(m[0]), int(m[-1])) if m else None


def in_seg(seg, measures):
    a, b = sat.span_seg(seg) if hasattr(sat, "span_seg") else map(int, sat.SEGS[seg][0].split("-"))
    sp = span(measures)
    return sp is not None and a <= sp[0] <= sp[1] <= b


def curve(seg, gs="gen", r1s="rev1", r2s="rev2", fs="final"):
    g, r1, r2 = sat.load(gs, seg), sat.load(r1s, seg), sat.load(r2s, seg)
    if not (g and r1 and r2):
        return None
    ex = {e["id"]: e for e in r1.get("experiences", []) if e.get("location") != "可疑或属于邻段"}
    total = sum(W.get(e.get("importance"), 1) for e in ex.values())
    core = {i for i, e in ex.items() if e.get("importance") == "核心"}
    pk = {p.get("k"): p for p in r2.get("per_k", [])}
    got = {}; chars = 0; rows = []
    for f in g["ladder"]:
        p = pk.get(f["k"], {})
        before = dict(got)
        for i in p.get("partial", []) or []:
            if i in ex: got[i] = max(got.get(i, 0), 0.5)
        for i in p.get("covers", []) or []:
            if i in ex: got[i] = 1.0
        newly = [i for i in got if got[i] > before.get(i, 0)]
        cov = sum(W.get(ex[i].get("importance"), 1) * v for i, v in got.items())
        chars += len(f.get("text", ""))
        rows.append({
            "k": f["k"], "id": f["id"], "text": f["text"], "measures": f.get("measures"),
            "gen_gain": f.get("gain"), "gen_relation": [r.get("type") for r in f.get("relation", [])],
            "gen_adds": f.get("adds"),
            "rev_case": p.get("case"), "rev_new": p.get("new_vs_earlier"), "vivid": p.get("vivid"),
            "abstract": p.get("abstract"), "conjuncture": p.get("conjuncture"), "location_ok": p.get("location_ok"),
            "worth": p.get("worth_attention"), "relation_check": p.get("relation_check"),
            "problems": p.get("problems", []),
            "newly_covered": [{"id": i, "importance": ex[i].get("importance"), "what": ex[i].get("what")} for i in newly],
            "cum_cov": round(cov / max(1, total), 3),
            "cum_core": round(sum(got.get(i, 0) for i in core) / max(1, len(core)), 3),
            "cum_chars": chars, "read_seconds": round(chars / READ_CPS),
            "sources": sorted({s.get("src") for s in f.get("sources", [])}),
        })
    fin = sat.load(fs, seg)
    uncovered = [{"id": i, "importance": e.get("importance"), "what": e.get("what")}
                 for i, e in ex.items() if got.get(i, 0) == 0]
    return {"seg": seg, "measures": sat.mm(seg), "label": sat.SEGS[seg][1],
            "seconds": round(sat.nmeas(seg) * sat.SEC_PER_MEASURE),
            "n_rev_experiences": len(ex), "n_core": len(core), "n_offsite_flagged": len(r1.get("experiences", [])) - len(ex),
            "gen_stop": g.get("stop_after"), "gen_stop_reason": g.get("stop_reason"),
            "rev_keep": (r2.get("stop_recommendation") or {}).get("keep"),
            "rev_stop_reason": (r2.get("stop_recommendation") or {}).get("reason"),
            "rev_drop_inside": (r2.get("stop_recommendation") or {}).get("drop_inside"),
            "missing": r2.get("missing", []), "template_check": r2.get("template_check"),
            "final_beads": len(fin["beads"]) if fin else None,
            "uncovered_by_ladder": uncovered, "rows": rows}


def checks(stage, seg):
    d = sat.load(stage, seg)
    if not d:
        return None
    beads = d.get("beads", [])
    bad_meas = [b["id"] for b in beads if not in_seg(seg, b.get("measures", ""))]
    q = d.get("_quotes", {})
    reader = d.get("reader", "")
    return {"seg": seg, "stage": stage, "beads": len(beads), "roles": [b.get("role") for b in beads],
            "quotes": q.get("n"), "quotes_unverified": q.get("unverified"),
            "measures_outside_segment": bad_meas, "reader_chars": len(reader),
            "reader_read_seconds": round(len(reader) / READ_CPS),
            "segment_seconds": round(sat.nmeas(seg) * sat.SEC_PER_MEASURE),
            "relations": [r.get("type") for r in d.get("relations", [])],
            "timeline_steps": len(d.get("timeline", []))}


if __name__ == "__main__":
    cv = [c for c in (curve(s) for s in sat.SEGS) if c]
    (OUT / "curves.json").write_text(json.dumps(cv, ensure_ascii=False, indent=1), encoding="utf-8")
    ck = [c for st in ("final", "prod", "nopool", "final2") for c in (checks(st, s) for s in sat.SEGS) if c]
    (OUT / "checks.json").write_text(json.dumps(ck, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in cv:
        print(c["seg"], f"{c['seconds']}s", "exp", c["n_rev_experiences"], "core", c["n_core"], "| gen_stop", c["gen_stop"],
              "rev_keep", c["rev_keep"], "final", c["final_beads"])
        for r in c["rows"]:
            print(f"   k{r['k']} {r['gen_gain']:3s} rev={r['rev_case']} worth={r['worth']} vivid={r['vivid']} cov={r['cum_cov']:.2f} core={r['cum_core']:.2f} +{len(r['newly_covered'])} chars={r['cum_chars']}")
    for c in ck:
        print(c["stage"], c["seg"], c["beads"], c["roles"], "q", c["quotes"], "bad", c["quotes_unverified"], "outside", c["measures_outside_segment"], "reader", c["reader_chars"])
