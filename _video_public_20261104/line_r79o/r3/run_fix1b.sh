cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
PUB_BL_PROMPT=prompt_BLg63b.txt python blend.py g68K3b g6 > r3/g68K3b.log 2>&1 &
PUB_BL_PROMPT=prompt_BLg561b.txt python blend.py g68K4b g56 > r3/g68K4b.log 2>&1 &
wait
grep -h "连贯\|不合格\|泛化\|Error" r3/g68K3b.log r3/g68K4b.log
PUB_PAR=30 python r3/quick2.py g68K3b g68K4b > r3/q_k34b.log 2>&1
python gate2.py g68K3b g68K4b
