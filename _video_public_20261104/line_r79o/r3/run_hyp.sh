cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_RIDSUF=_Lr79o PUB_JREP=1
python vs2.py g68BA g68BAx80b hypBA &
python vs2.py g68BB g68BBx80b hypBB &
python -c "
import sys; sys.stdout.reconfigure(encoding='utf-8'); import pub24
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(16) as ex: list(ex.map(pub24.lang_all, [(w,j,t) for t in ['g68BA','g68BAx80b','g68BB','g68BBx80b'] for w in pub24.WORKS for j in pub24.JUDGES]))
" &
wait
