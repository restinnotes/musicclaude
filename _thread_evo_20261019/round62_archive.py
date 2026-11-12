"""Close the corrected same-position comparison, retaining the old direct loss."""
import copy
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import round54_candidates as R
from round59_inspect import blind
import round37_fair as F

ROOT = B.ROOT / 'runs/_batches/round62_sample_checkpoint'
source = B.ROOT / 'runs/_batches/round54_broader'
collection = json.loads((B.ROOT / 'runs/_batches/round50_from_r49b/fair_r54sample_vsqu_quick_result.json').read_text(encoding='utf-8'))
assert collection['terminal'] and len(collection['rows']) == 4
assert all(row['status'] == 'full_read_required' for row in collection['rows'])
q = blind('r54sample', 'qu', ROOT.name)
assert q['complete'] == 4 and q['wins'] == 0 and not q['pass']
c = copy.deepcopy(next(c for c in json.loads((source / 'candidates.json').read_text(encoding='utf-8'))['candidates'] if c['tag'] == 'r54sample'))
c.update({'checkpoint_base': 'qu', 'final_mainline_at_freeze': 'r54weave',
    'reuse_only': True, 'new_production_calls': 0,
    'downstream_required': 'Would require affected N05e/N05f and final acceptance versus current mainline, but corrected quick4 fails so none are run.'})
B.write_frozen(ROOT / 'candidates.json', B.json_text({'base': 'qu', 'final_mainline': 'r54weave',
    'candidates': [c], 'workers': 4, 'reuse_only': True,
    'scope': 'Reporting receipt for the existing exact selected pair; no production collector or new sampling in this batch.'}))
old_applied = json.loads((source / 'r54sample_applied.json').read_text(encoding='utf-8'))
for w, sha in old_applied['graph_hashes'].items():
    assert B.digest((B.V.OUT / f'{w}_r54sample.json').read_text(encoding='utf-8')) == sha
B.write_frozen(ROOT / 'r54sample_applied.json', B.json_text({**old_applied, 'base': 'qu',
    'reuse_receipt_only': True, 'source_applied': str((source / 'r54sample_applied.json').relative_to(B.ROOT)),
    'actual_original_production_base_metadata': old_applied['base'], 'new_model_calls': 0}))
d = {'tag': 'r54sample', 'actual_comparison_base': 'qu', 'status': 'archive',
    'recorded_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'fully_read_quick': q, 'near_pass': False,
    'reason': 'All four actual balanced same-position votes prefer current A4 qu, with substantial losses in specific transitions and later development. Historical bare-A4 versus postwrite-final comparison alone was insufficient; this corrected test now directly rules out this selected paired sample at its checkpoint.',
    'original_receiver_terminal': True, 'original_parent_session': '90598',
    'new_productions': 0, 'old_comparison_preserved': True,
    'infra': 'Op60 G6 first attempt UPSTREAM_STREAM_ERROR; original receiver alone completed attempt1. Both attempts are one measurement slot, not two votes or quality productions.',
    'next': 'No floors, finish4, author return, downstream or promotion. Current mainline remains r54weave. Final r49b comparison only after convergence.',
    'unmeasured': ['checkpoint coverage floors', 'checkpoint standalone floors', 'affected N05e/N05f production', 'final vs r54weave']}
B.write_frozen(ROOT / 'r54sample_final_disposition.json', B.json_text(d))
F.summary('r54sample', 'qu')
print(B.json_text({'status': d['status'], 'base': 'qu', 'wins': q['wins'], 'no_regress': q['no_regress'], 'net': q['net_sums'], 'new_productions': 0}))
