#!/bin/sh
# 新作品：从定稿的珠子一路做到大众版。线逐字用定稿。这条串联脚本的最终版还没有从头整条跑过，各步都单独跑过。
# sh public_flow.sh 作品 线TAG "Center"
W=$1; E=$2; C=$3
cd /d/musicclaude/_video_public_20261104
L=qa/log/flow_$W; mkdir -p $L
export PUB_WORKS=$W PUB_WORK=$W WORK=$W PYTHONIOENCODING=utf-8
step() { [ -f $L/$STEP.ok ] && return 0; echo "== $1 $(date +%H:%M)"; shift; "$@" > $L/$STEP.log 2>&1 || { echo "失败 $STEP"; tail -n 5 $L/$STEP.log | cut -c1-300; exit 1; }; touch $L/$STEP.ok; grep -v " ok " $L/$STEP.log | tail -n 3 | cut -c1-240; }
STEP=struct; step 整理珠子 python op52_up.py struct
STEP=lines; step 写线 python op52_up.py lines $E "$C"
STEP=src; step 匹配 python op52_up.py src $E
STEP=rank; step 独立排序 python pub2.py rank
STEP=f0; step 分组和情绪 python pub4.py f0
STEP=f0e; step 读词评审 python -c "import pub_eval; pub_eval.run('f0', lite=True)"
STEP=f1; step 拆词 python pub11.py f0 f1
STEP=f1s; step 词做减法 python pub14.py f1 f1s
STEP=f5; step 线逐字用定稿 python pub19.py f1s f5
STEP=f6; step 按覆盖提词 python pub20.py f5 f1 f6
STEP=f6c; step 对原稿覆盖 python pub_cover.py judge f6
STEP=f6b; step 盲读 python pub12.py test f6
STEP=f6m; step 标音符 python -c "import pub3; pub3.marks('f6')"
STEP=f6x; step 明确指向 python pub18.py explicit f6 f6
STEP=f6l; step 交界 python pub9.py f6
STEP=f6q; step 版面 python qa/layout6.py $W f6
STEP=film; step 全片 python film_v6.py render --work $W --tag f6 --out out/全片/${W}_大众版_f6.mp4
