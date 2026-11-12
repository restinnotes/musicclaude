"""Node 2 round D14 = D12's P1 + causal and plain-language rules (10-26, PLAN_20261026.md step 1). Route: MimicGate web,
Web6 High and Web5.6 High (THREAD_ROUTE=mimic). One call per piece, feel first then why; no score facts, no beads.
New against D12: no pseudo-causes ("更在乎/更有分量/不是从前那个人"), new history = concrete things that happened in him,
"可以/允许/不等于" only rules a reading out, music coming back is not the other person answering; the sentences themselves
will be reused verbatim in the final line, so they must already be plain speech.
ids: d14{f|t|s}{6|56}_<work>_r<j> (Web High via mimicgate); D14_TAG=d14x -> the same prompts at Extra High / max through
the gpt2 chain (THREAD_ROUTE=gpt2), also the High-vs-ExtraHigh comparison (user 10-26).
usage: THREAD_ROUTE=mimic python draft14.py [names]"""
import os
import draft10 as d, draft12 as d12, evo, node2b

RULES = """7. 前因要说到具体。“经历过前面那些，所以现在不一样了”“这份感情有了新的分量”“他更在乎了、更珍惜了”“他已经不是原来的自己”这类话本身不是原因：要说出前面具体发生了什么（例如“他第一次希望这种亲近以后还能有，可这不是他一个人说了算”），以及它为什么让此刻成了这样。说不出来，就照实写这一段只是前面的延续。
8. “可以这样”“不等于那样”“允许……”只排除了一种理解，不是此刻这种感受出现的原因。要写的是它为什么现在真的出现了。
9. 音乐回到熟悉的地方，不等于对方回应了、关系恢复了、问题解决了；音乐变亮、变强，不等于他得到了保证。
10. “新增历史”只写他心里真实发生过、以后真能用上的具体事；“他成熟了”“理解更深了”“更复杂了”不算。
11. 你写下的感受和理由，以后会被原样摘出来给普通听众看。所以每一句都要是能直接念给人听的话，具体、有温度；不要写成“延续需要”“安顿”“承托”“投入”这类概括词，也不要写成分析报告。"""
P2 = d12.P1.replace("\n从第一段写到最后一段", "\n" + RULES + "\n\n从第一段写到最后一段")
assert P2 != d12.P1
LENSES = ("f", "t", "s")
TAG = os.environ.get("D14_TAG", "d14")


def msg(w, lens):
    segs = d.segs(w)
    bounds = ", ".join(str(s["start"]) for s in segs) + f", {segs[-1]['end'] + 1}"
    return P2.replace("{NAME}", d12.NAME[w]).replace("{BOUNDS}", bounds).replace("{LENS}", d12.LENS[lens])


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, msg(w, lens), {"stage": "d14", "work": w, "lens": lens}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [x | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


def cells(only=None):
    for w in d.W:
        for m in ("6", "56"):
            for lens in LENSES:
                name = f"{TAG}{lens}{m}_{w}_r1"
                if (only is None or name in only) and not (d.OUT / f"{name}.json").exists():
                    yield name, (lambda name=name, w=w, mdl=("g6" if m == "6" else "g56"), lens=lens: one(name, w, mdl, lens))


if __name__ == "__main__":
    import sys
    evo.run_parallel(list(cells(set(sys.argv[1:]) or None)), 5 if evo.ROUTE == "mimic" else 1)
