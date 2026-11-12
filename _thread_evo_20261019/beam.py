"""Integration step with several paths kept alive (user 10-23: "写稿评宏观、综合阶段看珠子并多路保留，评委都要写理由，最后只给我看
综合后的成品"). Drafts never saw beads; this step does.
Per section, every kept path (its own established history) gets one call that writes 2 different readings of this section
(3 at the first), each written directly as this section's part of the relation graph (user 10-23: "线最后肯定还是关系图 …
直接在这里就把关系图加进来就可以了"): 1–3 items (<= 45 chars, one thought each, `follows` when led by the previous item, a key),
cross-section arrows only to the earlier items that really are the cause (提供理由/动摇/限制/改写/唤起), and the section's relation
to the Center (还说不清/正在面对/没在想) — the v4.3 graph form of THREAD_SPEC §九5, with no prose->graph conversion step (that step
had split one feeling into many steps and produced the abstract labels). Plus history update and self-rated credibility.
A pruning judge (other model) keeps the best WIDTH paths, with a reason for each kept/dropped path. After the last section a
final judge (both models, own reading of the piece first) ranks the surviving paths; a wording-only polish pass on the winner
(every change logged) also writes the Center sentence, which is only clear in hindsight.
Pools: drafts from the N8 prompt and the corrected D9 prompts (d9L, d9S, d9LC); unsplittable drafts left out.
Runs: 1 (S01 invented traits; stopped), 3 (Op.60 v7, prose lines — user: its 1–3 "怪的很": a whole backstory and the theme
stated over a 3-bar opening; the prune judge had kept it *because* it "建立了明确的人物起点"), 60c/61c (prose; stopped at S02–S03
for the graph switch). From 60c on: the first section may be one unclear item with no past/traits/theme; no section may add a
backstory nothing supports; pruning and final judges penalize that and forced arrows.
ids: bm<T>_<sec>_<path>, bm<T>_<sec>_prune, bm<T>_final_<judge>, bm<T>_polish.
usage: python beam.py run|final|polish|all|render <T> <op60|op61>"""
import json, random, re, sys
from pathlib import Path
import evo, node2b, seq, segcheck

CFG = {"op60": {"name": "肖邦《船歌》Op.60", "short": "《船歌》", "Op": "Op.60",
                "struct": evo.ROOT / "inputs" / "pkg" / "03_Bead机器可读",
                # 10-23 user: N8 drafts out of the pool (the corrected prompt beat it); rounds 1–6 still had them
                "pool": [f"{f}_op60_r{j}" for f in ("d9L", "d9S", "d9LC") for j in (1, 2, 3)]},
       "op61": {"name": "肖邦《幻想波兰舞曲》Op.61", "short": "《幻想波兰舞曲》", "Op": "Op.61",
                "struct": Path("D:/musicclaude/_bead_op61_20261020/deliverable/03_Bead机器可读"),
                "pool": [f"{f}_op61_r{j}" for f in ("d9L", "d9S", "d9LC") for j in (1, 2, 3)]}}
WIDTH = 3
OUT = evo.ROOT / "evaluations" / "beam"
SECS = []
BAN = "站稳 立足 挺直 安顿 承受 承担 敞开 托住 悬着 落定 归属 边界 限度 代价 空缺 位置 意义 回应 辨认".split()
RELS = ("提供理由", "动摇", "限制", "改写", "唤起")
CREL = ("还说不清", "正在面对", "没在想")


def setup(work):
    c = CFG[work]
    seq.W, seq.STRUCT, seq.POOL = work, c["struct"], c["pool"]
    seq.INTRO = seq.INTRO.replace("肖邦《船歌》Op.60", c["name"])
    SECS[:] = [s["id"] for s in segcheck.seg.load(work)["segments"]]


def bars_s(sec):
    a, b = seq.bars(sec)
    return f"{a}–{b}"


REST = ("说清它们为什么此刻出现：理由来自前面的经历，用 because 指出是前面哪一条；条目里只用几个字点到，不要复述前一段。"
        "这一段若只是前面的延续或再次出现，就说清这一次为什么不一样。理由不要只是把听感换个说法。")
# round 3 (60f/61f): 61e opened with "他怀念一段曾令自己动心的往事" — the theme named in bar 1 although the beads only half
# support it (advisor + both judges). The first section must not name what he longs for or mourns.
FIRST = ("这是第一段，没有前史：可以只写一条，允许他还说不清自己在盼什么——只写此刻被牵动、还说不清的状态。"
         "不要交代他的过去、性格或习惯，不要说出他怀念、渴望或害怕的具体是什么（例如“怀念一段往事”），也不要提前说出贯穿全曲的那件事。"
         "几种写法要真的不同。")
# round 6 (60j/61j, user 10-23): 17–23 in v8 explained only the main bead (floating, at ease) and dropped the undercurrent
# that the other beads are mostly about — the prompt said "只抓这一段最主要的那种感受" and one item. User: "不能只有最主要的"
# (and no section titles fed). v8's lines were also labels ("那份模糊的盼望在亲近中初次有了方向，因此他尝到温柔的满足"):
# the review6 C1 sentence (写他具体在想什么、怕什么、想要什么) had not been carried over.
GEN = ("\n请只处理第 {A}–{B} 小节这一段，写出 {K} 种不同的写法：都接在上面这条路已经确立的历史后面，但对这一段的感受"
       "给出真正不同的理解（不是同一个意思换个说法）。每一种写成这一段在“关系图”里的部分：\n"
       "   - items：一般 2 条，最多 3 条，每条不超过 45 个字，一条一个念头或一步变化；同一个念头里连着的几层（想要和随之的迟疑、做法和它的理由）"
       "留在一条里，不要按逗号切碎，也不要把同一种感受拆成几步。整段合计不超过 100 字，普通人一遍能懂。\n"
       "     不要只解释最主要的那一种感受：这一段的听感里有几种不同的东西（主体验、侧面、段内的转变），线要把它们一起说明——"
       "它们为什么此刻一起出现、彼此怎样牵扯；只有这一段确实只有一种感受时才写 1 条。{REST}\n"
       "     每条写 text；由本段上一条引出的，follows 写 true；再给一个 key：几个字的把手，单独看也懂。\n"
       "   - 写具体：每条都要让读者说得出他此刻具体在想什么、怕什么、想要什么或在做什么；不要用“盼望有了方向”“满足”“牵念”“缺憾”"
       "这类概括词代替。可以写那个从头到尾不变的轻处境里的小念头、小动作（例如想再待一会儿、话到嘴边又咽回去），但不编新事件来推动转折。"
       "理由要用人话讲出前后怎么接上，不要只用“因此”把两个状态连起来。\n"
       "   - 先想清楚：和上一段相比，这一段新出现了什么、哪里不一样，再写它的理由。不要用前面已经用过的同一个理由包办这一段"
       "（例如段段都是“珍惜，所以怕它不长久”），也不要把听感里已有的感受换个心理词重说一遍；理由要具体到这一段，而不是整首的总主题。"
       "证据不足时可以写得不确定，不要硬造新的转折。\n"
       "   - because：这一段真正的前因——前面段落的哪一条（写编号，如 S02-1）给这一段的哪一条（item，从 1 数）"
       "提供理由、动摇、限制、改写或唤起（rel 只能是这五个词之一）。只连最直接的前因，一条一般一个箭头，最多两个；主题相近、情绪相似、"
       "同一状态再次出现都不算。连远处的段落时，那段经历必须在这一段真的重新起了作用。每个箭头写一句 why：前面那条经历具体改变了这一段的什么；"
       "写不出来的箭头就不要连。第一段没有，写空。\n"
       "   - 新出现的动机或价值判断（例如责任、使命、要证明自己）必须有前面写过的具体前因；没有前因就不要引入。\n"
       "   - 不要把心事提前收成答案：中间各段不要把含混的感受收窄成一个明确的诉求；最后一段也不要写成已经完成的决定或已经成立的结论"
       "（音乐落定，不等于他的问题解决了）。\n"
       "   - center_relation：这一段他和贯穿全曲的那件事是什么关系：还说不清 / 正在面对 / 没在想。按这一段实际判断："
       "如果他此刻沉浸在别的感受里、没在想那件事，就写没在想。\n"
       "   - 只写他此刻怎样、为什么；不写他没有做什么，不用“同时存在”“还没有定论”这类收尾。各段开头和句式不要雷同。"
       "不要用“越……越……”句式；也不要段段用同一个动词串起来（例如每段都是“……化成……”）。不要借用听感里的词句。\n"
       "   - 不要编出不必要的心理动作（劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心）。不要交代前文和听感都撑不住的人物前史"
       "（过去的习惯、性格、身世）。听感里音乐的起伏不用写成他心情的起伏；听感里的画面和比喻是听者对音乐的形容，不是他身上发生的事。"
       "不编外部事件、物件、对白。\n"
       "   - history：到这一段为止新确立、以后仍会起作用的事（一两条短句；没有就写“无”）。\n"
       "   - credibility：1–10，你认为这种理解有多可信，并用一句话说理由（why）。\n"
       "候选解释可以采用、合并，也可以都不用。\n"
       "最后只输出一个 ```json 代码块：\n"
       '{"options": [{"items": [{"text": "…", "key": "…", "follows": false}], "because": [{"item": 1, "from": "S01-1", "rel": "提供理由", "why": "…"}], '
       '"center_relation": "还说不清", "history": ["…"], "credibility": 7, "why": "…", "uses": ["候选3"]}]}\n')

GRAPH = ("“线”是一张关系图：每段 1–3 条短条目，说明这一段的听感为什么此刻出现；“→”表示由本段上一条引出，“←”是跨段箭头，"
         "指向真正的前因（提供理由、动摇、限制、改写、唤起）；方括号里是这一段他和贯穿全曲那件事的关系。")
# round 2 (60e/61e, 10-23): round-1 judges + advisor: one cause ("珍惜，所以怕它不长久") carried 10+ sections; arrows linked
# similar moods, several per item, far back without saying why now; "下决心""他已明白" slipped through.
CRIT = ("开头几段把话说死——提前交代人物的过去、性格，或提前说出贯穿全曲的主题——要扣分（开头允许还说不清）；"
        "凡是前文和听感都撑不住的人物前史，都要扣分。"
        "逐段核对：和上一段相比，这条路说出了这一段新出现的什么？连续几段用同一个理由包办，或只是把听感换成心理词，要扣分"
        "（有意的回返可以，但要说出这一次为什么不一样）。"
        "逐条核对箭头：只有前面那条经历真的促成、改变或限制了这一段的状态才算；主题相近、情绪相似、同一状态再次出现都不算；"
        "连远处的段落而说不出它为什么此刻重新起作用的，也不算。牵强的箭头要扣分。"
        "出现“下决心”“想通了”“他已明白”这类没有必要的心理动作，要扣分；没有前因就冒出的新动机或价值判断（责任、使命……）要扣分。"
        "箭头后面“——”是写的人给出的理由，理由站不住的箭头按牵强处理。"
        "把含混的感受过早收窄成明确诉求，或把结尾写成已经完成的决定、已经成立的答案，要扣分。"
        "具体：读者能否说出他此刻具体在想什么、怕什么、想要什么或在做什么？用“盼望有了方向”“满足”“牵念”“缺憾”这类概括词堆起来、只用“因此”连起两个状态的条目，要明显扣分（换成同义的抽象说法不算具体）。只解释了这一段最主要的一种感受、丢掉侧面或段内转变的，要扣分。"
        "不要因为某条路“人物起点更明确”就偏向它。")
PRUNE = ("你是一位独立评审。我们在为{WORK}做讲解视频：听感记录（珠子）会原样给观众看。" + GRAPH +
         "线正在从头一段一段写，下面有 {N} 条写到第 {K} 段为止的路（{LABELS}），请选出最好的 {W} 条留下继续写。\n\n"
         "看这些：每段是否说明了这一段主要听感为什么此刻出现（只是话题相近不算）；理由是否真来自这条路前面的经历、而不是听感本身换个说法；"
         "有没有编出不必要的心理动作或来回摆；读起来是不是一件事在往前走；是不是普通人一遍能懂。" + CRIT +
         "也要留意保留真正不同的方向：两条路只差措辞时，只留一条。\n"
         "每条路都要写理由（留下或淘汰都要）。\n\n"
         "最后只输出一个 ```json 代码块：\n"
         '{"keep": ["路A"], "reasons": {"路A": "…", "路B": "…"}}\n\n'
         "# 听感记录（到第 {K} 段为止）\n\n{BEADS}\n\n# 各条路\n\n{PATHS}")
FINAL = ("你是一位独立评审，熟悉{WORK}。我们在为它做讲解视频：听感记录（珠子）会原样给观众看。" + GRAPH +
         "理由来自这个人前面的经历，不是“音乐忽然怎样了”。\n\n"
         "先用几句话写出你自己对{SHORT}全曲情感过程的理解，作为参照。然后比较下面 {N} 条完整的线（{LABELS}）。\n\n"
         "逐段判断：这一段的线有没有说明【主体验】为什么此刻出现（是 / 部分 / 否，每个都写一句理由）；有没有编出不必要的心理动作；"
         "有没有借用或复述听感；箭头是否真是前因。整条看：它隐含的那件贯穿全曲的事（Center）是什么，放在{SHORT}上可不可信；"
         "是不是一件事在往前走；是不是普通人一遍能懂。" + CRIT + "每个分数都写理由。\n\n"
         "最后只输出一个 ```json 代码块：\n"
         '{"my_reading": "…", "ranking": ["线A"], "paths": {"线A": {"center": "…", "segments": [{"seg": 1, "explains": "是|部分|否", "why": "…"}], '
         '"invented": {"score": 1, "why": "…"}, "opening": {"score": 1, "why": "…"}, "arrows": {"score": 1, "why": "…"}, '
         '"coherence": {"score": 1, "why": "…"}, "plain": {"score": 1, "why": "…"}, "overall": {"score": 1, "why": "…"}}}}\n'
         "（segments 要有 {NSEG} 项；分数 1–10，invented 分数高 = 编得少，opening 分数高 = 开头没把话说死，arrows 分数高 = 箭头都站得住；"
         "ranking 包含全部，不许并列。）\n\n"
         "# 听感记录\n\n{BEADS}\n\n# 各条线\n\n{PATHS}")
POLISH = ("下面是一张讲解视频用的“线”的关系图，共 {NSEG} 段，讲一个人在{WORK}里经历的一件事：每段几条短条目，说明他此刻为什么会这样，"
          "“←”箭头指向前面段落里真正的前因。它是一段一段分开写成的，所以放在一起读时，句式和用词可能重复、单调。\n\n"
          "任务一：只改条目的说法，让全篇读起来像一个人在自然地讲这件事——\n"
          "1. 每条的意思、它的理由和箭头关系都不能变；不加新的心理动作、新的理由、新的事件或人物前史，也不删掉任何一层因果。"
          "开头若写得还说不清，就保持说不清。\n"
          "2. 句式要有变化：不要条条以“他”开头，不要反复用“因为……”“这一次……”起句；“越……越……”全篇最多留两处。\n"
          "3. 同一个说法不要在几段里反复出现，换成那一段里更具体的说法。\n"
          "4. 少用抽象的词（依靠、安稳、掌控、约束、踏实、牵挂这一类），能换成他具体在想什么、怕什么、想要什么就换；不用这些词："
          + "、".join(BAN) + "。\n"
          "5. 每条不超过 45 字，不要比原文更长；只改有毛病的地方，没毛病的条目原样保留。\n"
          "每处改动都要记录：改了哪条、原句、新句、修的是什么毛病、有没有丢掉或多出意思（说明理由）。\n\n"
          "任务二：写出 Center——回头看整张图，把各段组织起来的那件事。格式：最小完整关系句，主语是一个或多个对象（名词短语），"
          "谓语说它们怎样相关，从较早处成立到结尾；不写人称和动作（不要“他想……却……”）；不只是两个名词；不预告发展路线和最后的结果。\n\n"
          "最后只输出一个 ```json 代码块：\n"
          '{"items": {"S01-1": "新文本", "…": "…（每一条都要有，没改的照抄）"}, "center": "…", '
          '"changes": [{"item": "S01-1", "before": "…", "after": "…", "defect": "…", "meaning_check": "…"}]}\n\n'
          "# 关系图\n\n{TEXT}")


def fill(t, work, **kw):
    t = t.replace("{WORK}", CFG[work]["name"]).replace("{SHORT}", CFG[work]["short"]).replace("{NSEG}", str(len(SECS)))
    for k, v in kw.items():
        t = t.replace("{" + k + "}", str(v))
    return t


def load(T, sec):
    p = OUT / T / f"{sec}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def save(T, sec, obj):
    p = OUT / T / f"{sec}.json"; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def ids_of(steps):
    return {f"{st['sec']}-{i + 1}": it for st in steps for i, it in enumerate(st["items"])}


def graph_text(steps, ids=True):
    """render a path as graph text; ids=True shows item ids (for the writer), False shows bars + key (for judges / the user)"""
    allit = ids_of(steps); out = []
    for st in steps:
        out.append(f"第{SECS.index(st['sec']) + 1}段（{bars_s(st['sec'])}）［{st.get('center_relation') or '?'}］")
        for i, it in enumerate(st["items"]):
            iid = f"{st['sec']}-{i + 1}"
            out.append(f"  {iid + ' ' if ids else ''}{'→ ' if it.get('follows') and i else ''}{it['text']}")
            for b in st.get("because") or []:
                if b.get("item") == i + 1 and b.get("from") in allit:
                    src = b["from"].split("-")[0]
                    out.append(f"      ← {b['rel']}：" + (b["from"] if ids else f"（{bars_s(src)}）「{allit[b['from']].get('key') or ''}」")
                               + (f"　——{b['why']}" if b.get("why") else ""))   # the writer's reason for the arrow, so judges can check it
    return "\n".join(out)


def gen_msg(work, sec, path):
    a, b = seq.bars(sec); cands = seq.pool_text(sec); first = sec == SECS[0]
    hist = [h for st in path["steps"] for h in st["history"]]
    m = seq.INTRO.replace("{A}", str(a)).replace("{B}", str(b))
    m += "\n【这条路到目前为止确立的历史】\n" + ("\n".join(f"- {h}" for h in hist) if hist else "（这是第一段，还没有历史）") + "\n"
    if path["steps"]:
        m += "【这条路前面各段的关系图（条目前是编号）】\n" + graph_text(path["steps"]) + "\n"
    m += f"\n【这一段的听感记录（另一位作者听这段音乐写下的，原文）】\n{seq.beads(sec)}\n"
    m += "\n【候选解释】\n" + "\n\n".join(f"候选{i + 1}：\n{t}" for i, (_, t) in enumerate(cands)) + "\n"
    g = GEN
    if False and TWO and not first:   # folded into GEN in round 6   # round 5 variant: judges/advisor kept saying one broad item per section leaves this section's feelings unexplained
        g = g.replace("   - items：1–3 条，", "   - items：一般写 2 条（最多 3 条）——一条说这一段最主要的感受为什么出现，另一条说段内的转变或另一种同时出现的感受为什么出现；"
                      "这一段确实只有一种感受时才只写 1 条。每条", 1)
    return m + fill(g, work, A=a, B=b, K=3 if first else 2, REST=FIRST if first else REST)


TWO = __import__("os").environ.get("BEAM_TWO") == "1"


def clean_option(o, sec, prev_ids):
    items = [{"text": (it.get("text") or "").strip(), "key": (it.get("key") or "").strip(), "follows": bool(it.get("follows"))}
             for it in (o.get("items") or []) if (it.get("text") or "").strip()][:3]
    if not items:
        return None
    items[0]["follows"] = False
    bec = [{"item": int(b.get("item") or 0), "from": str(b.get("from") or "").strip(), "rel": b.get("rel"), "why": (b.get("why") or "").strip()}
           for b in (o.get("because") or []) if isinstance(b, dict)]
    bec = [b for b in bec if 1 <= b["item"] <= len(items) and b["from"] in prev_ids and b["rel"] in RELS]
    cr = o.get("center_relation") if o.get("center_relation") in CREL else None
    return {"sec": sec, "items": items, "because": bec, "center_relation": cr,
            "line": "".join(it["text"] for it in items),
            "history": [h for h in o.get("history") or [] if h and h.strip() != "无"],
            "cred": o.get("credibility"), "cred_why": o.get("why", ""), "uses": o.get("uses") or []}


def step(T, work, sec, paths, model):
    k = SECS.index(sec) + 1; jobs = []
    for p in paths:
        rid = f"bm{T}_{sec}_{p['id'] or 'root'}"
        if not evo.done(rid):
            jobs.append(node2b.job(rid, gen_msg(work, sec, p), {"stage": "beam_gen", "sec": sec}, w=model))
    evo.run_parallel(jobs, 6)
    kids = []
    for p in paths:
        r = seq.parse(evo.output(f"bm{T}_{sec}_{p['id'] or 'root'}")) or {}
        prev = ids_of(p["steps"])
        for i, o in enumerate(r.get("options") or []):
            st = clean_option(o, sec, prev)
            if st:
                kids.append({"id": p["id"] + "abc"[i], "steps": p["steps"] + [st]})
    if len(kids) <= WIDTH:
        return kids, None
    labs = [f"路{chr(65 + i)}" for i in range(len(kids))]; order = list(range(len(kids))); random.Random(f"{T}{sec}").shuffle(order)
    m = fill(PRUNE, work, N=len(kids), K=k, W=WIDTH, LABELS="、".join(labs), BEADS=beads_upto(k),
             PATHS="\n\n".join(f"## {labs[j]}\n{graph_text(kids[i]['steps'], ids=False)}" for j, i in enumerate(order)))
    rid = f"bm{T}_{sec}_prune"
    if not evo.done(rid):
        node2b.job(rid, m, {"stage": "beam_prune", "sec": sec}, w="g56" if model == "g6" else "g6")[1]()
    r = seq.parse(evo.output(rid)) or {}
    lab2 = {labs[j]: kids[i] for j, i in enumerate(order)}
    keep = [lab2[l] for l in (r.get("keep") or []) if l in lab2][:WIDTH]
    if len(keep) < WIDTH:   # judge failed or kept too few: fill by self-rated credibility
        rest = sorted([c for c in kids if c not in keep], key=lambda c: -(c["steps"][-1]["cred"] or 0))
        keep += rest[:WIDTH - len(keep)]
    reasons = {lab2[l]["id"]: why for l, why in (r.get("reasons") or {}).items() if l in lab2}
    for c in kids:
        c["steps"][-1]["prune_why"] = reasons.get(c["id"], "")
    return keep, {"all": kids, "reasons": reasons}


def beads_upto(k):
    return "\n\n".join(f"### 第{i + 1}段　第 {bars_s(s)} 小节\n" + seq.beads(s) for i, s in enumerate(SECS[:k]))


def run(T, work, model="g6"):
    paths = [{"id": "", "steps": []}]
    for sec in SECS:
        st = load(T, sec)
        if st:
            paths = st["kept"]; continue
        paths, pr = step(T, work, sec, paths, model)
        if not paths:
            print(T, sec, "NO PATHS", flush=True); return False
        save(T, sec, {"kept": paths, "pruned": pr})
        print(T, sec, "kept", [p["id"] for p in paths], "|", " / ".join(p["steps"][-1]["line"][:30] for p in paths), flush=True)
    return True


def final(T, work):
    paths = load(T, SECS[-1])["kept"]; labs = [f"线{chr(65 + i)}" for i in range(len(paths))]; res = {}
    jobs, maps = [], {}
    for jn, w in (("gpt6", "g6"), ("gpt56", "g56")):
        order = list(range(len(paths))); random.Random(f"{T}final{jn}").shuffle(order)
        m = fill(FINAL, work, N=len(paths), LABELS="、".join(labs), BEADS=beads_upto(len(SECS)),
                 PATHS="\n\n".join(f"## {labs[j]}\n{graph_text(paths[i]['steps'], ids=False)}" for j, i in enumerate(order)))
        rid = f"bm{T}_final_{jn}"; maps[jn] = {labs[j]: paths[i]["id"] for j, i in enumerate(order)}
        if not evo.done(rid):
            jobs.append(node2b.job(rid, m, {"stage": "beam_final"}, w=w))
    evo.run_parallel(jobs, 2)
    for jn, mp in maps.items():
        r = seq.parse(evo.output(f"bm{T}_final_{jn}")) or {}
        if not r.get("paths"):   # 61e: gpt56 returned no parsable JSON -> one retry under a new id
            rid2 = f"bm{T}_final_{jn}_r2"
            if not evo.done(rid2):
                node2b.job(rid2, evo.rd(evo.RUNS / f"bm{T}_final_{jn}" / "input.txt"), {"stage": "beam_final"}, w="g6" if jn == "gpt6" else "g56")[1]()
            r = seq.parse(evo.output(rid2)) or {}
        res[jn] = {"ranking": [mp.get(x, x) for x in r.get("ranking", [])], "my_reading": r.get("my_reading"),
                   "paths": {mp.get(k, k): v for k, v in (r.get("paths") or {}).items()}}
    (OUT / T / "final.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for jn, r in res.items():
        print(T, jn, r["ranking"], {k: (v.get("overall") or {}).get("score") for k, v in r["paths"].items()}, flush=True)
    return res


def winner(res):
    """best mean overall across both judges; ties -> better mean rank"""
    ids = {k for r in res.values() for k in r["paths"]}
    def key(i):
        sc = [(r["paths"].get(i, {}).get("overall") or {}).get("score") or 0 for r in res.values()]
        rk = [r["ranking"].index(i) if i in r["ranking"] else 9 for r in res.values()]
        return (-sum(sc), sum(rk))
    return sorted(ids, key=key)[0]


def stats(texts):
    t = "".join(texts)
    return {"越越": len(re.findall(r"越.{0,14}?越", t)), "禁用词": [w for w in BAN if w in t],
            "以他开头": sum(x.startswith("他") for x in texts), "因为": t.count("因为"), "最长": max(map(len, texts)), "条目": len(texts)}


def polish(T, work):
    res = json.loads((OUT / T / "final.json").read_text(encoding="utf-8")); pid = winner(res)
    p = next(x for x in load(T, SECS[-1])["kept"] if x["id"] == pid)
    ids = ids_of(p["steps"]); before = {k: v["text"] for k, v in ids.items()}
    rid = f"bm{T}_polish"
    if not evo.done(rid):
        node2b.job(rid, fill(POLISH, work, TEXT=graph_text(p["steps"])), {"stage": "polish"}, w="g6")[1]()
    r = seq.parse(evo.output(rid)) or {}
    after = {k: ((r.get("items") or {}).get(k) or v).strip() for k, v in before.items()}
    out = {"path": pid, "center": r.get("center"), "before": before, "after": after, "changes": r.get("changes"),
           "stats_before": stats(list(before.values())), "stats_after": stats(list(after.values()))}
    (OUT / T / "polish.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(T, "winner", pid, "center:", out["center"], "\n before", out["stats_before"], "\n after ", out["stats_after"], flush=True)
    audit(T, work, p, after)
    center(T, work)
    render(T, work)


# round 4 (60g/61g): three rounds of judges and advisors kept finding arrows that link similar moods rather than causes,
# whatever the writing prompt said. So the winner's arrows get the strict audit of the old graph pipeline (tgraph4 ARROWS42:
# keep only 支持): each arrow is shown with both items and the writer's reason; only arrows judged 支持 are kept.
AUDIT = ("下面是一张关系图里的跨段箭头。每个箭头声称：前面某段的一条经历，给后面某段的一条提供理由、动摇、限制、改写或唤起，"
         "后面附有写的人给的理由。请逐个判断这个因果是否成立：\n"
         "- 支持：前面那条经历确实促成、改变或限制了后面那条的状态，理由站得住；\n"
         "- 勉强：只是情绪相似、主题相近、同一状态再次出现，或理由说不出前面那条具体改变了什么；\n"
         "- 不支持：两条之间没有这种关系。\n"
         "每个都写一句理由。最后只输出一个 ```json 代码块：\n"
         '{"arrows": [{"n": 1, "verdict": "支持|勉强|不支持", "why": "…"}]}\n\n{ARROWS}')


def audit(T, work, p, texts):
    arrows = [(st["sec"], b) for st in p["steps"] for b in st.get("because") or []]
    if not arrows:
        return
    lines = []
    for n, (sec, b) in enumerate(arrows, 1):
        src, dst = b["from"], f"{sec}-{b['item']}"
        lines.append(f"{n}. 【{bars_s(src.split('-')[0])}】{texts.get(src, '')}\n   —{b['rel']}→ 【{bars_s(sec)}】{texts.get(dst, '')}"
                     + (f"\n   写的人的理由：{b['why']}" if b.get("why") else ""))
    rid = f"bm{T}_audit"
    if not evo.done(rid):
        node2b.job(rid, AUDIT.replace("{ARROWS}", "\n".join(lines)), {"stage": "arrow_audit"}, w="g56")[1]()
    r = seq.parse(evo.output(rid)) or {}
    v = {a.get("n"): a for a in r.get("arrows") or []}
    res = [{"sec": sec, "from": b["from"], "item": b["item"], "verdict": (v.get(n) or {}).get("verdict"), "why": (v.get(n) or {}).get("why")}
           for n, (sec, b) in enumerate(arrows, 1)]
    (OUT / T / "audit.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(T, "arrow audit:", {k: sum(x["verdict"] == k for x in res) for k in ("支持", "勉强", "不支持", None)}, flush=True)


# Center as its own step (user 10-23 on v8: "这个 center 怎么感觉选的很怪 前面那几个感觉重叠很多而且不太说人话"). It had been
# written inside the wording-polish call ("回头看整张图"), so it listed one noun per stage (未明的期待、亲近中的欲望与深切喜欢……)
# joined by "交织" — a table of contents, not the one matter. Now: 3 candidates under P0's definition, then another model picks.
CENTER = ("下面是一张讲解视频用的“线”的关系图，讲一个人在{WORK}里经历的一件事。请回头看整张图，写出把各段组织起来的那件事（Center）。\n"
          "Center 是什么（原始要求）：说清楚共同的困扰——什么对这个人重要，又是什么使它难以安顿。它不预告发展的路线和最后的回答。\n"
          "写法：\n"
          "1. 一句话。主语是一个或最多两个对象（名词短语），谓语说出它们怎样相关；这个关系要从较早的段落就成立，一直到结尾。\n"
          "2. 两个对象要真的是两样东西，不能是同一种感情的不同程度或不同阶段；不要按段落顺序把各段的感受列成一串。\n"
          "3. 谓语要具体（例如谁妨碍谁、谁让谁变得更难），不要用“交织”“相连”“影响”“牵动”这类说了等于没说的词。\n"
          "4. 不写人称和动作（不要“他想……却……”）；不只是两个名词；不预告结局；普通人一遍能懂，不用抽象的姿态词。\n"
          "写 3 个真正不同的候选，每个说明它怎样把开头、中段和结尾组织起来。\n"
          "最后只输出一个 ```json 代码块：\n"
          '{"candidates": [{"center": "…", "how": "…"}]}\n\n# 关系图\n\n{GRAPH}')
CPICK = ("下面是一张讲解视频用的“线”的关系图，和 {N} 个候选的 Center（把各段组织起来的那件事）。Center 要求：说清楚什么对这个人重要、"
         "又是什么使它难以安顿；一句话，最多两个真正不同的对象，谓语具体（不用“交织”“相连”“影响”这类空词）；不按阶段罗列；不预告结局；"
         "普通人一遍能懂。\n"
         "请逐个评：它能不能把开头、中段、结尾都组织起来（举出段落）；有没有罗列、重叠、空词、预告结局；是不是人话。每项写理由，然后选一个。\n"
         "最后只输出一个 ```json 代码块：\n"
         '{"reviews": [{"n": 1, "why": "…"}], "pick": 1}\n\n# 关系图\n\n{GRAPH}\n\n# 候选\n\n{CANDS}')


def center(T, work):
    pol = json.loads((OUT / T / "polish.json").read_text(encoding="utf-8"))
    p = next(x for x in load(T, SECS[-1])["kept"] if x["id"] == pol["path"])
    steps = [dict(st, items=[dict(it, text=re.sub(r"^[→\s]+", "", pol["after"].get(f"{st['sec']}-{i + 1}", it["text"])))
                             for i, it in enumerate(st["items"])]) for st in p["steps"]]
    gt = graph_text(steps, ids=False)
    rid = f"bm{T}_center"
    if not evo.done(rid):
        node2b.job(rid, fill(CENTER, work, GRAPH=gt), {"stage": "center"}, w="g6")[1]()
    cands = (seq.parse(evo.output(rid)) or {}).get("candidates") or []
    if not cands:
        print(T, "center: no candidates", flush=True); return
    rid2 = f"bm{T}_cpick"
    if not evo.done(rid2):
        ct = "\n".join(f"{i + 1}. {c.get('center')}\n   （作者说明：{c.get('how', '')}）" for i, c in enumerate(cands))
        node2b.job(rid2, fill(CPICK, work, N=len(cands), GRAPH=gt, CANDS=ct), {"stage": "center_pick"}, w="g56")[1]()
    r = seq.parse(evo.output(rid2)) or {}
    k = r.get("pick") if isinstance(r.get("pick"), int) and 1 <= r.get("pick") <= len(cands) else 1
    out = {"center": cands[k - 1].get("center"), "candidates": cands, "reviews": r.get("reviews"), "pick": k, "old": pol.get("center")}
    (OUT / T / "center.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(T, "center:", out["center"], flush=True)


def kept_arrow(T, sec, b):
    p = OUT / T / "audit.json"
    if not p.exists():
        return True
    for a in json.loads(p.read_text(encoding="utf-8")):
        if a["sec"] == sec and a["from"] == b["from"] and a["item"] == b["item"]:
            return a["verdict"] in ("支持", None)
    return True


def render(T, work):
    """final graph: JSON (segments/items/because, same shape as v6) + md rendered like the v6 relation graph"""
    pol = json.loads((OUT / T / "polish.json").read_text(encoding="utf-8"))
    p = next(x for x in load(T, SECS[-1])["kept"] if x["id"] == pol["path"])
    allit = ids_of(p["steps"]); segs = []
    cj = OUT / T / "center.json"   # the separate Center step wins over the one written inside polish
    cen = json.loads(cj.read_text(encoding="utf-8"))["center"] if cj.exists() else pol.get("center")
    md = [f"# {CFG[work]['Op']}｜关系图（逐段综合 {T}）\n", f"**Center：**{cen or '（未生成）'}\n"]
    for st in p["steps"]:
        items = [{"id": f"{st['sec']}-{i + 1}", "text": re.sub(r"^[→\s]+", "", pol["after"].get(f"{st['sec']}-{i + 1}", it["text"])), "key": it.get("key"),
                  "follows": it.get("follows")} for i, it in enumerate(st["items"])]
        segs.append({"bars": bars_s(st["sec"]), "relation": st.get("center_relation"), "items": items,
                     "because": [{"from": b["from"], "to": f"{st['sec']}-{b['item']}", "rel": b["rel"], "why": b.get("why", "")} for b in st.get("because") or [] if kept_arrow(T, st["sec"], b)]})
        md.append(f"### {bars_s(st['sec'])}　（{st.get('center_relation') or '?'}）\n")
        for i, it in enumerate(items):
            md.append(f"- {'→ ' if it['follows'] and i else ''}{it['text']}")
            for b in [x for x in st.get("because") or [] if kept_arrow(T, st["sec"], x)]:
                if b["item"] == i + 1 and b["from"] in allit:
                    md.append(f"  - ← {b['rel']}：（{bars_s(b['from'].split('-')[0])}）「{allit[b['from']].get('key') or ''}」")
        md.append("")
    (OUT / T / "graph.json").write_text(json.dumps({"center": cen, "segments": segs, "path": pol["path"]},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / T / "graph.md").write_text("\n".join(md), encoding="utf-8")
    print(OUT / T / "graph.md", flush=True)


if __name__ == "__main__":
    ph, T, work = sys.argv[1], sys.argv[2], sys.argv[3]
    setup(work)
    if ph in ("run", "all") and not run(T, work):
        sys.exit(1)
    if ph in ("final", "all"):
        final(T, work)
    if ph in ("polish", "all"):
        polish(T, work)
    if ph == "render":
        render(T, work)
    if ph == "center":
        center(T, work); render(T, work)
    if ph == "audit":   # retro-fit the arrow audit to an already polished round, then re-render
        pol = json.loads((OUT / T / "polish.json").read_text(encoding="utf-8"))
        audit(T, work, next(x for x in load(T, SECS[-1])["kept"] if x["id"] == pol["path"]), pol["after"])
        render(T, work)
    if ph == "msg":
        print(gen_msg(work, sys.argv[4], {"id": "", "steps": []}))
