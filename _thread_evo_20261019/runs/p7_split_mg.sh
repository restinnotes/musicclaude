#!/bin/bash
# 10-28 晚：gpt3 账号被拦，用户：用 mimicgate High 续跑。补完 P7（4 段退改、8 段复核、整首对照包3）→ 评委校准（P4d 原题重判 4 次）→ 实验 3（8 次）。
# 同时最多 3 个、提交间隔 ≥20 s；任何一步出现 MIMIC STOPPED 就整条停下，不再开下一步。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=mimic MG_SLOTS=3 PYTHONUNBUFFERED=1
python repair_line.py > runs/repair_line3.log 2>&1 || exit 1
grep -q "MIMIC STOPPED" runs/repair_line3.log && exit 2
python calib_mg.py > runs/calib_mg.log 2>&1 || exit 1
grep -q "MIMIC STOPPED" runs/calib_mg.log && exit 2
python split_judge.py > runs/split_judge.log 2>&1
