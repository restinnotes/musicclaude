export PUB_JREP=1 PUB_RIDSUF=_Lr79o PUB_PAR=14
python relines.py g68C2Y g68RA g6 &
python relines.py g68C2Y g68RB g56 &
wait
python pub24.py test g68RA > r3/RA.log 2>&1 &
python pub24.py test g68RB > r3/RB.log 2>&1 &
wait
python pub24.py gate g68RA g68RB
