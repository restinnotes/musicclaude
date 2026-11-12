#!/bin/bash
# 11-10 K26（I02 换方向）：K26a = GPT-6 方案 1 自然句块（PUB_FRAG_RULE=nat）；K26b = GPT-6 方案 2 一屏一句（one）；GPT-5.6 的方案交回改成碎块后另跑。写手 GPT-6。写完快筛。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=r2c
PUB_FRAG_RULE=nat PUB_BL_PFX=k26 python r3/fragwrite.py g68K26a prompt_K26_g6_1.txt g6 > r3/K26a_write.log 2>&1 &
PUB_FRAG_RULE=one PUB_BL_PFX=k26 python r3/fragwrite.py g68K26b prompt_K26_g6_2.txt g6 > r3/K26b_write.log 2>&1 &
python r3/adv_k26r.py > r3/adv_k26r.log 2>&1 &
wait
cat r3/adv_k26r.log | cut -c1-1500
grep -q "泛化检查过" r3/adv_k26r.log && PUB_FRAG_RULE=nat PUB_BL_PFX=k26 python r3/fragwrite.py g68K26c prompt_K26_g56_2.txt g6 > r3/K26c_write.log 2>&1 &
grep -h -v "^\[k26" r3/K26a_write.log r3/K26b_write.log
for t in g68K26a g68K26b; do [ -f r3/s24/screen_op61_$t.json ] && [ -f r3/s24/screen_op60_$t.json ] && bash r3/pipe_K24test.sh $t > r3/pipe_${t}test.log 2>&1 & done
wait
grep -h -v "^\[k26" r3/K26c_write.log
[ -f r3/s24/screen_op61_g68K26c.json ] && [ -f r3/s24/screen_op60_g68K26c.json ] && bash r3/pipe_K24test.sh g68K26c > r3/pipe_g68K26ctest.log 2>&1
for t in g68K26a g68K26b g68K26c; do echo "## $t"; grep -E "^绝对验收4 $t|^骨架测 $t|^$t op|两位以上|^盲比4" r3/pipe_${t}test.log 2>/dev/null | cut -c1-220; done
echo "== K26 测完 $(date)"
