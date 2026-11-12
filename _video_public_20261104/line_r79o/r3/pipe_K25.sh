#!/bin/bash
# 11-10 K25：第 3 次（最后一次）交回后的四个候选。K25b = GPT-5.6 重写、K25bR = GPT-5.6 修补 K24b3、K25a = GPT-6 重写、K25aR = GPT-6 修补 K24a3。写完全部跑快筛。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
PUB_BL_PFX=k25 python r3/fragwrite.py g68K25b prompt_K24r3_g56.txt g6 > r3/K25b_write.log 2>&1 &
PUB_BL_PFX=k25 python r3/fragwrite.py g68K25a prompt_K24r3_g6.txt g6 > r3/K25a_write.log 2>&1 &
PUB_BL_PFX=k25r python r3/fragrepair.py g68K25bR g68K24b3 prompt_K24r3_g56_repair.txt g6 > r3/K25bR_write.log 2>&1 &
PUB_BL_PFX=k25r python r3/fragrepair.py g68K25aR g68K24a3 prompt_K24r3_g6_repair.txt g6 > r3/K25aR_write.log 2>&1 &
wait
grep -h -v "^\[k25" r3/K25*_write.log
for t in g68K25bR g68K25aR g68K25b g68K25a; do [ -f r3/s24/screen_op61_$t.json ] && [ -f r3/s24/screen_op60_$t.json ] && bash r3/pipe_K24test.sh $t > r3/pipe_${t}test.log 2>&1 & done
wait
for t in g68K25bR g68K25aR g68K25b g68K25a; do grep -E "$t|两位以上|盲比4" r3/pipe_${t}test.log | cut -c1-200; done
echo "== K25 测完 $(date)"
