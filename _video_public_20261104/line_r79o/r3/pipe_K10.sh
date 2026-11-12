#!/bin/bash
# 11-09 凌晨 写稿层大改：两位顾问各自据十来个局部候选的结论改写稿提示词 → 两首各写一份 → 去小节号 → 全套测量 + 开放评审
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_BC_ALL=1 PUB_JREP=1
ADV_EXTRA=r3/adv_extra_K10.txt python r3/adv_fix.py g68K3M2 g6 prompt_BLg63n.txt BLg64a &
ADV_EXTRA=r3/adv_extra_K10.txt python r3/adv_fix.py g68K3M2 g56 prompt_BLg63n.txt BLg64b &
wait
PUB_BL_PROMPT=prompt_BLg64a.txt python blend.py g68K10a g6 &
PUB_BL_PROMPT=prompt_BLg64b.txt python blend.py g68K10b g6 &
wait
for t in g68K10a g68K10b; do
  n=$(python -c "import gate2;print(sum(gate2.barnums(w,'$t') for w in gate2.WORKS))")
  if [ "$n" != "0" ]; then python nobar2.py $t ${t}M; else for w in op60 op61; do cp r3/s24/screen_${w}_$t.json r3/s24/screen_${w}_${t}M.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'${t}M',rd(S/f'screen_{w}_${t}M.json'))"; fi
done
echo "== K10 写好 $(date)"
export PUB_VS3=1
for t in g68K10aM g68K10bM; do
  python vs2.py $t g68K3M2 &
  python units.py judge $t &
  python -c "
import pub24, faithful
from concurrent.futures import ThreadPoolExecutor
jobs=[(k,(w,j,'$t')) for w in pub24.WORKS for j in pub24.JUDGES for k in ('fa','bc')]
with ThreadPoolExecutor(16) as ex: list(ex.map(lambda x: faithful.one(x[1]) if x[0]=='fa' else pub24.bead_cov(x[1]), jobs))
" &
  python r3/open_review.py $t &
done
wait
python -c "
import gate2, core
for t in ['g68K10aM','g68K10bM']:
  for w in gate2.WORKS: print(t, w, '旧覆盖', gate2.bcov(w,t), '对 K3M2', gate2.bcov(w,'g68K3M2'), '；两位都判核心的要点覆盖', core.score(w,t)[0], '对 w23', core.score(w,'w23')[0], '；走样', gate2.faith(w,t))
"
bash r3/open_batch.sh g68K10aM g68K10bM | grep 开放评审
echo "== K10 测完 $(date)"
