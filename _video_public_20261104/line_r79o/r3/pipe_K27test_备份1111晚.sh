#!/bin/bash
# 11-10 午 快筛（新口径）：绝对验收第四版（标准读现行版，run 名 s8）、骨架测、整屏单元覆盖（重新分层 units2）+ 只看大块的必读覆盖、走样、退步检查（盲比第五版 v5b：load 只算大块）。
# 用法：bash r3/pipe_K27test.sh TAG [原料目录，默认 r2c]
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=${2:-r2c}
T=$1
python r3/skeleton.py $T run1 > r3/skel_$T.log 2>&1 &
OF_ARGON=1 python r3/open_free.py $T > r3/openF_$T.log 2>&1 &   # 11-11 开放评审三位：GPT-6、GPT-5.6、Argon（Argon 报出两位 GPT 都漏的问题）
python r3/openabs5.py $T run1 > r3/oa5_${T}.log 2>&1 &   # 11-10 晚 第五版（原样顺读），校准中
python units.py judge $T > r3/cov3_$T.log 2>&1 &
python faithful.py $T > r3/faith_$T.log 2>&1 &
python r3/vs5.py g68K11g $T v5b$T > r3/vs5_$T.log 2>&1 &
python units2.py big $T > r3/big2_$T.log 2>&1 &
wait
python r3/openabs5.py sum $T run1
python r3/skeleton.py sum $T run1
python units2.py score $T
grep "两位以上" r3/faith_$T.log
python r3/vs5.py sum v5b$T
echo "== $T 快筛测完 $(date)"
