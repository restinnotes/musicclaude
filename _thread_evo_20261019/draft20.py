"""D20 (10-27): D12's P1 prompt, byte-identical to what was sent on 10-23 — no "不要联网搜索" line, the model may search
the web. Calibration found that 27 of the 32 10-23 D12 drafts had called web.run, while every draft since 10-24 carried
the NO_WEB suffix; the 10-23 drafts without a search score like today's. The user: web search is of course allowed.
D20 checks that web-enabled drafts on today's route come back to the 10-23 level.
ids: d20{f|t|p|s}{6|56}_<work>_r1.  usage: THREAD_ROUTE=gpt3s python draft20.py"""
import os
import draft10 as d, draft12 as d12, evo, node2b


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, d12.msg(w, lens), {"stage": "d20-web", "work": w, "lens": lens, "web": True}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [x | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


if __name__ == "__main__":
    cells = os.environ.get("D20_CELLS", "f6_op61,t6_op61,p6_op61,s6_op61,f6_op60,t6_op60,f56_op61,t56_op61").split(",")
    jobs = []
    for c in cells:
        lm, w = c.split("_"); l, m = lm[0], lm[1:]
        n = f"d20{l}{m}_{w}_r1"
        if not (d.OUT / f"{n}.json").exists():
            jobs.append((n, lambda n=n, w=w, m=m, l=l: one(n, w, "g6" if m == "6" else "g56", l)))
    print(len(jobs), "drafts:", [n for n, _ in jobs], flush=True)
    evo.run_parallel(jobs, 8)
