"""Round 2 of non-prose form (user 10-21: approved bullets; wants more condensed, deeper, content visible at a glance;
plain words, not philosophy). F4 = rewrite existing line; F5 = write from P0 directly (route A, no beads).
ids: fm_F4_<thread>_r<j>, fm_F5_<work>_r<j>"""
import arts, evo, gen, node2b, node2s, plain

FORM = ("每段最多三行：\n"
        "第一行加粗：一句话点出这一刻最关键的心理机制——要说出一个读者没想到、但一听就明白的道理"
        "（方向示例，与本曲无关：“越怕被丢下，就越先把人推开”），用人话，不用心理学或哲学术语，不要只描述状态。\n"
        "第二行以“← 因为”开头：是前面哪一段的什么导致了它（一句）。\n"
        "第三行以“→ 于是”开头：它把他推向哪里（一句）。\n"
        "这一段没有新的变化，就只写第一行。不要前言、总结、过渡和修饰。")
F4 = "把下面这篇文章改写成极凝练的要点，不损失原文的关键因果。保留原来的分段标题。\n" + FORM + "\n只输出改写后的内容。\n\n"
F5 = ("这一次不要写成散文，也不要写前言。请按上面给定的段落写这条 Thread，" + FORM +
      "\n每一次变化都由前面已经发生的事推出，不靠音乐事件推动，不编外部事件、物件或对白。")

if __name__ == "__main__":
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(t))
            for j in (1, 2):
                rid = f"fm_F4_{t}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, F4 + src, {"stage": "fmt2", "variant": "F4", "thread": t}))
        for j in (1, 2):
            rid = f"fm_F5_{w}_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, gen.render("P0", w, "note").replace(node2s.LAST, F5 + "\n\n" + node2s.LAST), {"stage": "fmt2", "variant": "F5", "work": w}))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 4)
