cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=2 PUB_LA_CAL=2
python addcov.py g68K3A g68K3A2 > r3/ac2.log 2>&1
PUB_PAR=30 python r3/full2.py g68K3A g68K3A2 > r3/full_k3a.log 2>&1
grep -A4 "^== " r3/full_k3a.log
