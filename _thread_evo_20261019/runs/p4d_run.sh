#!/bin/bash
# 10-27 晚：P4d = P4c 的做法 + 转折候选先由评委单独标出能解释哪些珠子（池子 P27t，tlabel.py）。与 P4a、P4c 并行。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_TURNS=1
python tlabel.py > runs/p4d_tlabel.log 2>&1 || exit 1
for w in op60 op61; do
  ( python synth3.py P4d $w P27t >> runs/p4d_synth_$w.log 2>&1 &&
    python fill3.py P4d $w > runs/p4d_fill_$w.log 2>&1 &&
    python finalize3.py P4d $w > runs/p4d_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P4d_op60/final.json evaluations/synth/P4d_op61/final.json; echo P4D_DONE
