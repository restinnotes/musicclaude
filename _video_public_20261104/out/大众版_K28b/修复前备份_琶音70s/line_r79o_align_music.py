"""Pitch-aware, ordered audio attack refinement shared by every work.

The input is an approximately aligned music JSON, not an unaligned score.
No titles, measure numbers, hand numbers or passage times enter the algorithm.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import librosa
from scipy.ndimage import maximum_filter1d, gaussian_filter1d
from scipy.signal import find_peaks

SR, HOP = 22050, 256
FPS = SR / HOP
VERSION = 'score-events-anchors-v2'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def note_signature(notes):
    return hashlib.sha256(json.dumps([(n['h'], n['p'], n['s'], n['e']) for n in notes], separators=(',', ':')).encode()).hexdigest()

def features(audio, cache):
    p = Path(audio)
    key = hashlib.sha256(f'{p.resolve()}:{p.stat().st_size}:{p.stat().st_mtime_ns}:{SR}:{HOP}'.encode()).hexdigest()[:16]
    cache = Path(cache) / f'pitch_{key}.npz'
    if cache.exists():
        z = np.load(cache)
        return z['C'], z['attack'], z['env'], float(z['duration'])
    print(f'Analyzing audio: {p}', flush=True)
    y, _ = librosa.load(p, sr=SR, mono=True)
    C = np.abs(librosa.cqt(y, sr=SR, hop_length=HOP, fmin=librosa.midi_to_hz(21), n_bins=88)).astype(np.float32)
    # Local normalization preserves quiet high notes following loud chords.
    smooth = gaussian_filter1d(C, .65, axis=1)
    floor = np.maximum(np.max(smooth, axis=1, keepdims=True)*.001, 1e-6)
    log = np.log1p(smooth / floor)
    attack = np.maximum(0, log - np.concatenate([log[:, :1].repeat(3, axis=1), log[:, :-3]], axis=1))
    attack = gaussian_filter1d(attack, .65, axis=1)
    local_peak = maximum_filter1d(attack, size=round(FPS*4)|1, axis=1)
    attack /= np.maximum(local_peak, .08)
    env = librosa.feature.rms(y=y, hop_length=HOP)[0].astype(np.float32)
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(cache, C=C, attack=attack, env=env, duration=len(y)/SR)
    return C, attack, env, len(y)/SR

def groups_of(notes, tolerance=.012):
    groups = []
    for i in sorted(range(len(notes)), key=lambda i: (notes[i]['s'], notes[i]['p'])):
        n = notes[i]
        if not groups or n['s']-groups[-1]['s'] > tolerance:
            groups.append({'s': n['s'], 'idx': []})
        groups[-1]['idx'].append(i)
    return groups

def pitch_curve(attack, pitches):
    bins = np.array(sorted(set(p-21 for p in pitches if 21 <= p <= 108)))
    if not len(bins):
        return np.zeros(attack.shape[1])
    # Each fundamental votes once. Octave partials must not impersonate a note.
    return np.mean(attack[bins], axis=0)

def ordered_refine(notes, attack, radius=2.5):
    if radius <= 0 or not notes or attack.ndim != 2 or attack.shape[0] != 88 or attack.shape[1] == 0:
        raise ValueError('Need positive search radius, notes, and 88-bin audio features')
    if any(n['s'] < 0 or n['e'] <= n['s'] for n in notes):
        raise ValueError('Invalid input note interval')
    groups = groups_of(notes)
    times = np.array([g['s'] for g in groups])
    candidates, qualities = [], []
    for g in groups:
        curve = pitch_curve(attack, [notes[i]['p'] for i in g['idx']])
        lo = max(0, round((g['s']-radius)*FPS))
        hi = min(len(curve), round((g['s']+radius)*FPS)+1)
        peaks, _ = find_peaks(curve[lo:hi], distance=3, prominence=.04)
        ix = peaks+lo
        base = min(len(curve)-1, max(0, round(g['s']*FPS)))
        ix = np.unique(np.r_[ix, base])
        # Bound computation, while always retaining the original time.
        score = curve[ix] - .10*((ix/FPS-g['s'])/radius)**2
        best = ix[np.argsort(score)[-36:]]
        ix = np.unique(np.r_[best, base])
        candidates.append(ix/FPS)
        qualities.append(curve[ix])
    costs, parents = [], []
    for i, (ts, q) in enumerate(zip(candidates, qualities)):
        unary = -2*q + .20*((ts-times[i])/radius)**2
        if i == 0:
            costs.append(unary)
            parents.append(np.full(len(ts), -1, dtype=int))
            continue
        prev = candidates[i-1]
        delta = ts[:, None]-prev[None, :]
        expected = times[i]-times[i-1]
        # Smooth the *offset*, not the onset sequence. Strong pitch attacks may
        # still express rubato and acceleration without a median filter.
        transition = .35*np.minimum(((delta-expected)/max(.12, expected*.5))**2, 12)
        transition[delta < min(.018, expected*.45)] = np.inf
        total = transition + costs[-1][None, :]
        par = np.argmin(total, axis=1)
        costs.append(unary + total[np.arange(len(ts)), par])
        parents.append(par)
    if not costs or not np.isfinite(costs[-1]).any():
        raise ValueError('No ordered attack path; input onset groups are inconsistent')
    choice = int(np.argmin(costs[-1]))
    chosen, confidence = [], []
    for i in range(len(groups)-1, -1, -1):
        chosen.append(float(candidates[i][choice]))
        confidence.append(float(qualities[i][choice]))
        choice = int(parents[i][choice])
    chosen = chosen[::-1]
    confidence = confidence[::-1]
    out = copy.deepcopy(notes)
    rows = []
    for g, t, q in zip(groups, chosen, confidence):
        shift = t-g['s']
        for idx in g['idx']:
            n = out[idx]
            n['s'] = round(notes[idx]['s']+shift, 4)
            n['e'] = round(max(n['s']+.025, notes[idx]['e']+shift), 4)
        curve = pitch_curve(attack, [notes[k]['p'] for k in g['idx']])
        at = min(len(curve)-1, max(0, round(g['s']*FPS)))
        rows.append({'before': g['s'], 'after': round(t, 4), 'pitches': [notes[k]['p'] for k in g['idx']], 'attack_support_before': round(float(curve[at]), 3), 'attack_support': round(q, 3)})
    out.sort(key=lambda n: (n['s'], n['p']))
    return out, rows

def summarize(rows):
    if not rows:
        return {'groups': 0}
    shifts = np.array([abs(r['after']-r['before']) for r in rows])
    support = np.array([r['attack_support'] for r in rows])
    return {'groups': len(rows), 'median_shift_ms': round(float(np.median(shifts))*1000), 'p90_shift_ms': round(float(np.percentile(shifts, 90))*1000), 'low_support_groups': int(np.sum(support < .35)), 'median_attack_support_before': round(float(np.median([r['attack_support_before'] for r in rows])), 3), 'median_attack_support': round(float(np.median(support)), 3)}

def align_file(music, audio, output, report, cache, radius=2.5, events=None):
    m = read(music)
    C, attack, env, duration = features(audio, cache)
    if abs(duration-m['dur']) > .2:
        raise ValueError(f'Audio/music duration mismatch: {duration:.3f} vs {m["dur"]:.3f}')
    event_qa = None
    if events:
        from event_alignment import align_events
        m['notes'], rows, event_qa = align_events(m['notes'], read(events), C, attack, radius)
    else:
        m['notes'], rows = ordered_refine(m['notes'], attack, radius)
    qa = {'version': VERSION, 'input': str(Path(music).resolve()), 'audio': str(Path(audio).resolve()), 'parameters': {'radius_seconds': radius, 'sample_rate': SR, 'hop': HOP}, 'summary': summarize(rows), 'opening_30s': summarize([r for r in rows if r['before'] < 30]), 'groups': rows}
    qa['status'] = 'REVIEW_REQUIRED'
    qa['event_alignment'] = event_qa
    qa['row_unit'] = 'score_event' if event_qa else 'onset_group'
    qa['limitations'] = ['Attack support is a fitting score, not measured timing error.', 'Pitch identities and measure/text timing are inherited from the input.', 'Score event metadata separates chords and grace notes; it does not establish whether the notated pitches match the performance.']
    qa['input_anomalies'] = input_anomalies(read(music)['notes'])
    m['alignment'] = {k: v for k, v in qa.items() if k != 'groups'}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(m, ensure_ascii=False), encoding='utf-8')
    Path(report).parent.mkdir(parents=True, exist_ok=True)
    Path(report).write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(qa['summary'], ensure_ascii=False), flush=True)
    print(output, flush=True)

def input_anomalies(notes):
    previous = {}
    overlaps = []
    for n in sorted(notes, key=lambda n: n['s']):
        key = (n['h'], n['p'])
        p = previous.get(key)
        if p and p['e'] > n['s']+.04:
            overlaps.append({'pitch': n['p'], 'part': n['h'], 'previous_start': p['s'], 'previous_end': p['e'], 'start': n['s']})
        if p is None or n['e'] > p['e']:
            previous[key] = n
    return {'same_pitch_overlaps': len(overlaps), 'examples': overlaps[:20]}

def main():
    root = Path(__file__).resolve().parent
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--work', nargs='+', choices=['op60', 'op61'])
    a.add_argument('--music'); a.add_argument('--audio'); a.add_argument('--output')
    a.add_argument('--report'); a.add_argument('--radius', type=float, default=2.5); a.add_argument('--events', help='Score-event manifest from prepare_events.py')
    a.add_argument('--cache', default=str(root/'cache'))
    x = a.parse_args()
    if x.work:
        for work in x.work:
            ep = root/f'input/{work}_events.json'
            align_file(root/f'input/{work}_music_source.json', read(root/f'plans/{work}_points.json')['audio'], root/f'input/{work}_music_aligned.json', root/f'qa/{work}_alignment.json', x.cache, x.radius, ep if ep.exists() else None)
    else:
        if not all([x.music, x.audio, x.output, x.report]):
            a.error('Use --work, or --music --audio --output --report')
        align_file(x.music, x.audio, x.output, x.report, x.cache, x.radius, x.events)

if __name__ == '__main__': main()
