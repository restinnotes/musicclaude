"""Control D17 (10-27): D12's P1 prompt, byte-identical, rewritten on today's routes (gpt3 = yi account max for Web6,
MimicGate High for 5.6). D14/D15/D16 (all written today on the yi account) explain far fewer beads and get far more 相反
than D12 (written 10-23 on the gpt4 account). If D17 drops the same way, the cause is the route/model state, not the prompt.
ids: d17{f|t}{6|56}_<work>_r1.  usage: THREAD_ROUTE=gpt3s THREAD_ROUTE_G56=mimic python draft17.py"""
import os
import draft10 as d, draft12 as d12, evo, node2b


def one(name, w, mdl, lens):
    for rid in (name, name + "_x"):
        if not evo.done(rid):
            node2b.job(rid, d12.msg(w, lens), {"stage": "d17-control", "work": w, "lens": lens}, w=mdl)[1]()
        r = d.parse(rid) if evo.done(rid) else None
        xs = (r or {}).get("sections") or []
        if len(xs) == len(d.segs(w)) and all(x.get("thread") for x in xs):
            return d.save(name, [x | {"sec": s["id"], "bars": f"{s['start']}–{s['end']}"} for x, s in zip(xs, d.segs(w))])
    print(name, "FAILED (sections != segments)", flush=True)


if __name__ == "__main__":
    w = os.environ.get("D17_WORK", "op61")
    jobs = [(f"d17{l}{m}_{w}_r1", lambda l=l, m=m: one(f"d17{l}{m}_{w}_r1", w, "g6" if m == "6" else "g56", l))
            for l in "ft" for m in ("6", "56") if not (d.OUT / f"d17{l}{m}_{w}_r1.json").exists()]
    evo.run_parallel(jobs, 4)
