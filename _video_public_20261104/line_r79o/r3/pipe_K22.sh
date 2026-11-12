#!/bin/bash
# 11-09 晚 K22：I02 两位顾问的四套方案（adv_k22），写手都用 GPT-6，只差提示词。只写，不测；我先读一屏再决定测不测（I04a）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_BL_PFX=k22
# 只改写稿（原料 r2c）
( PUB_SRC=r2c PUB_BL_PROMPT=prompt_K22_g56_P1_screen.txt python blend.py g68K22a g6 > r3/K22a_write.log 2>&1 ) &
( PUB_SRC=r2c PUB_BL_PROMPT=prompt_K22_g6_P2_screen.txt  python blend.py g68K22d g6 > r3/K22d_write.log 2>&1 ) &
# 先改线再写稿
( PUB_SRC=r2c python r3/reline_k22.py r2k22b prompt_K22_g56_P2_line.txt prompt_K22_g56_P2_map.txt g6 > r3/K22b_line.log 2>&1 && \
  PUB_SRC=r2k22b PUB_BL_PROMPT=prompt_K22_g56_P2_screen.txt python blend.py g68K22b g6 > r3/K22b_write.log 2>&1 ) &
( PUB_SRC=r2c python r3/reline_k22.py r2k22c prompt_K22_g6_P1_line.txt prompt_K22_g6_P1_map.txt g6 > r3/K22c_line.log 2>&1 && \
  PUB_SRC=r2k22c PUB_BL_PROMPT=prompt_K22_g6_P1_screen.txt python blend.py g68K22c g6 > r3/K22c_write.log 2>&1 ) &
wait
echo "== K22 写完 $(date)"
