"""Judge calibration with judge_v2 (stage-1 Thread criteria, bead reference attached).
usage: python calib.py <eval_id> <work> <name,...> [--shuffles 3] [--judges gpt6,gpt56,gemini]
Each shuffle presents the same articles in a different random order/labels. Names: run ids or B0.
Outputs evaluations/<eval_id>/{plan.json,rows.json} and runs/j2_<eval_id>_<block>/.
"""
import argparse, json, random
import arts, evo, seg

EV = evo.ROOT / "evaluations"
BEADFILE = "参考_各段珠子.md"


JV = ["judge_v2"]


def prompt(work, labels):
    d = seg.load(work)
    rng = "、".join(f"{s['start']}–{s['end']}" for s in d["segments"])
    t = evo.rd(evo.ROOT / "prompts" / f"{JV[0]}.md")
    return (t.replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels)).replace("{WORK}", d["work"])
            .replace("{TOTAL}", str(d["total_measures"])).replace("{RANGES}", rng).replace("{NSEG}", str(len(d["segments"])))
            .replace("{BEADFILE}", BEADFILE))


def run(eid, work, names, shuffles, judges, workers):
    out = EV / eid; out.mkdir(parents=True, exist_ok=True)
    if (out / "plan.json").exists():   # a pre-written plan defines the article set
        names = sorted({n for b in json.loads((out / "plan.json").read_text(encoding="utf-8")).values() for n in b["map"].values()})
    import causal
    texts = {n: (arts.b0() if n == "B0" else causal.text(n)) for n in names}
    import align
    bead = evo.rd(align.BEAD_READER[work])
    pf = out / "plan.json"
    if pf.exists():
        plan = json.loads(pf.read_text(encoding="utf-8"))
    else:
        plan = {}
        for jn in judges:
            for s in range(1, shuffles + 1):
                m = names[:]; random.Random(f"{eid}{jn}{s}").shuffle(m)
                plan[f"s{s}_{jn}"] = {"judge": jn, "map": {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}}
        pf.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    jobs = []
    for bid, b in plan.items():
        rid = f"{JV[0]}_{eid}_{bid}"
        if evo.done(rid):
            continue
        labels = list(b["map"]); jp = prompt(work, labels)
        adir = out / "articles" / bid; adir.mkdir(parents=True, exist_ok=True)
        files = []
        for lab, n in b["map"].items():
            p = adir / f"{lab}.md"; p.write_text(f"# {lab}\n\n" + texts[n], encoding="utf-8"); files.append(p)
        bp = adir / BEADFILE; bp.write_text(bead, encoding="utf-8")
        if b["judge"] == "gemini":
            msg = (jp + "\n\n" + "\n\n".join(f"========== {lab} ==========\n{texts[n]}" for lab, n in b["map"].items())
                   + f"\n\n========== {BEADFILE} ==========\n{bead}")
            jobs.append((rid, lambda rid=rid, msg=msg, jp=jp: evo.call_gemini_direct(rid, msg, prompt_text=jp, meta={"stage": "judge_v2"})))
        else:
            model = evo.G6 if b["judge"] == "gpt6" else evo.G56
            msg = jp + f"\n\n（文章在附件 " + "、".join(f"{l}.md" for l in labels) + f" 中；参考材料是附件 {BEADFILE}。）"
            jobs.append((rid, lambda rid=rid, msg=msg, jp=jp, files=files + [bp], model=model:
                         evo.call(rid, msg, prompt_text=jp, attach=files, model=model, meta={"stage": "judge_v2"})))
    print(f"{eid}: {len(jobs)} calls", flush=True)
    evo.run_parallel(jobs, workers)
    collect(eid)


def collect(eid):
    plan = json.loads((EV / eid / "plan.json").read_text(encoding="utf-8"))
    rows = []
    for bid, b in plan.items():
        r = evo.output(f"{JV[0]}_{eid}_{bid}")
        if not r:
            continue
        try:
            j = evo.parse_json(r)
        except Exception as e:
            print(bid, "parse fail", e); continue
        rk = j.get("ranking", [])
        for lab, n in b["map"].items():
            a = (j.get("articles") or {}).get(lab) or {}
            rows.append({"block": bid, "judge": b["judge"], "name": n, "rank": rk.index(lab) + 1 if lab in rk else None,
                         "n": len(b["map"]), "plot": (a.get("external_plot") or {}).get("severity") if isinstance(a.get("external_plot"), dict) else None,
                         "center": (a.get("center") or {}).get("present") if isinstance(a.get("center"), dict) else a.get("center"), "center_stmt": (a.get("center") or {}).get("statement") if isinstance(a.get("center"), dict) else a.get("center_statement"),
                         "history": a.get("history"), "connection": a.get("connection"),
                         "conn_musical_only": a.get("connection_is_musical_only"), "alive": a.get("alive"), "why_now": a.get("why_now_logic"),
                         "self_driven": a.get("self_driven"), "drivers": a.get("segment_drivers"),
                         "music_driven": (sum(d == "乐" for d in a["segment_drivers"]) / len(a["segment_drivers"])) if a.get("segment_drivers") else None,
                         "undriven": (sum(d == "无" for d in a["segment_drivers"]) / len(a["segment_drivers"])) if a.get("segment_drivers") else None,
                         "retell": (a.get("bead_retelling") or {}).get("share_of_segments") if isinstance(a.get("bead_retelling"), dict) else None,
                         **{k: a.get(k) for k in ("why_now_by_segment", "center_relation_by_segment", "forced_segments", "history", "connection", "mechanism", "accumulation", "faithful", "language", "problems", "bead_faithful", "glance", "insight", "plain", "chain", "concrete", "fit", "flow", "selection", "conflicts", "standalone", "accumulation", "reasons_from_music_and_history",
                                                  "adds_relations_beyond_beads", "alive_language", "overall", "verdict")}})
    (EV / eid / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{eid}: {len(rows)} rows")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("eid"); ap.add_argument("work"); ap.add_argument("names")
    ap.add_argument("--shuffles", type=int, default=3); ap.add_argument("--judges", default="gpt6,gpt56")
    ap.add_argument("--workers", type=int, default=9); ap.add_argument("--judge", default="judge_v2")
    a = ap.parse_args()
    JV[0] = a.judge
    run(a.eid, a.work, a.names.split(","), a.shuffles, a.judges.split(","), a.workers)
