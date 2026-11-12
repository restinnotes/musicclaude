"""Node 2 round D15 = D14 with its content leaks removed (10-27). Both judges on the D14 High drafts (Op.61 above all) said
the drafts pressed the whole piece into one continuous "亲近—牵挂—祝愿—幸福" story about a concrete other person, and rewrote
strain, self-doubt, exhaustion and resistance as real joy. D14's rule 7 example ("他第一次希望这种亲近以后还能有") is itself
a Barcarolle-style intimacy story, and rule 11's "有温度" pushes towards warmth. D15: no example (any example leaks a direction), no warmth
demand, one generic rule against smoothing all segments into one story; no feeling words taken from the judges' bead-based feedback (drafting stays bead-free). Same lenses / models as D14.
ids: d15{f|t|s}{6|56}_<work>_r<j>.  usage: THREAD_ROUTE=mimic D14_TAG=d15 python draft15.py"""
import os
os.environ.setdefault("D14_TAG", "d15")
import draft10 as d, draft12 as d12, draft14 as d14, evo

RULES = d14.RULES.replace(
    "（例如“他第一次希望这种亲近以后还能有，可这不是他一个人说了算”）",
    "（不举例：说出前面哪一段里他具体经历了什么）"
).replace("具体、有温度", "具体，像一个人在讲自己的事")
RULES += """
12. 每一段先照实听出这段的感受是什么方向，再找原因；不要为了让全曲连成一个顺的故事，把方向不同的感受改写成同一个方向，也不要把每一段的变化都压进同一条关系故事里。不必给全曲安排一个具体的“另一个人”，除非这一段的感受真的离不开他。"""
assert RULES != d14.RULES and "有温度" not in RULES and "这种亲近以后" not in RULES
d14.P2 = d12.P1.replace("\n从第一段写到最后一段", "\n" + RULES + "\n\n从第一段写到最后一段")

if __name__ == "__main__":
    import sys
    evo.run_parallel(list(d14.cells(set(sys.argv[1:]) or None)), 5 if evo.ROUTE == "mimic" else 1)
