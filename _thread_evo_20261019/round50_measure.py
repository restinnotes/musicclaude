"""Frozen, collect-only requests using existing review and labeling prompts."""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault('JV', '2')
import experiment_batch as B
import round37_fair as FAIR
import round45_label as LABEL
import e2e_open as OPEN


def jobs(action, tag, base):
    if action == 'open':
        for w in B.F.WORKS:
            for j in ('g6', 'g56', 'gem'):
                for k in ((1,) if j == 'gem' else (1, 2)):
                    msg = OPEN.P.format(LINE=B.V.view(B.V.graph_of(w, tag), center=False), BEADS=OPEN.covjudge.bead_text(w))
                    yield f'eo2_{w}_{tag}_{j}_r{k}', msg + ('\n' if k == 2 else ''), j
    elif action == 'labels':
        for w in B.F.WORKS:
            g = B.V.graph_of(w, tag)
            line = '\n'.join(f"{s['sec']}：" + ' '.join(i['text'] for i in s['items']) for s in g['segments'])
            yield f'sc{tag}_{w}_A11', LABEL.PROMPT.format(CENTER=g['center'], LINE=line), 'g6'
    elif action == 'fair':
        for w in B.F.WORKS:
            for j in B.F.JUDGES:
                for seat in ('newX', 'newY'):
                    a, b = B.V.graph_of(w, base), B.V.graph_of(w, tag)
                    x, y = (b, a) if seat == 'newX' else (a, b)
                    yield FAIR.rid_of(w, j, tag, base, seat), B.V.BLIND2.format(NAME=B.V.covjudge.NAME[w], WHAT=B.V.WHAT2, X=B.V.view(x), Y=B.V.view(y), BEADS=B.V.beads(w)), j


def collect(action, tag, base, phase='all'):
    import msvcrt
    os.environ['THREAD_ROUTE'] = 'mimic' if action == 'labels' else 'gpt3s'
    B.F.configure()
    folder = B.ROOT / 'runs/_batches/round50_from_r49b'
    tasks = list(jobs(action, tag, base))
    if phase != 'all':
        assert action == 'fair', 'Phases apply only to blind comparisons'
        # Four balanced first-pass seats, one per work/judge. Remaining seats
        # are requested only after the first four have been read and passed.
        first = {FAIR.rid_of(w, j, tag, base,
                           'newX' if (w, j) in (('op60', 'g6'), ('op61', 'g56')) else 'newY')
                 for w in B.F.WORKS for j in B.F.JUDGES}
        tasks = [t for t in tasks if (t[0] in first) == (phase == 'quick')]
    with (folder / f'{action}_{tag}_receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def one(job):
            rid, msg, j = job
            B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', msg)
            if not B.evo.done(rid):
                import mg_schedule
                try:
                    # Explicit protection pauses all submission routes.
                    state = mg_schedule.status()
                    if state['cooling'] and state.get('cooldown_kind') == 'suspicious_behavior':
                        mg_schedule.check()
                    response = (B.evo.call_gemini_direct(rid, msg, meta={'stage': 'e2e_open', 'web': True}) if j == 'gem' else
                                B.evo.call(rid, msg, model=B.V.JUDGES[j], meta={'stage': f'r50-{action}', 'web': True}))
                except mg_schedule.CoolingDown as exc:
                    return {'rid': rid, 'status': 'not_submitted_cooldown', 'error': str(exc)}
                if not response:
                    return {'rid': rid, 'status': 'incomplete_inspect_receiver'}
            return {'rid': rid, 'status': 'full_read_required', 'sha256': B.digest(B.evo.output(rid))}
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(one, tasks))
        suffix = '' if phase == 'all' else f'_vs{base}_{phase}'
        (folder / f'{action}_{tag}{suffix}_result.json').write_text(B.json_text({'terminal': True, 'rows': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)
        if action == 'fair' and phase != 'quick' and all(B.evo.done(r) for r, _, _ in tasks):
            print(B.json_text(FAIR.summary(tag, base)), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('open', 'labels', 'fair'))
    p.add_argument('tag')
    p.add_argument('--base', default='r49b')
    p.add_argument('--phase', choices=('all', 'quick', 'finish'), default='all')
    a = p.parse_args()
    collect(a.action, a.tag, a.base, a.phase)
