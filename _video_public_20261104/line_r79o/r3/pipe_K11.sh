#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1
python dense.py g68K9e g68K11b 9.5
echo "== K11b 写好"
export PUB_VS3=1 PUB_VS3B=1
for t in g68K11 g68K11b; do
  python vs2.py $t g68K3M2 &
  python units.py judge $t &
  python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'$t')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
done
python r3/openabs.py g68K11 g68K11b run1 run2 &
wait
python -c "
import gate2, core
for t in ['g68K9e','g68K11','g68K11b']:
  for w in gate2.WORKS: print(t, w, '旧覆盖', gate2.bcov(w,t), '；核心要点覆盖', core.score(w,t)[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,t))
"
echo "== K11 测完 $(date)"
