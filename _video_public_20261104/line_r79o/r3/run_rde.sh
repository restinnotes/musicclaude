export PUB_JREP=1 PUB_RIDSUF=_Lr79o PUB_PAR=14 PUB_RL_CUT=2
python relines.py g68C2Y g68RD g56 &
python relines.py g68C2Y g68RE g6 &
wait
python pub24.py test g68RD > r3/RD.log 2>&1 &
python pub24.py test g68RE > r3/RE.log 2>&1 &
wait
python pub24.py gate g68RD g68RE
