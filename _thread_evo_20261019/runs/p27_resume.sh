#!/bin/bash
# 10-27 晚：回退提示词超长修好后重启 P4a（已完成的调用直接复用）。每一步成功才进下一步，崩了就停在那一步。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1
for w in op60 op61; do
  ( python synth3.py P4a $w P27 >> runs/p4a_synth_$w.log 2>&1 &&
    python fill3.py P4a $w > runs/p4a_fill_$w.log 2>&1 &&
    python finalize3.py P4a $w > runs/p4a_final_$w.log 2>&1 ) &
done
wait
# 看门狗以两首的 final.json 是否都在来判断结束；缺一个就说明有一步崩了
ls evaluations/synth/P4a_op60/final.json evaluations/synth/P4a_op61/final.json; echo PIPELINE_DONE
