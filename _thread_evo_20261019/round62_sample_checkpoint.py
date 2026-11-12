"""Repair one historical checkpoint placement without resampling the product."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import round54_candidates as R

ROOT = B.ROOT / 'runs/_batches/round62_sample_checkpoint'
R.BASE = 'r50progress1rr'
R.ROOT = B.ROOT / 'runs/_batches/round54_broader'
old_manifest = json.loads((R.ROOT / 'candidates.json').read_text(encoding='utf-8'))
c = next(c for c in old_manifest['candidates'] if c['tag'] == 'r54sample')
q15 = (B.ROOT / 'schemes/Q15_A4.txt').read_text(encoding='utf-8')
assert c['mode'] == 'sample'
assert all((B.ROOT / s['path']).read_text(encoding='utf-8') == q15 for s in c['steps'][:2])
proofs = []
for w in B.F.WORKS:
    for k in (1, 2, 3):
        assert R.stage_seen(c, w, k)
        proofs.append(R.verify_input(c, w, k))
    d = R.checked_result(c, w)
    stored = B.V.graph_of(w, 'r54sample')
    assert [i['text'] for s in d['segments'] for i in s['items']] == [i['text'] for s in stored['segments'] for i in s['items']]
old = json.loads((R.ROOT / 'r54sample_disposition.json').read_text(encoding='utf-8'))
assert old['quick']['base'] == 'r50progress1rr' and old['quick']['complete'] == 4
policy = {
    'frozen_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'tag': 'r54sample', 'checkpoint_base': 'qu', 'actual_final_mainline': 'r54weave',
    'status': 'missing_same_position_checkpoint_not_a_new_production_or_favorable_reask',
    'finding': 'Historical selected output is bare Q15 A4 plus verbatim selection, but its original quick4 compared against post-N05e r50progress1rr. That is a valid direct final-body loss, not evidence that the A4 sampling mechanism failed at its same-position checkpoint.',
    'old_comparison': {'path': 'runs/_batches/round54_broader/r54sample_disposition.json', 'sha256': B.digest(B.json_text(old)), 'preserve_all_original_votes': True},
    'input_proofs': proofs,
    'body_hashes': {w: B.digest((B.V.OUT / f'{w}_r54sample.json').read_text(encoding='utf-8')) for w in B.F.WORKS},
    'checkpoint_source_hashes': {w: B.digest((B.V.OUT / f'{w}_qu.json').read_text(encoding='utf-8')) for w in B.F.WORKS},
    'calls_in_prepare': 0, 'new_productions': 0,
    'next': 'One original balanced quick4 versus current A4 node output qu. Original gates unchanged. Floors only if quick passes. If survivor rerun affected N05e/N05f under a new tag, then formal final comparison against then-current accepted mainline; never call a qu checkpoint win a win over r54.',
    'r49b': 'Only final convergence MD. No new fixed-start requests.',
    'other_r54_modes': 'Role/reader/weave read current final LINE as postwrite inputs; ground hard-format failure happened before comparison. This verified placement defect concerns sample only; it is not evidence all past baselines were wrong.'
}
B.write_frozen(ROOT / 'placement_audit.json', B.json_text(policy))
print(B.json_text({'tag': 'r54sample', 'checkpoint_base': 'qu', 'final_base': 'r54weave', 'existing_source_calls_verified': len(proofs), 'new_productions': 0}))
