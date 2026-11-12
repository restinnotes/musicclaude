"""Behavior-steering experiment batch (round E1). Each variant changes ONE thing relative to its base.
Bases:  C4 = P0 + bead-derived Center #4 ("那句话") block + D3 beads   (= cw_c1_4_r1 setup)
        C6 = P0 + bead-derived Center #6 (沉醉/失去边界) block + D3 beads
        PD = P0 + D3 beads (model's own main line)
Variants: base | X1 show-not-tell last line | X2 first-person monologue | X3 no-explaining rule | X6 whisper-to-listener
          | X7 <=150 字/段 | X4 two-stage plan->write | X8 critique->redraft (from a base draft)
usage: python exp.py <n_per_cell>
run ids: e1_<base>_<variant>_r<j>   (X4 plan: e1p_<base>_r<j>; X8 uses e1_<base>_base_r<j> as its draft)
"""
import json, sys
import centers, evo, gen

P0 = gen.render("P0", "op60", "orig")
OLD_LAST = "最后给我一篇鲜活的文章 能够合理化每个段落的情绪 即为什么在当前段落会感受到这个"
assert OLD_LAST in P0
MAT = gen.material("D3", "op60")
CANDS = json.loads((evo.ROOT / "evaluations" / "centers" / "c1.json").read_text(encoding="utf-8"))
BLOCK = {"C4": centers.block(CANDS[3]), "C6": centers.block(CANDS[5]), "PD": ""}

X = {
    "X1": None,  # handled by replacing the last line
    "X2": "用第一人称写：从头到尾是同一个“我”在这段时间里的内心独白。没有旁白，没有解说，不跳出来评论自己。",
    "X3": "不要解释情绪：不要写“为什么会这样？因为……”“原来……”“这使……”“这不是……而是……”这类句子，也不要在段尾总结。"
          "让前面发生过的事，在后面以具体的样子回来——一个动作、一句没说完的话、一种身体感觉——读者自己会明白为什么。",
    "X6": "想象读者正戴着耳机听这一段，你在他耳边轻声说话：只说他此刻正在经历什么，以及前面的什么此刻回来了、变了。"
          "不讲道理，不做分析。",
    "X7": "每一段不超过150字。",
}
X1_LAST = "最后给我一篇鲜活的文章 让读者在经历中感到每个段落的情绪为什么会在此刻出现——让他自己感到，而不是听你解释"

PLAN = ("先不要写文章。请按段落逐段写出你对这条 Thread 的理解，每段三行：\n"
        "1. 此刻：这一段正在经历什么（依据体验记录，一句话）；\n2. 来由：前面哪一段的什么经历此刻在起作用、怎样起作用（一句话，写明段号）；\n"
        "3. 变化：这件事在人身上什么变了、什么还没解决（一句话）。\n最后用一句话写出全篇的 Center。只输出这份理解。")
WRITE = ("下面是你此前对这条 Thread 逐段整理出的理解。现在请据此写文章：理解只是你写作的依据，不要把它当作结论写进文章；"
         "不解释，不总结，让读者在经历中感到每一段为什么会这样。\n\n========== 理解 ==========\n{PLAN}\n========== 理解结束 ==========\n")
CRIT = ("下面是你按上面的要求写出的初稿。请先在心里找出其中所有：解释情绪的句子（“为什么……因为……”“原来……”），段尾总结句，"
        "只是把体验记录换个说法重讲的句子，以及“摇曳、托举、悬着、终于”之类的抽象词。然后从头重写全文：同样的分段，"
        "同样的这条线，但让那些理解通过具体的经历显出来，而不是被说出来。只输出新文章。\n\n========== 初稿 ==========\n{DRAFT}\n========== 初稿结束 ==========\n")


def msg(base, var, extra=""):
    p = P0.replace(OLD_LAST, X1_LAST) if var == "X1" else P0
    if var in ("X2", "X3", "X6", "X7"):
        p = p.replace(OLD_LAST, X[var] + "\n\n" + OLD_LAST)
    b = ("\n\n" + BLOCK[base]) if BLOCK[base] else ""
    return p + b + ("\n\n---\n" + extra if extra else "") + MAT


def job(rid, m, meta):
    return (rid, lambda: evo.call(rid, m, prompt_text=m[:4000], meta=meta))


if __name__ == "__main__":
    n = int(sys.argv[1])
    jobs = []
    for base in ("C4", "C6", "PD"):
        vars_ = ["base", "X1", "X2", "X3", "X6", "X7"] if base == "C4" else ["base", "X1", "X2", "X3"]
        for v in vars_:
            for j in range(1, n + 1):
                rid = f"e1_{base}_{v}_r{j}"
                if not evo.done(rid):
                    jobs.append(job(rid, msg(base, "base" if v == "base" else v), {"stage": "e1", "base": base, "variant": v}))
        for j in range(1, n + 1):   # X4 stage 1 (plan)
            rid = f"e1p_{base}_r{j}"
            if not evo.done(rid):
                jobs.append(job(rid, msg(base, "base", PLAN), {"stage": "e1_plan", "base": base}))
    print(len(jobs), "first-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
    # second wave: X4 write from plan, X8 critique->redraft from base drafts
    jobs = []
    for base in ("C4", "C6", "PD"):
        for j in range(1, n + 1):
            plan = evo.output(f"e1p_{base}_r{j}")
            if plan and not evo.done(f"e1_{base}_X4_r{j}"):
                jobs.append(job(f"e1_{base}_X4_r{j}", msg(base, "base", WRITE.replace("{PLAN}", plan)), {"stage": "e1", "base": base, "variant": "X4"}))
            draft = evo.output(f"e1_{base}_base_r{j}")
            if draft and not evo.done(f"e1_{base}_X8_r{j}"):
                jobs.append(job(f"e1_{base}_X8_r{j}", msg(base, "base", CRIT.replace("{DRAFT}", draft)), {"stage": "e1", "base": base, "variant": "X8"}))
    print(len(jobs), "second-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
