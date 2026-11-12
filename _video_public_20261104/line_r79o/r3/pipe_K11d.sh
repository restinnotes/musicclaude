#!/bin/bash
# 11-09 凌晨 K11d：K9e0（只删感受、带原文）→ 按评委点名回补（K9e 对 K3M2 盲比理由）→ 修接缝 → 第 5 段这类过密屏收紧（不许电报式）→ 全套测量 + 绝对验收两遍
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1
RESTORE_CITED=1 RESTORE_MAX=8 python restore.py g68K3M2 g68K9e0 g68K9e g68K9g0
python cut.py seam g68K3M2 g68K9g0 g68K9g
DENSE_V2=1 python dense.py g68K9g g68K11d 8
echo "== K11d 写好 $(date)"
export PUB_VS3B=1
python vs2.py g68K11d g68K3M2 &
python units.py judge g68K11d &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K11d')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K11d run1 run2 &
wait
python -c "
import gate2, core
for w in gate2.WORKS: print('K11d', w, '旧覆盖', gate2.bcov(w,'g68K11d'), '；核心要点覆盖', core.score(w,'g68K11d')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K11d'))
"
echo "== K11d 测完 $(date)"
