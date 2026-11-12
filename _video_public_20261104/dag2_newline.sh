#!/bin/bash
# 11-06：DAG2 接线的新版本。用法：bash dag2_newline.sh 线TAG [prep|run]
# prep：在 line_<TAG>/ 建工作副本（代码、输入、现在视频 w23 的屏幕和 g68 提示词），用新线生成输入（V2.01）。不调模型。
# run：现在的视频按新原稿重测基线；用 g68 提示词写屏幕稿 → 修两轮线的人话 → 每步全套测试 → 门槛对照。
set -e
TAG=$1; MODE=${2:-run}
SRC=/d/musicclaude/_video_public_20261104; EVO=/d/musicclaude/_thread_evo_20261019; DST=$SRC/line_$TAG
export PUB_RIDSUF=_L$TAG PUB_WORKS=op60,op61
if [ "$MODE" = prep ]; then
  (cd $EVO && [ -f evaluations/v6fix/合写_op60_$TAG.md ] || python v6weave.py $TAG)
  mkdir -p $DST/r2 $DST/r3/s24 $DST/r3/audit21 $DST/qa/log
  cp $SRC/*.py $SRC/大众版标准.md $SRC/用户判定.md $DST/
  cp -r $SRC/input $SRC/plans $DST/ 2>/dev/null || true
  cp $SRC/r3/script_op6?_w23.json $DST/r3/; cp $SRC/r3/script_op6?_w23.json $DST/r2/ 2>/dev/null || true
  cp $SRC/r3/s24/prompt_g68.txt $DST/r3/s24/
  cd $DST && LINE_TAG=$TAG python -c "import pub2; pub2.prepare()"
  python - <<P
import json
for w in ('op60','op61'):
    d=json.load(open('r2/'+w+'_src.json',encoding='utf-8')); print(w,'段',len(d['sections']),'线',sum(len(s['lines']) for s in d['sections']),'珠',sum(len(s['beads']) for s in d['sections']))
P
  exit 0
fi
if [ "$MODE" = run2 ]; then
  # 11-06 晚：新流程。评委翻倍（PUB_JREP=1）；修线用第二版（同时看人话问题和看片盲比理由），两轮。
  cd $DST; export PUB_JREP=1 PUB_PAR=14
  python - > qa/log/baseline.log 2>&1 <<'Q'
import sys; sys.argv=['x']
from concurrent.futures import ThreadPoolExecutor
import pub24, pub_cover, pub21, pub18
J=[(w,j,'w23') for w in pub24.WORKS for j in pub24.JUDGES]
with ThreadPoolExecutor(12) as ex:
    list(ex.map(pub_cover.judge, J)); list(ex.map(pub24.bead_cov, J)); list(ex.map(pub21.audit, J)); list(ex.map(pub24.lang_all, J))
    list(ex.map(pub18.lang_one, [(w,j,'FINAL') for w in pub24.WORKS for j in pub24.JUDGES]))
Q
  python pub24.py write g68 > qa/log/write_g68.log 2>&1
  python pub24.py precheck g68
  python pub24.py test g68 > qa/log/test_g68.log 2>&1
  python pub24.py fixlines2 g68 g68C > qa/log/fix_g68C.log 2>&1
  python pub24.py test g68C > qa/log/test_g68C.log 2>&1
  python pub24.py fixlines2 g68C g68C2 > qa/log/fix_g68C2.log 2>&1
  python pub24.py test g68C2 > qa/log/test_g68C2.log 2>&1
  python pub24.py gate g68 g68C g68C2
  exit 0
fi
cd $DST
# 基线：现在的视频（w23）对新原稿的覆盖、珠子严格覆盖、精细体验、整屏人话；新线本身的人话（FINAL）
python - > qa/log/baseline.log 2>&1 <<'P'
import sys; sys.argv=['x']
from concurrent.futures import ThreadPoolExecutor
import pub24, pub_cover, pub21, pub18
J=[(w,j,'w23') for w in pub24.WORKS for j in pub24.JUDGES]
with ThreadPoolExecutor(10) as ex:
    list(ex.map(pub_cover.judge, J)); list(ex.map(pub24.bead_cov, J)); list(ex.map(pub21.audit, J)); list(ex.map(pub24.lang_all, J))
    list(ex.map(pub18.lang_one, [(w,j,'FINAL') for w in pub24.WORKS for j in pub24.JUDGES]))
P
python pub24.py write g68 > qa/log/write_g68.log 2>&1
python pub24.py precheck g68
python pub24.py test g68 > qa/log/test_g68.log 2>&1
python pub24.py fixlines g68 g68L > qa/log/fix_g68L.log 2>&1
python pub24.py test g68L > qa/log/test_g68L.log 2>&1
python pub24.py fixlines g68L g68L2 > qa/log/fix_g68L2.log 2>&1
python pub24.py test g68L2 > qa/log/test_g68L2.log 2>&1
python pub24.py gate g68 g68L g68L2
