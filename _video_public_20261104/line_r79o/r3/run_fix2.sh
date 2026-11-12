cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
python r3/adv_fix.py g68K3b g6 prompt_BLg63b.txt BLg63c g68K3 > r3/fixK3c.log 2>&1 &
python r3/adv_fix.py g68K4b g56 prompt_BLg561b.txt BLg561c g68K4 > r3/fixK4c.log 2>&1 &
wait
grep -h "诊断\|Traceback\|Error" r3/fixK3c.log r3/fixK4c.log
PUB_BL_PROMPT=prompt_BLg63c.txt python blend.py g68K3c g6 > r3/g68K3c.log 2>&1 &
PUB_BL_PROMPT=prompt_BLg561c.txt python blend.py g68K4c g56 > r3/g68K4c.log 2>&1 &
wait
grep -h "连贯\|不合格\|泛化\|Error" r3/g68K3c.log r3/g68K4c.log
PUB_PAR=30 python r3/quick2.py g68K3c g68K4c > r3/q_k34c.log 2>&1
python gate2.py g68K3c g68K4c
