#!/bin/bash
# 11-09 晚 K23 快筛（I04）：绝对验收第三版（两位评委一遍）+ 意思单元覆盖（对 r2c 冻结清单，K11g 已有）+ 走样（对各自的原料）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PUB_SRC=r2k23b python r3/openabs3.py g68K23b run1 > r3/oa3_K23b.log 2>&1 &
PUB_SRC=r2k23c python r3/openabs3.py g68K23c run1 > r3/oa3_K23c.log 2>&1 &
PUB_SRC=r2c python r3/openabs3.py g68K23b0 run1 > r3/oa3_K23b0.log 2>&1 &
PUB_SRC=r2c python r3/openabs3.py g68K23c0 run1 > r3/oa3_K23c0.log 2>&1 &
PUB_SRC=r2k23b python faithful.py g68K23b > r3/faith_K23b.log 2>&1 &
PUB_SRC=r2k23c python faithful.py g68K23c > r3/faith_K23c.log 2>&1 &
PUB_SRC=r2c python units.py judge g68K23b g68K23c g68K23b0 g68K23c0 > r3/cov3_K23.log 2>&1 &
wait
for t in g68K11g g68K23b g68K23c g68K23b0 g68K23c0; do python r3/openabs3.py sum $t run1; done
PUB_SRC=r2c python units.py score g68K11g g68K23b g68K23c g68K23b0 g68K23c0
tail -n 3 r3/faith_K23b.log r3/faith_K23c.log
echo "== K23 快筛测完 $(date)"
