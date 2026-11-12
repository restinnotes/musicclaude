"""核对：片子音频和原音频是否 1:1，音符时间和音频起音是否对得上。python qa/sync_check.py WORK CLIP START"""
import json, subprocess, sys
import numpy as np
w, clip, start = sys.argv[1], sys.argv[2], float(sys.argv[3]); SR = 8000
def pcm(path, ss=None, t=None):
    cmd = ['ffmpeg', '-v', 'error', *(['-ss', str(ss)] if ss is not None else []), '-i', path, *(['-t', str(t)] if t else []), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, dtype=np.float32)
a = json.load(open(f'plans/{w}_points.json', encoding='utf-8'))['audio']; m = json.load(open(f'input/{w}_music.json', encoding='utf-8'))
c = pcm(clip); d = len(c)/SR; s = pcm(a, start, d)
n = min(len(c), len(s)); print('片长', round(d, 2), '片和原音频的相关', round(float(np.corrcoef(c[:n], s[:n])[0, 1]), 4))
for r in (.9, .95, 1.05, 1.1):
    x = np.interp(np.arange(0, n, r), np.arange(n), s[:n])[:n]; k = min(len(x), n); print('  假设变速', r, round(float(np.corrcoef(c[:k], x[:k])[0, 1]), 4))
HOP = 80
def flux(x):
    e = np.array([np.sqrt(np.mean(x[i:i+HOP*2]**2)) for i in range(0, len(x)-HOP*2, HOP)]); f = np.maximum(0, np.diff(np.log(e+1e-3))); return f-f.mean()
f = flux(s)
ons = np.array([x['s'] for x in m['notes'] if start <= x['s'] < start+d])-start
print('音符数', len(ons), '每秒', round(len(ons)/d, 1))
best = []
for sc in np.arange(.9, 1.101, .01):
    for lag in np.arange(-1, 1.01, .02):
        idx = ((ons*sc+lag)*SR/HOP).astype(int); idx = idx[(idx >= 0) & (idx < len(f))]
        best.append((float(f[idx].mean()), round(float(sc), 2), round(float(lag), 2)))
best.sort(reverse=True); print('音符和起音最吻合：', best[:3])
idx = (ons*SR/HOP).astype(int); idx = idx[idx < len(f)]; print('不拉伸不偏移的吻合度', round(float(f[idx].mean()), 4))
