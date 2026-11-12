"""Freeze one reviewed boundary mechanism without changing adviser prose."""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import round54_candidates as R
import round59_inspect as inspect

ROOT = B.ROOT / 'runs/_batches/round61_boundary'
BASE = 'r54weave'
advisers = B.ROOT / 'runs/_batches/round61_new_findings'
tasks = json.loads((advisers / 'advisors.json').read_text(encoding='utf-8'))['tasks']
proofs = []
for author in ('r61_advisor_g6a', 'r61_advisor_g56'):
    folder = B.evo.RUNS / author
    message = (folder / 'prepared_input.txt').read_text(encoding='utf-8')
    assert B.digest(message) == next(t for t in tasks if t['rid'] == author)['input_sha256']
    proofs.append(inspect.exact(author, message))
    data = B.V.parse(author)
    assert len(data['candidates']) == 1
    B.record_review(author, True, '已全文读诊断、完整prompt、风险、放弃方向；实际完整附件/字节manifest绑定。状态边界机制通用且不接触珠子构思。原评级和相反意见保留；顾问将tracebound快筛口头称未通过的句子不能替代脚本原快筛pass，实际在覆盖底线失败。' + B.json_text(proofs[-1]))

plan = B.V.parse('r61_advisor_g6a')['candidates'][0]
assert len(plan['steps']) == 1
step = plan['steps'][0]
prompt = step['prompt']
placeholders = sorted(set(re.findall(r'\{([A-Z_]+)\}', prompt)))
assert set(placeholders) == {'SECTIONS', 'CENTER', 'LINE'}
path = ROOT / 'prompts/r61bridge_P1.txt'
B.write_frozen(path, prompt)
candidate = {'tag': 'r61bridge', 'author': 'r61_advisor_g6a', 'author_index': 0,
    'name': plan['name'], 'hypothesis': plan['hypothesis'], 'risk': plan['risk'],
    'mode': 'edits', 'attempt': 1,
    'steps': [{'id': 'P1', 'author_id': step['id'], 'path': str(path.relative_to(B.ROOT)),
               'sha256': B.digest(prompt), 'placeholders': placeholders}],
    'checkpoint_base': BASE, 'final_mainline_at_freeze': BASE,
    'downstream_required': [],
    'edit_contract': 'replace only; at most one entry in the later segment for each adjacent boundary; all metadata unchanged; empty edits permitted'}
B.write_frozen(ROOT / 'candidates.json', B.json_text({'base': BASE, 'workers': 4,
    'candidates': [candidate], 'source_hashes': {w: B.digest((B.V.OUT / f'{w}_{BASE}.json').read_text(encoding='utf-8')) for w in B.F.WORKS}}))
B.write_frozen(ROOT / 'prompt_review.json', B.json_text({'approved': True,
    'generic_and_interfaces_checked': True, 'complete_prompt_read': True,
    'source_proofs': proofs, 'calls': 0,
    'selection': 'Two completed advisers propose the same adjacent event-state distinction; run the no-BEADS/no-REVIEWS representative once, do not count BoundarySeam as an independent mechanism. Third adviser still collecting under original parent.',
    'history': 'R53 broad consistency and R55 broad repairs failed; this restricts modifications to later-side handoff items with all original metadata frozen. No revival of coverage word substitutions or full rewrites.',
    'baseline': 'Actual final r54weave; formal acceptance advances on a new accepted mainline. r49b only at convergence for final MD.'}))
R.BASE, R.ROOT = BASE, ROOT
for w in B.F.WORKS:
    message = R.message(candidate, w, 1)
    assert not re.search(r'\{(?:SECTIONS|CENTER|LINE)\}', message)
    B.write_frozen(B.evo.RUNS / R.rid(candidate, w, 1) / 'prepared_input.txt', message)
print(B.json_text({'prepared': candidate['tag'], 'base': BASE, 'calls': 0, 'new_productions': 2,
    'time': datetime.now(ZoneInfo('America/New_York')).isoformat()}))
