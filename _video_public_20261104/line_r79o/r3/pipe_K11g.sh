#!/bin/bash
# 11-09 定稿候选 K11g = K11f + 语病微修（每处 ≤4 字）：复核绝对验收两遍、走样、覆盖、对 K11f 盲比
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1 PUB_VS3B=1
python vs2.py g68K11g g68K11f &
python units.py judge g68K11g &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K11g')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K11g run1 run2 &
wait
python r3/openabs.py g68K11g run1 run2 | grep 绝对验收
python -c "
import gate2, core
for w in gate2.WORKS: print('K11g', w, '旧覆盖', gate2.bcov(w,'g68K11g'), '；核心要点覆盖', core.score(w,'g68K11g')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K11g'))
"
echo "== K11g 复核完 $(date)"
