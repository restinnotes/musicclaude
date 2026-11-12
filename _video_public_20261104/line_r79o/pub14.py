"""词太多太重复时只做减法：模型从现有的词里挑，不新写。线不动。全走 gpt3。
python pub14.py 来源TAG 新TAG
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, wr
R3 = pub3.OUT

SEL = """下面是一首器乐曲“边听边看”视频的屏幕文字。每段几组，每组是线（一个人经历的事）和一些短词（听的人当下的感受）。观众边听音乐边扫屏幕，只有一眼。现在词太多，一个感受说了好几遍，观众扫不完。

请只做减法：每组挑出留下的词，其余去掉。不要改字，不要新写。

- 同一个感受、同一个画面只留说得最好的一个说法，其余都去掉。
- 优先留：一扫就懂的身体感觉、具体的事、心里闪过的话。优先去：要想一下才懂的、读着像评语的、只在说声音怎么样的。
- 主组留几个，次组留一两个。每组留下的词整体要让人一眼扫完，又能感到这组和那句线是一回事，也能感到这段的情绪在变。
- 不能掉清单里的感受，至少留一个说法（清单按原稿写，意思留下就算）。

只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"keep":[0,3]}]}]}，keep 是留下的词的编号。

【不能掉清单（珠子）】
{KEEP}

【屏幕文字】
{CUR}
"""


def one(a):
    w, src, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{src}.json')
    pids = {x['id'] for s in rd(pub2.OUT/f'{w}_src.json')['sections'] for b in s['beads'] for x in b['points']}
    keep = '\n'.join(f"- {x['text']}" for x in pub2.musts(w) if x['id'] in pids)
    rows = []
    for s in d['sections']:
        rows.append(f"\n### {s['sec']}")
        for i, g in enumerate(s['groups']):
            rows.append(f"第{i}组（{g['rank']}）线：" + ' '.join(l['text'] for l in g.get('lines', [])))
            rows += [f"  {n}. {b['text']}" for n, b in enumerate(g.get('beads', []))]
    msg = SEL.replace('{KEEP}', keep).replace('{CUR}', '\n'.join(rows))
    for k in range(3):
        ans = call(f'pub14_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public14-select')
        try:
            K = {s['sec']: {int(g['idx']): g['keep'] for g in s['groups']} for s in parse(ans)['sections']}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    if i in K.get(s['sec'], {}):
                        g['beads'] = [b for n, b in enumerate(g.get('beads', [])) if n in set(K[s['sec']][i])]
            errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True)
            ws = [b['text'] for s in d['sections'] for g in s['groups'] for b in g.get('beads', [])]
            print(w, tag, '词', len(ws), '总字', sum(map(len, ws)), flush=True)
            if not errs: wr(p, d); return True
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
