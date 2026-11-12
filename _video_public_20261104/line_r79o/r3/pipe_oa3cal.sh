#!/bin/bash
# 11-09 晚 绝对验收第三版校准：K11g 两遍 + 四个只改一处的对照
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
for t in "g68K11g run1" "g68K11g run2" "g68K11gCL run1" "g68K11gCS run1" "g68K11gCN run1" "g68K11gCV run1"; do
  python r3/openabs3.py $t > "r3/oa3_${t// /_}.log" 2>&1 &
done
wait
for t in g68K11g g68K11gCL g68K11gCS g68K11gCN g68K11gCV; do python r3/openabs3.py sum $t run1 run2; done
echo "== 绝对验收3 校准测完 $(date)"
