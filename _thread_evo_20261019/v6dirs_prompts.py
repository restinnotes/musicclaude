"""10-29 prompts for the parallel directions (user: "我们几个方向不是可以并发的吗"). Owned by Claude (experiment semantics);
the runner v6dirs.py only fills the placeholders. Shared rule text is taken from v6fix.FIX so A1/A2/B1 differ only in what
they are given and how much they handle per call.
  A2 (WHOLE)  : DAG 1 control — repair v6 in ONE call per piece (v6 + all beads + all diagnoses), same rules as A1.
  B1 (RAD*)   : DAG 2-2B — no v6 at all; segment by segment from the prompt + the line written so far + this segment's beads,
                written directly in the v6 graph form; Center and each segment's relation written afterwards from the line."""
import v6fix

_F = v6fix.FIX
RULES = _F[_F.index("要求：\n"):_F.index("\n\n【Center】")]          # the A1 requirement block, verbatim
THREE = _F[_F.index("这次修补只解决三个问题："):_F.index("\n\n要求：\n")]   # the three problems + keep-v6 paragraph, verbatim

# ---------- A2: whole-piece repair ----------
WHOLE = ("下面是肖邦{NAME}的一条 Thread（关系图，叫 v6），以及另一批人听这首曲子每一段写下的听感记录（珠子）。请在 v6 的基础上把整首修补一遍。\n\n"
         "{WHAT}\n\n" + THREE + "\n\n" +
         RULES.replace("from 只能写【前面已经修好的段】里的条目编号", "from 只能写修补后前面段落里的条目编号（编号写成 S03-1 这样）") +
         "\n\n【Center】{CENTER}\n\n【v6】\n{V6}\n\n【珠子】\n{BEADS}\n\n【两位评审对 v6 的逐段诊断】\n{DIAG}\n\n"
         "只输出 json：\n```json\n"
         '{{"segments": [{{"sec": "S01", "relation": "还说不清",\n'
         '   "items": [{{"id": "S01-1", "text": "……", "key": "……", "follows": false, "explains": ["B1"]}}],\n'
         '   "because": [], "gaps": []}},\n'
         '  {{"sec": "S02", "relation": "没在想", "items": [{{"id": "S02-1", "text": "……", "key": "……", "follows": false, "explains": ["B2"]}}],\n'
         '   "because": [{{"from": "S01-1", "to": "S02-1", "rel": "提供理由"}}], "gaps": [{{"bead": "B4", "why": "……"}}]}}],\n'
         ' "changes": [{{"v6": ["R12", "R13"], "now": ["S04-1"], "what": "合并", "why": "……"}}]}}\n```')
assert "{V6}" in WHOLE and "修补后前面段落里的条目编号" in WHOLE

# A2 revision: one call for the whole piece with every segment's checker notes (same CHK as A1, run per segment)
WHOLE_REV = ("\n\n【上一次的修补被核对者退回的地方】（按段列出）\n{NOTES}\n\n上一次的修补结果：\n{PREV}\n\n"
             "请据此重写：只改被指出的问题，没被指出的段和条目照旧；格式和要求同上，仍然输出整首。")

# ---------- B1: radical, segment by segment, no v6 ----------
WHAT_RAD = ("Thread 是什么：一个人在这首曲子里经历的一件事。每一段要让人看见他此刻为什么会这样，理由来自他前面真实经历过、相信过、发现过的东西，"
            "而不是音乐忽然发生了什么。珠子是另一批人听这段音乐写下的听感，写的是此刻听到、感到的具体样子，会和线并排展示；"
            "线不用把珠子再描写一遍，而是给这些感受一个“为什么偏偏此刻会这样”的理由。\n"
            "关系图的写法：每段几条短句；条目前的 → 表示由上一条引出；← 是跨段箭头，指回前面某段的某一条（提供理由、说明、限制、动摇、唤起、改写、失效）；"
            "⟲ 是前面仍在起作用的东西。")
_r = RULES
_r = _r.replace("- 形式同 v6：relation 是这一段他和 Center 的关系（还说不清 / 正在面对 / 没在想），一般沿用 v6；", "- 形式：")
_r = _r.replace("条数跟这一段真正发生了多少相称，没多少事就写一两条；修补后的条数一般不多于 v6 这一段，除非 v6 确实漏掉了这一段的主体验。",
                "条数跟这一段真正发生了多少相称，没多少事就写一两条。")
_r = _r.replace("from 只能写【前面已经修好的段】里的条目编号", "from 只能写【前面已经写好的段】里的条目编号")
_r = _r.replace("可以补一座接在前面已确立内容上的局部心理过程", "可以写接在前面已确立内容上的局部心理过程")
_r = _r.replace("也不写对修改的说明。", "也不写对写法的说明。")
_r = _r.replace("Center 不改。", "")
assert "v6" not in _r and "Center" not in _r and "修补" not in _r.replace("硬补", ""), _r
RAD_RULES = _r + ("\n- 递进：此刻的原因要从前面某段已经确立的东西推出，在 because 里连出来（第一段没有前面的段）。"
                  "开头允许还说不清：第一段可以只写一两条，不交代过去、性格、习惯，不提前说出主题。不要预告后面的段。")
RAD = ("下面是肖邦{NAME}。我们一段一段写出这首曲子的 Thread（关系图）：前面的段已经写好，现在写 {SEC}（第 {A}–{B} 小节）。"
       "写完这一段还会接着写后面的段。\n\n{WHAT}\n\n"
       "这一段要解决好三件事：\n1. 覆盖：这一段珠子里的感受（主体验、段内变化，以及和它们同时成立的另一侧面），线要给出他此刻为什么会这样。\n"
       "2. 不啰嗦：不把一个意思拆成几条，不翻来覆去说同一件事，没有没必要的心理环节和不成立的因果。\n"
       "3. 说人话：不抽象、不像哲理总结、不写工整对照、不由作者替他宣布领悟、不只说他没做什么。\n\n" + RAD_RULES +
       "\n\n【全曲分段】（只是让你知道这一段在整首里的位置）\n{SEGS}\n\n【前面已经写好的段】（跨段箭头用这里的编号）\n{DONE}\n\n【这一段的珠子】\n{BEADS}\n\n"
       "只输出 json：\n```json\n"
       '{{"items": [{{"id": "{SEC}-1", "text": "……", "key": "……", "follows": false, "explains": ["B1"]}}],\n'
       ' "because": [{{"from": "S02-3", "to": "{SEC}-1", "rel": "提供理由"}}],\n'
       ' "gaps": [{{"bead": "B4", "why": "……"}}]}}\n```')

# B1 check: v6fix.CHK without the v6 comparison (item 4) and with this direction's own progression question
_c = v6fix.CHK
_c = _c.replace("下面是一条 Thread（关系图）在某一段的修补结果。", "下面是一条 Thread（关系图）在某一段新写的内容。")
_c = _c.replace("4. 和 v6 这一段比：v6 这一段里已经说清的实质内容（具体心理事实、前后关系），修补后有没有丢掉、又没有被更好的说法取代？列出丢掉的，没有就留空。"
                "删掉的重复、空话，以及和珠子对不上而被改掉的解释，都不算丢。\n",
                "4. 递进：这一段此刻的原因，是不是接在前面某段已经确立的东西上，而不只是重复全曲一直成立的背景理由？第一段直接判“是”。一句理由。\n")
_c = _c.replace("修补后", "这一段")
_c = _c.replace("【这一段 v6 原来的样子】\n{CUR}\n\n", "")
_c = _c.replace("【这一段这一段】", "【这一段新写的】").replace("【前面已经修好的段】", "【前面已经写好的段】")
_c = _c.replace('"lost": [{{"v6": ["R12"], "what": "……"}}]', '"progress": "是", "progress_why": "……"')
assert "v6" not in _c and "{CUR}" not in _c and "4. 递进" in _c and "修好" not in _c, _c
RAD_CHK = _c
RAD_REV = v6fix.REV.replace("上一次的修补被核对者退回", "上一次写的被核对者退回").replace("上一次的修补结果", "上一次写的结果")

# B1 Center + relations, after the whole line is written
RAD_CENTER = ("下面是肖邦{NAME}一条 Thread（关系图）的全部段落。请为它写 Center，并给每段标出他和 Center 的关系。\n\n"
              "Center：写成一句最小完整的关系句——主语是一个或几个对象（名词短语），谓语说它们怎样相关，从较早处就成立、一直到结尾；"
              "不写人称和动作（“他想……却……”算多余），不只是两个名词，不预告结局，不概括各段经过，不加线里没有的东西，用普通人的话。\n"
              "每段的关系取 还说不清 / 正在面对 / 没在想 之一：每段都在 Center 的范围里，但不必显性面对它；开头允许还说不清；"
              "没在想的段也属于同一件事。不设比例。\n\n{LINE}\n\n"
              "只输出 json：\n```json\n"
              '{{"center": "……", "why": "一句理由", "relations": {{"S01": "还说不清", "S02": "没在想"}}}}\n```')

# A2 refine (10-29, after the first blind check): v6 vs w2 — new better on P1/P2/P3 in most segments, but all four judges called it a
# substantive regression; what was lost was mostly what he came to understand (the RULES now say to keep it in plain words).
WHOLE_REFINE = ("\n\n【上一轮的修补结果】\n{PREV}\n\n"
                "【匿名盲评对上一轮的意见】两位评委把上一轮和 v6 匿名比较：上一轮在覆盖、啰嗦、人话上大多好于 v6，但丢了 v6 已经说清的下面这些内容（按段列出）：\n{NOTES}\n\n"
                "请在上一轮的基础上把整首再修一遍：把被指出丢掉的内容找回来。它们大多是他想明白的东西——保留这个认识，用他自己的平常话说出来，"
                "并让人看出是前面哪段经历让他想到的，不要恢复成 v6 的总结句、对照句；评委列的内容里，如果有前文没有经历撑着、把无奈写成高尚坚定选择的，"
                "可以不找回，在 changes 里说明。找回时，一条认识用一句平常话说清，能并进已有条目就并进去，不要恢复 v6 的整串步骤；并让人看出它为什么此刻成立——是前面哪段经历引出的，就用 ← 指回那一条。上一轮已经改好的地方（覆盖、精简、人话）不要退回去，条数也不要因此涨回 v6 的样子。格式和要求同上，仍然输出整首。")
