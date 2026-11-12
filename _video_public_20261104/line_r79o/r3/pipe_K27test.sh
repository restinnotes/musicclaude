#!/bin/bash
# 快筛。11-11 晚 I15 提速（准则第九节第 3 条“贵的测量放后面”）：先只跑开放评审（三位）、绝对验收 5b、盲比、骨架测；
# 覆盖（cov3、big2）、走样（faith）这几项贵的，只给过了绝对验收和退步检查的候选补：bash r3/pipe_K27full.sh TAG [原料目录]。
# 11-11 一天调用 36 小时里，这三项占 8.3 小时，多数花在明显失败的候选上。旧版留在 pipe_K27test_备份1111晚.sh。
# 用法：bash r3/pipe_K27test.sh TAG [原料目录，默认 r2c]；QS_FULL=1 时一次跑全。
cd /d/musicclaude/_video_public_20261104/line_r79o
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PUB_SRC=${2:-r2c}
T=$1
python r3/skeleton.py $T run1 > r3/skel_$T.log 2>&1 &
OF_ARGON=${OF_ARGON-1} python r3/open_free.py $T > r3/openF_$T.log 2>&1 &   # 11-11 开放评审三位：GPT-6、GPT-5.6、Argon
python r3/openabs5.py $T run1 > r3/oa5_${T}.log 2>&1 &
python r3/vs5.py g68K11g $T v5b$T > r3/vs5_$T.log 2>&1 &
wait
python r3/openabs5.py sum $T run1
python r3/skeleton.py sum $T run1
python r3/vs5.py sum v5b$T
echo "== $T 快筛测完 $(date)"
[ "$QS_FULL" = "1" ] && bash r3/pipe_K27full.sh $T ${2:-r2c}
