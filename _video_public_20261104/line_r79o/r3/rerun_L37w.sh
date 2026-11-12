#!/bin/bash
# 11-12：L37 写稿被 Argon 429 限流，错开重跑（写线已出，只重跑写稿 + 快筛）
cd /d/musicclaude/_video_public_20261104/line_r79o
for i in g61 g62 g63 g561 g562; do
  PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68L37$i prompt_K28b.txt argon "40,5,30,6,3,5" - g68K28b r2L37$i > r3/run_L37${i}w.log 2>&1 &
  sleep 240
done
bash r3/run_L37.sh g563 > r3/run_L37g563.log 2>&1 &
wait
for i in g61 g62 g63 g561 g562; do grep -h "大块\|绝对验收\|盲比5\|不合格" r3/run_L37${i}w.log | cut -c1-220; done
grep -h "线 \|大块\|绝对验收\|盲比5\|没出来" r3/run_L37g563.log | cut -c1-220
