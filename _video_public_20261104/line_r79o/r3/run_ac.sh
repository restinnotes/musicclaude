cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
python addcov.py g68K3 g68K3A
PUB_PAR=30 python r3/quick2.py g68K3A > r3/q_k3a.log 2>&1
python gate2.py g68K3A
