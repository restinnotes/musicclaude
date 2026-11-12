#!/bin/bash
# 用法：r2_round.sh 基线 候选…   两首生成，再全部快筛
base=$1; shift
python pub2.py gen "$@" > r2/gen_$base.log 2>&1
for t in "$@"; do python pub2.py quick $t $base >> r2/quick_$base.log 2>&1 & 
  while [ $(jobs -r | wc -l) -ge 6 ]; do wait -n; done
done; wait
cat r2/quick_$base.log | grep -E " vs "
