"""10-31 (user: "现在的人话还是不太行 ... 稳稳、亲近这种抽象的词 ... 很多没有必要的否定性的东西 ... '他原先怕顾不上亲近，如今事情越占心思，
那份向往真被挤到后头' 这种完全读不通的东西 ... gemini 很可能能够直接写出人话 ... gpt 的优势在于发现问题"; reference: the Turing
SillyTavern preset blocks (往复族, 否定-修正句式, 否定式反应, 排比, 主语链, 判语收尾) and op7418/Humanizer-zh (不是X而是Y, 格言伪深度,
AI 高频词, 模糊关联, 层叠的“的”, 四字词排比, 套话收尾...)). A general language pass, piece-agnostic:
  find   : GPT (mimicgate gpt-6) lists the language problems of a line item by item, by type, with the exact words (hu_<w>_<tag>).
           The number of problems is also the new 人话 metric (run it on any version).
  write  : Gemini rewrites the line from the problem list; meaning, item order, citations and segment structure stay
           (hw_<w>_<out>, gemini-3.8-flash-high, one call per piece).
  write with HUMAN_FULL=1: Gemini re-says EVERY item in spoken voice (h2), the problem list only as reference.
  write with HUMAN_MODE=3: re-say every item with self-checks from the Turing preset (删掉否定那半句少什么 / 来回只写变化 /
           一句一主语) + no idioms, slang, exaggeration, no longer than the original (after h2 drifted into 俗语 and +30% length).
  HUMAN_WRITER=argon: Gemini 4 Argon (local AIStudio2API).
  HUMAN_WRITER=gpt: the same prompt written by gpt-6 instead of Gemini (to compare writers).
  HUMAN_MODE=5: mode 3 but Center words and what they cover keep their breadth (亲近 is not turned into 待在一起).
  HUMAN_MODE=6: no fixed abstract-word list (keep-words come from the gloss), negations that are his choice stay, + inner.
  HUMAN_MODE=4: mode 3 + allow one inner half-sentence per segment ("他想：……") — the inner/outer idea.
usage: python v6human.py find <tag> [...] | write <base> <out> | fixlost <base> <tag> <out>
  fixlost: segments that >= 2 repeated blind reports say lost something of <base> are re-said with those notes."""
import json, re, sys
from collections import Counter
import covjudge, evo, v6fix as V
from v6gen import build, gloss_text

RULES = """1. 读不通：一句话里因果、指代、主语跳来跳去，读者要停下来猜才懂（例：“他原想先忙完再说，如今越忙那件事越被挤到后头，他才发现顾不上的其实是自己”）。
2. 抽象空词：没有具体所指的状态词、大词（例如“稳稳”“自在”“余地”“安宁”“温柔”这类），读者不知道到底指什么样的想法或处境。Center 的核心词可以保留，但要让读者知道它在这里指什么。
3. 不必要的否定：用否定来写他（“不再……也不……”“不必……不用……”“没……”成串）；“不是 A，而是 B”而 A 并不是前文真有的预期；写他没做什么，而不写他在做什么、想要什么。自检：删掉否定那半句，读者少知道什么？什么也不少就算问题。
4. 往复：做了又收回、想了又放下、离开又回来，局面没有变化（这类来回只留结果，或写出这一次带来的变化）。
5. 公式化：排比、对仗、格言、伪深度的总结句，“他终于明白”式判语，句尾拔高。
6. 腔调：书面腔、电报腔、文言腔，四字词堆砌，“的”层层叠，被字句，“进行＋动词”。
7. 主语链：一句里主语换来换去，或者省略主语后读起来像别的人或物在做事。
8. 重复：相邻条目把同一个意思说了两遍。"""

FIND = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目（方括号里是条目编号，〔〕里是这条提到的前文）。它要像一个人平平常常讲自己的事那样好懂。
请只看语言，逐条找出下面这些问题（找不到就不报，不要为了报而报；内容、情节、观点都不评）：
{RULES}

只输出 json：
```json
{{"problems": [{{"id": "S01-2", "type": 3, "words": "原文里出问题的那几个字", "why": "一句话说为什么是问题"}}]}}
```

【线】
{LINE}"""

WRITE = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目。请把它改成一个人平平常常讲自己的事时会说的话——自然、好懂、具体。

要改的问题，另一位编辑已经逐条找出来了（见【问题清单】）；没列出的条目，读起来别扭的也可以顺手改，读着顺的原样保留。改的时候：
- 意思一点不能变：不增加原文没有的事件、人物、背景、感受，不删掉某条独有的意思；可能的不改成确定的，相关的不改成因果。
- 少用否定：直接写他在做什么、想要什么、怕什么；“不是……而是……”只在前面真有那个预期时才用。
- 抽象词换成具体说法：读者要知道他到底在想什么样的事；但下面【Center 各部分指什么】里的意思要守住，不能改窄或换掉。
- 每条一句话、只说一件事，一般二三十字、最多五十字；不用分号把几件事串起来；不写排比、格言、总结句；不写声音、画面、身体感受；第三人称“他”。
- 段落、条目顺序和数量尽量不变（同一段里两条说的是同一件事，可以合成一条）；每条的 cite（它提到的前文条目编号）原样保留。

【Center 各部分指什么】
{GLOSS}

【问题清单】
{PROBLEMS}

【线】（json；sec 是段，items 里 id 是条目编号，cite 是它提到的前文条目）
{LINE}

只输出改好的 json，结构和上面一样：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


WRITE2 = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目。现在它读起来还像是在“写”：抽象词多（自在、安宁、温柔、余地之类）、否定句多（不再……也不……、不必……、不是……而是……）、有的句子要读两遍才懂。
请你把每一条都重新说一遍，就像这个人坐下来，跟一个朋友平平常常讲自己这段经历——用说话的口气，具体、好懂；少用否定，直接说他在做什么、想要什么、怕什么；不用排比、格言、总结句。

必须守住：
- 每条原来的意思一点不能变：不加原文没有的事件、人物、背景、感受，不丢掉某条独有的意思；可能的不改成确定的，相关的不改成因果。
- 下面【Center 各部分指什么】里的意思要守住，不能改窄或换掉。
- 段落、条目顺序和数量不变（同一段里两条说的是同一件事，可以合成一条）；每条的 cite 原样保留。
- 每条一句话、只说一件事，一般二三十字、最多五十字；不写声音、画面、身体感受；第三人称“他”。

另一位编辑找出的问题，可以作参考（不限于这些）：
{PROBLEMS}

【Center 各部分指什么】
{GLOSS}

【线】（json；sec 是段，items 里 id 是条目编号，cite 是它提到的前文条目）
{LINE}

只输出改好的 json，结构和上面一样：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


WRITE3 = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目。请把每一条重新说一遍，让它读起来像这个人跟一个熟朋友平平常常讲自己这段经历：一读就懂，说的是具体的想法，不像在写文章。

改法（每一条都按这几点过一遍）：
1. 说具体：抽象的状态词（亲近、自在、安宁、分寸、余地、温柔、珍惜、投入之类）换成他具体在想什么、想做什么、怕什么。但下面【Center 各部分指什么】里的意思要守住，不能改窄或换成另一件事。
2. 正着说：直接写他在做什么、想要什么、怕什么。每个否定都自检：删掉否定那半句，读者少知道什么？什么也不少，就删掉，只写正面那半句。“不是A而是B”“不再……”“不必……”“不用……”只在A确实是前文写过的想法时才用。
3. 来回只写变化：“想A却又B”“收回又放不下”“一边……一边……”这种来回，只在这一次和前面不同时才写，写出这次多了什么；没有变化就只写结果。注意：他在两头之间被牵着，本来就是这条线要讲的事，这层意思不能丢，只是不要写成动作一样的来回。
4. 一句读懂：一句话一个主语、一件事，因果顺着说，读者不用回头再读。不用分号。
5. 平常话：不用成语、俗语、夸张说法（比如“豁出命”“催命符”）、比喻；不用排比、格言、总结句；“如今”“便”“却”“仍”“终于”这类书面虚词少用。
6. 不加长：每条不比原来长，全篇字数不超过原来。

例：
✗ 他不再执着于结果，也不必再证明什么，只是安稳地待在当下。
✓ 他先不去想结果会怎样，只想把手上这件事做完。
✗ 他原先怕顾不上那份打算，如今琐事越占心思，那份打算真被挤到后头。
✓ 琐事越来越多，他原来最想做的事，渐渐顾不上去想了。

必须守住：
- 每条原来的意思一点不能变：不加原文没有的事件、人物、背景、感受，不丢掉某条独有的意思；可能的不改成确定的，相关的不改成因果。
- 段落、条目顺序和数量不变（同一段里两条说的是同一件事，可以合成一条）；每条的 cite 原样保留。
- 不写声音、画面、身体感受；第三人称“他”。{EXTRA}

另一位编辑找出的问题，可以作参考（不限于这些）：
{PROBLEMS}

【Center 各部分指什么】
{GLOSS}

【线】（json；sec 是段，items 里 id 是条目编号，cite 是它提到的前文条目）
{LINE}

只输出改好的 json，结构和上面一样：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""

OLD_R1 = "1. 说具体：抽象的状态词（亲近、自在、安宁、分寸、余地、温柔、珍惜、投入之类）换成他具体在想什么、想做什么、怕什么。但下面【Center 各部分指什么】里的意思要守住，不能改窄或换成另一件事。"

# 10-31 mode 5: blind judges said mode 3 lost coverage where Center words were made concrete (亲近 → 待在一起). Center words
# and what they cover stay in their own breadth; only the other empty words are made concrete.
KEEP_CENTER = """1. 说具体，但 Center 的词不动：Center 里的词，以及下面【Center 各部分指什么】里它在这首曲子里指的那几样东西，用原词或同样宽的说法，不要换成其中一小件事（例如把“亲密”换成“待在一起”，就把一整件事缩成了一小件）。其余的抽象状态词（自在、安宁、分寸、余地、稳稳之类）换成他具体在想什么、想做什么、怕什么。"""

INNER = """
- 他心里的话可以直接写出来，像他当时对自己说的半句话（例：他想：再试一次吧。），每段至多一处，只用在这一段最要紧的地方；心里话说的也必须是原条已有的意思。"""

# 10-31 mode 6 (from the blind judges' lost lists on h3–h9): (a) a fixed list of "abstract words" hit Center words of some
# piece (亲近 in Op.60/61, 分寸 = Op.60's self-restraint), so which words stay now comes only from the piece's gloss;
# (b) "删掉否定那半句" removed negations that ARE content — he refuses a way out (不肯为了省事说自己不想要, 不用否认喜欢
# 来守住分寸). Mode 6 = these two fixes + the inner half-sentence of mode 4 (h4 was the best of the first round).
R1_6 = """1. 说具体，但 Center 的词不动：下面【Center 各部分指什么】里的词和它在这首曲子里指的那几样东西，用原词或同样宽的说法，不要换成其中一小件事（例如把一整种向往换成其中某一件小事）。其余空泛的状态词，换成他具体在想什么、想做什么、怕什么。"""
R2_6 = """2. 正着说，但留下他的选择：能直接写他在做什么、想要什么、怕什么的，就直接写。每个否定都自检：删掉否定那半句，读者少知道什么？什么也不少，就删掉。但如果否定说的是他拒绝了哪条路、放下了哪个原来的想法、不肯拿什么去换什么（例如“他不肯为了图省事就放弃原来的打算”），那就是他的选择，必须留下，可以换个说法，但要让读者仍然看得出他拒绝的是什么。“不是A而是B”只在A确实是前文写过的想法时才用。"""
OLD_R2 = "2. 正着说：直接写他在做什么、想要什么、怕什么。每个否定都自检：删掉否定那半句，读者少知道什么？什么也不少，就删掉，只写正面那半句。“不是A而是B”“不再……”“不必……”“不用……”只在A确实是前文写过的想法时才用。"


def line_json(g):
    return json.dumps({"segments": [{"sec": s["sec"], "relation": s.get("relation"),
                                     "items": [{"id": it["id"], "text": it["text"],
                                                "cite": [b["from"] for b in s["because"] if b.get("to") == it["id"] and b.get("rel") == "引用"]}
                                               for it in s["items"]]} for s in g["segments"]]}, ensure_ascii=False, indent=0)


def find(tags):
    for T in tags:
        jobs = [(f"hu_{w}_{T}", (lambda w=w: evo.done(f"hu_{w}_{T}") or evo.call(f"hu_{w}_{T}", FIND.format(NAME=covjudge.NAME[w], RULES=RULES,
                 LINE=V.view(V.v6(w) if T == "v6" else V.graph_of(w, T), ids=True, center=False)), model=evo.G6, meta={"stage": "v6-human-find"})))
                for w in ("op60", "op61")]
        evo.run_parallel(jobs, 2)
        res = {}
        for w in ("op60", "op61"):
            P = (V.parse(f"hu_{w}_{T}") or {}).get("problems") or []
            g = V.v6(w) if T == "v6" else V.graph_of(w, T)
            n_items = sum(len(s["items"]) for s in g["segments"]); chars = sum(len(i["text"]) for s in g["segments"] for i in s["items"])
            c = Counter(str(p.get("type")) for p in P)
            res[w] = {"problems": len(P), "items": n_items, "chars": chars, "per100": round(100 * len(P) / max(chars, 1), 2), "by_type": dict(c), "list": P}
            print(T, w, "语言问题", len(P), f"（每百字 {res[w]['per100']}）", "按类", dict(sorted(c.items())), flush=True)
        (V.OUT / f"human_{T}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


def write(base, out):
    def piece(w):
        g = V.graph_of(w, base)
        P = (V.parse(f"hu_{w}_{base}") or {}).get("problems") or []
        names = {1: "读不通", 2: "抽象空词", 3: "不必要的否定", 4: "往复", 5: "公式化", 6: "腔调", 7: "主语链", 8: "重复"}
        pt = "\n".join(f"- [{p.get('id')}] {names.get(int(p.get('type') or 0), p.get('type'))}：「{p.get('words', '')}」——{p.get('why', '')}" for p in P) or "（无）"
        rid = f"hw_{w}_{out}"
        if not evo.done(rid):
            env = __import__("os").environ; mode = env.get("HUMAN_MODE") or ("2" if env.get("HUMAN_FULL") else "1")
            T = {"1": WRITE, "2": WRITE2}.get(mode) or WRITE3.replace("{EXTRA}", INNER if mode == "4" else "")
            if mode == "5":
                T = T.replace(OLD_R1, KEEP_CENTER)
            if mode == "6":
                T = WRITE3.replace("{EXTRA}", INNER).replace(OLD_R1, R1_6).replace(OLD_R2, R2_6)
                assert R1_6 in T and R2_6 in T
            msg = T.format(NAME=covjudge.NAME[w], GLOSS=gloss_text(w), PROBLEMS=pt, LINE=line_json(g))
            if env.get("HUMAN_WRITER") == "gpt":      # 10-31 user: Gemini is not a must; GPT may do better in a long pipeline
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-human-write"})
            elif env.get("HUMAN_WRITER") == "argon":  # 10-31: Gemini 4 Argon (local AIStudio2API), ~100 calls allowed
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-human-write"})
            else:
                evo.call_gemini_direct(rid, msg, meta={"stage": "v6-human-write"})
        e = V.parse(rid) or {}
        G, kept = build(w, base, out, e)
        print(w, out, "按问题清单改", len(P), "处", "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), "没写出的段", kept, flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


FIXLOST = """下面是肖邦{NAME}的一条“线”：一个人在这首曲子里经历的一件事，按段写成条目。它是从一版较早的稿子润色来的，读起来已经像人话了；但几位独立的评委对照早稿，反复指出下面几段把早稿里的一些意思弄丢了（见每段的【评委说丢了】）。
请只重写这几段，把丢的意思找回来，同时保持现在这种平常说话的口气。其余段落不用输出。

改的时候：
{RULES}

{SEGS}

【Center 各部分指什么】
{GLOSS}

只输出这几段改好的 json（每条的 cite 照现在这版填）：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def fixlost(base, tag, out, k=2):
    """10-31: segments that >= k of the repeated blind reports (blind_<tag>_vsb0*.json) say lost something of the base
    are re-said by the writer with those notes and the base text; the rest stays word for word (general, notes only from
    the judges' output)."""
    import os
    rules = WRITE3.replace("{EXTRA}", INNER).replace(OLD_R1, R1_6).replace(OLD_R2, R2_6)
    rules = rules.split("改法（每一条都按这几点过一遍）：")[1].split("另一位编辑找出的问题")[0].replace("{{", "{").replace("}}", "}")
    L = {}
    for suf in ("", "_r2", "_r3", "_r4"):
        f = V.OUT / f"blind_{tag}_vs{base}{suf}.json"
        if f.exists():
            for rid, x in json.loads(f.read_text(encoding="utf-8")).items():
                for sec, it in x["lost_new"]:
                    L.setdefault(x["w"], {}).setdefault(sec, []).append(it.get("what", ""))
    def piece(w):
        bad = {sec: xs for sec, xs in (L.get(w) or {}).items() if len(xs) >= k}
        A = {x["sec"]: x for x in json.loads(line_json(V.graph_of(w, base)))["segments"]}
        B = {x["sec"]: x for x in json.loads(line_json(V.graph_of(w, tag)))["segments"]}
        rid = f"hl_{w}_{out}"
        if bad and not evo.done(rid):
            segs = "\n\n".join(f"### {sec}\n【早稿】\n" + "\n".join(f"- {it['text']}" for it in A[sec]["items"])
                                + "\n【现在这版】（json）\n" + json.dumps(B[sec]["items"], ensure_ascii=False)
                                + "\n【评委说丢了】\n" + "\n".join(f"- {x}" for x in xs) for sec, xs in sorted(bad.items()) if sec in A and sec in B)
            msg = FIXLOST.format(NAME=covjudge.NAME[w], RULES=rules, SEGS=segs, GLOSS=gloss_text(w))
            if os.environ.get("HUMAN_WRITER") == "gpt":
                evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-human-fixlost"})
            elif os.environ.get("HUMAN_WRITER") == "argon":
                evo.call_argon_direct(rid, msg, meta={"stage": "v6-human-fixlost"})
            else:
                evo.call_gemini_direct(rid, msg, meta={"stage": "v6-human-fixlost"})
        e = (V.parse(rid) or {}) if bad else {}
        e["segments"] = [x for x in e.get("segments") or [] if x.get("sec") in bad]
        G, kept = build(w, tag, out, e, allow_empty=True)
        print(w, out, f"被≥{k}份盲评说丢了的段", {sec: len(xs) for sec, xs in sorted(bad.items())}, "重写了", [x["sec"] for x in e["segments"]],
              "字数", sum(len(i["text"]) for x in G["segments"] for i in x["items"]), flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


# 10-31 (user: "他这个非常能去发现问题 我觉得应该就是要通过这种方式去迭代语言的"): the problems now come from an OPEN review
# (lang_open.py: no categories, "通不通顺、是不是人话", several judges) instead of my 8 categories; the writer fixes those spots
# and the same kind of problem elsewhere; meaning, items, cites stay.
FIXOPEN = """下面是一条“线”：一个人在肖邦{NAME}里经历的一件事，按段写成条目。几位读者不带任何框框读了它，逐处指出了读起来不通顺、不像人话、别扭的地方（见【读者意见】，同一处可能被几位都指出）。
请据此改这条线：
- 被指出的地方都要改；同样的毛病在别的条目里也有的，一并改。读着顺的地方原样保留，不要为改而改。
- 读者给的“更自然的说法”可以参考，但不一定照抄；改完要像一个人平平常常讲自己的事。
- 意思一点不能变：不加原文没有的事件、人物、背景、感受，不丢掉某条独有的意思；可能的不改成确定的，相关的不改成因果。下面【Center 各部分指什么】里的意思要守住，可以换成具体的说法，但不能缩成其中一小件事。
{LENRULE}
- 段落、条目顺序和数量不变（同一段里两条说的是同一件事，可以合成一条）；每条的 cite 原样保留；第三人称“他”；不写声音、画面、身体感受。

【读者意见】
{ISSUES}

【Center 各部分指什么】
{GLOSS}

【线】（json；sec 是段，items 里 id 是条目编号，cite 是它提到的前文条目）
{LINE}

只输出改好的 json，结构和上面一样：
```json
{{"segments": [{{"sec": "S01", "items": [{{"text": "……", "cite": []}}]}}]}}
```"""


def open_issues(w, tag):
    import lang_open as L
    L.TAG = tag; out = []    # reads v1 or v2 reviews depending on LO_V
    for j in ("g6", "g56", "gem"):
        for k in ((1,) if j == "gem" else (1, 2)):
            e = V.parse(L.rid(w, "line", j, k)) or {}
            out += [f"- [{x.get('where')}]「{x.get('quote')}」——{x.get('why')}（可以考虑：{x.get('better')}）" for x in e.get("issues") or []]
            out += [f"- 整体：{x}" for x in e.get("recurring") or []]
            out += [f"- 全篇累积（{c.get('severity')}）：{c.get('phenomenon')}——{c.get('effect')}；哪些可以保留：{c.get('boundary')}；建议：{c.get('suggestion')}" for c in e.get("cumulative") or []]
    return "\n".join(out)


def fixopen(base, out):
    import os
    def piece(w):
        g = V.graph_of(w, base); rid = f"ho_{w}_{out}"
        if not evo.done(rid):
            lenrule = ("- 篇幅：全篇字数不超过原来。把话说完整需要的字，从别处删掉重复和可有可无的话来腾出，不要加原来没有的解释。" if os.environ.get("FIX_LEN") == "0"
                       else "- 篇幅：全篇字数最多比原来多一成。把话说完整可以补几个字，但不要把一句扩成两句的分量，也不要加原来没有的解释。")
            issues = open_issues(w, base); n = issues.count("\n- ") + bool(issues)
            print(w, base, "读到开放评审意见", n, "条", flush=True)    # 11-01 rule: never run a fix on zero inputs
            if not n:
                raise SystemExit(f"{w} {base}: 没读到任何开放评审意见，停下")
            msg = FIXOPEN.replace("{LENRULE}", lenrule).format(NAME=covjudge.NAME[w], ISSUES=issues, GLOSS=gloss_text(w), LINE=line_json(g))
            writer = os.environ.get("HUMAN_WRITER", "argon")
            (evo.call_argon_direct if writer == "argon" else evo.call_gemini_direct)(rid, msg, meta={"stage": "v6-human-fixopen"}) if writer != "gpt" else evo.call(rid, msg, model=evo.G6, meta={"stage": "v6-human-fixopen"})
        G, kept = build(w, base, out, V.parse(rid) or {})
        print(w, out, "按开放评审改", "字数", sum(len(i["text"]) for s in G["segments"] for i in s["items"]), "没写出的段", kept, flush=True)
    evo.run_parallel([(w, (lambda w=w: piece(w))) for w in ("op60", "op61")], 2)


if __name__ == "__main__":
    a = sys.argv[1:]
    {"find": lambda: find(a[1:]), "fixlost": lambda: fixlost(a[1], a[2], a[3]), "fixopen": lambda: fixopen(a[1], a[2])}.get(a[0], lambda: write(a[1], a[2]))()
