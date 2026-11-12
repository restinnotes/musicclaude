cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
python r3/adv_fix.py g68K3 g6 prompt_BLg63.txt BLg63b > r3/fixK3.log 2>&1 &
python r3/adv_fix.py g68K4 g56 prompt_BLg561.txt BLg561b > r3/fixK4.log 2>&1 &
wait
grep -h "诊断\|Traceback\|Error" r3/fixK3.log r3/fixK4.log
for p in BLg63b BLg561b; do
  who=g6; case $p in BLg56*) who=g56;; esac
  case $p in BLg63b) t=g68K3b;; BLg561b) t=g68K4b;; esac
  PUB_BL_PROMPT=prompt_$p.txt python blend.py $t $who > r3/$t.log 2>&1 &
done
wait
grep -h "连贯\|不合格\|泛化" r3/g68K3b.log r3/g68K4b.log
PUB_PAR=30 python r3/quick2.py g68K3b g68K4b > r3/q_k34b.log 2>&1
python gate2.py g68K3b g68K4b
