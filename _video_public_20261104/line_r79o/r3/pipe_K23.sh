#!/bin/bash
# 11-09 晚 K23 = K22 交回提出者后的第 1 次修订（adv_k22r）。只走两层方案（两位都判只改写稿“不行”）。
# 端到端对照：同一份写稿提示词各跑新线和原线 r2c（K23b0、K23c0），两份只差线，作为 DAG 改动的证据。写完先过机械预检，不测。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_BL_PFX=k23
( PUB_SRC=r2c python r3/reline_k22.py r2k23b prompt_K22r_g56_P2_line.txt prompt_K22r_g56_P2_map.txt g6 > r3/K23b_line.log 2>&1 && \
  PUB_SRC=r2k23b PUB_BL_PROMPT=prompt_K22r_g56_P2_screen.txt python blend.py g68K23b g6 > r3/K23b_write.log 2>&1 ) &
( PUB_SRC=r2c python r3/reline_k22.py r2k23c prompt_K22r_g6_P1_line.txt prompt_K22r_g6_P1_map.txt g6 > r3/K23c_line.log 2>&1 && \
  PUB_SRC=r2k23c PUB_BL_PROMPT=prompt_K22r_g6_P1_screen.txt python blend.py g68K23c g6 > r3/K23c_write.log 2>&1 ) &
( PUB_SRC=r2c PUB_BL_PROMPT=prompt_K22r_g56_P2_screen.txt python blend.py g68K23b0 g6 > r3/K23b0_write.log 2>&1 ) &
( PUB_SRC=r2c PUB_BL_PROMPT=prompt_K22r_g6_P1_screen.txt python blend.py g68K23c0 g6 > r3/K23c0_write.log 2>&1 ) &
wait
for t in "g68K23b r2k23b" "g68K23c r2k23c" "g68K23b0 r2c" "g68K23c0 r2c"; do python r3/k22check.py $t; done
echo "== K23 写完 $(date)"
