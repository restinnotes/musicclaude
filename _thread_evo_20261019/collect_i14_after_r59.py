"""Fresh unchanged I01 group with a prospective, immutable specific issue scope.

prepare sends no requests. collect never declares convergence; all ten answers
must be read and individually matched to prior issues by the executor.
"""
import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
import experiment_batch as B
import e2e_open as E
import collect_i14_after_round30 as receiver

FOLDER = B.ROOT / 'runs/_batches/i14_after_r59'
TAG = 'r54weave'


def stamp():
    return datetime.now(ZoneInfo('America/New_York')).isoformat()


def validate_scope():
    scope = json.loads((FOLDER / 'audit_scope.json').read_text(encoding='utf-8'))
    for path, sha in scope['frozen_file_hashes'].items():
        assert B.digest((B.ROOT / path).read_text(encoding='utf-8')) == sha, path
    for row in scope['prior_issue_sources']:
        assert B.reviewed(row['rid']) and B.digest(B.evo.output(row['rid'])) == row['output_sha256']
    for path in scope['failed_round_sources']:
        d = json.loads((B.ROOT / path).read_text(encoding='utf-8'))
        assert d['status'] == 'archive'
    E.TAG = TAG
    return scope


def prepare():
    if (FOLDER / 'fresh_group_manifest.json').exists():
        validate_scope()
        return
    sources, issues = [], []
    for w in B.F.WORKS:
        for j in ('g6', 'g56', 'gem'):
            for k in ((1,) if j == 'gem' else (1, 2)):
                rid = f'eo2_{w}_{TAG}_{j}_r{k}'
                assert B.reviewed(rid)
                sources.append({'rid': rid, 'work': w, 'output_sha256': B.digest(B.evo.output(rid))})
                for index, problem in enumerate(B.V.parse(rid)['problems']):
                    issues.append({'rid': rid, 'problem_index': index, 'work': w, **problem})
    failed = ['runs/_batches/round55_current/r55shell_final_disposition.json',
              'runs/_batches/round55_current/r55restored_final_disposition.json',
              'runs/_batches/round56_paired/r56paired_final_disposition.json']
    paths = failed + ['标准.md', '迭代准则.md', 'e2e_open.py'] + [str((B.V.OUT / f'{w}_{TAG}.json').relative_to(B.ROOT)) for w in B.F.WORKS]
    hashes = {p: B.digest((B.ROOT / p).read_text(encoding='utf-8')) for p in paths}
    scope = {'frozen_at': stamp(), 'tag': TAG, 'status': 'prospective_only_no_new_review_requests',
        'rule': 'Original I14: at least two consecutive actual rounds without acceptance, and one fresh unchanged I01 group has no new medium-or-higher specific findings relative to all frozen prior findings. Known unresolved issues remain unresolved. No perfection/generalization claim.',
        'must_finish_before_stopping': ['r59routefirst checkpoint disposition', 'r59tracebound original-author final return and any resulting lawful production/measurement'],
        'invalid_if_mainline_changes': True, 'failed_rounds': ['R55', 'R56'], 'failed_round_sources': failed,
        'prior_issue_sources': sources, 'prior_issues': issues, 'frozen_file_hashes': hashes,
        'novelty_rule': 'Match specific location, quoted fact or phrase and failure mechanism; broad themes alone do not establish an old issue. Preserve original severity, dissent and outside-scope advice. Unmatched medium-or-higher means not converged; no re-asking unchanged reviews until favorable.'}
    B.write_frozen(FOLDER / 'audit_scope.json', B.json_text(scope))
    validate_scope()
    rows = []
    for j, k in (('g6',1),('g56',1),('gem',1),('g6',2),('g56',2)):
        for w in B.F.WORKS:
            rid = f'eo2_i14r60_{w}_{TAG}_{j}_r{k}'
            message = E.msg(w) + ('\n' if k == 2 else '')
            assert not (B.evo.RUNS / rid).exists()
            B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', message)
            rows.append({'rid':rid,'work':w,'judge':j,'repeat':k,'input_sha256':B.digest(message),'input_chars':len(message)})
    B.write_frozen(FOLDER / 'fresh_group_manifest.json', B.json_text({'frozen_at': stamp(),'workers':4,
        'scope_sha256':B.digest((FOLDER/'audit_scope.json').read_text(encoding='utf-8')),
        'route':'gpt3s preferred for GPT judges','review_slots':rows,'automatic_i14_verdict':False}))
    print(B.json_text({'calls':0,'prior_sources':len(sources),'prior_specific_issues':len(issues),'frozen_review_slots':10}))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=('prepare','collect'))
    a=p.parse_args()
    if a.action=='prepare':
        prepare()
    else:
        receiver.FOLDER=FOLDER
        receiver.validate_scope=validate_scope
        receiver.collect()
