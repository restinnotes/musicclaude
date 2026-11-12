"""Bind the fully read fresh group and preserve the failed I14 check.

The concrete novelty decisions below are executor findings, not generated ratings.
This script never requests a model or alters a rating/product.
"""
import json
from datetime import datetime
from zoneinfo import ZoneInfo
import experiment_batch as B
import collect_i14_after_r59 as I
from round59_inspect import exact


def build():
    scope = I.validate_scope()
    manifest = json.loads((I.FOLDER / 'fresh_group_manifest.json').read_text(encoding='utf-8'))
    collection = json.loads((I.FOLDER / 'collection_result.json').read_text(encoding='utf-8'))
    assert collection['original_receiver_terminal']
    rows, full = [], ['# 当前r54weave原I01新组全文', '', '原评审提示词、等级及分歧原样保留；不是验收分数。', '']
    for row in manifest['review_slots']:
        rid = row['rid']
        assert B.reviewed(rid), 'Executor must read before binding: ' + rid
        result = next(x for x in collection['review_slots'] if x['rid'] == rid)
        assert result['status'] == 'full_read_required'
        message = I.E.msg(row['work']) + ('\n' if row['repeat'] == 2 else '')
        assert row['input_sha256'] == B.digest(message)
        proof = exact(rid, message)
        assert result['output_sha256'] == proof['output_sha256']
        d = B.V.parse(rid)
        assert isinstance(d['problems'], list) and isinstance(d['top3'], list) and 'minor' in d
        assert all(p['severity'] in ('轻微', '中等', '严重') and str(p['goal'])[:1] in '1234'
                   and all(k in p for k in ('where', 'quotes', 'why', 'suggestion')) for p in d['problems'])
        rows.append({**row, **proof, 'problems': len(d['problems']),
                     'medium_or_higher': sum(p['severity'] in ('中等', '严重') for p in d['problems'])})
        full += ['## ' + rid, '', '```text', B.evo.output(rid), '```', '']
    assert len(rows) == 10
    # These cannot be absorbed into a broad theme to manufacture convergence.
    new = [
        {'rid': 'eo2_i14r60_op60_r54weave_gem_r1', 'problem_index': 3,
         'finding': 'S04没把话全说出口→S05不再时时藏好、自然被看见之间的心理过渡被判不足。',
         'severity': '中等', 'status': 'new_relative_to_frozen_specific_inventory',
         'closest_prior': [{'rid': 'eo2_op60_r54weave_gem_r1', 'problem_index': 2}],
         'distinction': '旧项指S05外部被看见与音乐抽空/孤立听感错位；新项指同一故事从克制到自然流露的前后因果桥。位置相邻或同一段不能证明同一问题。保留直接盲比中认为S04未说尽可铺垫S05自然流露的相反读法，不以多数票改新项等级。',
         'history_boundary': 'R52/R53含义一致性和R55修订/回补已有失败，不能自动当本问题已解决；顾问必须查旧完整prompt和实际结果，避免重买同义方案。'},
        {'rid': 'eo2_i14r60_op60_r54weave_g56_r2', 'problem_index': 2,
         'finding': 'S06-B1纯净、初恋般新鲜感缺少相近处境；与同项S06-B4感官沉醉分开记录。',
         'severity': '中等', 'status': 'new_specific_subfinding_relative_to_frozen_inventory_with_related_failed_trial',
         'closest_prior': [{'rid': 'eo2_op60_r54weave_g6_r2', 'problem_index': 2}],
         'distinction': '旧项明确B4/S07身体性沉醉不足，没有明确B1纯净新鲜感；不能只按覆盖大类合并。B4旧问题与本项原中等评级都保留。',
         'history_boundary': 'R59tracebound覆盖与原作者最后反馈已涉及B1纯净缺口并因固定P1事实不足放弃；新颖性不是未试机制证据，不再自动购买同一A4措辞修补。'}]
    for item in new:
        d = B.V.parse(item['rid'])['problems'][item['problem_index']]
        assert d['severity'] == item['severity']
        item['raw_problem'] = d
    observations = [
        {'rid': 'eo2_i14r60_op61_r54weave_g56_r1', 'problem_index': 0,
         'finding': 'S06暖意→S08回忆安慰和现实无依靠重复，后接S09/S10没答案重复。',
         'prior_exact_context': [{'rid': 'eo2_op61_r54weave_g6_r1', 'field': 'minor'},
                                 {'rid': 'eo2_op61_r54weave_gem_r1', 'problem_index': 3},
                                 {'rid': 'eo2_op61_r54weave_g56_r2', 'problem_index': 1}],
         'disposition': '旧完整minor已明确S06和S08短暂安慰复现并认为必要；新评委判中等且Gem新组亦判S08重复中等。保留具体分歧，不称已解决；本次已有明确新增项，毋须靠这一争议判收敛。'},
        {'rid': 'eo2_i14r60_op60_r54weave_g6_r2', 'problem_index': 1,
         'finding': 'S07可能需要陪伴→S12也许让对方安心的动机跳跃。',
         'prior_exact_context': [{'rid': 'eo2_op60_r54weave_g56_r1', 'field': 'minor'}],
         'disposition': '旧minor已逐句指出S12想到让对方安心稍跳一步、认为尚可读通；新项评级中等，与同一新组G56r2轻微原样并列，不降级或假称新事实。'}]
    assessment = {'status': 'not_converged_new_medium_findings', 'tag': I.TAG,
        'assessed_at': datetime.now(ZoneInfo('America/New_York')).isoformat(),
        'scope_sha256': B.digest((I.FOLDER / 'audit_scope.json').read_text(encoding='utf-8')),
        'fresh_group_complete': True, 'all_ten_full_read_and_exact_input_bound': True,
        'all_original_parents_terminal': True, 'review_rows': rows,
        'at_least_two_consecutive_zero_acceptance_rounds': scope['failed_rounds'],
        'new_medium_findings': new, 'specific_dissent_observations': observations,
        'remaining_findings': '完整原文保留；本次以具体新增中等项即足以否定I14，不宣称其余每一子项都已完成旧项匹配。',
        'next': 'I02 multi-adviser diagnosis with complete fresh group and failed prompts/outcomes. No altered standards or product edits. Do not repeat unchanged I01 merely to obtain a favorable result.',
        'zip': 'frozen by user; no change'}
    B.write_frozen(I.FOLDER / 'assessment.json', B.json_text(assessment))
    B.write_frozen(I.FOLDER / 'fresh_open_reviews_full.md', '\n'.join(full))
    print(B.json_text({'status': assessment['status'], 'reviews': len(rows),
                       'medium_or_higher_instances': sum(r['medium_or_higher'] for r in rows),
                       'explicit_new_records': len(new)}))


if __name__ == '__main__':
    build()
