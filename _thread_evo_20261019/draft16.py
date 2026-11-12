"""Node 2 round D16 (10-27, user: the line must come from bead-free independent drafts alone, or it cannot generalize to
other works). The pool-only line lost to package 3 on local, moment-to-moment mechanisms (a sudden intrusion felt in the
body first, a breath that already senses leaving, holding oneself up making the longing sharper, tiredness changing what
can be felt). D12-style drafts give one feeling and one long-range reason per segment and never write the turns inside a
segment. D16 = D12's P1 (D14's extra rules made the model push one story and flip directions, so they are not used) plus
a turns field: every change inside the segment, sudden or gradual, and why it happens exactly then; the cause may be long
past, may have happened a few bars ago, or may be the body reacting before thought. Nothing piece-specific is added.
ids: d16{f|t|s}{6|56}_<work>_r<j>.  usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python draft16.py [names]"""
import os
import draft10 as d, draft12 as d12, evo, node2b

FIELDS = ('"feel": "这一段最主要的感受，可以有几个侧面，一两句", '
          '"turns": [{"change": "段内的一次变化：先怎样，后来怎样（没有明显变化就写一条“没有明显转折”）", '
          '"how": "突然 / 渐渐", "why_now": "为什么恰好在这时这样变：可能来自很久以前的经历，也可能来自这一段里刚刚发生的事，或者是身体先于念头的反应"}], '
          '"thread": "从前面经历过的事出发，解释这一段整体为什么会这样感受", '
          '"used": "具体依赖了前面哪些经历；没有就写 无", '
          '"new": ["这一段真正建立、以后可能起作用的经历，每条一句；没有就空列表"]')
TURNS = """
7. 一段音乐里的感受常常不是一种状态，而是一个过程：先怎样，后来怎样，中间有一下或几下转折。请写出段内每一次值得注意的转折，说清它是突然发生还是渐渐发生，以及为什么恰好在这时发生。原因不一定来自很久以前：也可能是这一段里刚刚发生的事（刚才的什么让此刻有了变化），也可能是身体先于念头的反应（人还没想明白，身体已经先紧了或先松了）。不要把每个转折都归到同一个长远原因上。
8. “可以这样”“不等于那样”只排除了一种理解，不是此刻这种感受出现的原因。音乐回到熟悉的地方，不等于对方回应了、问题解决了。"""
P3 = d12.P1.replace("\n从第一段写到最后一段", TURNS + "\n\n从第一段写到最后一段").replace(d.FIELDS, FIELDS)
assert TURNS in P3 and '"turns"' in P3
TAG = os.environ.get("D16_TAG", "d16")
WEB = os.environ.get("D16_WEB") == "1"      # 10-27: web search allowed (D21 = D16 with web)


def msg(w, lens):
    segs = d.segs(w)
    bounds = ", ".join(str(s["start"]) for s in segs) + f", {segs[-1]['end'] + 1}"
    return P3.replace("{NAME}", d12.NAME[w]).replace("{BOUNDS}", bounds).replace("{LENS}", d12.LENS[lens])


def flat(x):
    """pool / judges read thread text: the turns go in front of the segment-level reason"""
    ts = [t for t in x.get("turns") or [] if t.get("change") and "没有明显转折" not in t.get("change", "")]
    pre = "".join(f"{t['change']}（{t.get('how', '')}）：{t.get('why_now', '')} " for t in ts)
    return dict(x, thread=(pre + "整体上：" + x.get("thread", "")) if pre else x.get("thread", ""))


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, msg(w, lens), {"stage": TAG, "work": w, "lens": lens, "web": WEB}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [flat(x) | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


def cells(works, lenses, models, only=None):
    for w in works:
        for m in models:
            for lens in lenses:
                name = f"{TAG}{lens}{m}_{w}_r1"
                if (only is None or name in only) and not (d.OUT / f"{name}.json").exists():
                    yield name, (lambda name=name, w=w, mdl=("g6" if m == "6" else "g56"), lens=lens: one(name, w, mdl, lens))


if __name__ == "__main__":
    import sys
    works = os.environ.get("D16_WORKS", "op60,op61").split(","); lenses = os.environ.get("D16_LENSES", "fts")
    evo.run_parallel(list(cells(works, lenses, ("6", "56"), set(sys.argv[1:]) or None)), 10)
