"""Coverage of the Thread graphs against their original line (user 10-21: the graph must not lose the line's content).
Same tool as stepcheck: GPT-6 causal-step inventory of the original; GPT-5.6 checks each version step by step
(kept/weakened/lost/wrong) and lists additions. Versions: full graph (all nodes + edges, as text) and the concise view.
usage: python graphcov.py   -> evaluations/stepcheck/graph_rows.json"""
import json
from collections import defaultdict
import arts, evo, stepcheck, tgraph2

T = ["n7_op60_IA_c31_r1", "n7_op61_IA_c31_r1"]


def full_text(j):
    N = {n["id"]: n for n in j["nodes"]}; out = defaultdict(list)
    for e in j["edges"]:
        out[N.get(e["to"], {}).get("seg")].append(e)
    md = []
    for s in j["segments"]:
        md += [f"### {s['bars']}", f"Center（{s.get('center_move')}）：{s.get('center_touch')}"]
        md += [f"- {n['id']} {n['type']}（{n.get('certainty')}）：{n['text']}" for n in j["nodes"] if n["seg"] == s["bars"]]
        md += [f"- 关系：{e['from']}（{N.get(e['from'], {}).get('seg')}）{e['rel']} {e['to']}" + (f"：{e['note']}" if e.get("note") else "") for e in out[s["bars"]]]
        md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    stepcheck.OUT.mkdir(parents=True, exist_ok=True)
    evo.run_parallel([(f"inv_{t}", (lambda t=t: evo.call(f"inv_{t}", stepcheck.INV + arts.clean(evo.output(t)), prompt_text=stepcheck.INV, meta={"stage": "step_inventory"})))
                      for t in T if not evo.done(f"inv_{t}")], 2)
    vers = {}
    for t in T:
        (stepcheck.OUT / f"{t}.json").write_text(json.dumps(evo.parse_json(evo.output(f"inv_{t}")), ensure_ascii=False, indent=1), encoding="utf-8")
        j = json.loads((tgraph2.OUT / f"tg2_{t}_r1.json").read_text(encoding="utf-8"))
        vers[(t, "full")] = full_text(j)
        vers[(t, "view")] = (tgraph2.OUT / f"tg2_{t}_r1_view.md").read_text(encoding="utf-8")
    jobs = []
    for (t, v), txt in vers.items():
        rid = f"gchk_{v}_{t}"
        if not evo.done(rid):
            msg = stepcheck.CHK.replace("{INV}", (stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8")).replace("{TXT}", txt)
            jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=stepcheck.CHK[:300], model=evo.G56, meta={"stage": "graph_cov"}))))
    evo.run_parallel(jobs, 4)
    rows = []
    for (t, v), txt in vers.items():
        r = evo.output(f"gchk_{v}_{t}")
        if not r:
            continue
        c = evo.parse_json(r); st = c.get("steps", {}); ad = c.get("additions", [])
        inv = {s["id"]: s for s in json.loads((stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8"))["steps"]}
        rows.append({"thread": t, "version": v, "total": len(inv), **{k: list(st.values()).count(k) for k in ("kept", "weakened", "lost", "wrong")},
                     "not_kept": [{"id": k, "seg": inv.get(k, {}).get("segment"), "so": inv.get(k, {}).get("so"), "verdict": x} for k, x in st.items() if x != "kept"],
                     "add_new": [a.get("text") for a in ad if a.get("type") == "new"], "chars": len(txt)})
    (stepcheck.OUT / "graph_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    for r in rows:
        print(f"{r['thread']:20s} {r['version']:4s} 保留{r['kept']}/{r['total']} 弱化{r['weakened']} 丢{r['lost']} 错{r['wrong']} 新增{len(r['add_new'])} 字{r['chars']}", flush=True)
