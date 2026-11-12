"""10-29: pick among candidate versions of single segments (whole-piece blind counts are too noisy between near-identical
versions: w15/w16b got new "lost" items in segments identical to w14). For each segment: v6's version (reference, labelled),
the candidates (anonymised, shuffled), this segment's beads, the preceding segment for context, and the fixed-checklist items of
the segment. Judges rank the candidates on four things; 2 judges x 2 shuffles; pick the best mean rank.
ids: st_<w>_<sec>_<j>_<k>.  usage: python sectour.py <w> <sec,sec> <tag,tag,...> -> evaluations/v6fix/sectour_<w>.json"""
import json, random, sys
import covjudge, evo, v6fix as V

P = """下面是肖邦{NAME}一条 Thread（关系图）第 {SEC} 段（第 {BARS} 小节）的几个修补候选，以及原来那一版（v6）的这一段作参照。候选顺序是随机的。

{WHAT}

请把候选从好到差排序，同时分项排序：
1. keep：v6 这一段已经说清的实质内容（下面“清单”列出的）保得最全——可以换说法，但意思要在；
2. cover：最能说清这一段珠子里的感受为什么此刻会这样（只看原因，不要求把珠子的细节写进线）；
3. lean：最少重复、拆碎、没必要的心理步骤；
4. plain：最像一个人在说自己的事，具体、不抽象、不像哲理总结；
5. own：线自己站得住——只读线（连同前一段）不看珠子也能明白他此刻为什么这样；说的是他自己的原因，而不是把珠子里的感受、画面、身体反应换个说法搬进来，也不是硬凑出来的“因为……所以”。
戏剧化、主观不算缺点。每项写一句理由。

【前一段（上下文，各候选相同）】
{PREV}

【v6 的这一段（参照，不参加排序）】
{V6}

【候选】
{CANDS}

【这一段的珠子】
{BEADS}

【清单：v6 这一段的实质内容】
{LIST}

只输出 json：
```json
{{"overall": ["C2", "C1"], "keep": ["C1", "C2"], "cover": ["C2", "C1"], "lean": ["C2", "C1"], "plain": ["C2", "C1"], "own": ["C2", "C1"], "why": "……"}}
```"""


def seg(g, sec):
    return next(s for s in g["segments"] if s["sec"] == sec)


def main(w, secs, tags):
    g6 = V.v6(w); K = json.loads((V.OUT / f"checklist_{w}.json").read_text(encoding="utf-8"))["items"]
    graphs = {t: V.graph_of(w, t) for t in tags}
    jobs, meta = [], {}
    for sec in secs:
        i = [s["sec"] for s in g6["segments"]].index(sec)
        prev = V.view({"center": "", "segments": [graphs[tags[0]]["segments"][i - 1]]}, center=False) if i else "（这是第一段）"
        lst = "\n".join(f"- {k['what']}" for k in K if k["sec"] == sec) or "（无）"
        for j, m in V.JUDGES.items():
            for k in range(2):
                # 10-29 bug fix: the id must name the candidate set, or a later tour of the same segment silently reuses an
                # earlier tour's answer and maps its C1..Cn onto different versions (happened for op61 S02/S08/S12/S13)
                import hashlib
                rid = f"st_{w}_{sec}_{j}_{k}_" + hashlib.sha1((",".join(tags) + "|own-v2").encode()).hexdigest()[:8]
                order = tags[:]; random.Random(rid).shuffle(order)
                lab = {f"C{n + 1}": t for n, t in enumerate(order)}
                cands = "\n\n".join(f"【{c}】\n" + V.view({"center": "", "segments": [seg(graphs[t], sec)]}, center=False, head=False) for c, t in lab.items())
                msg = P.format(NAME=covjudge.NAME[w], SEC=sec, BARS=seg(g6, sec)["bars"], WHAT=V.WHAT, PREV=prev,
                               V6=V.view({"center": "", "segments": [seg(g6, sec)]}, center=False, head=False), CANDS=cands,
                               BEADS=V.beads(w, sec), LIST=lst)
                meta[rid] = {"sec": sec, "lab": lab}
                if not evo.done(rid):
                    jobs.append((rid, lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "sectour"})))
    evo.run_parallel(jobs, 8)
    res = {}
    for rid, mt in meta.items():
        d = V.parse(rid) or {}
        for key in ("overall", "keep", "cover", "lean", "plain", "own"):
            for r, c in enumerate(d.get(key) or [], 1):
                t = mt["lab"].get(c)
                if t:
                    res.setdefault(mt["sec"], {}).setdefault(t, {}).setdefault(key, []).append(r)
    out = {}
    for sec, by in res.items():
        rows = sorted(by.items(), key=lambda x: sum(x[1].get("overall", [9])) / len(x[1].get("overall", [9])))
        out[sec] = {t: {k: round(sum(v) / len(v), 2) for k, v in d.items()} for t, d in rows}
        print(w, sec, " | ".join(f"{t}: 总 {out[sec][t].get('overall')} 保 {out[sec][t].get('keep')} 覆 {out[sec][t].get('cover')} 简 {out[sec][t].get('lean')} 人 {out[sec][t].get('plain')} 立 {out[sec][t].get('own')}" for t, _ in rows), flush=True)
    json.dump(out, open(V.OUT / f"sectour_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2].split(","), sys.argv[3].split(","))
