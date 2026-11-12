export PUB_JREP=2 PUB_RIDSUF=_Lr79o PUB_PAR=16
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import pub18
from pub2 import WORKS
with ThreadPoolExecutor(4) as ex: list(ex.map(pub18.lang_one, [(w, j, 'FINAL') for w in WORKS for j in ('g6s','g56s')]))
print('定稿线人话补测完')
" &
python pub24.py test g68RAH > r3/RAH2.log 2>&1 &
python pub24.py test g68RBH > r3/RBH2.log 2>&1 &
wait
python pub24.py gate g68RAH g68RBH
