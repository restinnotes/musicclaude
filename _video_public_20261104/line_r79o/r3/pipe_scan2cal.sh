#!/bin/bash
# 11-09 晚 截图评委第二版校准：每首同 5 屏；K11g 两遍（稳定）+ K18cM、w23S、SP（极易扫，正向）、SL（整段，反向）
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 SJ_THREADS=6 SJ_SECS=S03,S05,S09,S11,S13 FILM_DATA=line_r79o
( python r3/scanjudge2.py judge g68K11g run1 > r3/scan2b_K11g1.log 2>&1; python r3/scanjudge2.py judge g68K11gSP run1 > r3/scan2b_SP.log 2>&1; python r3/scanjudge2.py judge w23S run1 > r3/scan2b_w23.log 2>&1 ) &
( python r3/scanjudge2.py judge g68K11g run2 > r3/scan2b_K11g2.log 2>&1; python r3/scanjudge2.py judge g68K11gSL run1 > r3/scan2b_SL.log 2>&1; python r3/scanjudge2.py judge g68K18cM run1 > r3/scan2b_K18.log 2>&1 ) &
wait
python r3/scanjudge2.py sum g68K11g run1 run2
for t in g68K11gSP g68K11gSL g68K18cM w23S; do python r3/scanjudge2.py sum $t run1; done
echo "== 截图评委2 校准测完 $(date)"
