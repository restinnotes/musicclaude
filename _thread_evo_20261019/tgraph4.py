"""Thread graph v4 (user 10-21): v3 merged each segment into one long passage ("现在又像是散文了 ... 五合一如果做不好还不如不合并").
v2 split by type (所求/恐惧/理由/办法/状态) and repeated itself. v4: each segment = a few SHORT items, one thing each (<= ~35 chars);
merge only when the merged sentence is still short and natural; no summary items; recaps of earlier segments become arrows.
  center  : accepted sentence, verbatim
  segments: {bars, relation: 正在面对|还说不清|没在想, items:[{id, text, key, kind?}], because:[{from: earlier item, to: item here, rel, how?}], outer?}
Coverage: same step inventory as v3 (stepcheck.INV of the line), checked by GPT-5.6 (stepcheck.CHK).
ids: tg4_<line>_r<j> -> evaluations/tgraph4/
usage: python tgraph4.py build <line...> | final <graph id...> | cov <graph id...>"""
import json, re, sys
from collections import Counter
import arts, evo, node2b, stateinc, stepcheck, structured, tgraph3

OUT = evo.ROOT / "evaluations" / "tgraph4"
RELS = tgraph3.RELS
MAXLEN = 40
P = ("请把下面的原稿整理成一张“Thread 图”：每段几条短句（条目），加上条目之间的关系。之后视频怎么呈现、要提取什么，都从这张图里取，"
     "所以要一眼能看清：不是散文，也不是一段段长句。原稿是基准：它的每一步推进都不能丢；可以去掉的只有重复、铺垫、过渡、修饰、回顾和音乐描写。\n\n"
     "【Center】照抄下面这一句，一个字都不改，不要扩写、解释或另写：{CENTER}\n\n"
     "【条目 items】\n"
     "- 每条是一个短句，只说一件事：他此刻感到什么、想要什么、怕什么、做了什么、发现了什么。一般不超过 35 个字。"
     "一句说不完，就拆成两条；不要用分号和一连串逗号把几件事串成长句。\n"
     "- 几件事如果本来就是同一个念头，合成一句仍然很短、很自然，就合成一条；合不短的，分成几条。\n"
     "- 不按所求、恐惧、理由、办法、状态这些类型去拆；也不要写总结此刻状态的条目——那只会把前面几条再说一遍。\n"
     "- 每条都要说出别的条目没说过的东西。原稿里回顾、总结前面经历的句子不要写成条目，用关系指回那些条目。\n"
     "- 原稿里的限定要保留：原稿说仿佛、一度、那一刻、似乎，条目里也要有；一时的感受不能写成已经成立的认识；还说不清的，不要替他说清。"
     "不加原稿没有的东西。\n"
     "- key：每条给一个两到八个字的关键词，取自这条的原文，后面的关系用它来指代这一条。\n"
     "- kind：这条是一次理解的积累才标——分清（原先挤在一起的两个要求被分清）、办法的限度（一种给过他东西的办法显出不能处理的部分）、"
     "选择的代价、满足照出未满足、知道更多反而更尖锐；否则留空。\n\n"
     "【关系 because】\n"
     "- 写在后面那一段上：from 是更早段落的条目 id，to 是这一段的条目 id，rel 取：" + "、".join(RELS) + "。\n"
     "- 关系只用来说明：前面哪一条经历，让此刻的哪一条发生。同一段条目之间的先后不用连。\n"
     "- how 可以省略；只在它说出两端都没说的东西时才写，而且是一句短话。\n"
     "- 第一段以后的每一段，至少要有一条来自更早段落的关系——这就是他为什么此刻会这样。他暂时没在想那件事的段也一样。\n"
     "- 只连真正解释此刻的关系；“仍在起作用”只用于此刻确实还在左右他的感受或做法的东西。要连出原稿写到的远处关系，不只连上一段。\n\n"
     "【他和那件事的关系 relation】每段标一个：正在面对（他在想它、试办法、有所发现）、还说不清（他感到被什么牵动，但说不出是什么）、"
     "没在想（他沉浸在别的感受里，这件事暂时不在心上）。照原稿如实标，不要求比例。\n\n"
     "【outer】可选：原稿里有的可感处境，一句；没有就省略，不要编。\n\n"
     + stateinc.RULES +
     "不用“站稳、安顿、归属、边界、张力”这类抽象姿态词；原稿里有的，换成他具体在做什么、感到什么。\n"
     "\n只输出一个 ```json 代码块：{\"center\": \"…\", \"segments\": [{\"bars\": \"{FIRST}\", \"relation\": \"还说不清\", "
     "\"items\": [{\"id\": \"I1\", \"text\": \"…\", \"key\": \"…\", \"kind\": \"\"}], \"because\": []}]}\n"
     "第二段起 because 写成 [{\"from\": \"I1\", \"to\": \"I5\", \"rel\": \"改写\", \"how\": \"\"}]。segments 按顺序覆盖：{BARS}。\n\n")


# v4.1: v4 chopped sentences at every comma (Op.60 1–3 became 8 lines, 138–170 items per piece, 15 chars each) — the opposite
# failure. One item = one thought or one step (20–40 chars); layers of the same thought stay together; detail-only sentences fold in.
P41 = P.replace("- 每条是一个短句，只说一件事：他此刻感到什么、想要什么、怕什么、做了什么、发现了什么。一般不超过 35 个字。"
                "一句说不完，就拆成两条；不要用分号和一连串逗号把几件事串成长句。\n"
                "- 几件事如果本来就是同一个念头，合成一句仍然很短、很自然，就合成一条；合不短的，分成几条。\n",
                "- 每条是一句自然的话，说一个念头或一步变化：他此刻感到什么、想要什么、怕什么、做了什么、发现了什么。一般 20 到 40 个字。\n"
                "- 一个念头里本来连在一起的几层（例如想要和随之而来的迟疑、一个做法和它的理由），写在同一条里；只有换了一个新的念头、新的一步，才另起一条。"
                "不要把一句话按逗号切成几条，也不要用分号把几个念头串成一条长句。\n"
                "- 只记推进，不记细节：原稿里只是把同一个念头说得更细、更满的句子（例如“有时甚至……”这类补充），并进相关的那一条，或者略去。"
                "多数段落两到五条，内容多的段落可以多几条。条目不必都以“他”开头。\n", 1)
P41 = P41.replace("- key：每条给一个两到八个字的关键词，取自这条的原文，后面的关系用它来指代这一条。\n",
                  "- key：每条给一个四到十个字的短语，后面的关系用它来指代这一条；它要单独拿出来也看得懂指的是哪件事（有主要的动作或对象），不要截半句。\n", 1)
assert P41 != P and "多数段落两到五条" in P41 and "不要截半句" in P41
# key rewrite (v4.1 keys were half-sentence cuts like「不能成为」「几乎感不到」): items fixed, only keys re-written
KEYS = ("下面是一张图里的条目（id 和原文）。后面的关系会用一个短语来指代每一条，例如“←（1–3）「……」”。"
        "请给每条写一个四到十个字的短语：单独拿出来也看得懂指的是哪件事，有主要的动作或对象，不截半句，不加原文没有的意思。"
        "只输出一个 ```json 代码块：{\"I1\": \"…\", \"I2\": \"…\"}\n\n")
SHORT = 12
# v4.2 (user 10-21 on Op.60 4–16: "为什么和前面的有关联 ... 这两个为什么会被划归为两个异质的 bullet"): v4.1 forbade links
# inside a segment, so a segment's own 于是-chain became parallel bullets, and the model padded each bullet with a cross-segment
# arrow chosen by topic (4–16 got 「舍不得放下」→允许亲近, 「想让柔软多停留」→自由给予; the line says neither).
# Now: an item that follows from the previous item is marked follows=true (shown as →); cross-segment arrows only where the
# line makes the earlier experience the reason/premise/trigger; same-thing-twice items merge; audit keeps only 支持.
P42 = (P41.replace("- 关系只用来说明：前面哪一条经历，让此刻的哪一条发生。同一段条目之间的先后不用连。\n",
                   "- 同一段里，如果这一条是由上一条直接引出的（因为上一条，所以有这一条），给这一条标 follows: true；不是就不标。\n"
                   "- 跨段关系只连原稿写明的、或明显就是这个意思的前因：原稿把前面那条经历写成此刻的理由、前提或触发。"
                   "只是主题相近、情绪相似，不算，不要连。不必每一条都有跨段关系；通常一段里只有开头一两条有。\n", 1)
       .replace("- 每条都要说出别的条目没说过的东西。", "- 每条都要说出别的条目没说过的东西；两条如果其实在说同一件事（换个说法再说一遍），合成一条。", 1)
       .replace("\"key\": \"…\", \"kind\": \"\"}]", "\"key\": \"…\", \"kind\": \"\", \"follows\": false}]", 1))
assert P42.count("follows: true") == 1 and "换个说法再说一遍" in P42 and "\"follows\": false" in P42
# v4.3: with gpt3, v4.2's "merge same-thing items" made Op.61 items long again (avg 40–42 chars, 20–24 over 45, 9–13 chained).
# Now that → carries the in-segment cause, an over-long item is split into two linked items instead.
P43 = P42.replace("一般 20 到 40 个字。\n", "一般 20 到 40 个字，最长不超过 45 个字；超过了，说明装了两件事，就拆成两条，后一条标 follows。\n", 1)
assert P43 != P42
# repair pass: short items drop side-reasons ("对方从未作出承诺"); Op.60 v4.3 kept 50/56 vs v3's 54. Hand the weakened steps
# back with the line's text for those segments; only those segments' items change, ids kept so the arrows still hold.
FIX = ("下面是一张 Thread 图里几段的条目，以及原稿里这几段的原文。核对发现，原稿里有几步推进在这些条目里被弱化了（列在后面）。\n"
       "请只改这几段的条目：把缺掉的理由、前因或限定补回去，用原稿的意思，不加原稿没有的东西，也不改别的条目的意思。"
       "补了以后一条超过 45 个字，就拆成两条，后一条标 follows: true。保留原来的条目 id；拆出来的新条目，id 用原 id 加 b（例如 I12b）。"
       "每条仍是一句自然的话，不超过 45 个字，不用分号把几件事串在一起；只补缺掉的前因或关键限定，不把附带理由和程度补充补回来。\n"
       "只输出一个 ```json 代码块：{\"segments\": [{\"bars\": \"…\", \"items\": [{\"id\": \"I1\", \"text\": \"…\", \"key\": \"…\", \"kind\": \"\", \"follows\": false}]}]}\n\n")
ARROWS42 = None   # set below, after ARROWS
_A42 = ("- 支持：原稿明说了这个联系，或明显就是这个意思；\n- 勉强：原稿没这么说，但这样理解说得通；\n",
                          "- 支持：原稿把前面那条经历写成后面这条的理由、前提或触发（明说，或明显就是这个意思）；\n"
                          "- 勉强：原稿没这么写，只是这样理解说得通，或两条只是主题相近、情绪相似；\n")
# arrow audit: v4.1 coverage flagged 15 arrows of tg41_n8_op60_r1_r1 as links the line never makes (v3: 2)
ARROWS = ("下面是一篇原稿，以及从它整理出的“关系”：每条关系说前面某一条经历让后面某一条发生（或说明、限制、改写它）。"
          "请逐条判断原稿是否支持这条关系：\n- 支持：原稿明说了这个联系，或明显就是这个意思；\n- 勉强：原稿没这么说，但这样理解说得通；\n"
          "- 不支持：原稿里没有这个联系，或者它联系的其实是别的东西。\n"
          "只输出一个 ```json 代码块：{\"A1\": \"支持\", \"A2\": \"不支持\", ..., \"notes\": {\"A2\": \"一句话说明\"}}\n\n")
# v5 (user 10-21: "表达效率真的过关吗 ... 很多否定性的东西 ... 仍然不是我们特别喜欢的词"): v4.3 Op.60 had 93 items for 56 steps,
# 63% of items carried a negation, and few read as what he would say to himself. Keep every real move, drop side-reasons and
# emphasis; negations only when they carry content; plain words a person uses about himself; the disliked word list.
P5 = (P43.replace("原稿是基准：它的每一步推进都不能丢；可以去掉的只有重复、铺垫、过渡、修饰、回顾和音乐描写。",
                  "原稿是基准：它每一步真正的推进都不能丢（新的认识、新的所求、新的决定、新的困惑，以及后面会用到的前因）；"
                  "可以去掉的是重复、铺垫、过渡、修饰、回顾、音乐描写，以及同一步里的附带理由和程度补充。", 1)
      .replace("- 原稿里的限定要保留：",
               "- 否定只在说出真实的限制、被推翻的想法、或者后面会用到的东西时才写；其余改成正面说他此刻在想什么、做什么、感到什么。"
               "不要连串否定（“不……也不……更不……”）。\n"
               "- 尽量写成能还原成他心里一句话的样子，用一个人对朋友讲自己的事时会用的词（想要、怕、舍不得、不甘心、松了口气、硬撑、装作没事、"
               "嘴上说……心里其实……这一类），但不要为了用这些词而用。\n"
               "- 不用姿态词和抽象名词：站稳、立足、挺直、安顿、承受、承担、敞开、托住、悬着、落定、归属、边界、限度、代价、空缺、位置、意义、回应、辨认；"
               "也不用“正因为……才……”。原稿里有这些词的，换成他具体在想什么、怕什么、做什么。\n"
               "- 原稿里的限定要保留：", 1))
assert P5.count("否定只在说出真实的限制") == 1 and P5.count("同一步里的附带理由和程度补充") == 1
# v5.1: v5 removed the disliked words (12–15 -> 0) and halved chained negations, but items stayed at 93–97 for 56–60 steps and
# half still carried a negation (4–16: "他不必……也不必……" = the same step twice). Give each segment its step count from the
# inventory (one step, one item) and say what to write instead of a negation (example unrelated to the pieces).
P51 = (P5.replace("- 否定只在说出真实的限制、被推翻的想法、或者后面会用到的东西时才写；其余改成正面说他此刻在想什么、做什么、感到什么。",
                  "- 一步推进写一条。下面附有原稿每一段大约有几步推进，每段的条目数应当接近这个数；同一步的几种说法（换个角度再说一遍、"
                  "补一句“也不必……”）合成一条。\n"
                  "- 否定只在说出真实的限制、被推翻的想法、或者后面会用到的东西时才写；其余写他做了什么、想要什么，而不是他不必做什么"
                  "（例如不写“他不再追问结果”，写“他只管做眼前的事”）。", 1))
assert P51 != P5


def step_counts(t):
    inv = json.loads((stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8"))["steps"]
    c = Counter(re.sub(r"\s", "", s["segment"]).replace("-", "–").replace("—", "–") for s in inv)
    return "\n\n原稿各段大约的推进步数：" + "；".join(f"{b}：{c.get(b, 0)} 步" for b in structured.bars(tgraph3.work(t))) + "。\n\n"


# coverage checker v2: stepcheck.CHK marked condensed-but-complete steps as weakened (v5.1 Op.60 17–23 kept the cause and the
# result verbatim in meaning and was still "weakened"), so shorter graphs looked lossy. Weakened now needs a named loss.
CHK2 = stepcheck.CHK.replace("- kept：意思完整保留（换了说法没关系）；\n- weakened：还在，但因果或关键限定弱化、模糊了；\n",
                             "- kept：这一步的因和果都在（换了说法、说得更短、并进别的句子都没关系）；\n"
                             "- weakened：只用于这三种情况——因果断了（只剩结果，看不出因为什么）；关键限定丢了（仿佛、一度、还没、暂时这类）；"
                             "意思被压到读者会误解。说得更短本身不算弱化。\n", 1)
assert CHK2 != stepcheck.CHK
# trim (user 10-21 efficiency): building short (v5.1, one step per item) lost key moves late in each piece (judge GJ60f/GJ61f:
# why-now 8 -> 6.5–7, faithful 8 -> 6.2–6.8). So start from the content-rich v4.3 and edit only what the graph judges flagged
# there (repeats, empty negations, droppable detail, side-reasons, disliked words, wrong ✦ tags); items that carry arrows stay.
TRIM = ("下面是一张 Thread 图（每段的条目，带 id），以及几位评审逐条指出的问题。请按这些批注修改，目的是让图更精炼、一眼有内容，同时不丢任何一步真正的推进。\n"
        "规则：\n- 只改被点到的条目；没被点到的原样保留。\n"
        "- 重复：把它并进它重复的那一条，或删掉。空否定、可省细节、附带理由：删掉，或改成一句正面的话（他做了什么、想要什么）。"
        "抽象词、套路句：换成他具体在想什么、怕什么、做什么。标签贴错：改 kind 或留空。\n"
        "- 标了［有箭头］的条目不许删，只能改写，id 不变。\n"
        "- 每条不超过 45 个字，不用分号把几件事串在一起；不加原稿没有的东西；原稿的限定（仿佛、一度、还没）保留。\n"
        "- 不用这些词：站稳、立足、挺直、安顿、承受、承担、敞开、托住、悬着、落定、归属、边界、限度、代价、空缺、位置、意义、回应、辨认。\n"
        "只输出一个 ```json 代码块：{\"segments\": [{\"bars\": \"…\", \"items\": [{\"id\": \"I1\", \"text\": \"…\", \"key\": \"…\", \"kind\": \"\", \"follows\": false}]}]}"
        "——每一段都要输出完整的条目列表（包括没改的）。\n\n")
# reorg (user 10-21: "你现在的删改仅仅允许他去删吗 不允许重新组织吗 ... 句式单一 用词抽象单调 往往才是 ai 味道重的源头"):
# trim could only cut or merge flagged items, so v4.3's rhythm survived (56% of items open with 他; 仍/却 frames in ~17–20%).
# Rewrite each segment freely from v4.3's full content; keep every move and its reason; each new item names the old items it
# came from, so the why-now arrows are re-attached mechanically.
REORG = ("下面是一张 Thread 图（每段的条目，带 id），以及它所依据的原稿。请逐段重新组织、改写这张图，让它读起来像一个懂人心的人在讲这个人，"
         "而不是一张句式相同的清单。\n规则：\n"
         "- 可以合并、拆分、重排、改写条目。不加原稿没有的东西；但每一步真正的推进和它的理由都要留住——读者要看得出他为什么此刻会这样。"
         "原图里标了［有箭头］的条目，它说的事必须保留在某一条新条目里。\n"
         "- 句式要有变化：不要大多数条目都以“他”开头，不要反复套同一种框架（“他……，却……”“他不愿……也不……”“他仍……”）；长短交错；"
         "可以是他心里的一句话、一个问句、一个具体的动作或念头。不必为了变化而变化，读起来自然就好。\n"
         "- 用词具体：说得出他在想什么、怕什么、做什么。少用抽象名词和姿态词（站稳、承受、承担、安顿、回应、意义、位置、代价……）。\n"
         "- 只说他没做什么、不带信息的否定，改成正面说法；说出真实限制或被推翻的想法的否定，保留。\n"
         "- 一条一般不超过 45 个字；一段的条数跟这一段真正发生了多少相称。原稿的限定（仿佛、一度、还没）保留。\n"
         "- 每条写 from：它来自原图的哪几条（id 列表），用来把段与段之间的箭头接到新条目上；follows 表示由上一条引出；kind（理解的积累）"
         "沿用原图相应条目的，贴错了可以改或留空。\n"
         "只输出一个 ```json 代码块：{\"segments\": [{\"bars\": \"…\", \"items\": [{\"id\": \"N1\", \"text\": \"…\", \"from\": [\"I3\", \"I4\"], "
         "\"key\": \"…\", \"kind\": \"\", \"follows\": false}]}]}——每一段都要输出。\n\n")
TIER = ("下面是一篇原稿，以及从它抽出的因果步骤清单。请给每一步标一个：\n"
        "- 核心：一步真正的推进——新的认识、新的所求、新的决定、新的困惑，或者后面段落会用到的前因；\n"
        "- 细节：同一步里的附带理由、程度补充、把意思说得更满，删掉它，这一步的推进仍然成立。\n"
        "只输出一个 ```json 代码块：{\"S01\": \"核心\", \"S02\": \"细节\", ...}\n\n")
ARROWS42 = ARROWS.replace(*_A42, 1)
assert ARROWS42 != ARROWS


def index(j):
    return {it["id"]: (i, it) for i, s in enumerate(j["segments"]) for it in s.get("items") or []}


def check(j, w, t):
    segs, orig, I = j["segments"], tgraph3.segtexts(t, w), index(j)
    no_why, bad, dup, used = [], [], [], set()
    for i, s in enumerate(segs):
        ok = False
        for e in s.get("because") or []:
            f = e.get("from")
            if f in I and I[f][0] < i:
                ok = True; used.add(f)
            else:
                bad.append(f"{s['bars']} from {f}")
            if e.get("to") not in I or I[e["to"]][0] != i:
                bad.append(f"{s['bars']} to {e.get('to')}")
            if e.get("rel") not in RELS:
                bad.append(f"{s['bars']} rel {e.get('rel')}")
        if i and not ok:
            no_why.append(s["bars"])
        its = s.get("items") or []
        dup += [f"{s['bars']} {a['id']}≈{b['id']}" for k, a in enumerate(its) for b in its[k + 1:] if tgraph3.sim(a["text"], b["text"]) > 0.3]
    texts = [it["text"] for _, it in I.values()]; alltext = "\n".join(texts)
    return {"center_verbatim": j.get("center") == tgraph3.center(w), "bars_ok": [s["bars"] for s in segs] == structured.bars(w),
            "segments_without_why_now": no_why, "bad_refs": bad, "items": len(I), "follows": sum(bool(it.get("follows")) for _, it in I.values()), "too_long": [x for x in texts if len(x) > MAXLEN + 5],
            "too_short": [x for x in texts if len(x) < SHORT],
            "chained": [x for x in texts if x.count("；") + x.count(";") >= 1 or x.count("，") >= 4],
            "keys_short": [it.get("key") for _, it in I.values() if len(it.get("key") or "") < 4],
            "near_duplicates": dup, "hedge_lost": [s["bars"] for s in segs if tgraph3.HEDGE.search(orig.get(s["bars"], "")) and not any(tgraph3.HEDGE.search(it["text"]) for it in s.get("items") or [])],
            "formula": len(re.findall(r"越[^，。；]{0,12}越", alltext)) + len(re.findall(r"不是[^。；]{0,20}而是", alltext)),
            "posture_words": re.findall(r"站稳|安顿|归属|边界|张力", alltext),
            "arrows": sum(len(s.get("because") or []) for s in segs), "still_arrows": sum(e.get("rel") == "仍在起作用" for s in segs for e in s.get("because") or []),
            "relations": dict(Counter(s.get("relation") for s in segs)), "items_per_seg": [len(s.get("items") or []) for s in segs],
            "kinds": dict(Counter(it.get("kind") for _, it in I.values() if it.get("kind"))),
            "avg_item_chars": round(sum(map(len, texts)) / max(1, len(texts)), 1), "chars": len(alltext), "orig_chars": sum(len(x) for x in orig.values())}


def view(j, title):
    I = index(j); segs = j["segments"]
    md = [f"# {title}", "", f"**Center：**{j['center']}", ""]

    def src(e):
        x = I.get(e.get("from"))
        return f"（{segs[x[0]]['bars']}）「{x[1].get('key') or x[1]['text'][:10]}」" if x else f"（?）{e.get('from')}"
    for s in segs:
        md += [f"### {s['bars']}　（{s.get('relation')}）", ""]
        es = s.get("because") or []
        for n, it in enumerate(s.get("items") or []):   # a segment's first item has no previous item to follow from
            md.append(f"- {'→ ' if it.get('follows') and n else ''}{it['text']}" + (f"　✦ {it['kind']}" if it.get("kind") else ""))
            for e in es:
                if e.get("to") == it["id"] and (e.get("rel") != "仍在起作用" or e.get("how")):
                    md.append(f"  - ← {e.get('rel')}：{src(e)}" + (f" —— {e['how']}" if e.get("how") else ""))
        still = [src(e) for e in es if e.get("rel") == "仍在起作用" and not e.get("how")]
        if still:
            md.append("- ⟲ 仍在起作用：" + "；".join(dict.fromkeys(still)))
        if s.get("outer"):
            md.append(f"- ◎ {s['outer']}")
        md.append("")
    return "\n".join(md)


def full_text(j):
    I = index(j); segs = j["segments"]
    md = [f"Center：{j['center']}", ""]
    for s in segs:
        md.append(f"### {s['bars']}（{s.get('relation')}）")
        md += [f"- {it['id']}：{'（由上一条引出）' if it.get('follows') else ''}{it['text']}" + (f"（理解的积累：{it['kind']}）" if it.get("kind") else "") for it in s.get("items") or []]
        md += [f"- 关系：{e.get('from')}（{segs[I[e['from']][0]]['bars'] if e.get('from') in I else '?'}）{e.get('rel')} {e.get('to')}" + (f"：{e['how']}" if e.get("how") else "")
               for e in s.get("because") or []]
        if s.get("outer"):
            md.append(f"- 处境：{s['outer']}")
        md.append("")
    return "\n".join(md)


def title(w):
    return f"{'Op.60' if w == 'op60' else 'Op.61'}｜关系图"


def save(rid, t):
    w = tgraph3.work(t); j = evo.parse_json(evo.output(rid)); j["source"] = t; j["check"] = check(j, w, t)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}_view.md").write_text(view(j, title(w)), encoding="utf-8")
    print(rid, json.dumps(j["check"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    ph, args = sys.argv[1], sys.argv[2:]
    if ph in ("build", "build41", "build42", "build43", "build5", "build51"):
        pre, prompt = {"build": ("tg4", P), "build41": ("tg41", P41), "build42": ("tg42", P42), "build43": ("tg43", P43), "build5": ("tg5", P5), "build51": ("tg51", P51)}[ph]
        jobs = []
        for t in args:
            w = tgraph3.work(t)
            msg = (stateinc.fill(prompt, w).replace("{CENTER}", tgraph3.center(w)) + (step_counts(t) if ph == "build51" else "")
                   + "========== 原稿 ==========\n" + arts.clean(evo.output(t)))
            jobs += [node2b.job(f"{pre}_{t}_r{j}", msg, {"stage": pre, "thread": t}) for j in (1, 2) if not evo.done(f"{pre}_{t}_r{j}")]
        evo.run_parallel(jobs, 4)
        for t in args:
            for j in (1, 2):
                if evo.done(f"{pre}_{t}_r{j}"):
                    save(f"{pre}_{t}_r{j}", t)
    elif ph == "keys":
        jobs = []
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))
            lst = "\n".join(f"{it['id']}（{s['bars']}）：{it['text']}" for s in j["segments"] for it in s.get("items") or [])
            if not evo.done(f"keys_{g}"):
                jobs.append((f"keys_{g}", (lambda g=g, lst=lst: evo.call(f"keys_{g}", KEYS + lst, prompt_text=KEYS, model=evo.G56, meta={"stage": "graph4_keys"}))))
        evo.run_parallel(jobs, 2)
        for g in args:
            k = evo.parse_json(evo.output(f"keys_{g}"))
            (OUT / f"{g}_keys.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8"); print(g, len(k), "keys", list(k.values())[:8], flush=True)
    elif ph == "repair":   # -> <g>_fix.json (same because-lists, so <g>_arrows.json still applies)
        rows = json.loads((OUT / "cov_rows.json").read_text(encoding="utf-8"))
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); t = j["source"]; w = tgraph3.work(t); orig = tgraph3.segtexts(t, w)
            f2 = OUT / "cov2_rows.json"
            r2 = [r for r in (json.loads(f2.read_text(encoding="utf-8")) if f2.exists() else []) if r["graph"] == g]
            if r2:   # checker v2; a step counts as weakened only if every version (full, view) says so — the checker is noisy
                sets = [{s["id"] for s in r["not_kept"] if s.get("tier") in (None, "核心")} for r in r2]
                ids = set.intersection(*sets); bad = {s["id"]: s for r in r2 for s in r["not_kept"] if s["id"] in ids}
            else:
                bad = {s["id"]: s for r in rows if r["graph"] == g for s in r["not_kept"] if s.get("tier") in (None, "核心")}   # details may go
            segs = sorted({s["seg"] for s in bad.values()}, key=lambda b: int(re.split(r"[–-]", b)[0]))
            msg = FIX + "\n".join(
                f"### {b}\n原文：{orig.get(b, '')}\n条目：\n" + "\n".join(f"- {it['id']}：{it['text']}（key：{it.get('key')}）" + ("［由上一条引出］" if it.get("follows") else "")
                                                         for s in j["segments"] if s["bars"] == b for it in s.get("items") or [])
                for b in segs) + "\n\n被弱化的推进：\n" + "\n".join(f"- （{s['seg']}）因为{s['because']}，所以{s['so']}" for s in bad.values())
            if not evo.done(f"fix_{g}"):
                evo.call(f"fix_{g}", msg, prompt_text=FIX, model=evo.G6, meta={"stage": "graph4_fix"})
            fx = {s["bars"]: s["items"] for s in evo.parse_json(evo.output(f"fix_{g}"))["segments"]}
            for s in j["segments"]:
                if s["bars"] in fx:
                    s["items_before_fix"] = s["items"]; s["items"] = fx[s["bars"]]
            j["fixed_steps"] = list(bad)
            (OUT / f"{g}_fix.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            if (OUT / f"{g}_arrows.json").exists():
                (OUT / f"{g}_fix_arrows.json").write_text((OUT / f"{g}_arrows.json").read_text(encoding="utf-8"), encoding="utf-8")
            j["check"] = check(j, w, t); (OUT / f"{g}_fix.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"{g}_fix_view.md").write_text(view(j, title(w)), encoding="utf-8")
            print(g, "fixed segs", segs, json.dumps(j["check"], ensure_ascii=False)[:600], flush=True)
    elif ph == "trim":   # trim <graph id> <judge-eval ids comma-separated> <name of this graph in those evals> -> <g>_t
        g, evals, name = args[0], args[1].split(","), args[2]
        j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); t = j["source"]; w = tgraph3.work(t)
        probs = [p for e in evals for x in json.loads((evo.ROOT / "evaluations" / "graphjudge" / f"{e}.json").read_text(encoding="utf-8"))
                 if x["name"] == name for p in x.get("problems") or [] if p.get("type") in ("重复", "空否定", "可省细节", "附带理由", "抽象词", "套路句", "标签贴错", "不具体")]
        armed = {e.get("to") for s in j["segments"] for e in s.get("because") or []} | {e.get("from") for s in j["segments"] for e in s.get("because") or []}
        lst = "\n".join(f"### {s['bars']}\n" + "\n".join(f"- {it['id']}：{it['text']}（key：{it.get('key')}；kind：{it.get('kind') or ''}）" + ("［由上一条引出］" if it.get("follows") else "")
                                                       + ("［有箭头］" if it["id"] in armed else "") for it in s.get("items") or []) for s in j["segments"])
        notes = "\n".join(f"- （{p.get('seg')}）{p.get('type')}：{p.get('quote')}" for p in probs)
        rid = f"trim_{g}"
        if not evo.done(rid):
            evo.call(rid, TRIM + "========== 图 ==========\n" + lst + "\n\n========== 评审批注 ==========\n" + notes, prompt_text=TRIM, model=evo.G6, meta={"stage": "graph4_trim"})
        new = {s["bars"]: s["items"] for s in evo.parse_json(evo.output(rid))["segments"]}
        for s in j["segments"]:
            if s["bars"] in new:
                s["items_before_trim"] = s["items"]; s["items"] = new[s["bars"]]
        ids = {it["id"] for s in j["segments"] for it in s["items"]}
        for s in j["segments"]:   # an arrow whose end was merged away is dropped (and listed)
            s["because"] = [e for e in s.get("because") or [] if e.get("from") in ids and e.get("to") in ids]
        j["trim_notes"] = len(probs); j["check"] = check(j, w, t)
        (OUT / f"{g}_t.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{g}_t_view.md").write_text(view(j, title(w)), encoding="utf-8")
        print(g, "notes", len(probs), json.dumps(j["check"], ensure_ascii=False)[:500], flush=True)
    elif ph == "reorg":   # reorg <graph id> [run tag] [judge evals,comma] [name in evals] -> <g>_o<tag>
        g = args[0]; tag = args[1] if len(args) > 1 else "1"
        notes = ""
        if len(args) > 3:   # round 2: rewrite with the judges' notes on this graph and the coverage checker's wrong/weakened steps
            probs = [p for e in args[2].split(",") for x in json.loads((evo.ROOT / "evaluations" / "graphjudge" / f"{e}.json").read_text(encoding="utf-8"))
                     if x["name"] == args[3] for p in x.get("problems") or []]
            f2 = OUT / "cov2_rows.json"
            steps = {s["id"]: s for r in (json.loads(f2.read_text(encoding="utf-8")) if f2.exists() else []) if r["graph"] == g for s in r["not_kept"]}
            notes = ("\n\n========== 评审对这张图的批注（请据此重新组织，不只是删） ==========\n" + "\n".join(f"- （{p.get('seg')}）{p.get('type')}：{p.get('quote')}" for p in probs)
                     + "\n\n========== 原稿里被说错或说弱的推进（要说对、说清） ==========\n"
                     + "\n".join(f"- （{s['seg']}）{s['verdict']}：因为{s['because']}，所以{s['so']}" for s in steps.values())
                     + "\n\n同一个意思的条目要合成一条；只说他没做什么的否定改成正面说法。")
        j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); t = j["source"]; w = tgraph3.work(t)
        armed = {e.get("to") for s in j["segments"] for e in s.get("because") or []} | {e.get("from") for s in j["segments"] for e in s.get("because") or []}
        lst = "\n".join(f"### {s['bars']}（{s.get('relation')}）\n" + "\n".join(f"- {it['id']}：{it['text']}" + (f"（kind：{it['kind']}）" if it.get("kind") else "")
                                                       + ("［由上一条引出］" if it.get("follows") else "") + ("［有箭头］" if it["id"] in armed else "") for it in s.get("items") or [])
                        for s in j["segments"])
        rid = f"reorg_{g}_{tag}"
        if not evo.done(rid):
            evo.call(rid, REORG + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 图 ==========\n" + lst + notes, prompt_text=REORG, model=evo.G6, meta={"stage": "graph4_reorg"})
        def nb(b):   # the model may write "1—23（还说不清）"
            m = re.findall(r"\d+", b or ""); return f"{m[0]}–{m[1]}" if len(m) >= 2 else b
        new = {nb(s["bars"]): s["items"] for s in evo.parse_json(evo.output(rid))["segments"]}
        owner = {}
        for s in j["segments"]:
            for it in new.get(s["bars"], []):
                for o in it.get("from") or []:
                    owner.setdefault(o, it["id"])
        lost_armed = sorted(a for a in armed if a and a not in owner)
        for s in j["segments"]:
            if s["bars"] in new:
                s["items_before_reorg"] = s["items"]; s["items"] = [{k: v for k, v in it.items()} for it in new[s["bars"]]]
            seen, es = set(), []
            for e in s.get("because") or []:
                f, to = owner.get(e.get("from")), owner.get(e.get("to"))
                if f and to and (f, to, e.get("rel")) not in seen:
                    seen.add((f, to, e.get("rel"))); es.append({**e, "from": f, "to": to, "old": [e.get("from"), e.get("to")]})
            s["because"] = es
        j["lost_armed"] = lost_armed; j["check"] = check(j, w, t); og = f"{g}_o{tag}"
        (OUT / f"{og}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{og}_view.md").write_text(view(j, title(w)), encoding="utf-8")
        its = [it["text"] for s in j["segments"] for it in s["items"]]
        print(og, "items", len(its), "以他开头", f"{sum(x.startswith('他') for x in its) / len(its):.0%}", "仍", sum('仍' in x for x in its), "却", sum('却' in x for x in its),
              "lost armed", lost_armed, json.dumps({k: j["check"][k] for k in ("segments_without_why_now", "bad_refs", "arrows", "too_long", "posture_words")}, ensure_ascii=False)[:400], flush=True)
    elif ph == "split":   # -> <g>_s: an item "A；B" becomes A。 + B (follows), words unchanged; arrows keep pointing at A
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); n = 0
            for s in j["segments"]:
                out = []
                for it in s.get("items") or []:
                    parts = [x.strip() for x in re.split(r"[；;]", it["text"]) if x.strip()]
                    if len(parts) == 2 and min(map(len, parts)) >= 10:
                        out += [{**it, "text": parts[0].rstrip("，,") + "。"}, {"id": it["id"] + "b", "text": parts[1], "key": "", "kind": "", "follows": True}]; n += 1
                    else:
                        out.append(it)
                s["items"] = out
            t = j["source"]; w = tgraph3.work(t); j["check"] = check(j, w, t)
            (OUT / f"{g}_s.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"{g}_s_view.md").write_text(view(j, title(w)), encoding="utf-8")
            if (OUT / f"{g}_arrows.json").exists():
                (OUT / f"{g}_s_arrows.json").write_text((OUT / f"{g}_arrows.json").read_text(encoding="utf-8"), encoding="utf-8")
            print(g, "split", n, "items now", j["check"]["items"], "chained", len(j["check"]["chained"]), flush=True)
    elif ph == "arrows":
        jobs = []
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); I = index(j); n = 0; lst = []
            for s in j["segments"]:
                for e in s.get("because") or []:
                    n += 1; a, b = I.get(e.get("from")), I.get(e.get("to"))
                    if a and b:
                        lst.append(f"A{n}：（{j['segments'][a[0]]['bars']}）{a[1]['text']}  —{e.get('rel')}→  （{s['bars']}）{b[1]['text']}")
            msg = (ARROWS42 if g.startswith(("tg42", "tg43", "tg5")) else ARROWS) + "========== 原稿 ==========\n" + arts.clean(evo.output(j["source"])) + "\n\n========== 关系 ==========\n" + "\n".join(lst)
            if not evo.done(f"arrows_{g}"):
                jobs.append((f"arrows_{g}", (lambda g=g, msg=msg: evo.call(f"arrows_{g}", msg, prompt_text=ARROWS, model=evo.G56, meta={"stage": "graph4_arrows"}))))
        evo.run_parallel(jobs, 2)
        for g in args:
            a = evo.parse_json(evo.output(f"arrows_{g}"))
            (OUT / f"{g}_arrows.json").write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
            print(g, Counter(v for k, v in a.items() if k != "notes"), a.get("notes"), flush=True)
    elif ph == "final":   # relation per segment = majority of the line judges' 4 reads + both graph builds (tie: this graph)
        norm = {"面对": "正在面对", "说不清": "还说不清", "没在想": "没在想"}
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8")); t = j["source"]; w = tgraph3.work(t)
            kf = OUT / f"{g}_keys.json"
            if kf.exists():   # rewritten keys; the item texts stay as built
                k = json.loads(kf.read_text(encoding="utf-8"))
                ids = [it["id"] for s in j["segments"] for it in s.get("items") or []]
                if not set(k) & set(ids) and len(k) == len(ids):   # the model renumbered (I1… for R1…): match by order
                    k = dict(zip(ids, k.values()))
                for s in j["segments"]:
                    for it in s.get("items") or []:
                        it["key_model"] = it.get("key"); it["key"] = k.get(it["id"], it.get("key"))
            af = OUT / f"{g}_arrows.json"
            if af.exists():   # drop arrows the line does not support, unless that leaves a segment with no why-now arrow
                a = json.loads(af.read_text(encoding="utf-8")); n = 0; I = index(j); dropped = []
                for i, s in enumerate(j["segments"]):
                    es = s.get("because") or []; verdicts = []
                    for e in es:
                        n += 1; e["audit"] = a.get(f"A{n}"); verdicts.append(e["audit"])
                    keep = [e for e in es if e["audit"] not in (("不支持", "勉强") if g.startswith(("tg42", "tg43", "tg5")) else ("不支持",))]
                    if i and not any(I.get(e.get("from"), (99,))[0] < i for e in keep):
                        keep = es   # nothing supported left: keep and let the check show it
                        s["why_now_unsupported"] = True
                    dropped += [{"bars": s["bars"], **e, "note": (a.get("notes") or {}).get(f"A{n - len(es) + es.index(e) + 1}")} for e in es if e not in keep]
                    s["because"] = keep
                j["dropped_arrows"] = dropped
            reads = [x["center_relation_by_segment"] for x in json.loads((evo.ROOT / "evaluations" / f"C8{w[2:]}" / "rows.json").read_text(encoding="utf-8"))
                     if x["name"] == t and len(x.get("center_relation_by_segment") or []) == len(j["segments"])]
            pre = g[:g.index("_" + t)]
            base = re.sub(r"(_fix|_s)+$", "", g)   # a repaired/split graph and its build are one vote, not two
            sib = [json.loads(f.read_text(encoding="utf-8")) for f in OUT.glob(f"{pre}_{t}_r*.json") if f.stem != base and re.fullmatch(rf"{pre}_{t}_r\d+", f.stem)]
            for i, s in enumerate(j["segments"]):
                votes = [norm.get(r[i], r[i]) for r in reads] + [s["relation"]] + [x["segments"][i]["relation"] for x in sib]
                c = Counter(votes).most_common(); top = [k for k, n in c if n == c[0][1]]
                s["relation_votes"] = dict(c); s["relation_model"] = s["relation"]
                s["relation"] = s["relation"] if s["relation"] in top else top[0]
            j["check"] = check(j, w, t)
            (OUT / f"{g}_final.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"{g}_final_view.md").write_text(view(j, title(w)), encoding="utf-8")
            print(g, [(s["bars"], s["relation_model"], "→", s["relation"]) for s in j["segments"] if s["relation"] != s["relation_model"]], flush=True)
    elif ph in ("cov", "cov2"):
        chk, tag = (stepcheck.CHK, "g4chk") if ph == "cov" else (CHK2, "g4chk2")
        vers = {}
        for g in args:
            j = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))
            vers[(g, "full")] = full_text(j); vers[(g, "view")] = view(j, title(tgraph3.work(j["source"])))
        jobs = []
        for (g, v), txt in vers.items():
            t = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))["source"]; rid = f"{tag}_{v}_{g}"
            if not evo.done(rid):
                msg = chk.replace("{INV}", (stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8")).replace("{TXT}", txt)
                jobs.append((rid, (lambda rid=rid, msg=msg: evo.call(rid, msg, prompt_text=stepcheck.CHK[:300], model=evo.G56, meta={"stage": "graph4_cov"}))))
        evo.run_parallel(jobs, 4)
        rows = []
        for (g, v), txt in vers.items():
            r = evo.output(f"{tag}_{v}_{g}")
            if not r:
                continue
            t = json.loads((OUT / f"{g}.json").read_text(encoding="utf-8"))["source"]
            inv = {s["id"]: s for s in json.loads((stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8"))["steps"]}
            c = evo.parse_json(r); st = c.get("steps", {}); ad = c.get("additions", [])
            tf = stepcheck.OUT / f"{t}_tier.json"; tier = json.loads(tf.read_text(encoding="utf-8")) if tf.exists() else {}
            core = [k for k in inv if tier.get(k) == "核心"]
            rows.append({"graph": g, "version": v, "total": len(inv), **{k: list(st.values()).count(k) for k in ("kept", "weakened", "lost", "wrong")},
                         "core_total": len(core), "core_kept": sum(st.get(k) == "kept" for k in core),
                         "not_kept": [{"id": k, "seg": inv.get(k, {}).get("segment"), "because": inv.get(k, {}).get("because"), "so": inv.get(k, {}).get("so"), "verdict": x,
                                       "tier": tier.get(k)} for k, x in st.items() if x != "kept"],
                         "add_new": [a.get("text") for a in ad if a.get("type") == "new"], "chars": len(txt)})
        f = OUT / ("cov_rows.json" if ph == "cov" else "cov2_rows.json"); old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
        f.write_text(json.dumps([r for r in old if (r["graph"], r["version"]) not in vers] + rows, ensure_ascii=False, indent=1), encoding="utf-8")
        for r in rows:
            print(f"{r['graph']:32s} {r['version']:4s} 保留{r['kept']}/{r['total']} 核心保留{r['core_kept']}/{r['core_total']} 弱化{r['weakened']} 丢{r['lost']} 错{r['wrong']} 新增{len(r['add_new'])} 字{r['chars']}", flush=True)
    elif ph == "tier":   # which inventory steps are real moves (核心) and which are side-reasons / emphasis (细节)
        jobs = [(f"tier_{t}", (lambda t=t: evo.call(f"tier_{t}", TIER + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 步骤清单 ==========\n"
                                                     + (stepcheck.OUT / f"{t}.json").read_text(encoding="utf-8"), prompt_text=TIER, model=evo.G56, meta={"stage": "step_tier"})))
                for t in args if not evo.done(f"tier_{t}")]
        evo.run_parallel(jobs, 2)
        for t in args:
            k = evo.parse_json(evo.output(f"tier_{t}"))
            (stepcheck.OUT / f"{t}_tier.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
            print(t, Counter(k.values()), flush=True)
