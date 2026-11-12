"""给大众版做体检：沿用内容流程的覆盖（COV2）、不能掉清单、线不倒退，再加词是否读得懂。
python pub_eval.py TAG   结果写到 r3/eval_TAG.json
"""
import json, shutil, sys
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import pub2
from pub2 import WORKS, call, parse, rd, wr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/"_thread_evo_20261019"))
import covjudge
import v6fix as V
import v6cov

R3 = Path(__file__).resolve().parent/'r3'; R2 = pub2.OUT
BASE = rd(V.OUT/'cov2_r78a.json')

READ = """下面是一首器乐曲“边听边看”视频的屏幕文字。观众没读过任何原文，边听音乐边扫屏幕。屏幕上每段有几组：散开的词（听的人当下的感受），和一句白色的话（一个人经历的事）。

你就是这个没读过原文的观众。逐段回答：
1. 扫完这一段的词，你能感到什么？用一句话说。如果感觉不出来，就说感觉不出来。
2. 哪些词读不懂或没感觉：离开句子不知道在说什么，或者太抽象、太像书面概括。
3. 哪些词太长，已经不是一扫能过的东西。
4. 词和白色的话放在一起，你能明白为什么这个人会有这些感受吗？能 / 勉强 / 不能。
5. 只看白色的话，和上一段接得上吗？能 / 勉强 / 不能。

只输出 JSON：{"sections":[{"sec":"S01","feel":"…","unclear":["…"],"too_long":["…"],"joint":"能|勉强|不能","chain":"能|勉强|不能"}],"overall":"两三句话，说这样压之后最大的问题是什么，什么地方压得好"}

【屏幕文字】
{SCREEN}
"""


def plain(w, tag):
    rows = []
    for s in rd(R2/f'script_{w}_{tag}.json')['sections']:
        rows.append(f"\n### {s['sec']}")
        for g in s['groups']:
            rows.append('词：'+' / '.join(b['text'] for b in g.get('beads', [])))
            rows += ['话：'+l['text'] for l in g.get('lines', [])]
    return '\n'.join(rows)


def cov(a):
    w, j, tag = a; p = R3/f'cov_{w}_{j}_{tag}.json'
    if p.exists(): return w, j, rd(p)
    msg = v6cov.COV2.format(NAME=covjudge.NAME[w], WHAT=V.WHAT2, LINE=pub2.thread_view(w, tag), BEADS=V.beads(w))
    for k in range(3):
        ans = call(f'pubcov_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), msg, pub2.JUDGES[j], 'gpt3s', 'public-cov')
        try:
            d = parse(ans); assert d['beads']; wr(p, d); return w, j, d
        except Exception as e: print('覆盖不合格', w, j, repr(e)[:150], flush=True)
    return w, j, None


def read(a):
    w, j, tag = a; p = R3/f'read_{w}_{j}_{tag}.json'
    if p.exists(): return w, j, rd(p)
    for k in range(3):
        ans = call(f'pubread_{w}_{j}_{tag}'+('' if not k else f'_r{k}'), READ.replace('{SCREEN}', plain(w, tag)), pub2.JUDGES[j], 'gpt3s', 'public-read')
        try:
            d = parse(ans); assert d['sections']; wr(p, d); return w, j, d
        except Exception as e: print('可读不合格', w, j, repr(e)[:150], flush=True)
    return w, j, None


def run(tag, lite=False):
    for w in WORKS: shutil.copy(R3/f'script_{w}_{tag}.json', R2/f'script_{w}_{tag}.json')
    jobs = [(w, j, tag) for w in WORKS for j in ('g6', 'g56')]; res = {'tag': tag, 'cov': {}, 'read': {}}
    with ThreadPoolExecutor(8) as ex:
        fc = [] if lite else [ex.submit(cov, a) for a in jobs]; fr = [ex.submit(read, a) for a in jobs]
        fk = ex.submit(lambda: None) if lite else ex.submit(pub2.keep, tag); ft = ex.submit(pub2.thread_check, tag)
        for f in fc:
            w, j, d = f.result()
            if not d: continue
            R = v6cov.roles(w); got = {(x.get('sec'), str(x.get('bead'))): x for x in d['beads']}
            c = Counter((got.get(k) or {}).get('status', '未判') for k in R); old = BASE.get(f'{w}_{j}', {}).get('total', {})
            res['cov'][f'{w}_{j}'] = {'n': len(R), 'new': dict(c), 'r78a': old}
            print(w, j, f"覆盖 说清 {c['说清']}/{len(R)}（r78a {old.get('说清', 0)}）偏弱 {c['偏弱']} 相反 {c['相反']} 没有 {c['没有']}", flush=True)
        for f in fr:
            w, j, d = f.result()
            if not d: continue
            ss = d['sections']; un = [x for s in ss for x in s.get('unclear', [])]; lg = [x for s in ss for x in s.get('too_long', [])]
            words = sum(len(g.get('beads', [])) for s in rd(R2/f'script_{w}_{tag}.json')['sections'] for g in s['groups'])
            res['read'][f'{w}_{j}'] = {'words': words, 'unclear': un, 'too_long': lg, 'joint': dict(Counter(s.get('joint') for s in ss)), 'chain': dict(Counter(s.get('chain') for s in ss)), 'overall': d.get('overall', '')}
            print(w, j, f"词 {words} 读不懂 {len(un)} 太长 {len(lg)} 词和话 {dict(Counter(s.get('joint') for s in ss))} 接得上 {dict(Counter(s.get('chain') for s in ss))}", flush=True); print('  ', d.get('overall', '')[:300], flush=True)
        fk.result(); ft.result()
    wr(R3/f'eval_{tag}.json', res)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); run(sys.argv[1])
