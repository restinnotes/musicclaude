#!/bin/bash
# 11-09 K13 = K11g + 长感受块加锚点（不删不改字）：对 K11g 盲比 + 绝对验收四遍
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1 PUB_VS3B=1
python vs2.py g68K13 g68K11g &
python r3/openabs.py g68K13 run1 run2 run3 run4 &
wait
python r3/openabs.py g68K13 run1 run2 run3 run4 | grep 绝对验收
echo "== K13 测完 $(date)"
