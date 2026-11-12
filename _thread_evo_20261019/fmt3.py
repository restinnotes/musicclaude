"""F6 = F4 condensation applied to the concrete C1 prose (concrete first, then condensed). ids: fm_F6_<thread>_r<j>"""
import arts, evo, fmt2, node2b, plain
if __name__ == "__main__":
    jobs = []
    for w, ts in plain.THREADS.items():
        for t in ts:
            src = arts.clean(evo.output(f"pc_C1_{t}_r1"))
            for j in (1, 2):
                rid = f"fm_F6_{t}_r{j}"
                if not evo.done(rid):
                    jobs.append(node2b.job(rid, fmt2.F4 + src, {"stage": "fmt3", "variant": "F6", "thread": t}))
    evo.run_parallel(jobs, 4)
