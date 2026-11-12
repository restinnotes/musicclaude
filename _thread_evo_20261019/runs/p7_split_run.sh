#!/bin/bash
# 10-28 晚恢复后：补完 P7（核对、退改、整首对照包3，约 25 次），再跑实验 3 拆开评判（8 次）。同时最多 4 个请求（runs/gpt3_slots.txt）。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1
python repair_line.py > runs/repair_line2.log 2>&1 || exit 1
python split_judge.py > runs/split_judge.log 2>&1
