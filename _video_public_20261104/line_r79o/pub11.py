"""线和词分开重做，互不借用：线只从定稿的线来压，词只从定稿的珠子来拆。分组沿用来源版本。全走 gpt3。
python pub11.py 来源TAG 新TAG
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

LINES = """下面是一首器乐曲“边听边看”视频里的线：一个人经历的一件事，按段写成几条。观众边听边扫屏幕，定稿的线太长，请压成大众版。

- 只用这条线自己的意思。不看别的、不从任何听感里拿东西，不加定稿没有的想法、动作、感受和身体反应。
- 删重复、删修饰、删已经交代过的。留下：这个人此刻怎么了，为什么，和前面是什么关系。
- 判断能不能删，只问一件事：删掉这部分，读者还知道他为什么这样想、接下来为什么变了吗？不知道就不能删。
- 比定稿明显短，一句话扫完。比如“因为怕打扰对方，这几天我一直没有主动联系，其实心里很想知道对方过得好不好”，压成“怕打扰对方，我一直没联系，其实很想知道对方好不好”。
- 像这个人自己在说。人称和称呼跟定稿一样。一条说一件事。
- 同一段的几条多半是一起描述这一段，不要写成先后。跨段的发展要接得上：只读每段主组的线，从头到尾是一件有发展的事。
- 两条确实说同一件事可以并成一条。不能掉清单里的意思要留下。

按下面的分组输出，每组里的线从它列的 id 来。只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"lines":[{"text":"…","from":["S01-1"]}]}]}]}

【分组】
{GROUPS}

【定稿的线】
{FINAL}

【不能掉清单（线）】
{KEEP}
"""

WORDS = """下面是一首器乐曲“边听边看”视频的屏幕文字。每组有线（不要改）和几块词。观众边听音乐边扫屏幕，只有一眼。词来自珠子：听的人当下的感受。

现在的问题是不少词观众读不懂：离开句子不知道在说什么，或者只是书面总结。请重新写每组的词。

- 一块词就是一个完整的感受，由一两个或两三个词组成，扫过去就知道是什么感觉。比如“空荡荡”和“回声”放在一起。
- 一个词离开旁边的词读不懂，就和旁边的词放在一起，或者换个说法。可以是很短的词组或一声问，不要写成解释句。
- 留身体的感觉、具体的画面、心里闪过的话。不写抽象总结，不写音乐术语。
- 只来自定稿的珠子，不加新的比喻和情节。同一个感受只说一遍。不是每颗珠子都要留，主组可以多些，次组少些，整屏要一眼扫得完。
- 同一块的词 from 相同。除问号外不带标点，不带逗号。
- 每个词写 emotion（和所在组不同时才写，只能从下面选）：
"""+pub3.EMO_DESC+"""

只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"beads":[{"text":"…","emotion":"…","from":["S01-B1-p1"]}]}]}]}

【每段的组、线、现在的词】
{CUR}

【观众读不懂或嫌长的词】
{BAD}

【定稿的珠子】
{BEADS}
"""


def dedupe(d):
    """同一段里一条线整句包含另一条线时，从长的那条去掉重复的部分。"""
    n = 0
    for s in d['sections']:
        ls = [l for g in s['groups'] for l in g.get('lines', [])]
        for a in ls:
            for b in ls:
                core = b['text'].rstrip('。？！；，')
                if a is not b and len(a['text']) > len(b['text']) and core in a['text']:
                    rest = a['text'].replace(core, '', 1).strip('。；，、 ')
                    if len(rest) >= 6: a['text'] = rest+'。'; n += 1
    return n


def beads_only(w):
    rows = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for b in s['beads']:
            rows += [f"- {p['id']}：{p['text']}" for p in b['points']]
    return '\n'.join(rows)


def lines_only(w):
    rows = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        rows.append(f"\n### {s['sec']}"); rows += [f"- {l['id']}：{l['text']}" for l in s['lines']]
    return '\n'.join(rows)


def ask(rid, msg, stage):
    for k in range(3):
        ans = call(rid+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', stage)
        try:
            return {s['sec']: {int(g['idx']): g for g in s['groups']} for s in parse(ans)['sections']}
        except Exception as e: print(rid, '不合格', repr(e)[:200], flush=True)
    return None


def one(a):
    w, src, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{src}.json')
    ids = {l['id'] for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines']}
    groups = [{'sec': s['sec'], 'groups': [{'idx': i, 'rank': g['rank'], 'lines': sorted({x for l in g.get('lines', []) for x in l.get('from', []) if x in ids})} for i, g in enumerate(s['groups'])]} for s in d['sections']]
    keep = '\n'.join(f"- {x['id']}：{x['text']}" for x in pub2.musts(w) if x['id'] in ids)
    cur = [{'sec': s['sec'], 'groups': [{'idx': i, 'rank': g['rank'], 'emotion': g['emotion'], 'lines': [l['text'] for l in g.get('lines', [])], 'words': [b['text'] for b in g.get('beads', [])]} for i, g in enumerate(s['groups'])]} for s in d['sections']]
    bad = sorted({x for j in ('g6', 'g56') for s in rd(R3/f'read_{w}_{j}_{src}.json')['sections'] for x in s.get('unclear', [])+s.get('too_long', [])})
    with ThreadPoolExecutor(2) as ex:
        fl = ex.submit(ask, f'pub11L_{w}_{tag}', LINES.replace('{GROUPS}', json.dumps(groups, ensure_ascii=False)).replace('{FINAL}', lines_only(w)).replace('{KEEP}', keep), 'public11-lines')
        fw = ex.submit(ask, f'pub11W_{w}_{tag}', WORDS.replace('{CUR}', json.dumps(cur, ensure_ascii=False)).replace('{BAD}', '、'.join(bad)).replace('{BEADS}', beads_only(w)), 'public11-words')
        L, B = fl.result(), fw.result()
    if not L or not B: return False
    for s in d['sections']:
        for i, g in enumerate(s['groups']):
            g['lines'] = [{'text': l['text'], 'keys': [], 'from': l.get('from', [])} for l in L[s['sec']][i]['lines']] if i in L[s['sec']] else g['lines']
            if i in B[s['sec']]: g['beads'] = [{'text': b['text'], 'keys': [], 'from': b.get('from', []), **({'emotion': b['emotion']} if b.get('emotion') else {})} for b in B[s['sec']][i]['beads']]
    dedupe(d)
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True); wr(p.with_suffix('.try.json'), d)
    if errs: return False
    wr(p, d); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
