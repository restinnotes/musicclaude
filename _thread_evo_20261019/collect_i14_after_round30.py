"""Collect a fresh I01 group against a prospectively frozen I14 issue scope.

No changed review prompt, production, acceptance rule or automatic convergence verdict.
Preparation sends nothing. The original, exclusively locked receiver owns all calls.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('JV', '2')
os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
import e2e_open as E
import experiment_batch as B

FOLDER = B.ROOT / 'runs/_batches/i14_after_round30'


def now():
    return datetime.now(ZoneInfo('America/New_York')).isoformat()


def validate_scope():
    scope = json.loads((FOLDER / 'audit_scope.json').read_text(encoding='utf-8'))
    for row in scope['prior_issue_sources']:
        if B.digest(B.evo.output(row['rid']) or '') != row['output_sha256']:
            raise ValueError('prior issue output changed: ' + row['rid'])
    for name in ('round29_layers', 'round30_forward'):
        d = json.loads((B.ROOT / 'runs/_batches' / name / 'completed_round_summary.json').read_text(encoding='utf-8'))
        if d.get('accepted') != 0 or not d.get('all_original_parents_terminal'):
            raise ValueError('round not terminal with zero acceptance: ' + name)
    frozen = (B.evo.RUNS / 'batch_round30_forward_advisor_g6/prepared_input.txt').read_text(encoding='utf-8')
    material = json.loads(frozen.split('【完整材料】\n', 1)[1])
    E.TAG = 'qurefs'
    for w in B.F.WORKS:
        if material['mainline'][w] != B.V.view(B.V.graph_of(w, 'qurefs'), center=True):
            raise ValueError('mainline changed since prospective scope: ' + w)
    return scope


def prepare():
    validate_scope()
    path = FOLDER / 'fresh_group_manifest.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    rows = []
    for j, k in (('g6', 1), ('g56', 1), ('gem', 1), ('g6', 2), ('g56', 2)):
        for w in B.F.WORKS:
            rid = f'eo2_afterr30_{w}_qurefs_{j}_r{k}'
            message = E.msg(w) + ('\n' if k == 2 else '')
            folder = B.evo.RUNS / rid
            if folder.exists():
                raise ValueError('fresh run ID already exists before manifest: ' + rid)
            B.write_frozen(folder / 'prepared_input.txt', message)
            rows.append({'rid': rid, 'work': w, 'judge': j, 'repeat': k,
                         'input_sha256': B.digest(message), 'input_chars': len(message)})
    manifest = {'frozen_at': now(), 'workers': 4, 'route': 'gpt3s preferred for GPT judges',
                'scope_sha256': B.digest((FOLDER / 'audit_scope.json').read_text(encoding='utf-8')),
                'review_slots': rows, 'automatic_i14_verdict': False}
    B.write_frozen(path, B.json_text(manifest))
    return manifest


def collect():
    import msvcrt
    B.F.configure()
    validate_scope()
    manifest = json.loads((FOLDER / 'fresh_group_manifest.json').read_text(encoding='utf-8'))
    if manifest['scope_sha256'] != B.digest((FOLDER / 'audit_scope.json').read_text(encoding='utf-8')):
        raise ValueError('prospective scope changed')
    with (FOLDER / 'receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def one(row):
            rid = row['rid']
            message = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
            if B.digest(message) != row['input_sha256']:
                raise ValueError('frozen input changed: ' + rid)
            if not B.evo.done(rid):
                meta = {'stage': 'I01_fresh_I14_after_round30', 'web': True}
                if row['judge'] == 'gem':
                    B.evo.check_submission()
                    response = B.evo.call_gemini_direct(rid, message, meta=meta)
                else:
                    model = B.V.JUDGES[row['judge']]
                    B.evo.check_submission(model)
                    response = B.evo.call(rid, message, model=model, meta=meta)
                if not response:
                    return {**row, 'status': 'no_complete_response_inspect_before_retry'}
            parsed = B.V.parse(rid)
            valid = (isinstance(parsed, dict) and isinstance(parsed.get('problems'), list)
                     and isinstance(parsed.get('top3'), list) and 'minor' in parsed
                     and all(str(p.get('goal', '')).strip()[:1] in '1234'
                             and p.get('severity') in ('轻微', '中等', '严重')
                             and all(key in p for key in ('where', 'quotes', 'why', 'suggestion'))
                             for p in parsed['problems']))
            return {**row, 'status': 'full_read_required' if valid else 'invalid_review_inspect',
                    'output_sha256': B.digest(B.evo.output(rid))}
        with ThreadPoolExecutor(max_workers=manifest['workers']) as pool:
            result = list(pool.map(one, manifest['review_slots']))
        (FOLDER / 'collection_result.json').write_text(B.json_text({
            'collected_at': now(), 'original_receiver_terminal': True,
            'review_slots': result, 'i14': 'not_decided_full_read_and_specific_matching_required'
        }), encoding='utf-8')
        print(B.json_text(result), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'collect'))
    action = parser.parse_args().action
    if action == 'prepare':
        d = prepare()
        print(B.json_text({'slots': len(d['review_slots']), 'workers': d['workers'], 'model_calls': 0}))
    else:
        collect()
