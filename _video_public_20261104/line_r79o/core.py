"""11-08 晚 珠子要点分主次（大众版标准第 5 条：“最核心的不能掉（先独立排出主次再对照）”）。
两位评委（GPT-6、GPT-5.6）各自独立、不看任何屏幕稿，逐段把珠子要点分成核心 / 次要；两位都判核心的算核心。冻结在 r3/s24/core_{作品}.json。
之后“核心要点覆盖”直接用已有的整屏珠子覆盖逐条判定（beadcovA_*）算：核心要点里判“留住”的比例，不用再调评委。
python core.py list            建清单（已有就不动）
python core.py score TAG...    打印每版核心要点覆盖（每位评委、平均）
"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, R2, rd, wr, call, parse, G6, G56, WORKS, JUDGES

RANK = """下面是一首钢琴曲每一段的原稿：线（一个人经历的事，一两句）和珠子（几位听众在这一刻写下的感受，已按句拆成要点，每条有编号）。这份原稿要压缩成观众边听边扫的视频屏幕，每段只能留下一部分。

请逐段判断每条珠子要点是“核心”还是“次要”，不用考虑屏幕怎么写：
- 核心：这一刻最主要的那种感受，以及把它说得最具体、最有辨识度的那一个说法（一个画面、一种身体感觉、一句心里话、一个转折）。丢了它，这一段就少了一样别处没有的东西。
- 次要：同一种感受的其他听法或换个比喻再说一遍、补充说明、解释、纯写音乐本身而没有带出新感受的。
同一种感受有好几种说法时，只把最具体的那一个判核心。不同的感受各自判。每段的核心一般是少数，但不要为了凑比例硬判。

只输出 JSON：{"items":[{"id":"S01-B1-p1","rank":"核心|次要"}]}，逐条给全。

【原稿】
{SOURCE}
"""
prompt_lint.lint(RANK, 'core.py')


def src_text(w):
    NL = chr(10); out = []
    for s in rd(R2/f'{w}_src.json')['sections']:
        out.append(NL + '### ' + s['sec'])
        out += ['线：' + l['text'] for l in s['lines']]
        for b in s['beads']: out += [f"- {q['id']}：{q['text']}" for q in b['points']]
    return NL.join(out)


def rank(a):
    w, name, model = a; p = S/f'corerank_{w}_{name}.json'
    if p.exists(): return rd(p)
    ids = {q['id'] for s in rd(R2/f'{w}_src.json')['sections'] for b in s['beads'] for q in b['points']}
    for t in range(3):
        ans = call(f'pub24CORE_{w}_{name}' + ('' if not t else f'_r{t}'), RANK.replace('{SOURCE}', src_text(w)), model, 'gpt3s', 'public24-core')
        try:
            r = {x['id']: x.get('rank') for x in parse(ans)['items'] if x.get('id') in ids}; assert len(r) >= 0.95*len(ids)
            wr(p, r); return r
        except Exception as ex: print('不合格', w, name, repr(ex)[:150], flush=True)


def build():
    jobs = [(w, n, m) for w in WORKS for n, m in (('g6', G6), ('g56', G56))]
    with ThreadPoolExecutor(len(jobs)) as ex: res = dict(zip(jobs, ex.map(rank, jobs)))
    for w in WORKS:
        a, b = res[(w, 'g6', G6)], res[(w, 'g56', G56)]
        core = sorted(k for k in a if a.get(k) == '核心' and b.get(k) == '核心'); either = sorted(k for k in a if '核心' in (a.get(k), b.get(k)))
        wr(S/f'core_{w}.json', {'core': core, 'either': either, 'n': len(a)})
        print(w, '要点', len(a), '两位都判核心', len(core), '至少一位判核心', len(either), 'GPT-6 核心', sum(v == '核心' for v in a.values()), 'GPT-5.6 核心', sum(v == '核心' for v in b.values()), flush=True)


def score(w, t, key='core'):
    core = set(rd(S/f'core_{w}.json')[key]); xs = []
    for j in JUDGES:
        p = S/f'beadcovA_{w}_{j}_{t}.json'
        if p.exists():
            v = {x['id']: x.get('verdict') for x in rd(p)['items']}
            xs.append(round(sum(v.get(k) == '留住' for k in core)/max(1, len(core)), 3))
    return (round(sum(xs)/len(xs), 3) if xs else None), xs


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.argv[1] == 'list': build()
    else:
        for t in sys.argv[2:]:
            for w in WORKS: print(t, w, '核心覆盖', score(w, t), '宽口径', score(w, t, 'either')[0], flush=True)
