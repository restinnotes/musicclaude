#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2c
python r3/vs4.py g68K11g g68K11gZ v4self > r3/vs4_self.log 2>&1 &
python r3/vs4.py g68K11g g68K11gCL v4CL > r3/vs4_CL.log 2>&1 &
python r3/vs4.py g68K11g g68K11gCV v4CV > r3/vs4_CV.log 2>&1 &
python r3/vs4.py g68K11g g68K24a v4K24a > r3/vs4_K24a.log 2>&1 &
wait
python r3/vs4.py g68K11g g68K24b2 v4K24b2 > r3/vs4_K24b2.log 2>&1
for n in v4self v4CL v4CV v4K24a v4K24b2; do python r3/vs4.py sum $n; done
echo "== 盲比4 校准完 $(date)"
