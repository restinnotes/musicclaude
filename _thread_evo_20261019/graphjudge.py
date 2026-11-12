"""Graph judge (user 10-21: "有用的东西应该都让评委继承吧"). judge_graph_v1 = judge_spec_v3 (why-now, Center relations,
History/Connection, mechanism, accumulation, faithful) + judge_v5/line_v6 (self-driven, standalone, concrete, alive)
+ judge_form_v1 (glance, insight, plain words) + the two word lists from the 10-21 "站稳" discussion + new: efficiency
(repeats, empty negations, droppable detail). Assembly-only criteria (fit/flow/selection/bead_faithful) stay with judge_asm.
Each judge sees the original line + all graphs (anonymous, shuffled), several orders per model.
usage: python graphjudge.py <eid> <line id> <name=view.md,...> [--models gpt6,gpt56] [--shuffles 2]
-> evaluations/graphjudge/<eid>.json"""
import argparse, json, random, statistics
import arts, evo, seg

OUT = evo.ROOT / "evaluations" / "graphjudge"
SCORES = ("why_now", "center", "history_connection", "insight", "accumulation", "faithful", "standalone",
          "efficiency", "alive_concrete", "words", "glance", "overall")


def run(eid, t, graphs, models, shuffles, judge="judge_graph_v1"):
    w = "op60" if "op60" in t else "op61"; tpl = evo.rd(evo.ROOT / "prompts" / f"{judge}.md")
    texts = {n: evo.rd(evo.ROOT / p) for n, p in graphs.items()}
    plan, jobs = {}, []
    for m in models:
        for s in range(1, shuffles + 1):
            names = list(graphs); random.Random(f"{eid}{m}{s}").shuffle(names)
            labels = {f"图{chr(65 + i)}": n for i, n in enumerate(names)}; rid = f"gj_{eid}_{m}_s{s}"; plan[rid] = labels
            msg = (tpl.replace("{WORK}", seg.load(w)["work"]).replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels))
                   + "\n\n========== 原稿 ==========\n" + arts.clean(evo.output(t))
                   + "".join(f"\n\n========== {lab} ==========\n{texts[n]}" for lab, n in labels.items()))
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, prompt_text=tpl[:400], model=evo.G6 if m == "gpt6" else evo.G56, meta={"stage": "graph_judge"}))))
    evo.run_parallel(jobs, 4)
    rows = []
    for rid, labels in plan.items():
        r = evo.output(rid)
        if not r:
            continue
        j = evo.parse_json(r); rk = j.get("ranking", [])
        for lab, n in labels.items():
            g = (j.get("graphs") or {}).get(lab) or {}
            rows.append({"run": rid, "name": n, "rank": rk.index(lab) + 1 if lab in rk else None, **{k: g.get(k) for k in SCORES},
                         "items_now": g.get("items_now"), "items_if_trimmed": g.get("items_if_trimmed"), "problems": g.get("problems"), "verdict": g.get("verdict")})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{eid}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for n in graphs:
        rs = [x for x in rows if x["name"] == n]
        if not rs:
            continue
        avg = {k: round(statistics.mean(x[k] for x in rs if isinstance(x.get(k), (int, float))), 1) for k in SCORES if any(isinstance(x.get(k), (int, float)) for x in rs)}
        print(f"{n}: rank {[x['rank'] for x in rs]} | " + " ".join(f"{k}={v}" for k, v in avg.items())
              + f" | items {[x['items_now'] for x in rs]} -> {[x['items_if_trimmed'] for x in rs]}", flush=True)
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("eid"); ap.add_argument("line"); ap.add_argument("graphs")
    ap.add_argument("--models", default="gpt6,gpt56"); ap.add_argument("--shuffles", type=int, default=2); ap.add_argument("--judge", default="judge_graph_v1")
    a = ap.parse_args()
    run(a.eid, a.line, dict(x.split("=", 1) for x in a.graphs.split(",")), a.models.split(","), a.shuffles, a.judge)
