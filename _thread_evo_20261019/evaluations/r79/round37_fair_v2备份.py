"""R37 正反盲比：同一对版本，每首 × 每位评委 × 新版排前/排后各一票，共 8 票，并行。
提示词和门槛不变（8 票至少 6 票新版，单独/啰嗦/人话净胜不为负，至少 6 票不退步）；只是把座位平衡掉。
起因：206 票统计，新版排 X 时 57% 选新版，排 Y 时 36%。 usage: python round37_fair.py TAG BASE"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, screen_flow as F, v6fix as V

DIM = F.DIMENSIONS


def rid_of(w, j, tag, base, seat):
    return f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}'


def one(w, j, tag, base, seat):
    rid = rid_of(w, j, tag, base, seat)
    a, b = V.graph_of(w, base), V.graph_of(w, tag)
    x, y = (b, a) if seat == 'newX' else (a, b)
    msg = V.BLIND2.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2, X=V.view(x), Y=V.view(y), BEADS=V.beads(w))
    if not evo.done(rid):
        for k in range(4):
            evo.check_submission(V.JUDGES[j])
            if evo.call(rid, msg, model=V.JUDGES[j], meta={'stage': 'fair-blind', 'web': True}):
                break
    return read(w, j, tag, base, seat)


def read(w, j, tag, base, seat):
    rid = rid_of(w, j, tag, base, seat)
    d = V.parse(rid) if evo.done(rid) else None
    if not d or d.get('better') not in ('X', 'Y', '差不多'):
        return None
    new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
    secs = d['sections']
    return {'w': w, 'j': j, 'seat': seat, 'new_win': d['better'] == new, 'no_regress': d.get(f'{new}_replacing_{old}_regress') == '否',
            'net': {k: sum((s[k] == new) - (s[k] == old) for s in secs) for k in DIM}}


def summary(tag, base):
    rows = [read(w, j, tag, base, s) for w in F.WORKS for j in F.JUDGES for s in ('newX', 'newY')]
    got = [r for r in rows if r]
    sums = {k: sum(r['net'][k] for r in got) for k in DIM}
    wins, noreg = sum(r['new_win'] for r in got), sum(r['no_regress'] for r in got)
    ok = len(got) == 8 and wins >= 6 and noreg >= 6 and all(sums[k] >= 0 for k in DIM[:3])
    d = {'tag': tag, 'base': base, 'complete': len(got), 'wins': wins, 'no_regress': noreg, 'net_sums': sums, 'pass': ok, 'rows': got}
    (V.OUT / f'fair_{tag}_vs{base}.json').write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return d


if __name__ == '__main__':
    F.configure()
    tag, base = sys.argv[1:3]
    jobs = [(w, j, tag, base, s) for w in F.WORKS for j in F.JUDGES for s in ('newX', 'newY')]
    with ThreadPoolExecutor(max_workers=int(os.environ.get('FAIR_WORKERS', '8'))) as pool:
        list(pool.map(lambda a: one(*a), jobs))
    d = summary(tag, base)
    print(tag, '通过' if d['pass'] else '未过', f"{d['wins']}/{d['complete']}", '不退步', d['no_regress'], d['net_sums'], flush=True)
    for r in d['rows']:
        print(' ', r['w'], r['j'], r['seat'], '新胜' if r['new_win'] else '旧胜', '不退步' if r['no_regress'] else '退步', r['net'], flush=True)
