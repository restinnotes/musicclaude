"""Hierarchical, score-event-aware attack alignment (no work-specific rules)."""
from collections import defaultdict
from copy import deepcopy
import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.signal import find_peaks
from align_music import FPS, pitch_curve, ordered_refine, note_signature

def solve_chain(candidates, quality, predicted, scale, continuity=.06):
    costs, parents = [], []
    for i, (ts, q) in enumerate(zip(candidates, quality)):
        unary = -4*q + .35*((ts-predicted[i])/max(.1, scale[i]))**2
        if not i:
            costs.append(unary); parents.append(None)
            continue
        dt = ts[:, None]-candidates[i-1][None, :]
        expected = predicted[i]-predicted[i-1]
        trans = continuity*np.minimum(((dt-expected)/max(.2, expected*.5))**2, 5)
        trans[dt < min(.018, max(.0001, expected*.4))] = np.inf
        total = trans+costs[-1][None, :]
        p = np.argmin(total, axis=1)
        parents.append(p); costs.append(unary+total[np.arange(len(ts)), p])
    if not costs or not np.isfinite(costs[-1]).any():
        raise ValueError('No monotone event alignment path')
    idx = int(np.argmin(costs[-1])); chosen = []
    for i in range(len(costs)-1, -1, -1):
        chosen.append(float(candidates[i][idx]))
        if i: idx = int(parents[i][idx])
    return np.array(chosen[::-1])

def candidates_for(curve, lo, hi, predicted, count=80):
    a = max(0, int(lo*FPS)); b = min(len(curve), int(hi*FPS)+1)
    if b <= a:
        raise ValueError('Empty event search interval')
    peaks, _ = find_peaks(curve[a:b], distance=3, prominence=.015)
    ix = peaks+a
    base = min(b-1, max(a, round(predicted*FPS)))
    ix = np.unique(np.r_[ix, base])
    best = np.argsort(curve[ix]-.025*((ix/FPS-predicted)/max(.1, hi-lo))**2)[-count:]
    ix = np.unique(np.r_[ix[best], base])
    ts = np.unique(np.r_[ix/FPS, np.clip(predicted, max(0, lo), min(hi, (len(curve)-1)/FPS))])
    return ts, curve[np.clip(np.rint(ts*FPS).astype(int), 0, len(curve)-1)]

def interpolate_extrapolate(values, xs, ys):
    values = np.asarray(values)
    result = np.interp(values, xs, ys)
    left = ys[0]+(values-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
    right = ys[-1]+(values-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
    return np.where(values < xs[0], left, np.where(values > xs[-1], right, result))

def align_events(notes, metadata, C, attack, radius=2.5):
    ev = deepcopy(metadata['events'])
    if len(ev) != len(notes):
        raise ValueError('Event manifest does not match music input')
    if metadata.get('seed_signature') and metadata['seed_signature'] != note_signature(notes):
        raise ValueError('Event manifest belongs to different seed notes; regenerate it')
    # Small ornaments are ordinary local events, not free cadenzas requiring
    # a wide chord search. Keep their source timing prior and event ordering.
    runs = [r for r in metadata['runs'] if len(r['indices']) >= 8]
    free_ids = {r['id'] for r in runs}
    for e in ev:
        if e['grace_run'] not in free_ids: e['grace_run'] = None
    if not runs:
        out, rows = ordered_refine(notes, attack, radius)
        return out, rows, {'method': 'local-no-free-grace-runs', 'anchors': [], 'runs': [], 'unresolved_runs': metadata['unresolved_runs']}
    # A quiet pitch needs an actual local energy rise, not just a normalized
    # noise transient. This makes multiple chord fundamentals vote together.
    level = C/np.maximum(maximum_filter1d(C, size=round(6*FPS)|1, axis=1), 1e-6)
    evidence = attack*np.sqrt(np.clip(level, 0, 1))
    # Require a real broadband attack for chord anchors. An arpeggio note's
    # upper partials can resemble several members of a different chord.
    flux = np.sum(np.maximum(0, C-np.concatenate([C[:, :1].repeat(4, axis=1), C[:, :-4]], axis=1)), axis=0)
    flux = maximum_filter1d(flux, size=7)
    broadband = flux/np.maximum(maximum_filter1d(flux, size=round(30*FPS)|1), 1e-6)
    anchor_evidence = maximum_filter1d(evidence, size=15, axis=1)*np.sqrt(broadband)[None, :]
    regular = defaultdict(list)
    for i, e in enumerate(ev):
        if e['grace_run'] is None:
            regular[round(e['score_s'], 4)].append(i)
    anchors = [(s, ids) for s, ids in sorted(regular.items()) if len(set(notes[i]['p'] for i in ids)) >= 3]
    if len(anchors) < 2:
        out, rows = ordered_refine(notes, attack, radius)
        return out, rows, {'method': 'local-fallback', 'reason': 'fewer than two chord anchors'}
    wide = set()
    repair_intervals = []
    for run in runs:
        end = max(ev[i]['score_s'] for i in run['indices'])
        after = [j for j, (s, _) in enumerate(anchors) if s > end+.005]
        if after: wide.add(after[0])
        begin = min(ev[i]['score_s'] for i in run['indices'])
        before = [j for j, (s, _) in enumerate(anchors) if s <= begin+.005]
        if before: wide.add(before[-1])
        if before and after:
            repair_intervals.append((anchors[before[-1]][0], anchors[min(after[0]+1, len(anchors)-1)][0]))
    cand, qs, prior, scales = [], [], [], []
    for j, (s, ids) in enumerate(anchors):
        t = float(np.median([notes[i]['s'] for i in ids]))
        window = max(radius, 15.) if j in wide else radius
        bins = np.array(sorted(set(notes[i]['p']-21 for i in ids)))
        votes = anchor_evidence[bins]
        curve = .4*np.mean(votes, axis=0)+.6*np.percentile(votes, 25, axis=0)
        ts, q = candidates_for(curve, t-window, t+window, t)
        cand.append(ts); qs.append(q); prior.append(t); scales.append(window)
    target = solve_chain(cand, qs, np.array(prior), scales)
    score_t = np.array([s for s, _ in anchors])
    anchor_rows = [{'score': s, 'before': round(t, 4), 'after': round(float(at), 4), 'pitches': [notes[i]['p'] for i in ids], 'wide_search': j in wide} for j, ((s, ids), t, at) in enumerate(zip(anchors, prior, target))]
    # Local regular events use score position between the recovered anchors.
    # This repairs a distorted whole interval, including single melody notes.
    out = deepcopy(notes)
    regular_groups = sorted(regular.items())
    fixed = {s: t for (s, _), t in zip(anchors, target)}
    rc, rq, rp, rs = [], [], [], []
    for s, ids in regular_groups:
        t = max(0., float(interpolate_extrapolate(s, score_t, target)))
        if s in fixed:
            ts = np.array([fixed[s]])
            q = np.array([float(pitch_curve(evidence, [notes[i]['p'] for i in ids])[min(evidence.shape[1]-1, round(t*FPS))])])
        else:
            curve = pitch_curve(evidence, [notes[i]['p'] for i in ids])
            ts, q = candidates_for(curve, t-radius, t+radius, t)
        rc.append(ts); rq.append(q); rp.append(t); rs.append(radius)
    regular_t = solve_chain(rc, rq, np.array(rp), rs, continuity=.12)
    aligned = {}
    for (_, ids), t in zip(regular_groups, regular_t):
        for i in ids: aligned[i] = float(t)
    run_rows = []
    for run in runs:
        ids = run['indices']
        first, last = min(ev[i]['score_s'] for i in ids), max(ev[i]['score_s'] for i in ids)
        preceding = [(s, t) for (s, _), t in zip(regular_groups, regular_t) if s <= first+.005]
        following = [(s, t) for (s, _), t in zip(regular_groups, regular_t) if s > last+.005]
        if not preceding or not following:
            raise ValueError('Grace run lacks regular event boundaries')
        lo, hi = float(preceding[-1][1]), float(following[0][1])
        if hi <= lo:
            raise ValueError(f'Nonpositive grace span: {run["id"]} {lo} {hi}')
        margin = min(.03, (hi-lo)/(len(ids)+2)*.25)
        baseline = np.array([notes[i]['s'] for i in ids])
        span_ratio = (baseline[-1]-baseline[0])/(hi-lo)
        # A run can cover the full interval while most of its notes are still
        # crushed into clusters at either end. Check the internal spacing,
        # normalized by score spacing, before trusting its timing prior.
        score_steps = np.diff([ev[i]['score_s'] for i in ids])
        baseline_steps = np.diff(baseline)
        relative_tempo = baseline_steps / np.maximum(score_steps, 1e-6)
        average_tempo = (baseline[-1]-baseline[0]) / max(last-first, 1e-6)
        spacing_intact = (np.all(baseline_steps > 0)
                          and np.percentile(relative_tempo, 25) >= .25*average_tempo
                          and np.max(relative_tempo) <= 4*average_tempo)
        intact = (.5 <= span_ratio <= 1 and lo < baseline[0] < baseline[-1] < hi
                  and spacing_intact)
        priors = baseline if intact else np.linspace(lo, hi, len(ids)+2)[1:-1]
        gc, gq = [], []
        for i, t in zip(ids, priors):
            curve = pitch_curve(evidence, [notes[i]['p']])
            ts, q = candidates_for(curve, lo+margin, hi-margin, t, count=100)
            gc.append(ts); gq.append(q)
        prior_scale = max(.2, (hi-lo)*(.1 if intact else .5))
        gt = solve_chain(gc, gq, priors, [prior_scale]*len(ids), continuity=.35)
        if intact:
            support = np.array([evidence[notes[i]['p']-21, min(evidence.shape[1]-1, round(t*FPS))] for i, t in zip(ids, gt)])
            strong = np.flatnonzero(support >= .35)
            if len(strong) >= 2:
                weak = np.flatnonzero(support < .35)
                fallback = baseline[weak]+np.interp(weak, strong, gt[strong]-baseline[strong])
                for k, t in zip(weak, fallback):
                    lower = gt[k-1]+.005 if k else lo+.005
                    upper = gt[k+1]-.005 if k+1 < len(gt) else hi-.005
                    if lower < upper: gt[k] = np.clip(t, lower, upper)
        for k, (i, t) in enumerate(zip(ids, gt)):
            aligned[i] = float(t)
            next_t = gt[k+1] if k+1 < len(gt) else min(hi, t+np.median(np.diff(gt)))
            out[i]['e'] = round(float(t+.82*(next_t-t)), 4)
        run_rows.append({'id': run['id'], 'measure': run['measure'], 'boundary': [lo, hi], 'intact_baseline': bool(intact), 'before': [notes[i]['s'] for i in ids], 'after': [round(float(t), 4) for t in gt], 'pitches': [notes[i]['p'] for i in ids]})
    # Recovery is needed around written free runs. Preserve the existing local
    # refinement in ordinary passages rather than reinterpreting their tempo
    # from a sparse chord map.
    local_seed = [dict(n, _seed_index=i) for i, n in enumerate(notes)]
    local_out, _ = ordered_refine(local_seed, attack, radius)
    local_by_id = {n.pop('_seed_index'): n for n in local_out}
    rows = []
    for i, (n, e) in enumerate(zip(notes, ev)):
        t = aligned[i]
        out[i]['s'] = round(t, 4)
        if e['grace_run'] is None:
            # Warp release through the chord map as well, rather than carrying
            # a badly stretched source duration into the new performance.
            end = float(interpolate_extrapolate(e['score_e'], score_t, target))
            out[i]['e'] = round(max(t+.025, min(t+19., end)), 4)
            if not any(lo-.0001 <= e['score_s'] <= hi+.0001 for lo, hi in repair_intervals):
                out[i] = local_by_id[i]
                t = out[i]['s']
                if any(lo-.0001 <= e['score_e'] <= hi+.0001 for lo, hi in repair_intervals):
                    # A note before a recovered interval may release at its
                    # first chord. Carry that boundary into the release too.
                    out[i]['e'] = round(max(t+.025, min(t+19., end)), 4)
        curve = evidence[n['p']-21]
        b = min(len(curve)-1, round(n['s']*FPS)); a = min(len(curve)-1, round(t*FPS))
        rows.append({'event_id': e['id'], 'before': n['s'], 'after': out[i]['s'], 'pitches': [n['p']], 'grace_run': e['grace_run'], 'attack_support_before': round(float(curve[b]), 3), 'attack_support': round(float(curve[a]), 3)})
    out.sort(key=lambda n: (n['s'], n['p']))
    return out, rows, {'method': 'score-events-chord-anchors-bounded-grace', 'anchors': anchor_rows, 'runs': run_rows, 'repair_score_intervals': repair_intervals, 'unresolved_runs': metadata['unresolved_runs']}
