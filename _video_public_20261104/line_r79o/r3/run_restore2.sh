#!/bin/bash
# 11-12 窄回补 M1R2：只补讲体验的、K28b 原来留住而改写后丢掉的；小字最多多 8%；不写音乐本身
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
RESTORE_NARROW=1 RESTORE_BASE=g68K28b RESTORE_CAP=8% python r3/ctrl_restore.py g68CTRLsk2F g68M1R2 > r3/restore_M1R2.log 2>&1 || exit 1
v=g68M1R2
OF_ARGON=1 python r3/open_free.py $v > r3/openF_$v.log 2>&1 &
python r3/openabs5.py $v run1 > r3/abs_${v}_1.log 2>&1 &
python r3/openabs5.py $v run2 > r3/abs_${v}_2.log 2>&1 &
python r3/vs5.py g68K11g $v v5f$v > r3/vs_${v}.log 2>&1 &
python r3/vs5.py g68CTRLsk2F $v v5fmM1R2 > r3/vs_${v}_vs_main.log 2>&1 &
bash r3/pipe_K27full.sh $v r2e > r3/full_$v.log 2>&1 &
wait
echo "== $v"; grep -h "丢掉的单元" r3/restore_M1R2.log; grep -h "绝对验收5b" r3/abs_${v}_*.log | cut -c1-150; grep -h "盲比5" r3/vs_${v}.log | cut -c1-220
echo "== 对主线 CTRLsk2F"; grep -h "盲比5" r3/vs_${v}_vs_main.log | cut -c1-220
echo "== 覆盖走样"; grep -h "确认核心\|两位以上" r3/full_$v.log | cut -c1-220
