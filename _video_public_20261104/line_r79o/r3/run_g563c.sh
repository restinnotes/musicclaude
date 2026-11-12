#!/bin/bash
# 11-12 只改大块的全曲去重（GPT-5.6 交回），底稿 = 主线 g68CTRLsk2F（小字沿用），Argon 写；新形式下完整测 + 对主线盲比
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2e
python r3/handback_g563c.py > r3/handback_g563c.log 2>&1 || exit 1
cat r3/handback_g563c.log | cut -c1-300
PUB_FRAG_LINEONLY=1 PUB_FRAG_RULE=std9 bash r3/pipe_K27one.sh g68M2D prompt_L34g563c.txt argon "40,5,30,6,3,5" - g68CTRLsk2F r2e > r3/run_M2D.log 2>&1
v=g68M2D
python r3/openabs5.py $v run2 > r3/abs_${v}_2.log 2>&1 &
python r3/vs5.py g68CTRLsk2F $v v5fmM2D > r3/vs_${v}_vs_main.log 2>&1 &
bash r3/pipe_K27full.sh $v r2e > r3/full_$v.log 2>&1 &
wait
echo "== $v"; grep -h "大块\|绝对验收5b\|盲比5" r3/run_M2D.log r3/abs_${v}_2.log | cut -c1-220
echo "== 对主线"; grep -h "盲比5" r3/vs_${v}_vs_main.log | cut -c1-220
echo "== 覆盖走样"; grep -h "确认核心\|两位以上" r3/full_$v.log | cut -c1-220
