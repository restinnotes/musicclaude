"""11-09 晚 截图评委量尺两端的人造对照（只用于校准，不进成品）。三个已知样本（K11g、K18cM、w23S）大字都是多层长句，量尺上端没校准。
SP 极易扫（正向）：每屏只留话里的放大词作大字（一屏最多两行，每行一个词组），加三块最短的小字。内容丢很多，只测“扫不扫得到”。
SL 整段（反向）：每屏所有话和感受并成一行大段文字，不放大任何词。
python r3/ctl_scan.py 来源TAG
"""
import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pub24 import S, rd, wr, WORKS
for w in WORKS:
    d = rd(S/f'screen_{w}_{sys.argv[1]}.json'); sp = copy.deepcopy(d); sl = copy.deepcopy(d)
    for s, s2 in zip(sp['sections'], sl['sections']):
        L = [r for r in s['rows'] if r['kind'] == 'line']; F = [i for r in s['rows'] if r['kind'] == 'feel' for i in r['items']]
        rows = [{'kind': 'line', 'text': k, 'keys': [k], 'emotion': r.get('emotion'), 'from': r.get('from', [])} for r in L[:2] for k in (r.get('keys') or [])[:1]]
        short = sorted(F, key=lambda i: len(i['text']))[:3]
        if short: rows.append({'kind': 'feel', 'items': [dict(i, bars='') for i in short]})
        s['rows'] = rows or s['rows']
        txt = '；'.join([r['text'].rstrip('。') for r in s2['rows'] if r['kind'] == 'line'] + [i['text'] for r in s2['rows'] if r['kind'] == 'feel' for i in r['items']]) + '。'
        s2['rows'] = [{'kind': 'line', 'text': txt, 'keys': [], 'emotion': L[0].get('emotion') if L else '悬着', 'from': []}]
    wr(S/f'screen_{w}_{sys.argv[1]}SP.json', sp); wr(S/f'screen_{w}_{sys.argv[1]}SL.json', sl); print(w, '对照已生成')
