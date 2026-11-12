"""Bead coverage of a draft pool (user 10-23: "我们首先要保证九篇稿子能够cover所有的珠子的内容 然后再去往后面做对接吧").
Each bead-free draft is judged against every bead of its piece: 解释了 / 只提到 / 没有 / 相反 / 跳过, with a quoted reason.
A pool covers a bead when some draft explains it: strict = both judges say 解释了 for the same draft, loose = either judge.
Old drafts (d9L/d9S/d9LC, n8, B0) give the baseline; the new P0+ drafts (draft10.py, d10*) must not fall below it.
ids: cv_<draft>_<judge>.  usage: python covjudge.py run <draft-glob ...> | sum   -> evaluations/cover/"""
import fnmatch, json, sys
from pathlib import Path
import arts, draftjudge, evo, node2b, segcheck

OUT = evo.ROOT / "evaluations" / "cover"
NAME = {"op60": "《船歌》Op.60", "op61": "《幻想波兰舞曲》Op.61"}
STRUCT = {"op60": evo.ROOT / "inputs" / "pkg" / "03_Bead机器可读",
          "op61": Path("D:/musicclaude/_bead_op61_20261020/deliverable/03_Bead机器可读")}
JUDGES = ("g6", "g56")
OLD = {w: [f"{f}_{w}_r{j}" for f in ("d9L", "d9S", "d9LC", "n8") for j in (1, 2, 3)] + (["b0_op60"] if w == "op60" else [])
       for w in ("op60", "op61")}
GROUPS = {"修正稿9篇": ("d9L_*", "d9S_*", "d9LC_*"), "N8": ("n8_*",), "B0": ("b0_*",), "P0+全部": ("d10*",), "D11全部": ("d11*",), "D10+D11": ("d10*", "d11*"), "D12全部": ("d12*",),
          "D12自由": ("d12f*",), "D12时间": ("d12t*",), "D12他人": ("d12p*",), "D12自己": ("d12s*",), "D10–D12": ("d10*", "d11*", "d12*"), "D14 High": ("d14[fts]*",), "D14 High gpt6": ("d14[fts]6_*",), "D14 High gpt56": ("d14[fts]56_*",), "D14 ExtraHigh": ("d14x*",), "D14 ExtraHigh gpt6": ("d14x?6_*",), "D14 ExtraHigh gpt56": ("d14x?56_*",), "D15 High": ("d15*",), "D15 High gpt6": ("d15?6_*",), "D15 High gpt56": ("d15?56_*",), "D10–D12+D15": ("d10*", "d11*", "d12*", "d15*"), "D16": ("d16*",), "D17 对照": ("d17*",), "D18 mimic gpt6": ("d18*",), "D19 nozomi xhigh": ("d19*",), "D20 联网": ("d20*",), "D21 联网+转折": ("d21*",), "D22 联网+转折+应对": ("d22*",), "D21+D22": ("d21*", "d22*"), "D23 应对可选": ("d23*",), "D21+D23": ("d21*", "d23*"), "D10–D15": ("d10*", "d11*", "d12*", "d14*", "d15*"), "D10–D16": ("d1*",),
          "P0+逐段gpt6": ("d10c6_*",), "P0+逐段gpt56": ("d10c56_*",), "P0+一次gpt6": ("d10o6_*",), "P0+一次gpt56": ("d10o56_*",)}


def beads(w):
    out = []
    for f in sorted(STRUCT[w].glob("S*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        out += [{"id": f"{f.stem}-{b['id']}", "sec": f.stem, "role": b["role"], "measures": b["measures"], "text": b["text"]}
                for b in d["beads"]]
    return out


def bead_text(w):
    segs = {s["id"]: s for s in segcheck.seg.load(w)["segments"]}; out = []; last = None
    for b in beads(w):
        if b["sec"] != last:
            last = b["sec"]; s = segs[last]; out.append(f"\n### {last}　第 {s['start']}–{s['end']} 小节")
        out.append(f"- {b['id']}［{b['role']}］（{b['measures']}）{b['text']}")
    return "\n".join(out)


def sections(n):
    w = segcheck.work_of(n)
    if n.startswith(("d10", "d11", "d12", "d14", "d15", "d16", "d17", "d18", "d19", "d20", "d21", "d22", "d23")):
        d = json.loads((evo.ROOT / "evaluations" / "draft10" / f"{n}.json").read_text(encoding="utf-8"))
        return [f"感受：{x['feel']}\n{x['thread']}\n（用到的历史：{x.get('used') or '无'}）" for x in d["sections"]]
    if n.startswith("b0"):
        return [x["text"].strip() for x in segcheck.to_json(arts.b0(), "op60")["segments"]]
    draftjudge.W = w
    return draftjudge.sections(n)


def msg(n):
    w = segcheck.work_of(n); segs = segcheck.seg.load(w)["segments"]; ps = sections(n)
    assert ps and len(ps) == len(segs), n
    body = "\n\n".join(f"**{s['id']}　第 {s['start']}–{s['end']} 小节**\n{x}" for s, x in zip(segs, ps))
    return (evo.rd(evo.ROOT / "prompts" / "judge_cover_v1.md").replace("{NAME}", NAME[w])
            + "\n\n# 听感记录\n\n" + bead_text(w) + "\n\n# Thread 稿\n\n" + body)


def result(n, j):
    rid = f"cv_{n}_{j}"
    if not evo.done(rid):
        return None
    try:
        r = evo.parse_json(evo.output(rid))
    except Exception:
        return None
    return {x["id"]: x for x in r.get("beads", [])} | {"_gaps": r.get("gaps", "")}


def summarize(w):
    names = sorted({p.stem.rsplit("_", 1)[0][3:] for p in (evo.RUNS).glob(f"cv_*{w}*")} | set(OLD[w]))
    res = {(n, j): result(n, j) for n in names for j in JUDGES}
    res = {k: v for k, v in res.items() if v}
    bs = [b for b in beads(w) if b["role"] != "演奏条件"]
    per = {}
    for n in names:
        rs = [res.get((n, j)) for j in JUDGES]
        if not all(rs):
            continue
        per[n] = {lab: sum(r.get(b["id"], {}).get("label") == lab for r in rs for b in bs) / 2
                  for lab in ("解释了", "只提到", "没有", "相反")}
    groups = {}
    for g, pats in GROUPS.items():
        mem = [n for n in per if any(fnmatch.fnmatch(n, p) for p in pats)]
        if not mem:
            continue
        strict = [b["id"] for b in bs if any(all(res[(n, j)].get(b["id"], {}).get("label") == "解释了" for j in JUDGES) for n in mem)]
        loose = [b["id"] for b in bs if any(res[(n, j)].get(b["id"], {}).get("label") == "解释了" for n in mem for j in JUDGES)]
        groups[g] = {"drafts": mem, "strict": len(strict), "loose": len(loose), "total": len(bs),
                     "uncovered_strict": [b["id"] for b in bs if b["id"] not in strict],
                     "uncovered_loose": [b["id"] for b in bs if b["id"] not in loose]}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"summary_{w}.json").write_text(json.dumps({"per_draft": per, "groups": groups}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"== {w}: {len(bs)} beads (演奏条件 skipped)")
    for n, c in per.items():
        print(f"  {n:16} " + " ".join(f"{k}{v:g}" for k, v in c.items()))
    for g, d in groups.items():
        print(f"  [{g}] {len(d['drafts'])}篇  严格覆盖 {d['strict']}/{d['total']}  宽松 {d['loose']}/{d['total']}  严格缺: {' '.join(d['uncovered_strict'])}")


def show(n, secs=None):
    """both judges' label + reason per bead, for my own spot checks"""
    rs = {j: result(n, j) or {} for j in JUDGES}
    for b in beads(segcheck.work_of(n)):
        if secs and b["sec"] not in secs:
            continue
        print(f"{b['id']} [{b['role']}] {b['text'][:40]}")
        for j, r in rs.items():
            x = r.get(b["id"], {})
            print(f"   {j:4} {x.get('label', '-')}: {x.get('why', '')}  «{x.get('where', '')}»" + (f"  编造:{x['invented']}" if x.get("invented") else ""))
    for j, r in rs.items():
        print(f"{j} gaps: {r.get('_gaps', '')}")


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(sys.argv[2], sys.argv[3:] or None); sys.exit()
    if sys.argv[1] == "run":
        pats = sys.argv[2:] or ["*"]
        ns = [n for w in OLD for n in OLD[w]] + [p.stem for p in (evo.ROOT / "evaluations" / "draft10").glob("d[12][0-9]*.json")]
        ns = [n for n in ns if any(fnmatch.fnmatch(n, p) for p in pats)]
        evo.run_parallel([node2b.job(f"cv_{n}_{j}", msg(n), {"stage": "cover", "draft": n}, w=j)
                          for n in ns for j in JUDGES if not evo.done(f"cv_{n}_{j}")], 5 if evo.ROUTE == "mimic" else 16)
    for w in ("op60", "op61"):
        summarize(w)
