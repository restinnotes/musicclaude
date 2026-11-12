#!/bin/bash
# 11-08 晚 新测法校准：vs3（细腻、简洁新定义，允许判平）和 cov3（意思单元覆盖）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1
until [ -f r3/s24/units_op60.json ] && [ -f r3/s24/units_op61.json ] && [ -f r3/s24/screen_op61_g68K3M2D.json ] && [ -f r3/s24/screen_op61_g68K8b.json ]; do sleep 20; done
echo "== 材料齐了 $(date)"
for pair in "g68K3M2c g68K3M2" "g68K3M2D g68K3M2" "g68K3M2T2 g68K3M2" "g68K8b g68K3M2"; do python vs2.py $pair & done
python units.py judge w23 w23b g68K3M2 g68K3M2b g68K3M2D g68K3NR g68K3M2T2 g68K8b &
wait
echo "== 校准完 $(date)"
