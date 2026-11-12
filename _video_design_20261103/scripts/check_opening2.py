import json, sys
import numpy as np
import librosa
sys.stdout.reconfigure(encoding='utf-8')
SR, HOP = 22050, 256
fps = SR / HOP
# 《船歌》开头：每 0.2 秒的响度，以及第一组音（低音八度）所在音高上的能量
y, _ = librosa.load('work/op60.wav', sr=SR, mono=True, duration=5)
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
C = np.abs(librosa.cqt(y, sr=SR, hop_length=HOP, fmin=librosa.midi_to_hz(21), n_bins=88, bins_per_octave=12))
m = json.load(open('work/op60_music.json', encoding='utf-8'))
first = [n for n in m['notes'] if n['s'] < 0.05]
print('第一组音高', [n['p'] for n in first])
for t in np.arange(0, 4.4, 0.2):
    i = int(t * fps)
    j = int((t + 0.2) * fps)
    low = float(np.mean(C[[n['p'] - 21 for n in first], i:j]))
    low2 = float(np.mean(C[[n['p'] + 12 - 21 for n in first], i:j]))
    print(f'{t:4.1f}s 响度{float(np.mean(rms[i:j])):.4f} 该音高{low:.3f} 高八度{low2:.3f}')
# 《幻想波兰舞曲》前 30 秒：校正前后，每组音到最近录音起音的偏差
y2, _ = librosa.load('work/op61.wav', sr=SR, mono=True, duration=30)
ons = librosa.onset.onset_detect(y=y2, sr=SR, hop_length=HOP, units='time', backtrack=False, delta=0.08)
for tag, f in (('校正前', 'work/op61_music.json'), ('校正后', 'work/op61_music_v2.json')):
    ns = json.load(open(f, encoding='utf-8'))['notes']
    gs = []
    for n in sorted(ns, key=lambda x: x['s']):
        if n['s'] > 30:
            break
        if not gs or n['s'] - gs[-1] >= 0.05:
            gs.append(n['s'])
    gs = np.array(gs)
    row = []
    for a in range(0, 30, 5):
        g = gs[(gs >= a) & (gs < a + 5)]
        if len(g):
            d = [abs(float(ons[np.argmin(np.abs(ons - x))] - x)) for x in g]
            row.append(f'{a}-{a + 5}秒 {np.median(d) * 1000:.0f}')
    print(tag, '到最近起音的偏差中位数（毫秒）：', '；'.join(row))
