"""Node 2 round N5 (route A, no beads): the spine comes from research, not from beads.
  RA) P0 + "first look up reliable material on this piece (when/why written, the composer's situation, the readings
      performers and scholars commonly give, its form), then write the line as one continuous text (800-1200 chars)"
  RB) same as node2s SPINE_B: lay that line onto the segments; sound/experience one or two sentences per segment.
run ids: n5a_<work>_r<j> (spine), n5_<work>_RS_r<j> (Thread)
"""
import evo, gen, node2b, node2s

RESEARCH_A = ("先不要分段，也不要逐段描写音乐。请先查阅关于这首曲子的可靠资料：它写于何时、作曲家当时的处境、"
              "演奏家和研究者通常怎样理解它、它的曲式与关键转折。然后用一段连续的文字（约 800–1200 字）写出这条线本身："
              "这首曲子里那件属于人的事，从头到尾怎样发生、怎样被辨认、怎样被试探和承受、最后留下什么没有解决。"
              "查到的事实可以作为依据写进去，但不要编造史实，也不要把传记当成情节逐条讲；主体是这件事本身的来龙去脉和其中的因果。"
              "只输出这段文字。")

if __name__ == "__main__":
    plan = [("op60", 3), ("op61", 3)]
    jobs = [node2b.job(f"n5a_{w}_r{j}", node2s.base(w, "own") + "\n\n---\n" + RESEARCH_A, {"stage": "n5_spine", "work": w})
            for w, n in plan for j in range(1, n + 1) if not evo.done(f"n5a_{w}_r{j}")]
    print(len(jobs), "spine jobs", flush=True)
    evo.run_parallel(jobs, 6)
    jobs = []
    for w, n in plan:
        for j in range(1, n + 1):
            sp, rid = evo.output(f"n5a_{w}_r{j}"), f"n5_{w}_RS_r{j}"
            if sp and not evo.done(rid):
                jobs.append(node2b.job(rid, node2s.base(w, "own") + "\n\n---\n" + node2s.SPINE_B.replace("{SPINE}", sp),
                                       {"stage": "n5", "variant": "RS", "work": w}))
    print(len(jobs), "thread jobs", flush=True)
    evo.run_parallel(jobs, 6)
