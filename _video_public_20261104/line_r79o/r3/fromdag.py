"""11-11 把 DAG 写线流水线（_thread_evo_20261019/pipe.py）新写出的线，换进 DAG2 的原料：珠子、分段、Center 照抄 r2e，线换成新写的。
线的对应珠子取写线那一步自己标的 covers（只留 r2e 里还在的珠子）。读原始输出 runs/sc{TAG}_{作品}_A4/output.txt。
python r3/fromdag.py TAG NEW       例：python r3/fromdag.py L31a r2la
"""
import json, os, sys, copy, re
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import R2, rd, parse, WORKS
sys.stdout.reconfigure(encoding='utf-8')
RUNS = Path('D:/musicclaude/_thread_evo_20261019/runs')

if __name__ == '__main__':
    tag, new = sys.argv[1], sys.argv[2]; out = R2.parent/new; out.mkdir(exist_ok=True)
    for w in WORKS:
        raw = (RUNS/f'sc{tag}_{w}_A4'/'output.txt').read_text(encoding='utf-8')
        r = parse(raw); got = {str(s['sec']).split('：')[0].split(':')[0].strip(): s for s in r['segments']}   # 11-11 有的写线输出把段号写成“S01：第 1–3 小节”
        src = copy.deepcopy(rd(R2/f'{w}_src.json')); n = chars = cov = 0
        for s in src['sections']:
            bids = {b['id'] for b in s['beads']}; seg = got.get(s['sec']) or {'items': []}; idmap = {}; lines = []   # 11-12：允许线在某段不说话（空段）
            for k, it in enumerate(seg['items'], 1):
                i = f"{s['sec']}-{k}"
                if isinstance(it.get('id'), str): idmap[it['id']] = i
                beads = [b for b in (it.get('covers') or []) if b in bids]; cov += bool(beads)
                lines.append({'id': i, 'text': it['text'].strip(), 'beads': beads, 'refs': [c for c in (it.get('cite') or []) if isinstance(c, str)]})
                n += 1; chars += len(it['text'])
            s['lines'] = lines; s['relation'] = seg.get('relation') or s.get('relation')
        (out/f'{w}_src.json').write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding='utf-8')
        print(w, new, '线', n, '条', chars, '字；标了对应珠子的', cov, '条', flush=True)
