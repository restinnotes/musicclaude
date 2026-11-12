#!/bin/bash
python r3/gate.py || exit 1
# 11-11 晚：跑一套 adv_loop 方案到快筛。bash r3/run_L35.sh ID（如 g61、g562）
# 改了写线层的：写线 → 换进原料（r2L35ID）→ 屏幕稿；只改屏幕稿写法的：直接在 r2e 上写。对照：L31c（旧写线不打磨）、K28b（主线）。
cd /d/musicclaude/_video_public_20261104/line_r79o
ID=$1; SCH=/d/musicclaude/_thread_evo_20261019/schemes; SRC=r2e
if ls $SCH/L35_${ID}_A1.txt $SCH/L35_${ID}_A2.txt $SCH/L35_${ID}_A4.txt 2>/dev/null | grep -q .; then
  python r3/mk_L35.py $ID
  (cd /d/musicclaude/_thread_evo_20261019 && python pipe.py run schemes/L35$ID.json L35$ID 2>&1 | grep -v "^\[" | tail -5)
  PUB_SRC=r2e python r3/fromdag.py L35$ID r2L35$ID || { echo "== L35$ID 写线没出来"; exit 1; }
  SRC=r2L35$ID
fi
P=prompt_K28b.txt
[ -f $SCH/L35_${ID}_WRITE.txt ] && cp $SCH/L35_${ID}_WRITE.txt r3/s24/prompt_L35$ID.txt && P=prompt_L35$ID.txt
PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68L35$ID $P argon "40,5,30,6,3,5" - g68K28b $SRC
