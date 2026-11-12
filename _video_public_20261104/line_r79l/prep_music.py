"""从“已对齐录音”的 MIDI、小节表和录音生成画面用的音乐数据，并检查对齐。作品无关。
python prep_music.py op52 --midi 路径 --bars 小节表.json --audio 录音 [--title ..] [--performer ..]
产物：input/{work}_music.json，plans/{work}_points.json（只含录音和曲名），qa/{work}_music_check.json
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
import librosa, numpy as np, pretty_midi
ROOT = Path(__file__).resolve().parent


def main():
    a = argparse.ArgumentParser(); a.add_argument('work'); a.add_argument('--midi', required=True); a.add_argument('--bars', required=True); a.add_argument('--audio', required=True); a.add_argument('--title', default=''); a.add_argument('--performer', default='')
    x = a.parse_args(); sys.stdout.reconfigure(encoding='utf-8')
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td)/'a.wav'; subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', x.audio, '-ac', '1', '-ar', '22050', str(wav)], check=True)
        y, sr = librosa.load(str(wav), sr=22050, mono=True)
    pm = pretty_midi.PrettyMIDI(x.midi); al = {int(k): float(v) for k, v in json.load(open(x.bars, encoding='utf-8')).items()}
    hop = 512; fps = sr/hop
    C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop, fmin=librosa.midi_to_hz(21), n_bins=88, bins_per_octave=12)); env = librosa.feature.rms(y=y, hop_length=hop)[0]; Cn = C/(np.percentile(C, 99.5)+1e-9)
    # 哪个声部是右手：平均音高高的算右手。
    ins = [i for i in pm.instruments if i.notes]; order = sorted(ins, key=lambda i: np.mean([n.pitch for n in i.notes])); notes = []
    for rank, i in enumerate(order):
        h = 1 if rank == len(order)-1 and len(order) > 1 else 0
        for n in i.notes:
            i0 = int(n.start*fps); i1 = max(i0+2, int((n.start+.15)*fps)); b = min(87, max(0, n.pitch-21))
            notes.append(dict(s=round(n.start, 3), e=round(n.end, 3), p=n.pitch, h=h, en=float(np.mean(Cn[b, i0:i1])) if i0 < C.shape[1] else 0, g=float(np.mean(env[i0:i1])) if i0 < len(env) else 0))
    if len(order) == 1:
        for n in notes: n['h'] = 1 if n['p'] >= 60 else 0
    notes.sort(key=lambda n: (n['s'], n['p']))
    ens = np.clip(np.array([n['en'] for n in notes])/np.percentile([n['en'] for n in notes], 97), 0, 1)**.6; gs = np.clip(np.array([n['g'] for n in notes])/np.percentile([n['g'] for n in notes], 98), 0, 1)**.7
    for n, p, q in zip(notes, ens, gs): n['en'] = round(float(.55*p+.45*q), 3); n.pop('g'); n['sky'] = False
    rh = sorted([n for n in notes if n['h'] == 1], key=lambda n: n['s']); i = 0
    while i < len(rh):
        j = i
        while j+1 < len(rh) and rh[j+1]['s']-rh[i]['s'] < .045: j += 1
        max(rh[i:j+1], key=lambda n: n['p'])['sky'] = True; i = j+1
    # 对齐检查：每 20 秒一窗，MIDI 起音和录音起音强度做相关，看最优偏移。
    ons = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop); tr = np.zeros(len(ons))
    for n in notes:
        k = int(n['s']*fps)
        if 0 <= k < len(tr): tr[k] += 1
    tr = np.convolve(tr, np.hanning(5), 'same'); W = int(20*fps); rows = []
    for s in range(0, len(ons)-W, W):
        o = ons[s:s+W]-ons[s:s+W].mean(); t = tr[s:s+W]-tr[s:s+W].mean()
        if o.std() == 0 or t.std() == 0: continue
        lags = list(range(-16, 17)); cs = [float(np.dot(np.roll(t, l), o)/(np.linalg.norm(t)*np.linalg.norm(o)+1e-9)) for l in lags]; b = int(np.argmax(cs)); rows.append({'t': round(s/fps), 'off_ms': round(lags[b]/fps*1000), 'r': round(cs[b], 2)})
    dur = len(y)/sr; step = int(.1*fps); envs = [round(float(np.mean(env[i:i+step])/(np.percentile(env, 98)+1e-9)), 3) for i in range(0, len(env), step)]
    bars = sorted((k, v) for k, v in al.items())
    json.dump(dict(notes=notes, bars=bars, env=envs, dur=dur), open(ROOT/f'input/{x.work}_music.json', 'w', encoding='utf-8'))
    json.dump({'work': x.work, 'title': x.title, 'performer': x.performer, 'audio': x.audio, 'sections': []}, open(ROOT/f'plans/{x.work}_points.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    med = float(np.median([abs(r['off_ms']) for r in rows])); bad = [r for r in rows if abs(r['off_ms']) > 200 or r['r'] < .15]
    json.dump({'dur': dur, 'notes': len(notes), 'bars': len(bars), 'last_note_end': max(n['e'] for n in notes), 'median_off_ms': med, 'rows': rows, 'bad': bad}, open(ROOT/f'qa/{x.work}_music_check.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(x.work, '时长', round(dur, 1), '音符', len(notes), '小节', len(bars), '最后音结束', round(max(n['e'] for n in notes), 1), '偏移中位数', med, 'ms，窗口', len(rows), '可疑', len(bad)); print('中位相关', np.median([r['r'] for r in rows]))
    print('可疑窗口', bad[:20])


if __name__ == '__main__': main()
