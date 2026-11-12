#!/bin/bash
# 10-28：P4f = P4e 的做法，"不同原因不合并"改成只看本段听感本身判断原因（P4e Op.61 把用力、抗拒说成和那个人有关，B1 空了 2 颗）。
# P4a Op.60 对照包3 的退步：把"对方心意、两人的以后不由他决定"并进了"时间留不住"。与 P4c、P4d 并行。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_TURNS=1 SYNTH_CAUSES=1
for w in op60 op61; do
  ( python synth3.py P4f $w P27t >> runs/p4f_synth_$w.log 2>&1 &&
    python fill3.py P4f $w > runs/p4f_fill_$w.log 2>&1 &&
    python finalize3.py P4f $w > runs/p4f_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P4f_op60/final.json evaluations/synth/P4f_op61/final.json; echo P4E_DONE
