#!/bin/bash
# 11-12 我写 vs GPT-6 写（同一想法），各自 Argon 写稿 + 快筛
cd /d/musicclaude/_video_public_20261104/line_r79o
python r3/l39_g6.py || exit 1
export PUB_FRAG_NOBIG=1 PUB_FRAG_RULE=std9
bash r3/pipe_K27one.sh g68L39me prompt_L39me.txt argon "40,5,30,6,3,5" - g68K28b r2e > r3/run_L39me.log 2>&1 &
bash r3/pipe_K27one.sh g68L39g6 prompt_L39g6.txt argon "40,5,30,6,3,5" - g68K28b r2e > r3/run_L39g6.log 2>&1 &
wait
for v in me g6; do grep -h "大块\|绝对验收\|盲比5\|不合格\|Traceback\|Error" r3/run_L39$v.log | cut -c1-220; done
