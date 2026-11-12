"""线真正压缩：按每段音乐有多少秒来压。主组读完就懂，次组一瞥知道有另一面。全走 gpt3。
python pub16.py press 线来源TAG 词来源TAG 新TAG      压线
python pub16.py timed TAG                            有时间压力的读者：这段时间读得完吗、只读主组接得上吗
python pub16.py rate TAG                             每段字数和每秒字数
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, JUDGES, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

P = """下面是一首器乐曲“边听边看”视频里的线：一个人经历的一件事，按段写成几组。观众在听音乐，眼睛只是扫屏幕。每段音乐只有下面写的那么多秒，这段时间里他还要看旁边的词、听音乐，一秒读不了几个字。现在线太长，读不完。

请压。目的是：观众在这段时间里读得完，读完还知道这个人此刻怎么了、为什么、和上一段怎么接上。

- 主组（rank 主）那条线是观众一定会读的。保留让因果成立的字，其余都删。一段一段只读主组，要能接成一件有发展的事。
- 次组的线观众只是瞥一眼。一个短句，让人看出这里还有另一面就够，不交代来龙去脉。主组或前面已经说过的不要再说。
- 秒数少的段压得更狠；秒数多的段也不必写满。
- 判断能不能删，只问：删掉这几个字，读者还知道他为什么这样想、接下来为什么变了吗？知道就删。修饰、重复、并列的第三件事、已交代过的前情，都删。
- 前因后果留在同一条里，不要拆成几条。短连接“才”“可”“却”“便”可以留。
- 不加定稿没有的事，不把珠子写进来。像这个人自己在说，称呼不变。不写小节数。
- 每组条数可以减少。两条其实一件事就并成一条。

只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"lines":["…"]}]}]}，每段每组都要给。

【定稿的线（只作依据，不要照抄）】
{FINAL}

【现在的线（每段的秒数、每组的 rank）】
{CUR}
"""

TIMED = """你是普通观众，边听一首钢琴曲边扫屏幕，没读过任何原文。每一段屏幕只停留下面写的秒数，这段时间里你还要听音乐。屏幕上每段有几组，每组一句白色的话和几块短词。主组的话字大，次组的话字小。

逐段回答：
1. read：这段时间里你实际能读到哪些？all（话和词都读完）、main（主组的话读完，加几块词）、part（主组的话都读不完）。
2. long：哪一句话最影响你读完，照抄；没有就留空。
3. follow：只凭你实际读到的，和上一段接得上吗？能 / 勉强 / 不能。第一段写“能”。
4. why：只凭你实际读到的，你知道这个人为什么有这种感受吗？能 / 勉强 / 不能。

只输出 JSON：{"sections":[{"sec":"S01","read":"all|main|part","long":"…","follow":"能|勉强|不能","why":"能|勉强|不能"}],"overall":"两三句话：哪里读不完，哪里压过头了读不懂"}

【屏幕】
{SCREEN}
"""


def windows(w): return {s['sec']: s['window'] for s in rd(R2/f'{w}_src.json')['sections']}


def press(a):
    w, ls, ws, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{ls}.json'); words = rd(R3/f'script_{w}_{ws}.json'); win = windows(w)
    fin = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    cur = '\n'.join(f"\n### {s['sec']}（这段 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）\n" + '\n'.join(f"idx {i}（{g['rank']}）：" + ' ｜ '.join(l['text'] for l in g.get('lines', [])) for i, g in enumerate(s['groups'])) for s in d['sections'])
    msg = P.replace('{FINAL}', fin).replace('{CUR}', cur)
    for k in range(3):
        ans = call(f'pub16_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public16-press')
        try:
            N = {s['sec']: {int(g['idx']): g['lines'] for g in s['groups']} for s in parse(ans)['sections']}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    if i in N.get(s['sec'], {}) and N[s['sec']][i]:
                        fr = [x for l in g.get('lines', []) for x in l.get('from', [])]; g['lines'] = [{'text': t, 'keys': [], 'from': fr} for t in N[s['sec']][i] if t.strip()]
            break
        except Exception as ex: print(w, '不合格', repr(ex)[:200], flush=True)
    else: return False
    for s, t in zip(d['sections'], words['sections']):
        for g, h in zip(s['groups'], t['groups']): g['beads'] = h.get('beads', [])
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True)
    if errs: wr(p.with_suffix('.try.json'), d); return False
    wr(p, d); rate((w, tag)); return True


def rate(a):
    w, tag = a; d = rd(R3/f'script_{w}_{tag}.json'); win = windows(w); ll = 0; tot = 0; rows = []
    for s in d['sections']:
        sec = win[s['sec']][1]-win[s['sec']][0]; lc = sum(len(l['text']) for g in s['groups'] for l in g.get('lines', [])); mc = sum(len(l['text']) for g in s['groups'] if g['rank'] == '主' for l in g.get('lines', [])); wc = sum(len(b['text']) for g in s['groups'] for b in g.get('beads', []))
        ll += lc; tot += sec; rows.append((s['sec'], round(sec), lc, mc, wc, round((lc+wc)/sec, 1)))
    n = sum(len(g.get('lines', [])) for s in d['sections'] for g in s['groups']); fin = sum(len(l['text']) for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    print(w, tag, f'线 {n} 条 {ll} 字（定稿 {fin}，{round(ll/fin*100)}%），每秒最快', max(r[5] for r in rows), '全曲', round((ll+sum(r[4] for r in rows))/tot, 2), flush=True)
    print('  ', ' '.join(f'{r[0]}:{r[1]}s/{r[2]}+{r[4]}字/{r[5]}' for r in rows), flush=True)


def screen(w, tag):
    win = windows(w); rows = []
    for s in rd(R3/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}（屏幕停留 {round(win[s['sec']][1]-win[s['sec']][0])} 秒）")
        for g in s['groups']:
            rows.append(f"{g['rank']}组 话：" + ' '.join(l['text'] for l in g.get('lines', [])))
            rows.append('  词：' + '  /  '.join(b['text'] for b in g.get('beads', [])))
    return '\n'.join(rows)


def timed(a):
    w, j, tag = a; p = R3/f'timed_{w}_{j}_{tag}.json'
    if not p.exists():
        for k in range(3):
            ans = call(f'pub16T_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), TIMED.replace('{SCREEN}', screen(w, tag)), JUDGES[j], 'gpt3s', 'public16-timed')
            try: r = parse(ans); assert r['sections']; wr(p, r); break
            except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    r = rd(p); from collections import Counter
    print(w, j, tag, '读到', dict(Counter(s.get('read') for s in r['sections'])), '接得上', dict(Counter(s.get('follow') for s in r['sections'])), '知道为什么', dict(Counter(s.get('why') for s in r['sections'])), flush=True); print('  ', r.get('overall', '')[:260], flush=True)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'press':
        ls, ws, tag = sys.argv[2:5]
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(press, [(w, ls, ws, tag) for w in WORKS])), flush=True)
    elif c == 'timed':
        with ThreadPoolExecutor(4) as ex: list(ex.map(timed, [(w, j, sys.argv[2]) for w in WORKS for j in JUDGES]))
    elif c == 'rate':
        for w in WORKS: rate((w, sys.argv[2]))
