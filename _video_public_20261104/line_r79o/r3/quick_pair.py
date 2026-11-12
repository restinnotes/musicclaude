"""11-08 打碎实验的快筛：新版的意思走样、整屏珠子覆盖，加任意两两盲比（vs2，两种顺序）。
python r3/quick_pair.py A:B [C:D ...]      例：python r3/quick_pair.py g68K3S:g68K3N g68K3S:g68K3A g68K3N:g68K3A
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ['PUB_BC_ALL'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24, faithful, vs2, gate2
from pub24 import WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')

pairs = [a.split(':') for a in sys.argv[1:]]
tags = sorted({t for p in pairs for t in p})
jobs = []
for t in tags:
    jobs += [('fa', (w, j, t)) for w in WORKS for j in JUDGES]
    jobs += [('bc', (w, j, t)) for w in WORKS for j in JUDGES]
for a, b in pairs:
    jobs += [('v2', (w, j, a, b, f'{a}__{b}', s)) for w in WORKS for j in JUDGES for s in 'XY']


def run(x):
    k, a = x
    try:
        if k == 'fa': faithful.one(a)
        elif k == 'bc': pub24.bead_cov(a)
        else: vs2.one(a)
    except SystemExit as e: print(e, flush=True)
    except Exception as e: print('失败', k, a, repr(e)[:150], flush=True)


with ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '24'))) as ex: list(ex.map(run, jobs))
for t in tags:
    print(f'===== {t}')
    for w in WORKS: print(f"  {w} 走样 {gate2.faith(w, t)[0]}；整屏珠子覆盖 {gate2.bcov(w, t)}（w23 {gate2.bcov(w, 'w23')}）", flush=True)
for a, b in pairs:
    for w in WORKS:
        full, st, dims = gate2.vs(w, f'{a}__{b}')
        print(f"  {a} 对 {b} {w}：稳定选前 {st['新']}/敏感 {st['敏感']}/稳定选后 {st['旧']}；分项 " + '、'.join(f"{d} {x}:{y}" for d, (x, y) in dims.items()) + ('' if full else '（未测完）'), flush=True)
