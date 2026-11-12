#!/bin/bash
# 10-28：P5 = P4d（转折单独成栏 + 转折带评委标注，池子 P27t）+ 起点排名（frame.py，评审读全曲珠子给第一段候选排名，不看作者数）
#        + 比喻是感受、不许判听感存疑 + 每段最多 4 条（SYNTH_FRAME=1）。P4a/P4c 对照包3 的主要退步是第一段定歪了主线。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1 SYNTH_TURNS=1 SYNTH_FRAME=1
python frame.py P27t > runs/p5_frame.log 2>&1 || exit 1
for w in op60 op61; do
  ( python synth3.py P5 $w P27t >> runs/p5_synth_$w.log 2>&1 &&
    python fill3.py P5 $w > runs/p5_fill_$w.log 2>&1 &&
    python finalize3.py P5 $w > runs/p5_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P5_op60/final.json evaluations/synth/P5_op61/final.json; echo P5_DONE
