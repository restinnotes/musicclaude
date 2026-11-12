#!/bin/bash
# 11-12 用户：“按照流程没有阻塞的东西都可以一起开吧”。互不依赖的四件同时跑。
cd /d/musicclaude/_video_public_20261104/line_r79o
python r3/replay_diag.py > r3/replay_diag.log 2>&1 &
python r3/openabs5.py g68K28b run2 > r3/abs_K28b_run2.log 2>&1 &
python r3/openabs5.py g68K28b run3 > r3/abs_K28b_run3.log 2>&1 &
python r3/openabs5.py g68L32a run2 > r3/abs_L32a_run2.log 2>&1 &
(python r3/ctrl_small.py > r3/ctrl_small.log 2>&1 && bash r3/pipe_K27test.sh g68CTRLs r2e > r3/pipe_g68CTRLstest.log 2>&1) &
wait
echo "== 回放"; grep -A3 "^====" r3/replay_diag.log | cut -c1-260
echo "== 波动"; grep -h "绝对验收5b" r3/abs_K28b_run*.log r3/abs_L32a_run2.log | cut -c1-160
echo "== 小字对照"; grep -h "绝对验收5b\|盲比5" r3/pipe_g68CTRLstest.log | cut -c1-220
