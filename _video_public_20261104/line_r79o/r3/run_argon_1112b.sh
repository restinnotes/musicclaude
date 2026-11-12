#!/bin/bash
# 11-12 用户加了 Argon 账号：补开放评审第三位（Argon），并跑 Argon 版“限长 + 保内容”小字（g68CTRLsk2），和 GPT-6 版（g6CTRLsk）同一份要求对比
cd /d/musicclaude/_video_public_20261104/line_r79o
OF_ARGON=1 python r3/open_free.py g68CTRLh > r3/openF_argon_CTRLh.log 2>&1 &
(CTRL_S_TAG=g68CTRLsk2 CTRL_S_WHO=argon CTRL_S_CAP=1 CTRL_S_KEEP=1 python r3/ctrl_small.py > r3/ctrl_small_ak.log 2>&1 && bash r3/pipe_K27test.sh g68CTRLsk2 r2e > r3/pipe_g68CTRLsk2test.log 2>&1 && bash r3/pipe_K27full.sh g68CTRLsk2 r2e > r3/full_g68CTRLsk2.log 2>&1) &
# GPT-6 两版的快筛跑完后再补 Argon（open_free 按评委缓存，只补缺的）
while ps aux | grep -q "[r]un_CTRLs_g6"; do sleep 60; done
for v in g6CTRLsc2 g6CTRLsk2; do OF_ARGON=1 python r3/open_free.py $v > r3/openF_argon_$v.log 2>&1 & done
wait
echo "== Argon 版小字"; grep -h "绝对验收5b\|盲比5" r3/pipe_g68CTRLsk2test.log | cut -c1-230; grep -h "确认核心\|两位以上" r3/full_g68CTRLsk2.log | cut -c1-200
