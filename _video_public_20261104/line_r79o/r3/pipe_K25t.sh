#!/bin/bash
# 11-10 03:05 K25 快筛（重排）：写完的三个先测，两条并行；K25b 船歌写完再测（写稿进程 3828 仍在跑）。
cd /d/musicclaude/_video_public_20261104/line_r79o
bash r3/pipe_K24test.sh g68K25bR > r3/pipe_g68K25bRtest.log 2>&1 &
bash r3/pipe_K24test.sh g68K25aR > r3/pipe_g68K25aRtest.log 2>&1 &
wait
bash r3/pipe_K24test.sh g68K25a > r3/pipe_g68K25atest.log 2>&1 &
for i in $(seq 1 240); do [ -f r3/s24/screen_op60_g68K25b.json ] && break; ps -p 3828 >/dev/null || break; sleep 30; done
[ -f r3/s24/screen_op60_g68K25b.json ] && bash r3/pipe_K24test.sh g68K25b > r3/pipe_g68K25btest.log 2>&1 &
wait
for t in g68K25bR g68K25aR g68K25a g68K25b; do echo "## $t"; grep -E "$t|两位以上|盲比4|覆盖" r3/pipe_${t}test.log 2>/dev/null | cut -c1-220; done
echo "== K25 测完 $(date)"
