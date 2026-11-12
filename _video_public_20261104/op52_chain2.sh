#!/bin/sh
# Op.52：等 24 份 A 稿 -> N03 珠子、N04a Center 归纳同时跑。
T=/d/musicclaude/_thread_evo_20261019
L=/d/musicclaude/_video_public_20261104/qa/log
for i in $(seq 1 240); do [ "$(ls $T/works/op52/A/SRC-*.md 2>/dev/null | wc -l)" -ge 24 ] && break; sleep 30; done
[ "$(ls $T/works/op52/A/SRC-*.md 2>/dev/null | wc -l)" -ge 24 ] || { echo A稿不够; exit 1; }
cd $T
export WORK=op52 CDV=2 PYTHONIOENCODING=utf-8
python ../_bead_op61_20261020/chain.py production --work op52 > $L/op52_N03.log 2>&1 &
B=$!
( python center_from_A.py --work op52 && python center_dag.py write --work op52 && python center_dag.py spec --work op52 && python center_dag.py fit --work op52 && python center_dag.py report --work op52 ) > $L/op52_N04.log 2>&1 &
C=$!
wait $C; echo Center 退出 $?; tail -n 25 $L/op52_N04.log | cut -c1-300
wait $B; echo 珠子退出 $?; tail -n 6 $L/op52_N03.log | cut -c1-300
