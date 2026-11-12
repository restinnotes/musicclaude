cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=2 PUB_LA_CAL=2
PUB_PAR=20 python r3/full2.py g68K3A2 > r3/full_k3a2.log 2>&1
python vs2.py g68K3A2 g68K3A K3A2vsK3A > r3/k3a2_vs_k3a.log 2>&1
grep -A4 "^== " r3/full_k3a2.log; grep "稳定选" r3/k3a2_vs_k3a.log
