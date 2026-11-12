"""11-08 DAG2 门槛第二版（按用户 11-08 同意的大众版标准 7 条）。只读已有结果文件，不调模型。
快筛层（quick2.py 产出）：
  第 5 条 不丢：意思走样——至少两位评委同报一处严重问题就没过（硬门槛，已校准）；整屏珠子覆盖不低于 w23（底线）。
  第 1、2、3、4、6、7 条：新盲比 vs2 对 w23（两种顺序配对）——稳定选 w23 为 0；分项 why/alone（第 1 条）、flow（第 2 条）、concise（第 3 条）、human（第 4 条）、fine（第 6 条）、scan（第 7 条）新版赢的不少于 w23。
w23 只作底线；主线前进另要直接赢过当前主线（vs2 对主线）。
python gate2.py TAG [TAG...]
"""
import os, sys
os.environ['PUB_BC_ALL'] = '1'
import pub24, vs2
from pub24 import S, rd, WORKS, JUDGES

DIMS = ['scan', 'flow', 'concise', 'human', 'why', 'alone', 'fine']


def faith(w, t):
    sev = {j: [x for x in rd(S/f'faith_{w}_{j}_{t}.json')['issues'] if x.get('severity') == '严重'] for j in JUDGES if (S/f'faith_{w}_{j}_{t}.json').exists()}
    if len(sev) < len(JUDGES): return None, []
    grp = {}
    for j, v in sev.items():
        for x in v: grp.setdefault((x.get('sec'), (x.get('screen') or '').replace('【', '').replace('】', '')[:8]), set()).add(j)
    cons = [k for k, js in grp.items() if len(js) >= 2]
    return len(cons), cons


def bcov(w, t):
    xs = []
    for j in JUDGES:
        p = S/f'{pub24.BC_PRE}_{w}_{j}_{t}.json'
        if p.exists():
            it = rd(p)['items']; xs.append(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)))
    return round(sum(xs)/len(xs), 3) if len(xs) == len(JUDGES) else None


def vs(w, name):
    st = {'新': 0, '敏感': 0, '旧': 0}; dims = {d: [0, 0] for d in DIMS}; n = 0
    for j in JUDGES:
        px, py = S/f'{vs2.PRE}_{w}_{j}_{name}_X.json', S/f'{vs2.PRE}_{w}_{j}_{name}_Y.json'
        if not (px.exists() and py.exists()): continue
        rx, ry = rd(px), rd(py); n += 1
        sc = (1 if rx['better'] == 'X' else 0 if rx['better'] == '平' else -1) + (1 if ry['better'] == 'Y' else 0 if ry['better'] == '平' else -1)   # vs3 允许判平
        st['新' if sc == 2 else '旧' if sc == -2 else '敏感'] += 1
        for r, seat in ((rx, 'X'), (ry, 'Y')):
            for d in DIMS:
                v = (r.get('nets') or {}).get(d)
                if v in ('X', 'Y'): dims[d][0 if v == seat else 1] += 1
    return (n == len(JUDGES)), st, dims


def _avg(xs):
    xs = [x for x in xs if x is not None]; return round(sum(xs)/len(xs), 3) if xs else None


def cov(w, t):
    out = []
    for j in JUDGES:
        p = pub24.R3/f'cover_{w}_{j}_{t}.json'
        if p.exists(): it = rd(p)['items']; out.append(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)))
    return _avg(out) if len(out) == len(JUDGES) else None


def fine(w, t):
    try:
        import pub25; return pub25.score(w, t)[0]
    except Exception: return None


def lall(w, t):
    sc, med, sev = [], [], []
    def num(x):
        try: return float(str(x).split('/')[0])
        except Exception: return None
    for j in JUDGES:
        p = S/f'langallD_{w}_{j}_{t}.json'
        if p.exists():
            r = rd(p); sc.append(num(r.get('score') or r.get('overall_score'))); cum = r.get('cumulative') or []
            med.append(sum((c.get('severity') or '') in ('中等', '严重', '较重') for c in cum)); sev.append(sum((c.get('severity') or '') in ('严重', '较重') for c in cum))
    if len(sc) < len(JUDGES): return None, None, None
    return _avg(sc), _avg(med), _avg(sev)


def barnums(w, t):
    """11-08 机械硬检查：正文里不许出现小节号（评委不把它当问题，K3A 里约 56 处没人报；局部内容靠“到时出现”）。"""
    import re
    R = re.compile(r'\d+\s*[–—\-~～至到]\s*\d+\s*小节|第\s*\d+\s*小节|\d+\s*小节|小节\s*\d+')
    sc = rd(S/f'screen_{w}_{t}.json')
    return sum(bool(R.search(x['text'])) for s in sc['sections'] for x in s['rows'] if x['kind'] == 'line') + sum(bool(R.search(i['text'])) for s in sc['sections'] for x in s['rows'] if x['kind'] == 'feel' for i in x['items'])


def gate(t, base='w23'):
    ok_all = True; lines = []
    for w in WORKS:
        nf, cons = faith(w, t); b, b0 = bcov(w, t), bcov(w, base); full, st, dims = vs(w, f'{t}__{base}')
        checks = {'意思走样': nf == 0 if nf is not None else None, '整屏珠子覆盖': (b >= b0) if (b is not None and b0 is not None) else None,
                  '盲比稳定选旧为 0': st['旧'] == 0 if full else None, '正文无小节号': barnums(w, t) == 0}
        for d, (a, c) in dims.items(): checks[f'盲比 {d}'] = (a >= c) if full else None
        if os.environ.get('PUB_FULL') == '1':   # 全套：原稿覆盖、精细体验、整屏人话（分数不低于 w23，严重累积问题不多于 w23）
            c, c0 = cov(w, t), cov(w, base); f, f0 = fine(w, t), fine(w, base); (ls, lm, lv), (ls0, lm0, lv0) = lall(w, t), lall(w, base)
            checks.update({'原稿覆盖': (c >= c0) if None not in (c, c0) else None, '精细体验': (f >= f0) if None not in (f, f0) else None,
                           '整屏人话': (ls >= ls0) if None not in (ls, ls0) else None, '整屏严重累积': (lv <= lv0) if None not in (lv, lv0) else None})
            lines.append(f"{w} 全套：原稿覆盖 {c}（w23 {c0}）；精细 {f}（w23 {f0}）；整屏人话 {ls}、中等以上 {lm}、严重 {lv}（w23 {ls0}、{lm0}、{lv0}）")
        bad = [k for k, v in checks.items() if v is False]; miss = [k for k, v in checks.items() if v is None]
        ok = not bad and not miss; ok_all &= ok
        lines.append(f"{w}：走样 {nf} 处 {cons[:3]}；整屏珠子覆盖 {b}（w23 {b0}）；盲比 选新 {st['新']}/敏感 {st['敏感']}/选旧 {st['旧']}；分项新:旧 " + '、'.join(f"{d} {a}:{c}" for d, (a, c) in dims.items())
                     + f" → {'过' if ok else '没过：' + '、'.join(bad)}" + (f"；未测：{'、'.join(miss)}" if miss else ''))
    print(f"== {t} {'两首都过' if ok_all else '没过'}"); [print('  '+x) for x in lines]
    return ok_all


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    for t in sys.argv[1:]: gate(t)
