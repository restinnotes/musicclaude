"""Control D18 (10-27): D12's P1 prompt, byte-identical, written through MimicGate (High). ModelTrace on 10-27 put
every gpt3 answer (gpt-6-thinking and gpt-5-6-thinking alike) at gpt-6-luna, while MimicGate answers matched gpt-6-sol /
gpt-5.6-sol; so all of today's gpt3-written gpt-6 drafts (D14x, D16/D17 g6) came from a smaller model. D18 asks whether
genuine models at High write like the 10-23 D12 drafts (gpt4 account, max). The first two (op61 f/t, gpt-6) scored far
below D12, so D18 is widened to every lens, both works and both models (d17{f|t}56_op61 already are the same cell).
ids: d18{f|t|p|s}{6|56}_<work>_r1.  usage: THREAD_ROUTE=mimic python draft18.py"""
import os
import draft10 as d, draft17, evo

if __name__ == "__main__":
    assert evo.ROUTE == "mimic"
    jobs = []
    for w in os.environ.get("D18_WORKS", "op61,op60").split(","):
        for m in os.environ.get("D18_MODELS", "6,56").split(","):
            for l in os.environ.get("D18_LENSES", "ftps"):
                n = f"d18{l}{m}_{w}_r1"
                if (d.OUT / f"{n}.json").exists() or (m == "56" and w == "op61" and l in "ft"):
                    continue
                jobs.append((n, lambda n=n, w=w, m=m, l=l: draft17.one(n, w, "g6" if m == "6" else "g56", l)))
    print(len(jobs), "drafts:", [n for n, _ in jobs], flush=True)
    evo.run_parallel(jobs, 5)
