"""11-12 夜 骨架的检查（用户：“我们现在就专心骨架”）。把标准搬到骨架这一步，只看骨架，不往下写线：
  ① 互换：每段的骨架内容配四组珠子（本段、前、后、远），两位评委盲猜；看是不是只配本段（DAG 标准第 4 条）。
  ② 逐段判（两位评委各一次）：有没有理由、理由是不是只属于这段、是不是只把感受转述了一遍（翻译珠子）、有没有编具体的事、
     是具体的人的处境还是心理术语、是不是重新宣布前面已有的认识；全篇有几件不同的事；是不是同一个人同一件事、贴不贴 Center。
用法：python r3/skcheck.py 名字=来源 …   来源：run:TAG（写线流水线的 A1，取 A4 选中的那条）或 file:标签（r3/s24/sk41_{作品}_{标签}.json）加可选 #路线序号
例：python r3/skcheck.py L34g61=run:L34g61 sk41argon=file:argon#0
结果：r3/s24/skcheck_{名字}.json"""
import json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1])); os.environ['PUB_SRC'] = 'r2e'
from pub24 import R2, S, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
RUNS = Path('D:/musicclaude/_thread_evo_20261019/runs'); NM = '甲乙丙丁'; JS = (('g6', G6), ('g56', G56))
tx = lambda v: '；'.join(map(str, v)) if isinstance(v, list) else str(v or '')


def load(src, w):
    kind, rest = src.split(':', 1); tag, _, idx = rest.partition('#')
    if kind == 'run':
        rs = []; r = {}
        for dd in sorted(RUNS.glob(f'sc{tag}_{w}_A1*')):
            if (dd/'output.txt').exists():
                try: r = parse((dd/'output.txt').read_text(encoding='utf-8')); rs += (r.get('routes') or r.get('items') or r.get('candidates') or [])
                except Exception as ex: print('读不了', dd.name, repr(ex)[:80])
        if idx: x = rs[int(idx)]
        else:
            base = str(parse((RUNS/f'sc{tag}_{w}_A4'/'output.txt').read_text(encoding='utf-8')).get('base_route'))
            x = next((q for q in rs if str(q.get('route_id')) == base), rs[0])
    else:
        r = rd(S/f'sk41_{w}_{tag}.json'); rs = r.get('routes') or r.get('items') or r.get('candidates'); x = rs[int(idx or 0)]
    segs = [{'sec': str(s['sec'])[:3], 'text': tx(s.get('state')) + ('　理由：' + tx(s['why_now']) if s.get('why_now') else '') + ('　新增：' + tx(s['delta']) if s.get('delta') else '')} for s in x['segments']]
    giv = x.get('givens') or r.get('givens') or []
    return {'situation': x.get('situation'), 'givens': [g.get('text') if isinstance(g, dict) else str(g) for g in giv], 'segs': segs}


SWAP = """下面有一小段文字，是一个人在一首钢琴曲某一段里的处境（这一段他是什么情况、为什么这样）。另有四组听感记录（甲乙丙丁），各来自这首曲子的不同段落，记的是听那一段音乐时的感受。其中一组和这段文字来自同一段。

请判断：这段文字原本配的是哪一组？依据是它写的处境最能说明哪一组听感里的那种滋味。
再判断：除了你选的那一组，这段文字原样放到另外哪几组旁边，也同样说得通、看不出不合适？

只输出 JSON：{"pick":"甲|乙|丙|丁","also_fit":["同样说得通的组，没有就空"],"why":"一两句"}

【这段文字】
{LINE}

{GROUPS}
"""

JUDGE = """下面是一份“骨架”：为一首钢琴曲设计的、同一个人在全曲里经历的一件心事，按音乐分段，每段写他此刻的情况和缘由。它不是最终文案，后面还会有人照它写成句子，所以不要评价措辞、通顺、长短。只评内容。

这件事的核心（Center）：{CENTER}

请逐段判断，再给全篇的判断。只输出 JSON：
{"segs":[{"sec":"S01",
  "reason":"有|弱|无",            // 这一段有没有说出他此刻为什么是这样（缘由来自他的处境或前面段落），而不只是说他是什么状态
  "only_here":"是|否",            // 这一段的内容是不是只属于这一段：原样挪到别的段会明显不合适。放在哪段都通的话（重申他珍惜什么、担心什么、决定什么）判“否”
  "feeling_only":"是|否",         // 这一段是不是主要在描述感受的质地和变化（轻、热、清澈、沉浸、翻涌之类），而没有交代是什么处境让他这样
  "event":"",                     // 这一段如果写了某一次具体发生的事、对白、物件、地点、别人的具体举动来推动变化，写出来；没有就空字符串。一直如此的处境、习惯、关系状况不算
  "human":"人的事|心理术语|混合", // 内容是普通人讲自己经历时会说的事（谁、和对方怎样、他要什么、怕什么、怎么做），还是心理机制的术语（支撑、防线、体验、内在、自我、整合之类）
  "reannounce":""                 // 这一段如果把前面某段已经成立的认识、决定、担心当成新的再宣布一次，写出是哪一段的什么；没有就空字符串
 }],
 "distinct":["全篇真正不同的事（认识、决定、处境的不同侧面、后果）逐条列出，同一件事换说法只算一条"],
 "one_person_one_thing":"是|否","center":"贴|偏|不贴",
 "worst":"这份骨架最大的一个内容问题，一两句"}

【全篇不变的处境】
{GIVENS}

【这件事】{SIT}

【各段】
{SEGS}
"""


def swap(a):
    name, w, k, jn, J, sk = a; secs = rd(R2/f'{w}_src.json')['sections']; n = len(secs)
    if k >= len(sk['segs']): return None
    rnd = random.Random(f'{w}{k}'); cand = [k] + [i for i in (k-1, k+1) if 0 <= i < n]
    far = [i for i in range(n) if abs(i-k) >= 3]; rnd.shuffle(far)
    while len(cand) < 4: cand.append(far.pop())
    rnd.shuffle(cand)
    groups = '\n\n'.join(f'【{NM[i]}组】\n' + '\n'.join('- ' + b['text'] for b in secs[c]['beads']) for i, c in enumerate(cand))
    msg = SWAP.replace('{LINE}', sk['segs'][k]['text']).replace('{GROUPS}', groups); r = None
    for t in range(3):
        try: r = parse(call(f'sksw_{name}_{w}_{k}_{jn}' + ('' if not t else f'_r{t}'), msg, J, 'gpt3s', 'skcheck')); p = NM.index(r['pick'].strip()[0]); break
        except Exception as ex: print('重试', name, w, k, jn, repr(ex)[:100], flush=True); r = None
    if not r: return None
    pick = cand[p]; also = [cand[NM.index(x.strip()[0])] for x in r.get('also_fit', []) if x.strip() and x.strip()[0] in NM]
    return {'w': w, 'k': k, 'judge': jn, 'right': pick == k, 'only': pick == k and not [i for i in also if i != k], 'far': any(abs(i-k) > 1 for i in also + [pick])}


def judge(a):
    name, w, jn, J, sk = a; src = rd(R2/f'{w}_src.json')
    msg = JUDGE.replace('{CENTER}', src['center']).replace('{GIVENS}', '\n'.join('- ' + g for g in sk['givens']) or '（这份骨架没有单列）').replace('{SIT}', str(sk['situation'])).replace('{SEGS}', '\n'.join(f"{s['sec']}：{s['text']}" for s in sk['segs']))
    for t in range(3):
        try: r = parse(call(f'skjd_{name}_{w}_{jn}' + ('' if not t else f'_r{t}'), msg, J, 'gpt3s', 'skcheck')); assert r['segs']; return {'w': w, 'judge': jn, **r}
        except Exception as ex: print('重试', name, w, jn, repr(ex)[:100], flush=True)


def run(name, src):
    p = S/f'skcheck_{name}.json'
    if not p.exists():
        sk = {w: load(src, w) for w in WORKS}
        with ThreadPoolExecutor(14) as ex:
            fj = [ex.submit(judge, (name, w, jn, J, sk[w])) for w in WORKS for jn, J in JS]
            fs = [ex.submit(swap, (name, w, k, jn, J, sk[w])) for w in WORKS for k in range(len(sk[w]['segs'])) for jn, J in JS]
            res = {'src': src, 'judge': [f.result() for f in fj if f.result()], 'swap': [f.result() for f in fs if f.result()], 'n': {w: len(sk[w]['segs']) for w in WORKS}}
        p.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf-8')
    return rd(p)


def line(name, res):
    out = []
    for w in WORKS:
        sw = [x for x in res['swap'] if x['w'] == w]; jd = [x for x in res['judge'] if x['w'] == w]; n = sum(len(j['segs']) for j in jd) or 1
        c = lambda k, v: sum(str(s.get(k, '')).strip()[:len(v)] == v for j in jd for s in j['segs'])
        ne = lambda k: sum(bool(str(s.get(k, '')).strip()) for j in jd for s in j['segs'])
        out.append(f"{name} {w}｜互换 猜对 {sum(x['right'] for x in sw)}/{len(sw)}、只配本段 {sum(x['only'] for x in sw)}｜有理由 {c('reason','有')}/{n}｜只属本段 {c('only_here','是')}/{n}｜只描感受 {c('feeling_only','是')}/{n}｜编具体的事 {ne('event')}｜人的事 {c('human','人的事')}/{n}、术语 {c('human','心理术语')}｜重新宣布 {ne('reannounce')}｜不同的事 {'、'.join(str(len(j.get('distinct', []))) for j in jd)}｜Center {'、'.join(str(j.get('center')) for j in jd)}")
    return '\n'.join(out)


if __name__ == '__main__':
    jobs = [a.split('=', 1) for a in sys.argv[1:]]
    with ThreadPoolExecutor(len(jobs) or 1) as ex: rs = list(ex.map(lambda j: (j[0], run(*j)), jobs))
    print('\n===== 骨架检查汇总（每项分母 = 段数 × 两位评委）')
    for name, r in rs: print(line(name, r), flush=True)
    for name, r in rs:
        for j in r['judge']: print(f"  {name} {j['w']} {j['judge']} 最大问题：{str(j.get('worst'))[:200]}")
