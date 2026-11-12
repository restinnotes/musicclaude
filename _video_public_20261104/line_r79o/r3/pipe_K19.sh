#!/bin/bash
# 11-09 傍晚 K19：K11g 上只重组有长小字或偏密的屏（reshape.py），再走路线 B 的验收（绝对验收两遍 + 盲比快筛，都报）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2c PUB_BL_RATE=6.5
python reshape.py g68K11g g68K19 ${1:-g56}
bash r3/pipe_B_K19.sh g68K19 ${1:-g56}
