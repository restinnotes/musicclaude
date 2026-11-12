"""11-08 测量误差：同一版本换调用编号重测，看整屏珠子覆盖、整屏人话两次差多少（K3M2 与 K3A 内容只差小节号，船歌却 0.666 对 0.68、7.08 对 7.17）。
python r3/noise.py TAG...   （TAG 是复制出的同内容版本，如 w23b g68K3Ab g68K3M2b）"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ['PUB_BC_ALL'] = '1'; os.environ['PUB_BC_NOCACHE'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24, gate2
from pub24 import WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')
tags = sys.argv[1:]
jobs = [(k, (w, j, t)) for t in tags for w in WORKS for j in JUDGES for k in ('bc', 'la')]
def run(x):
    k, a = x
    try: (pub24.bead_cov if k == 'bc' else pub24.lang_all)(a)
    except Exception as e: print('失败', k, a, repr(e)[:150], flush=True)
with ThreadPoolExecutor(24) as ex: list(ex.map(run, jobs))
for t in tags:
    o = t[:-1]
    for w in WORKS: print(f"{w} {o}：覆盖 第一次 {gate2.bcov(w, o)} 第二次 {gate2.bcov(w, t)}；整屏人话 第一次 {gate2.lall(w, o)[0]} 第二次 {gate2.lall(w, t)[0]}", flush=True)
