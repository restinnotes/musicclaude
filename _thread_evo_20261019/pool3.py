"""Explanation pool v3 (PLAN_20261026.md step 3, 10-27). Same candidates as pool.py (every draft segment of the chosen
drafts; a segment leaves when both judges call it 相反 on more beads than they call it 解释了), with two changes:
- merge only when premise, bridge AND result are the same (GPT review 10-25); the old prompt merged "希望长久所以舍不得"
  with "珍惜当下所以想留住", which rest on different earlier experiences;
- no merged rewrite. premise / bridge / result are short labels for matching and path checks only; every group names a
  representative member whose own words are the clearest plain speech, and the line later reuses those words (the
  10-25 package lost its plain language exactly where merged rewrites replaced the drafts' sentences).
ids: pl3<tag>_<work>_<sec>.  usage: THREAD_ROUTE=mimic python pool3.py <tag> <work> [draft-glob ...]
-> evaluations/pool/<tag>/<work>/<sec>.json"""
import json, sys
import covjudge, draft10, evo, node2b, pool

DEDUP = """下面是许多位作者对肖邦{NAME}第{A}–{B}小节这一段的解释。每位作者都写了一条贯穿全曲的 Thread，这里只截出这一段：
他此刻的感受，以及为什么经历过前面那些的人此刻会这样感受。

请把它们分组。只有下面三样都相同，才算同一组：
1. 前提：它依赖前面已经发生过的哪件事（例如“前面已经尝过一次满足”和“前面一直没有被回应”是不同前提）；
2. 桥：前面那件事通过什么道理造成了现在（例如“因为知道会过去，所以想留住”和“因为担心对方不在乎，所以想留住”是不同的桥）；
3. 结果：它解释的是此刻哪种感受。
三样里有一样不同，就分开，即使最后都解释同一种感受、说法也很像。换个说法、换个侧重、详略不同，才算同一组。
不要删掉任何一条，也不要因为少见或你不同意就并进别的组。

每一组写：
- premise：前提，一句短话（没有前提就写“无”）
- bridge：桥，一句短话
- result：解释此刻的哪种感受，一句短话
- members：属于这一组的候选编号
- rep：组里原话最清楚、最具体、最像普通人说话的那一条的编号（以后会直接用它的原话）
- weak：如果这一组的理由其实是空的（例如只说“经历过所以不一样了”“更在乎了”“有了新的分量”，或者只说“可以这样”“不等于那样”，或者把音乐回来当成对方回应），写出原因；否则写 ""

premise / bridge / result 只用于比较，不会给读者看，写短一点即可。只输出 json：
```json
{{"groups": [{{"premise": "...", "bridge": "...", "result": "...", "members": ["c1", "c4"], "rep": "c4", "weak": ""}}]}}
```

# 候选
{CANDS}"""


def msg(w, sec, cs):
    s = next(s for s in draft10.segs(w) if s["id"] == sec)
    body = "\n\n".join(f"c{i + 1}：感受：{c['feel']}\n为什么：{c['thread']}\n（作者说它用到的前面经历：{c['used']}）"
                       for i, c in enumerate(cs))
    return DEDUP.format(NAME=covjudge.NAME[w], A=s["start"], B=s["end"], CANDS=body)


def load(tag, w, sec):
    return json.loads((pool.OUT / tag / w / f"{sec}.json").read_text(encoding="utf-8"))


def build(tag, w, pats):
    cs = pool.cands(w, pool.drafts(w, pats)); out = pool.OUT / tag / w; out.mkdir(parents=True, exist_ok=True)
    rid = lambda sec: f"pl3{tag}_{w}_{sec}"
    evo.run_parallel([node2b.job(rid(sec), msg(w, sec, c), {"stage": "pool3", "work": w, "sec": sec}, w="g6")
                      for sec, c in cs.items() if not evo.done(rid(sec))], 10)
    for sec, c in cs.items():
        try:
            gs = evo.parse_json(evo.output(rid(sec)))["groups"]
        except Exception:
            print(w, sec, "pool parse failed", flush=True); continue
        seen = set(); groups = []
        for g in gs:
            idx = [int(k[1:]) - 1 for k in g.get("members", []) if str(k)[1:].isdigit() and 0 < int(str(k)[1:]) <= len(c)]
            idx = [i for i in idx if i not in seen]; seen |= set(idx)
            if idx:
                groups.append((g, idx))
        groups += [({"premise": c[i]["used"], "bridge": "", "result": "", "rep": f"c{i + 1}", "weak": "", "unmerged": True}, [i])
                   for i in range(len(c)) if i not in seen]          # never drop a candidate the model left out
        mechs = []
        for k, (g, idx) in enumerate(groups, 1):
            rep = int(str(g.get("rep", ""))[1:]) - 1 if str(g.get("rep", ""))[1:].isdigit() else idx[0]
            rep = rep if rep in idx else idx[0]
            mem = [c[i] for i in idx]
            mechs.append({"id": f"M{k}", "premise": g.get("premise", ""), "bridge": g.get("bridge", ""), "result": g.get("result", ""),
                          "weak": g.get("weak", ""), "rep": {"src": c[rep]["src"], "feel": c[rep]["feel"], "thread": c[rep]["thread"],
                                                             "used": c[rep]["used"], "new": c[rep]["new"]},
                          "sources": [x["src"] for x in mem], "n": len(mem),
                          "explains": sorted({b for x in mem for b in x["explains"]}),
                          "partly": sorted({b for x in mem for b in x["partly"]} - {b for x in mem for b in x["explains"]}),
                          "members": [{"src": x["src"], "feel": x["feel"], "thread": x["thread"], "used": x["used"], "new": x["new"],
                                       "explains": x["explains"]} for x in mem]})
        (out / f"{sec}.json").write_text(json.dumps({"sec": sec, "mechs": mechs}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, sec, len(c), "candidates ->", len(mechs), "groups;", sum(bool(m["weak"]) for m in mechs), "weak", flush=True)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3:] or ["d1*"])
