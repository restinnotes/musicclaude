# 按录音校正每组音符的起音时间：在原时间附近，找这组音高上能量突然上升的时刻。
# 只移动时间，不改音高；用相邻几组的中位数防止个别音被错吸到别处。输出前后对比，效果不好就不用。
import json, sys
import numpy as np
import librosa
from scipy.ndimage import uniform_filter1d, median_filter
sys.stdout.reconfigure(encoding='utf-8')
SR, HOP = 22050, 256
fps = SR / HOP


def load_flux(wav):
    y, _ = librosa.load(wav, sr=SR, mono=True)
    C = np.abs(librosa.cqt(y, sr=SR, hop_length=HOP, fmin=librosa.midi_to_hz(21), n_bins=88, bins_per_octave=12))
    L = np.log1p(C * 40)
    D = np.maximum(0, np.diff(L, axis=1, prepend=L[:, :1]))
    D = uniform_filter1d(D, size=3, axis=1)
    ons = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    return y, C, D, ons


def groups_of(notes):
    gs = []
    for i, n in enumerate(sorted(range(len(notes)), key=lambda k: notes[k]['s'])):
        s = notes[n]['s']
        if gs and s - gs[-1]['s'] < 0.05:
            gs[-1]['idx'].append(n)
        else:
            gs.append(dict(s=s, idx=[n]))
    return gs


def score_flux(D, ps, nframes):
    f = np.zeros(nframes)
    for p in set(ps):
        for q in (p, p + 12):           # 低音的基频弱，八度泛音一起看
            b = q - 21
            if 0 <= b < 88:
                f += D[b, :nframes]
    return f


def corr_windows(notes, ons, win=20):
    tr = np.zeros(len(ons))
    for n in notes:
        k = int(n['s'] * fps)
        if 0 <= k < len(tr):
            tr[k] += 1
    tr = np.convolve(tr, np.hanning(9), 'same')
    out = []
    W = int(win * fps)
    for a in range(0, len(ons) - W, W):
        o = ons[a:a + W] - ons[a:a + W].mean()
        t = tr[a:a + W] - tr[a:a + W].mean()
        out.append(float(np.dot(t, o) / (np.linalg.norm(t) * np.linalg.norm(o) + 1e-9)))
    return np.array(out)


for name, wav, mus, firstw in [('船歌', 'work/op60.wav', 'work/op60_music.json', 3.0), ('幻想波兰舞曲', 'work/op61.wav', 'work/op61_music.json', 1.2)]:
    m = json.load(open(mus, encoding='utf-8'))
    notes = m['notes']
    y, C, D, ons = load_flux(wav)
    nfr = D.shape[1]
    gs = groups_of(notes)
    offs = []
    for gi, g in enumerate(gs):
        ps = [notes[i]['p'] for i in g['idx']]
        f = score_flux(D, ps, nfr)
        W = firstw if gi == 0 else 0.7
        sg = firstw * 0.6 if gi == 0 else 0.3
        a = max(0, int((g['s'] - W) * fps))
        b = min(nfr - 1, int((g['s'] + W) * fps))
        if b <= a:
            offs.append(0.0)
            continue
        tt = np.arange(a, b) / fps
        wgt = np.exp(-((tt - g['s']) ** 2) / (2 * sg * sg))
        sc = f[a:b] * wgt
        k = int(np.argmax(sc))
        # 太弱就不信
        if f[a:b][k] < np.percentile(f, 80):
            offs.append(np.nan)
        else:
            offs.append(float(tt[k] - g['s']))
    offs = np.array(offs)
    valid = np.where(~np.isnan(offs))[0]
    offs = np.interp(np.arange(len(offs)), valid, offs[valid])
    smooth = median_filter(offs, size=5, mode='nearest')
    # 第一组不参与平滑：开头那个音常被夹在 0 秒
    smooth[0] = offs[0]
    new_t = np.array([g['s'] for g in gs]) + smooth
    # 保持先后次序
    for i in range(1, len(new_t)):
        new_t[i] = max(new_t[i], new_t[i - 1] + 0.005)
    before = [dict(s=n['s']) for n in notes]
    after = json.loads(json.dumps(notes))
    for g, t in zip(gs, new_t):
        d = float(t - g['s'])
        for i in g['idx']:
            after[i]['s'] = round(notes[i]['s'] + d, 3)
            after[i]['e'] = round(max(notes[i]['e'] + d, after[i]['s'] + 0.05), 3)
    # 重算响度（用校正后的时间）
    Cn = C / (np.percentile(C, 99.5) + 1e-9)
    env = librosa.feature.rms(y=y, hop_length=HOP)[0]
    ens = []
    gsv = []
    for n in after:
        i0 = int(n['s'] * fps)
        i1 = max(i0 + 2, int((n['s'] + 0.15) * fps))
        b = min(87, max(0, n['p'] - 21))
        ens.append(float(np.mean(Cn[b, i0:i1])) if i0 < C.shape[1] else 0.0)
        gsv.append(float(np.mean(env[i0:i1])) if i0 < len(env) else 0.0)
    ens = np.clip(np.array(ens) / np.percentile(ens, 97), 0, 1) ** 0.6
    gsv = np.clip(np.array(gsv) / np.percentile(gsv, 98), 0, 1) ** 0.7
    for n, a_, b_ in zip(after, ens, gsv):
        n['en'] = round(float(0.55 * a_ + 0.45 * b_), 3)
    after.sort(key=lambda n: (n['s'], n['p']))
    c0 = corr_windows(before, ons)
    c1 = corr_windows(after, ons)
    print(f'== {name}  音符组 {len(gs)}')
    print(f'  整段相关（20 秒窗口均值）：校正前 {c0.mean():.3f} → 校正后 {c1.mean():.3f}；变差的窗口 {int((c1 < c0 - 0.02).sum())}/{len(c0)}，变好的 {int((c1 > c0 + 0.02).sum())}/{len(c0)}')
    print(f'  校正量绝对值：中位数 {np.median(np.abs(smooth)) * 1000:.0f} 毫秒，90% 分位 {np.percentile(np.abs(smooth), 90) * 1000:.0f} 毫秒，最大 {np.abs(smooth).max() * 1000:.0f} 毫秒')
    print('  第一组：', round(gs[0]['s'], 2), '→', round(float(new_t[0]), 2), '；前 8 组：', [round(float(x), 2) for x in new_t[:8]])
    print('  最差的 5 个窗口（起点秒，前→后）：', [(int(i * 20), round(float(c0[i]), 2), round(float(c1[i]), 2)) for i in np.argsort(c0)[:5]])
    m['notes'] = after
    json.dump(m, open(mus.replace('_music.json', '_music_v2.json'), 'w', encoding='utf-8'))
