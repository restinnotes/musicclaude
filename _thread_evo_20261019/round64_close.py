"""Close original I02 responses and resolve the two explicit I14 audit gaps."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import collect_i14_after_r62 as I
from round59_inspect import exact

scope = I.validate_scope()
root = B.ROOT / 'runs/_batches/round64_diagnosis'
manifest = json.loads((root / 'advisors.json').read_text(encoding='utf-8'))
collection = json.loads((root / 'collection.json').read_text(encoding='utf-8'))
assert collection['terminal']
rows = []
for t in manifest['tasks']:
    rid = t['rid']
    assert B.reviewed(rid)
    msg = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
    assert B.digest(msg) == t['input_sha256']
    d = B.V.parse(rid)
    assert d['candidates'] == [] and d['declined_directions']
    rows.append({**t, 'proof': exact(rid, msg), 'candidate_count': 0,
                 'declined_directions': d['declined_directions']})
assert len(rows) == 3
now = datetime.now(ZoneInfo('America/New_York')).isoformat()
if (root / 'final_disposition.json').exists():
    now = json.loads((root / 'final_disposition.json').read_text(encoding='utf-8'))['closed_at']
B.write_frozen(root / 'final_disposition.json', B.json_text({
    'status': 'no_independent_candidate_declined', 'tag': I.TAG, 'closed_at': now,
    'original_receiver_terminal': True, 'parent_session': 37718, 'all_three_full_read_and_input_bound': True,
    'rows': rows, 'production_calls': 0, 'new_versions': 0, 'DAG_change': False,
    'history_corrections': [
        'g6a将身体性S06-B1/B4缺口写作Op61，实际固定珠子归Op60；不采用作品口误。',
        'g6b将tracebound快筛0/4不退步描述成最终门槛失败；实际快筛4/4新版及所需净胜通过，确定失败是Op60 S06覆盖，未购买正式8票。',
        'g56把R58Trace概述为过快筛后覆盖失败；实际R58Trace为3/4但lean -4近线退回，后继R59tracebound才4/4快筛后覆盖失败。'],
    'boundary': '顾问没有新方案不是质量达标证明；不以多数意见删除原评级。下面的标准/原文审计独立决定I14未决子项。'}))

original = B.V.parse('eo2_i14r63_op60_r54weave_gem_r1')['problems'][3]
line = next(s for s in B.V.graph_of('op60', I.TAG)['segments'] if s['sec'] == 'S11')
texts = {x['id']: x['text'] for x in line['items']}
assert '高兴得胸口发疼' in texts['S11-2'] and '不想再' in texts['S11-2']
assert '不想再躲躲藏藏' in texts['S11-1'] and '没法替对方作决定' in texts['S11-3']
standard = (B.ROOT / '标准.md').read_text(encoding='utf-8')
assert '相关就行，不必逐颗解释，大体覆盖就够' in standard
assert '一段里的几种听感不压成一种' in standard
assert '戏剧化、主观、只讲一个故事；没有外部动作' in standard
beads = [b for b in B.V.covjudge.beads('op60') if b['sec'] == 'S11']
editorial = []
for rid, index in [('eo2_op61_r50progress1rr_g6_r1', 3), ('eo2_op61_r50progress1rr_g6_r2', 2)]:
    assert B.reviewed(rid)
    msg = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
    # The old renderer used different list/header whitespace; compare each
    # immutable bead body itself, rather than the presentation wrapper.
    assert all(msg.count(b['text']) == 1 for b in B.V.covjudge.beads('op61')
               if b['role'] != '演奏条件'), 'Earlier source must contain every identical fixed bead body once'
    issue = B.V.parse(rid)['problems'][index]
    assert issue['severity'] == '中等' and '原稿' in B.json_text(issue)
    editorial.append({'rid': rid, 'problem_index': index, 'original': issue,
                      'output_sha256': B.digest(B.evo.output(rid)), 'identical_fixed_beads_in_earlier_input': True})
scope_path = B.ROOT / 'runs/_batches/round52_current/open_input_scope_audit.json'
scope_audit = json.loads(scope_path.read_text(encoding='utf-8'))
old_material = json.loads((B.ROOT / 'runs/_batches/round61_new_findings/materials.json').read_text(encoding='utf-8'))
assert old_material['scope_audit'] == scope_audit
joined = (B.ROOT / 'deliver_20261103_r54weave/op61_线与珠子_r54weave.md').read_text(encoding='utf-8')
assert joined.count('原稿') == 1 and '相关原稿多以mm.214' in joined
resolution = {
    'tag': I.TAG, 'resolved_at': now, 'original_r63_assessment_preserved': True,
    'pain_source_finding': {
        'rid': 'eo2_i14r63_op60_r54weave_gem_r1', 'problem_index': 3, 'original': original,
        'classification': 'new_claim_not_established_as_a_standard_defect',
        'direct_evidence': {'complete_line_segment': line, 'complete_fixed_beads': beads,
            'standard_passages': ['相关就行，不必逐颗解释，大体覆盖就够', '一段里的几种听感不压成一种']},
        'executor_reason': '原意见承认第三条有未来不确定性，进而推断整段把喜悦本身的疼消掉；这一步与同段第二条高兴得胸口发疼直接矛盾。第一条坦白/长期陪伴、第二条浓烈喜悦、第三条未知带来的重量可以同时成立；标准以同段大体相关为单位，没有每条逐颗覆盖或英雄格局要求。故不构成新的中等标准缺口，不通过删掉未知或再补疼痛来迎合该推断。',
        'not_a_downgrade': '原中等原样保留，既不改为轻微也不以三位顾问多数压票；另有G6对同段两次疼措辞重复的轻微项原样保留，不与此中等覆盖意见混同。'},
    'editorial_bead_finding': {
        'rid': 'eo2_i14r63_op61_r54weave_g6_r1', 'problem_index': 2,
        'classification': 'known_fixed_bead_editorial_issue_with_preexisting_scope_audit',
        'earlier_exact_observations': editorial, 'scope_audit_source': str(scope_path.relative_to(B.ROOT)),
        'scope_preexists_in_frozen_r61_materials': True,
        'boundary': '冻结96项只列当前r54两组，未列更早r50的已审固定珠子问题；此补充不修改原冻结范围。更早原评审已指出同一S07/S09/S10原稿编辑说明，并含相同固定珠子全文；新意见未因主线换线才出现。原中等/尚存S09一处范围元数据保留，固定珠子不得改。不能声称已消灭所有编辑说明。'},
    'all_other_medium_instances': 'specific_matches.json列出全部26项各自位置/引文/机制及原具体证据，旧问题仍未解决，不借旧评级降低新评级。',
    'adviser_disposition': 'runs/_batches/round64_diagnosis/final_disposition.json',
    'no_model_calls_for_resolution': True, 'no_text_edits': True,
}
B.write_frozen(I.FOLDER / 'specific_subfinding_resolution.json', B.json_text(resolution))
matched = json.loads((I.FOLDER / 'specific_matches.json').read_text(encoding='utf-8'))
assert matched['all_medium_instances'] == 28 and matched['specific_known_instances'] == 26
assessment = json.loads((I.FOLDER / 'assessment.json').read_text(encoding='utf-8'))
assert assessment['all_ten_full_read_and_exact_input_bound']
final = {'status': 'verified_i14_stop_condition', 'i14': True, 'tag': I.TAG, 'verified_at': now,
    'rule': scope['rule'], 'prospective_scope_sha256': assessment['scope_sha256'],
    'fresh_ten_complete_full_read_and_exact_bound': True,
    'medium_instances': 28, 'specific_known_line_instances': 26,
    'known_fixed_bead_instances': 1, 'new_unsupported_segment_coverage_claims': 1,
    'new_valid_medium_or_higher_standard_defects': 0,
    'no_acceptance_round_sources': scope['failed_round_sources'],
    'latest_actual_failed_trials': ['runs/_batches/round61_boundary/r61bridge_final_disposition.json',
                                    'runs/_batches/round62_sample_checkpoint/r54sample_final_disposition.json'],
    'all_original_review_and_adviser_collectors_terminal': True,
    'new_I02_candidates': 0, 'no_repeated_favorable_I01_group_requested': True,
    'evidence': ['runs/_batches/i14_after_r62/audit_scope.json',
        'runs/_batches/i14_after_r62/assessment.json', 'runs/_batches/i14_after_r62/specific_matches.json',
        'runs/_batches/i14_after_r62/specific_subfinding_resolution.json',
        'runs/_batches/round64_diagnosis/final_disposition.json'],
    'quality_compliance_proven': False, 'global_best_or_generalization_proven': False,
    'remaining': '原有重复、分析腔、相互需要/安心依据、体验未完全覆盖及全部严重/中等分歧仍存在；I14只终止本次已试搜索，不声称所有标准都已满足。固定起点r49直接8票仍未通过。',
    'completion_still_requires': 'Separate product/evidence/scheduling/document audit and script-generated final comparison MD.'}
for path in final['no_acceptance_round_sources'] + final['latest_actual_failed_trials']:
    assert json.loads((B.ROOT / path).read_text(encoding='utf-8'))['status'] == 'archive'
B.write_frozen(I.FOLDER / 'final_i14_assessment.json', B.json_text(final))
print(B.json_text({'I14_stop_condition': True, 'new_candidates': 0, 'quality_compliance_proven': False, 'calls': 0}))
