export PUB_JREP=1 PUB_RIDSUF=_Lr79o PUB_PAR=14
python trimfeel.py g68RB g68RBF &
python trimfeel.py g68RD g68RDF &
wait
python pub24.py test g68RBF > r3/RBF.log 2>&1 &
python pub24.py test g68RDF > r3/RDF.log 2>&1 &
wait
python pub24.py gate g68RBF g68RDF
