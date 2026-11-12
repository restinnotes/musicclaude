"""11-08 分阶段流水线快筛（两位顾问 GPT-6、GPT-5.6 独立给出、意见一致的提速办法，见 r3/speed/）。
每个候选包（两首）各走一个状态机，候选之间不互相等：
  A 盲比初筛：每首 2 位评委（GPT-6、GPT-5.6 各 1）× 两种顺序，对当前主线。任一首两位评委都稳定选主线 → 整包淘汰（明显输）。
  B 走样 + 覆盖初筛：每首 2 位评委。两位同报同一处严重走样，或覆盖均值比 w23 低 0.03 以上 → 整包淘汰。
  C 补齐：没有明显失败的，盲比、走样、覆盖都补到 4 位评委（原快筛标准），再出结论。
两首始终同阶段：一首明显失败，整包停。
python r3/stage.py 主线TAG 候选TAG [候选TAG...]
"""
import os, sys, threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
os.environ['PUB_BC_ALL'] = '1'; os.environ['PUB_JREP'] = '1'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pub24, faithful, vs2, gate2
from pub24 import S, rd, WORKS, JUDGES
sys.stdout.reconfigure(encoding='utf-8')
J1, J2 = ['g6', 'g56'], ['g6r', 'g56r']
POOL = ThreadPoolExecutor(int(os.environ.get('PUB_PAR', '28')))
LOCK = threading.Lock()


def runall(jobs):
    def f(x):
        k, a = x
        try:
            if k == 'fa': faithful.one(a)
            elif k == 'bc': pub24.bead_cov(a)
            else: vs2.one(a)
        except SystemExit as e: print(e, flush=True)
        except Exception as e: print('失败', k, a, repr(e)[:150], flush=True)
    list(POOL.map(f, jobs))


def vs_state(w, name, js):
    st = {'新': 0, '敏感': 0, '旧': 0}; dims = {d: [0, 0] for d in gate2.DIMS}
    for j in js:
        px, py = S/f'{vs2.PRE}_{w}_{j}_{name}_X.json', S/f'{vs2.PRE}_{w}_{j}_{name}_Y.json'
        if not (px.exists() and py.exists()): continue
        rx, ry = rd(px), rd(py)
        sc = (1 if rx['better'] == 'X' else 0 if rx['better'] == '平' else -1) + (1 if ry['better'] == 'Y' else 0 if ry['better'] == '平' else -1)   # vs3 允许判平
        st['新' if sc == 2 else '旧' if sc == -2 else '敏感'] += 1
        for r, seat in ((rx, 'X'), (ry, 'Y')):
            for d in gate2.DIMS:
                v = (r.get('nets') or {}).get(d)
                if v in ('X', 'Y'): dims[d][0 if v == seat else 1] += 1
    return st, dims


def faith_cons(w, t, js):
    grp = {}
    for j in js:
        p = S/f'faith_{w}_{j}_{t}.json'
        if not p.exists(): continue
        for x in rd(p)['issues']:
            if x.get('severity') == '严重': grp.setdefault((x.get('sec'), (x.get('screen') or '').replace('【', '').replace('】', '')[:8]), set()).add(j)
    return sum(len(v) >= 2 for v in grp.values())


def bc_mean(w, t, js):
    xs = []
    for j in js:
        p = S/f'{pub24.BC_PRE}_{w}_{j}_{t}.json'
        if p.exists(): it = rd(p)['items']; xs.append(sum(x.get('verdict') == '留住' for x in it)/max(1, len(it)))
    return round(sum(xs)/len(xs), 3) if xs else None


def say(t, msg):
    with LOCK: print(f'【{t}】{msg}', flush=True)


def cand(main, t):
    name = f'{t}__{main}'
    runall([('v2', (w, j, t, main, name, s)) for w in WORKS for j in J1 for s in 'XY'])
    for w in WORKS:
        st, _ = vs_state(w, name, J1)
        if st['旧'] == len(J1): say(t, f'A 淘汰：{w} 两位评委都稳定选主线 {main}'); return False
    say(t, 'A 过：' + '；'.join(f"{w} {vs_state(w, name, J1)[0]}" for w in WORKS))
    runall([(k, (w, j, t)) for w in WORKS for j in J1 for k in ('fa', 'bc')])
    for w in WORKS:
        nf, b, b0 = faith_cons(w, t, J1), bc_mean(w, t, J1), gate2.bcov(w, 'w23')
        if nf: say(t, f'B 淘汰：{w} 两位评委同报 {nf} 处严重走样'); return False
        if b is not None and b0 is not None and b < b0 - 0.03: say(t, f'B 淘汰：{w} 覆盖 {b}（w23 {b0}）'); return False
    say(t, 'B 过：' + '；'.join(f"{w} 覆盖 {bc_mean(w, t, J1)}" for w in WORKS))
    runall([('v2', (w, j, t, main, name, s)) for w in WORKS for j in J2 for s in 'XY'] + [(k, (w, j, t)) for w in WORKS for j in J2 for k in ('fa', 'bc')])
    out = []; ok = True
    for w in WORKS:
        st, dims = vs_state(w, name, J1+J2); nf = faith_cons(w, t, J1+J2); b, b0 = bc_mean(w, t, J1+J2), gate2.bcov(w, 'w23')
        good = st['旧'] == 0 and st['新'] >= 3 and nf == 0 and all(a >= c for a, c in dims.values()) and gate2.barnums(w, t) == 0
        ok &= good
        out.append(f"{w}：对 {main} 选新 {st['新']}/敏感 {st['敏感']}/选旧 {st['旧']}；分项 " + '、'.join(f"{d} {a}:{c}" for d, (a, c) in dims.items()) + f"；走样 {nf}；覆盖 {b}（w23 {b0}）→ {'过' if good else '没过'}")
    say(t, f"C {'两首都过，送全套' if ok else '没过'}：" + ' | '.join(out))
    return ok


if __name__ == '__main__':
    main, cands = sys.argv[1], sys.argv[2:]
    with ThreadPoolExecutor(len(cands)) as ex: res = list(ex.map(lambda t: cand(main, t), cands))
    print('结果', dict(zip(cands, res)), flush=True)
