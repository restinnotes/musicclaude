export PUB_JREP=1 PUB_RIDSUF=_Lr79o PUB_PAR=14 PUB_TF_HALF=1
python trimfeel.py g68RB g68RBH &
python trimfeel.py g68RA g68RAH &
wait
python pub24.py test g68RBH > r3/RBH.log 2>&1 &
python pub24.py test g68RAH > r3/RAH.log 2>&1 &
wait
python pub24.py gate g68RBH g68RAH
