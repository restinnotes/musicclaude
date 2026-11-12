#!/bin/bash
# 10-27 晚：联网稿建池 P27 → 只从池子接线 P4a → 补缺 → 定稿并对照包3（全部走 gpt3）
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1
for w in op60 op61; do
  ( python pool4.py P27 $w > runs/p27_pool_$w.log 2>&1
    python synth3.py P4a $w P27 > runs/p4a_synth_$w.log 2>&1
    python fill3.py P4a $w > runs/p4a_fill_$w.log 2>&1
    python finalize3.py P4a $w > runs/p4a_final_$w.log 2>&1 ) &
done
wait
date > runs/p27_done.txt; echo PIPELINE_DONE
