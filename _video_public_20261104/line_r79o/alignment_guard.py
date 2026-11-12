"""Conservative release checks, not a guarantee of perceptual synchronization.

No work names, measure numbers, or performance timestamps enter the checks.
Certificates bind the tested note data to the exact recording bytes.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

VERSION = 'alignment-release-checks-v1'


def notes_digest(notes):
    return hashlib.sha256(json.dumps(notes, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def audio_digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def assess(music, qa, audio):
    issues = []
    def flag(code, detail, window=None):
        issues.append(dict(code=code, detail=detail, window=window))
    notes = music['notes']
    if not notes or any(not all(math.isfinite(n[k]) for k in ('s', 'e', 'p'))
                        or n['s'] < 0 or n['e'] <= n['s']
                        or n['s'] >= music['dur'] or n['e'] > music['dur']+.1
                        for n in notes):
        flag('invalid_note_intervals', 'Empty, invalid, or out-of-recording note data')
    rows = qa.get('groups') or []
    actual, reported = defaultdict(list), defaultdict(list)
    for n in notes: actual[n['p']].append(n['s'])
    for row in rows:
        for pitch in row['pitches']: reported[pitch].append(row['after'])
    # Onset-group reports summarize notes grouped within the aligner's 12 ms
    # tolerance; the individual offsets are preserved in the output notes.
    tolerance = .000051 if rows and all('event_id' in row for row in rows) else .0121
    if (set(actual) != set(reported)
            or any(len(actual[p]) != len(reported[p])
                   or any(abs(a-b) > tolerance for a, b in zip(sorted(actual[p]), sorted(reported[p])))
                   for p in actual)):
        flag('report_note_mismatch', 'Alignment report does not describe these output notes')
    events = qa.get('event_alignment')
    if events is None:
        flag('missing_score_events', 'Local search alone cannot validate free score passages')
    else:
        if events.get('unresolved_runs'):
            flag('unresolved_score_events', events['unresolved_runs'])
        for run in events.get('runs', []):
            ts = run['after']; lo, hi = run['boundary']; window = [lo, hi]
            if (not ts or len(ts) != len(run['pitches']) or hi <= lo
                    or any(not math.isfinite(t) or not lo < t < hi for t in ts)
                    or any(b <= a for a, b in zip(ts, ts[1:]))):
                flag('invalid_free_run', run['id'], window)
                continue
            gaps = [b-a for a, b in zip(ts, ts[1:])]
            support = [r['attack_support'] for r in rows if r.get('grace_run') == run['id']]
            if len(support) != len(ts) or mean(support) < .25:
                flag('weak_free_run_audio_evidence', run['id'], window)
            # A genuinely fast, well-supported run is allowed. Detect clusters
            # separated by huge gaps, rather than imposing a minimum speed.
            if len(gaps) >= 7:
                typical = (ts[-1]-ts[0])/len(gaps)
                lower = sorted(gaps)[len(gaps)//4]
                if lower < .25*typical and max(gaps) > 4*typical:
                    flag('internally_compressed_free_run', run['id'], window)
    return dict(version=VERSION, status='REVIEW_REQUIRED' if issues else 'AUTOMATED_CHECKS_PASSED',
                issues=issues, notes_sha256=notes_digest(notes), audio_sha256=audio_digest(audio),
                limitation='Passing these checks is not a measured timing-error guarantee; independent recording benchmarks remain necessary.')


def require_renderable(music, audio):
    check = (music.get('alignment') or {}).get('automatic_validation') or {}
    if check.get('version') != VERSION or check.get('status') != 'AUTOMATED_CHECKS_PASSED':
        issues = check.get('issues') or [{'code': 'missing_current_validation'}]
        raise ValueError('Alignment requires review before export: ' + json.dumps(issues, ensure_ascii=False))
    if check.get('notes_sha256') != notes_digest(music['notes']):
        raise ValueError('Aligned note data changed after validation; realign before export')
    if check.get('audio_sha256') != audio_digest(audio):
        raise ValueError('Recording changed after validation; realign this recording before export')


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--music', required=True); a.add_argument('--audio', required=True)
    a.add_argument('--qa', required=True); a.add_argument('--out', required=True)
    x = a.parse_args()
    def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
    report = assess(read(x.music), read(x.qa), x.audio)
    Path(x.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # Auditing cannot silently promote an existing candidate for release.
    return 2 if report['issues'] else 0


if __name__ == '__main__': raise SystemExit(main())
