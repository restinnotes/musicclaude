"""New I14 cycle after the actual boundary trial and corrected sample checkpoint.

The judge prompt is unchanged. All prior concrete findings are frozen before
submission. Collection alone never declares convergence or modifies products.
"""
import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
os.environ.setdefault('JV', '2')
os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
import experiment_batch as B
import e2e_open as E
import collect_i14_after_round30 as receiver
import round50_measure as M
from round59_inspect import exact

FOLDER = B.ROOT / 'runs/_batches/i14_after_r62'
TAG = 'r54weave'


def now():
    return datetime.now(ZoneInfo('America/New_York')).isoformat()


def validate_scope():
    scope = json.loads((FOLDER / 'audit_scope.json').read_text(encoding='utf-8'))
    for path, sha in scope['frozen_file_hashes'].items():
        assert B.digest((B.ROOT / path).read_text(encoding='utf-8')) == sha, path
    for row in scope['prior_issue_sources']:
        assert B.reviewed(row['rid']) and B.digest(B.evo.output(row['rid'])) == row['output_sha256']
    for path in scope['failed_round_sources']:
        assert json.loads((B.ROOT / path).read_text(encoding='utf-8'))['status'] == 'archive'
    for row in scope['corrected_checkpoint_decisive_votes']:
        assert B.reviewed(row['rid'])
        assert B.digest(B.evo.output(row['rid'])) == row['output_sha256']
    assert len(scope['corrected_checkpoint_decisive_votes']) == 3
    E.TAG = TAG
    return scope


def prepare():
    if (FOLDER / 'fresh_group_manifest.json').exists():
        validate_scope()
        return
    old_scope = json.loads((B.ROOT / 'runs/_batches/i14_after_r59/audit_scope.json').read_text(encoding='utf-8'))
    fresh = json.loads((B.ROOT / 'runs/_batches/i14_after_r59/fresh_group_manifest.json').read_text(encoding='utf-8'))
    assessment = json.loads((B.ROOT / 'runs/_batches/i14_after_r59/assessment.json').read_text(encoding='utf-8'))
    assert assessment['status'] == 'not_converged_new_medium_findings'
    sources, issues, minors = [], [], []
    for source in old_scope['prior_issue_sources'] + fresh['review_slots']:
        rid, w = source['rid'], source['work']
        assert B.reviewed(rid)
        sources.append({'rid': rid, 'work': w, 'output_sha256': B.digest(B.evo.output(rid))})
        d = B.V.parse(rid)
        for index, problem in enumerate(d['problems']):
            issues.append({'rid': rid, 'problem_index': index, 'work': w, **problem})
        minors.append({'rid': rid, 'work': w, 'minor': d['minor']})
    assert len(sources) == 20 and len({r['rid'] for r in sources}) == 20
    failed = ['runs/_batches/round55_current/r55shell_final_disposition.json',
              'runs/_batches/round55_current/r55restored_final_disposition.json',
              'runs/_batches/round56_paired/r56paired_final_disposition.json',
              'runs/_batches/round61_boundary/r61bridge_final_disposition.json']
    decisive = []
    for rid, msg, judge in M.jobs('fair', 'r54sample', 'qu'):
        if rid in ('v6b3_op61_g6_r54sample_vsqu_newY',
                   'v6b3_op61_g56_r54sample_vsqu_newX',
                   'v6b3_op60_g56_r54sample_vsqu_newY'):
            assert B.reviewed(rid)
            d = B.V.parse(rid)
            new = 'X' if rid.endswith('_newX') else 'Y'
            assert d['better'] in ('X', 'Y') and d['better'] != new
            decisive.append(exact(rid, msg))
    assert len(decisive) == 3
    paths = failed + ['标准.md', '迭代准则.md', 'e2e_open.py', 'DAG.md',
        'runs/_batches/round61_new_findings/baseline_policy.json',
        'runs/_batches/i14_after_r59/assessment.json',
        'runs/_batches/round61_boundary/production_verified.json',
        'runs/_batches/round62_sample_checkpoint/placement_audit.json']
    paths += [str((B.V.OUT / f'{w}_{TAG}.json').relative_to(B.ROOT)) for w in B.F.WORKS]
    scope = {'frozen_at': now(), 'tag': TAG,
        'status': 'prospective_only_before_fresh_requests',
        'rule': old_scope['rule'], 'novelty_rule': old_scope['novelty_rule'],
        'prior_issue_sources': sources, 'prior_issues': issues, 'prior_minor_observations': minors,
        'frozen_file_hashes': {p: B.digest((B.ROOT / p).read_text(encoding='utf-8')) for p in paths},
        'failed_rounds': ['R55', 'R56', 'R57-R59 archived', 'R61'], 'failed_round_sources': failed,
        'corrected_checkpoint_decisive_votes': decisive,
        'corrected_checkpoint_bound': 'Three actual original balanced checkpoint votes choose qu. Last original in-flight vote cannot bring new wins above 1/4, hence neither quick3/4 nor near-pass minimum2/4 can be reached. No new product or promotion can result; still collect and read the last original response before stopping.',
        'must_finish_before_stopping': ['original90598 fourth checkpoint vote and final disposition', 'fresh ten original I01 replies and specific issue matching'],
        'why_new_cycle': 'The failed R60 I14 was followed by original multi-adviser I02, a new fully produced R61 boundary mechanism and real quick4, plus a correction of the previously unmeasured same-position sampling mechanism. This group checks the completed new search cycle; it is not a retry for a favorable rating or a claim old medium issues were solved.',
        'unresolved': 'All known problems and contrary readings remain known; no downgrade, majority override or broad-category matching. New location/claim/mechanism or a previously unrecorded medium subfinding means I14 fails.',
        'invalid_if_mainline_changes': True, 'zip': 'frozen',
        'previous_goal_turn': {'classification': 'progress', 'evidence': ['R61 actual paired production and quick4 disposition', 'verified historical checkpoint placement defect and original correction requests']}}
    B.write_frozen(FOLDER / 'audit_scope.json', B.json_text(scope))
    validate_scope()
    rows = []
    for j, k in (('g6', 1), ('g56', 1), ('gem', 1), ('g6', 2), ('g56', 2)):
        for w in B.F.WORKS:
            rid = f'eo2_i14r63_{w}_{TAG}_{j}_r{k}'
            assert not (B.evo.RUNS / rid).exists()
            msg = E.msg(w) + ('\n' if k == 2 else '')
            B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', msg)
            rows.append({'rid': rid, 'work': w, 'judge': j, 'repeat': k,
                         'input_sha256': B.digest(msg), 'input_chars': len(msg)})
    B.write_frozen(FOLDER / 'fresh_group_manifest.json', B.json_text({'frozen_at': now(),
        'workers': 4, 'route': 'gpt3s preferred for GPT judges', 'review_slots': rows,
        'scope_sha256': B.digest((FOLDER / 'audit_scope.json').read_text(encoding='utf-8')),
        'automatic_i14_verdict': False}))
    print(B.json_text({'calls': 0, 'prior_sources': len(sources), 'prior_specific_issues': len(issues), 'new_slots': 10}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare', 'collect'))
    args = p.parse_args()
    if args.action == 'prepare':
        prepare()
    else:
        receiver.FOLDER = FOLDER
        receiver.validate_scope = validate_scope
        receiver.collect()
