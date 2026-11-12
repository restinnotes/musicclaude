#!/bin/bash
# 11-09 K12：K11f 上只删长感受块（>35 字）里次要的小句（问题清单用 K11f 绝对验收报的）→ 修接缝 → 第 5 段再收一点（每秒 7.5 字）→ 对 K11f 盲比 + 全套 + 绝对验收四遍
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1 PUB_VS3B=1
CUT_LONG=35 CUT_ISSUES=openA2 CUT_V2=1 python cut.py g68K11f g68K12a0
python cut.py seam g68K11f g68K12a0 g68K12a
DENSE_V3=1 python dense.py g68K12a g68K12 7.5
echo "== K12 写好 $(date)"
python vs2.py g68K12 g68K11f &
python vs2.py g68K12 g68K3M2 &
python units.py judge g68K12 &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K12')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K12 run1 run2 run3 run4 &
wait
python r3/openabs.py g68K12 run1 run2 run3 run4 | grep 绝对验收
python -c "
import gate2, core
for t in ['g68K11f','g68K12']:
  for w in gate2.WORKS: print(t, w, '旧覆盖', gate2.bcov(w,t), '；核心要点覆盖', core.score(w,t)[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,t))
"
echo "== K12 测完 $(date)"
