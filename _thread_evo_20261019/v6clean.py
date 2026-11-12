"""10-30 w36: w35 is the best blind so far (4/4 prefer new, 2/4 not a regression, cover 10-13:1-4, 人话 11-13:1-2, coverage Op.60
44/44, Op.61 49/47) but the coverage repair let bead content in: Op.60 got plot the line never set up ("对方重新愿意亲近他",
"决定彻底结束这段关系，转身离开", a body-fantasy item), pure retelling 4-5, alone 11/14 & 9/14; Op.61 S13 grew to 467 chars
with an invented "故土和共同记忆"; Op.61 lost to v6 on 啰嗦 in 8 segments for one judge.
Last pass, in order, only segments with notes: drop events/plot/context the line never set up; turn retold items into his
reason (or drop); merge restatements where a blind judge found the segment wordier than v6 (char target); give back the few
items the blind judges named lost; keep every distinct reason (coverage). Writer does not see beads.
ids: cl_<w>_<sec>_<out>.  usage: python v6clean.py <base> <out> [w:sec ...  extra segments to tighten]"""
import json, random, sys
import covjudge, draft10, evo, v6fix as V
from v6restore import P

T_INV = """
- 评委只读这条线时指出：{X}
  线里从没交代过的外部事件或情节（对方做了什么、关系怎样了结、地点、国家、历史）不要写进来——删掉，或者改成他心里的事。"""
T_RET = """
- 下面几条被指出只是在转述此刻的感受或想象，没说他为什么会这样。改成他自己的原因（来自线前面的经历或这一段新的心理变化）；没有新原因的就删掉：
{X}"""
T_LEAN = """
- 评委认为这一段比原来的 v6 啰嗦：有几条在用不同说法重申同一件事。把它们合并，整段收到大约 {N} 个字以内；具体的说法比概括的说法好，不要为了短改抽象。"""
T_LOST = """
- 评委指出下面这些 v6 说清的内容这一段丢了，请用他自己的平常话找回（能并进现有条目就并）：
{X}"""
TAIL = """
- 这一段现有的每一个不同的原因都要留下（可以合并、改短）；线里没交代过的外部背景一律删掉。"""


def notes(base):
    N = {}
    get = lambda w, s: N.setdefault((w, s), {"inv": [], "ret": [], "lean": False, "lost": []})
    al = json.loads((V.OUT / f"alone_{base}.json").read_text(encoding="utf-8"))
    for k, v in al.items():
        w = k.split("_")[0]
        for x in v.get("weak_secs") or []:
            get(w, x[0])["inv"].append(x[2])
        for r in v.get("retold") or []:
            if r[1] == "复述珠子":
                n = get(w, r[0].split("-")[0])
                if r[0] not in n["ret"]:
                    n["ret"].append(r[0])
    bl = json.loads((V.OUT / f"blind_{base}.json").read_text(encoding="utf-8"))
    for rid, v in bl.items():
        for sec, x in v.get("lost_new") or []:
            get(v["w"], sec)["lost"].append(x["what"])
        new = "X" if random.Random(rid).random() < 0.5 else "Y"     # same deterministic flip as v6fix.blind
        for s in (V.parse(rid) or {}).get("sections") or []:
            if s.get("lean") != new and s.get("sec"):
                get(v["w"], s["sec"])["lean"] = True
    return N


def main(base, out, force=()):
    N = notes(base)
    for sp in force:                   # extra segments to tighten by hand (e.g. op61:S13 grew to 467 chars without a lean vote)
        w, sec = sp.split(":")
        N.setdefault((w, sec), {"inv": [], "ret": [], "lean": False, "lost": []})["lean"] = True

    def piece(w):
        g = V.graph_of(w, base); segs = {s["id"]: s for s in draft10.segs(w)}; g6 = V.v6(w)
        v6s = {s["sec"]: s for s in g6["segments"]}
        rows = json.loads((V.OUT / f"{w}_{base}.json").read_text(encoding="utf-8"))["rows"]
        done = {"center": g["center"], "segments": []}; remap = {}
        chars = lambda s: sum(len(i["text"]) for i in s["items"])

        def keep(s):
            s = json.loads(json.dumps(s))
            for b in s["because"]:
                b["from"] = remap.get(b.get("from"), b.get("from"))
            done["segments"].append(s); V.tidy(done)
        for s in g["segments"]:
            sec = s["sec"]; nt = N.get((w, sec))
            if not nt:
                keep(s); continue
            txt = {it["id"]: it["text"] for it in s["items"]}
            tasks = ""
            for x in nt["inv"]:
                tasks += T_INV.format(X=x)
            if nt["ret"]:
                tasks += T_RET.format(X="\n".join(f"  · [{i}] {txt.get(i, '')}" for i in nt["ret"] if i in txt))
            if nt["lean"]:
                tasks += T_LEAN.format(N=int(min(0.8 * chars(s), chars(v6s[sec])) // 10 * 10))
            if nt["lost"]:
                tasks += T_LOST.format(X="\n".join(f"  · {x}" for x in nt["lost"]))
            tasks += TAIL
            maxn = max(len(v6s[sec]["items"]), len(s["items"]))
            rid = f"cl_{w}_{sec}_{out}"
            if not evo.done(rid):
                evo.call(rid, P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=s["bars"], REL=s.get("relation"), TASKS=tasks, MAXN=maxn,
                                       LINE=V.view(done, ids=True, center=False) if done["segments"] else "（这是第一段）",
                                       CUR=V.view({"center": "", "segments": [s]}, ids=True, center=False, head=False)).replace(
                                           "（原来的 v6 这一段是", "（参考：原来的 v6 这一段是"),
                         model=evo.G6, meta={"stage": "v6-clean"})
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
            print(f"{w} {sec}: 情节 {len(nt['inv'])} 复述 {len(nt['ret'])} 啰嗦 {int(nt['lean'])} 找回 {len(nt['lost'])} | "
                  f"{len(s['items'])} 条 → {len(ns['items'])} 条 | {chars(s)} 字 → {chars(ns)} 字", flush=True)
        G = V.tidy(done)
        json.dump({"graph": G, "rows": rows, "base": f"{base} 清理情节与复述、收紧啰嗦段"}, open(V.OUT / f"{w}_{out}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        (V.OUT / f"{w}_{out}.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，{out}）\n\n" + V.view(G), encoding="utf-8")
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
