"""Remaining production steps, run as one detached process (survives app restarts; every step is cached/resumable).
S10 gen_b -> rev2_b -> final_b ; piece_b over all 13 final_b ; final2_b for segments the piece check flags ; build."""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sat  # noqa: E402


def main():
    sat.run(["pool", "gen_b", "rev1_b", "rev2_b", "final_b"], list(sat.SEGS))
    missing = [s for s in sat.SEGS if not sat.done("final_b", s)]
    if missing:
        print("STOP: final_b missing", missing, flush=True); return
    if not sat.load("piece_b", "ALL"):
        if sat.blocked("piece_b", "ALL"):
            print("STOP: piece_b uncertain/parse error", flush=True); return
        sat.t_piece("final_b", "piece_b")
    if not sat.load("piece_b", "ALL"):
        print("STOP: piece_b failed", flush=True); return
    fl = [s for s in sat.SEGS if sat.needs_fix(s, "piece_b")]
    print("piece_b flags:", fl, flush=True)
    (ROOT / "runs" / "piece_b_flags.txt").write_text(",".join(fl), encoding="utf-8")
    if fl:
        sat.run(["final2_b"], fl)
    subprocess.run([sys.executable, str(ROOT / "build_op61.py")], cwd=ROOT)
    print("FINISHED", flush=True)


if __name__ == "__main__":
    main()
