"""10-30 w35: w34 (restore + de-retell + v6 form, from w31) fixed the line's own logic (pure bead retelling 0-1, own reasons
Op.60 26-28/50, Op.61 20/39; arrows 22/21, almost all necessary; Op.60 blind lost only 2/4) but lost coverage
(Op.60 37/41, Op.61 43/46; w31 41/40, 50/46) and Op.61 blind lost 13/14. Mixing segments of w24/w31/w34 would leave arrows
pointing at items of another version, so instead: one more in-order pass on w34, only on segments with notes:
blind "lost vs v6" (both judges), beads judged not 说清 (both judges, with the judge's one-line reason), checklist items lost.
The writer still does not see beads; for coverage it gets the judges' reason and is told to add his reason, not the feeling.
Nothing already in the segment is removed unless it duplicates what is written now.
ids: r2_<w>_<sec>_<out>.  usage: python v6repair2.py <base> <out>"""
import json, sys
import covjudge, draft10, evo, v6fix as V
from v6restore import P

T_LOST = """
- 两位评委把这一段和原来的 v6 比，指出下面这些 v6 说清了、现在这一段丢了或说薄了的内容。请找回来：用他自己的平常话，能并进现有条目的就并进去；意思已经在了的不用重复。
{X}
"""
T_COV = """
- 这条线旁边的听感记录里，这一段有些感受，线还没说出他为什么会这样（下面是评委的说明）。请补上原因：是他心里的事——想要什么、怕什么、前面哪件事让此刻不一样；不要把这种感受本身写进线，也不要写声音和画面。补不出可信的原因就不补。
{X}
"""
TAIL = """
- 这一段现有的内容都要留下（可以改写得更短），只有和新写的重复的才删。
"""


def notes(base):
    out = {}
    bl = json.loads((V.OUT / f"blind_{base}.json").read_text(encoding="utf-8"))
    for v in bl.values():
        for sec, x in v.get("lost_new") or []:
            out.setdefault((v["w"], sec), {"lost": [], "cov": []})["lost"].append(x["what"])
    ck = json.loads((V.OUT / f"checklist_{base}.json").read_text(encoding="utf-8"))
    for w in ("op60", "op61"):
        K = {k["id"]: k for k in json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]}
        for kid in ck[w].get("lost_any") or []:
            out.setdefault((w, K[kid]["sec"]), {"lost": [], "cov": []})["lost"].append(K[kid]["what"])
    cov = json.loads((V.OUT / f"cov_{base}.json").read_text(encoding="utf-8"))
    for k, v in cov.items():
        w = k.split("_")[0]
        for sec, bead, lab, why in v.get("weak") or []:
            if lab != "说清":
                out.setdefault((w, sec), {"lost": [], "cov": []})["cov"].append(why)
    return out


def main(base, out):
    N = notes(base)

    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}; g6 = V.v6(w)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        done = {"center": g["center"], "segments": []}; remap = {}   # old item id -> new id, from the edited segments' src

        def keep(s):                   # an untouched segment: re-point its back-arrows at the edited earlier segments' new ids
            s = json.loads(json.dumps(s))
            for b in s["because"]:
                b["from"] = remap.get(b.get("from"), b.get("from"))
            done["segments"].append(s); V.tidy(done)
        for s in g["segments"]:
            sec = s["sec"]; nt = N.get((w, sec))
            if not nt:
                keep(s); continue
            tasks = ""
            if nt["lost"]:
                tasks += T_LOST.format(X="\n".join(f"  · {x}" for x in nt["lost"]))
            if nt["cov"]:
                tasks += T_COV.format(X="\n".join(f"  · {x}" for x in nt["cov"]))
            tasks += TAIL
            maxn = max(len(g6["segments"][[x["sec"] for x in g6["segments"]].index(sec)]["items"]), len(s["items"]))
            rid = f"r2_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), TASKS=tasks, MAXN=maxn,
                                       LINE=V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）",
                                       CUR=V.view({"center": "", "segments": [s]}, ids=True, center=False, head=False)).replace(
                                           "（原来的 v6 这一段是", "（参考：原来的 v6 这一段是"),
                         model=evo.G6, meta={"stage": "v6-repair2"})
            e = V.parse(rid) or {}
            if not isinstance(e.get("items"), list) or not e["items"]:
                print(w, sec, "没有结果，保留原样", flush=True); keep(s); continue
            old = {it["id"]: it for it in s["items"]}
            ns = V.seg_graph(e, sec, segs[sec]); ns["relation"] = s.get("relation")
            for oid in old:
                remap[oid] = None
            for it, raw in zip(ns["items"], e["items"]):
                it["explains"] = sorted({b for i in raw.get("src") or [] for b in old.get(i, {}).get("explains", [])})
                for i in raw.get("src") or []:
                    if i in old and remap.get(i) is None:
                        remap[i] = it["id"]
            done["segments"].append(ns); V.tidy(done)
            rows[sec] = {"edit": e, "check": None, "notes": [], "revised": False}
            print(f"{w} {sec}: 找回 {len(nt['lost'])} 处 补原因 {len(nt['cov'])} 处 | {len(s['items'])} 条 → {len(ns['items'])} 条 | "
                  f"{sum(len(x['text']) for x in s['items'])} 字 → {sum(len(x['text']) for x in ns['items'])} 字 | 箭头 {len(s['because'])} → {len(ns['because'])}", flush=True)
        G = V.tidy(done)
        json.dump({"graph": G, "rows": rows, "base": f"{base} 补覆盖与丢失"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
