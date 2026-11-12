"""Blind block judging. Each block = anchor (B0, optional) + k candidates, shuffled, labelled 文章A.. .
Judges: gpt6 / gpt56 via gpt3 (articles attached as files), gemini via opencode (articles inline).
usage: python judge.py <eval_id> <work> <run-glob,...> [--anchor] [--k 4] [--judges gpt6,gpt56,gemini] [--seed 1]
Outputs evaluations/<eval_id>/{blocks.json, <block>_<judge>.json} and runs/j_<eval_id>_<block>_<judge>/.
"""
import argparse, json, random
import arts, evo, seg

EV = evo.ROOT / "evaluations"


def judge_prompt(work, labels):
    d = seg.load(work)
    rng = "、".join(f"{s['start']}–{s['end']}" for s in d["segments"])
    t = evo.rd(evo.ROOT / "prompts" / "judge_v1.md")
    return (t.replace("{N}", str(len(labels))).replace("{LABELS}", "、".join(labels)).replace("{WORK}", d["work"])
            .replace("{TOTAL}", str(d["total_measures"])).replace("{RANGES}", rng).replace("{NSEG}", str(len(d["segments"]))))


def make_blocks(names, k, seed):
    r = random.Random(seed); names = names[:]; r.shuffle(names)
    nb = -(-len(names) // k)
    pad = nb * k - len(names)
    names += r.sample(names[:len(names) - k], pad) if pad else []   # fillers get a second reading
    return [names[i * k:(i + 1) * k] for i in range(nb)]


def run(eval_id, work, globs, anchor, k, judges, seed, workers):
    out = EV / eval_id; out.mkdir(parents=True, exist_ok=True)
    pool = arts.pool(globs)
    if anchor:
        pool["B0"] = arts.b0()
    (out / "articles").mkdir(exist_ok=True)
    bf = out / "blocks.json"
    if bf.exists():
        plan = json.loads(bf.read_text(encoding="utf-8"))
    else:
        plan = {}
        for jn in judges:
            blocks = make_blocks([n for n in pool if n != "B0"], k, seed + sum(map(ord, jn)))
            for bi, b in enumerate(blocks):
                members = b + (["B0"] if anchor else [])
                random.Random(f"{seed}{jn}{bi}").shuffle(members)
                labels = [f"文章{chr(65 + i)}" for i in range(len(members))]
                plan[f"b{bi + 1}_{jn}"] = {"judge": jn, "map": dict(zip(labels, members))}
        bf.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    jobs = []
    for bid, b in plan.items():
        rid = f"j_{eval_id}_{bid}"
        if evo.done(rid):
            continue
        labels = list(b["map"]); jp = judge_prompt(work, labels)
        adir = out / "articles" / bid; adir.mkdir(parents=True, exist_ok=True)
        files = []
        for lab, name in b["map"].items():
            p = adir / f"{lab}.md"; p.write_text(f"# {lab}\n\n" + pool[name], encoding="utf-8"); files.append(p)
        if b["judge"] == "gemini":
            msg = jp + "\n\n" + "\n\n".join(f"========== {lab} ==========\n{pool[n]}" for lab, n in b["map"].items())
            jobs.append((rid, lambda rid=rid, msg=msg, jp=jp: evo.call_gemini(rid, msg, prompt_text=jp, meta={"stage": "judge"})))
        else:
            model = evo.G6 if b["judge"] == "gpt6" else evo.G56
            msg = jp + f"\n\n（{len(labels)} 篇文章分别在附件 " + "、".join(f"{l}.md" for l in labels) + " 中。）"
            jobs.append((rid, lambda rid=rid, msg=msg, jp=jp, files=files, model=model:
                         evo.call(rid, msg, prompt_text=jp, attach=files, model=model, meta={"stage": "judge"})))
    print(f"{eval_id}: {len(jobs)} judge calls", flush=True)
    evo.run_parallel(jobs, workers)
    collect(eval_id)


def collect(eval_id):
    out = EV / eval_id
    plan = json.loads((out / "blocks.json").read_text(encoding="utf-8"))
    rows = []
    for bid, b in plan.items():
        resp = evo.output(f"j_{eval_id}_{bid}")
        if not resp:
            continue
        try:
            j = evo.parse_json(resp)
        except Exception as e:
            print(f"{bid}: parse fail {e}"); continue
        rank = j.get("ranking", [])
        for lab, name in b["map"].items():
            a = (j.get("articles") or {}).get(lab)
            if not a:
                continue
            rows.append({"block": bid, "judge": b["judge"], "label": lab, "name": name,
                         "rank": rank.index(lab) + 1 if lab in rank else None, "n": len(b["map"]), **a})
    (out / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{eval_id}: {len(rows)} article judgments collected")
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_id"); ap.add_argument("work"); ap.add_argument("globs")
    ap.add_argument("--anchor", action="store_true"); ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--judges", default="gpt6,gpt56,gemini"); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    run(a.eval_id, a.work, a.globs.split(","), a.anchor, a.k, a.judges.split(","), a.seed, a.workers)
