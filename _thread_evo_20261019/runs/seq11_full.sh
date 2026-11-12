#!/bin/bash
# 10-28 晚（用户：最后版本应该是 thread 和珠子都是关系图形式结合到一起）：P11 = 不用 T0 + 直接写关系图步子 + 每个感受后跟具体前因 + 原因落在具体对象。
# 两首全量，gpt3 max（同时最多 2 个，runs/gpt3_slots.txt = 2）；写完各做整首对照包3 + 拆开评判（包3 / P9 / P11）。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s SEQ_TAG=11 SEQ_NO_T0=1 SEQ_GRAPH=1 SEQ_CAUSE=1 SEQ_BASE=9 PYTHONUNBUFFERED=1
python seq_repair.py op60 S14 full > runs/seq11_op60_full.log 2>&1 &
python seq_repair.py op61 S13 full > runs/seq11_op61_full.log 2>&1 &
wait
