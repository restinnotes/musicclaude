"""线逐字用定稿，一条线一组；词按已有匹配（每颗珠子最接近哪条线）放到那条线旁边。纯脚本，不调模型。
python pub19.py 词来源TAG 新TAG
"""
import sys
import pub2, pub3
from pub2 import WORKS, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT


def one(w, src, tag):
    d = rd(R3/f'script_{w}_{src}.json'); s0 = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}; out = {k: v for k, v in d.items() if k != 'sections'}; out['sections'] = []
    for s in d['sections']:
        o = s0[s['sec']]; lines = o['lines']; after = {p['id']: b['after'] for b in o['beads'] for p in b['points']}
        emo = {}; main_ids = []
        for g in s['groups']:
            for l in g.get('lines', []):
                for x in l.get('from', []):
                    emo.setdefault(x, g['emotion'])
                    if g['rank'] == '主' and x not in main_ids: main_ids.append(x)
        fallback = next(g['emotion'] for g in s['groups'] if g['rank'] == '主')
        mi = next((i for i, l in enumerate(lines) if l['id'] in main_ids), 0)
        groups = [{'rank': '主' if i == mi else '次', 'emotion': emo.get(l['id'], fallback), 'lines': [{'text': l['text'], 'keys': [], 'from': [l['id']]}], 'beads': []} for i, l in enumerate(lines)]
        for g in s['groups']:
            base = next((i for i, l in enumerate(lines) if any(l['id'] in x.get('from', []) for x in g.get('lines', []))), mi)
            for b in g.get('beads', []):
                f = (b.get('from') or [None])[0]; i = after.get(f, base); i = i if 0 <= i < len(groups) else base
                groups[i]['beads'].append({k: v for k, v in b.items() if k != 'emotion'})
        out['sections'].append({**{k: v for k, v in s.items() if k != 'groups'}, 'groups': groups})
    errs = pub3.check(w, out); print(w, tag, '问题', errs[:5], '组', sum(len(s['groups']) for s in out['sections']), '无词的线', sum(not g['beads'] for s in out['sections'] for g in s['groups']), flush=True)
    wr(R3/f'script_{w}_{tag}.json', out); wr(R2/f'script_{w}_{tag}.json', out)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for w in WORKS: one(w, sys.argv[1], sys.argv[2])
