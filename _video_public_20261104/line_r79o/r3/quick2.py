"""11-08 DAG2 快筛（按标准修订稿）：每个候选两首都跑
- 意思走样（faithful.py，严重条数）
- 整屏珠子覆盖（PUB_BC_ALL=1，大字小字都算，和 w23 同法比）
- 新盲比 vs2（对现在的旧视频 w23，两种顺序配对；分项：扫、连贯、不啰嗦、人话、为什么、单独成立、细腻）
python r3/quick2.py TAG [TAG...]
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ['PUB_BC_ALL'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24, faithful, vs2
from pub24 import WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')

tags = sys.argv[1:]
jobs = []
for t in tags:
    jobs += [('fa', (w, j, t)) for w in WORKS for j in JUDGES]
    jobs += [('bc', (w, j, t)) for w in WORKS for j in JUDGES]
    jobs += [('v2', (w, j, t, 'w23', f'{t}__w23', s)) for w in WORKS for j in JUDGES for s in 'XY']
jobs += [('bc', (w, j, 'w23')) for w in WORKS for j in JUDGES]


def run(x):
    k, a = x
    try:
        if k == 'fa': faithful.one(a)
        elif k == 'bc': return (a, pub24.bead_cov(a))
        else: vs2.one(a)
    except SystemExit as e: print(e, flush=True)
    except Exception as e: print('失败', k, a, repr(e)[:150], flush=True)


with ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '28'))) as ex: res = [r for r in ex.map(run, jobs) if r]
bc = {}
for (w, j, t), v in res: bc.setdefault((w, t), []).append(v)
for t in tags:
    print(f'===== {t}')
    faithful.summary(t)
    for w in WORKS:
        a, b = bc.get((w, t), []), bc.get((w, 'w23'), [])
        print(f"{t} {w} 整屏珠子覆盖 {round(sum(a)/max(1, len(a)), 3)}（w23 {round(sum(b)/max(1, len(b)), 3)}）", flush=True)
    vs2.report(f'{t}__w23')
