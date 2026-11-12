#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
for t in g68K25a g68K26a g68K26c g68K24a3 g68K25b; do python r3/vs5.py g68K11g $t v5$t > /dev/null 2>&1 & done
wait
for t in g68K25a g68K26a g68K26c g68K24a3 g68K25b; do python r3/vs5.py sum v5$t; done
echo "== 盲比5 候选完 $(date)"
