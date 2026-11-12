#!/bin/bash
# 11-09 下午 K15：写稿层重写（揉在一起 + 每屏按停留秒数定字数上限）。用户：“我感觉你这现在的dag2内容看上去还是很像我们之前那个版本的”。
# 用户：“你这个流程也要按照你之前提速的那个方式来提速”→ 两个候选一起走分阶段快筛（r3/stage.py：A 盲比 2 位 → B 走样+覆盖 2 位 → C 补齐 4 位，明显输就停），
# 只有活过快筛的才做意思单元覆盖和绝对验收；超上限的屏并行重写；每账号在途 8。
# 用法：bash r3/pipe_K15.sh 写手1标签 写手1 写手2标签 写手2     例：bash r3/pipe_K15.sh g68K15a g6 g68K15b g56（写稿已由 blend.py 完成）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_BL_RATE=${PUB_BL_RATE:-5.5}
prep() {   # 超上限重写 → 去小节号 → 定版 ${T}M
  T=$1; WHO=$2
  python refit.py $T ${T}R $WHO
  n=$(python -c "import gate2;print(sum(gate2.barnums(w,'${T}R') for w in gate2.WORKS))")
  if [ "$n" != "0" ]; then python nobar2.py ${T}R ${T}M; else for w in op60 op61; do cp r3/s24/screen_${w}_${T}R.json r3/s24/screen_${w}_${T}M.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'${T}M',rd(S/f'screen_{w}_${T}M.json'))"; fi
  echo "== $T 定版 ${T}M $(date)"
}
prep $1 $2 &
prep $3 $4 &
wait
export PUB_VS3=1 PUB_VS3B=1
python r3/stage.py g68K11g ${1}M ${3}M | tee r3/${1}_stage.log
for T in ${1}M ${3}M; do
  if grep -q "【$T】.*淘汰" r3/${1}_stage.log; then echo "== $T 快筛淘汰，不再测"; continue; fi
  python units.py judge $T &
  python r3/openabs.py $T run1 &
done
wait
python -c "
import gate2, core
for T in ['${1}M','${3}M']:
  for w in gate2.WORKS: print(T, w, '旧覆盖', gate2.bcov(w,T), '；走样', gate2.faith(w,T))
"
echo "== K15 测完 $(date)"
