#!/bin/bash
# 11-10 第 2 次交回后：K26c3（GPT-5.6，chain3）先写；GPT-6 的方案交回改成碎块后由我核对检查规则再写 K26a3。写手 GPT-6，快筛用 pipe_K26test.sh（盲比第五版）。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
python r3/adv_k26x2r.py > r3/adv_k26x2r.log 2>&1 &
PUB_FRAG_RULE=chain3 PUB_BL_PFX=k26y python r3/fragwrite.py g68K26c3 prompt_K26x2_g56.txt g6 > r3/K26c3_write.log 2>&1
grep -v "^\[k26y" r3/K26c3_write.log
[ -f r3/s24/screen_op61_g68K26c3.json ] && [ -f r3/s24/screen_op60_g68K26c3.json ] && bash r3/pipe_K26test.sh g68K26c3 > r3/pipe_g68K26c3test.log 2>&1
grep -E "^绝对验收4 g68K26c3|^骨架测 g68K26c3|^g68K26c3 op|两位以上|^盲比5" r3/pipe_g68K26c3test.log | cut -c1-220
wait
echo "== K26c3 测完 $(date)"
