#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
(CTRL_S_TAG=g6CTRLsc2 CTRL_S_WHO=g6 CTRL_S_CAP=1 python r3/ctrl_small.py > r3/ctrl_small_g6c.log 2>&1 && bash r3/pipe_K27test.sh g6CTRLsc2 r2e > r3/pipe_g6CTRLsc2test.log 2>&1 && bash r3/pipe_K27full.sh g6CTRLsc2 r2e > r3/full_g6CTRLsc2.log 2>&1) &
(CTRL_S_TAG=g6CTRLsk2 CTRL_S_WHO=g6 CTRL_S_CAP=1 CTRL_S_KEEP=1 python r3/ctrl_small.py > r3/ctrl_small_g6k.log 2>&1 && bash r3/pipe_K27test.sh g6CTRLsk2 r2e > r3/pipe_g6CTRLsk2test.log 2>&1 && bash r3/pipe_K27full.sh g6CTRLsk2 r2e > r3/full_g6CTRLsk2.log 2>&1) &
wait
for v in g6CTRLsc2 g6CTRLsk2; do echo "== $v"; grep -h "绝对验收5b\|盲比5" r3/pipe_${v}test.log | cut -c1-230; grep -h "确认核心\|两位以上" r3/full_$v.log | cut -c1-200; done
echo "== CTRLs 绝对验收第二遍"; grep -h "绝对验收5b" r3/abs_CTRLs_run2.log | cut -c1-160
