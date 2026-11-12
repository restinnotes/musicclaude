"""Restore score-event identity from the source MIDI and its grace-run evidence.

Paths belong in configuration; the matching code does not inspect work titles.
The source and warped MIDI must have identical per-part/pitch multiplicities.
"""
import argparse
from collections import defaultdict
from pathlib import Path
import json
import pretty_midi
from music21.pitch import Pitch
from align_music import read, note_signature

ROOT = Path(__file__).resolve().parent

def build_events(seed, midi_path, evidence_path):
    pm = pretty_midi.PrettyMIDI(str(midi_path))
    by_seed, by_score = defaultdict(list), defaultdict(list)
    for i, n in enumerate(seed['notes']):
        by_seed[n['h'], n['p']].append(i)
    for h, ins in enumerate(pm.instruments):
        for n in ins.notes:
            by_score[h, n.pitch].append(n)
    if set(by_seed) != set(by_score) or any(len(by_seed[k]) != len(by_score[k]) for k in by_seed):
        raise ValueError('Seed/source MIDI identities differ; cannot restore event metadata')
    events = [None]*len(seed['notes'])
    for key, indices in by_seed.items():
        indices.sort(key=lambda i: (seed['notes'][i]['s'], seed['notes'][i]['e']))
        source = sorted(by_score[key], key=lambda n: (n.start, n.end))
        for idx, n in zip(indices, source):
            events[idx] = {'id': f'event-{idx}', 'score_s': float(n.start), 'score_e': float(n.end), 'grace_run': None}
    evidence = read(evidence_path)['selected']['validation']['score']
    raw_runs = evidence.get('grace_realization', {}).get('groups', [])
    downbeats = pm.get_downbeats()
    measure_numbers = evidence.get('downbeat_measure_numbers')
    runs, failures = [], []
    used = set()
    for raw in raw_runs:
        semantic_measure = raw['measure']
        if measure_numbers:
            matches = [j for j, n in enumerate(measure_numbers) if int(n) == semantic_measure]
            if not matches:
                failures.append({'measure': semantic_measure, 'reason': 'measure missing from numbering evidence'})
                continue
            bar = matches[0]
        else:
            bar = semantic_measure-1
        # Quarter lengths convert through the MIDI tempo map, rather than a
        # hardcoded seconds-per-quarter assumption.
        if bar >= len(downbeats):
            failures.append({'measure': semantic_measure, 'reason': 'bar outside MIDI'})
            continue
        tick0 = pm.time_to_tick(float(downbeats[bar]))
        indices = []
        for j, names in enumerate(raw['source_pitch_order']):
            offset = raw['first_offset_quarter_length'] + j*raw['step_quarter_length']
            expected = pm.tick_to_time(round(tick0+offset*pm.resolution))
            for name in names:
                pitch = Pitch(name).midi
                possible = [i for i, (n, ev) in enumerate(zip(seed['notes'], events)) if n['p'] == pitch and abs(ev['score_s']-expected) < .004 and i not in used and i not in indices]
                if len(possible) != 1:
                    indices = []
                    break
                indices.append(possible[0])
            if not indices:
                break
        if len(indices) != sum(len(x) for x in raw['source_pitch_order']):
            failures.append({'measure': semantic_measure, 'reason': 'ambiguous or missing MIDI event'})
            continue
        rid = f'grace-{len(runs)}'
        for i in indices:
            events[i]['grace_run'] = rid
        used.update(indices)
        runs.append({'id': rid, 'measure': semantic_measure, 'indices': indices})
    return {'seed_signature': note_signature(seed['notes']), 'source_midi': str(Path(midi_path).resolve()), 'evidence': str(Path(evidence_path).resolve()), 'events': events, 'runs': runs, 'unresolved_runs': failures}

def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--work', nargs='+', required=True)
    x = a.parse_args()
    cfg = read(ROOT/'input/event_sources.json')
    for work in x.work:
        c = cfg[work]
        out = build_events(read(ROOT/f'input/{work}_music_source.json'), c['source_midi'], c['score_evidence'])
        p = ROOT/f'input/{work}_events.json'
        p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
        print(work, len(out['events']), 'events;', len(out['runs']), 'grace runs;', out['unresolved_runs'])

if __name__ == '__main__': main()
