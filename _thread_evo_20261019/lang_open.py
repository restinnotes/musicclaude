"""10-31 (user: "排几个 gpt 去直接评价这段文字的语言问题 … 不需要暗示他 … 就直接说 他这里表达通不通顺 是否人话 … 包括珠子"):
open-ended language review, no categories, no hints. Texts: the line (h13) and the beads, per work; judges gpt-6 and 5.6,
2 runs each. ids lo_<w>_<text>_<judge>_r<k>.  usage: python lang_open.py run | report"""
import json, sys
import covjudge, evo, v6fix as V

P = """请读下面这段中文。它是{WHAT}。

请你逐处指出读起来不通顺、不像人话、让你别扭或要停下来想一想的地方：引出原文，说一句为什么，再给一个更自然的说法。没有问题的地方不用提，不要为了凑数挑毛病。
最后整体说一说：这段文字的语言你给几分（1–10），最主要的问题是什么，有没有一再出现的毛病。

【文字】
{TEXT}

只输出 json：
```json
{{"issues": [{{"where": "段号或位置", "quote": "原文", "why": "…", "better": "…"}}], "score": 0, "main": "最主要的问题", "recurring": ["一再出现的毛病"]}}
```"""
WHAT = {"line": "一段音乐听后写成的“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目（〔〕里是这句提到的前文出处）",
        "beads": "一组音乐听感记录：逐段写下肖邦{NAME}每一段听起来像什么、让人想到什么"}


NM = {"g6": "gpt-6", "g56": "5.6", "gem": "Gemini 3.8"}


TAG = __import__("os").environ.get("LO_TAG", "h13")      # which line version to review


# 10-31 v2 (GPT-6 asked why the open review missed the user's negation complaint: per-spot review sees single sentences,
# not what accumulates over the whole text): read the whole first, then local issues, then an independent cumulative check
# with several quotes as evidence and a boundary (when the same kind of wording is natural). Still no categories.
P2 = """请阅读下面这段中文。

它是一条跟随音乐发展的“线”：写的是一个人在这首曲子里经历的一件事，按段写成条目。〔〕表示这句话提到的前文出处。这段文字会和音乐听感记录一起给读者看，希望读起来像一个人在平平常常地讲自己的经历。允许含蓄，不要求补造具体人物、事件或场景。

请作为第一次读到它的普通中文读者，独立评审它的语言质量。你不知道作者此前修改过什么，也不要预先假定它有哪些毛病。

评审分成三个步骤：

第一步：连续阅读整篇。

先从头到尾阅读，把它当作一段完整的叙述，而不是一组需要逐句批改的句子。

注意实际的阅读体验：哪些地方自然流畅，哪些地方读着费劲，整篇读完后有没有留下明显的不舒服、不顺畅或者单调的感觉。

此时先不要着急改写句子，也不要预设问题类别。

第二步：检查局部语言。

逐处指出真正读起来不通顺、不像人话、让人别扭或需要停下来想一想的表达。

每处引用原文，说明为什么不自然，并给一个更自然的说法。

只指出实际存在的问题。没有问题的地方不用提，不要为了凑数挑毛病。

改写时尽量保留原句的意思、人物的心理区别和前后关系，不要为了让句子好听而擅自改变人物经历。

第三步：独立检查整篇的累积效果。

这一步很重要。请暂时放下第二步挑出的具体问题，重新从头到尾看整篇。

检查是否存在这样的情况：某一种写法单独出现时并没有明显错误，甚至完全自然，但在多处反复出现之后，让整篇的阅读体验变差。

不要只寻找单句中的错误，也不要只把第二步的问题重新归纳一遍。要真正检查连续阅读时产生的效果。

对于发现的每一种累积性问题：

1. 引用多处原文作为证据。如果问题跨越全文，尽量选取不同段落的例子；如果问题集中在同一小节，可以引用几句相邻的原文。
2. 解释为什么这些表达连起来会造成问题。不能仅仅因为某种写法出现次数多，就认定它不好。
3. 区分这种写法在哪些情况下本来是自然、必要或有效的，哪些地方才是真正多余或影响阅读的。不要把所有相似表达一律判错。
4. 说明这种累积问题的实际影响有多大，是轻微、中等还是严重。
5. 如果值得修改，提出具体的改进方向，并选择一两个代表性位置示范改写。不必机械地修改所有同类表达。

不要预设必须找到多少种累积性问题。某一种写法反复出现也可能完全合理，甚至是叙述所需要的。如果没有充分证据，就不要把它列为问题。

最后作出整体判断。

给语言质量打 1–10 分。

说清楚最影响阅读体验的是什么，哪些是次要问题。不要因为某类问题比较容易统计、比较容易举例，就高估它的重要性。

请特别注意：局部语言问题与全文累积问题是两种不同的判断。前者需要证明那句话本身不自然；后者需要证明多处表达连起来产生了不理想的效果。一种表达即使单独没有问题，也可以成为累积问题的证据，但必须讲清楚累积影响。

评审结果只输出 JSON，不要在 JSON 外添加文字。

输出结构：

```json
{{
  "issues": [
    {{
      "where": "段号或位置",
      "quote": "原文",
      "why": "这句话本身为什么不自然",
      "better": "更自然的改写"
    }}
  ],
  "cumulative": [
    {{
      "phenomenon": "从文本中独立归纳出的累积问题",
      "evidence": [
        {{
          "where": "段号或位置",
          "quote": "原文"
        }}
      ],
      "effect": "为什么这些表达连起来影响阅读体验",
      "boundary": "同类写法在哪些情况下自然、必要或有效；哪些用法才构成问题",
      "severity": "轻微、中等或严重",
      "suggestion": "具体改进方向，以及一两个代表性位置的改写示范"
    }}
  ],
  "score": 0,
  "main": "对整体语言质量的判断及最主要的问题",
  "recurring": [
    "确实有充分证据、影响阅读体验的一再出现的毛病"
  ]
}}
```

如果没有值得指出的局部问题，`issues` 返回空数组。如果没有充分证据支持的累积问题，`cumulative` 和 `recurring` 返回空数组。

【文字】

{TEXT}"""
PV = __import__("os").environ.get("LO_V", "")      # LO_V=2 -> P2, ids with _v2


def text(w, t):
    if t == "line":
        return V.view(V.graph_of(w, TAG), center=False)
    return covjudge.bead_text(w)


def rid(w, t, j, k):
    return f"lo_{w}_{t}{'' if TAG == 'h13' or t == 'beads' else '_' + TAG}_{j}_r{k}" + ("_v2" if PV == "2" else "")


if __name__ == "__main__":
    if sys.argv[1] == "run":
        jobs = []
        for w in ("op60", "op61"):
            for t in (("line", "beads") if TAG == "h13" and PV != "2" else ("line",)):
                msg = P2.format(TEXT=text(w, t)) if PV == "2" else P.format(WHAT=WHAT[t].format(NAME=covjudge.NAME[w]), TEXT=text(w, t))
                for j, m in V.JUDGES.items():
                    for k in (1, 2):
                        r = rid(w, t, j, k)
                        if not evo.done(r):
                            jobs.append((r, (lambda r=r, msg=msg + ("\n" if k == 2 else ""), m=m: evo.call(r, msg, model=m, meta={"stage": "lang_open"}))))
        if "--gem" in sys.argv:      # 10-31 user: "也可以问问 gemini3.8 虽然他不一定做得好" — one run per text
            jobs = [(rid(w, t, "gem", 1), (lambda w=w, t=t: evo.call_gemini_direct(rid(w, t, "gem", 1), (P2.format(TEXT=text(w, t)) if PV == "2" else P.format(WHAT=WHAT[t].format(NAME=covjudge.NAME[w]), TEXT=text(w, t))),
                                                                            meta={"stage": "lang_open"})))
                    for w in ("op60", "op61") for t in (("line", "beads") if TAG == "h13" and PV != "2" else ("line",)) if not evo.done(rid(w, t, "gem", 1))]
        evo.run_parallel(jobs, 8)
    md = ["# 不给分类，直接问：通不通顺、是不是人话", ""]
    for w in ("op60", "op61"):
        for t in (("line", "beads") if TAG == "h13" and PV != "2" else ("line",)):
            md += [f"## {w} · {'线 h13' if t == 'line' else '珠子'}", ""]
            for j in list(V.JUDGES) + ["gem"]:
                for k in ((1,) if j == "gem" else (1, 2)):
                    e = V.parse(rid(w, t, j, k)) or {}
                    if not e:
                        md.append(f"- {NM[j]} 第{k}次：没有结果"); continue
                    md.append(f"### {NM[j]} 第{k}次：{e.get('score')} 分，{len(e.get('issues') or [])} 处")
                    md.append(f"- 最主要的问题：{e.get('main', '')}")
                    md.append(f"- 一再出现：{'；'.join(e.get('recurring') or [])}")
                    md += [f"  - [{x.get('where')}]「{x.get('quote')}」——{x.get('why')} → {x.get('better')}" for x in e.get("issues") or []]
                    for c in e.get("cumulative") or []:
                        md.append(f"- 累积（{c.get('severity')}）：{c.get('phenomenon')}｜影响：{c.get('effect')}｜边界：{c.get('boundary')}｜建议：{c.get('suggestion')}")
                        md += [f"    - [{x.get('where')}]「{x.get('quote')}」" for x in c.get("evidence") or []]
                    md.append("")
    (V.OUT / f"lang_open{'' if TAG == 'h13' else '_' + TAG}{'_v2' if PV == '2' else ''}.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(l for l in md if l.startswith(("##", "###", "- 最主要", "- 一再"))))
