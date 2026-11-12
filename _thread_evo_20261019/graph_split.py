"""10-28 night: the finished line (P8, 感受 + 为什么 per item, ~100 chars an item) cut into relation-graph steps of <= 45 chars,
content unchanged (THREAD_SPEC §九 5 / §十 4 form). The 10-21 prose->graph conversion was paused because it split one feeling
into many steps and added abstract labels, so: one feeling stays one step; only the chained causes inside 为什么 are split;
no labels, no new words of meaning, every qualifier kept. Each step keeps the item it came from, so the line's own explains
(the bead join) and from (the ← arrows) carry over. One g6 call per piece, then one g56 audit per piece (lost cause or
qualifier / added content / feeling split apart). ids: gs<T>_<work>, ga<T>_<work>.
usage: THREAD_ROUTE=gpt3s python graph_split.py <T> -> evaluations/seq8/P<T>g_<work>.json"""
import json, sys
import covjudge, draft10, evo, join11 as K, node2b

S = evo.ROOT / "evaluations" / "seq8"
CUT = """下面是肖邦{NAME}一条 Thread 的逐段条目，每条是“感受”加“为什么”。请把它排成关系图的短步，用来在视频里一步步出现。

规则：
1. 每一步一句话，不超过 45 个字；由同一条里上一步直接引出的，标 follows: true。
2. 内容一点都不改：不加新的意思、新的原因、新的例子，也不删掉任何一步原因或限定（仿佛、一度、还没、暂时这类要留着）。可以删掉重复的话和连接用的虚词。
3. 一个感受写成一步，不拆成几步；只把“为什么”里连着的几步因果拆开，每步说一件事。不加“转折”“领悟”之类的标签，不写编号和小节号。
4. 每一步写明它来自原来的第几条（i）。条目顺序不变。

{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"i": 1, "steps": [{{"text": "……", "follows": false}}, {{"text": "……", "follows": true}}]}}]}}]}}
```"""
AUDIT = """下面是一条 Thread 的原文条目，以及把它排成关系图短步之后的样子。请逐段核对短步版：
- lost：原文里的哪一步原因、哪个限定（仿佛、一度、还没、暂时这类）在短步里没有了；
- added：短步里有哪些原文没有的意思；
- split：哪个感受被拆成了几步、读起来断了。
每处写段号和一句话；没有就留空列表。

【原文】
{ORIG}

【短步】
{NEW}

只输出 json：
```json
{{"lost": [{{"sec": "S03", "what": "……"}}], "added": [], "split": [], "ok": "是 / 否", "why": "一句"}}
```"""


FIX = """

【上一版短步被核对者退回】
{NOTES}
请据此重排这一首：让步、对照、因果（“可……却……”“不是……而是……”“没有……反而……”“于是”这类）只要不超过 45 字，就留在同一步里；把删掉的转折和因果连接词补回来；其余照旧，格式同上。

【上一版短步】
{PREV}"""


def fix(T, w):
    """10-28: Op.61's first cut was 18 chars a step, 10 places split apart and 3 connectives dropped -> one revision, one re-audit."""
    rows, line = orig(T, w); a = evo.parse_json(evo.output(f"ga{T}_{w}")) or {}
    notes = "\n".join(f"- {k} {x.get('sec')}：{x.get('what', '')}" for k in ("lost", "split", "added") for x in a.get(k) or [])
    prev = steps_text(evo.parse_json(evo.output(f"gs{T}_{w}")))
    if not evo.done(f"gs{T}b_{w}"):
        evo.call(f"gs{T}b_{w}", CUT.format(NAME=covjudge.NAME[w], LINE=line) + FIX.format(NOTES=notes, PREV=prev), model=evo.G6, meta={"stage": "graph-split-fix"})
    g = evo.parse_json(evo.output(f"gs{T}b_{w}"))
    if not evo.done(f"ga{T}b_{w}"):
        evo.call(f"ga{T}b_{w}", AUDIT.format(ORIG=line, NEW=steps_text(g)), model=evo.G56, meta={"stage": "graph-split-audit"})
    a2 = evo.parse_json(evo.output(f"ga{T}b_{w}")) or {}
    steps = [st["text"] for s in g["segments"] for it in s.get("items") or [] for st in it.get("steps") or []]
    print(f"{w} 重排：{len(steps)} 步，每步 {sum(map(len, steps)) // max(1, len(steps))} 字 | 超 45 字 {sum(len(t) > 45 for t in steps)} | 核对 {a2.get('ok')} | 丢 {len(a2.get('lost') or [])} | 加 {len(a2.get('added') or [])} | 拆碎 {len(a2.get('split') or [])} | {a2.get('why')}", flush=True)
    for k in ("lost", "added", "split"):
        for x in a2.get(k) or []:
            print(f"     {k} {x.get('sec')}：{x.get('what', '')[:90]}", flush=True)
    json.dump({"graph": g, "audit": a2, "first": {"graph": evo.parse_json(evo.output(f"gs{T}_{w}")), "audit": a}},
              open(S / f"P{T}g_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def orig(T, w):
    rows = json.loads((S / f"P{T}_{w}.json").read_text(encoding="utf-8"))
    return rows, "\n\n".join(f"### {s['id']}\n" + "\n".join(f"{i}. 感受：{K.clean(x.get('feel', ''))} 为什么：{K.clean(x.get('why', ''))}"
                                                           for i, x in enumerate(rows[s["id"]]["edit"].get("items") or [], 1)) for s in draft10.segs(w))


def steps_text(g):
    return "\n\n".join(f"### {s['sec']}\n" + "\n".join(f"{'→ ' if st.get('follows') else '• '}{st['text']}" for it in s.get("items") or [] for st in it.get("steps") or [])
                       for s in g.get("segments") or [])


def main(T):
    jobs, data = [], {}
    for w in ("op60", "op61"):
        rows, line = orig(T, w); data[w] = (rows, line)
        if not evo.done(f"gs{T}_{w}"):
            jobs.append(node2b.job(f"gs{T}_{w}", CUT.format(NAME=covjudge.NAME[w], LINE=line), {"stage": "graph-split"}, w="g6"))
    evo.run_parallel(jobs, 2)
    jobs = []
    for w, (rows, line) in data.items():
        g = evo.parse_json(evo.output(f"gs{T}_{w}"))
        if not evo.done(f"ga{T}_{w}"):
            jobs.append(node2b.job(f"ga{T}_{w}", AUDIT.format(ORIG=line, NEW=steps_text(g)), {"stage": "graph-split-audit"}, w="g56"))
    evo.run_parallel(jobs, 2)
    for w, (rows, line) in data.items():
        g = evo.parse_json(evo.output(f"gs{T}_{w}")); a = evo.parse_json(evo.output(f"ga{T}_{w}")) or {}
        steps = [st["text"] for s in g["segments"] for it in s.get("items") or [] for st in it.get("steps") or []]
        n_items = {s["id"]: len(rows[s["id"]]["edit"].get("items") or []) for s in draft10.segs(w)}
        got = {s["sec"]: sorted({it["i"] for it in s.get("items") or []}) for s in g["segments"]}
        miss = {sec: n for sec, n in n_items.items() if got.get(sec) != list(range(1, n + 1))}
        long_ = [t for t in steps if len(t) > 45]
        print(f"{w}: {len(steps)} 步，共 {sum(map(len, steps))} 字，每步 {sum(map(len, steps)) // max(1, len(steps))} 字 | 超 45 字 {len(long_)} | 条目对不上 {miss}", flush=True)
        print(f"   核对：{a.get('ok')} | 丢 {len(a.get('lost') or [])} | 加 {len(a.get('added') or [])} | 拆碎 {len(a.get('split') or [])} | {a.get('why')}", flush=True)
        for k in ("lost", "added", "split"):
            for x in a.get(k) or []:
                print(f"     {k} {x.get('sec')}：{x.get('what', '')[:90]}", flush=True)
        json.dump({"graph": g, "audit": a}, open(S / f"P{T}g_{w}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[2] == "fix":
        fix(sys.argv[1], sys.argv[3])
    else:
        main(sys.argv[1])
