#!/bin/bash
# 11-12 Argon 版限长保内容小字（CTRLsk2）在新评法（成片形式）下完整重测，并补覆盖走样
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
v=g68CTRLsk2F
OF_ARGON=1 python r3/open_free.py $v > r3/openF_$v.log 2>&1 &
python r3/openabs5.py $v run1 > r3/abs_${v}_1.log 2>&1 &
python r3/openabs5.py $v run2 > r3/abs_${v}_2.log 2>&1 &
python r3/vs5.py g68K11g $v v5f$v > r3/vs_${v}.log 2>&1 &
python r3/vs5.py g68K28bF $v v5fmCTRLsk2 > r3/vs_${v}_vs_K28bF.log 2>&1 &
bash r3/pipe_K27full.sh $v r2e > r3/full_$v.log 2>&1 &
wait
echo "== $v"; grep -h "绝对验收5b" r3/abs_${v}_*.log | cut -c1-150; grep -h "盲比5" r3/vs_${v}.log | cut -c1-220
echo "== 对 K28bF"; grep -h "盲比5" r3/vs_${v}_vs_K28bF.log | cut -c1-220
echo "== 覆盖走样"; grep -h "确认核心\|两位以上" r3/full_$v.log | cut -c1-220
