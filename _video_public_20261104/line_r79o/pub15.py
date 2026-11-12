"""线局部修：不拆条，前因后果留在同一条里；按评委原话补丢的环节，再从别处省回字数。全走 gpt3。
python pub15.py 线来源TAG 词来源TAG 新TAG
"""
import sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3, pub13
from pub2 import G6, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲视频里的线：一个人经历的一件事，按段写成几条。“定稿”完整、读者读得懂；“压缩版”给边听边扫屏幕的观众看。

评委拿压缩版和定稿比，指出压缩版的毛病：心理发展的环节丢了，单独读时不知道他为什么这样想、接下来为什么变了（原话附后）。但也有评委说过：把一件事拆成好几条会零碎、承接感变弱，所以不要拆。

请局部修改压缩版，只改有问题的条，其余一字不动：
- 评委说丢了的环节，确实影响“他为什么这样想、接下来为什么变了”的，从定稿里用最少的字补回来。一个小句就够。
- 前因和后果放在同一条里，用“才”“可”“却”“便”“这回”这样的短连接接上，不要拆成几条。段与段之间也要接得上：这一段第一条要让人知道它从上一段的哪里来。
- 为了不变长，同时删掉这段里可有可无的修饰、重复的话；并列三四件事的，只留决定他下一步的那两件。这段改完的总字数不比现在多，最好更少。{LOOSE}
- 不加定稿没有的事，不把珠子写进来。像这个人自己在说，称呼不变。不写小节数。

只输出 JSON：{"edits":[{"sec":"S01","old":"压缩版里那一条的原文，逐字照抄","new":"改后的一条"}]}

【定稿的线】
{FINAL}

【压缩版（每段按组列出，｜隔开各条）】
{CUR}

【评委比对定稿时的意见（这些段定稿更好）】
{WHY}
"""


def one(a):
    w, ls, ws, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{ls}.json'); words = rd(R3/f'script_{w}_{ws}.json')
    fin = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    cur = '\n'.join(f"{s['sec']} 第{i}组：" + ' ｜ '.join(l['text'] for l in g.get('lines', [])) for s in d['sections'] for i, g in enumerate(s['groups']))
    import os
    msg = P.replace('{LOOSE}', '（评委点名丢了环节的段，为补回环节可以多几个字，但不要把并列的话堆回来。评委说次序倒了的，把次序调回来。）' if os.environ.get('LOOSE') else '').replace('{FINAL}', fin).replace('{CUR}', cur).replace('{WHY}', pub13.why(w, ls))
    for k in range(3):
        ans = call(f'pub15_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public15-lines')
        try:
            E = parse(ans)['edits']; n = 0
            for e in E:
                s = next(x for x in d['sections'] if x['sec'] == e['sec']); done = False
                for g in s['groups']:
                    for l in g.get('lines', []):
                        if l['text'] == e['old']: l['text'] = e['new']; n += 1; done = True; break
                    if done: break
                if not done: print(w, '没找到', e['old'][:40], flush=True)
            print(w, '线改', n, '/', len(E), flush=True); break
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    else: return False
    for s, t in zip(d['sections'], words['sections']):
        for g, h in zip(s['groups'], t['groups']): g['beads'] = h.get('beads', [])
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True)
    ll = [l['text'] for s in d['sections'] for g in s['groups'] for l in g.get('lines', [])]; print(w, tag, '线', len(ll), '均字', sum(map(len, ll))//len(ll), '总字', sum(map(len, ll)), flush=True)
    if errs: wr(p.with_suffix('.try.json'), d); return False
    wr(p, d); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    ls, ws, tag = sys.argv[1:4]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, ls, ws, tag) for w in WORKS])), flush=True)
