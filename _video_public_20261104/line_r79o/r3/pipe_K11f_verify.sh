#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1 PUB_VS3B=1
python vs2.py g68K11f w23 &
python r3/openabs.py g68K11f run3 run4 &
wait
python r3/openabs.py g68K11f run1 run2 run3 run4 | grep 绝对验收
echo "== K11f 复核完 $(date)"
