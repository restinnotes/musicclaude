"""Watchdog for the background P27 / P4a pipeline (10-27, user: a timed check, so a stuck infrastructure does not go
unnoticed). Prints one status block and, when something looks wrong, lines starting with STUCK:
- the pipeline's python processes are gone but runs/p27_done.txt is missing (crashed);
- a gpt3 call has been in flight longer than LIMIT minutes (normal g6 max calls take 10-20 min);
- nothing finished for LIMIT minutes although processes are alive;
- a log shows a Traceback, GPT3 STOPPED or a FAILED call.
usage: python watchdog.py"""
import time
from pathlib import Path
import psutil

ROOT = Path(__file__).parent; R = ROOT / "runs"
PREFIX = ("flP4e_", "fnP4e_", "cv_d22", "lc_d22", "mcE1_", "peE2_", "pcE2_", "pjE2_", "peE2b_", "pcE2b_", "pjE2b_", "d23", "cv_d23", "mcE1_d23", "pe7_", "pc7_", "pe7r_", "pc7r_", "fn7_")       # 10-28 顾问建议后：只剩 P4e 收尾、D22 评分和实验 1–3
LOGS = ["p4e_fill_op60", "p4e_final_op60", "cov_d22", "local_d22", "mech_check", "precise", "precise_bridge", "d23", "cov_d23", "mech_check_d23", "repair_line", "precise_bridge_redo"]
EXPECT_DONE = R / "advisor_20261028" / "experiments_done.txt"
SCRIPTS = ("mech_check.py", "precise.py", "repair_line.py", "draft23.py", "pool4.py", "synth3.py", "fill3.py", "finalize3.py", "tlabel.py", "frame.py", "draft22.py", "covjudge.py", "local_check.py")
LIMIT = 45
now = time.time(); stuck = []

alive = []
for p in psutil.process_iter(["cmdline"]):
    a = p.info["cmdline"] or []
    if len(a) > 1 and "python" in a[0].lower() and a[1].endswith(SCRIPTS):     # not shells whose text names a script
        alive.append(" ".join(a[1:]))
done = (R / "p27_done.txt").exists() or all((ROOT / "evaluations" / "synth" / f"P4a_{w}" / "final.json").exists()
                                           for w in ("op60", "op61"))
done_c = all((ROOT / "evaluations" / "synth" / f"P4c_{w}" / "final.json").exists() for w in ("op60", "op61"))
done_d = all((ROOT / "evaluations" / "synth" / f"P4d_{w}" / "final.json").exists() for w in ("op60", "op61"))
done_e = (ROOT / "evaluations" / "synth" / "P4e_op60" / "final.json").exists()          # P4e Op.61 已停（10-28）
done_6 = all((ROOT / "evaluations" / "synth" / f"P6_{w}" / "final.json").exists() for w in ("op60", "op61"))
done_5 = all((ROOT / "evaluations" / "synth" / f"P5_{w}" / "final.json").exists() for w in ("op60", "op61"))
done_f = all((ROOT / "evaluations" / "synth" / f"P4f_{w}" / "final.json").exists() for w in ("op60", "op61"))
print("进程:", alive or "无", "| 全流程结束:", done, "| P4c 结束:", done_c, "| P4d 结束:", done_d, "| P4e(只 Op.60) 结束:", done_e, "| P4f 结束:", done_f, "| P5 结束:", done_5, "| P6 结束:", done_6)
if not alive and not (EXPECT_DONE.exists()):
    stuck.append("流程进程都不在了，但还没写 p27_done.txt（可能崩了）")

runs = [d for d in R.iterdir() if d.is_dir() and d.name.startswith(PREFIX)]
fin = [d for d in runs if (d / "output.txt").exists()]
fail = [d for d in runs if any(d.glob("call_fail_*.log"))]
open_ = [d for d in runs if (d / "input.txt").exists() and not (d / "output.txt").exists()
         and not any(d.glob("call_fail_*.log"))]
last = max(((d / "output.txt").stat().st_mtime for d in fin), default=0)
print(f"调用: 完成 {len(fin)}，失败过 {len(fail)}，未完成 {len(open_)}；最近一次完成在 {(now - last) / 60:.0f} 分钟前")
for d in open_:
    age = (now - (d / "input.txt").stat().st_mtime) / 60
    if age > LIMIT:
        stuck.append(f"{d.name} 已等 {age:.0f} 分钟")
if alive and fin and (now - last) / 60 > LIMIT:
    stuck.append(f"{LIMIT} 分钟内没有任何调用完成")
try:
    print(f"gpt3 最近一次提交在 {(now - float((R / 'gpt3_last_submit.txt').read_text())) / 60:.0f} 分钟前")
except Exception:
    pass

for n in LOGS:
    f = R / f"{n}.log"
    if not f.exists():
        continue
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    bad = [l for l in lines if "Traceback" in l or "STOPPED" in l or "FAILED" in l or "parse failed" in l]
    print(f"{n}: {len(lines)} 行；最后：{(lines[-1] if lines else '')[:120]}")
    stuck += [f"{n}: {l[:160]}" for l in bad]

for s in stuck:
    print("STUCK:", s)
if not stuck:
    print("正常")
