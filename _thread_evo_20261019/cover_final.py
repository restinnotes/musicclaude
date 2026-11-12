"""Coverage of the two final lines (10-27): the same bead-coverage judge as covjudge.py, both judges, on final_line.json.
ids: cvF_<work>_<judge>.  usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python cover_final.py"""
import json
import covjudge, evo, node2b, segcheck


def msg(w):
    line = json.loads((evo.ROOT / "evaluations" / "synth" / f"P3a_{w}" / "final_line.json").read_text(encoding="utf-8"))
    segs = segcheck.seg.load(w)["segments"]; by = {s["sec"]: s for s in line["sections"]}
    body = "\n\n".join(f"**{s['id']}　第 {s['start']}–{s['end']} 小节**\n" + "\n".join(f"{it['feel']} {it.get('why', '')}" for it in by[s["id"]]["items"])
                       for s in segs)
    return (evo.rd(evo.ROOT / "prompts" / "judge_cover_v1.md").replace("{NAME}", covjudge.NAME[w])
            + "\n\n# 听感记录\n\n" + covjudge.bead_text(w) + "\n\n# Thread 稿\n\n" + body)


evo.run_parallel([node2b.job(f"cvF_{w}_{j}", msg(w), {"stage": "cover-final", "work": w}, w=j) for w in ("op60", "op61") for j in covjudge.JUDGES], 4)
for w in ("op60", "op61"):
    bs = [b for b in covjudge.beads(w) if b["role"] != "演奏条件"]; rs = {}
    for j in covjudge.JUDGES:
        try:
            rs[j] = {x["id"]: x for x in evo.parse_json(evo.output(f"cvF_{w}_{j}")).get("beads", [])}
        except Exception:
            rs[j] = {}
    strict = [b["id"] for b in bs if all(rs[j].get(b["id"], {}).get("label") == "解释了" for j in rs)]
    loose = [b["id"] for b in bs if any(rs[j].get(b["id"], {}).get("label") == "解释了" for j in rs)]
    opp = [b["id"] for b in bs if all(rs[j].get(b["id"], {}).get("label") == "相反" for j in rs)]
    out = {"strict": len(strict), "loose": len(loose), "total": len(bs), "both_opposite": opp,
           "missing_strict": [b["id"] for b in bs if b["id"] not in strict]}
    (evo.ROOT / "evaluations" / "synth" / f"P3a_{w}" / "final_coverage.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(w, "final coverage strict", out["strict"], "/", out["total"], "loose", out["loose"], "both-opposite", opp, flush=True)
