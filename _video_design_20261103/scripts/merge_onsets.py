# 局部采用校正：只在“校正后明显更贴近录音”的 5 秒窗口里换时间，其余保持原对齐。
# 判断依据：每组音到最近录音起音的距离（中位数）。密集段这个数字本来就小，规则基本不会触发。
import json, sys
from collections import defaultdict
import numpy as np
import librosa
sys.stdout.reconfigure(encoding='utf-8')
SR, HOP = 22050, 256
IMPROVE = 0.06   # 至少改善 60 毫秒才采用
WIN = 5.0


def groups(ns):
    out = []
    for n in sorted(ns, key=lambda x: x['s']):
        if not out or n['s'] - out[-1] >= 0.05:
            out.append(n['s'])
    return np.array(out)


def dev(gs, ons, a, b):
    g = gs[(gs >= a) & (gs < b)]
    if len(g) == 0:
        return None, 0
    return float(np.median([abs(ons[np.argmin(np.abs(ons - x))] - x) for x in g])), len(g)


for name, wav, base in [('船歌', 'work/op60.wav', 'work/op60_music'), ('幻想波兰舞曲', 'work/op61.wav', 'work/op61_music')]:
    m1 = json.load(open(base + '.json', encoding='utf-8'))
    m2 = json.load(open(base + '_v2.json', encoding='utf-8'))
    y, _ = librosa.load(wav, sr=SR, mono=True)
    # 分段检测：整首一起算时，安静段的起音会被响的段落压掉，开头和弱奏处就测不准
    seg = 30 * SR
    ons = []
    for k in range(0, len(y), seg):
        part = y[k:k + seg]
        if len(part) < SR:
            continue
        ons += [k / SR + float(t) for t in librosa.onset.onset_detect(y=part, sr=SR, hop_length=HOP, units='time', backtrack=False, delta=0.07)]
    ons = np.array(ons)
    n1, n2 = m1['notes'], m2['notes']
    # 同一手、同一音高的音，先后次序不变，据此一一对应
    d1, d2 = defaultdict(list), defaultdict(list)
    for n in sorted(n1, key=lambda x: x['s']):
        d1[(n['h'], n['p'])].append(n)
    for n in sorted(n2, key=lambda x: x['s']):
        d2[(n['h'], n['p'])].append(n)
    pairs = []
    for k in d1:
        if len(d1[k]) != len(d2[k]):
            raise SystemExit('音符数对不上')
        pairs += list(zip(d1[k], d2[k]))
    g1, g2 = groups(n1), groups(n2)
    T = float(m1['dur'])
    chosen = []
    rows = []
    for a in np.arange(0, T, WIN):
        b = a + WIN
        x1, c1 = dev(g1, ons, a, b)
        x2, c2 = dev(g2, ons, a, b)
        if x1 is None or x2 is None:
            continue
        rows.append((a, x1, x2, c1))
        # 只在稀疏窗口采用：密集段“最近的起音”总是很近，这个判断没有意义
        if x1 - x2 >= IMPROVE and c1 <= 14:
            chosen.append((a, b))
    inwin = lambda t: any(a <= t < b for a, b in chosen)
    out = []
    used = 0
    for p, q in pairs:
        if inwin(p['s']):
            r = dict(q)
            used += 1
        else:
            r = dict(p)
        out.append(r)
    # 第一个音：原对齐把它夹在 0 秒，一律用校正值
    firsts = [q for p, q in pairs if p['s'] < 0.05]
    fid = {id(p): q for p, q in pairs if p['s'] < 0.05}
    for i, (p, q) in enumerate(pairs):
        if p['s'] < 0.05:
            out[i] = dict(q)
    # 窗口交界保持先后次序（只防止明显倒序，按原次序排）
    order = sorted(range(len(pairs)), key=lambda i: pairs[i][0]['s'])
    last = -1.0
    for i in order:
        if out[i]['s'] < last - 0.05:
            d = last - out[i]['s']
            out[i]['s'] = round(out[i]['s'] + d, 3)
            out[i]['e'] = round(max(out[i]['e'], out[i]['s'] + 0.05), 3)
        last = max(last, out[i]['s'])
    out.sort(key=lambda n: (n['s'], n['p']))
    m1['notes'] = out
    json.dump(m1, open(base + '_v3.json', 'w', encoding='utf-8'))
    d_all = np.array([r[1] for r in rows])
    g3 = groups(out)
    d3 = [dev(g3, ons, a, a + WIN)[0] for a, *_ in rows]
    d3 = np.array([x if x is not None else np.nan for x in d3])
    print(f'== {name}：采用校正的窗口 {len(chosen)}/{len(rows)}，涉及 {used} 个音；第一个音 → {min(n["s"] for n in out):.2f} 秒')
    print('  采用的窗口（秒）：', [int(a) for a, b in chosen])
    print(f'  到最近起音的偏差：窗口中位数 {np.median(d_all) * 1000:.0f} → {np.nanmedian(d3) * 1000:.0f} 毫秒；超过 300 毫秒的窗口 {int((d_all > 0.3).sum())} → {int(np.nansum(d3 > 0.3))}')
    bad = [(int(rows[i][0]), round(float(d3[i]) * 1000)) for i in np.argsort(-np.nan_to_num(d3))[:8]]
    print('  校正后仍最差的窗口（起点秒，毫秒）：', bad)
