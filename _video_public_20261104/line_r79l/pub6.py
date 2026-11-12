"""第三步：线不动，回到原珠子把词重新拆出来，要具体、有感觉。全走 gpt3。
python pub6.py 来源TAG 新TAG
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, WORKS, call, parse, rd, source_matched, wr

P = """下面是一首器乐曲视频的文字。观众边听边扫屏幕，屏幕上每段有几组，每组一句线（不要改）和一把散开的词（词来自珠子，也就是听的人当下的感受）。

现在的问题：词太少、太抽象，像书面的概括，失去了原珠子里的感觉。请回到原珠子，把每组的词重新拆出来。

- 直接从原珠子里拿最有感觉的词，留住具体的东西：身体的感觉、画面、比喻、一声问。比如“心里空荡荡的，像走进一间搬空的屋子，说话都有回声”，拆成“空荡荡”“搬空的屋子”“回声”。不要概括成“失落”这样的抽象词。
- 一颗珠子最打动人的地方，就拆成它的几个词，放在一起，读者扫过去就能想象那一刻。其余珠子可以不用。
- 主组可以有一小把，次组少一些。整屏仍然要一眼扫得完，同一个感受不说两遍。
- 是词或很短的词组，不是半句，没有逗号，除问号外不带标点。离开句子也要有感觉。不写音乐术语。
- 每个词写 emotion（和所在组不同时才写，只能从下面选）和 from（来自哪条原珠子要点的 id）：
"""+pub3.EMO_DESC+"""

只输出 JSON。按输入的段和组的顺序，idx 是组在这一段里的序号（从 0 开始）：
{"sections":[{"sec":"S01","groups":[{"idx":0,"beads":[{"text":"…","emotion":"…","from":["S01-B1-p1"]}]}]}]}

【现在每段的组和线】
{CUR}

【原文】
{SRC}
"""


def one(a):
    w, src, tag = a; p = pub3.OUT/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(pub3.OUT/f'script_{w}_{src}.json')
    cur = [{'sec': s['sec'], 'groups': [{'idx': i, 'rank': g['rank'], 'emotion': g['emotion'], 'lines': [l['text'] for l in g.get('lines', [])]} for i, g in enumerate(s['groups'])]} for s in d['sections']]
    msg = P.replace('{CUR}', json.dumps(cur, ensure_ascii=False)).replace('{SRC}', source_matched(w))
    for k in range(3):
        ans = call(f'pub6_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public6-words')
        try:
            r = {s['sec']: {g['idx']: g['beads'] for g in s['groups']} for s in parse(ans)['sections']}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    g['beads'] = [{'text': b['text'], 'keys': [], 'from': b.get('from', []), **({'emotion': b['emotion']} if b.get('emotion') else {})} for b in r[s['sec']].get(i, [])]
            errs = pub3.check(w, d)
        except Exception as e:
            print(w, '解析失败', repr(e)[:200], flush=True); continue
        print(w, tag, '问题', len(errs), errs[:4], flush=True)
        wr(p.with_suffix('.try.json'), d)
        if not errs: wr(p, d); return True
    return False


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
    pub3.marks(tag)
