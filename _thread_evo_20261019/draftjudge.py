"""Whole-draft judge (user 10-23: "does the N8 Center itself drive the back-and-forth? how good are the corrected drafts?").
All Op.60 drafts, none of which saw beads, are judged against all 14 sections' beads: is each main bead explained,
how many unneeded psychological moves, and every "adopt a way -> it fails -> another way" cycle.
Families: n8 (N8 prompt, tournament Center), c6 (N8 prompt, Center c6), d9L / d9S (corrected rules, no Center),
d9LC (corrected L rules + the tournament Center) -> d9L vs d9LC isolates the Center.
usage: python draftjudge.py <eid>   -> evaluations/draftjudge/<eid>.json"""
import json, random, sys
import arts, evo, node2b, segcheck, seq

W = __import__("os").environ.get("DJW", "op60")   # DJW=op61 (10-23): macro-judge the Op.61 drafts too (bead-free, so no STRUCT needed)
FAM = {"n8": [f"n8_{W}_r{j}" for j in (1, 2, 3)],
       "c6": [f"n8_op60_c6_r{j}" for j in (1, 2, 3, 4)] if W == "op60" else [f"n8_op61_c4_r{j}" for j in (3, 4)],
       "d9L": [f"d9L_{W}_r{j}" for j in (1, 2, 3)], "d9S": [f"d9S_{W}_r{j}" for j in (1, 2, 3)],
       "d9LC": [f"d9LC_{W}_r{j}" for j in (1, 2, 3)]}
OUT = evo.ROOT / "evaluations" / "draftjudge"


def sections(n):
    t = arts.clean(evo.output(n)); segs = segcheck.seg.load(W)["segments"]
    j = segcheck.to_json(t, W)
    if j:
        return [x["text"].strip() for x in j["segments"]]
    if n.startswith("d9L"):
        d = seq.split_listen(t)
        if len(d) == len(segs):
            return [d[s["start"]] for s in segs]
    ps = [p.strip() for p in t.split("\n\n") if p.strip()]
    return ps if len(ps) == len(segs) else None


def beads_all():
    out = []
    for i in range(1, 15):
        s = f"S{i:02}"; a, b = seq.bars(s)
        out.append(f"### 第{i}段　第 {a}–{b} 小节\n" + seq.beads(s))
    return "\n\n".join(out)


def groups():
    names = [n for f in FAM.values() for n in f]; random.Random("DJ").shuffle(names)
    # deal round-robin by family so each group mixes families
    order = sorted(names, key=lambda n: (next(k for k, v in FAM.items() if n in v), n))
    gs = [[] for _ in range(4)]
    for i, n in enumerate(order):
        gs[i % 4].append(n)
    return gs


if __name__ == "__main__":
    eid = sys.argv[1]; segs = segcheck.seg.load(W)["segments"]
    # MACRO (user 10-23): drafts give the whole-piece view and are judged without beads (judge_macro_v1, reasons required);
    # bead fit is judged only after the integration step. eid starting with "DM" selects it.
    MACRO = eid.startswith("DM")
    tmpl = evo.rd(evo.ROOT / "prompts" / ("judge_macro_v1.md" if MACRO else "judge_draft_v1.md")); B = "" if MACRO else beads_all()
    if W == "op61":
        tmpl = (tmpl.replace("肖邦《船歌》Op.60", "肖邦《幻想波兰舞曲》Op.61").replace("《船歌》", "《幻想波兰舞曲》")
                .replace("同样的 14 段", "同样的 13 段"))
    plan = {}; jobs = []
    only = [int(x) for x in sys.argv[2:]]
    for gi, g in enumerate(groups()):
        if only and gi not in only:
            continue
        ok = [n for n in g if evo.done(n) and sections(n)]
        miss = set(g) - set(ok)
        if miss:
            print("skip (missing/unsplittable):", miss, flush=True)
        for jn in ("gpt6", "gpt56"):
            keys = ok[:]; random.Random(f"{eid}{gi}{jn}").shuffle(keys)
            labs = [f"稿{chr(65 + i)}" for i in range(len(keys))]
            body = "\n\n".join(f"## {lab}\n\n" + "\n\n".join(f"**第{i + 1}段（{s['start']}–{s['end']}）**\n{t}"
                                                              for i, (s, t) in enumerate(zip(segs, sections(k))))
                               for lab, k in zip(labs, keys))
            m = (tmpl.replace("{N}", str(len(keys))).replace("{LABELS}", "、".join(labs))
                 + ("" if MACRO else "\n\n# 听感记录\n\n" + B) + "\n\n# 稿子\n\n" + body)
            rid = f"{eid}_g{gi}_{jn}"; plan[rid] = dict(zip(labs, keys))
            jobs.append(node2b.job(rid, m, {"stage": "draftjudge"}, w="g6" if jn == "gpt6" else "g56"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{eid}_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    evo.run_parallel([j for j in jobs if not evo.done(j[0])], 8)
    res = {}
    for rid, mp in plan.items():
        r = seq.parse(evo.output(rid))
        if r:
            res[rid] = {"ranking": [mp.get(x, x) for x in r.get("ranking", [])], "drafts": {mp.get(k, k): v for k, v in (r.get("drafts") or {}).items()}}
    (OUT / f"{eid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print({rid: r["ranking"] for rid, r in res.items()}, flush=True)
