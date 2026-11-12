"""只跑看片盲比（原顺序 + 交换顺序）并按配对报告。python r3/vs_only.py TAG..."""
import sys; sys.path.insert(0, '.'); sys.stdout.reconfigure(encoding='utf-8')
from concurrent.futures import ThreadPoolExecutor
import pub24, vs_order
tags = sys.argv[1:]
jobs = [(f, (w, j, t, s)) for t in tags for w in pub24.WORKS for j in pub24.JUDGES for s in 'XY' for f in (pub24.vs_one, vs_order.one)]
with ThreadPoolExecutor(int(__import__("os").environ.get("PUB_PAR", "16"))) as ex: list(ex.map(lambda a: a[0](a[1]), jobs))
for t in tags: vs_order.report(t)
