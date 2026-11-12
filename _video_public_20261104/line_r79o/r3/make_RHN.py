"""11-07 g68RHN = g68RHM，只把 op60 第 40 行（S13）改清楚：“越喜欢跟他待着”主语不清，评委“为什么”7:15 多点 S13。意思照定稿：就算听到也拿不准，越在一起越觉得时间快。
op61 与 g68RHM 逐字相同，测量文件直接复用（改名）。"""
import copy, glob, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
from pub24 import S, rd, wr, to_script
scr = copy.deepcopy(rd(S/'screen_op60_g68RHM.json')); k = -1
for s in scr['sections']:
    for x in s['rows']:
        if x['kind'] != 'line': continue
        k += 1
        if k == 40:
            x['text'] = '可就算听到了，越待在一起越觉得时间过得快，真能一直这样吗？'; x['keys'] = ['时间过得快']; print(s['sec'], x)
wr(S/'screen_op60_g68RHN.json', scr); to_script('op60', 'g68RHN', scr)
base = os.path.dirname(os.path.abspath(__file__))
for f in glob.glob(os.path.join(base, '..', '**', '*op61*g68RHM*'), recursive=True):
    g = f.replace('g68RHM', 'g68RHN')
    if not os.path.exists(g): shutil.copy2(f, g)
print('op61 复用', len(glob.glob(os.path.join(base, '..', '**', '*op61*g68RHN*'), recursive=True)))
