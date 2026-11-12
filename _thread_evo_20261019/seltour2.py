"""Accepted Centers (center_v3 round 3, self-accepted: form + content tests) -> N7 lines (2 each) -> judge_spec_v2
-> best line per Center -> P0 graph + concise view. Number of Centers per work = entries in sel_<w>.json.
ids: n7a_/n7_<w>_IA_c3<k>_r<j>; judging evals C3<60|61>.
usage: python seltour2.py lines | judge | graphs"""
import json, subprocess, sys
from collections import defaultdict
from statistics import mean
import arts, evo, node2b, node2i, node2j, skeleton, stateinc, tgraph2, tg_winners

W = ("op60", "op61")


def centers(w):
    return json.loads((evo.ROOT / "evaluations" / "centers" / f"sel_{w}.json").read_text(encoding="utf-8"))


def ids(w):
    return [f"n7_{w}_IA_c3{k}_r{j}" for k in range(1, len(centers(w)) + 1) for j in (1, 2)]


if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "lines":
        jobs = [node2b.job(f"n7a_{w}_c3{k}_r{j}", node2i.base(w, f"sel_{w}:{k}") + "\n\n---\n" + node2j.SPINE, {"stage": "n7_spine", "src": f"c3{k}"})
                for w in W for k in range(1, len(centers(w)) + 1) for j in (1, 2) if not evo.done(f"n7a_{w}_c3{k}_r{j}")]
        evo.run_parallel(jobs, 6); jobs = []
        for w in W:
            for k in range(1, len(centers(w)) + 1):
                for j in (1, 2):
                    sp = evo.output(f"n7a_{w}_c3{k}_r{j}")
                    if sp and not evo.done(f"n7_{w}_IA_c3{k}_r{j}"):
                        jobs.append(node2b.job(f"n7_{w}_IA_c3{k}_r{j}", node2i.base(w, f"sel_{w}:{k}") + "\n\n---\n" + node2j.LAY.replace("{SPINE}", sp),
                                               {"stage": "n7", "src": f"c3{k}"}))
        evo.run_parallel(jobs, 6)
    elif ph == "judge":
        for w, anchor in (("op60", "n6_op60_IB_own_r1"), ("op61", "n6_op61_IA_rs_r2")):
            names = [n for n in ids(w) if evo.done(n)]
            subprocess.run([sys.executable, "mkplan.py", f"C3{w[2:]}", anchor, str(min(3, len(names))), ",".join(names)], check=True)
        procs = [subprocess.Popen([sys.executable, "-u", "calib.py", f"C3{w[2:]}", w, "x", "--judge", "judge_spec_v2", "--workers", "4"],
                                  stdout=open(evo.RUNS / f"C3{w[2:]}.log", "w"), stderr=subprocess.STDOUT) for w in W]
        for p in procs:
            p.wait()
    elif ph == "graphs":
        best = {}
        for w in W:
            rows = json.loads((evo.ROOT / "evaluations" / f"C3{w[2:]}" / "rows.json").read_text(encoding="utf-8")); by = defaultdict(list)
            for r in rows:
                try:
                    by[r["name"]].append(float(r["overall"]))
                except Exception:
                    pass
            for k in range(1, len(centers(w)) + 1):
                c = [n for n in by if f"_c3{k}_" in n]
                if c:
                    best[(w, k)] = max(c, key=lambda n: mean(by[n]))
        print({f"{w}:{k}": (n, round(mean(by_n), 2)) for (w, k), n in best.items() for by_n in [[0]]}, flush=True)
        jobs = [(f"sk_{t}", (lambda t=t: evo.call(f"sk_{t}", skeleton.SK + arts.clean(evo.output(t)), prompt_text=skeleton.SK, meta={"stage": "skeleton"})))
                for (w, k), t in best.items() if not evo.done(f"sk_{t}")]
        evo.run_parallel(jobs, 6); jobs = []
        for (w, k), t in best.items():
            (skeleton.OUT / f"{t}.json").write_text(json.dumps(evo.parse_json(evo.output(f"sk_{t}")), ensure_ascii=False, indent=1), encoding="utf-8")
            msg = stateinc.fill(tgraph2.P, w) + "========== 原稿 ==========\n" + arts.clean(evo.output(t)) + "\n\n========== 骨架 ==========\n" + (skeleton.OUT / f"{t}.json").read_text(encoding="utf-8")
            if not evo.done(f"tg2_{t}_r1"):
                jobs.append(node2b.job(f"tg2_{t}_r1", msg, {"stage": "tgraph2", "thread": t}))
        evo.run_parallel(jobs, 6)
        for (w, k), t in best.items():
            if evo.done(f"tg2_{t}_r1"):
                tgraph2.save(f"tg2_{t}_r1", w)
                j = json.loads((tgraph2.OUT / f"tg2_{t}_r1.json").read_text(encoding="utf-8"))
                cl = centers(w)[k - 1]["center"]
                v = tg_winners.view(j, f"{'Op.60' if w == 'op60' else 'Op.61'}｜Center：{cl}", cl)
                (tgraph2.OUT / f"tg2_{t}_r1_view.md").write_text(v, encoding="utf-8"); print("view", t, len(v), flush=True)
