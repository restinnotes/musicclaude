# 核对开头：录音里实际出声的时间，和音符数据的时间，逐个对比
import json, sys
import numpy as np
import librosa
sys.stdout.reconfigure(encoding='utf-8')
SR, HOP = 22050, 256
for name, wav, mus, end in [('船歌', 'work/op60.wav', 'work/op60_music.json', 30), ('幻想波兰舞曲', 'work/op61.wav', 'work/op61_music.json', 30)]:
    y, _ = librosa.load(wav, sr=SR, mono=True, duration=end)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    fps = SR / HOP
    first = next(i / fps for i, v in enumerate(rms) if v > 0.01)
    ons = librosa.onset.onset_detect(y=y, sr=SR, hop_length=HOP, units='time', backtrack=False, delta=0.08)
    notes = json.load(open(mus, encoding='utf-8'))['notes']
    groups = []
    for n in notes:
        if n['s'] > end:
            break
        if groups and n['s'] - groups[-1][0] < 0.05:
            groups[-1][1] += 1
        else:
            groups.append([n['s'], 1])
    mt = np.array([g[0] for g in groups])
    print(f'== {name}：录音第一次明显出声 {first:.2f} 秒；音符第一个 {mt[0]:.2f} 秒')
    print('  录音起音（前 14 个）：', [round(float(x), 2) for x in ons[:14]])
    print('  音符起音（前 14 个）：', [round(float(x), 2) for x in mt[:14]])
    # 每 5 秒窗口：每个音符组最近的录音起音有多远
    for a in range(0, end, 5):
        m = mt[(mt >= a) & (mt < a + 5)]
        if len(m) == 0 or len(ons) == 0:
            print(f'  {a:2d}–{a + 5:2d} 秒：无音符')
            continue
        d = [float(ons[np.argmin(np.abs(ons - x))] - x) for x in m]
        print(f'  {a:2d}–{a + 5:2d} 秒：{len(m):2d} 组音符，录音相对音符的偏差中位数 {np.median(d) * 1000:6.0f} 毫秒')
