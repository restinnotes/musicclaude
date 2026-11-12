#!/bin/bash
# 11-09 晚 K24 快筛 + 绝对验收第四版校准（标准换成 8 条后）。
# 第四版校准：K11g 两遍、打转对照 CL、笼统对照 CV；候选 K24b（K24a 写完另跑）；K23bN 作参照。
# 快筛：骨架测、意思单元覆盖、走样、退步检查（和 K11g 盲比 vs3b，两种顺序）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
T=${1:-g68K24b}
for x in "g68K11g run1" "g68K11g run2" "g68K11gCL run1" "g68K11gCV run1" "$T run1"; do python r3/openabs4.py $x > "r3/oa4_${x// /_}.log" 2>&1 & done
PUB_SRC=r2k23b python r3/openabs4.py g68K23bN run1 > r3/oa4_K23bN.log 2>&1 &
python r3/skeleton.py $T run1 > r3/skel_$T.log 2>&1 &
python units.py judge $T > r3/cov3_$T.log 2>&1 &
python faithful.py $T > r3/faith_$T.log 2>&1 &
python r3/vs4.py g68K11g $T v4$T > r3/vs4_$T.log 2>&1 &
wait
for t in g68K11g g68K11gCL g68K11gCV $T; do python r3/openabs4.py sum $t run1 run2; done
PUB_SRC=r2k23b python r3/openabs4.py sum g68K23bN run1
python r3/skeleton.py sum g68K11g run1 run2; python r3/skeleton.py sum $T run1
python units.py score g68K11g $T
grep "两位以上" r3/faith_$T.log
python r3/vs4.py sum v4$T
echo "== $T 快筛测完 $(date)"
