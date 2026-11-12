#!/bin/bash
# 11-11 I12 交回后的一批：两位顾问各三套 DAG2（原料 r2e），四套改线。两条链并行跑，每条链三个候选依次写+快筛。
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_FRAG_RULE=std9
P="40,5,30,6,3,5"
for L in "r2f prompt_L29_g6_1.txt g6" "r2g prompt_L29_g6_2.txt g56" "r2h prompt_L29_g56_1.txt g6" "r2i prompt_L29_g56_2.txt g56"; do set -- $L; PUB_SRC=r2e python r3/dagline.py $1 $2 $3 > r3/dagline_$1.log 2>&1 & done
( PUB_FRAG_PLANWHO=g6 bash r3/pipe_K27one.sh g68K29a prompt_K29_g6_1.txt argon "$P" prompt_K29_g6_1_plan.txt g68K28b r2e > r3/pipe_K29a.log 2>&1
  bash r3/pipe_K27one.sh g68K29b prompt_K29_g6_2.txt g56 "$P" - g68K28b r2e > r3/pipe_K29b.log 2>&1
  bash r3/pipe_K27one.sh g68K29c prompt_K29_g6_3.txt g6 "$P" - - r2e > r3/pipe_K29c.log 2>&1 ) &
( bash r3/pipe_K27one.sh g68K29d prompt_K29_g56_1.txt g6 "$P" - - r2e > r3/pipe_K29d.log 2>&1
  PUB_FRAG_PLANWHO=g6 bash r3/pipe_K27one.sh g68K29e prompt_K29_g56_2.txt g56 "$P" prompt_K29_g56_2_plan.txt g68K28b r2e > r3/pipe_K29e.log 2>&1
  bash r3/pipe_K27one.sh g68K29f prompt_K29_g56_3.txt argon "$P" - g68K28b r2e > r3/pipe_K29f.log 2>&1 ) &
wait
echo "== K29 一批做完 $(date)"
