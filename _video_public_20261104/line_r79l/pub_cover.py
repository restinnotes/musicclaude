"""短版对原稿（定稿的珠子 + 线）的覆盖率：原稿每个要点、每条线，屏幕上留下了没有。全走 gpt3。
python pub_cover.py count TAG      只数来源：哪些珠子有词来自它（不调模型）
python pub_cover.py judge TAG      两位评委逐条判
结果：r3/cover_{w}_{j}_{TAG}.json
"""
import json, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import JUDGES, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲视频的两份文字。“原稿”是完整的：珠子（听的人当下的感受，已按句拆成要点）和线（一个人经历的事）。“短版”是给边听边扫屏幕的观众看的，每段有几组，每组一句话（线）和几块短词（词）。

请逐条判断：原稿的每个要点、每条线，它要说的意思，观众从同一段的短版上能不能得到？
- 留住：意思在，说法不同、更短都没关系。
- 部分：只留了一部分，比如留了感受没留原因，留了一头没留转折的另一头。
- 没有：短版上没有。
只看意思，纯粹描写音乐、乐器、小节的句子，只要它带的感受在就算留住。同一段里在哪一组都算。
via 写这个意思在短版的哪里：词 / 线 / 都有 / 无。

只输出 JSON：{"items":[{"id":"S01-B1-p1","verdict":"留住|部分|没有","via":"词|线|都有|无"}]}，要逐条给全，不要漏。

【短版】
{SCREEN}

【原稿】
{SOURCE}
"""


def source_list(w):
    rows = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        rows.append(f"\n### {s['sec']}\n线：")
        rows += [f"- {l['id']}：{l['text']}" for l in s['lines']]
        rows.append('珠子：')
        for b in s['beads']:
            rows += [f"- {p['id']}：{p['text']}" for p in b['points']]
    return '\n'.join(rows)


def screen(w, tag):
    rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for g in s['groups']:
            rows.append('话：'+' '.join(l['text'] for l in g.get('lines', []))); rows.append('词：'+' / '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def count(w, tag):
    src = rd(R2/f'{w}_src.json'); d = rd(R3/f'script_{w}_{tag}.json')
    used = {x for s in d['sections'] for g in s['groups'] for b in g.get('beads', []) for x in b.get('from', [])}
    beads = [b for s in src['sections'] for b in s['beads']]; pts = [p for b in beads for p in b['points']]
    hit = [b for b in beads if any(p['id'] in used for p in b['points'])]
    by = Counter(b.get('role') for b in beads); hb = Counter(b.get('role') for b in hit); must = {x['id'] for x in pub2.musts(w)}
    print(w, tag, f"珠子 {len(hit)}/{len(beads)} 颗有词来自它；要点 {sum(p['id'] in used for p in pts)}/{len(pts)}；不能掉要点 {sum(p['id'] in used for p in pts if p['id'] in must)}/{sum(p['id'] in must for p in pts)}", {k: f"{hb[k]}/{by[k]}" for k in by}, flush=True)


def judge(a):
    w, j, tag = a; p = R3/f'cover_{w}_{j}_{tag}.json'
    if not p.exists():
        msg = P.replace('{SCREEN}', screen(w, tag)).replace('{SOURCE}', source_list(w))
        for k in range(3):
            ans = call(f'pubcover_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public-cover')
            try: r = parse(ans); assert r['items']; wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); it = {x['id']: x for x in r['items']}; src = rd(R2/f'{w}_src.json')
    lines = [l['id'] for s in src['sections'] for l in s['lines']]; beads = [b for s in src['sections'] for b in s['beads']]; pts = [q['id'] for b in beads for q in b['points']]
    def c(ids): return dict(Counter((it.get(i) or {}).get('verdict', '未判') for i in ids))
    full = sum(all((it.get(q['id']) or {}).get('verdict') != '没有' for q in b['points']) and any((it.get(q['id']) or {}).get('verdict') == '留住' for q in b['points']) for b in beads)
    some = sum(any((it.get(q['id']) or {}).get('verdict') in ('留住', '部分') for q in b['points']) for b in beads)
    print(w, j, tag, '要点', c(pts), '/', len(pts), '线', c(lines), '/', len(lines), f'珠子至少沾到 {some}/{len(beads)}', '要点来自', dict(Counter((it.get(i) or {}).get('via') for i in pts)), flush=True)
    return it


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c, tag = sys.argv[1:3]
    if c == 'count':
        for w in WORKS: count(w, tag)
    else:
        with ThreadPoolExecutor(4) as ex: list(ex.map(judge, [(w, j, tag) for w in WORKS for j in JUDGES]))
