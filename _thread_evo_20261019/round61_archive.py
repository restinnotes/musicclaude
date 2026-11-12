"""Record the real four-vote result without buying unnecessary later gates."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import round54_candidates as R

R.BASE = 'r54weave'
R.ROOT = B.ROOT / 'runs/_batches/round61_boundary'
q = R.quick_state('r61bridge')
assert q['complete'] == 4 and q['wins'] == 2 and not q['pass']
assert q['net_sums'] == {'alone': 2, 'lean': -1, 'plain': 1, 'cover': 2}
d = {'tag': 'r61bridge', 'actual_comparison_base': R.BASE, 'status': 'archive',
    'recorded_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'fully_read_quick': q, 'actual_quality_productions': 1,
    'failed_conditions': ['overall new-version votes 2/4 < 3/4', 'lean net -1 < 0'],
    'near_pass': False,
    'reason': 'Two conditions fail, so original I12 single-condition exception does not apply. Op60 model returns empty edits and both blind judges tie every section; Op61 both prefer the one-entry warmth handoff edit, but G56 prefers old brevity there. Preserve that small positive evidence without replacing the accepted paired mainline.',
    'next': 'No coverage, standalone, finish4, author return or promotion. No hand merge of the single-work word change. The new Op60 S04/S05 concern remains unresolved with contrary readings retained.',
    'unmeasured': ['coverage floors', 'standalone floors', 'remaining blind4'],
    'no_regress_is_not_a_quick_gate': True,
    'source_verification': 'runs/_batches/round61_boundary/production_verified.json'}
B.write_frozen(R.ROOT / 'r61bridge_final_disposition.json', B.json_text(d))
print(B.json_text({'tag': d['tag'], 'base': R.BASE, 'status': d['status'], 'wins': q['wins'], 'calls': 0}))
