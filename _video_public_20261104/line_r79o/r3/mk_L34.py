"""11-11 晚：把 adv_loop 顾问方案落成写线 scheme（schemes/L34{ID}.json）。没改的层用旧提示词（Q6_A1、Q6_A2、Q15_A4）；A4 末尾补“每段都要写”（L32、L33 的教训：不补会交白卷或缺段）。
python r3/mk_L34.py g61"""
import json, sys
from pathlib import Path
SCH = Path('D:/musicclaude/_thread_evo_20261019/schemes'); i = sys.argv[1]
PATCH = (SCH/'L33_g6_A4b.txt').read_text(encoding='utf-8').split('【每段都要写】')[1]
sc = json.loads((SCH/'L32a.json').read_text(encoding='utf-8')); sc['name'] = f'L34{i}'; sc['note'] = f'L34{i}：11-11 晚 I02 换方向（adv_loop.py 方案 {i}）'
f = lambda k, d: f'L34_{i}_{k}.txt' if (SCH/f'L34_{i}_{k}.txt').exists() else d
a4 = f('A4', 'Q15_A4.txt'); t = (SCH/a4).read_text(encoding='utf-8')
if '【每段都要写】' not in t: t += '\n\n【每段都要写】' + PATCH
(SCH/f'L34_{i}_A4b.txt').write_text(t, encoding='utf-8')
for st in sc['steps']:
    st['prompt_file'] = {'A1': f('A1', 'Q6_A1.txt'), 'A2': f('A2', 'Q6_A2.txt'), 'A3': 'Q6_A3.txt', 'A4': f'L34_{i}_A4b.txt'}[st['id']]
(SCH/f'L34{i}.json').write_text(json.dumps(sc, ensure_ascii=False, indent=1), encoding='utf-8')
print(i, [s['prompt_file'] for s in sc['steps']])
