"""11-12 互换测试（用户问：S(x) 的线能解释 S(x+1) 的珠子吗）：线是贴着本段的，还是放在哪段都通的通用句？
每段的线（整段几条）配四组听感记录（本段、前一段、后一段、一段较远的，打乱），评委盲猜它原本配哪一组，并说还有哪几组也配得上。
瞎猜 25%。python r3/swaptest.py [SRC=r2e] → r3/s24/swap_{SRC}_{作品}.json"""
import json, os, sys, random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
SRC = sys.argv[1] if len(sys.argv) > 1 else 'r2e'
os.environ['PUB_SRC'] = SRC
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
ASK = """下面有一小段文字，写的是一个人在一首钢琴曲某一段里的心事（几条，每条一句）。另有四组听感记录（甲乙丙丁），各来自这首曲子的不同段落，记的是听那一段音乐时的感受。其中一组和这段文字来自同一段。

请判断：这段文字原本配的是哪一组？判断依据是这段文字写的处境和心情，最能说明哪一组听感里的那种滋味。
再判断：除了你选的那一组，这段文字原样放到另外哪几组旁边，也同样说得通、看不出不合适？

只输出 JSON：{"pick":"甲|乙|丙|丁","also_fit":["同样说得通的组，没有就空"],"why":"一两句"}

【这段文字】
{LINE}

{GROUPS}
"""
NM = '甲乙丙丁'


def one(a):
    w, k, jn, J = a
    secs = rd(R2/f'{w}_src.json')['sections']; n = len(secs); s = secs[k]
    if not s['lines']: return None
    rnd = random.Random(f'{w}{k}')
    cand = [k] + [i for i in (k-1, k+1) if 0 <= i < n]
    far = [i for i in range(n) if abs(i-k) >= 3]; rnd.shuffle(far)
    while len(cand) < 4: cand.append(far.pop())
    rnd.shuffle(cand)
    groups = '\n\n'.join(f'【{NM[i]}组】\n' + '\n'.join('- ' + b['text'] for b in secs[c]['beads']) for i, c in enumerate(cand))
    msg = ASK.replace('{LINE}', '\n'.join('- ' + l['text'] for l in s['lines'])).replace('{GROUPS}', groups)
    for t in range(3):
        try:
            r = parse(call(f'swap_{SRC}_{w}_{s["sec"]}_{jn}' + ('' if not t else f'_r{t}'), msg, J, 'gpt3s', 'swaptest')); p = NM.index(r['pick'].strip()[0]); break
        except Exception as ex: print('重试', w, s['sec'], jn, repr(ex)[:100], flush=True); r = None
    if not r: return None
    pick = cand[p]; also = [cand[NM.index(x.strip()[0])] for x in r.get('also_fit', []) if x.strip() and x.strip()[0] in NM]
    kind = lambda i: '本段' if i == k else '邻段' if abs(i-k) == 1 else '远段'
    o = {'w': w, 'sec': s['sec'], 'judge': jn, 'right': pick == k, 'pick': kind(pick), 'pick_sec': secs[pick]['sec'], 'also': [kind(i) + secs[i]['sec'] for i in also if i != pick], 'why': r.get('why', '')}
    print(json.dumps(o, ensure_ascii=False), flush=True); return o


if __name__ == '__main__':
    jobs = [(w, k, jn, J) for w in WORKS for k in range(len(rd(R2/f'{w}_src.json')['sections'])) for jn, J in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(12) as ex: res = [x for x in ex.map(one, jobs) if x]
    (S/f'swap_{SRC}.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for w in WORKS:
        rr = [x for x in res if x['w'] == w]
        print(w, SRC, f"猜对 {sum(x['right'] for x in rr)}/{len(rr)}；猜成邻段 {sum(x['pick']=='邻段' for x in rr)}；猜成远段 {sum(x['pick']=='远段' for x in rr)}；猜对但还有别组也通 {sum(x['right'] and bool(x['also']) for x in rr)}；猜对且只配本段 {sum(x['right'] and not x['also'] for x in rr)}")
