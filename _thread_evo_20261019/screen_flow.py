"""Sequential experimental gates. No new prompts, models or acceptance thresholds.

Blind comparisons first; absolute floors only for survivors; diagnostics opt-in.
An early rejection uses an upper bound, never scores missing reviews as zero.
"""
import argparse
import json
import os
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

os.environ.setdefault('JV', '2')
import evo
import mg_schedule
import v6fix as V
import verdict

WORKS = ('op60', 'op61')
JUDGES = ('g6', 'g56')
DIMENSIONS = ('alone', 'lean', 'plain', 'cover')
ORDER = (('op60', 'g6'), ('op61', 'g56'), ('op60', 'g56'), ('op61', 'g6'))


def blind_ids(tag, base, acceptance=False):
    return [(f'v6b2_{w}_{j}_{tag}_vs{base}{suffix}', w, j)
            for suffix in (('', '_r2') if acceptance else ('',)) for w, j in ORDER]


def blind_state(tag, base, acceptance=False):
    rows, missing, invalid = [], [], []
    remaining_segments = 0
    for rid, w, j in blind_ids(tag, base, acceptance):
        expected = [s['sec'] for s in V.graph_of(w, tag)['segments']]
        d = V.parse(rid)
        if not d:
            missing.append(rid)
            remaining_segments += len(expected)
            continue
        flip = random.Random(rid).random() < .5
        new, old = ('X', 'Y') if flip else ('Y', 'X')
        sections = d.get('sections') or []
        reg = d.get(f'{new}_replacing_{old}_regress')
        if (len(sections) != len(expected) or {s.get('sec') for s in sections} != set(expected)
                or d.get('better') not in ('X', 'Y', '差不多') or reg not in ('是', '否')
                or any(s.get(k) not in ('X', 'Y', '差不多') for s in sections for k in DIMENSIONS)):
            invalid.append(rid)
            continue
        rows.append({'rid': rid, 'w': w, 'j': j, 'new_win': d['better'] == new,
                     'no_regress': reg == '否',
                     'net': {k: sum((s[k] == new) - (s[k] == old) for s in sections) for k in DIMENSIONS}})
    total, needed = (8, 6) if acceptance else (4, 3)
    wins = sum(r['new_win'] for r in rows)
    noreg = sum(r['no_regress'] for r in rows)
    sums = {k: sum(r['net'][k] for r in rows) for k in DIMENSIONS}
    impossible = []
    if wins + len(missing) < needed:
        impossible.append('remaining votes cannot reach the required new-version wins')
    for k in DIMENSIONS[:3]:
        if sums[k] + remaining_segments < 0:
            impossible.append(f'{k}: even every remaining segment winning leaves a negative net')
    if acceptance and noreg + len(missing) < 6:
        impossible.append('remaining votes cannot reach six non-regressions')
    # Malformed evidence cannot justify a pass or an early rejection.
    status = ('invalid' if invalid else 'reject' if impossible else 'pending' if missing else 'pass')
    return {'status': status, 'planned': total, 'complete': len(rows), 'wins': wins,
            'no_regress': noreg, 'net_sums': sums, 'missing': missing, 'invalid': invalid,
            'remaining_segment_upper_bound': remaining_segments, 'reasons': impossible, 'rows': rows}


def feedback_policy(state, floor_failures=(), attempt=1, hard_constraint_failure=False):
    """Routing heuristic only; never changes the acceptance gate."""
    if hard_constraint_failure:
        return 'archive_and_change_direction'
    if state['complete'] != 4 or state['invalid'] or state['missing']:
        return 'archive_and_change_direction' if state['status'] == 'reject' else 'await_complete_evidence'
    deficits = int(state['wins'] < 3) + sum(state['net_sums'][k] < 0 for k in DIMENSIONS[:3])
    deficits += bool(floor_failures)
    near = (state['wins'] >= 2 and deficits <= 1 and len(floor_failures) <= 1
            and all(state['net_sums'][k] >= -4 for k in DIMENSIONS[:3]))
    return 'return_to_author' if near and attempt < 3 else 'archive_and_change_direction'


def floor_state(tag, base, kind=None):
    missing, failures = [], []
    for w in WORKS:
        if kind in (None, 'coverage'):
            a = {j: verdict.cov_secs(w, j, tag) for j in JUDGES}
            b = {j: verdict.cov_secs(w, j, base) for j in JUDGES}
            for t, data in ((tag, a), (base, b)):
                missing += [f'cov2_{w}_{j}_{t}' for j in JUDGES if data[j] is None]
            if all(x is not None for x in (*a.values(), *b.values())):
                failures += [f'{w} {s} coverage drops >=2 for both judges' for s in b['g6']
                             if all(b[j].get(s, 0) - a[j].get(s, 0) >= 2 for j in JUDGES)]
        if kind in (None, 'alone'):
            a = {j: verdict.alone_count(w, j, tag) for j in JUDGES}
            b = {j: verdict.alone_count(w, j, base) for j in JUDGES}
            for t, data in ((tag, a), (base, b)):
                missing += [f'al2_{w}_{j}_{t}' for j in JUDGES if data[j] is None]
            if all(x is not None for x in (*a.values(), *b.values())):
                if all(b[j] - a[j] >= 1 for j in JUDGES):
                    failures.append(f'{w} fewer self-standing sections for both judges')
    return {'status': 'reject' if failures else 'pending' if missing else 'pass',
            'failures': failures, 'missing': sorted(set(missing))}


def submit(jobs, workers=2):
    def one(job):
        rid, message, model, stage = job
        if not evo.done(rid):
            evo.check_submission(model)
            answer = evo.call(rid, message, model=model, meta={'stage': stage, 'web': True})
            if not answer:
                raise RuntimeError(f'{rid}: no complete response; inspect existing receiver before retry')
        return rid
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, jobs))


def run_blind(tag, base, acceptance=False):
    for rid, w, j in blind_ids(tag, base, acceptance):
        state = blind_state(tag, base, acceptance)
        if state['status'] in ('reject', 'invalid', 'pass'):
            return state
        if rid not in state['missing']:
            continue
        flip = random.Random(rid).random() < .5
        a, b = V.graph_of(w, base), V.graph_of(w, tag)
        x, y = (b, a) if flip else (a, b)
        message = V.BLIND2.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2,
                                 X=V.view(x), Y=V.view(y), BEADS=V.beads(w))
        # Across candidates batch parallelism supplies concurrency. Within a candidate
        # inspect each completed vote before spending another request.
        submit([(rid, message, V.JUDGES[j], 'v6-blind')], 1)
    return blind_state(tag, base, acceptance)


def run_floor(tag, base, kind):
    import v6cov
    import v6alone
    state = floor_state(tag, base, kind)
    if state['status'] != 'pending':
        return state
    jobs = []
    for t in dict.fromkeys((base, tag)):
        for w in WORKS:
            for j in JUDGES:
                rid = f'{"cov2" if kind == "coverage" else "al2"}_{w}_{j}_{t}'
                if rid not in state['missing']:
                    continue
                if evo.done(rid):
                    raise ValueError(f'{rid}: malformed completed floor review; do not overwrite/retry silently')
                g = V.graph_of(w, t)
                if kind == 'coverage':
                    msg = v6cov.COV2.format(NAME=V.covjudge.NAME[w], WHAT=V.WHAT2,
                                           LINE=V.view(g), BEADS=V.beads(w))
                else:
                    msg = v6alone.ALONE2.format(NAME=V.covjudge.NAME[w], LINE=v6alone.line_ids(g))
                jobs.append((rid, msg, V.JUDGES[j], f'v6-{kind}'))
    # A baseline result is shared by every candidate. The batch prepares it once,
    # before survivor floors, rather than letting workers race on identical IDs.
    submit(jobs, 2)
    if kind == 'coverage':
        for t in dict.fromkeys((base, tag)):
            v6cov.summarize(t)
    else:
        for t in dict.fromkeys((base, tag)):
            summary = {}
            for w in WORKS:
                for j in JUDGES:
                    if verdict.alone_count(w, j, t) is None:
                        continue
                    d = V.parse(f'al2_{w}_{j}_{t}')
                    sections = d['sections']
                    summary[f'{w}_{j}'] = {
                        'self': dict(Counter(s['self'] for s in sections)),
                        'repeat': sum(s.get('repeat') == '有' for s in sections),
                        'label_mismatch': sum(s.get('label') == '对不上' for s in sections),
                        'trans': None, 'translation_diagnostic': '未测',
                        'weak_secs': [(s['sec'], s['self'], s.get('self_why', ''))
                                      for s in sections if s['self'] != '成立']}
            (V.OUT / f'alone2_{t}.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return floor_state(tag, base, kind)


def save_state(tag, base, data):
    publish_blind(tag, base, data['blind'])
    p = V.OUT / f'screen_flow_{tag}_vs{base}.json'
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return data


def publish_blind(tag, base, state):
    """Keep existing verdict/scoreboard/feedback readers compatible, without calls."""
    groups = {'': {}}
    if state['planned'] == 8:
        groups['_r2'] = {}
    for row in state['rows']:
        rid = row['rid']; d = V.parse(rid)
        new, old = ('X', 'Y') if random.Random(rid).random() < .5 else ('Y', 'X')
        cnt = {k: {'new': sum(s[k] == new for s in d['sections']),
                   'base': sum(s[k] == old for s in d['sections']),
                   '平': sum(s[k] == '差不多' for s in d['sections'])} for k in DIMENSIONS}
        lost = lambda label: [(s['sec'], item) for s in d['sections']
                               for item in s.get(f'lost_in_{label}', [])]
        suffix = '_r2' if rid.endswith('_r2') else ''
        groups[suffix][rid] = {'w': row['w'], 'j': row['j'],
                               'better': '新版' if d['better'] == new else base if d['better'] == old else '差不多',
                               'new_regress': d[f'{new}_replacing_{old}_regress'], 'cnt': cnt,
                               'lost_new': lost(new), 'lost_base': lost(old)}
    for suffix, summary in groups.items():
        path = V.OUT / f'blind2_{tag}_vs{base}{suffix}.json'
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
        # Complete original reasons remain available to I12, not a lossy summary.
        report = [f'# {tag} 对 {base}：已完成{len(summary)}份，缺测不计零', '']
        for rid in summary:
            report += [f'## {rid}', evo.output(rid), '']
        path.with_suffix('.md').write_text('\n'.join(report), encoding='utf-8')


def screen(tag, base='qurefs', acceptance=False, attempt=1):
    state = run_blind(tag, base, acceptance)
    data = {'tag': tag, 'base': base, 'blind': state, 'status': state['status']}
    if state['status'] != 'pass':
        data['next'] = feedback_policy(state, attempt=attempt)
        return save_state(tag, base, data)
    for kind in ('coverage', 'alone'):
        floor = run_floor(tag, base, kind)
        data[kind] = floor
        if floor['status'] != 'pass':
            data.update(status=floor['status'], next=feedback_policy(state, floor['failures'], attempt))
            return save_state(tag, base, data)
    data.update(status='acceptance_pass' if acceptance else 'quick_pass',
                next='I09_review' if acceptance else 'complete_pipeline_then_acceptance')
    return save_state(tag, base, data)


def configure():
    os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
    os.environ.setdefault('MG_GLOBAL', '4')
    os.environ.setdefault('MG_SLOTS', '4')
    os.environ.setdefault('MG_ATTEMPTS', '1')
    if not 1 <= int(os.environ['MG_GLOBAL']) <= 10:
        raise ValueError('MG_GLOBAL must be between 1 and 10')
    if V.JV != '2':
        raise ValueError('screen_flow requires JV=2; judge prompts and thresholds unchanged')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tag')
    p.add_argument('--base', default='qurefs')
    p.add_argument('--acceptance', action='store_true')
    p.add_argument('--inspect', action='store_true', help='read existing evidence only; no model calls')
    a = p.parse_args()
    configure()
    if a.inspect:
        d = blind_state(a.tag, a.base, a.acceptance)
        d['feedback'] = feedback_policy(d)
    else:
        if a.acceptance:
            # Must qualify at the four-vote gate before spending the second group.
            quick = screen(a.tag, a.base)
            if quick['status'] != 'quick_pass':
                print(json.dumps(quick, ensure_ascii=False, indent=2)); return
        d = screen(a.tag, a.base, a.acceptance)
    print(json.dumps(d, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
