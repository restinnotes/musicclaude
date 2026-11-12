"""Node 2 round N6 (route A, no beads): the line must drive itself; music events never cause a turn (user 10-21).
  IA (two calls): A) the matter itself as one continuous, time-ordered text with NO music at all; its turns follow the
                     order of the given segments.  B) lay it onto the segments: every segment starts from where the previous
                     one left the person; the reason for the turn is earlier experience; music at most one sentence, only as
                     the outward shape of a state already explained, never as its cause.
  IB (one call): P0 + the same rules in one pass.
Sources: own (no Center), c (top route-A self-Center), rs (look things up first; the spine still never mentions music).
run ids: n6a_<work>_<src>_r<j> (spine), n6_<work>_<IA|IB>_<src>_r<j>
"""
import json
import evo, gen, node2b, node2s

LAST = node2s.LAST
TOPC = {"op60": [("s60", 2), ("s60", 6)], "op61": [("s61", 4), ("s61", 2)]}

SPINE = ("先不要分段，也完全不要写音乐（不写声音、旋律、主题、调性、节奏、小节）。请用一段连续的文字（约 1000–1500 字）"
         "写出这条线本身：这首曲子里那件属于人的事，从头到尾怎样一步一步发生。要求：每一次变化都必须由前面已经发生在这个人身上的事推出来"
         "——因为先前得到了什么、相信了什么、试过什么、发现了什么，所以此刻才会这样；不要让任何变化“忽然”从外面降临。"
         "这条线的先后要和上面给定的段落先后对应（你心里知道每一步大致落在哪一段），但文字里不提段落、不提音乐。只输出这段文字。")
RESEARCH = ("动笔前，先查阅关于这首曲子的可靠资料（写于何时、作曲家当时的处境、演奏家和研究者通常怎样理解它），"
            "用来帮助你判断这件属于人的事是什么；但写出来的文字里不讲传记，也不编造史实。\n\n")
RULES = ("写法要求（最重要）：\n"
         "1. 全文必须自己读起来就是一条有先后、有因果的连续过程。每一段都从上一段结束时这个人所处的状态写起，"
         "先说清这一段的变化为什么会发生——理由是前面哪一段的什么经历、已经成立的什么认识。\n"
         "2. 音乐事件不能当原因。不要写“此时音乐忽然……于是他……”“新的主题出现，像是他决定……”“到了第X小节，……”。"
         "不要用音乐描写开头一段。音乐每段最多一句，只能作为一个已经说明了来由的状态的外在样子出现；把所有写音乐的句子删掉，文章仍然应当完整连贯。\n"
         "3. 每段的当下体验不必展开（另有专门的记录负责），重点是这件事此刻走到了哪一步、为什么。\n"
         "4. 不另编情节、对白、物件或人生事件。不写前言，直接从第一段写起。\n")
LAY = ("下面是你此前写出的这条线。现在把它落到上面给定的段落上，写成完整的文章。\n\n" + RULES +
       "\n========== 线 ==========\n{SPINE}\n========== 结束 ==========\n")


def base(work, src):
    p = gen.render("P0", work, "note")
    if src == "own" or src == "rs":
        return p
    tag, k = src.split(":")
    c = json.loads((evo.ROOT / "evaluations" / "centers" / f"{tag}.json").read_text(encoding="utf-8"))[int(k) - 1]
    return p.replace(LAST, f"这一次，Thread 所围绕的那件事（Center）是：{c['center']}\n\n" + LAST)


def srcs(work):
    return [("own", "own"), ("rs", "rs")] + [(f"c{k}", f"{t}:{k}") for t, k in TOPC[work]]


if __name__ == "__main__":
    works = ["op60", "op61"]
    jobs = []
    for w in works:
        for name, s in srcs(w):
            n = 2 if name in ("own", "rs") else 1
            for j in range(1, n + 1):
                rid = f"n6a_{w}_{name}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, base(w, s) + "\n\n---\n" + (RESEARCH if name == "rs" else "") + SPINE,
                                           {"stage": "n6_spine", "src": name, "work": w}))
        for j in (1, 2):
            rid = f"n6_{w}_IB_own_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, base(w, "own").replace(LAST, RULES + "\n" + LAST), {"stage": "n6", "variant": "IB", "work": w}))
    print(len(jobs), "first-wave jobs", flush=True)
    evo.run_parallel(jobs, 14)
    jobs = []
    for w in works:
        for name, s in srcs(w):
            for j in (1, 2):
                sp, rid = evo.output(f"n6a_{w}_{name}_r{j}"), f"n6_{w}_IA_{name}_r{j}"
                if sp and not evo.done(rid):
                    jobs.append(node2b.job(rid, base(w, s) + "\n\n---\n" + LAY.replace("{SPINE}", sp),
                                           {"stage": "n6", "variant": "IA", "src": name, "work": w}))
    print(len(jobs), "second-wave jobs", flush=True)
    evo.run_parallel(jobs, 14)
