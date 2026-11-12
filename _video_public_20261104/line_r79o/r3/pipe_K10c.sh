#!/bin/bash
# 11-09 凌晨 K10b 接近过线（盲比连贯、为什么、单独成立大赢；走样没过、太长）→ 交回 GPT-5.6 第二次改（迭代准则 I12/I13）
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1
# 已完成：ADV_EXTRA=r3/adv_extra_K10c.txt python r3/adv_fix.py g68K10bM g56 prompt_BLg64b.txt BLg64c
PUB_BL_PROMPT=prompt_BLg64c.txt python blend.py g68K10c g6
n=$(python -c "import gate2;print(sum(gate2.barnums(w,'g68K10c') for w in gate2.WORKS))")
if [ "$n" != "0" ]; then python nobar2.py g68K10c g68K10cM; else for w in op60 op61; do cp r3/s24/screen_${w}_g68K10c.json r3/s24/screen_${w}_g68K10cM.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'g68K10cM',rd(S/f'screen_{w}_g68K10cM.json'))"; fi
echo "== K10c 写好 $(date)"
export PUB_VS3=1 PUB_VS3B=1
python vs2.py g68K10cM g68K3M2 &
python units.py judge g68K10cM &
python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'g68K10cM')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
python r3/openabs.py g68K10cM run1 &
wait
python -c "
import gate2, core
for w in gate2.WORKS: print('K10c', w, '旧覆盖', gate2.bcov(w,'g68K10cM'), '；核心要点覆盖', core.score(w,'g68K10cM')[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,'g68K10cM'))
"
echo "== K10c 测完 $(date)"
