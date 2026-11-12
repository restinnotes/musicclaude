"""把原稿整篇（珠子和线）给模型，假定原稿是对的、读得懂的，只决定怎么拆。线不动，只换词。全走 gpt3。
python pub12.py split 来源TAG 新TAG     拆词
python pub12.py test TAG                盲读还原：没读过原稿的观众先猜每块是什么，再由看过原稿的评委比对
"""
import json, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pub2, pub3
from pub2 import G6, JUDGES, WORKS, call, parse, rd, source_matched, wr
R3 = pub3.OUT

SPLIT = """下面是一首器乐曲“边听边看”视频的原稿：线（一个人经历的事）和珠子（听的人当下的感受）。原稿是对的，读者读得懂，你不用改进它，也不用判断它。

观众边听音乐边扫屏幕，只有一眼，读不了句子。所以每组线旁边要放几块短词。你的任务只是拆：从原稿拆出这些短词。

【原稿为什么读得懂，拆的时候就留什么】
一句珠子读得懂，靠的是几样东西：说的是谁或什么；发生了什么；它和什么相对（“却”“还”“明知”的两头）。上一句交代过的东西，也算在内。拆之前先看整颗珠子，问：这个感受，读者要知道哪几样才懂？拆出来的那块必须带着它们。
- 带着转折的，两头都留。“明明知道这样更累，还是不想停下来”，不能只拆出“不想停下来”，要“知道会累 还不想停”。
- 有指代的，换回它指的东西。“那个”“它”“熟悉的”“又回来”“刚才”，观众不知道指什么，写出来是什么。
- 比喻要能自己站住。“老房子里桌椅都没动”，只拆出“桌椅没动”没人懂，要带上它要说的：“桌椅还在 人不在了”。原稿这句带不出感受，就不拆这句。
- 只是在说声音怎么样的句子，不拆声音，拆这句里听的人的感受；没有感受的就不拆。“声部越来越密，让人喘不过气”，拆“喘不过气”。
- 不要替原稿总结。“这是一段幻想和遗憾交织的回忆”这种读起来像评语的不要，改用原稿里的身体感觉、具体的事或心里闪过的话。

【怎么拆】
- 尽量用原稿自己的字。不加原稿没有的比喻、情节、感受。
- 一块就是一个完整的感受，一两个或两三个短词。一块里的词 from 相同，除问号外不带标点。
- 不用每句都拆，线上已经说清的不用再说一遍，同一个感受只说一遍。主组可以多些，次组少些，整屏一眼扫得完。
- 不能掉清单里的感受要留下。
- 每块放到这段里和它最有关的那一组。

每个词写 emotion（和所在组不同时才写，只能从下面选）：
"""+pub3.EMO_DESC+"""

只输出 JSON：{"sections":[{"sec":"S01","groups":[{"idx":0,"beads":[{"text":"…","emotion":"…","from":["S01-B1-p1"]}]}]}]}

【屏幕上已有的组和线（线不改，idx 照抄）】
{CUR}

【不能掉清单（珠子）】
{KEEP}

【原稿：珠子和线】
{SRC}
"""

BLIND = """你是一个普通观众，没读过任何原文。你在听一首钢琴曲，屏幕上每段有几组文字：白色的话（一个人经历的事），旁边是几块短词。你只能扫一眼。

逐块回答：
- guess：只看这块词和它所在组的话，你觉得这块说的是什么感受、什么事？用一句大白话说。真的不知道就写“不知道”。不要脑补说得很圆。
- read：懂（一扫就知道）/ 半懂（大概知道，要想一下）/ 不懂。

只输出 JSON：{"blocks":[{"id":"S01-0-0","guess":"…","read":"懂|半懂|不懂"}]}

【屏幕文字】
{SCREEN}
"""

MATCH = """视频屏幕上有一些短词块，从原稿的珠子拆出来。两位没读过原稿的观众只看屏幕，猜了每块在说什么。请比对：观众猜到的，是不是原稿这几句要说的感受？

- 对上：猜到了原稿说的感受，说法不同没关系。
- 偏了：沾点边，但感受或对象不一样。
- 没对上：猜错了，或者不知道。

每块按两位观众分别判。只输出 JSON：{"blocks":[{"id":"S01-0-0","a":"对上|偏了|没对上","b":"对上|偏了|没对上","lost":"偏了或没对上时，观众缺了什么"}]}

【每块：词、原稿、两位观众的猜测】
{ROWS}
"""


def chunks(beads):
    out = []; seen = {}
    for b in beads:
        k = (b.get('from') or [b['text']])[0]
        if k not in seen: seen[k] = []; out.append(seen[k])
        seen[k].append(b)
    return out


def one(a):
    w, src, tag = a; p = R3/f'script_{w}_{tag}.json'
    if p.exists(): return True
    d = rd(R3/f'script_{w}_{src}.json')
    cur = [{'sec': s['sec'], 'groups': [{'idx': i, 'rank': g['rank'], 'emotion': g['emotion'], 'lines': [l['text'] for l in g.get('lines', [])]} for i, g in enumerate(s['groups'])]} for s in d['sections']]
    pids = {x['id'] for s in rd(pub2.OUT/f'{w}_src.json')['sections'] for b in s['beads'] for x in b['points']}
    keep = '\n'.join(f"- {x['id']}：{x['text']}" for x in pub2.musts(w) if x['id'] in pids)
    msg = SPLIT.replace('{CUR}', json.dumps(cur, ensure_ascii=False)).replace('{KEEP}', keep).replace('{SRC}', source_matched(w))
    for k in range(3):
        ans = call(f'pub12_{w}_{tag}'+('' if not k else f'_r{k}'), msg, G6, 'gpt3s', 'public12-split')
        try:
            B = {s['sec']: {int(g['idx']): g for g in s['groups']} for s in parse(ans)['sections']}
            for s in d['sections']:
                for i, g in enumerate(s['groups']):
                    g['beads'] = [{'text': b['text'], 'keys': [], 'from': b.get('from', []), **({'emotion': b['emotion']} if b.get('emotion') else {})} for b in B.get(s['sec'], {}).get(i, {}).get('beads', [])]
            errs = pub3.check(w, d); print(w, tag, '问题', len(errs), errs[:5], flush=True); wr(p.with_suffix('.try.json'), d)
            if not errs: wr(p, d); return True
        except Exception as e: print(w, '不合格', repr(e)[:200], flush=True)
    return False


def blocks(w, tag):
    d = rd(R3/f'script_{w}_{tag}.json'); out = []
    for s in d['sections']:
        for i, g in enumerate(s['groups']):
            for n, ch in enumerate(chunks(g.get('beads', []))):
                out.append({'id': f"{s['sec']}-{i}-{n}", 'sec': s['sec'], 'group': i, 'words': [b['text'] for b in ch], 'from': sorted({x for b in ch for x in b.get('from', [])})})
    return d, out


def screen(w, tag):
    d, bs = blocks(w, tag); rows = []
    for s in d['sections']:
        rows.append(f"\n### {s['sec']}")
        for i, g in enumerate(s['groups']):
            rows.append(f"第{i}组 话：" + ' '.join(l['text'] for l in g.get('lines', [])))
            rows += [f"  {b['id']}：{'  '.join(b['words'])}" for b in bs if b['sec'] == s['sec'] and b['group'] == i]
    return '\n'.join(rows)


def blind(a):
    w, j, tag = a; p = R3/f'blind_{w}_{j}_{tag}.json'
    if p.exists(): return rd(p)
    for k in range(3):
        ans = call(f'pub12B_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), BLIND.replace('{SCREEN}', screen(w, tag)), JUDGES[j], 'gpt3s', 'public12-blind')
        try: r = parse(ans); assert r['blocks']; wr(p, r); return r
        except Exception as e: print('盲读不合格', w, j, repr(e)[:150], flush=True)
    return None


def test_one(a):
    w, tag = a; p = R3/f'match_{w}_{tag}.json'
    A, B = blind((w, 'g6', tag)), blind((w, 'g56', tag))
    if not A or not B: return None
    ga = {x['id']: x for x in A['blocks']}; gb = {x['id']: x for x in B['blocks']}
    pts = {x['id']: x['text'] for s in rd(pub2.OUT/f'{w}_src.json')['sections'] for b in s['beads'] for x in b['points']}
    _, bs = blocks(w, tag)
    if not p.exists():
        rows = [f"{b['id']} 词：{'  '.join(b['words'])}\n  原稿：{' '.join(pts.get(x, '') for x in b['from'])}\n  观众甲：{ga.get(b['id'], {}).get('guess', '不知道')}\n  观众乙：{gb.get(b['id'], {}).get('guess', '不知道')}" for b in bs]
        for k in range(3):
            ans = call(f'pub12M_{w}_{tag}'+('' if not k else f'_r{k}'), MATCH.replace('{ROWS}', '\n'.join(rows)), G6, 'gpt3s', 'public12-match')
            try: r = parse(ans); assert r['blocks']; wr(p, r); break
            except Exception as e: print('比对不合格', w, repr(e)[:150], flush=True)
    m = rd(p); M = {x['id']: x for x in m['blocks']}
    read = Counter(x.get('read') for x in A['blocks']+B['blocks']); hit = Counter(v for x in m['blocks'] for v in (x.get('a'), x.get('b')))
    both = [b for b in bs if M.get(b['id'], {}).get('a') == '对上' and M.get(b['id'], {}).get('b') == '对上']
    miss = [b for b in bs if M.get(b['id'], {}).get('a') != '对上' and M.get(b['id'], {}).get('b') != '对上']
    words = sum(len(b['words']) for b in bs); chars = sum(len(x) for b in bs for x in b['words'])
    print(w, tag, f"块 {len(bs)} 词 {words} 总字 {chars} 自评 {dict(read)} 对原稿 {dict(hit)} 两位都对上 {len(both)} 都没对上 {len(miss)}", flush=True)
    return {'w': w, 'blocks': len(bs), 'words': words, 'chars': chars, 'read': dict(read), 'hit': dict(hit), 'both': len(both), 'miss': [{'words': b['words'], 'lost': M[b['id']].get('lost', ''), 'guess': [ga.get(b['id'], {}).get('guess'), gb.get(b['id'], {}).get('guess')]} for b in miss if b['id'] in M]}


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    c = sys.argv[1]
    if c == 'split':
        src, tag = sys.argv[2:4]
        with ThreadPoolExecutor(2) as ex: print(list(ex.map(one, [(w, src, tag) for w in WORKS])), flush=True)
    elif c == 'test':
        tag = sys.argv[2]
        with ThreadPoolExecutor(2) as ex: res = list(ex.map(test_one, [(w, tag) for w in WORKS]))
        wr(R3/f'blindtest_{tag}.json', res)
