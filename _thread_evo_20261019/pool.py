"""Per-segment explanation pool (PLAN_解释池_20261023.md 六-1). Candidates are the P0+-family drafts (d10*/d11*/d12*) cut
by segment; they already carry feel / thread / used / new, and covjudge.py already says which beads each segment's text
explains, so no extraction call is needed. A candidate leaves this segment's pool when both judges call it 相反 on more
beads than they call it 解释了 there. One call per segment then merges candidates that give the same mechanism
(same premise and same consequence, not same wording) and keeps every distinct one, with how many drafts proposed it.
ids: pl<tag>_<work>_<sec>.  usage: python pool.py <tag> <work> [draft-glob ...]   -> evaluations/pool/<tag>/<work>/<sec>.json"""
import fnmatch, json, sys
import covjudge, draft10, evo, node2b

OUT = evo.ROOT / "evaluations" / "pool"
DEDUP = """下面是许多位作者对肖邦{NAME}第{A}–{B}小节这一段的解释（每位作者都写了一条连贯的 Thread，这里只截出这一段）。
请把它们按“机制”归并：只有前提不同、或者带来的后果不同的，才算两种不同的解释；同一个意思换了说法、换了侧重，算同一种。
例如“希望长久所以舍不得”和“珍惜当下所以想留住”算同一种；“担心过失去，所以重新得到时更热烈”和“尝过幸福，所以对以后有了更多期待”算两种。
不要删掉任何一种不同的解释，也不要因为它少见或你不同意就并进别的里面。

每一种写：
- text：用成员的原话或把成员合起来写成一两句，说清理由；不要加任何成员都没有的新理由；用普通人能懂的话。
- premise：它需要前面已经发生过什么（没有就写“无”）。
- members：属于这一种的候选编号。

只输出 json：
```json
{{"mechs": [{{"text": "...", "premise": "...", "members": ["c1", "c4"]}}]}}
```

# 候选
{CANDS}"""


def drafts(w, pats):
    return sorted(p.stem for p in draft10.OUT.glob(f"d1*_{w}_*.json") if any(fnmatch.fnmatch(p.stem, x) for x in pats))


def cands(w, names):
    """{sec: [candidate]}; labels from covjudge (strict = both judges)"""
    beads = covjudge.beads(w); out = {}
    for n in names:
        rs = [covjudge.result(n, j) for j in covjudge.JUDGES]
        if not all(rs):
            continue
        d = json.loads((draft10.OUT / f"{n}.json").read_text(encoding="utf-8"))
        for x in d["sections"]:
            sb = [b["id"] for b in beads if b["sec"] == x["sec"]]
            lab = {b: [r.get(b, {}).get("label") for r in rs] for b in sb}
            exp = [b for b in sb if all(l == "解释了" for l in lab[b])]
            loose = [b for b in sb if any(l == "解释了" for l in lab[b]) and b not in exp]
            opp = [b for b in sb if all(l == "相反" for l in lab[b])]
            if len(opp) > len(exp):
                continue
            out.setdefault(x["sec"], []).append({"src": n, "feel": x["feel"], "thread": x["thread"], "used": x.get("used") or "无",
                                                 "new": x.get("new") or [], "explains": exp, "partly": loose, "opposite": opp})
    return out


def dedup_msg(w, sec, cs):
    s = next(s for s in draft10.segs(w) if s["id"] == sec)
    body = "\n\n".join(f"c{i + 1}：{c['thread']}\n（作者说它用到的前面经历：{c['used']}）" for i, c in enumerate(cs))
    return DEDUP.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], CANDS=body)


def build(tag, w, pats):
    cs = cands(w, drafts(w, pats)); out = OUT / tag / w; out.mkdir(parents=True, exist_ok=True)
    jobs = [node2b.job(f"pl{tag}_{w}_{sec}", dedup_msg(w, sec, c), {"stage": "pool", "work": w, "sec": sec}, w="g6")
            for sec, c in cs.items() if not evo.done(f"pl{tag}_{w}_{sec}")]
    evo.run_parallel(jobs, 16)
    for sec, c in cs.items():
        try:
            ms = evo.parse_json(evo.output(f"pl{tag}_{w}_{sec}"))["mechs"]
        except Exception:
            print(w, sec, "dedup parse failed", flush=True); continue
        for i, m in enumerate(ms):
            mem = [c[int(k[1:]) - 1] for k in m.get("members", []) if k[1:].isdigit() and 0 < int(k[1:]) <= len(c)]
            m.update(id=f"M{i + 1}", sources=[x["src"] for x in mem], n=len(mem),
                     explains=sorted({b for x in mem for b in x["explains"]}),
                     partly=sorted({b for x in mem for b in x["partly"]} - {b for x in mem for b in x["explains"]}),
                     new=[h for x in mem for h in x["new"]][:6])
        (out / f"{sec}.json").write_text(json.dumps({"sec": sec, "cands": c, "mechs": ms}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, sec, len(c), "candidates ->", len(ms), "mechanisms", flush=True)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3:] or ["d1*"])
