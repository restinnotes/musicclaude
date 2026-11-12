"""词太少、覆盖不够时往回提：把减法前的词都作候选，尽量多留。线不动，词放到匹配的那条线旁边。全走 gpt3。
python pub20.py 现版TAG 候选TAG 新TAG
"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲“边听边看”视频的文字。每段有几条线（一个人经历的事）。旁边要放短词（听的人当下的感受），来自原稿的珠子。观众边听音乐边扫屏幕，词是散开的，一扫就有感觉，不用读完。

现在词太少，原稿很多珠子的感受屏幕上没有了。下面给了每颗珠子的候选词。请重新挑，尽量多留：

- 每颗珠子至少留一块词；不能掉清单里的要点都要有词。
- 只有这几种可以去掉：和别的词说的是同一个感受（只留说得最好的）；只在描述声音怎么样、没有听的人的感受；读着像评语，要想一下才懂；离开上下文不知道在说什么。
- 一颗珠子写了几种不同的感受，就留几块，不要只留一块。
- 候选里没有合适的（或者某个要点的感受没有词），就从这个要点的原文拆一个：一两个或两三个短词，是一个完整的感受，一扫就懂；用原文的字，不加原文没有的比喻和情节；除问号外不带标点；不写音乐术语和小节数。

只输出 JSON：{"sections":[{"sec":"S01","keep":[0,3,5],"new":[{"text":"…","from":"S01-B1-p2"}]}]}。keep 是留下的候选编号，每段编号独立。

【不能掉清单（珠子要点）】
{KEEP}

【每段：线、每颗珠子的要点和候选词】
{ROWS}
"""


def one(a):
    w, cur, pool, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{cur}.json'); pl = rd(R3/f'script_{w}_{pool}.json'); src = {s['sec']: s for s in rd(R2/f'{w}_src.json')['sections']}
    pids = {x['id'] for s in src.values() for b in s['beads'] for x in b['points']}; keep = '\n'.join(f"- {x['id']}：{x['text']}" for x in pub2.musts(w) if x['id'] in pids)
    rows = []; cands = {}
    for s, ps in zip(d['sections'], pl['sections']):
        sec = s['sec']; o = src[sec]; seen = set(); lst = []
        for sc in (s, ps):
            for g in sc['groups']:
                for b in g.get('beads', []):
                    if b['text'] not in seen: seen.add(b['text']); lst.append(b)
        cands[sec] = lst; byp = {}
        for n, b in enumerate(lst):
            byp.setdefault((b.get('from') or [''])[0], []).append(n)
        rows.append(f"\n### {sec}\n线：" + ' ｜ '.join(l['text'] for l in o['lines']))
        for bd in o['beads']:
            rows.append(f"珠子 {bd['id']}（{bd.get('role')}）")
            for x in bd['points']:
                rows.append(f"  {x['id']}：{x['text']}\n    候选：" + ('、'.join(f"{n}={lst[n]['text']}" for n in byp.get(x['id'], [])) or '无'))
        rest = [n for k, v in byp.items() if k not in {x['id'] for bd in o['beads'] for x in bd['points']} for n in v]
        if rest: rows.append('其他候选：' + '、'.join(f"{n}={lst[n]['text']}" for n in rest))
    msg = P.replace('{KEEP}', keep).replace('{ROWS}', '\n'.join(rows))
    for k in range(3):
        ans = call(f'pub20_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public20-widen')
        try: R = {s['sec']: s for s in parse(ans)['sections']}; break
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    else: return False
    nw = 0
    for s in d['sections']:
        sec = s['sec']; o = src[sec]; after = {x['id']: bd['after'] for bd in o['beads'] for x in bd['points']}; old = {b['text']: i for i, g in enumerate(s['groups']) for b in g.get('beads', [])}; r = R.get(sec, {})
        for g in s['groups']: g['beads'] = []
        chosen = [cands[sec][n] for n in r.get('keep', []) if 0 <= n < len(cands[sec])]
        chosen += [{'text': x['text'], 'keys': [], 'from': [x.get('from')] if x.get('from') else []} for x in r.get('new', []) if x.get('text')]; nw += len(r.get('new', []))
        for b in chosen:
            f = (b.get('from') or [None])[0]; i = after.get(f, old.get(b['text'], 0)); i = i if 0 <= i < len(s['groups']) else 0
            s['groups'][i]['beads'].append({k: v for k, v in b.items() if k != 'emotion'})
    errs = pub3.check(w, d); print(w, tag, '问题', errs[:5], flush=True)
    ws = [b for s in d['sections'] for g in s['groups'] for b in g.get('beads', [])]; used = {x for b in ws for x in b.get('from', [])}; beads = [b for s in src.values() for b in s['beads']]; pts = [x for b in beads for x in b['points']]
    print(w, tag, '词', len(ws), '新拆', nw, '字', sum(len(b['text']) for b in ws), '珠子有词', sum(any(x['id'] in used for x in b['points']) for b in beads), '/', len(beads), '要点有词', sum(x['id'] in used for x in pts), '/', len(pts), '无词的线', sum(not g['beads'] for s in d['sections'] for g in s['groups']), flush=True)
    if errs: wr(p.with_suffix('.try.json'), d); return False
    wr(p, d); wr(R2/f'script_{w}_{tag}.json', d); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cur, pool, tag = sys.argv[1:4]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, cur, pool, tag) for w in WORKS])), flush=True)
