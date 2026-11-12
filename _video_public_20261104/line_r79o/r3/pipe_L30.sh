#!/bin/bash
# 11-11 改线端到端（准则：DAG 改动只按端到端证据收）。同一份 DAG2 提示词（K28b：大字用线原话，底稿 K28b），原料只差线：r2e（对照）、r2f/r2g/r2h/r2i（四套改线）。五个同时跑。
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_FRAG_RULE=std9
for s in e f g h i; do
  bash r3/pipe_K27one.sh g68L30$s prompt_K28b.txt argon "40,5,30,6,3,5" - g68K28b r2$s > r3/pipe_L30$s.log 2>&1 &
done
wait
echo "== L30 做完 $(date)"
