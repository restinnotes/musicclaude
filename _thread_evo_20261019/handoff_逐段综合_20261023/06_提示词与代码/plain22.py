"""Plain-language 2x2 (user 10-23, PLAN_逐段构建线_20261023.md step 2): is the missing 人话 caused by too much context, by a long
rule-laden prompt, or both? Content is fixed (the N8 draft n8_op60_r1, source of the v6 line); only the wording may change.
Sections: S02 (4–16, one feeling split into steps), S04 (24–34, conflicts with the beads), S13 (103–110, abstract causation).
  LW long rules + whole article   SW short + whole article   LS long rules + this section only   SS short + section only
ids: p22_<cond>_<sec>_<m>.  usage: python plain22.py run | show"""
import json, re, sys
import evo, node2b, segcheck, arts

SRC = "n8_op60_r1"
SECS = ["S02", "S04", "S13"]
CONDS = ["LW", "SW", "LS", "SS"]
OUT = evo.ROOT / "evaluations" / "plain22"

LONG = ("请把下面这一段改写成人话。要求：\n"
        "1. 用一个人对朋友讲自己的事时会用的词，读者一遍就能跟上；写他具体在想什么、怕什么、想要什么，不要用抽象名词概括心理。\n"
        "2. 不用这些词：站稳、立足、挺直、安顿、承受、承担、敞开、托住、悬着、落定、归属、边界、限度、代价、空缺、位置、意义、回应、辨认。\n"
        "3. 否定只在说出真实的限制、被推翻的想法时才写；其余改成正面说他此刻在想什么、做什么。不要连串否定（“不……也不……更不……”）。\n"
        "4. 不要“越……越……”这类套路句，不要整齐的对仗、分号对举，不要把心理过程总结成一句哲理。\n"
        "5. 不要替人物宣布他意识到了什么；不要用连接句代替推导。\n"
        "6. 原文的每一步因果都要保留；原文的限定（仿佛、一度、那一刻）要保留；不新编情节、物件、对白；不写音乐。\n"
        "7. 只改这一段，不改意思，不加不减。只输出改写后的这一段。\n")
SHORT = "请用普通人一遍就能听懂的话，把下面这一段重新说一遍：不改意思，不加也不减。只输出这段话。\n"


def sections():
    j = segcheck.to_json(arts.clean(evo.output(SRC)), "op60")
    return {s["id"]: s for s in j["segments"]}


def message(cond, sec):
    S = sections(); s = S[sec]
    head = LONG if cond[0] == "L" else SHORT
    if cond[1] == "W":
        whole = "\n\n".join(f"【第{x['start']}–{x['end']}小节】\n{x['text']}" for x in S.values())
        return (head + f"\n下面是整篇文章，供你了解前后文；只改写其中第 {s['start']}–{s['end']} 小节这一段。\n\n"
                + whole + f"\n\n===== 要改写的段：第 {s['start']}–{s['end']} 小节 =====\n{s['text']}")
    return head + "\n" + s["text"]


def smells(t):
    sents = [x for x in re.split(r"[。！？\n]", t) if x.strip()]
    neg = sum(1 for x in sents if re.search(r"不(?!由|只|仅|断|久|同|少|住|禁|过|觉)|没有?|未(?!来)|无(?!论|法)", x))
    return {"chars": len(t), "sents": len(sents), "neg_sent%": round(100 * neg / max(1, len(sents))),
            "这份/一种": len(re.findall(r"这份|那份|一种", t)), "；": t.count("；"), "越越": len(re.findall(r"越.{0,12}越", t))}


if __name__ == "__main__":
    if sys.argv[1] == "run":
        evo.run_parallel([node2b.job(f"p22_{c}_{s}_{m}", message(c, s), {"stage": "plain22", "cond": c, "sec": s}, w=m)
                          for s in SECS for c in CONDS for m in ("g6", "g56") if not evo.done(f"p22_{c}_{s}_{m}")], 8)
    elif sys.argv[1] == "show":
        S = sections(); OUT.mkdir(parents=True, exist_ok=True); md = ["# 人话 2×2：同一内容，只改说法\n",
              "LW = 长规则 + 整篇上下文；SW = 短提示 + 整篇；LS = 长规则 + 只给这一段；SS = 短提示 + 只给这一段。原文 = N8 原稿（n8_op60_r1）。\n"]
        stats = {}
        for s in SECS:
            md.append(f"\n## 第 {S[s]['start']}–{S[s]['end']} 小节\n\n**原文**　{smells(S[s]['text'])}\n\n{S[s]['text']}\n")
            for c in CONDS:
                for m in ("g6", "g56"):
                    t = (evo.output(f"p22_{c}_{s}_{m}") or "").strip()
                    stats[f"{c}_{s}_{m}"] = smells(t)
                    md.append(f"\n**{c}·{m}**　{smells(t)}\n\n{t}\n")
        (OUT / "p22_view.md").write_text("\n".join(md), encoding="utf-8")
        (OUT / "p22_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding="utf-8")
        print(OUT / "p22_view.md")
