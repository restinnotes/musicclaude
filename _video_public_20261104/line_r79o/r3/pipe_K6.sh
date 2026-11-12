#!/bin/bash
# 11-08 写稿层候选：GPT-6 改写稿提示词 → 两首写两份（K6a、K6b）→ 有小节号就精确去掉 → 快筛对 K3M2
cd /d/musicclaude/_video_public_20261104/line_r79o
ADV_EXTRA=r3/adv_extra_K3.txt python r3/adv_fix.py g68K3A g6 prompt_BLg63n.txt BLg63d
for t in g68K6a g68K6b; do PUB_BL_PROMPT=prompt_BLg63d.txt python blend.py $t g6 & done; wait
for t in g68K6a g68K6b; do
  n=$(python -c "import gate2;print(sum(gate2.barnums(w,'$t') for w in gate2.WORKS))")
  if [ "$n" != "0" ]; then python nobar2.py $t ${t}M; else for w in op60 op61; do cp r3/s24/screen_${w}_$t.json r3/s24/screen_${w}_${t}M.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'${t}M',rd(S/f'screen_{w}_${t}M.json'))"; fi
done
PUB_JREP=1 PUB_PAR=30 python r3/quick_pair.py g68K6aM:g68K3M2 g68K6bM:g68K3M2
