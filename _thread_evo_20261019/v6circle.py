"""DAG N09d (11-01): fix the open review's CUMULATIVE findings at the content level.
Found: across five styles of the same content (h23 / third person free / first person / from meaning notes) Gemini's open
review names the same two problems — a narrow set of abstract words repeated (亲近、舍不得、温柔、那种生活、受损) and the same
dilemma re-said segment after segment ("想靠近—怕催促—收住—仍盼回应"); GPT's reviews say the same ("同一认识跨多个阶段反复完整
说明，信息增量偏小"). N09c can never fix this: its prompt says 意思一点不能变、条目数量不变, and circling is a matter of meaning.
Also N07's "不要改窄" makes every layer repeat the same Center word.
Here the writer gets only the cumulative findings (several readers), the whole line, and per segment the meanings the coverage
judges say the beads rely on (must stay). Allowed: delete or shrink a restatement to a few words of reference, merge items,
use the space for what is new in this segment, say a Center word through its different facets instead of the same word.
Not allowed: new events / people / scenes, losing a segment's own step or a bead-carrying meaning, changing relation.
ids ci_<w>_<out>.  usage: CI_ISSUES=h22k,h23 CI_COV=h22k python v6circle.py <base> <out>"""
import json, os, sys
import covjudge, evo, lang_open as L, v6fix as V
from v6gen import build, gloss_text
from v6human import line_json

P = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事，按段写成条目。几位读者连续读完后，都指出了同样的全篇问题（见【读者意见】）：同一个两难在后面几段被反复重说、几乎没有新东西；少数几个抽象词翻来覆去地用，读着像原地打转。
这不是字句问题，是内容安排的问题，所以这次允许改内容：
1. 某段在重说前面已经说过的两难或认识时，把重说删掉，或压成几个字的回指（例如“还是那份顾虑”），腾出的地方只写这一段真正新的东西：这次多知道了什么、换了什么做法、哪种办法在这里失效或有了结果、心情落在哪里。这一段本来就没新东西的，就写短。
2. 反复出现的抽象词（读者点名的那些），换成这一段里它具体指的那一面来说（见【Center 各部分指什么】里列的几个侧面），不要每段都用同一个词；但不能把它缩成其中一小件事。
3. 必须保留：每段【要保留的意思】（另一批听感记录靠这些意思接上这条线，可以换说法，不能丢）；每段他此刻和整件事的关系；段与段之间的因果。不加新的事件、人物、场景、对白，不写声音、画面、身体感受；可能的不改成确定的。
4. 每段的条目可以合并、减少，顺序可以调；说人话，句子完整；第三人称“他”；全篇字数不超过原来。每条的 cite 写它提到的更早段落里的条目编号（按你写出的新编号，第 1 段是 S01-1、S01-2……）。

【读者意见】
{ISSUES}

【Center 各部分指什么】
{GLOSS}

【要保留的意思】（按段）
{KEEP}

【线】（json）
{LINE}

只输出改好的整条线 json：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def cumulative(w, tags):
    L.PV = "2"          # 11-01: the open reviews on file are all P2 (_v2 ids); without this nothing was read
    out = []
    for tag in tags:
        L.TAG = tag
        for j in ("g6", "g56", "gem"):
            for k in ((1,) if j == "gem" else (1, 2)):
                e = V.parse(L.rid(w, "line", j, k)) or {}
                out += [f"- （{c.get('severity')}）{c.get('phenomenon')}——{c.get('effect')}；读者举的例子：" + "；".join(f"[{x.get('id') or x.get('where')}]「{x.get('quote')}」" for x in (c.get("evidence") or [])[:4])
                        + f"；可以保留的：{c.get('boundary')}；建议：{c.get('suggestion')}" for c in e.get("cumulative") or []]
    return "\n".join(out)


def keep_text(w, tag):
    out = {}
    for j in V.JUDGES:
        for x in (V.parse(f"cov_{w}_{j}_{tag}") or {}).get("beads") or []:
            if x.get("status") == "说清" and x.get("items"):
                out.setdefault(x.get("sec"), set()).add(str(x["items"]))
    return "\n".join(f"{sec}：" + "；".join(sorted(v)) for sec, v in sorted(out.items()))


def run(base, out):
    tags = os.environ.get("CI_ISSUES", base).split(","); cov = os.environ.get("CI_COV", base)
    writer = os.environ.get("CI_WRITER", "argon")
    def piece(w):
        g = V.graph_of(w, base); rid = f"ci_{w}_{out}"
        iss = cumulative(w, tags)
        if not evo.done(rid):
            msg = P.format(NAME=covjudge.NAME[w], ISSUES=iss, GLOSS=gloss_text(w), KEEP=keep_text(w, cov), LINE=line_json(g))
            if writer == "argon":
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-circle"})
            elif writer == "gem":
                evo.call_gemini_direct(rid, msg, meta={"stage": "v6-circle"})
            else:
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-circle"})
        G, kept = build(w, base, out, V.parse(rid) or {})
        C = sum(len(i["text"]) for s in g["segments"] for i in s["items"]); T = [i["text"] for s in G["segments"] for i in s["items"]]
        print(w, out, "累积意见", iss.count("\n") + 1, "条", "条目", sum(len(s["items"]) for s in g["segments"]), "→", len(T), "字数", C, "→", sum(map(len, T)), "没写出的段", kept, flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
