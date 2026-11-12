"""10-30 w36: w35 (w34 + coverage/lost repair) brought coverage back (Op.60 44/44 like w24, Op.61 49/47) but some segments grew
back to v6 length or beyond (Op.61 S13 6 -> 12 items, 467 chars) and one invented outside context ("故土和共同记忆", leaked
from the coverage judge's reason). Here: tighten only the named segments — merge items that say the same thing, drop what
repeats the line before, keep every distinct reason, drop context the line never set up — to a char target
(max(1.2 x w34, 0.75 x current)). In order; later segments' back-arrows re-pointed via src, as in v6repair2.
ids: tg_<w>_<sec>_<out>.  usage: python v6tight.py <base> <out> <ref> op60:S07,S13 op61:S13 ..."""
import json, sys
import covjudge, draft10, evo, v6fix as V
from v6restore import P

T = """
- 这一段太长了，请收紧到大约 {N} 个字以内：说的是同一件事的条目合成一条，和前面各段重复的部分删掉；
- 每一个不同的原因都要留下来，意思不能丢——只删重复，不删内容；具体的说法比概括的说法好，不要为了短改得更抽象；
- 线里从来没有交代过的外部背景（地点、国家、历史、具体的人和事）删掉，只留他心里的事。
"""


def main(base, out, ref, specs):
    want = {}
    for sp in specs:
        w, secs = sp.split(":")
        want.setdefault(w, set()).update(secs.split(","))

    def piece(w):
        g = V.graph_of(w, base); r = {s["sec"]: s for s in V.graph_of(w, ref)["segments"]}
        segs = {s["id"]: s for s in draft10.segs(w)}; g6 = V.v6(w)
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        done = {"center": g["center"], "segments": []}; remap = {}
        chars = lambda s: sum(len(i["text"]) for i in s["items"])

        def keep(s):
            s = json.loads(json.dumps(s))
            for b in s["because"]:
                b["from"] = remap.get(b.get("from"), b.get("from"))
            done["segments"].append(s); V.tidy(done)
        for s in g["segments"]:
            sec = s["sec"]
            if sec not in want.get(w, ()):
                keep(s); continue
            n = int(max(1.2 * chars(r[sec]), 0.75 * chars(s)) // 10 * 10)
            maxn = len(g6["segments"][[x["sec"] for x in g6["segments"]].index(sec)]["items"])
            rid = f"tg_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), TASKS=T.format(N=n), MAXN=maxn,
                                       LINE=V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）",
                                       CUR=V.view({"center": "", "segments": [s]}, ids=True, center=False, head=False)),
                         model=evo.G6, meta={"stage": "v6-tight"})
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
            print(f"{w} {sec}: 目标 {n} 字 | {len(s['items'])} 条 → {len(ns['items'])} 条 | {chars(s)} 字 → {chars(ns)} 字", flush=True)
        G = V.tidy(done)
        json.dump({"graph": G, "rows": rows, "base": f"{base} 收紧过长段"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
