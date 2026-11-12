"""Sectional synthesis pilot (user 10-23, PLAN_逐段构建线_20261023.md step 1). Instead of picking one whole draft, the line is
built section by section: established history so far + every pool draft's text for this section -> the model judges each
candidate, writes this section's explanation (pick / merge compatible ones / write new), and updates the history. A second
short call only says the explanation in plain words. Drafts never saw beads; condition C shows this section's beads at
the synthesis step only (verbatim, all roles), B does not.
Pool (user 10-23): drafts from the current N8 prompt + the corrected D9 prompts; c6_syn (a whole-piece synthesis) excluded.
ids: sq<B|C>_<m>_r<j>_S0k (judge+explain), sqp<B|C>_<m>_r<j>_S0k (plain).  usage: python seq.py run [S..]; python seq.py show"""
import json, re, sys
import evo, node2b, segcheck, arts

W = "op60"
SECTIONS = ["S01", "S02", "S03", "S04"]
POOL = [f"n8_op60_r{j}" for j in (1, 2, 3)] + [f"n8_op60_c6_r{j}" for j in (1, 2, 3, 4)] + \
       [f"d9L_op60_r{j}" for j in (1, 2, 3)] + [f"d9S_op60_r{j}" for j in (1, 2, 3)]
STRUCT = evo.ROOT / "inputs" / "pkg" / "03_Bead机器可读"
OUT = evo.ROOT / "evaluations" / "seq"
V = __import__("os").environ.get("SEQV", "1")   # "2": revised prompts (pilot v1 review, see TASK2), ids sq2*/sqp2*
P = {"1": "sq", "2": "sq2", "3": "sq3", "4": "sq4"}[V]
ROLE = {"主体验": "主体验", "段内变化": "段内变化", "另一侧面": "侧面", "另一种理解": "另一种听法（和本段某一颗不能同时成立）"}

INTRO = ("我们在为肖邦《船歌》Op.60 做一部随音乐播放的讲解视频。其中“线”讲一个人在这首曲子里经历的一件事："
         "每一段说明他此刻为什么会有这样的感受，理由来自他前面已经经历过的事，而不是“音乐忽然怎样了”。\n"
         "这条线正在从头到尾一段一段地确定。下面给你到目前为止确立的历史（第一段时还没有），"
         "以及几位作者各自为第 {A}–{B} 小节写的解释。他们各自写了整首，前文和这里确立的历史不一定一样。\n")
TASK = ("\n请只处理第 {A}–{B} 小节这一段：\n"
        "1. 逐个看候选：它这一段的解释哪里成立、哪里牵强？能不能接上已经确立的历史？有没有编出不必要的心理动作"
        "（劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心）？{BEADQ}\n"
        "2. 写出这一段的解释：可以采用一个候选、合并几个确实相容的候选，也可以写新的。一个理由能说清，就不要拆成几步；"
        "这一段可以没有新的变化，只是前面感受的延续、加深或再次出现。不编外部事件、物件、对白。{BEADW}\n"
        "3. 更新历史：到这一段为止，确立了什么、以后仍会起作用（几条短句；没有新的就写“无”）。前面已有的历史不用重抄。\n"
        "最后只输出一个 ```json 代码块：\n"
        '{"assessments": [{"cand": "候选1", "holds": "成立之处", "weak": "牵强之处"}], "chosen": ["候选2"], '
        '"explanation": "这一段的解释", "why": "为什么这样选", "history": ["新确立的一条"]}\n')
BEADQ = "它能不能说明下面这些听感为什么此刻会出现？"
BEADW = "解释要说明这些听感为什么此刻出现，但不要把听感再写一遍（听感另有记录直接给观众看）。"
# v2 (pilot v1 review 10-23): v1 texts were static and repeated the whole situation every section; the anti-move list
# leaked into the text ("不需要劝说、想通或下定决心"), every section carried "不是……也不是……" disclaimers; S01 refused any
# starting point, so B chains had nothing to grow from; C chains turned one bead's simile (a long-held confession) into
# the plot of all four sections. Writing rules now: only what is new here; say what he is and why, never what he is not
# doing; a first section may set a starting point; bead images are a listener's similes, not events in his life.
TASK2 = ("\n请只处理第 {A}–{B} 小节这一段：\n"
         "1. 逐个看候选：它这一段的解释哪里成立、哪里牵强？能不能接上已经确立的历史？有没有编出不必要的心理动作"
         "（劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心）？{BEADQ}\n"
         "2. 写出这一段的解释：可以采用一个候选、合并几个确实相容的候选，也可以写新的。写法：\n"
         "   - 只写这一段新出现的、或比前面更强／更弱的东西，以及它为什么此刻出现；已经在历史里的不要再讲一遍。"
         "如果这一段只是前面感受的延续或再次出现，用一两句说清是什么在延续、为什么此刻不同。\n"
         "   - 只写他此刻怎样、为什么；不写他没有做什么、不需要什么，也不要评论这段解释本身。\n"
         "   - 第一段没有前史：可以确立一个起点（他在意什么、为什么会被牵动），但不要编具体的往事。\n"
         "   - 不编外部事件、物件、对白。{BEADW}\n"
         "3. 更新历史：到这一段为止，确立了什么、以后仍会起作用（几条短句；没有新的就写“无”）。前面已有的历史不用重抄。\n"
         "最后只输出一个 ```json 代码块：\n"
         '{"assessments": [{"cand": "候选1", "holds": "成立之处", "weak": "牵强之处"}], "chosen": ["候选2"], '
         '"explanation": "这一段的解释", "why": "为什么这样选", "history": ["新确立的一条"]}\n')
# v3 (user 10-23 "好啰嗦", pointing at ChatGPT's own examples, e.g. 24–34: 熟悉的亲近再次出现，他便比第一次更加投入。正因为已经
# 知道它有多珍贵，才更想把话说够、把这一刻留久一点。): v2 lines ran 150–300 chars because they tried to answer every bead,
# restated the situation and closed with hedges ("……同时存在""还没有定论"); the separate plain call lengthened them further,
# and bead contours (surges, then easing) came back as his mood swinging. Now: one main feeling, one reason pointing to an
# earlier section, two or three sentences (<= 80 chars), written directly as the line; no separate plain call.
TASK3 = ("\n请只处理第 {A}–{B} 小节这一段：\n"
         "1. 逐个看候选：它这一段的解释哪里成立、哪里牵强？能不能接上已经确立的历史？有没有编出不必要的心理动作"
         "（劝自己、提醒自己、想通、找到办法、发现办法不管用、下决心）？能不能说明这一段最主要的听感为什么此刻出现？\n"
         "2. 写出这一段的线（line）：\n"
         "   - 两三句，不超过 80 个字，普通人一遍能听懂的话。\n"
         "   - 只抓这一段最主要的那种感受，说清它为什么此刻出现；理由只给一个，并说清它来自前面哪一段的经历"
         "（可以直接说“刚才”“第一次”“那时”）。不必逐颗解释听感。\n"
         "   - 这一段若只是前面的延续或再次出现，就说清这一次为什么不一样。\n"
         "   - 只写他此刻怎样、为什么；不写他没有做什么，不用“同时存在”“还没有定论”这类收尾，不评论解释本身。\n"
         "   - 听感里音乐的起伏（涌上来、退下去）不用写成他心情的起伏；听感里的画面和比喻是听者对音乐的形容，不是他身上发生的事。\n"
         "   - 第一段没有前史：可以确立一个起点（他在意什么、为什么会被牵动），但不要编具体的往事。不编外部事件、物件、对白。\n"
         "3. 更新历史：到这一段为止，确立了什么、以后仍会起作用（一两条短句；没有新的就写“无”）。\n"
         "最后只输出一个 ```json 代码块：\n"
         '{"assessments": [{"cand": "候选1", "holds": "成立之处", "weak": "牵强之处"}], "chosen": ["候选2"], '
         '"line": "这一段的线", "why": "为什么这样写", "history": ["新确立的一条"]}\n')
# v4 (v3 review 10-23): v3 lines were short (34–62 chars) but every one opened with "刚才……" (my own hint) and spent half
# its length re-telling the previous section; several lifted the beads' own words (陶醉、走神、悬着); the reason was often
# just "he sank deeper", adding nothing the beads did not say. Now: no fixed opener, earlier sections named in a few
# words only, no wording taken from the beads, and the reason must be something the beads do not already say.
TASK4 = (TASK3.replace("（可以直接说“刚才”“第一次”“那时”）", "（前面的经历只用几个字点到，不要复述前一段）")
         .replace("   - 这一段若只是前面的延续或再次出现，就说清这一次为什么不一样。\n",
                  "   - 这一段若只是前面的延续或再次出现，就说清这一次为什么不一样。\n"
                  "   - 理由要是听感里没有的东西：他前面经历过什么、因此此刻在意什么。不要借用听感里的词句（例如听感说“走神”，线就不要再说“走神”）。\n"
                  "   - 各段的开头和句式不要雷同。\n"))
assert TASK4 != TASK3 and "听感里没有的东西" in TASK4
BEADW2 = ("解释要说明这些听感（例如更急、更舍不得、忽然空了）为什么此刻出现，但不要把听感再写一遍。"
          "听感记录里的画面和比喻（说话、握手、船、烟花……）是听者对音乐的形容，不是这个人身上真的发生的事，不要把它们写成情节。")
PLAIN = ("下面是讲解视频里一段旁白的意思。请用普通人一遍就能听懂的话说出来：不改意思，不加也不减，几句话就够。只输出这段话。\n\n{X}")


LHEAD = re.compile(r"^感受：\s*[（(〔\[]\s*第?\s*(\d+)\s*[—–\-~至到]+\s*(\d+)\s*小节\s*[）)〕\]]", re.M)


def split_listen(t):
    """d9L drafts head each segment with '感受：（第a–b小节）…' instead of a heading line."""
    ms = list(LHEAD.finditer(t))
    return {int(m.group(1)): t[m.start():ms[i + 1].start() if i + 1 < len(ms) else len(t)].strip() for i, m in enumerate(ms)}


def pool_text(sec):
    out = []; a, _ = bars(sec)
    for n in POOL:
        t = evo.output(n)
        if not t:
            continue
        j = segcheck.to_json(arts.clean(t), W)
        s = next((x["text"] for x in (j or {}).get("segments", []) if x["id"] == sec), None)
        if s is None and n.startswith("d9L"):
            s = split_listen(arts.clean(t)).get(a)
        if s is None:   # some d9S drafts drop the headings but keep exactly one paragraph per segment
            ps = [p.strip() for p in arts.clean(t).split("\n\n") if p.strip()]
            if len(ps) == len(segcheck.seg.load(W)["segments"]):
                s = ps[int(sec[1:]) - 1]
        if s:
            out.append((n, s.strip()))
        else:
            print("pool: no", sec, "in", n, flush=True)
    return out


def beads(sec):
    d = json.loads((STRUCT / f"{sec}.json").read_text(encoding="utf-8"))
    return "\n".join(f"- 【{ROLE.get(b['role'], b['role'])}】（{b['measures'].split('（')[0]}）{b['text']}" for b in d["beads"])


def bars(sec):
    d = json.loads((STRUCT / f"{sec}.json").read_text(encoding="utf-8"))
    return d["mm_start"], d["mm_end"]


def parse(t):
    m = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", t or "", re.S)
    try:
        return json.loads(m[-1]) if m else None
    except json.JSONDecodeError:
        return None


def message(cond, sec, history):
    a, b = bars(sec); cands = pool_text(sec)
    m = INTRO.replace("{A}", str(a)).replace("{B}", str(b))
    m += "\n【到目前为止确立的历史】\n" + ("\n".join(f"- {h}" for h in history) if history else "（这是第一段，还没有历史）") + "\n"
    if cond == "C":
        m += f"\n【这一段的听感记录（另一位作者听这段音乐写下的，原文）】\n{beads(sec)}\n"
    m += "\n【候选解释】\n" + "\n\n".join(f"候选{i + 1}：\n{t}" for i, (_, t) in enumerate(cands)) + "\n"
    m += {"1": TASK, "2": TASK2, "3": TASK3, "4": TASK4}[V].replace("{A}", str(a)).replace("{B}", str(b)).replace("{BEADQ}", BEADQ if cond == "C" else "") \
        .replace("{BEADW}", (BEADW if V == "1" else BEADW2) if cond == "C" else "")
    return m, [n for n, _ in cands]


def chain(cond, mdl, j, secs):
    history = []
    for sec in secs:
        rid = f"{P}{cond}_{mdl}_r{j}_{sec}"
        msg, names = message(cond, sec, history)
        if not evo.done(rid):
            node2b.job(rid, msg, {"stage": "seq", "cond": cond, "sec": sec, "pool": names}, w=mdl)[1]()
        r = parse(evo.output(rid))
        if not r:
            print(rid, "PARSE FAIL", flush=True); return
        r["pool"] = names
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{rid}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        pid = f"{P}p{cond}_{mdl}_r{j}_{sec}"
        if V in ("3", "4"):
            r["explanation"] = r.get("line", "")
        elif not evo.done(pid):
            node2b.job(pid, PLAIN.replace("{X}", r.get("explanation", "")), {"stage": "seq_plain", "sec": sec}, w=mdl)[1]()
        history += [h for h in r.get("history") or [] if h and h.strip() != "无"]
        print(rid, "ok; chosen", [names[int(c.replace("候选", "")) - 1] if re.fullmatch(r"候选\d+", c) else c
                                   for c in r.get("chosen") or []], flush=True)


CHAINS = [f"{c}_{m}_r{j}" for c in "BC" for m in ("g6", "g56") for j in (1, 2)]
LABEL = {"B": "不看珠子", "C": "看珠子"}


def chain_texts(ch):
    """plain text per section for one chain (None if a section is missing)"""
    if V in ("3", "4"):
        return {s: (json.loads((OUT / f"{P}{ch}_{s}.json").read_text(encoding="utf-8")).get("line") or None)
                if (OUT / f"{P}{ch}_{s}.json").exists() else None for s in SECTIONS}
    return {s: clean(evo.output(f"{P}p{ch}_{s}")) or None for s in SECTIONS}


def clean(t):
    return re.sub(r"</?WritingBlock[^>]*>", "", t or "").strip()


def base_texts():
    j = segcheck.to_json(arts.clean(evo.output("n8_op60_r1")), W)
    return {x["id"]: x["text"].strip() for x in j["segments"] if x["id"] in SECTIONS}


def show():
    B = base_texts(); md = ["# 逐段构建线：Op.60 第 1–39 小节试点\n",
                           "每段先列珠子（原文），再列各版本的线。**A** = 现行 N8 原稿（v6 关系图的来源）；"
                           "**B** = 逐段综合、不看珠子；**C** = 逐段综合、看珠子。B/C 显示的是“说成人话”后的版本，"
                           "下面小字是综合时写的解释、采用了哪些候选和新确立的历史。候选池：N8 稿 7 篇 + 修正稿 6 篇（d9L 边听边写、d9S 只改规则）。\n"]
    for s in SECTIONS:
        a, b = bars(s)
        md.append(f"\n---\n\n## {s}　第 {a}–{b} 小节\n\n**珠子**\n\n{beads(s)}\n\n### A · 现行 N8 原稿\n\n{B[s]}\n")
        for ch in CHAINS:
            p = OUT / f"{P}{ch}_{s}.json"
            if not p.exists():
                continue
            r = json.loads(p.read_text(encoding="utf-8")); names = r.get("pool") or []
            chosen = [names[int(c[2:]) - 1] if re.fullmatch(r"候选\d+", c) and int(c[2:]) <= len(names) else c for c in r.get("chosen") or []]
            md.append(f"\n### {ch[0]} · {LABEL[ch[0]]} · {ch[2:]}\n\n{clean(evo.output(f'{P}p{ch}_{s}')) or '（人话版缺）'}\n\n"
                      f"> 综合时的解释：{r.get('explanation', '')}\n>\n> 采用：{'、'.join(chosen)}｜理由：{r.get('why', '')}\n>\n"
                      f"> 新确立的历史：{'；'.join(r.get('history') or [])}\n")
    (OUT / f"seq_view_v{V}.md").write_text("\n".join(md), encoding="utf-8")
    print(OUT / f"seq_view_v{V}.md")


def judge(eid, groups, judges=("gpt6", "gpt56")):
    """groups: list of chain lists; each judge call sees A + the chains of one group (shuffled, anonymous)"""
    import random
    tmpl = evo.rd(evo.ROOT / "prompts" / "judge_seq_v1.md")
    allbeads = "\n\n".join(f"### {s}　第 {bars(s)[0]}–{bars(s)[1]} 小节\n" + "\n".join(
        f"- {b['id']}【{ROLE.get(b['role'], b['role'])}】{b['text']}" for b in json.loads((STRUCT / f'{s}.json').read_text(encoding='utf-8'))['beads'])
        for s in SECTIONS)
    jobs = []; plan = {}
    for gi, grp in enumerate(groups):
        vers = {"A": base_texts(), **{ch: chain_texts(ch) for ch in grp}}
        vers = {k: v for k, v in vers.items() if all(v.values())}
        for jn in judges:
            keys = list(vers); random.Random(f"{eid}{gi}{jn}").shuffle(keys)
            labels = [f"线{chr(65 + i)}" for i in range(len(keys))]
            body = "\n\n".join(f"## {lab}\n\n" + "\n\n".join(f"**{s}**\n{vers[k][s]}" for s in SECTIONS) for lab, k in zip(labels, keys))
            m = (tmpl.replace("{N}", str(len(keys))).replace("{LABELS}", "、".join(labels))
                 + "\n\n# 听感记录\n\n" + allbeads + "\n\n# 各份线\n\n" + body)
            rid = f"{eid}_g{gi}_{jn}"; plan[rid] = dict(zip(labels, keys))
            jobs.append(node2b.job(rid, m, {"stage": "seq_judge"}, w="g6" if jn == "gpt6" else "g56"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{eid}_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    evo.run_parallel([j for j in jobs if not evo.done(j[0])], 4)
    res = {}
    for rid, mp in plan.items():
        r = parse(evo.output(rid))
        if r:
            res[rid] = {"ranking": [mp.get(x, x) for x in r.get("ranking", [])],
                        "versions": {mp.get(k, k): v for k, v in (r.get("versions") or {}).items()}}
    (OUT / f"{eid}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for rid, r in res.items():
        print(rid, r["ranking"], {k: v.get("overall") for k, v in r["versions"].items()}, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show()
    elif sys.argv[1] == "judge":
        judge(sys.argv[2], [[c for c in CHAINS if c.endswith("r1")], [c for c in CHAINS if c.endswith("r2")]])
    elif sys.argv[1] == "run":
        secs = sys.argv[2:] or SECTIONS
        evo.run_parallel([(f"{c}_{m}_{j}", (lambda c=c, m=m, j=j: chain(c, m, j, secs)))
                          for c in ("C" if V in ("3", "4") else "BC") for m in ("g6", "g56") for j in (1, 2)], 8)
    elif sys.argv[1] == "msg":
        print(message(sys.argv[2], sys.argv[3], [])[0])
