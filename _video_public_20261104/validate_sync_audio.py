"""Independent STFT attack cross-check, not a human timing ground truth.

Reads candidate times but does not modify them. Unlike fitting, uses a linear
FFT bank and short windows rather than constant-Q pitch analysis.
"""
import argparse
import json
from pathlib import Path
import subprocess
import librosa
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from align_music import read

ROOT = Path(__file__).resolve().parent
SR, HOP = 22050, 128

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', required=True); p.add_argument('--seconds', type=float, help='Optional excerpt length; default checks the entire recording')
    x = p.parse_args()
    qa = read(ROOT/f'qa/{x.work}_alignment.json')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', qa['audio'], *(['-t', str(x.seconds)] if x.seconds is not None else []), '-ac', '1', '-ar', str(SR), '-f', 'f32le', 'pipe:1'], check=True, capture_output=True).stdout
    y = np.frombuffer(raw, dtype='<f4')
    x.seconds = len(y)/SR
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=HOP))
    diff = np.maximum(0, S-np.concatenate([S[:, :1].repeat(3, axis=1), S[:, :-3]], axis=1))
    freq = librosa.fft_frequencies(sr=SR, n_fft=2048)
    times = np.arange(S.shape[1])*HOP/SR
    total = gaussian_filter1d(diff.sum(axis=0), 1)
    def near(curve, t):
        peaks, _ = find_peaks(curve, distance=3)
        peaks = peaks[np.abs(times[peaks]-t) <= .15]
        if not len(peaks):
            return {'matched': False}
        k = int(peaks[np.argmin(np.abs(times[peaks]-t))])
        return {'matched': True, 'reference_time': round(float(times[k]), 4), 'delta_ms': round(float((t-times[k])*1000), 1)}
    anchors = []
    runs = []
    detail = qa.get('event_alignment') or {}
    for a in detail.get('anchors', []):
        if a['after'] >= x.seconds: continue
        anchors.append(dict(candidate=a['after'], pitches=a['pitches'], **near(total, a['after'])))
    for run in detail.get('runs', []):
        if run['after'][0] >= x.seconds: continue
        notes = []
        for pitch, t in zip(run['pitches'], run['after']):
            # The short FFT resolves middle/high fundamentals. Low bass
            # frequencies require a longer window and are left unscored.
            if pitch < 60 or t >= x.seconds: continue
            f = librosa.midi_to_hz(pitch)
            mask = (freq >= f*2**(-.45/12)) & (freq <= f*2**(.45/12))
            if not np.any(mask): continue
            curve = gaussian_filter1d(diff[mask].sum(axis=0), .7)
            notes.append(dict(pitch=pitch, candidate=t, **near(curve, t)))
        errors = [abs(n['delta_ms']) for n in notes if n['matched']]
        runs.append({'id': run['id'], 'measure': run['measure'], 'notes': notes, 'eligible_notes': len(notes), 'matched': len(errors), 'median_absolute_difference_ms': round(float(np.median(errors)), 1) if errors else None, 'max_absolute_difference_ms': round(float(max(errors)), 1) if errors else None})
    out = {'method': 'independent-linear-STFT-attack-cross-check', 'limitation': 'Nearest spectral attack is corroborating evidence, not human annotated timing ground truth; no low-bass error estimate.', 'seconds': x.seconds, 'anchors': anchors, 'runs': runs}
    path = ROOT/f'qa/{x.work}_stft_crosscheck_v2.json'
    path.write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(path)
    print('anchors', anchors[:6])
    print('runs', [{k: v for k, v in r.items() if k != 'notes'} for r in runs])

if __name__ == '__main__': main()
