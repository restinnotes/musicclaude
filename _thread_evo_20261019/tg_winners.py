"""Center tournament winners -> skeleton -> Thread graph v2 (P0 concepts) -> concise review view.
Winners (RT60/RT61, judge_spec_v2): op60 rs1, rs5; op61 rs2, rs6.
ids: sk_<line>, tg2_<line>_r1; views: evaluations/tgraph2/tg2_<line>_r1_view.md"""
import json, sys
from collections import defaultdict
import arts, evo, node2b, skeleton, stateinc, tgraph2

LINES = [("op60", "n7_op60_IA_rs1_r1"), ("op60", "n7_op60_IA_rs5_r1"), ("op61", "n7_op61_IA_rs2_r1"), ("op61", "n7_op61_IA_rs6_r1")]


def view(j, title, center_line):
    N = {n["id"]: n for n in j["nodes"]}; inc = defaultdict(list)
    for e in j["edges"]:
        inc[e["to"]].append(e)
    segpos = {s["bars"]: i for i, s in enumerate(j["segments"])}
    md = [f"# {title}", "", f"**Center：**{center_line}", ""]   # the accepted Center sentence, verbatim (not the graph's own expansion)
    for i, s in enumerate(j["segments"]):
        md += [f"### {s['bars']}", "", f"◇ **Center（{s.get('center_move')}）**：{s.get('center_touch')}", ""]
        for sid in s["state"]:
            n = N.get(sid, {}); md.append(f"**此刻：{n.get('text')}**" + ("（还模糊）" if n.get("certainty") == "模糊" else ""))
            es = sorted(inc[sid], key=lambda e: (segpos.get(N.get(e["from"], {}).get("seg"), 99) == i, e.get("rel") not in ("提供理由", "改写", "唤起", "失效")))[:3]
            for e in es:
                src = N.get(e["from"], {})
                md.append(f"- ← **{e['rel']}**（{src.get('seg')}·{src.get('type')}）{src.get('text')}" + (f"\n  　{e['note']}" if e.get("note") else ""))
        keys = [N[x] for x in s.get("new", []) if x in N and N[x]["type"] in ("发现", "机制") and x not in s["state"]][:2]
        for n in keys:
            md.append(f"- ✦ {n['type']}{'｜' + n['kind'] if n.get('kind') and n['kind'] != '其他' else ''}：{n['text']}" + ("（还模糊）" if n.get("certainty") == "模糊" else ""))
        hist = [N[h] for h in (s.get("history") or []) if h in N][:2]
        if hist:
            md.append("- ⟲ 仍在起作用：" + "；".join(f"（{h['seg']}）{h['text']}" for h in hist))
        md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    ph = sys.argv[1] if len(sys.argv) > 1 else "all"
    if ph in ("all", "gen"):
        jobs = [(f"sk_{t}", (lambda t=t: evo.call(f"sk_{t}", skeleton.SK + arts.clean(evo.output(t)), prompt_text=skeleton.SK, meta={"stage": "skeleton"})))
                for w, t in LINES if not evo.done(f"sk_{t}")]
        evo.run_parallel(jobs, 4)
        jobs = []
        for w, t in LINES:
            r = evo.output(f"sk_{t}")
            if not r:
                continue
            (skeleton.OUT / f"{t}.json").write_text(json.dumps(evo.parse_json(r), ensure_ascii=False, indent=1), encoding="utf-8")
            msg = stateinc.fill(tgraph2.P, w) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + (skeleton.OUT / f"{t}.json").read_text(encoding="utf-8")
            if not evo.done(f"tg2_{t}_r1"):
                jobs.append(node2b.job(f"tg2_{t}_r1", msg, {"stage": "tgraph2", "thread": t}))
        evo.run_parallel(jobs, 4)
    for w, t in LINES:
        if evo.done(f"tg2_{t}_r1"):
            tgraph2.save(f"tg2_{t}_r1", w)
            j = json.loads((tgraph2.OUT / f"tg2_{t}_r1.json").read_text(encoding="utf-8"))
            k = int(t.split("_rs")[1].split("_")[0])
            cl = json.loads((evo.ROOT / "evaluations" / "centers" / f"rs_{w}.json").read_text(encoding="utf-8"))[k - 1]["center"]
            v = view(j, f"{w}｜Center 候选 {k}｜关系图（精简视图）", cl)
            (tgraph2.OUT / f"tg2_{t}_r1_view.md").write_text(v, encoding="utf-8")
            print(t, "view chars", len(v), flush=True)
