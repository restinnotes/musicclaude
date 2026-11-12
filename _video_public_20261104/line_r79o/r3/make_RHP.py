"""11-07 g68RHP = g68RHN，op60 S13 第 41、42 行：原因（怕连这样待着都没了）和结果（少露些心意）放进同一行，用定稿原话。原注：g68RHP = g68RHN，只把 op60 第 40 行（S13）改清楚：“越喜欢跟他待着”主语不清，评委“为什么”7:15 多点 S13。意思照定稿：就算听到也拿不准，越在一起越觉得时间快。
op61 与 g68RHN 逐字相同，测量文件直接复用（改名）。"""
import copy, glob, os, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
from pub24 import S, rd, wr, to_script
scr = copy.deepcopy(rd(S/'screen_op60_g68RHN.json')); k = -1
for s in scr['sections']:
    for x in s['rows']:
        if x['kind'] != 'line': continue
        k += 1
        if k == 41:
            x['text'] = '起初他怕自己的需要给对方添负担，如今更怕对方哪天不再需要他。'; x['keys'] = ['不再需要他']; print(s['sec'], x)
        if k == 42:
            x['text'] = '怕连这样待着都没了，他想：少露些心意，会不会少疼些？'; x['keys'] = ['少露些心意']; print(s['sec'], x)
wr(S/'screen_op60_g68RHP.json', scr); to_script('op60', 'g68RHP', scr)
base = os.path.dirname(os.path.abspath(__file__))
for f in glob.glob(os.path.join(base, '..', '**', '*op61*g68RHN*'), recursive=True):
    g = f.replace('g68RHN', 'g68RHP')
    if not os.path.exists(g): shutil.copy2(f, g)
print('op61 复用', len(glob.glob(os.path.join(base, '..', '**', '*op61*g68RHP*'), recursive=True)))
