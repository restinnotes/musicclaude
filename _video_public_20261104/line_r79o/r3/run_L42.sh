#!/bin/bash
# 11-12 夜：跑一套骨架方案到“骨架检查 + 线的互换测试”，不写屏幕稿（先只看骨架，过了再往下）。bash r3/run_L42.sh ID（g561、g562、g61、g62、pool）
cd /d/musicclaude/_video_public_20261104/line_r79o; ID=$1
for try in 1 2; do
  (cd /d/musicclaude/_thread_evo_20261019 && python pipe.py run schemes/L42$ID.json L42$ID 2>&1 | grep -v "^\[" | tail -3)
  PUB_SRC=r2e python r3/fromdag.py L42$ID r2L42$ID && break
done
[ -f r2L42$ID/op60_src.json ] && [ -f r2L42$ID/op61_src.json ] || { echo "== L42$ID 线没出来"; exit 1; }
python r3/swaptest.py r2L42$ID > r3/s24/swap_r2L42$ID.log 2>&1 &
python r3/skcheck.py L42$ID=run:L42$ID 2>&1 | grep -v "^\[" | cut -c1-500
wait; grep "猜对 " r3/s24/swap_r2L42$ID.log
echo "== L42$ID 做完 $(date)"
