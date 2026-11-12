export PUB_JREP=1 PUB_RIDSUF=_Lr79o PUB_PAR=14 PUB_RL_CUT=1
python relines.py g68C2Y g68RC g6 && python pub24.py test g68RC > r3/RC.log 2>&1 && python pub24.py gate g68RC
