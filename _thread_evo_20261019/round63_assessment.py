"""Record a conservative I14 result; never rewrite a model finding."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import collect_i14_after_r62 as I
from round59_inspect import exact

scope = I.validate_scope()
collected = json.loads((I.FOLDER / 'collection_result.json').read_text(encoding='utf-8'))
assert collected['original_receiver_terminal']
rows = []
for row in collected['review_slots']:
    rid = row['rid']
    msg = I.E.msg(row['work']) + ('\n' if row['repeat'] == 2 else '')
    assert B.digest(msg) == row['input_sha256']
    proof = exact(rid, msg)
    assert proof['output_sha256'] == row['output_sha256']
    d = B.V.parse(rid)
    assert set(d) == {'problems', 'top3', 'minor'}
    assert all(p['goal'] in ('1', '2', '3', '4') and p['severity'] in ('轻微', '中等', '严重') for p in d['problems'])
    # The last response was read in full before running this script; all others
    # already have executor inspection receipts from the original collection.
    if rid == 'eo2_i14r63_op60_r54weave_g56_r2':
        B.record_review(rid, True, '全部五项问题/引文/理由/建议/top3/minor已全文阅读；保留长久陪伴重复、分析腔和相反的整体发展读法，改珠子及每条两句建议不采纳。' + B.json_text(proof))
    assert B.reviewed(rid)
    rows.append({**row, 'proof': proof, 'problems': len(d['problems']),
                 'medium_or_higher': sum(p['severity'] != '轻微' for p in d['problems'])})
assert len(rows) == 10

rid = 'eo2_i14r63_op60_r54weave_gem_r1'
finding = B.V.parse(rid)['problems'][3]
assert finding['goal'] == '4' and finding['severity'] == '中等' and 'S11' in finding['where']
line = next(s for s in B.V.graph_of('op60', I.TAG)['segments'] if s['sec'] == 'S11')
beads = [b for b in B.V.covjudge.beads('op60') if b['sec'] == 'S11']
assessment = {
    'status': 'not_proven_unmatched_medium_subfinding', 'i14': False, 'tag': I.TAG,
    'assessed_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
    'scope_sha256': B.digest((I.FOLDER / 'audit_scope.json').read_text(encoding='utf-8')),
    'fresh_group_complete': True, 'all_ten_full_read_and_exact_input_bound': True,
    'original_receiver_terminal': True, 'review_rows': rows,
    'decisive_unmatched_subfinding': {
        'rid': rid, 'problem_index': 3, 'original': finding,
        'specific_claim': 'S11第三条将疼痛归因于不能替对方决定未来，是否挤掉B2/B3的喜悦浓烈和珍贵感本身带来的疼；这与旧的同句分析腔或S13退缩动能错位不同，不能按大类自动匹配。',
        'counterevidence_not_suppressed': {'complete_current_segment': line, 'complete_fixed_segment_beads': beads,
            'reason': 'S11第二条已明确写高兴得胸口发疼且不再害臊，第一条也明确愿长久陪伴、不再躲藏；所以新意见不能直接证明整段没有该原因。标准要求同段大体覆盖，不要求每条承担所有珠子，也不要求英雄式格局。'},
        'decision': '未找到冻结96项中同一位置、同一疼痛原因错配机制的精确旧项；保留原中等意见与反证，交I02诊断成立性及是否有通用可运行的新机制，暂不声称新问题已证实或已经收敛。'},
    'verified_known_examples': [
        {'fresh': ['eo2_i14r63_op60_r54weave_gem_r1', 1], 'prior': ['eo2_op60_r54weave_gem_r1', 1], 'mechanism': '同一S13-2往回收喜欢与固定珠子不肯让步冲突'},
        {'fresh': ['eo2_i14r63_op61_r54weave_gem_r1', 2], 'prior': ['eo2_op61_r54weave_gem_r1', 3], 'mechanism': '同一S09两小节短促闪回却负担复杂二元辨析；R60 Gem第2项亦明确'},
        {'fresh': ['eo2_i14r63_op61_r54weave_gem_r1', 3], 'prior': ['eo2_op61_r54weave_gem_r1', 1], 'mechanism': '同一S13温和日常收束与固定珠子高潮能量不相称；原严重、新中等均保留'},
        {'fresh': ['eo2_i14r63_op61_r54weave_gem_r1', 1], 'prior': ['eo2_op61_r54weave_gem_r1', 4], 'mechanism': '同一亲近/难堪/受气标签全文重复，原轻微与新严重并存不取多数降级'}],
    'editorial_bead_scope': {
        'fresh': ['eo2_i14r63_op61_r54weave_g6_r1', 2], 'original_severity': '中等',
        'preexisting_scope_source': 'runs/_batches/round52_current/open_input_scope_audit.json',
        'boundary': '固定canonical珠子中的原稿编辑说明不能靠改线修好，且不等于交付N03i四处都存在；实际S09仍有一处范围元数据。保留问题，不改珠子、不把它当作可任意消去的线缺点。'},
    'partial_matching_boundary': '这里只记录足以阻止收敛的未决中等子项和已核实具体旧例，不声称其余所有子项都已穷尽匹配。',
    'next': 'I02 original multi-adviser diagnosis and distinct runnable proposals; no repeated unchanged I01 group to seek a favorable verdict.',
    'baseline_policy': 'Final candidate acceptance follows latest accepted mainline r54weave; r49b only final convergence MD. ZIP remains frozen.',
    'all_original_r62_checkpoint_votes_terminal': True,
    'r62_disposition_source': 'runs/_batches/round62_sample_checkpoint/r54sample_final_disposition.json',
    'quality_compliance_proven': False,
}
assert json.loads((B.ROOT / assessment['r62_disposition_source']).read_text(encoding='utf-8'))['status'] == 'archive'
B.write_frozen(I.FOLDER / 'assessment.json', B.json_text(assessment))
print(B.json_text({'status': assessment['status'], 'read': 10, 'medium_instances': sum(r['medium_or_higher'] for r in rows), 'calls': 0}))
