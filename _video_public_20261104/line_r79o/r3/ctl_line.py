"""11-10 晚 绝对验收第五版的正向对照 LN（只用于校准，不进成品）：拿一版屏幕稿，每屏的“话”全部换成这一段线的原句（一句一块，按线的顺序、
出现秒数依次 0、3、6…），小块、旁注不动。线是一个人在往下讲，用来看新评委会不会把本来接得上的大字也报成“跳”。
python r3/ctl_line.py 来源TAG   → r3/s24/screen_{作品}_{来源TAG}LN.json（原料按 PUB_SRC）
"""
import sys, copy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pub24 import S, R2, rd, wr, WORKS
sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    tag = sys.argv[1]
    for w in WORKS:
        d = copy.deepcopy(rd(S/f'screen_{w}_{tag}.json')); src = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}
        for s in d['sections']:
            old = [r for r in s['rows'] if r['kind'] == 'line']; emo = old[0].get('emotion', '') if old else ''
            new = []
            for k, ln in enumerate(src[s['sec']]['lines']):
                r = {'kind': 'line', 'text': ln['text'], 'keys': [], 'emotion': emo, 'from': [ln['id']]}
                if k: r['at'] = 3.0*k
                new.append(r)
            s['rows'] = new + [r for r in s['rows'] if r['kind'] != 'line']
        wr(S/f'screen_{w}_{tag}LN.json', d); print(w, '已写', len(d['sections']), '屏')
