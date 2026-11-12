#!/bin/bash
# 11-10 午 标准第 8 条改（看得过来只要求大块）后重判：绝对验收第四版（标准文本自动读新版，run 名 s8）+ 盲比第五版（load 改只算大块，名 v5b）。K11g 作参照。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
for t in g68K11g g68K26c2 g68K25a g68K26a3; do python r3/openabs4.py $t s8 > r3/oa4_${t}_s8.log 2>&1 & done
wait
for t in g68K26c2 g68K25a; do python r3/vs5.py g68K11g $t v5b$t > /dev/null 2>&1 & done; wait
python r3/vs5.py g68K11g g68K26a3 v5bg68K26a3 > /dev/null 2>&1
for t in g68K11g g68K26c2 g68K25a g68K26a3; do python r3/openabs4.py sum $t s8; done
for t in g68K26c2 g68K25a g68K26a3; do python r3/vs5.py sum v5b$t; done
echo "== 新第 8 条重判完 $(date)"
