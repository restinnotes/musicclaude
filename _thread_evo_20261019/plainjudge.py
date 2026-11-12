"""Judge plain-language compressions of a line against its original (attached as 原文.md); the original is also one
of the blind candidates. GPT judges only. usage: python plainjudge.py <eid>  -> evaluations/<eid>/rows.json"""
import json, random, sys
import arts, evo, plain, seg

EV = evo.ROOT / "evaluations"
JV = ["judge_plain_v1"]
VARIANTS = [("P", (1, 2)), ("PL", (1, 2))]


def prompt(work, labels):
    d = seg.load(work)
    return (evo.rd(evo.ROOT / "prompts" / f"{JV[0]}.md").replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels))
            .replace("{WORK}", d["work"]).replace("{NSEG}", str(len(d["segments"]))))


def run(eid, shuffles=2):
    out = EV / eid; out.mkdir(parents=True, exist_ok=True); plan = {}; jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            names = [t] + [f"{v}_{t}_r{j}" if v.startswith("pc_") else f"pl_{v}_{t}_r{j}" for v, js in VARIANTS for j in js]
            names = [n for n in names if evo.done(n)]
            for jn, model in (("gpt6", evo.G6), ("gpt56", evo.G56)):
                for s in range(1, shuffles + 1):
                    m = names[:]; random.Random(f"{eid}{t}{jn}{s}").shuffle(m)
                    bid = f"{t}_s{s}_{jn}"; mp = {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}
                    plan[bid] = {"judge": jn, "work": w, "thread": t, "map": mp}
                    adir = out / "articles" / bid; adir.mkdir(parents=True, exist_ok=True); files = []
                    for lab, n in mp.items():
                        p = adir / f"{lab}.md"; p.write_text(f"# {lab}\n\n" + arts.clean(evo.output(n)), encoding="utf-8"); files.append(p)
                    o = adir / "原文.md"; o.write_text(arts.clean(evo.output(t)), encoding="utf-8")
                    jp = prompt(w, list(mp)); rid = f"jpl_{eid}_{bid}"
                    msg = jp + "\n\n（文章在附件 " + "、".join(f"{l}.md" for l in mp) + " 中；参考材料是附件 原文.md。）"
                    if not evo.done(rid):
                        jobs.append((rid, lambda rid=rid, msg=msg, jp=jp, files=files + [o], model=model:
                                     evo.call(rid, msg, prompt_text=jp, attach=files, model=model, meta={"stage": "judge_plain"})))
    (out / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(eid, len(jobs), "calls", flush=True)
    evo.run_parallel(jobs, 4)
    rows = []
    for bid, b in plan.items():
        r = evo.output(f"jpl_{eid}_{bid}")
        if not r:
            continue
        j = evo.parse_json(r); rk = j.get("ranking", [])
        for lab, n in b["map"].items():
            a = (j.get("articles") or {}).get(lab) or {}
            dr = a.get("segment_drivers") or []
            rows.append({"block": bid, "judge": b["judge"], "thread": b["thread"], "name": n, "rank": rk.index(lab) + 1 if lab in rk else None,
                         "chars": len(arts.clean(evo.output(n))), "music_driven": (dr.count("乐") / len(dr)) if dr else None,
                         **{k: a.get(k) for k in ("fidelity", "lost_steps", "plain", "concrete", "self_driven", "alive", "overall", "verdict")}})
    (out / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(rows), "rows")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "v2":
        JV[0] = "judge_plain_v2"
        VARIANTS[:] = [("PL", (1,)), ("pc_C1", (1, 2)), ("pc_C2", (1, 2)), ("pc_C3", (1, 2))]
    run(sys.argv[1])
