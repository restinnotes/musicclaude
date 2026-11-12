"""Advisor round 1 (adv_r1), experiments 1, 2, 4. Third person throughout; no invented dialogue/actions.
  si  (exp 1): state model + per-segment increments -> structured line with conditional fields  ids: si_<t>_r<j> (si_a_ = step A)
  cr  (exp 2): re-render existing structured st_<t>_r1 with conditional fields only              ids: cr_<t>
  fp  (exp 4): fidelity / concreteness / no-filler final pass on a candidate (minimal edits)     ids: fp_<cand>
All outputs JSON: {center, segments:[{bars, headline, why?, history?, revises?, pressure?}]} -> evaluations/stateinc/<id>.json/.md"""
import json, re, sys
import arts, evo, fmt4, node2b, plain, seg, structured

OUT = evo.ROOT / "evaluations" / "stateinc"
SCHEMA = ("只输出一个 ```json 代码块：{\"center\": \"整篇围绕的那件事（一句人话，内部元数据）\", \"segments\": [{\"bars\": \"{FIRST}\", \"headline\": \"……\", "
          "\"why\": \"（可选）\", \"history\": \"（可选）\", \"revises\": \"（可选）原以为……，现在……\", \"pressure\": \"（可选）\"}]}\n"
          "segments 必须按顺序覆盖这些段落，一个不多一个不少：{BARS}。可选字段不需要就省略。\n")
RULES = ("统一使用第三人称“他”。不要新增原稿没有的对白、动作、事件或人物关系：可以把心理说具体（他怕什么、想知道什么），"
         "但不能写成他说了某句话、做了某件事。不要提音乐。不要用“越……越……”“不是……而是……”“X 不等于 Y／不代表”“真正的……是……”“与其……不如……”"
         "这类套路句式，也不要对仗、格言式的金句。少用“归属、安顿、承认、支点、某某与某某的两难”这类概念词，尽量说成他具体想要什么、怕什么。\n")
SI_A = ("请以原稿为内容来源，以 F8 稿为逻辑参照，做“持续状态增量”分析（这一步不是成稿）。\n"
        "第一步，建立全篇状态模型：这条人物主线中持续起作用的状态——他具体想要什么、害怕什么；他用什么办法保护自己；哪些过去的经历至今仍影响他的判断；"
        "哪些现实限制不由他控制；哪种尚未解决的矛盾推动他继续作出选择。\n"
        "第二步，逐段记录状态增量：进入本段时他已经知道、相信或害怕什么；本段新增了什么认识或心理变化；这次变化为什么会从先前的经历中发生；"
        "它给下一段留下了什么尚未解决的问题。只保留真正影响当前选择的旧经历；长程呼应写清旧经历的具体内容及其当前作用，不要只列段号。\n"
        "用简洁的条目输出即可，不要散文。\n\n")
SI_B = ("下面是一篇“线”的状态模型与逐段状态增量。请据此压缩成结构化线稿，供讲解视频使用。\n"
        "每段以一句具体的心理变化为主（headline）。只有在不解释前因就会读不懂时，才写 why（一句）；只有某段较早的经历正在改变本段的意义或选择时，"
        "才写 history（一句，用自然语言说清是哪件旧经历、它现在怎样起作用，不要列段号）；只有认识确实改变时才写 revises；只有本段确实给下一段留下新问题时才写 pressure。"
        "不要强迫每段使用相同字段或相同长度；同一心理机制只解释一次。全稿以 2200–2600 字为目标；如果必须在字数和关键因果之间取舍，优先保留因果。\n"
        + RULES + SCHEMA + "\n")
CR = ("请使用与下面这份结构化线稿完全相同的内容和段落划分，重新渲染结构。headline 必须保留；why 只有当本段变化无法从 headline 看懂时才保留（一句）；"
      "history 只有当某段较早的经历正在改变本段的意义或选择时才保留（一句，用自然语言说清，不要列段号）；revises 只有认识确实改变才保留；"
      "pressure 只有本段确实产生推动下一段的新问题才保留。同一心理机制只解释一次；短段允许只保留一个心理动作。不得新增内容，不得改变因果关系。\n"
      + RULES + SCHEMA + "\n")
FP = ("请对下面的候选线稿（JSON）做终审，对照后面的原稿。不要整篇重写，不要增加任何新内容。逐段检查并做最小修改：\n"
      "1. 新增内容：是否把心理愿望写成了原稿没有明确支持的对白、动作、事件或人物关系？没有依据的改回心理愿望。\n"
      "2. 抽象表达：是否用“归属、安顿、相互承认、支点”等概念代替了人物的具体想法？改成他实际想知道什么、害怕什么、想要什么。\n"
      "3. 重复与空转：一句话若只是重复上一句、删掉后因果不受影响，就删掉或合并。\n"
      "4. 固定句式：“越……越……”“不是……而是……”等套路和空泛总结。\n"
      "不得改变段落的因果关系、中心问题或已有心理转折。统一第三人称。只修改有明确问题的句子，其余原样保留。\n"
      "输出修改后的完整 JSON（同样的结构），只输出一个 ```json 代码块。\n\n")


def fill(t, w):
    b = structured.bars(w)
    return t.replace("{FIRST}", b[0]).replace("{BARS}", "、".join(b))


def render(j, title):
    md = [f"# {title}", ""]
    for s in j["segments"]:
        md += [f"### {s['bars']}", "", f"**{s['headline']}**"]
        for k, mark in (("why", "← "), ("history", "◎ "), ("revises", "↺ "), ("pressure", "→ ")):
            if s.get(k):
                md.append(mark + s[k])
        md.append("")
    return "\n".join(md)


def save(rid, w):
    r = evo.output(rid)
    if not r:
        return
    j = evo.parse_json(r); got = [s["bars"].replace("-", "–").replace("—", "–") for s in j["segments"]]
    heads = [s["headline"] for s in j["segments"]]
    j.update(work=w, source=rid, segments_valid=got == structured.bars(w),
             formula=sum(any(re.search(v, h) for v in fmt4.PAT.values()) for h in heads))
    md = render(j, rid); OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{rid}.md").write_text(md, encoding="utf-8")
    nf = sum(1 for s in j["segments"] for k in ("why", "history", "revises", "pressure") if s.get(k))
    print(rid, "ok" if j["segments_valid"] else "SEG MISMATCH", "formula", j["formula"], "optional-fields", nf, "chars", len(md) - len(rid) - 3, flush=True)


def threads():
    return [(t, w) for w, ts in plain.THREADS.items() for t in ts]


if __name__ == "__main__":
    ph = sys.argv[1]; jobs = []
    if ph == "si":
        for t, w in threads():
            src = "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== F8 稿（逻辑参照） ==========\n" + arts.clean(evo.output(f"fm_F8_{t}_r1"))
            if not evo.done(f"si_a_{t}"):
                jobs.append(node2b.job(f"si_a_{t}", SI_A + src, {"stage": "si_a", "thread": t}))
        evo.run_parallel(jobs, 4); jobs = []
        for t, w in threads():
            a = evo.output(f"si_a_{t}")
            for j in (1, 2):
                if a and not evo.done(f"si_{t}_r{j}"):
                    jobs.append(node2b.job(f"si_{t}_r{j}", fill(SI_B, w) + a, {"stage": "si_b", "thread": t}))
        evo.run_parallel(jobs, 4)
        for t, w in threads():
            for j in (1, 2):
                save(f"si_{t}_r{j}", w)
    elif ph == "cr":
        for t, w in threads():
            src = (evo.ROOT / "evaluations" / "structured" / f"st_{t}_r1.json").read_text(encoding="utf-8")
            if not evo.done(f"cr_{t}"):
                jobs.append(node2b.job(f"cr_{t}", fill(CR, w) + src, {"stage": "cr", "thread": t}))
        evo.run_parallel(jobs, 4)
        for t, w in threads():
            save(f"cr_{t}", w)
    elif ph == "fp":
        for cand in sys.argv[2].split(","):
            t = next(x for x, _ in threads() if x in cand); w = "op60" if "op60" in t else "op61"
            src = (OUT / f"{cand}.json").read_text(encoding="utf-8")
            if not evo.done(f"fp_{cand}"):
                jobs.append((f"fp_{cand}", (lambda cand=cand, m=FP + src + "\n\n========== 原稿 ==========\n" + arts.clean(evo.output(t)):
                                           node2b.job(f"fp_{cand}", m, {"stage": "fp"})[1]())))
        evo.run_parallel(jobs, 4)
        for cand in sys.argv[2].split(","):
            save(f"fp_{cand}", "op60" if "op60" in cand else "op61")
