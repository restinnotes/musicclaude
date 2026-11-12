#!/bin/bash
# 10-28 晚：P8 小测试过关后扩到两首全部（Op.60 接着 S08–S14，Op.61 S01–S13，Center 写完再回头写），然后整首对照包3 + 拆开评判。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=mimic MG_SLOTS=2 MG_ATTEMPTS=2 PYTHONUNBUFFERED=1
SEQ_G56=S06 python seq_repair.py op60 S14 full > runs/seq8_op60_full.log 2>&1 &
SEQ_FREE=op61 python seq_repair.py op61 S13 full > runs/seq8_op61_full.log 2>&1 &
wait
