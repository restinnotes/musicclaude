#!/bin/bash
# 过了绝对验收和退步检查的候选，补覆盖和走样（准则第九节第 3 条）。用法：bash r3/pipe_K27full.sh TAG [原料目录]
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=${2:-r2c}
T=$1
python units.py judge $T > r3/cov3_$T.log 2>&1 &
python faithful.py $T > r3/faith_$T.log 2>&1 &
python units2.py big $T > r3/big2_$T.log 2>&1 &
wait
python units2.py score $T
grep "两位以上" r3/faith_$T.log
echo "== $T 覆盖走样测完 $(date)"
