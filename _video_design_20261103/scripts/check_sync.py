# 端到端核对：从成片里取出音轨，看它和“画面用的音符时间”是否对齐（检查合成环节有没有引入偏移）
import json, os, subprocess, sys
import numpy as np
import librosa
sys.stdout.reconfigure(encoding='utf-8')
SR, HOP = 22050, 512
fps = SR / HOP
CASES = [
    ('out/船歌_主片样片_底部字幕.mp4', 'work/op60_music_v3.json', -5.0),
    ('out/对比A_一段一页.mp4', 'work/op60_music_v3.json', 107.6),
    ('out/对比B_第一人称.mp4', 'work/op60_music_v3.json', 107.6),
    ('out/幻想波兰舞曲_开头样片.mp4', 'work/op61_music_v3.json', -5.0),
]
for f, mus, t0 in CASES:
    tmp = 'work/final/_a.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ac', '1', '-ar', str(SR), tmp], check=True)
    y, _ = librosa.load(tmp, sr=SR, mono=True)
    ons = librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP)
    tr = np.zeros(len(ons))
    for n in json.load(open(mus, encoding='utf-8'))['notes']:
        k = int((n['s'] - t0) * fps)
        if 0 <= k < len(tr):
            tr[k] += 1
    tr = np.convolve(tr, np.hanning(5), 'same')
    # 只算有音乐的部分
    a = int(max(0, -t0) * fps)
    b = min(len(ons), int((len(y) / SR - (12 if '主片' in f else 0)) * fps))
    o = ons[a:b] - ons[a:b].mean()
    t = tr[a:b] - tr[a:b].mean()
    lags = list(range(-40, 41))
    cs = [float(np.dot(np.roll(t, l), o) / (np.linalg.norm(t) * np.linalg.norm(o) + 1e-9)) for l in lags]
    i = int(np.argmax(cs))
    # 片头静音时长：前 8 秒内第一次明显出声
    rms = librosa.feature.rms(y=y[:SR * 8], hop_length=HOP)[0]
    first = next((j / fps for j, v in enumerate(rms) if v > 0.01), None)
    print(f"{os.path.basename(f)}：整段最优偏移 {lags[i] / fps * 1000:.0f} 毫秒，相关 {cs[i]:.2f}；开头第一次明显出声在 {first if first is None else round(first, 2)} 秒")
