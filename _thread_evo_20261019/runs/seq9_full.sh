#!/bin/bash
# 10-28 晚：P9（不用 T0）扩到两首全部；Center 写完再回头写；整首对照包3 + 拆开评判（包3 / P8 / P9）。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=mimic MG_SLOTS=2 MG_ATTEMPTS=2 SEQ_TAG=9 SEQ_NO_T0=1 PYTHONUNBUFFERED=1
python seq_repair.py op60 S14 full > runs/seq9_op60_full.log 2>&1 &
python seq_repair.py op61 S13 full > runs/seq9_op61_full.log 2>&1 &
wait
