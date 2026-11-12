"""Node 2 round N4: make the LINE the backbone (user 10-21: current Threads still read bead-driven).
  SP (spine-first, two calls): A) write the line as one continuous text, no segments, no per-segment sound description;
                                B) lay that line onto the given segments: each segment says where the line is now and why;
                                   sound/experience at most one or two sentences as grounding (beads cover the rest).
  BB (one call): P0 + "the body is the matter itself; each segment's present experience gets one or two sentences only".
Sources: own (P0, no Center) and bc (bead-derived tournament-winning Center).  Works: op60 (x3), op61 (x2).
run ids: n4_<work>_<SP|BB>_<own|bc>_r<j>   (SP step A: n4a_<work>_<own|bc>_r<j>)
"""
import json, sys
import evo, gen, node2b

LAST = "最后给我一篇鲜活的文章 能够合理化每个段落的情绪 即为什么在当前段落会感受到这个"
WIN = {"op60": "c60v2", "op61": "c61v2"}
WIN_K = {"op60": 3, "op61": 3}

SPINE_A = ("先不要分段，也不要逐段描写音乐。请用一段连续的文字（约 800–1200 字）写出这条线本身：这首曲子里那件属于人的事，"
           "从头到尾怎样发生、怎样被辨认、怎样被试探和承受、最后留下什么没有解决。可以提到音乐里最关键的几处转折作为依据，"
           "但主体是这件事本身的来龙去脉和其中的因果。只输出这段文字。")
SPINE_B = ("下面是你此前写出的这条线。现在把它落到上面给定的段落上，写成完整的文章：每一段都要说清这条线此刻走到了哪一步、"
           "为什么会走到这里（前面哪段的什么经历在起作用）。关于这一段声音和当下体验的描写，最多一两句，只作为依据——"
           "那部分另有专门的记录负责，不需要你展开。不写前言。\n\n========== 线 ==========\n{SPINE}\n========== 结束 ==========\n")
BACKBONE = ("这篇文章的主体是那件事本身怎样一步步发生、变化：每段写清它此刻走到哪一步、为什么。"
            "每段关于声音和当下体验的描写最多一两句，只作为依据，不要展开——当下体验另有专门的记录负责。直接从第一段写起，不写前言。")


def base(work, src):
    p = gen.render("P0", work, "note")
    if src == "bc":
        c = json.loads((evo.ROOT / "evaluations" / "centers" / f"{WIN[work]}.json").read_text(encoding="utf-8"))[WIN_K[work] - 1]
        p = p.replace(LAST, f"这一次，Thread 所围绕的那件事（Center）是：{c['center']}\n\n" + LAST)
    return p


if __name__ == "__main__":
    plan = [("op60", 3), ("op61", 2)]
    jobs = []
    for work, n in plan:
        for src in ("own", "bc"):
            for j in range(1, n + 1):
                b = base(work, src)
                rid = f"n4_{work}_BB_{src}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, b.replace(LAST, BACKBONE + "\n\n" + LAST), {"stage": "n4", "variant": "BB", "src": src, "work": work}))
                rid = f"n4a_{work}_{src}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, b + "\n\n---\n" + SPINE_A, {"stage": "n4_spine", "src": src, "work": work}))
    print(len(jobs), "first-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
    jobs = []
    for work, n in plan:
        for src in ("own", "bc"):
            for j in range(1, n + 1):
                spine = evo.output(f"n4a_{work}_{src}_r{j}")
                rid = f"n4_{work}_SP_{src}_r{j}"
                if spine and not evo.done(rid):
                    jobs.append(node2b.job(rid, base(work, src) + "\n\n---\n" + SPINE_B.replace("{SPINE}", spine),
                                           {"stage": "n4", "variant": "SP", "src": src, "work": work}))
    print(len(jobs), "second-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
