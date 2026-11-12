#!/bin/bash
# 11-12：Argon 今天限流用完（用户：“argon 应该是今天都不行了”）。L37 写稿改用 GPT-6（K28b 写法本身只切线原话），开放评审先跑两位 GPT，Argon 明天补（open_free 按评委缓存，补跑只补 Argon）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OF_ARGON=
for i in g61 g62 g63 g561 g562; do
  PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g6L37$i prompt_K28b.txt g6 "40,5,30,6,3,5" - g68K28b r2L37$i > r3/run_L37${i}g.log 2>&1 &
  sleep 60
done
( (cd /d/musicclaude/_thread_evo_20261019 && python pipe.py run schemes/L37g563.json L37g563 2>&1 | grep -v "^\[" | tail -5)
  PUB_SRC=r2e python r3/fromdag.py L37g563 r2L37g563 && PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g6L37g563 prompt_K28b.txt g6 "40,5,30,6,3,5" - g68K28b r2L37g563 ) > r3/run_L37g563g.log 2>&1 &
wait
for i in g61 g62 g63 g561 g562 g563; do grep -h "线 \|大块\|绝对验收\|盲比5\|不合格\|missing" r3/run_L37${i}g.log | cut -c1-220; done
