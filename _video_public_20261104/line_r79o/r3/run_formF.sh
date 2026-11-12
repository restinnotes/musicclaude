#!/bin/bash
# 11-12 评委看到的稿子改成和成片一致（一起出现、不出旁注）后，K28b 和 CTRLs 在新评法下重测（标签加 F，旧缓存不混用）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
for v in g68K28bF g68CTRLsF; do
  OF_ARGON=1 python r3/open_free.py $v > r3/openF_$v.log 2>&1 &
  python r3/openabs5.py $v run1 > r3/abs_${v}_1.log 2>&1 &
  python r3/openabs5.py $v run2 > r3/abs_${v}_2.log 2>&1 &
  python r3/vs5.py g68K11g $v v5f$v > r3/vs_${v}.log 2>&1 &
done
python r3/vs5.py g68K28bF g68CTRLsF v5fmCTRLs > r3/vs_CTRLsF_vs_K28bF.log 2>&1 &
wait
for v in g68K28bF g68CTRLsF; do echo "== $v"; grep -h "绝对验收5b" r3/abs_${v}_*.log | cut -c1-150; grep -h "盲比5" r3/vs_${v}.log | cut -c1-220; done
echo "== CTRLsF 对 K28bF"; grep -h "盲比5" r3/vs_CTRLsF_vs_K28bF.log | cut -c1-220
