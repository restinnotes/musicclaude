"""11-08 分段覆盖测法的校准：w23、K3M2 两首各用 4 位评委按 3 段测，和整首测法两次的结果比（平均是否在误差内、K3M2 与 w23 的先后是否一致），并比单次耗时。"""
import os, sys
os.environ['PUB_BC_ALL'] = '1'; os.environ['PUB_JREP'] = '1'; os.environ['PUB_BC_SPLIT'] = '3'
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24
from pub24 import S, rd, WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')
tags = sys.argv[1:] or ['w23', 'g68K3M2']
jobs = [(w, j, t) for t in tags for w in WORKS for j in JUDGES]
with ThreadPoolExecutor(len(jobs)) as ex: list(ex.map(lambda a: pub24.bead_cov(a), jobs))
def m(pre, w, t):
    xs = []
    for j in JUDGES:
        p = S/f'{pre}_{w}_{j}_{t}.json'
        if p.exists(): it = rd(p)['items']; xs.append(round(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)), 3))
    return xs, (round(sum(xs)/len(xs), 3) if xs else None)
for t in tags:
    for w in WORKS:
        print(f"{w} {t}：整首测法 第一次 {m('beadcovA', w, t)} 第二次 {m('beadcovA', w, t+'b')}；分段测法 {m('beadcovAP3', w, t)}", flush=True)
