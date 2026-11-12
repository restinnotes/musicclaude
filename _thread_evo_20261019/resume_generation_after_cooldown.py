"""One delayed retry of the two current generation jobs after the shared cooldown.

This is a bounded continuation job, not a watchdog: it exits after both commands.
It reuses completed run IDs and never changes prompts or model settings.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import mg_schedule

ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "runs" / "continuation_20261102_generation"


def save(**fields):
    FOLDER.mkdir(exist_ok=True)
    path = FOLDER / "state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.update(pid=os.getpid(), updated_utc=datetime.now(timezone.utc).isoformat(), **fields)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run(scheme, tag, measurement=False):
    mg_schedule.check()
    env = {**os.environ, "THREAD_ROUTE": "mimic", "MG_GLOBAL": "2", "MG_SLOTS": "2", "MG_ATTEMPTS": "1", "REF": "qu"}
    if measurement:
        env["SCREEN_BLIND_FIRST"] = "1"
    label = f"measure_{tag}" if measurement else tag
    logpath = FOLDER / f"{label}.log"
    command = (["measure_candidates_20261102.py", tag, "--base", "qu"] if measurement
               else ["pipe.py", "run", f"schemes/{scheme}.json", tag])
    with logpath.open("a", encoding="utf-8") as log:
        process = subprocess.run([sys.executable, "-u", *command],
                                 cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    print(label, "exit", process.returncode, flush=True)
    return {"tag": tag, "measurement": measurement, "exit_code": process.returncode, "log": str(logpath)}


def main(measure_tag=None, serial_recovery=False, measure_first=False):
    # The lock is held for the bounded timer and its children, avoiding duplicate timers.
    import msvcrt
    FOLDER.mkdir(exist_ok=True)
    with (FOLDER / "owner.lock").open("a+b") as lock:
        if lock.seek(0, 2) == 0:
            lock.write(b"\0")
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            raise SystemExit("已有接续任务持有锁，不重复启动")
        while True:
            state = mg_schedule.status()
            remaining = state.get("cooldown_until", 0) - time.time()
            if remaining <= 0:
                break
            save(stage="cooling", resume_after_utc=state["resume_after_utc"], failed_run=state.get("failed_run"))
            time.sleep(min(remaining, 30))
        jobs = [(name, tag, False) for name, tag in (("R26T2", "r26t2"), ("R26G3", "r26g3"))
                if not all((ROOT / "evaluations" / "v6fix" / f"{work}_{tag}.json").exists()
                           for work in ("op60", "op61"))]
        if measure_tag:
            jobs.append((None, measure_tag, True))
        if measure_first:
            jobs.sort(key=lambda job: not job[2])
        save(stage="generating", commands=[("measure/" if measure else f"{name}/") + tag
                                           for name, tag, measure in jobs], results=[])
        print("冷却结束，补失败和未提交的步骤，完整返回复用", flush=True)
        if serial_recovery:
            # Current recovery has only one missing G3 generation call. Complete
            # that actual task before starting the previously reviewed T2 screen.
            results = []
            for job in jobs:
                result = run(*job)
                results.append(result)
                if result["exit_code"]:
                    break
        else:
            with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as pool:
                futures = [pool.submit(run, *job) for job in jobs]
                results = [future.result() for future in futures]
        save(stage="finished", results=results)
        if any(result["exit_code"] for result in results):
            raise SystemExit("至少一套未完成；保留结果，按共享冷却状态继续，不自动立即重试")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", choices=("r26t2",), help="恢复已通读双曲候选的快筛；先确认旧测量父进程已退出")
    parser.add_argument("--serial-recovery", action="store_true", help="先补生成，成功后才恢复测量；任一阶段失败即结束本轮")
    parser.add_argument("--measure-first", action="store_true", help="先判断已有成品，避免另一候选的生成阻塞评审")
    args = parser.parse_args()
    main(args.measure, args.serial_recovery, args.measure_first)
