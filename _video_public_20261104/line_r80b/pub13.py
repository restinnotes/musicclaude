"""成品局部修：线按评委意见拆短补因果；词只改盲读没对上或半懂的块，其余不动。全走 gpt3。
python pub13.py 来源TAG 新TAG        两首同跑
"""
import json, sys
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, QUICK, WORKS, call, parse, rd, wr
R3 = pub3.OUT; R2 = pub2.OUT

LINES = """下面是一首器乐曲视频里的线：一个人经历的一件事，按段写成几条。“定稿”完整、读者读得懂；“压缩版”是给边听边扫屏幕的观众看的。观众一眼只能读一小句。

压缩版现在两头都有问题：
1. 有些条太长，一条塞了几件事，扫不完。
2. 和定稿比，有些地方丢了他心理发展的环节，单独读时不知道他为什么这样想、接下来为什么变了（评委原话附后）。

请局部修改压缩版，只改有问题的条，其余一字不动：
- 一条塞了几件事的，拆成几条，每条只说一件事，一扫读完，单独读也懂。拆开不是把一个意思说两遍。
- 评委说丢了的环节，确实影响“他为什么这样想、接下来为什么变了”的，从定稿里用最少的字补回来。
- 同时删掉可有可无的修饰和重复。修完这段的总字数不应比现在多。
- 不加定稿没有的事，不把珠子写进来。像这个人自己在说，称呼不变。
- 同段几条是一起描述这一段的，不是先后。不要加“后来”“接着”“然后”。
- 改动的条保留原来的 from。

只输出 JSON：{"edits":[{"sec":"S01","old":"压缩版里那一条的原文，逐字照抄","new":["改后第一条","改后第二条"]}]}

【定稿的线】
{FINAL}

【压缩版（每段按组列出）】
{CUR}

【评委比对定稿时的意见（这些段定稿更好）】
{WHY}
"""

WORDS = """视频屏幕上的短词块，从原稿的珠子（听的人当下的感受）拆出来，观众边听音乐边扫屏幕，只有一眼。原稿是对的，读者读得懂。

下面这些块，没读过原稿的观众只看屏幕时，猜偏了或者要想一下才懂。其余的块已经够好，不动。请只修这些块：
- 对照原稿，看观众缺了什么：说的是谁或什么？发生了什么？转折的两头？把缺的最少的东西带上，让这块一扫就懂。
- 指代要换回它指的东西（“那个”“它”“熟悉的”“又回来”“刚才”）。比喻要带上它要说的感受。
- 只在说声音怎么样的，换成这句里听的人的感受；原稿这句没有感受，就删掉这块（words 给空数组）。
- 读着像评语的，换成原稿里的身体感觉、具体的事或心里闪过的话。
- 一块一两个或两三个短词，比现在只短不长太多。用原稿的字，不加原稿没有的比喻、情节和感受。不要标点，问号除外。
- 不能掉清单里的感受不要删。

只输出 JSON：{"blocks":[{"id":"S01-0-1","words":["…","…"]}]}

【不能掉清单（珠子）】
{KEEP}

【要修的块：词、所在组的线、观众的猜测、原稿整颗珠子】
{ROWS}
"""


def why(w, tag):
    rows = {}
    for jj, seat in [(j, x) for j in ('g6', 'g56') for x in ('newX', 'newY')]:
        p = R2/f'tvote_{w}_{jj}_{tag}_{seat}.json'
        if not p.exists(): continue
        old = 'Y' if seat == 'newX' else 'X'
        for s in rd(p).get('sections', []):
            o = rows.setdefault(s['sec'], [])
            if s.get('alone') == old and s.get('alone_why'): o.append(s['alone_why'])
            for x in s.get(f"lost_in_{'X' if seat == 'newX' else 'Y'}", []) or []: o.append('丢了：'+x.get('what', ''))
    return '\n'.join(f"{k}：" + ' / '.join(v) for k, v in sorted(rows.items()) if v)


def fix_lines(w, src, tag):
    d = rd(R3/f'script_{w}_{src}.json')
    fin = '\n'.join(f"{s['sec']} {l['id']}：{l['text']}" for s in rd(R2/f'{w}_src.json')['sections'] for l in s['lines'])
    cur = '\n'.join(f"{s['sec']} 第{i}组：" + ' ｜ '.join(l['text'] for l in g.get('lines', [])) for s in d['sections'] for i, g in enumerate(s['groups']))
    msg = LINES.replace('{FINAL}', fin).replace('{CUR}', cur).replace('{WHY}', why(w, src))
    for k in range(3):
        ans = call(f'pub13L_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public13-lines')
        try:
            E = parse(ans)['edits']; n = 0
            for e in E:
                s = next(x for x in d['sections'] if x['sec'] == e['sec'])
                for g in s['groups']:
                    for i, l in enumerate(g.get('lines', [])):
                        if l['text'] == e['old']:
                            g['lines'][i:i+1] = [{'text': t, 'keys': [], 'from': l.get('from', [])} for t in e['new'] if t.strip()]; n += 1; break
                    else: continue
                    break
                else: print(w, '没找到', e['old'][:40], flush=True)
            print(w, '线改', n, '/', len(E), flush=True); return d
        except Exception as ex: print(w, '线不合格', repr(ex)[:200], flush=True)
    return None


def fix_words(w, src, tag, d):
    import pub12
    A, B = rd(R3/f'blind_{w}_g6_{src}.json'), rd(R3/f'blind_{w}_g56_{src}.json'); m = {x['id']: x for x in rd(R3/f'match_{w}_{src}.json')['blocks']}
    ga = {x['id']: x for x in A['blocks']}; gb = {x['id']: x for x in B['blocks']}
    src_d = rd(R2/f'{w}_src.json'); P = {}
    for s in src_d['sections']:
        for b in s['beads']:
            for x in b['points']: P[x['id']] = ' '.join(y['text'] for y in b['points'])
    keep = '\n'.join(f"- {x['id']}：{x['text']}" for x in pub2.musts(w) if x['id'] in P)
    _, bs = pub12.blocks(w, src); bad = []
    for b in bs:
        r = [ga.get(b['id'], {}).get('read'), gb.get(b['id'], {}).get('read')]; h = m.get(b['id'], {})
        if '不懂' in r or r == ['半懂', '半懂'] or h.get('a') != '对上' or h.get('b') != '对上': bad.append(b)
    lines = {f"{s['sec']}-{i}": ' '.join(l['text'] for l in g.get('lines', [])) for s in rd(R3/f'script_{w}_{src}.json')['sections'] for i, g in enumerate(s['groups'])}
    rows = [f"{b['id']}\n  词：{'  '.join(b['words'])}\n  线：{lines[b['sec']+'-'+str(b['group'])]}\n  观众甲：{ga.get(b['id'], {}).get('guess')}\n  观众乙：{gb.get(b['id'], {}).get('guess')}\n  缺：{m.get(b['id'], {}).get('lost', '')}\n  原稿：{P.get(b['from'][0], '') if b['from'] else ''}" for b in bad]
    print(w, '要修的块', len(bad), '/', len(bs), flush=True)
    msg = WORDS.replace('{KEEP}', keep).replace('{ROWS}', '\n'.join(rows))
    for k in range(3):
        ans = call(f'pub13W_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public13-words')
        try:
            new = {x['id']: x['words'] for x in parse(ans)['blocks']}; idx = {b['id']: b for b in bad}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    chs = pub12.chunks(g.get('beads', [])); out = []
                    for n, ch in enumerate(chs):
                        cid = f"{s['sec']}-{i}-{n}"
                        if cid in new and cid in idx:
                            base = ch[0]; out += [{'text': t, 'keys': [], 'from': base.get('from', []), **({'emotion': base['emotion']} if base.get('emotion') else {})} for t in new[cid] if t.strip()]
                        else: out += ch
                    g['beads'] = out
            return d
        except Exception as ex: print(w, '词不合格', repr(ex)[:200], flush=True)
    return None


def one(a):
    w, src, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = fix_lines(w, src, tag)
    if d is None: return False
    d = fix_words(w, src, tag, d)
    if d is None: return False
    errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True); wr(p.with_suffix('.try.json'), d)
    if errs:
        # 屏幕文字带了小节号的：交回模型只改这几条。
        bad = sorted({e.split('含定位：', 1)[1] for e in errs if '含定位：' in e})
        if bad:
            ans = call(f'pub13F_{w}_{tag}', '下面这些是视频屏幕上的短文字，里面带了小节号或数字，观众看不懂。请去掉定位，只留感受，意思不变，不加新内容。只输出 JSON：{"fix":[{"old":"…","new":"…"}]}\n'+'\n'.join(bad), G6, 'gpt3s', 'public13-fix')
            m = {x['old']: x['new'] for x in parse(ans)['fix']}
            for s in d['sections']:
                for g in s['groups']:
                    for x in g.get('lines', [])+g.get('beads', []):
                        if x['text'] in m: x['text'] = m[x['text']]
            errs = pub3.check(w, d); print(w, tag, '修后问题', len(errs), errs[:5], flush=True)
    if errs: return False
    ls = [l['text'] for s in d['sections'] for g in s['groups'] for l in g.get('lines', [])]; ws = [b['text'] for s in d['sections'] for g in s['groups'] for b in g.get('beads', [])]
    print(w, tag, '线', len(ls), '均字', sum(map(len, ls))//len(ls), '总字', sum(map(len, ls)), '词', len(ws), '总字', sum(map(len, ws)), flush=True)
    wr(p, d); return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    src, tag = sys.argv[1:3]
    with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
