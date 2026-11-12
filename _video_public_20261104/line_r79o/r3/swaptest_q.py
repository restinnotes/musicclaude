"""11-12 体验性质的互换测试：珠子磨成体验性质（写线 A3）之后，各段的差别还在不在？
每段的体验性质配四组珠子原文（本段、前、后、一段远的），评委盲猜它是从哪一组提炼的。python r3/swaptest_q.py [写线TAG=L34g61]"""
import json, os, sys, random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['PUB_SRC'] = 'r2e'
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
TAGQ = sys.argv[1] if len(sys.argv) > 1 else 'L34g61'
ASK = """下面有一组“体验性质”，是从一首钢琴曲某一段的听感记录里提炼出来的（去掉了画面、比喻和音乐术语）。另有四组听感记录原文（甲乙丙丁），各来自这首曲子的不同段落，其中一组就是它的来源。

请判断：这组体验性质最像是从哪一组提炼出来的？
再判断：除了你选的那一组，它原样放到另外哪几组旁边，也同样说得通、看不出不合适？

只输出 JSON：{"pick":"甲|乙|丙|丁","also_fit":["同样说得通的组，没有就空"],"why":"一两句"}

【体验性质】
{LINE}

{GROUPS}
"""
NM = '甲乙丙丁'


def quals(w):
    raw = open(f'D:/musicclaude/_thread_evo_20261019/runs/sc{TAGQ}_{w}_A3/output.txt', encoding='utf-8').read()
    r = parse(raw); return {(x.get('section_id') or x.get('segment_id')): '\n'.join('- ' + '；'.join(b['qualities']) + (f"（{b['temporal_shape']}）" if b.get('temporal_shape') else '') for b in x['beads']) for x in (r.get('sections') or r.get('segments'))}


QUAL = {w: quals(w) for w in WORKS}


def one(a):
    w, k, jn, J = a
    secs = rd(R2/f'{w}_src.json')['sections']; n = len(secs); s = secs[k]
    if s['sec'] not in QUAL[w]: return None
    rnd = random.Random(f'{w}{k}')
    cand = [k] + [i for i in (k-1, k+1) if 0 <= i < n]
    far = [i for i in range(n) if abs(i-k) >= 3]; rnd.shuffle(far)
    while len(cand) < 4: cand.append(far.pop())
    rnd.shuffle(cand)
    groups = '\n\n'.join(f'【{NM[i]}组】\n' + '\n'.join('- ' + b['text'] for b in secs[c]['beads']) for i, c in enumerate(cand))
    msg = ASK.replace('{LINE}', QUAL[w][s['sec']]).replace('{GROUPS}', groups); r = None
    for t in range(3):
        try:
            r = parse(call(f'swapQ_{TAGQ}_{w}_{s["sec"]}_{jn}' + ('' if not t else f'_r{t}'), msg, J, 'gpt3s', 'swaptest')); p = NM.index(r['pick'].strip()[0]); break
        except Exception as ex: print('重试', w, s['sec'], jn, repr(ex)[:100], flush=True); r = None
    if not r: return None
    pick = cand[p]; also = [cand[NM.index(x.strip()[0])] for x in r.get('also_fit', []) if x.strip() and x.strip()[0] in NM]
    kind = lambda i: '本段' if i == k else '邻段' if abs(i-k) == 1 else '远段'
    o = {'w': w, 'sec': s['sec'], 'judge': jn, 'right': pick == k, 'pick': kind(pick), 'also': [kind(i) + secs[i]['sec'] for i in also if i != pick]}
    print(json.dumps(o, ensure_ascii=False), flush=True); return o


if __name__ == '__main__':
    jobs = [(w, k, jn, J) for w in WORKS for k in range(len(rd(R2/f'{w}_src.json')['sections'])) for jn, J in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(12) as ex: res = [x for x in ex.map(one, jobs) if x]
    (S/f'swapQ_{TAGQ}.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    for w in WORKS:
        rr = [x for x in res if x['w'] == w]
        print(w, '体验性质', f"猜对 {sum(x['right'] for x in rr)}/{len(rr)}；猜成邻段 {sum(x['pick']=='邻段' for x in rr)}；猜成远段 {sum(x['pick']=='远段' for x in rr)}；猜对且只配本段 {sum(x['right'] and not x['also'] for x in rr)}；也配得上远段 {sum(any(a.startswith('远段') for a in x['also']) or x['pick']=='远段' for x in rr)}")
