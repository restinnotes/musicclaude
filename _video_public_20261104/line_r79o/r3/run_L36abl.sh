#!/bin/bash
# 11-11 深夜：诊断消融 L36abl（L32a 去掉 TARGETS）跑到快筛，和 L32a（53）比打转排名
cd /d/musicclaude/_video_public_20261104/line_r79o
python r3/gate.py || exit 1
(cd /d/musicclaude/_thread_evo_20261019 && python pipe.py run schemes/L36abl.json L36abl 2>&1 | grep -v "^\[" | tail -5)
PUB_SRC=r2e python r3/fromdag.py L36abl r2L36abl || { echo "== L36abl 写线没出来"; exit 1; }
PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68L36abl prompt_K28b.txt argon "40,5,30,6,3,5" - g68K28b r2L36abl
