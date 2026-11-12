"""10-28 night: final review of the finished line in graph steps (P<T>g, graph_split.py) — experiment 3's split review with
package 3 / P<T> (same content, 感受 + 为什么) / P<T>g (steps), anonymised in random order, and the package 3 regression
judge on P<T>g. Tells whether the graph form costs anything against the prose it came from.
ids: fe<T>_<work>_<core|align>_<judge>, fr<T>_<work>_<judge>.  usage: THREAD_ROUTE=gpt3s python final_eval.py <T>"""
import json, random, sys
import covjudge, draft10, evo, finalize3, join11 as K, mech_check, node2b, split_judge as SJ

S = evo.ROOT / "evaluations" / "seq8"


def versions(T, w):
    t = (S / f"P{T}_{w}.txt").read_text(encoding="utf-8").split("\n", 2)
    center = t[1].replace("Center：", "", 1)
    g = json.loads((S / f"P{T}g_{w}.json").read_text(encoding="utf-8"))["graph"]
    by = {s["sec"]: s for s in g["segments"]}
    steps = "\n".join(f"### {s['id']} ｜ {s['start']}–{s['end']} 小节\n\n" + "\n".join(
        f"{'→' if st.get('follows') else '•'} {K.clean(st['text'])}" for it in by.get(s["id"], {}).get("items") or [] for st in it.get("steps") or []) + "\n"
        for s in draft10.segs(w))
    return {"包3": SJ.pkg3(w), f"P{T}": (center, K.clean(t[2].strip())), f"P{T}g": (center, steps)}


def main(T):
    jobs, order = [], {}
    for w in ("op60", "op61"):
        vs = versions(T, w)
        beads = "\n".join(f"- {b['id']}［{b['role']}］{b['text']}" for b in covjudge.beads(w) if b["role"] != "演奏条件")
        mechs = "\n".join(f"{i}. {m}" for i, m in enumerate(mech_check.MECH[w], 1))
        for kind in ("core", "align"):
            for j in ("g6", "g56"):
                rid = f"fe{T}_{w}_{kind}_{j}"; ks = list(vs); random.Random(rid).shuffle(ks); order[rid] = dict(zip(SJ.NAMES, ks))
                vt = "\n\n".join(f"========== {n} 版 ==========\nCenter：{vs[k][0]}\n\n{vs[k][1]}" for n, k in zip(SJ.NAMES, ks))
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, (SJ.CORE if kind == "core" else SJ.ALIGN).format(NAME=covjudge.NAME[w], VERSIONS=vt, MECHS=mechs, BEADS=beads),
                                           {"stage": "final-eval"}, w=j))
        new = f"Center：{vs[f'P{T}g'][0]}\n\n{vs[f'P{T}g'][1]}"
        jobs += [node2b.job(f"fr{T}_{w}_{j}", finalize3.R.format(NAME=covjudge.NAME[w], OLD=finalize3.PKG3[w].read_text(encoding="utf-8-sig"), NEW=new),
                            {"stage": "final-R"}, w=j) for j in ("g6", "g56") if not evo.done(f"fr{T}_{w}_{j}")]
    json.dump(order, open(S / f"order_final{T}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    evo.run_parallel(jobs, 10)          # 10-28 user: up to 10 in flight is fine (runs/gpt3_slots.txt = 8)
    for rid, o in order.items():
        r = evo.parse_json(evo.output(rid)) if evo.done(rid) else {}; un = lambda xs: [o.get(x, x) for x in xs or []]
        line = f"{rid}: 总排名 {un((r or {}).get('overall'))}"
        if "_core_" in rid:
            line += " | " + "；".join(f"{k} {un(v)}" for k, v in ((r or {}).get("ranks") or {}).items())
        else:
            line += f" | 主体验说清 { {o.get(k, k): v for k, v in ((r or {}).get('b1_clear') or {}).items()} } | 写反 { {o.get(k, k): v for k, v in ((r or {}).get('reversed') or {}).items()} }"
        print(line, flush=True)
    for w in ("op60", "op61"):
        for j in ("g6", "g56"):
            r = evo.parse_json(evo.output(f"fr{T}_{w}_{j}")) if evo.done(f"fr{T}_{w}_{j}") else {}
            print(f"{w} 短步版整首对照包3 {j}：{(r or {}).get('verdict')}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
