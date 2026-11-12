cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
i=0
for p in BLg61 BLg62 BLg63 BLg561 BLg562 BLg563; do
  i=$((i+1)); who=g6; case $p in BLg56*) who=g56;; esac
  PUB_BL_PROMPT=prompt_$p.txt python blend.py g68K$i $who > r3/k$i.log 2>&1 &
done
wait
grep -h "连贯\|不合格\|泛化" r3/k?.log
PUB_PAR=30 python r3/quick2.py g68K1 g68K2 g68K3 g68K4 g68K5 g68K6
