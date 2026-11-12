#!/bin/bash
# 11-12 CTRLs（只改小字，中等 13）进验收：补覆盖、走样；对主线 K28b 盲比。同时 GPT-6 版小字（加“不比原来长”）治“扫得动”。
cd /d/musicclaude/_video_public_20261104/line_r79o
bash r3/pipe_K27full.sh g68CTRLs r2e > r3/full_CTRLs.log 2>&1 &
python r3/vs5.py g68K28b g68CTRLs v5mg68CTRLs > r3/vsmain_CTRLs.log 2>&1 &
(CTRL_S_TAG=g6CTRLsc CTRL_S_WHO=g6 CTRL_S_CAP=1 python r3/ctrl_small.py > r3/ctrl_small_g6.log 2>&1 && bash r3/pipe_K27test.sh g6CTRLsc r2e > r3/pipe_g6CTRLsctest.log 2>&1) &
wait
echo "== CTRLs 覆盖走样"; tail -6 r3/full_CTRLs.log
echo "== CTRLs 对 K28b"; grep -h "盲比5" r3/vsmain_CTRLs.log | cut -c1-230
echo "== GPT-6 小字（限长）"; grep -h "绝对验收5b\|盲比5" r3/pipe_g6CTRLsctest.log | cut -c1-230
