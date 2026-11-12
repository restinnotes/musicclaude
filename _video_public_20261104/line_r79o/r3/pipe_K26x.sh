#!/bin/bash
# 11-10 I12 第 1 次交回后：K26a2（GPT-6 改的自然句块，nat2）、K26c2（GPT-5.6 改的关系链，chain2），写手 GPT-6；同时用盲比第五版重跑旧候选（两个一批）。写完快筛（pipe_K26test.sh，盲比第五版）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
PUB_FRAG_RULE=nat2 PUB_BL_PFX=k26x python r3/fragwrite.py g68K26a2 prompt_K26x1_g6.txt g6 > r3/K26a2_write.log 2>&1 &
PUB_FRAG_RULE=chain2 PUB_BL_PFX=k26x python r3/fragwrite.py g68K26c2 prompt_K26x1_g56.txt g6 > r3/K26c2_write.log 2>&1 &
( for pair in "g68K25a g68K26c" "g68K26a g68K24a3" "g68K25b"; do for t in $pair; do python r3/vs5.py g68K11g $t v5$t > /dev/null 2>&1 & done; wait; done ) &
wait
for t in g68K25a g68K26a g68K26c g68K24a3 g68K25b; do python r3/vs5.py sum v5$t; done
grep -h -v "^\[k26x" r3/K26a2_write.log r3/K26c2_write.log
for t in g68K26a2 g68K26c2; do [ -f r3/s24/screen_op61_$t.json ] && [ -f r3/s24/screen_op60_$t.json ] && bash r3/pipe_K26test.sh $t > r3/pipe_${t}test.log 2>&1 & done
wait
for t in g68K26a2 g68K26c2; do echo "## $t"; grep -E "^绝对验收4 $t|^骨架测 $t|^$t op|两位以上|^盲比5" r3/pipe_${t}test.log 2>/dev/null | cut -c1-220; done
echo "== K26x 测完 $(date)"
