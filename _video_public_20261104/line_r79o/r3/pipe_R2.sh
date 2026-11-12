#!/bin/bash
# 11-08 第二轮：T3（只换难懂术语、换时要具体）和 K7（同一写稿提示词、GPT-5.6 写），去小节号后分阶段快筛对 K3M2
cd /d/musicclaude/_video_public_20261104/line_r79o
TERM_V3=1 TERM_MAX=1.0 python term.py g68K3M2 g68K3M2T3 &
PUB_BL_PROMPT=prompt_BLg63n.txt python blend.py g68K7 g56 &
wait
n=$(python -c "import gate2;print(sum(gate2.barnums(w,'g68K7') for w in gate2.WORKS))")
if [ "$n" != "0" ]; then python nobar2.py g68K7 g68K7M; else for w in op60 op61; do cp r3/s24/screen_${w}_g68K7.json r3/s24/screen_${w}_g68K7M.json; done; python -c "
from pub24 import S,rd,to_script
for w in ['op60','op61']: to_script(w,'g68K7M',rd(S/f'screen_{w}_g68K7M.json'))"; fi
python -c "import gate2;print('小节号', {t: sum(gate2.barnums(w,t) for w in gate2.WORKS) for t in ['g68K3M2T3','g68K7M']})"
python r3/stage.py g68K3M2 g68K3M2T3 g68K7M
