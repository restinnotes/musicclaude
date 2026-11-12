"""快筛：只跑看片盲比（两种顺序）和线人话，过了再跑全套。python r3/quick.py TAG..."""
import os, sys; sys.path.insert(0, '.'); sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import pub24, vs_order, pub18
tags = sys.argv[1:]
jobs = [(f, (w, j, t, s)) for t in tags for w in pub24.WORKS for j in pub24.JUDGES for s in 'XY' for f in (pub24.vs_one, vs_order.one)]
jobs += [(pub18.lang_one, (w, j, t)) for t in tags for w in pub24.WORKS for j in pub24.JUDGES]
with ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '28'))) as ex: list(ex.map(lambda a: a[0](a[1]), jobs))
for t in tags: pub24.gate(t)
