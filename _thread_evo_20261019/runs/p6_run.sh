#!/bin/bash
# 10-28：D22（D21 + 每段写"用什么办法对付感受、起什么作用、什么反作用"，联网）→ 评委覆盖 + 局部机制检查
#        → 池子 P28（P27 的联网稿 + D22，转折和应对各自单独作候选）→ 转折/应对标注 P28t → 起点排名 → P6 接线（P5 的设置）→ 补缺 → 定稿。
cd /d/musicclaude/_thread_evo_20261019
export THREAD_ROUTE=gpt3s PYTHONUNBUFFERED=1
python draft22.py > runs/d22.log 2>&1
python covjudge.py run "d22*" > runs/cov_d22.log 2>&1
python local_check.py $(cd evaluations/draft10; ls d22*_op61_r1.json | sed 's/.json//') > runs/local_d22.log 2>&1
echo D22_JUDGED
python pool4.py P28 op60 > runs/p28_pool_op60.log 2>&1 &
python pool4.py P28 op61 > runs/p28_pool_op61.log 2>&1 &
wait
python tlabel.py P28 P28t > runs/p6_tlabel.log 2>&1 || exit 1
export SYNTH_TURNS=1 SYNTH_FRAME=1
python frame.py P28t > runs/p6_frame.log 2>&1 || exit 1
for w in op60 op61; do
  ( python synth3.py P6 $w P28t >> runs/p6_synth_$w.log 2>&1 &&
    python fill3.py P6 $w > runs/p6_fill_$w.log 2>&1 &&
    python finalize3.py P6 $w > runs/p6_final_$w.log 2>&1 ) &
done
wait
ls evaluations/synth/P6_op60/final.json evaluations/synth/P6_op61/final.json; echo P6_DONE
