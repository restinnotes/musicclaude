export PUB_RIDSUF=_Lr79o PUB_JREP=2
PUB_FL_NOGROW=1 python pub24.py fixlines2 g68RHH g68RHL
PUB_TF_HALF=1 python trimfeel.py g68RHL g68RHLT &
PUB_TF_HALF=1 python trimfeel.py g68RHH g68RHT &
wait
PUB_PAR=30 python r3/quick.py g68RHL g68RHLT g68RHT
