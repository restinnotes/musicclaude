#!/bin/bash
# 10-27 晚：P4e = P4d（转折单独成栏 + 转折带评委标注，池子 P27t）+ "不同原因不合并"规则（挑选和检查都加，SYNTH_CAUSES=1）。
# P4a Op.60 对照包3 的退步：把"对方心意、两人的以后不由他决定"并进了"时间留不住"。与 P4c、P4d 并行。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_TURNS=1 SYNTH_CAUSES=1
until grep -q "op61 S13 turns labeled\|op61 S13 no labels" runs/p4d_tlabel.log 2>/dev/null; do sleep 30; done
for w in op60 op61; do
  ( python synth3.py P4e $w P27t >> runs/p4e_synth_$w.log 2>&1 &&
    python fill3.py P4e $w > runs/p4e_fill_$w.log 2>&1 &&
    python finalize3.py P4e $w > runs/p4e_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P4e_op60/final.json evaluations/synth/P4e_op61/final.json; echo P4E_DONE
