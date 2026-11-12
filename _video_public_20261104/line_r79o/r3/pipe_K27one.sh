#!/bin/bash
# 写一个 K27 候选并快筛。用法：bash r3/pipe_K27one.sh TAG 提示词 写手 "大块字数,大块个数,小块字数,小块个数,大块每秒字数,旁注条数" [第一步提示词或-] [底稿TAG或-] [原料目录]
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=${7:-r2c}
T=$1
export PUB_FRAG_RULE=${PUB_FRAG_RULE:-std8} PUB_FRAG_P="$4" PUB_BL_PFX=k27_$T
[ "${5:--}" != "-" ] && export PUB_FRAG_PLAN=$5
[ "${6:--}" != "-" ] && export PUB_FRAG_BASE=$6
python r3/fragwrite.py $T $2 $3 > r3/${T}_write.log 2>&1
grep -v "^\[" r3/${T}_write.log | cut -c1-300
[ -f r3/s24/screen_op61_$T.json ] && [ -f r3/s24/screen_op60_$T.json ] && bash r3/pipe_K27test.sh $T ${7:-r2c} > r3/pipe_${T}test.log 2>&1
grep -E "^绝对验收4|^绝对验收5|^骨架测|^g68K27.* op|两位以上|^盲比5" r3/pipe_${T}test.log | cut -c1-330
echo "== $T 做完 $(date)"
