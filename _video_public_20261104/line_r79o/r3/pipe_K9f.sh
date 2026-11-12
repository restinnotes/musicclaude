#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1
python restore.py g68K3M2 g68K9e0 g68K9e g68K9f0
python cut.py seam g68K3M2 g68K9f0 g68K9f
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1
python vs2.py g68K9f g68K3M2 &
python units.py judge g68K9f &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K9f')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
wait
python -c "
import gate2, core
for w in gate2.WORKS: print(w, '旧覆盖', gate2.bcov(w,'g68K9f'), '对 K3M2', gate2.bcov(w,'g68K3M2'), '；两位都判核心的要点覆盖', core.score(w,'g68K9f')[0], '对 K3M2', core.score(w,'g68K3M2')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K9f') if hasattr(gate2,'faith') else '')
"
python r3/open_review.py g68K9f; bash r3/open_batch.sh g68K9f | grep 开放评审
echo "== K9 测完 $(date)"
