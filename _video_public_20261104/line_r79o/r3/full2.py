"""11-08 DAG2 全套（按新标准）：快筛三项（走样、整屏珠子覆盖、新盲比）+ 原稿覆盖、精细体验、整屏人话；评委数由 PUB_JREP 定（全套用 2）。
python r3/full2.py TAG [TAG...]"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ['PUB_BC_ALL'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24, faithful, vs2, pub_cover
from pub24 import WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')
tags = sys.argv[1:]; jobs = []
for t in tags + ['w23']:
    jobs += [('bc', (w, j, t)) for w in WORKS for j in JUDGES] + [('la', (w, j, t)) for w in WORKS for j in JUDGES] + [('cv', (w, j, t)) for w in WORKS for j in JUDGES] + [('fi', (w, j, t)) for w in WORKS for j in JUDGES]
for t in tags:
    jobs += [('fa', (w, j, t)) for w in WORKS for j in JUDGES] + [('v2', (w, j, t, 'w23', f'{t}__w23', s)) for w in WORKS for j in JUDGES for s in 'XY']
def run(x):
    k, a = x
    try:
        if k == 'fa': faithful.one(a)
        elif k == 'bc': pub24.bead_cov(a)
        elif k == 'la': pub24.lang_all(a)
        elif k == 'cv': pub_cover.judge(a)
        elif k == 'fi': __import__('pub25').judge(a)
        else: vs2.one(a)
    except SystemExit as e: print(e, flush=True)
    except Exception as e: print('失败', k, a, repr(e)[:150], flush=True)
with ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '30'))) as ex: list(ex.map(run, jobs))
import gate2
os.environ['PUB_FULL'] = '1'
for t in tags: gate2.gate(t)
