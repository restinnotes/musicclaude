#!/bin/bash
# 11-09 下午 顾问路线 B（以 K11g 为底逐屏重组）的流水线。GPT-6 顾问（r3/s24/adv_k18_g6.json）：绝对验收和整体盲比分开测，先看绝对验收（严重 0、中等 0），
# 盲比不再一步淘汰；新路线至少给一轮按问题修改的机会。所以这里：超上限重写 → 去小节号 → 绝对验收（两位 × 两遍）和盲比快筛（对 K11g）同时跑，都报。
# 用法：PUB_SRC=r2c bash r3/pipe_B.sh 标签 写手(g6|g56)
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_BL_RATE=${PUB_BL_RATE:-5.5}
T=$1; WHO=$2
python refit.py $T ${T}R $WHO
n=$(python -c "import gate2;print(sum(gate2.barnums(w,'${T}R') for w in gate2.WORKS))")
if [ "$n" != "0" ]; then python nobar2.py ${T}R ${T}M; else for w in op60 op61; do cp r3/s24/screen_${w}_${T}R.json r3/s24/screen_${w}_${T}M.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'${T}M',rd(S/f'screen_{w}_${T}M.json'))"; fi
echo "== $T 定版 ${T}M $(date)"
export PUB_VS3=1 PUB_VS3B=1
python r3/openabs.py ${T}M run1 run2 > r3/${T}_abs.log 2>&1 &
python r3/stage.py g68K11g ${T}M > r3/${T}_stage.log 2>&1 &
wait
grep "绝对验收" r3/${T}_abs.log; grep "】\|结果" r3/${T}_stage.log
echo "== ${T}M 测完 $(date)"
