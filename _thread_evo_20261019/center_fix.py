"""10-28 night (user on the Op.60 Center "他盼着两个人能够相爱，在亲近时高兴得忘了自己……": "这个 center 是怎么决定的？我们之前想要的是
这种类型的 center 吗？"). No: finalize3's F prompt only asked for "一句普通人能懂的话" (no format), so it came out as a person +
action summary of the route. THREAD_SPEC table (P0, 09-21/22, recovered 10-21): the minimal complete relation sentence —
objects as noun phrases + how they relate, holding from early on to the end; no person/action phrasing; not just two nouns;
no route or ending; no default conflict. Written after the line (§十 4). Examples are unrelated to the pieces.
Per piece: g6 writes 3 candidates and picks one against the rules; g56 checks the pick independently.
ids: cf<T>_<work>, ck<T>_<work>.  usage: THREAD_ROUTE=gpt3s python center_fix.py <T> -> evaluations/seq8/center<T>_<work>.json"""
import json, sys
import covjudge, draft10, evo, join11 as K, node2b

S = evo.ROOT / "evaluations" / "seq8"
RULES = """Center 的要求（项目早先定下的格式）：
- 说出整首是同一件事：什么对他重要、什么使它难以安顿；
- 写成最小完整关系句：主语是一个或几个对象（名词短语），谓语说出它们怎样相关；这个关系从较早处就成立，一直到结尾；
- 不写人称和动作（不写“他想……却……”“他盼着……”）；不能只是两个名词；
- 不预告发展路线和结局，不概括各段经过；不预设关系类型，不默认是冲突——确实是冲突才写冲突；
- 和每一段都对得上：每段都在这个关系的范围里（不必每段都推进它，有的段可以还说不清或暂时没在想）。
格式示例（与本曲无关）：“对自由的向往与对安稳的依赖都真实，却彼此拉扯。”“已经失去的家与仍在继续的日常同时在场。”"""
W = """下面是肖邦{NAME}一条 Thread 的全部条目（逐段，每段末尾是这一段新确立的变化）。请为它写 Center。

""" + RULES + """

先写 3 个候选，再逐个按上面每条检查，选出最好的一个。

{LINE}

只输出 json：
```json
{{"candidates": ["……", "……", "……"], "checks": [{{"i": 1, "format": "是", "preview": "否", "fits": "是", "why": "……"}}], "best": 1, "why": "……"}}
```"""
C = """下面是肖邦{NAME}一条 Thread 的全部条目，以及为它写的 Center。请按要求逐条核对这个 Center，每条一句理由。

""" + RULES + """

【Center】{CENTER}

{LINE}

只输出 json：
```json
{{"format": "是 / 否", "preview": "是 / 否（是否预告了路线或结局）", "fits": "是 / 否（是否每段都在它的范围里）", "typical": "是 / 否（是否抓住了这条线最核心的那件事）", "why": "……", "fix": "如果有问题，给一句改好的 Center；没有就留空"}}
```"""


def line(T, w):
    rows = json.loads((S / f"P{T}_{w}.json").read_text(encoding="utf-8"))
    return "\n\n".join(f"### {s['id']}\n" + "\n".join(f"- {K.clean(x.get('feel', ''))} → {K.clean(x.get('why', ''))}" for x in rows[s["id"]]["edit"].get("items") or [])
                       + "\n新确立的变化：" + "；".join(K.clean(t) for t in rows[s["id"]]["edit"].get("new") or []) for s in draft10.segs(w))


def main(T):
    data = {w: line(T, w) for w in ("op60", "op61")}
    evo.run_parallel([node2b.job(f"cf{T}_{w}", W.format(NAME=covjudge.NAME[w], LINE=l), {"stage": "center-fix"}, w="g6")
                      for w, l in data.items() if not evo.done(f"cf{T}_{w}")], 2)
    jobs = []
    for w, l in data.items():
        r = evo.parse_json(evo.output(f"cf{T}_{w}"))
        best = r["candidates"][max(1, min(3, int(r.get("best") or 1))) - 1]
        if not evo.done(f"ck{T}_{w}"):
            jobs.append(node2b.job(f"ck{T}_{w}", C.format(NAME=covjudge.NAME[w], CENTER=best, LINE=l), {"stage": "center-check"}, w="g56"))
    evo.run_parallel(jobs, 2)
    for w, l in data.items():
        r = evo.parse_json(evo.output(f"cf{T}_{w}")); best = r["candidates"][max(1, min(3, int(r.get("best") or 1))) - 1]
        k = evo.parse_json(evo.output(f"ck{T}_{w}")) or {}
        final = k.get("fix") if (k.get("fix") and "否" in "".join(str(k.get(x, "")) for x in ("format", "fits", "typical"))) else best
        json.dump({"candidates": r["candidates"], "checks": r.get("checks"), "picked": best, "pick_why": r.get("why"), "check": k, "final": final},
                  open(S / f"center{T}_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{w} 候选：", r["candidates"], flush=True)
        print(f"   选：{best} | 核对 格式 {k.get('format')} 预告 {k.get('preview')} 对得上 {k.get('fits')} 抓住核心 {k.get('typical')} | {k.get('why')}", flush=True)
        print(f"   最终：{final}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
