#!/bin/bash
# 11-12 CTRLsk3 = CTRLsk2 只多一处：心里话原样保留（标准第 6 条），Argon 写；新形式下完整测 + 覆盖走样 + 对 K28bF 盲比
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
CTRL_S_TAG=g68CTRLsk3 CTRL_S_WHO=argon CTRL_S_CAP=1 CTRL_S_KEEP=1 CTRL_S_INNER=1 python r3/ctrl_small.py > r3/ctrl_small_sk3.log 2>&1 || exit 1
v=g68CTRLsk3
OF_ARGON=1 python r3/open_free.py $v > r3/openF_$v.log 2>&1 &
python r3/openabs5.py $v run1 > r3/abs_${v}_1.log 2>&1 &
python r3/openabs5.py $v run2 > r3/abs_${v}_2.log 2>&1 &
python r3/vs5.py g68K11g $v v5f$v > r3/vs_${v}.log 2>&1 &
python r3/vs5.py g68K28bF $v v5fmCTRLsk3 > r3/vs_${v}_vs_K28bF.log 2>&1 &
bash r3/pipe_K27full.sh $v r2e > r3/full_$v.log 2>&1 &
wait
echo "== $v"; grep -h "绝对验收5b" r3/abs_${v}_*.log | cut -c1-150; grep -h "盲比5" r3/vs_${v}.log | cut -c1-220
echo "== 对 K28bF"; grep -h "盲比5" r3/vs_${v}_vs_K28bF.log | cut -c1-220
echo "== 覆盖走样"; grep -h "确认核心\|两位以上" r3/full_$v.log | cut -c1-220
