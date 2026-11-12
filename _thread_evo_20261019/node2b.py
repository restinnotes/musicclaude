"""Node 2 round N2: variants around P0 + one-sentence bead-derived Center (most promising in N1 by my reading).
  cn : + start directly at segment 1, no preface/thesis
  cs : + no "也许……" hypothetical mini-scenes or invented events; reasons come from what was already lived + the music now
  cL : two-step — first a per-segment logic chain (feeling | which earlier experience it comes from | what happens in the music),
       then the article, keeping that logic explicit in plain words
  c on GPT-5.6 and on Gemini (direct) as writers
Centers: 1 / 4 (说出口), 6 (沉醉), 2.  run ids: n2_<variant>c<k>_<writer>_r<j>
"""
import sys
import evo, node2

NOPRE = "直接从第一段写起，不要在正文前写任何说明、前言或对全篇主题的预告。"
NOSPEC = "不要用“也许……”这样的假设小场景，也不要另编具体事件、对白或物件；每段感受的理由，来自前文已经写过的经历和此刻音乐里发生的事。"
PLAN = ("先不要写文章。请逐段写出这条 Thread 的逻辑链，每段一行：此刻的感受｜它从前面哪一段的什么经历而来（写明段号）｜此刻音乐里实际发生了什么。"
        "最后一行写出全篇的 Center。只输出这份逻辑链。")
WRITE = ("下面是你此前整理的逻辑链。现在据此写文章：这条逻辑要在文章里用人话说出来——读者读完每一段，应当明白此刻为什么会这样——"
         "但不要写成提纲或清单，也不要在正文前写前言。\n\n========== 逻辑链 ==========\n{PLAN}\n========== 结束 ==========\n")


def base(k):
    return node2.variants()[f"P0c{k}"]


def with_line(m, line):
    return m.replace(node2.LAST, line + "\n\n" + node2.LAST)


def job(rid, m, meta, w="g6"):
    if w == "gem":
        return (rid, lambda: evo.call_gemini_direct(rid, m, prompt_text=m, meta=meta))
    model = evo.G6 if w == "g6" else evo.G56
    return (rid, lambda: evo.call(rid, m, prompt_text=m, model=model, meta=meta))


if __name__ == "__main__":
    n = int(sys.argv[1]); jobs = []
    for k in (1, 4, 6, 2):
        for j in range(1, n + 1):
            for var, m in (("cn", with_line(base(k), NOPRE)), ("cs", with_line(base(k), NOSPEC))):
                rid = f"n2_{var}{k}_g6_r{j}"
                if not evo.done(rid):
                    jobs.append(job(rid, m, {"stage": "n2", "variant": var, "center": k}))
            for w in ("g56", "gem"):
                rid = f"n2_c{k}_{w}_r{j}"
                if k in (1, 6) and not evo.done(rid):
                    jobs.append(job(rid, base(k), {"stage": "n2", "variant": "c", "center": k, "writer": w}, w))
            rid = f"n2p_cL{k}_r{j}"
            if k in (1, 6) and not evo.done(rid):
                jobs.append(job(rid, base(k) + "\n\n---\n" + PLAN, {"stage": "n2_plan", "center": k}))
    print(len(jobs), "first-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
    jobs = []
    for k in (1, 6):
        for j in range(1, n + 1):
            plan = evo.output(f"n2p_cL{k}_r{j}")
            rid = f"n2_cL{k}_g6_r{j}"
            if plan and not evo.done(rid):
                jobs.append(job(rid, base(k) + "\n\n---\n" + WRITE.replace("{PLAN}", plan), {"stage": "n2", "variant": "cL", "center": k}))
    print(len(jobs), "second-wave jobs", flush=True)
    evo.run_parallel(jobs, 12)
