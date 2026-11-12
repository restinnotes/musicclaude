#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
PUB_FRAG_RULE=nat3 PUB_BL_PFX=k26y python r3/fragwrite.py g68K26a3 prompt_K26x2_g6.txt g6 > r3/K26a3_write.log 2>&1
grep -v "^\[k26y" r3/K26a3_write.log
[ -f r3/s24/screen_op61_g68K26a3.json ] && [ -f r3/s24/screen_op60_g68K26a3.json ] && bash r3/pipe_K26test.sh g68K26a3 > r3/pipe_g68K26a3test.log 2>&1
grep -E "^绝对验收4 g68K26a3|^骨架测 g68K26a3|^g68K26a3 op|两位以上|^盲比5" r3/pipe_g68K26a3test.log | cut -c1-220
echo "== K26a3 测完 $(date)"
