"""10-28: the rest of P7 and experiment 3 move from gpt3 max to MimicGate High (gpt3 account blocked). recheck_p3a showed
High checks are looser than gpt3 max (8 segments passed on High, 3 of them on max), so before trusting High's "不差于包3"
the same regression prompt that gpt3 max answered for P4d (both judges said 实质退步) is sent unchanged to High.
High also says 退步 -> its P7 verdicts can be read next to the gpt3 ones; High says 不差于 -> it is too lenient for this.
ids: cal_fnP4d_<work>_R_<judge>.  usage: THREAD_ROUTE=mimic python calib_mg.py"""
import evo, node2b

PAIRS = [(w, j) for w in ("op60", "op61") for j in ("g6", "g56")]


def main():
    jobs = []
    for w, j in PAIRS:
        rid = f"cal_fnP4d_{w}_R_{j}"
        if not evo.done(rid):
            msg = (evo.RUNS / f"fnP4d_{w}_R_{j}" / "input.txt").read_text(encoding="utf-8")
            jobs.append(node2b.job(rid, msg, {"stage": "calib-R"}, w=j))
    evo.run_parallel(jobs, 4)
    for w, j in PAIRS:
        old, new = (evo.parse_json(evo.output(r)) or {} for r in (f"fnP4d_{w}_R_{j}", f"cal_fnP4d_{w}_R_{j}"))
        print(f"{w} {j}: gpt3 max {old.get('verdict')} | MimicGate High {new.get('verdict')}", flush=True)


if __name__ == "__main__":
    main()
