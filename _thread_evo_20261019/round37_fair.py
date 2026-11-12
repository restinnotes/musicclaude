"""R37 正反盲比：同一对版本，每首 × 每位评委 × 新版排前/排后各一票，共 8 票，并行。
提示词和门槛不变（8 票至少 6 票新版，单独/啰嗦/人话净胜不为负，至少 6 票不退步）；只是把座位平衡掉。
起因：206 票统计，新版排 X 时 57% 选新版，排 Y 时 36%。 usage: python round37_fair.py TAG BASE"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import evo, screen_flow as F, v6fix as V

# 11-06 用户：“要的呀 center 和来回摆都应该加入盲比”。FAIR_V=3（默认）在盲比里加 center（贴 Center）和 step（往前走、不来回）两项；
# 门槛：8 票至少 6 票新版、至少 6 票不退步，alone/lean/plain/center/step 净胜都不为负（cover 照旧只看不卡）。FAIR_V=2 是旧版，只为复现旧结果。
FV = os.environ.get('FAIR_V', '3')
DIM = F.DIMENSIONS + (('center', 'step') if FV == '3' else ())
# 11-06 用户：“dag 的人话标准如果实在会冲突可能能放宽 反正 dag2 还要再人话化一遍”。v3 里人话（plain）和覆盖一样只看不卡。
GATE = DIM[:3] if FV == '2' else ('alone', 'lean', 'center', 'step')
ADD3 = """5. center（贴 Center）：这条线本该讲的是这件事——{CENTER}。哪一版这一段讲的更是这件事本身（Center 里那几样东西是不是都在、是不是缠在一起），而不是一件和它相近的另一件事？
6. step（往前走、不来回）：放在前面所有段之后看，哪一版这一段是在往前走——带出前面没有的新东西（新的处境、更深一层的认识、一个落到自己身上的后果）——而不是回到前面已经讲过的状态，或者换个说法把前面的话再说一遍？整条线要像一步步往前探索，不像在迷宫里来回绕。
"""


def prompt(w, x, y):
    p = V.BLIND2
    if FV == '3':
        p = p.replace('5. lost：', ADD3.replace('{CENTER}', V.graph_of(w, 'r78a')['center']) + '7. lost：')
        p = p.replace('最后整体判断：', '最后整体判断（以上六项同样重要）：')
        p = p.replace('"cover": "X", "cover_why": "……",', '"cover": "X", "cover_why": "……", "center": "Y", "center_why": "……", "step": "X", "step_why": "……",')
        assert '"step"' in p and '6. step' in p
    return p.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2, X=V.view(x), Y=V.view(y), BEADS=V.beads(w))


def rid_of(w, j, tag, base, seat):
    return f'v6b3_{w}_{j}_{tag}_vs{base}_{seat}' if FV == '2' else f'v6b4_{w}_{j}_{tag}_vs{base}_{seat}'


def one(w, j, tag, base, seat):
    rid = rid_of(w, j, tag, base, seat)
    a, b = V.graph_of(w, base), V.graph_of(w, tag)
    x, y = (b, a) if seat == 'newX' else (a, b)
    msg = prompt(w, x, y)
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
            'net': {k: sum((s.get(k) == new) - (s.get(k) == old) for s in secs) for k in DIM}}


def summary(tag, base):
    # 11-06 晚：某一首两版一字不差（修的人判这首不用改）时，评委只能判“差不多”，不计这一首的票；门槛按比例算
    same = {w for w in F.WORKS if V.view(V.graph_of(w, tag)) == V.view(V.graph_of(w, base))}
    rows = [read(w, j, tag, base, s) for w in F.WORKS if w not in same for j in F.JUDGES for s in ('newX', 'newY')]
    got = [r for r in rows if r]; n = len(rows)
    sums = {k: sum(r['net'][k] for r in got) for k in DIM}
    wins, noreg = sum(r['new_win'] for r in got), sum(r['no_regress'] for r in got)
    # 用户 11-04：两首要各自过，合计票和净胜不能盖住单首失败。每首（改动了的）分别看选新、不退步和各项净胜
    per = {}
    for w in F.WORKS:
        if w in same: continue
        R_ = [r for r in got if r['w'] == w]; m = len(F.JUDGES) * 2
        per[w] = {'wins': sum(r['new_win'] for r in R_), 'no_regress': sum(r['no_regress'] for r in R_), 'n': m,
                  'net': {k: sum(r['net'][k] for r in R_) for k in DIM}}
        per[w]['pass'] = len(R_) == m and per[w]['wins'] >= 0.75 * m and per[w]['no_regress'] >= 0.75 * m and all(per[w]['net'][k] >= 0 for k in GATE)
    ok = n > 0 and len(got) == n and all(x['pass'] for x in per.values())
    d = {'tag': tag, 'base': base, 'same': sorted(same), 'per_work': per, 'complete': len(got), 'wins': wins, 'no_regress': noreg, 'net_sums': sums, 'pass': ok, 'rows': got}
    (V.OUT / (f'fair_{tag}_vs{base}.json' if FV == '2' else f'fair3_{tag}_vs{base}.json')).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
    return d


if __name__ == '__main__':
    F.configure()
    tag, base = sys.argv[1:3]
    jobs = [(w, j, tag, base, s) for w in F.WORKS for j in F.JUDGES for s in ('newX', 'newY')]
    import zlib
    def run(a):   # gpt3、gpt4 按调用编号分流
        evo.TL.route = 'gpt4s' if zlib.crc32(rid_of(*a).encode()) % 2 else 'gpt3s'; return one(*a)
    with ThreadPoolExecutor(max_workers=int(os.environ.get('FAIR_WORKERS', '8'))) as pool:
        list(pool.map(run, jobs))
    d = summary(tag, base)
    print(tag, '通过' if d['pass'] else '未过', f"{d['wins']}/{d['complete']}", '不退步', d['no_regress'], d['net_sums'], flush=True)
    for r in d['rows']:
        print(' ', r['w'], r['j'], r['seat'], '新胜' if r['new_win'] else '旧胜', '不退步' if r['no_regress'] else '退步', r['net'], flush=True)
