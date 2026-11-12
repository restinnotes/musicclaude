export PUB_RIDSUF=_Lr79o PUB_PAR=16
PUB_RL_CUT=3 python relines.py g68C2Y g68RG g6 &
PUB_RL_CUT=3 python relines.py g68C2Y g68RH g56 &
wait
PUB_TF_HALF=1 python trimfeel.py g68RG g68RGH &
PUB_TF_HALF=1 python trimfeel.py g68RH g68RHH &
wait
export PUB_JREP=2
python pub24.py test g68RGH > r3/RGH.log 2>&1 &
python pub24.py test g68RHH > r3/RHH.log 2>&1 &
wait
python pub24.py gate g68RGH g68RHH
