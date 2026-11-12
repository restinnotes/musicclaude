#!/bin/bash
# 11-10 盲比第五版校准：自比（应平）、K11g 对 K11gU（原文只切块：human 应平）、K26c 对 K26cT（同块电报腔：human 应稳定选 K26c）、K11g 对 CL/CV（旧对照：core、fine 应仍选 K11g）。过了再重跑 K25a、K26a、K26c 对 K11g。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
PUB_FRAG_RULE=chain python r3/ctl_tele.py g68K26c g68K26cT > r3/ctl_tele.log 2>&1 &
python r3/vs5.py g68K11g g68K11g v5self > /dev/null 2>&1 &
python r3/vs5.py g68K11g g68K11gU v5K11gU > /dev/null 2>&1 &
python r3/vs5.py g68K11g g68K11gCL v5CL > /dev/null 2>&1 &
python r3/vs5.py g68K11g g68K11gCV v5CV > /dev/null 2>&1 &
wait
cat r3/ctl_tele.log
python r3/vs5.py g68K26c g68K26cT v5K26cT > /dev/null 2>&1
for n in v5self v5K11gU v5CL v5CV v5K26cT; do python r3/vs5.py sum $n; done
echo "== 盲比5 校准完 $(date)"
