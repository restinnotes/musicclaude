#!/bin/bash
# 11-12 交回后“改”的方案：写线 → 换原料 → 写稿（WRITE 沿用原方案的，没有就用 K28b；允许空大块屏）→ 快筛
cd /d/musicclaude/_video_public_20261104/line_r79o
BI=$1; B=${BI:0:2}; I=${BI:2}
(cd /d/musicclaude/_thread_evo_20261019 && python pipe.py run schemes/L38$BI.json L38$BI 2>&1 | grep -v "^\[" | tail -5)
PUB_SRC=r2e python r3/fromdag.py L38$BI r2L38$BI || { echo "== L38$BI 写线没出来"; exit 1; }
P=prompt_K28b.txt; [ -f r3/s24/prompt_L$B$I.txt ] && P=prompt_L$B$I.txt
PUB_FRAG_NOBIG=1 PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68L38$BI $P argon "40,5,30,6,3,5" - g68K28b r2L38$BI
