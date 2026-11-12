export PUB_RIDSUF=_Lr79o PUB_JREP=2
PUB_PAR=28 python r3/vs_only.py g68RGH g68RHH
PUB_PAR=16 python pub24.py test g68RGH > r3/RGH.log 2>&1 &
PUB_PAR=16 python pub24.py test g68RHH > r3/RHH.log 2>&1 &
wait
python pub24.py gate g68RGH g68RHH
