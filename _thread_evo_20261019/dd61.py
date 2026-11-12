"""Op.61 line with the doing/dreaming Center (research framing found in 16/24 bead sources; the current Op.61 lines use
exile/belonging). Same N7 method (spine without music/plot, then lay onto segments). Then skeleton + graph v2.
ids: n7a_op61_dd_r<j>, n7_op61_IA_dd_r<j>"""
import evo, node2b, node2i, node2j

if __name__ == "__main__":
    w, s = "op61", "dd61:1"; jobs = []
    for j in (1, 2):
        if not evo.done(f"n7a_op61_dd_r{j}"):
            jobs.append(node2b.job(f"n7a_op61_dd_r{j}", node2i.base(w, s) + "\n\n---\n" + node2j.SPINE, {"stage": "n7_spine", "src": "dd", "work": w}))
    evo.run_parallel(jobs, 2); jobs = []
    for j in (1, 2):
        sp = evo.output(f"n7a_op61_dd_r{j}")
        if sp and not evo.done(f"n7_op61_IA_dd_r{j}"):
            jobs.append(node2b.job(f"n7_op61_IA_dd_r{j}", node2i.base(w, s) + "\n\n---\n" + node2j.LAY.replace("{SPINE}", sp), {"stage": "n7", "src": "dd", "work": w}))
    evo.run_parallel(jobs, 2)
