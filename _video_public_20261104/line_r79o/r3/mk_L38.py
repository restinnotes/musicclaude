"""11-12 交回后“改”的方案落成 scheme（schemes/L38{批}{ID}.json）。没改的层沿用原方案（L{批}_{ID}_*），再没有就用旧提示词。不自动补“每段都要写”（交回后的方案可能有意让某段不说话）。
python r3/mk_L38.py 34g62"""
import json, sys
from pathlib import Path
SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes'); bi = sys.argv[1]; b, i = bi[:2], bi[2:]
sc = json.loads((SCH/'L32a.json').read_text(encoding='utf-8')); sc['name'] = f'L38{bi}'; sc['note'] = f'L38{bi}：11-12 交回提出者后的修改版（handback_all.py）'
def f(k, d):
    for c in (f'L38_{bi}_{k}.txt', f'L{b}_{i}_{k}.txt'):
        if (SCH/c).exists(): return c
    return d
for st in sc['steps']:
    st['prompt_file'] = {'A1': f('A1', 'Q6_A1.txt'), 'A2': f('A2', 'Q6_A2.txt'), 'A3': 'Q6_A3.txt', 'A4': f('A4', 'Q15_A4.txt')}[st['id']]
(SCH/f'L38{bi}.json').write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding='utf-8')
print(bi, [s['prompt_file'] for s in sc['steps']])
