"""Non-prose form for the line (user 10-21: prose is anti-psychological-mechanism; final product is not prose; maybe
bullet / ChatGPT-answer style). Small batch to look at first.
  F1 rewrite existing line: ChatGPT-answer style, per segment a few points: state / why (which earlier segment) / mechanism
  F2 rewrite existing line, minimal: 改写成要点式，重点讲心理机制，不要散文的连接
  F3 write from P0 directly in that form (route A, no beads, no Center given)
ids: fm_<F1|F2>_<thread>_r1, fm_F3_<work>_r<j>"""
import evo, gen, node2b, node2s

THREADS = {"op60": "n6_op60_IB_own_r1", "op61": "n7_op61_IA_c4_r1"}
H = "保留原来的分段标题。只输出改写后的内容。\n\n"
F1 = ("把下面这篇文章改写成 ChatGPT 回答那样的要点式：每段下面列几个要点，讲清楚——他此刻怎么了；为什么会这样（是前面哪一段的什么导致的）；"
      "背后是什么心理机制（用人话说清楚，可以点名常见的心理机制）；这会把他推向哪里。不要散文式的过渡、铺垫和修饰，没有内容的话一句都不要。"
      "这一段没有新的变化，就只写一两条。不损失原文的内容。" + H)
F2 = "把下面这篇文章改写成要点式，重点讲心理机制，不要散文式的连接。" + H
F3 = ("这一次不要写成散文。请用 ChatGPT 回答那样的要点式来写这条 Thread：按上面给定的段落，每段下面列几个要点，讲清楚——他此刻怎么了；"
      "为什么会这样（是前面哪一段的什么经历或认识导致的）；背后是什么心理机制（用人话说清楚，可以点名常见的心理机制）；这会把他推向哪里。"
      "每一次变化都由前面已经发生的事推出，不靠音乐事件推动，不编外部事件、物件或对白；音乐最多一句，只作为这个状态的外在样子。"
      "不要过渡、铺垫和修饰；这一段没有新的变化，就只写一两条。")

if __name__ == "__main__":
    jobs = []
    for w, t in THREADS.items():
        src = __import__("arts").clean(evo.output(t))
        for v, p in (("F1", F1), ("F2", F2)):
            rid = f"fm_{v}_{t}_r1"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, p + src, {"stage": "fmt", "variant": v, "thread": t}))
        for j in (1, 2):
            rid = f"fm_F3_{w}_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, gen.render("P0", w, "note").replace(node2s.LAST, F3 + "\n\n" + node2s.LAST), {"stage": "fmt", "variant": "F3", "work": w}))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 4)
