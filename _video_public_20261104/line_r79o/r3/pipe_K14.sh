#!/bin/bash
# 11-09 K14 = K11g 上只收紧三屏（船歌第 5 段、幻想第 3、11 段），规则同 dense V3（因果对比不删、画面不压缩、放大词不动）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1 PUB_VS3=1 PUB_VS3B=1
DENSE_V3=1 DENSE_ONLY="op60:S05:6.5,op61:S11:6,op61:S03:5.5" python dense.py g68K11g g68K14 8
echo "== K14 写好 $(date)"
python vs2.py g68K14 g68K11g &
python vs2.py g68K14 g68K3M2 &
python units.py judge g68K14 &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K14')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K14 run1 run2 run3 run4 &
wait
python r3/openabs.py g68K14 run1 run2 run3 run4 | grep 绝对验收
python -c "
import gate2, core
for w in gate2.WORKS: print('g68K14', w, '旧覆盖', gate2.bcov(w,'g68K14'), '；核心要点覆盖', core.score(w,'g68K14')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K14'))
"
echo "== K14 测完 $(date)"
