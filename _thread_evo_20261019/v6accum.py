"""DAG N10h (11-01): accumulation — the line must move forward, not circle. Found by the blind judges comparing the DAG product
(q6k) with the repaired h17: "阶段之间更像重复同一矛盾，没有让先前的认识产生新的后果"; h17's strength (inherited from the 10-21 v6,
not from any DAG step) is that each change grows out of what he tried earlier, what it cost and what limit he found.
  judge <tag>          : two judges read the line only (no beads), per segment from the second on: what is new, which earlier item
                         it grows from, verdict 推进 / 重复 / 跳跃, and a suggestion drawn only from experiences already in the line.
                         ids ac_<w>_<j>_<tag>.
  fix <tag> <out>      : segments any judge called 重复 / 跳跃 go to the writer with the whole line, the judges' notes, and the
                         meanings the coverage judges said the beads rely on there (must stay). ids acf_<w>_<out>.
  keep <tag> <new> <out>: after judging <new>, per rewritten segment keep the new text only where fewer judge-verdicts are
                         non-推进 than in <tag>; elsewhere the old segment stays.  Coverage is then guarded by N10g.
usage: python v6accum.py judge q7k ; python v6accum.py fix q7k q8 ; python v6accum.py judge q8 ; python v6accum.py keep q7k q8 q8a"""
import json, os, sys
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text
from v6human import line_json

JUDGE = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事，按段写成条目（方括号里是条目编号，如 S03-2）。只读这条线，不需要音乐知识。
一条好的线会往前走：后面的变化来自他前面亲身试过的办法、付出的代价、发现的限制或得到的认识；前面立住的东西到后面会产生新的后果——被用上、失效、被改写，或让他换一种做法。不好的线会原地打转：后面几段把前面已经说过的矛盾或认识换个说法再说一遍，没有新的后果；或者变化突然出现，前面找不到来由。
戏剧化、只讲一个故事、情绪强烈都不是缺点；一段里情绪重复出现也不一定是打转，要看有没有新的后果。

请逐段（从第二段起）判断：
- new：这一段比前面所有段多了什么（新的认识、新的做法、某个办法的后果或失效、新付出的代价）；没有就写“无”。
- from：这一段的变化来自前面哪一条（写条目编号，一句话说怎么来的）；找不到就写“无”。
- verdict：推进 / 重复（主要在重说前面的矛盾或认识，没有新后果）/ 跳跃（有变化，但前面找不到来由）。
- repeats：如果是重复，重说的是前面哪几条（编号）。
- suggest：如果不是推进，一句话说可以从前面哪条经历里长出什么新后果（只用线里已有的经历，不加新的事件和人物）。
最后说全篇：有没有一条前后相接的发展（试过的办法—后果—下一步），最大的原地打转在哪里。

{LINE}

只输出 json：
```json
{{"segments": [{{"sec": "S02", "new": "…", "from": "…", "verdict": "推进", "repeats": [], "suggest": "…"}}], "whole": "…"}}
```"""

FIX = """下面是肖邦{NAME}的一条“线”的全文：一个人在这首曲子里经历的一件事，按段写成条目。两位读者发现其中几段在原地打转（重说前面的矛盾或认识，没有新的后果），或变化来得突然（前面找不到来由）。请只重写这几段：
- 让这一段的变化从前面他亲身经历过的东西里长出来：前面试过的办法在这里有了后果或失效，前面付出的代价在这里被他看见，前面得到的认识在这里被用上或被改写。读者的建议可以参考，但以全文前后连得上为准。
- 重说前面的话删掉或压成半句，腾出地方给这一段新的东西。只用线里已有的经历，不加新的事件、人物、场景，不写声音、画面。
- 每段【要保留的意思】是另一批听感记录靠来接上这条线的那几层意思，必须保留（可以换说法）。
- 和后面各段仍要接得上；他此刻和整件事的关系（每段的 relation）不变；保持现在的说话口气，用平常话；字数和现在大致相当；每条的 cite 照现在这版填（可以引前面的条目编号）；第三人称“他”。

【线的全文】（json）
{LINE}

【要重写的段】
{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json：
```json
{{"segments": [{{"sec": "S03", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def text(g):
    L = []
    for s in g["segments"]:
        L.append(f"## {s['sec']}（{s.get('relation') or ''}）")
        L += [f"[{it['id']}] {it['text']}" for it in s["items"]]
    return "\n".join(L)


def judge(tag):
    jobs = []
    for w in ("op60", "op61"):
        msg = JUDGE.format(NAME=covjudge.NAME[w], LINE=text(V.graph_of(w, tag)))
        for j, m in V.JUDGES.items():
            rid = f"ac_{w}_{j}_{tag}"
            if not evo.done(rid):
                jobs.append((rid, (lambda rid=rid, msg=msg, m=m: evo.call(rid, msg, model=m, meta={"stage": "v6-accum-judge"}))))
    evo.run_parallel(jobs, 4)
    for w in ("op60", "op61"):
        v = verdicts(w, tag)
        bad = {sec: d for sec, d in v.items() if any(x != "推进" for x in d.values())}
        n = sum(len(d) for d in v.values())
        print(tag, w, "非推进判定", sum(x != "推进" for d in v.values() for x in d.values()), "/", n, "| 段", {s: "/".join(d.values()) for s, d in sorted(bad.items())}, flush=True)


def verdicts(w, tag):
    out = {}
    for j in V.JUDGES:
        for x in (V.parse(f"ac_{w}_{j}_{tag}") or {}).get("segments") or []:
            out.setdefault(x.get("sec"), {})[j] = str(x.get("verdict") or "")[:2]
    return out


def notes(w, tag):
    out = {}
    for j in V.JUDGES:
        for x in (V.parse(f"ac_{w}_{j}_{tag}") or {}).get("segments") or []:
            if str(x.get("verdict") or "").startswith("推进"):
                continue
            out.setdefault(x.get("sec"), []).append(f"- {x.get('verdict')}：多了什么：{x.get('new')}；来由：{x.get('from')}；重说了：{x.get('repeats')}；建议：{x.get('suggest')}")
    return out


def keepers(w, tag):
    """what the coverage judges said the beads rely on, per segment (items quoted by 说清 verdicts)"""
    out = {}
    for j in V.JUDGES:
        for x in (V.parse(f"cov_{w}_{j}_{tag}") or {}).get("beads") or []:
            if x.get("status") == "说清" and x.get("items"):
                out.setdefault(x.get("sec"), set()).add(str(x["items"]))
    return out


def fix(tag, out):
    def piece(w):
        g = V.graph_of(w, tag); N = notes(w, tag); K = keepers(w, tag)
        segs = []
        for sec in sorted(N):
            L = [f"### {sec}", "【读者意见】"] + N[sec]
            if K.get(sec):
                L += ["【要保留的意思】"] + [f"- {k}" for k in sorted(K[sec])]
            segs.append("\n".join(L))
        print(w, out, "要重写的段", sorted(N), flush=True)
        rid = f"acf_{w}_{out}"; e = {}
        if segs:
            if not evo.done(rid):
                evo.call(rid, FIX.format(NAME=covjudge.NAME[w], LINE=line_json(g), SEGS="\n\n".join(segs), GLOSS=gloss_text(w)), model=evo.G6, meta={"stage": "v6-accum-fix"})
            e = V.parse(rid) or {}
            e["segments"] = [s for s in e.get("segments") or [] if s.get("sec") in N]
        G, _ = build(w, tag, out, e, allow_empty=True)
        print(w, out, "重写了", [s["sec"] for s in e.get("segments") or []], "字数", sum(len(i["text"]) for s in g["segments"] for i in s["items"]), "→",
              sum(len(i["text"]) for s in G["segments"] for i in s["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


def keep(tag, new, out):
    for w in ("op60", "op61"):
        a, b = verdicts(w, tag), verdicts(w, new)
        bad = lambda d: sum(x != "推进" for x in d.values())
        N = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, new)))["segments"]}
        O = {s["sec"]: s for s in json.loads(line_json(V.graph_of(w, tag)))["segments"]}
        changed = [sec for sec in N if json.dumps(N[sec]["items"], ensure_ascii=False) != json.dumps(O.get(sec, {}).get("items"), ensure_ascii=False)]
        better = [sec for sec in changed if bad(b.get(sec, {})) < bad(a.get(sec, {}))]
        e = {"segments": [{"sec": sec, "items": [{"text": it["text"], "cite": it["cite"]} for it in N[sec]["items"]]} for sec in better]}
        build(w, tag, out, e, allow_empty=True)
        print(w, out, "改过的段", changed, "推进变好、采用", better, flush=True)


if __name__ == "__main__":
    x = sys.argv[1:]
    {"judge": lambda: judge(x[1]), "fix": lambda: fix(x[1], x[2]), "keep": lambda: keep(x[1], x[2], x[3])}[x[0]]()
