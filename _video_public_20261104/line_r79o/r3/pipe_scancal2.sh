#!/bin/bash
# 11-09 晚 重跑截图评委校准：18:49 那批四条流水线各 12 线程同时起 docker exec，进程起不来（0xC0000142）。改成两条并行、各 8 线程；沿用已存的结果。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 SJ_THREADS=8
( python r3/scanjudge.py judge g68K11g run1 > r3/scan2_K11g_1.log 2>&1; python r3/scanjudge.py judge g68K18cM run1 > r3/scan2_K18c.log 2>&1 ) &
( python r3/scanjudge.py judge g68K11g run2 > r3/scan2_K11g_2.log 2>&1; python r3/scanjudge.py judge w23S run1 > r3/scan2_w23.log 2>&1 ) &
wait
for t in g68K11g g68K18cM w23S; do python r3/scanjudge.py sum $t run1 run2; done
echo "== 校准测完 $(date)"
