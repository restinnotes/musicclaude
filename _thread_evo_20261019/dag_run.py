"""10-31: run the DAG downstream of the new Center (N04 v2) on both works from the same start, reusing old products only
where they do not depend on the Center (segmentation, A drafts, beads).
  pick  : N05 output — per work the new-Center article (ln2_<w>_r1..3) with the highest mean overall in the blind legibility
          read (line_dag.py LDV=2 judge, lj2_<w>_<judge>); the old-Center article in that read is only a reference.
  graph : N06 tgraph4 build with the new Center (2 builds, ids tg4_<article>_r1/_r2), keep the build with the fewer check
          problems. (The old N06 also ran keys / arrow audit / final; N08 rewrites every item and drops relation labels, so
          those steps are skipped here.)
  import: -> evaluations/v6fix/<w>_<TAG>0.json (same graph format as v6), then the normal tags:
          python v6gen.py gloss (GLOSS_TAG=<TAG>0) ; v6gen.py write <TAG>0 <TAG>1 ; v6human.py write <TAG>1 <TAG>2 (HUMAN_MODE=6) ...
usage: python dag_run.py pick | graph | import   (TAG env, default d)"""
import json, os, re, sys
from statistics import mean
import arts, draft10, evo, node2b, stateinc, tgraph3, tgraph4, v6fix as V
import center_dag

TAG = os.environ.get("TAG", "d")
CENTER = json.loads((center_dag.OUT / "chosen2.json").read_text(encoding="utf-8"))
tgraph3.center = lambda w: CENTER[w]          # N06 must see the new Center (it is also checked verbatim)
PICK = evo.ROOT / "evaluations" / "center_dag" / f"pick_{TAG}.json"


def pick():
    out = {}
    for w in ("op60", "op61"):
        sc = {}
        for jn in ("g6", "g56"):
            r = evo.output(f"lj2_{w}_{jn}")
            if not r:
                continue
            # map 文章X -> run id: rebuild the same shuffle as line_dag.judge
            import random
            ns = ["n8_op60_r1" if w == "op60" else "n8_op61_r2"] + [f"ln2_{w}_r{j}" for j in (1, 2, 3) if evo.done(f"ln2_{w}_r{j}")]
            m = ns[:]; random.Random(f"lj{w}{jn}").shuffle(m); mp = {f"文章{chr(65 + i)}": n for i, n in enumerate(m)}
            for a in (evo.parse_json(r) or {}).get("articles") or []:
                n = mp.get(a.get("id"))
                if n and n.startswith("ln2_"):
                    sc.setdefault(n, []).append(float(a.get("overall") or 0) + float(a.get("legible") or 0) / 10)
        best = max(sc, key=lambda n: mean(sc[n]))
        out[w] = best; print(w, {n: round(mean(v), 2) for n, v in sc.items()}, "->", best, flush=True)
    PICK.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


def problems(c):
    return len(c.get("segments_without_why_now") or []) * 3 + len(c.get("bad_refs") or []) * 2 + len(c.get("too_long") or []) + (0 if c.get("center_verbatim") else 5)


def graph():
    P = json.loads(PICK.read_text(encoding="utf-8")); jobs = []
    for w, t in P.items():
        msg = (stateinc.fill(tgraph4.P, w).replace("{CENTER}", CENTER[w]) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)))
        jobs += [node2b.job(f"tg4_{t}_r{j}", msg, {"stage": "dag_n06", "thread": t}) for j in (1, 2) if not evo.done(f"tg4_{t}_r{j}")]
    evo.run_parallel(jobs, 4)
    for w, t in P.items():
        for j in (1, 2):
            if evo.done(f"tg4_{t}_r{j}"):
                tgraph4.save(f"tg4_{t}_r{j}", t)


def imp():
    P = json.loads(PICK.read_text(encoding="utf-8"))
    for w, t in P.items():
        cands = []
        for j in (1, 2):
            f = tgraph4.OUT / f"tg4_{t}_r{j}.json"
            if f.exists():
                d = json.loads(f.read_text(encoding="utf-8")); cands.append((problems(d["check"]), j, d))
        _, j, d = min(cands, key=lambda x: x[:2])
        segs = draft10.segs(w); out = []
        for s, x in zip(segs, d["segments"]):
            out.append({"sec": s["id"], "bars": x["bars"], "relation": x.get("relation"),
                        "items": [{k: it.get(k) for k in ("id", "text", "key", "follows")} for it in x.get("items") or []],
                        "because": [{k: e.get(k) for k in ("from", "to", "rel", "how")} for e in x.get("because") or []]})
        g = V.tidy({"center": CENTER[w], "segments": out})
        json.dump({"graph": g, "rows": {}, "base": f"DAG：新 Center 写稿 {t} → 转关系图 tg4_{t}_r{j}"}, open(V.OUT / f"{w}_{TAG}0.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{TAG}0.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜DAG 新 Center 关系图（{TAG}0）\n\n" + V.view(g), encoding="utf-8")
        print(w, "导入", f"tg4_{t}_r{j}", "段", len(out), "条目", sum(len(s["items"]) for s in out), "检查", d["check"].get("segments_without_why_now"), flush=True)


if __name__ == "__main__":
    {"pick": pick, "graph": graph, "import": imp}[sys.argv[1]]()
