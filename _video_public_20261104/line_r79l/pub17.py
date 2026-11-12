"""压完之后修两件事：线按评委原话改人话（不变长）；词用已有的短词补原稿完全丢掉的要点（不调模型）。
python pub17.py 线来源TAG 词来源TAG 短词库TAG 覆盖结果TAG 新TAG
"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲视频里的线：一个人经历的一件事。这一版为了让观众边听边读得完，已经压得很短。评委说有些句子压完不像人话了（原话附后），也有观众说某些段不知道这个人为什么会这样（附后）。

请局部修改，只改被点名的句子，其余一字不动：
- 改成这个人自己平常会说的话：不要书面词、不要省掉主语后读着像提纲、不要把几件事用分号硬接。
- 被点名“不知道为什么”的段，从定稿里用最少的字带上原因。
- 改完不能明显变长。这段时间有限，整段的字数最多多一点点。
- 不加定稿没有的事，称呼不变，不写小节数，不要拆成几条。

只输出 JSON：{"edits":[{"sec":"S01","old":"原文逐字照抄","new":"改后的一条"}]}

【定稿的线（依据）】
{FINAL}

【现在的线】
{CUR}

【评委说不像人话的地方】
{PLAIN}

【观众说不知道为什么的段】
{WHY}
"""


def plain_notes(w, tag):
    rows = {}
    for j in ('g6', 'g56'):
        for seat in ('newX', 'newY'):
            p = R2/f'tvote_{w}_{j}_{tag}_{seat}.json'
            if not p.exists(): continue
            old = 'Y' if seat == 'newX' else 'X'
            for s in rd(p).get('sections', []):
                if s.get('plain') == old and s.get('plain_why'): rows.setdefault(s['sec'], []).append(s['plain_why'])
    return '\n'.join(f"{k}：" + ' / '.join(v) for k, v in sorted(rows.items()))


def why_notes(w, tag):
    rows = {}
    for j in ('g6', 'g56'):
        p = R3/f'timed_{w}_{j}_{tag}.json'
        if p.exists():
            r = rd(p); rows.setdefault('总评', []).append(r.get('overall', ''))
            for s in r['sections']:
                if s.get('why') != '能': rows.setdefault(s['sec'], []).append(f"判“{s.get('why')}”")
    return '\n'.join(f"{k}：" + ' / '.join(v) for k, v in sorted(rows.items()))


def fill_words(w, d, pool_tag, cov_tag):
    """两位评委都判“没有”的要点：短词库里有来自它的词，就补一个回来，放在所在段词最少的组。"""
    bad = None
    for j in ('g6', 'g56'):
        it = {x['id'] for x in rd(R3/f'cover_{w}_{j}_{cov_tag}.json')['items'] if x.get('verdict') == '没有'}
        bad = it if bad is None else bad & it
    pool = rd(R3/f'script_{w}_{pool_tag}.json'); n = 0; added = []
    for s, ps in zip(d['sections'], pool['sections']):
        have = {x for g in s['groups'] for b in g.get('beads', []) for x in b.get('from', [])}; texts = {b['text'] for g in s['groups'] for b in g.get('beads', [])}
        for i, pg in enumerate(ps['groups']):
            for b in pg.get('beads', []):
                f = (b.get('from') or [None])[0]
                if f in bad and f not in have and b['text'] not in texts:
                    tg = s['groups'][i]; tg.setdefault('beads', []).append(b); have.add(f); texts.add(b['text']); n += 1; added.append(b['text'])
    print(w, '都判没有的要点', len(bad), '补回词', n, added[:40], flush=True)


def one(a):
    w, ls, ws, pool, cov, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{ls}.json'); words = rd(R3/f'script_{w}_{ws}.json')
    fin = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    cur = '\n'.join(f"{s['sec']} 第{i}组（{g['rank']}）：" + ' ｜ '.join(l['text'] for l in g.get('lines', [])) for s in d['sections'] for i, g in enumerate(s['groups']))
    msg = P.replace('{FINAL}', fin).replace('{CUR}', cur).replace('{PLAIN}', plain_notes(w, ls)).replace('{WHY}', why_notes(w, ls))
    for k in range(3):
        ans = call(f'pub17_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public17-plain')
        try:
            E = parse(ans)['edits']; n = 0
            for e in E:
                s = next(x for x in d['sections'] if x['sec'] == e['sec'])
                for g in s['groups']:
                    for l in g.get('lines', []):
                        if l['text'] == e['old']: l['text'] = e['new']; n += 1
            print(w, '线改', n, '/', len(E), flush=True); break
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    else: return False
    for s, t in zip(d['sections'], words['sections']):
        for g, h in zip(s['groups'], t['groups']): g['beads'] = list(h.get('beads', []))
    fill_words(w, d, pool, cov)
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True)
    if errs: wr(p.with_suffix('.try.json'), d); return False
    wr(p, d); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ls, ws, pool, cov, tag = sys.argv[1:6]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, ls, ws, pool, cov, tag) for w in WORKS])), flush=True)
