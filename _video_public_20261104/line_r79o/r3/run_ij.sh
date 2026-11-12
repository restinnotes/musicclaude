export PUB_RIDSUF=_Lr79o
PUB_RL_CUT=4 python relines.py g68C2Y g68RI g56 &
PUB_RL_CUT=4 python relines.py g68C2Y g68RJ g6 &
wait
PUB_TF_HALF=1 python trimfeel.py g68RI g68RIH &
PUB_TF_HALF=1 python trimfeel.py g68RJ g68RJH &
wait
PUB_JREP=2 PUB_PAR=28 python r3/quick.py g68RIH g68RJH
