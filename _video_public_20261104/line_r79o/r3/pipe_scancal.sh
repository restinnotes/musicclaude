#!/bin/bash
# 11-09 晚 截图评委校准：K11g 两遍（同一版是否接近）、K18cM（太碎）、w23S（旧视频核心短语）；候选 K20、K20T 同批
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python r3/scanjudge.py judge g68K11g run1 > r3/scan_K11g_1.log 2>&1 &
python r3/scanjudge.py judge g68K11g run2 > r3/scan_K11g_2.log 2>&1 &
python r3/scanjudge.py judge g68K18cM run1 > r3/scan_K18c.log 2>&1 &
python r3/scanjudge.py judge w23S run1 > r3/scan_w23.log 2>&1 &
wait
python r3/scanjudge.py judge g68K20 run1 > r3/scan_K20.log 2>&1 &
python r3/scanjudge.py judge g68K20T run1 > r3/scan_K20T.log 2>&1 &
python r3/scanjudge.py judge g68K11gT run1 > r3/scan_K11gT.log 2>&1 &
wait
for t in g68K11g g68K18cM w23S g68K20 g68K20T g68K11gT; do python r3/scanjudge.py sum $t run1 run2; done
echo "== 校准测完 $(date)"
