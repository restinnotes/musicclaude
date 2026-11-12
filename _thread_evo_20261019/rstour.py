"""Route A Center tournament with research Centers (rs_<work>.json, 6 each) + Op.61 doing/dreaming (dd61).
Each Center -> one N7 line (spine without music/plot, then lay). Judged with judge_spec_v2 in blocks of 3 + an anchor line.
ids: n7a_<w>_rs<k>_r1 / n7_<w>_IA_rs<k>_r1 ; judging evals RT60 / RT61"""
import evo, node2b, node2i, node2j

if __name__ == "__main__":
    jobs = []
    for w in ("op60", "op61"):
        for k in range(1, 7):
            if not evo.done(f"n7a_{w}_rs{k}_r1"):
                jobs.append(node2b.job(f"n7a_{w}_rs{k}_r1", node2i.base(w, f"rs_{w}:{k}") + "\n\n---\n" + node2j.SPINE, {"stage": "n7_spine", "src": f"rs{k}", "work": w}))
    evo.run_parallel(jobs, 4); jobs = []
    for w in ("op60", "op61"):
        for k in range(1, 7):
            sp = evo.output(f"n7a_{w}_rs{k}_r1")
            if sp and not evo.done(f"n7_{w}_IA_rs{k}_r1"):
                jobs.append(node2b.job(f"n7_{w}_IA_rs{k}_r1", node2i.base(w, f"rs_{w}:{k}") + "\n\n---\n" + node2j.LAY.replace("{SPINE}", sp), {"stage": "n7", "src": f"rs{k}", "work": w}))
    evo.run_parallel(jobs, 4)
