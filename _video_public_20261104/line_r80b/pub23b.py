"""两层线的其余测：对原稿（珠子+线）的覆盖率（小字也在屏幕上，算进去）、人话（N09 开放评审 + 句式统计，只看大字）、和珠子的字面重合。
python pub23b.py cover TAG
python pub23b.py lang TAG
python pub23b.py overlap TAG [TAG...]
"""
import os, sys
os.environ.setdefault('PUB_WORKS', 'op60,op61')
import pub_cover, pub18, pub2, pub3
from pub2 import rd, WORKS, JUDGES
from concurrent.futures import ThreadPoolExecutor
R3 = pub3.OUT; R2 = pub2.OUT


def screen2(w, tag):
    rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for g in s['groups']:
            rows.append('话：'+' '.join(l['text']+(f"（小字：{l['detail']}）" if l.get('detail') else '') for l in g.get('lines', []))); rows.append('词：'+' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


pub_cover.screen = screen2


def bg(t):
    t = ''.join(c for c in t if '一' <= c <= '鿿'); return [t[i:i+2] for i in range(len(t)-1)]


def overlap(tag):
    for w in WORKS:
        src = {s['sec']: set(bg(' '.join(b['text'] for b in s['beads']))) for s in rd(R2/f'{w}_src.json')['sections']}; tot = hit = wt = wh = 0
        for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
            for g in s['groups']:
                for l in g.get('lines', []):
                    x = bg(l['text']); tot += len(x); hit += sum(i in src[s['sec']] for i in x)
                    L = set(x)
                    for b in g.get('beads', []): y = bg(b['text']); wt += len(y); wh += sum(i in L for i in y)
        print(w, tag, '大字双字在同段珠子占比', round(hit/max(1, tot), 3), '屏幕词双字在同组大字占比', round(wh/max(1, wt), 3))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'cover':
        with ThreadPoolExecutor(4) as ex: list(ex.map(pub_cover.judge, [(w, j, sys.argv[2]) for w in WORKS for j in JUDGES]))
    elif c == 'lang': pub18.lang(sys.argv[2])
    elif c == 'overlap':
        for t in sys.argv[2:]: overlap(t)
