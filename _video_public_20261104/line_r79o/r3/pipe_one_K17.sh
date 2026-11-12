#!/bin/bash
# 11-09 下午：单个候选的流水线（K15 版 pipe_K15.sh 的单候选写法，候选之间不互相等）：超上限重写 → 去小节号 → 分阶段快筛（对 K11g）→ 活下来的做意思单元覆盖和绝对验收。
# 用法：PUB_SRC=r2c bash r3/pipe_one.sh 写稿标签 写手(g6|g56)
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
python r3/stage.py g68K11g ${T}M | tee r3/${T}_stage.log
if grep -q "淘汰" r3/${T}_stage.log; then echo "== ${T}M 快筛淘汰，不再测 $(date)"; exit 0; fi
python units.py judge ${T}M &
python r3/openabs.py ${T}M run1 run2 &
wait
python -c "
import gate2
for w in gate2.WORKS: print('${T}M', w, '旧覆盖', gate2.bcov(w,'${T}M'), '；走样', gate2.faith(w,'${T}M'))
"
echo "== ${T}M 测完 $(date)"
