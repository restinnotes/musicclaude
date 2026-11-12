"""Freeze original-author attempt2 with exact previously reviewed route reuse."""
import json
import re
import difflib
import experiment_batch as B
import round54_candidates as R

rid = 'r58trace_feedback_g56_interface_v2'
folder = B.evo.RUNS / rid
message = (folder / 'prepared_input.txt').read_text(encoding='utf-8')
assert all((folder / name).read_text(encoding='utf-8') == message for name in ('prompt.txt', 'input.txt'))
log = json.loads((folder / 'call.log').read_text(encoding='utf-8'))
assert log['completed'] and log['route'] == 'gpt3-serial'
answer = R.parsed(rid)
original = R.parsed('r58trace_feedback_g56_v2')['candidate']
assert answer['decision'] == 'interface_corrected'
prompt, old = answer['prompt'], original['steps'][0]['prompt']
prefix_old = old.split('ROUTES中的source_warnings是必须')[0]
prefix_new = prompt.split('ROUTES中的source_warnings是必须')[0]
assert prefix_old.replace('不得把结构上的depends_on', '不得将结构上的depends_on') == prefix_new
suffix_old = old[old.index('【第三步：保留确定程度】'):]
suffix_new = prompt[prompt.index('【第三步：保留确定程度】'):]
changes = [s for s in difflib.ndiff(suffix_old.splitlines(), suffix_new.splitlines()) if s.startswith(('- ', '+ '))]
assert len(changes) == 2 and changes[0] == '- 2. 是否执行了所有source_warnings？'
assert changes[1].startswith('+ 2. 是否逐条检查了source_warnings')
B.record_review(rid, True, '全文读decision/reason/完整通用A4；实际prepared/prompt/input逐字绑定。原作者修正warning可选字段段和最终检查2，另把→将无语义变化；其余逐字不变。泛化/四步接口/原标准核验通过，未手改提示词或成品，不是新质量尝试。')
root = B.ROOT / 'runs/_batches/round59_trace_repair'
R.BASE = 'qu'
prior = json.loads((B.ROOT / 'runs/_batches/round58_upstream/candidates.json').read_text(encoding='utf-8'))
source_candidate = next(c for c in prior['candidates'] if c['tag'] == 'r58trace')
sources = {}
for work in B.F.WORKS:
    source = f'scr58trace_{work}_P1'
    assert B.reviewed(source)
    proof = R.verify_input(source_candidate, work, 1)
    sources[work] = {'rid': source, 'input_sha256': proof['full_input_sha256'],
                     'output_sha256': B.digest(B.evo.output(source)), 'original_input_verification': proof}
placeholders = sorted(set(re.findall(r'\{([A-Z_]+)\}', prompt)))
assert set(placeholders) == {'SECTIONS', 'CENTER', 'ROUTES', 'TARGETS'}
path = root / 'prompts/r59tracebound_P1.txt'
B.write_frozen(path, prompt)
candidate = {'tag': 'r59tracebound', 'author': 'r55_advisor_g56',
    'author_feedback': 'r58trace_feedback_g56_v2', 'interface_clarification': rid,
    'name': original['name'], 'hypothesis': original['hypothesis'], 'risk': original['risk'],
    'mode': 'fullgraph', 'attempt': 2, 'parent_attempt': 'r58trace', 'route_sources': sources,
    'steps': [{'id': 'P1', 'author_id': 'route_bound_a4', 'path': str(path.relative_to(B.ROOT)),
               'sha256': B.digest(prompt), 'placeholders': placeholders}],
    'checkpoint_base': 'qu', 'final_mainline_at_freeze': 'r54weave',
    'downstream_required': source_candidate['downstream_required']}
manifest = {'base': 'qu', 'final_mainline': 'r54weave', 'workers': 4, 'candidates': [candidate],
    'source_hashes': {w: B.digest((B.V.OUT / f'{w}_qu.json').read_text(encoding='utf-8')) for w in B.F.WORKS},
    'source_route_line_hashes': source_candidate['line_source_hashes'],
    'reuse': 'Actual approved unchanged P1 ROUTES including all original warnings; no JSON adaptation or P1 regeneration. One new original-author A4 per work.'}
B.write_frozen(root / 'candidates.json', B.json_text(manifest))
B.write_frozen(root / 'prompt_review.json', B.json_text({'approved': True, 'complete_prompt_read': True,
    'generic_and_interfaces_checked': True, 'source_advisers_full_read': True, 'route_reuse_verified': sources,
    'source_feedback_output_sha256': B.digest(B.evo.output('r58trace_feedback_g56_v2')),
    'source_interface_sha256': B.digest(B.evo.output(rid)), 'quality_attempt': 2, 'calls_in_prepare': 0}))
print(B.json_text({'tag': candidate['tag'], 'new_production_calls': 2, 'reused_route_rids': [s['rid'] for s in sources.values()]}))
