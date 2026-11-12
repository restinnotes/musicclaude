#!/bin/bash
# 10-27 晚：P4c = 同一池子 P27，挑选时转折候选单独成栏、必须看、讲清"此刻为什么"的转折和整段解释并存（SYNTH_TURNS=1）。
# P4a 里转折占池子约四成却只被选中 3 次。gpt-6 挑选、5.6 检查，与 P4a 相同。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_TURNS=1
for w in op60 op61; do
  ( python synth3.py P4c $w P27 >> runs/p4c_synth_$w.log 2>&1 &&
    python fill3.py P4c $w > runs/p4c_fill_$w.log 2>&1 &&
    python finalize3.py P4c $w > runs/p4c_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P4c_op60/final.json evaluations/synth/P4c_op61/final.json; echo P4C_DONE
