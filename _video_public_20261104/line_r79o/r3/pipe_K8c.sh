#!/bin/bash
# 11-08 晚 K8c：屏幕上已有的意思单元一样不丢、只删重复和空话、保留过渡；测 vs3 对 K3M2、cov3、旧覆盖、走样
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1
ONEFEEL_UNITS=1 python onefeel.py g68K3M2 g68K8c; python -c "import gate2;print(\"小节号\", sum(gate2.barnums(w,\"g68K8c\") for w in gate2.WORKS))"
python vs2.py g68K8c g68K3M2 &
python units.py judge g68K8c &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K8c')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
wait
python -c "
import gate2, core
for w in gate2.WORKS: print(w, '旧覆盖', gate2.bcov(w,'g68K8c'), '对 K3M2', gate2.bcov(w,'g68K3M2'), '；两位都判核心的要点覆盖', core.score(w,'g68K8c')[0], '对 K3M2', core.score(w,'g68K3M2')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K8c') if hasattr(gate2,'faith') else '')
"
echo "== K8c 测完 $(date)"
