"""Plain rewrite, made concrete (user 10-21: dislikes abstract words like 站稳).
  C1: PL + "把抽象的词换成他具体在想什么、怕什么、想要什么，像对朋友讲这件事"
  C2: C1 + three generic before/after examples (not from this piece)
  C3: C1 + a list of words to avoid
run ids: pc_<C1|C2|C3>_<thread>_r<j>.  Also: python concrete.py density <glob>... prints abstract-word density per 1000 chars.
"""
import re, sys, glob
import arts, evo, node2b, plain

ABSTRACT = ["站稳", "立足", "挺直", "安顿", "承受", "承担", "敞开", "托住", "悬着", "落定", "归属", "边界", "限度", "代价",
            "空缺", "位置", "意义", "回应", "辨认", "姿态", "确认", "完整", "真实", "价值", "并不等于", "不等于", "正因为"]
BASE = "用人话简单地重写下面这篇文章，不损失内容，全文约 {N} 字。保留原来的分段标题。"
C1 = BASE + ("把抽象的词换成这个人具体在想什么、怕什么、想要什么、在做什么，像他在对一个朋友讲自己这件事；"
             "读者读完每一句，都应该能说出他此刻心里具体是怎么回事。")
EX = ("\n\n改写方向的例子（只示范方向，和这篇无关）：\n"
      "- “他在亲密中获得了安顿，却也看见了它的边界。” → “和她在一起时他终于能睡个好觉了；可他也发现，有些话他还是不敢跟她说。”\n"
      "- “他试图以坚定的姿态承担这份失去。” → “他告诉自己不能垮，照常上班，照常见人，谁问起都说没事。”\n"
      "- “满足没有消除空缺，反而使它更加清晰。” → “该有的都有了，他却还是半夜醒来，想不通自己到底还缺什么。”")
AVOID = ("\n\n尽量不用这类词：" + "、".join(ABSTRACT[:20]) + "。如果非用不可，紧接着说清它具体指什么。")
TAIL = "只输出重写后的文章。\n\n"
VAR = {"C1": C1 + TAIL, "C2": C1 + EX + "\n\n" + TAIL, "C3": C1 + AVOID + "\n\n" + TAIL}


def density(t):
    return 1000 * sum(t.count(w) for w in ABSTRACT) / max(1, len(t))


if __name__ == "__main__":
    if sys.argv[1:2] == ["density"]:
        for pat in sys.argv[2:]:
            for d in sorted(glob.glob(f"runs/{pat}")):
                n = d.replace("\\", "/").split("/")[-1]; t = arts.clean(evo.output(n) or "")
                print(f"{n:40s} chars {len(t):5d}  abstract/1000 {density(t):5.1f}")
        sys.exit()
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(t))
            for v, tpl in VAR.items():
                for j in (1, 2):
                    rid = f"pc_{v}_{t}_r{j}"
                    if not evo.done(rid):
                        jobs.append(node2b.job(rid, tpl.replace("{N}", str(plain.N[w])) + src, {"stage": "concrete", "variant": v, "thread": t, "work": w}))
    print(len(jobs), "jobs", flush=True)
    evo.run_parallel(jobs, 4)
