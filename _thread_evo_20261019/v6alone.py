"""10-29 (user: "我希望比如你把线单独拿出来能够自己看一遍就是成立的 不依赖珠子 ... 不能纯粹就在翻译珠子 这一点我们现在会不会没有评定").
Two measurements the repair rounds never had (coverage, blind and the gate all show the beads):
  ALONE : the judge sees ONLY the line. Per segment: does the line by itself make clear why he feels this now (成立/勉强/不成立);
          per item: 内心原因 (his own reason / change) vs 描写 (describing a sensation, image, bodily reaction — reads like a
          translation of listening notes); per arrow: 成立且必要 / 可有可无 / 读不出关系.
  TRANS : the judge sees the line AND the beads. Per item: 自己的原因 / 复述珠子 (a bead's feeling, image or bodily reaction put
          into the line in other words) / 两者都有.
v6 was written without beads, so it is the baseline here. ids: al_<w>_<j>_<tag>, tr_<w>_<j>_<tag>.
usage: python v6alone.py <tag> [...]   (tag v6 = original) -> evaluations/v6fix/alone_<tag>.json/.md"""
import json, sys
from collections import Counter
import covjudge, evo, v6fix as V

ALONE = """下面是一条“线”（Thread）：一个人在肖邦{NAME}里经历的一件事，按段写成关系图。只给你这条线，没有别的材料。

关系图的写法：每段先标他和 Center 的关系（还说不清 / 正在面对 / 没在想）；条目前的 → 表示由上一条引出；← 是跨段箭头，指回前面某段的某一条，冒号前是关系，「」里是那一条的关键词；⟲ 是前面仍在起作用的东西。方括号里是条目编号。

这条线应该自己就能读通：只读它，就能明白他每一段为什么会这样，理由来自他前面经历过、想过、发现过的事。请逐段判断：
1. self：只读这条线，这一段他此刻为什么会这样，能不能从线自己的前文看明白？成立 / 勉强 / 不成立，写一句理由。
2. 每一条：是在说他的内心原因或变化（他想要什么、怕什么、发现了什么、因此怎样），还是在描写一种感受、画面或身体反应（像在转述听音乐时的感觉，本身没说出为什么）？原因 / 描写。
3. 每个 ← 箭头：只读线，这个前后关系是否自然成立、有没有必要？成立且必要 / 可有可无 / 读不出关系。写一句理由。
最后整体判断：只读这条线，是不是一件自己连贯、有来龙去脉的事；最主要的问题是什么。
戏剧化、主观、只讲一个故事都不算缺点。

【线】
{LINE}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "self": "成立", "self_why": "……", "items": [{{"id": "S01-1", "kind": "原因"}}],
   "arrows": [{{"to": "S02-1", "label": "成立且必要", "why": "……"}}]}}],
 "whole": "……", "main_problem": "……"}}
```"""
TRANS = """下面是一条“线”（Thread，一个人在肖邦{NAME}里经历的一件事，按段写成关系图），以及另一批人听这首曲子每一段写下的听感记录（珠子）。
线和珠子会并排展示：珠子写此刻听到、感到的具体样子；线应该用他自己的经历给出“为什么偏偏此刻会这样”，而不是把珠子的感受再说一遍。

请逐条判断线的每一条：
- 自己的原因：说的是他自己的想法、处境变化或前因，即使拿掉珠子也有意义；
- 复述珠子：把珠子里写的感受、画面、身体反应或比喻换个说法放进了线，本身没给出原因；
- 两者都有：既有自己的原因，也夹带了复述。
复述的写出是对应哪颗珠子的哪句话。

【线】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

只输出 json：
```json
{{"items": [{{"id": "S01-1", "label": "自己的原因", "bead": "", "why": "……"}}]}}
```"""


# 11-02 JV=2 (标准.md): "why now" is felt, not causal sentences; continuation / immersion can stand; no 原因/描写 split
# (it pushed lines toward psychological analysis); per segment also: repeats an earlier conclusion? label matches content?
import os as _os
JV = _os.environ.get("JV", "1")
ALONE2 = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按音乐段落分段，每段几条要点。只给你这条线，没有别的材料。
每段标题后的括号是他此刻和整件事的关系（没在想 / 还说不清 / 正在面对）；〔〕是这句接着前面哪一段的哪一条；方括号里是条目编号。

这条线应该自己就成立：有逻辑、有时序、内在有发展，各段不是各说各的；看得出他此刻为什么这样，但不需要用“因为……所以……”交代——前面经历过的、已经明白的，成为后面的理由，后面的经历又让前面的意味更清楚。推动它的是他自己前面的经历，不是音乐里发生了什么，也不是新编的事件。一段只是延续、沉浸或暂时没在想，也可以成立。

请逐段判断，每项写一句理由：
1. self：只读这条线，这一段他此刻为什么这样，读得出来吗？成立 / 勉强 / 不成立。
2. repeat：这一段有没有把前面已经说过、已经得出的东西当成新的再说一遍？有 / 没有；有就写出哪一条重说了哪一条。
3. label：段首标的关系和这一段实际写的内容对得上吗？对得上 / 对不上。
最后整体判断：只读这条线，是不是一件自己长出来、往前走的事；最主要的问题是什么。
戏剧化、主观、只讲一个故事都不算缺点。

【线】
{LINE}

只输出 json：
```json
{{"sections": [{{"sec": "S01", "self": "成立", "self_why": "……", "repeat": "没有", "repeat_what": "", "label": "对得上", "label_why": "……"}}],
 "whole": "……", "main_problem": "……"}}
```"""
TRANS2 = """下面是一条“线”（一个人在肖邦{NAME}里经历的一件事，按段写成要点），以及另一批人听这首曲子每一段写下的听感记录（珠子）。
线和珠子会排在一起给读者看：珠子写此刻听到、感到的样子；线讲他自己的经历，只要在同一段里有情境相近的处境或原因就行，不该把珠子再说一遍。

请逐条判断线的每一条：
- 自己的原因：说的是他自己的经历、想法或处境，拿掉珠子也有意义；
- 复述珠子：把珠子里的感受、画面、比喻换个说法放进了线，或者把珠子里想象出的人物动作、情节写成了他真的经历的事；
- 两者都有：既有自己的经历，也夹带了复述。
复述的写出是对应哪颗珠子的哪句话。

【线】（方括号里是条目编号）
{LINE}

【珠子】
{BEADS}

只输出 json：
```json
{{"items": [{{"id": "S01-1", "label": "自己的原因", "bead": "", "why": "……"}}]}}
```"""


def graph(w, tag):
    return V.v6(w) if tag == "v6" else V.graph_of(w, tag)


def line_ids(g):
    """the line with [id] tags and ← arrows that also name the target item, so judges can refer to them"""
    return V.view(g, ids=True)


A, T = ("al2", "tr2") if JV == "2" else ("al", "tr")


def run(tags):
    jobs = []
    for tag in tags:
        for w in ("op60", "op61"):
            g = graph(w, tag)
            ma = (ALONE2 if JV == "2" else ALONE).format(NAME=covjudge.NAME[w], LINE=line_ids(g))
            mt = (TRANS2 if JV == "2" else TRANS).format(NAME=covjudge.NAME[w], LINE=line_ids(g), BEADS=V.beads(w))
            for j, m in V.JUDGES.items():
                for rid, msg in ((f"{A}_{w}_{j}_{tag}", ma), (f"{T}_{w}_{j}_{tag}", mt)):
                    if not evo.done(rid):
                        jobs.append((rid, lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "v6-alone"})))
    evo.run_parallel(jobs, 12)
    for tag in tags:
        summarize(tag)


def summarize(tag):
    out = {}; md = [f"# 线单独读 / 是否翻译珠子：{tag}", ""]
    for w in ("op60", "op61"):
        g = graph(w, tag); n_items = sum(len(s["items"]) for s in g["segments"]); n_arrows = sum(len(s["because"]) for s in g["segments"])
        for j in V.JUDGES:
            a = V.parse(f"{A}_{w}_{j}_{tag}") or {}; t = V.parse(f"{T}_{w}_{j}_{tag}") or {}
            rep = sum(s.get("repeat") == "有" for s in a.get("sections") or []); badlab = sum(s.get("label") == "对不上" for s in a.get("sections") or [])
            selfc = Counter(s.get("self") for s in a.get("sections") or [])
            kind = Counter(x.get("kind") for s in a.get("sections") or [] for x in s.get("items") or [])
            arr = Counter(x.get("label") for s in a.get("sections") or [] for x in s.get("arrows") or [])
            tr = Counter(x.get("label") for x in t.get("items") or [])
            key = f"{w}_{j}"
            out[key] = {"repeat": rep, "label_mismatch": badlab, "items": n_items, "arrows": n_arrows, "self": dict(selfc), "kind": dict(kind), "arrow": dict(arr), "trans": dict(tr),
                        "whole": a.get("whole", ""), "main_problem": a.get("main_problem", ""),
                        "weak_secs": [(s.get("sec"), s.get("self"), s.get("self_why", "")) for s in a.get("sections") or [] if s.get("self") != "成立"],
                        "retold": [(x.get("id"), x.get("label"), x.get("bead", ""), x.get("why", "")) for x in t.get("items") or [] if x.get("label") != "自己的原因"]}
            md += [f"## {'Op.60' if w == 'op60' else 'Op.61'} · {'gpt-6' if j == 'g6' else 'gpt-5.6'}", "",
                   f"- 只读线，各段“此刻为什么”：成立 {selfc.get('成立', 0)} / 勉强 {selfc.get('勉强', 0)} / 不成立 {selfc.get('不成立', 0)}（共 {len(g['segments'])} 段）",
                   f"- 只读线，条目性质：原因 {kind.get('原因', 0)} / 描写 {kind.get('描写', 0)}（共 {n_items} 条）",
                   f"- 只读线，箭头：成立且必要 {arr.get('成立且必要', 0)} / 可有可无 {arr.get('可有可无', 0)} / 读不出关系 {arr.get('读不出关系', 0)}（共 {n_arrows} 个）",
                   f"- 对照珠子，条目：自己的原因 {tr.get('自己的原因', 0)} / 复述珠子 {tr.get('复述珠子', 0)} / 两者都有 {tr.get('两者都有', 0)}",
                   f"- 整体：{a.get('whole', '')}", f"- 最主要的问题：{a.get('main_problem', '')}", ""]
            md += [f"  - {s} {st}：{why}" for s, st, why in out[key]["weak_secs"]]
            md += [f"  - {i} {lab}（{b}）：{why}" for i, lab, b, why in out[key]["retold"]] + [""]
            print(tag, key, f"段成立 {selfc.get('成立', 0)}/{len(g['segments'])} 勉强 {selfc.get('勉强', 0)} 不成立 {selfc.get('不成立', 0)} | "
                  + (f"重说 {rep} 段 | 标签对不上 {badlab} 段 | " if JV == "2" else "") + 
                  f"条目 原因 {kind.get('原因', 0)} 描写 {kind.get('描写', 0)} /{n_items} | 箭头 必要 {arr.get('成立且必要', 0)} 可有可无 {arr.get('可有可无', 0)} 读不出 {arr.get('读不出关系', 0)} /{n_arrows} | "
                  f"复述珠子 {tr.get('复述珠子', 0)} 两者都有 {tr.get('两者都有', 0)} 自己的原因 {tr.get('自己的原因', 0)}", flush=True)
    (V.OUT / f"alone{'2' if JV == '2' else ''}_{tag}.md").write_text("\n".join(md), encoding="utf-8")
    json.dump(out, open(V.OUT / f"alone{'2' if JV == '2' else ''}_{tag}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    run(sys.argv[1:])
