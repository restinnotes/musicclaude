"""Head-to-head on the whole piece (user 10-23: "我们提出的这种一点一点往后积累的方式是否比以前质量好很多"). The new
sectional-synthesis graphs were only ever compared with each other; here the current v6 relation graph and the new graph
(beam winner after polish) meet under the beam's final rubric (beads shown, opening-states-the-theme / unsupported backstory /
forced arrows penalized, a reason for every verdict). Both are rendered the same way. 2 judges x 2 orders.
usage: python headtohead.py <op60|op61> <ver>[,<ver>...]   ver = v6 or a beam tag (e.g. v6,60d,60e)
       -> evaluations/beam/h2h_<work>_<vers joined by _>.json"""
import json, random, sys
import beam, evo, node2b, seq


def render(g):
    """graph dict (v6 json or beam graph.json: segments[bars, relation, items[id,text,key,follows], because[from,to,rel]])"""
    by_id = {it["id"]: (s["bars"], it) for s in g["segments"] for it in s["items"]}; out = []
    for k, s in enumerate(g["segments"]):
        out.append(f"第{k + 1}段（{s['bars']}）［{s.get('relation') or '?'}］")
        for i, it in enumerate(s["items"]):
            out.append(f"  {'→ ' if it.get('follows') and i else ''}{it['text']}")
            for b in s.get("because") or []:
                if b.get("to") == it["id"] and b.get("from") in by_id:
                    bars, src = by_id[b["from"]]
                    out.append(f"      ← {b['rel']}：（{bars}）「{src.get('key') or ''}」")
    return "\n".join(out)


if __name__ == "__main__":
    work, vs = sys.argv[1], sys.argv[2].split(","); T = "_".join(vs)
    beam.setup(work)
    def load(v):
        if v == "v6":
            return json.loads((evo.ROOT / "deliverable" / "thread_v6" / f"Op{work[2:]}_关系图.json").read_text(encoding="utf-8"))
        return json.loads((beam.OUT / v / "graph.json").read_text(encoding="utf-8"))
    vers = {(v if v == "v6" else f"beam{v}"): load(v) for v in vs}
    assert all(len(v["segments"]) == len(beam.SECS) for v in vers.values())
    keys = list(vers); labs = [f"线{chr(65 + i)}" for i in range(len(keys))]; jobs = []; maps = {}
    for jn, w in (("gpt6", "g6"), ("gpt56", "g56")):
        for s in (1, 2):
            order = keys[:]; random.Random(f"h2h{work}{T}{jn}{s}").shuffle(order)
            body = "\n\n".join(f"## {lab}\n{render(vers[k])}" for lab, k in zip(labs, order))
            m = beam.fill(beam.FINAL, work, N=len(keys), LABELS="、".join(labs), BEADS=beam.beads_upto(len(beam.SECS)), PATHS=body)
            rid = f"h2h_{work}_{T}_{jn}_{s}"; maps[rid] = dict(zip(labs, order))
            if not evo.done(rid):
                jobs.append(node2b.job(rid, m, {"stage": "h2h"}, w=w))
    evo.run_parallel(jobs, 4)
    res = {}
    for rid, mp in maps.items():
        r = seq.parse(evo.output(rid)) or {}
        res[rid] = {"ranking": [mp.get(x, x) for x in r.get("ranking", [])], "my_reading": r.get("my_reading"),
                    "paths": {mp.get(k, k): v for k, v in (r.get("paths") or {}).items()}}
    (beam.OUT / f"h2h_{work}_{T}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for rid, r in res.items():
        print(rid, r["ranking"], {k: (v.get("overall") or {}).get("score") for k, v in r["paths"].items()},
              {k: sum(x.get("explains") == "是" for x in v.get("segments", [])) for k, v in r["paths"].items()}, flush=True)
