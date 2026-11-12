"""Control D19 (10-27): D12's P1 prompt, byte-identical, written on the Nozomi Pro MimicGate container at Extra High.
D18 (same prompt, yi MimicGate, High, real gpt-6 / gpt-5.6-sol by ModelTrace) scored far below the 10-23 D12 drafts
(gpt4 account, max). D19 separates the thinking-effort question: same prompt, real model, Extra High.
ids: d19{f|t|p|s}{6|56}_<work>_r1.  usage: THREAD_ROUTE=nozomi python draft19.py"""
import os
import draft10 as d, draft17, evo

if __name__ == "__main__":
    assert evo.ROUTE == "nozomi"
    cells = os.environ.get("D19_CELLS", "f6_op61,t6_op61,p6_op61,s6_op61,f6_op60,t6_op60,f56_op61,t56_op61").split(",")
    jobs = []
    for c in cells:
        lm, w = c.split("_"); l, m = lm[0], lm[1:]
        n = f"d19{l}{m}_{w}_r1"
        if not (d.OUT / f"{n}.json").exists():
            jobs.append((n, lambda n=n, w=w, m=m, l=l: draft17.one(n, w, "g6" if m == "6" else "g56", l)))
    print(len(jobs), "drafts:", [n for n, _ in jobs], flush=True)
    evo.run_parallel(jobs, 8)
