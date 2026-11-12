#!/bin/bash
# 10-27 晚：对照线 P4b = 同一个池子 P27，挑选和检查都用 5.6（max），看能不能快一倍而质量不降。与 P4a 并行。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_A=g56 SYNTH_B=g56
for w in op60 op61; do
  ( python synth3.py P4b $w P27 >> runs/p4b_synth_$w.log 2>&1 &&
    python fill3.py P4b $w > runs/p4b_fill_$w.log 2>&1 &&
    python finalize3.py P4b $w > runs/p4b_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P4b_op60/final.json evaluations/synth/P4b_op61/final.json; echo P4B_DONE
