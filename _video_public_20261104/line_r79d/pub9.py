"""一颗珠子可能同时对应几条线：模型逐块判断，放到两条带的交界。全走 gpt3。
python pub9.py TAG      结果写到 r3/links_{w}_{TAG}.json
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, source_matched, wr

P = """下面是一首器乐曲“边听边看”视频每段的屏幕文字。每段有几组，每组是一句或几句线（一个人经历的事）和几块词（每块来自同一颗珠子，也就是听的人当下的一种感受）。

现在每块词只归在一组里，但一种感受可能同时和这段的另一组线有关。屏幕可以把这样的词块放在两组的交界，让观众看出它两边都沾。

请逐段判断：哪些词块除了所在的组，还和这段的另一组线有关？
- 判断标准：这块词写的感受，在另一组线里也能找到情境相近的处境或原因，读者看到会觉得说得通。相关就算，不要求逐项解释。
- 词块里纯粹的声音、画面、比喻本身不算，只看人的感受那一层。
- 只是这段都在说同一件事不算；要真的能在那一组的线上落下来。
- 交界是少数。只标最明显、去掉交界观众就会误解的那几块；很多段一块也没有。说得通但不突出的，不标。

只输出 JSON，只列有第二组的词块：{"links":[{"sec":"S01","chunk":"S01-0-1","also":1,"why":"一句话"}]}
chunk 照抄下面的编号，also 是另一组的序号。

【屏幕文字】
{CUR}

【原文】
{SRC}
"""


def chunks(beads):
    out = []; seen = {}
    for b in beads:
        k = (b.get('from') or [b['text']])[0]
        if k not in seen: seen[k] = []; out.append(seen[k])
        seen[k].append(b)
    return out


def one(a):
    w, tag = a; p = pub3.OUT/f'links_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(pub3.OUT/f'script_{w}_{tag}.json'); cur = []; idx = {}
    for s in d['sections']:
        gs = []
        for i, g in enumerate(s['groups']):
            cs = []
            for n, ch in enumerate(chunks(g.get('beads', []))):
                cid = f"{s['sec']}-{i}-{n}"; idx[cid] = ch[0]['text']; cs.append({'chunk': cid, 'words': [b['text'] for b in ch]})
            gs.append({'group': i, 'rank': g.get('rank'), 'lines': [l['text'] for l in g.get('lines', [])], 'chunks': cs})
        cur.append({'sec': s['sec'], 'groups': gs})
    msg = P.replace('{CUR}', json.dumps(cur, ensure_ascii=False)).replace('{SRC}', source_matched(w))
    for k in range(3):
        ans = call(f'pub9_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public9-links')
        try:
            r = parse(ans); good = []
            for x in r['links']:
                _, gi, _ = x['chunk'].rsplit('-', 2) if False else (None, None, None)
                parts = x['chunk'].split('-')
                if x['chunk'] in idx and int(parts[1]) != int(x['also']): good.append({**x, 'first': idx[x['chunk']], 'group': int(parts[1])})
            wr(p, {'links': good}); print(w, '交界词块', len(good), '/', len(idx), flush=True); return True
        except Exception as e: print(w, '不合格', repr(e)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, sys.argv[1]) for w in WORKS])), flush=True)
