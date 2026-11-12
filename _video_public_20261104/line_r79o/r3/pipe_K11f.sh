#!/bin/bash
# 11-09 凌晨 K11e：K9e0 → 按 K9e、K11d 两轮评委点名回补（每首至多 12 句）→ 修接缝 → 过密屏收紧（保留因果对比、画面不压缩）→ 全套测量 + 绝对验收两遍
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1
RESTORE_V2=1 RESTORE_CITED=1 RESTORE_MAX=12 RESTORE_FROM=g68K9e,g68K11d python restore.py g68K3M2 g68K9e0 g68K9e g68K9i0
python cut.py seam g68K3M2 g68K9i0 g68K9i
DENSE_V3=1 python dense.py g68K9i g68K11f 8
echo "== K11f 写好 $(date)"
export PUB_VS3B=1
python vs2.py g68K11f g68K3M2 &
python units.py judge g68K11f &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K11f')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K11f run1 run2 &
wait
python -c "
import gate2, core
for w in gate2.WORKS: print('K11e', w, '旧覆盖', gate2.bcov(w,'g68K11f'), '；核心要点覆盖', core.score(w,'g68K11f')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K11f'))
"
echo "== K11f 测完 $(date)"
