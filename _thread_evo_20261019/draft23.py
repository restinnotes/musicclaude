"""D23 (10-28) = D22 with coping optional. Experiment 1: D22 raised the coping-type mechanisms (Op.60 2/4, Op.61 1) but the
forced per-segment field made mechanical "try - fail - switch" loops jump from 8/17 to 67/72 and lost the non-coping
ones (sudden intrusion, tiredness turning into drive). D23: write coping only where he really is coping (most segments he
is not), at most one, and never as a chain of strategies.

Old D22 doc:
D22 (10-28): D21 (D16's in-segment turns + web) plus a coping field. P4a/P4c/P4d all lost to package 3 on the same
kind of mechanism: what he does to cope with a feeling, and how that coping changes the feeling in turn (holding on
harder that makes the longing sharper, questions that cannot close the distance yet keep coming, comfort fading and
then finding he can still be glad alone). Those were written with the beads in view; no draft prompt ever asked for
coping, so the pool never had them. The rule's examples are generic and taken from neither piece. Beads unseen.
Coping items join the pool as their own candidates (src "#c", treated like turns).
ids: d23{f|t|p|s}{6|56}_<work>_r1.  usage: THREAD_ROUTE=gpt3s python draft23.py"""
import os
import draft10 as d, draft12 as d12, draft16 as d16, evo, node2b

COPE_FIELD = ('"cope": [{"how": "他此刻确实在用什么办法对付这份感受（撑着、追问、抓紧、躲开……）；大多数段落没有，就写“没有在对付”", '
              '"effect": "这个办法起了什么作用", '
              '"backfire": "它反过来怎样改变了感受，带来什么代价或新的感受（常常是“越……越……”）；没有就写 无"}], ')
FIELDS = d16.FIELDS.replace('"thread": "从前面经历过的事出发', COPE_FIELD + '"thread": "从前面经历过的事出发', 1)
COPE_RULE = """
9. 人面对一种感受时，有时会做点什么来对付它，而这个办法本身又会反过来改变感受：越想忘记，越常想起；越想证明自己没事，越累；一个暂时的安慰退去以后，也可能意外发现自己还剩下别的力量。只有在这一段他确实在对付这份感受时才写，最多写一条；大多数段落他并没有在“对付”什么，只是在感受，那就写“没有在对付”。不要写成“试一个办法—失败—换一个办法”的循环，也不要为了交代应对而编出策略的更替：一个办法起了作用、又带来反作用，这本身就够了。"""
P22 = d16.P3.replace(d16.FIELDS, FIELDS).replace(d16.TURNS, d16.TURNS + COPE_RULE)
assert COPE_RULE in P22 and '"cope"' in P22


def msg(w, lens):
    segs = d.segs(w)
    bounds = ", ".join(str(s["start"]) for s in segs) + f", {segs[-1]['end'] + 1}"
    return P22.replace("{NAME}", d12.NAME[w]).replace("{BOUNDS}", bounds).replace("{LENS}", d12.LENS[lens])


def cope_items(x):
    return [c for c in x.get("cope") or [] if c.get("how") and "没有在对付" not in c.get("how", "")]


def flat(x):
    """judges read: turns, then coping, then the segment-level reason"""
    y = d16.flat(x)
    cs = cope_items(x)
    if not cs:
        return y
    pre = "".join(f"他用{c['how']}来对付：{c.get('effect', '')}；反过来{c.get('backfire', '')} " for c in cs)
    th = y["thread"]
    return dict(y, thread=th.replace("整体上：", pre + "整体上：", 1) if "整体上：" in th else pre + "整体上：" + th)


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, msg(w, lens), {"stage": "d23", "work": w, "lens": lens, "web": True}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [flat(x) | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


if __name__ == "__main__":
    jobs = []
    for w in ("op60", "op61"):
        for m in ("6", "56"):
            for lens in os.environ.get("D22_LENSES", "ftps"):
                n = f"d23{lens}{m}_{w}_r1"
                if not (d.OUT / f"{n}.json").exists():
                    jobs.append((n, lambda n=n, w=w, m=m, lens=lens: one(n, w, "g6" if m == "6" else "g56", lens)))
    print(len(jobs), "drafts", flush=True)
    evo.run_parallel(jobs, 16)
