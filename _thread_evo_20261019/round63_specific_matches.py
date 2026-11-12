"""Specific executor matches, preserving original findings and severity."""
import json
import experiment_batch as B
import collect_i14_after_r62 as I

scope = I.validate_scope()
assessment = json.loads((I.FOLDER / 'assessment.json').read_text(encoding='utf-8'))
prior = {(p['rid'], p['problem_index']): p for p in scope['prior_issues']}

def rid(work, judge, repeat=1, cycle='fresh'):
    prefix = {'fresh': 'eo2_i14r63_', 'old': 'eo2_', 'r60': 'eo2_i14r60_'}[cycle]
    return f'{prefix}{work}_r54weave_{judge}_r{repeat}'

def old(work, judge, index, repeat=1, cycle='old'):
    return (rid(work, judge, repeat, cycle), index)

matches = []
def match(work, judge, repeat, index, refs, explanation):
    r = rid(work, judge, repeat)
    p = B.V.parse(r)['problems'][index]
    assert p['severity'] in ('中等', '严重')
    sources = [prior[ref] for ref in refs]
    assert sources and all(s['work'] == work for s in sources)
    matches.append({'rid': r, 'problem_index': index, 'original': p,
                    'classification': 'specific_known_finding_unresolved',
                    'prior_exact_items': sources, 'executor_reason': explanation,
                    'severity_policy': 'Original old and fresh ratings preserved independently; a higher fresh rating does not erase a prior specific observation, and no majority vote resolves dissent.'})

repeat_expression = [old('op60', 'g56', 0, 2)]
analysis = [old('op60', 'g56', 2, 2), old('op60', 'g56', 3)]
for judge, repeat, index in [('g6', 1, 0), ('g56', 1, 0), ('gem', 1, 4), ('g6', 2, 0)]:
    match('op60', judge, repeat, index, repeat_expression,
          '同一S02-2与S04-2/3想多说、怕破坏自在、收住的连续重复；新初段范围包含S01起点，并未增加新的断裂机制。原先也明确缺少比上次走远的结果。')
for judge, repeat, index in [('g6', 1, 2), ('g56', 1, 4), ('g6', 2, 3), ('g56', 2, 2)]:
    match('op60', judge, repeat, index, analysis + [old('op60', 'g6', 2, cycle='r60')],
          '同一S07不是自己一个人在需要、S09亲近未因担忧变假、S11不能替对方决定、S12给的好/留不住以后等抽象心理归纳；各新引文对应原具体句，不只按分析腔大类。')
match('op60', 'g56', 1, 1,
      [old('op60', 'g6', 1), old('op60', 'g6', 1, 2, 'r60')],
      '复合意见逐项对应：S07-3已经盼以后陪伴而S11-1重新发现，旧g6第1项轻微已有；S12-1让对方安心却无对方不安依据、从互需跳到单方奉献，R60g6r2第1项中等原文已精确指出。两处原评级均保留。')
match('op60', 'g56', 2, 1,
      [old('op60', 'g6', 1), old('op60', 'g56', 0, 2, 'r60')],
      'S07-3→S11-1长久陪伴重作发现的精确旧项，加R60g56r2第0项所列S12多陪/用心不能留未来的再次重述；不是把不同阶段全部认作重复。')
match('op60', 'g6', 2, 1, [old('op60', 'g56', 0, 2, 'r60')],
      'S02舍不得好时光、S04留住好时光、S08未来不准、S11对方未必如此、S12留不住以后、S13索保证到S14放下，原完整链位置和机制相同。')
match('op60', 'gem', 1, 0,
      [old('op60', 'gem', 1, cycle='r60'), old('op60', 'gem', 1), old('op60', 'g56', 0, 2)],
      'S11/12刚不躲藏而S13再撤回、最后S14再不隐藏：旧Gem S13项已指出推翻S11/12积累，R60第1项已指出完整自我和解后循环，旧g56第0项指出前半同一克制。保留新严重与其他评委认可回返有意义的相反判断。')
match('op60', 'gem', 1, 1, [old('op60', 'gem', 1)],
      '同一S13-2往回收喜欢，与固定S13-B1/B3持续推进不让步相反；逐字动作及珠子相同。')
match('op60', 'gem', 1, 2,
      [old('op60', 'gem', 2), old('op60', 'gem', 3, cycle='r60')],
      '两个子项均对应：S05自然曝光与悬空孤立听感不符的旧中等，以及S04未说尽→S05不再藏的无过渡R60新增中等；不能只用前者吞掉后者。')
match('op60', 'gem', 1, 5,
      [old('op60', 'g56', 3), old('op60', 'gem', 3)],
      'S05先前/如今对照、S11并不等于/没法决定、S13解释想收回更难受，旧g56第3项已有各句心理机制归纳，旧Gem第3项包含S11冷静推理。')

middle = [old('op61', 'g6', 0), old('op61', 'gem', 0, cycle='r60')]
for judge, repeat, index in [('g6', 1, 0), ('gem', 1, 0), ('g56', 2, 0)]:
    match('op61', judge, repeat, index, middle,
          '同一S04是否走错、S07早知孤单还走吗、S09到底想要什么、S10回去未必恢复、S11万一能呢的重复回环；旧意见同时承认各步有新认识，认可与否分歧不删。')
match('op61', 'g6', 1, 1, [old('op61', 'g56', 0, cycle='r60')],
      '同一S06-4回忆温暖与S08两条回忆安慰/现实无人陪的完整重复过程，R60精确列出原句及新旧作用。')
match('op61', 'g56', 1, 0,
      [old('op61', 'g6', 1), old('op61', 'g56', 1, 2)],
      'S04未知是否后悔、S09答不上来、S10无答案重复结束各问；原g56r2第1项精确包含全部位置和重复未知机制，评级轻微保留。')
match('op61', 'g6', 2, 1,
      [old('op61', 'g56', 1, 2), old('op61', 'gem', 3)],
      'S09问题后再答不上来、S10再无答案为精确旧项；S09仅两小节却用完整二元解释的体量子项也已在旧Gem第3项明确，不仅是泛泛啰嗦。')
match('op61', 'g56', 2, 1,
      [old('op61', 'g56', 0, 2), old('op61', 'g56', 0, cycle='r60')],
      '三个子项分别对应：S07前两条孤单惧怕重复旧g56r2第0项；S06暖→S08暖及回忆不代现实、S09答不上→S10无答案均R60g56r1第0项精确列出。')
match('op61', 'gem', 1, 1, [old('op61', 'gem', 4)],
      '同一全文亲近/日子/难堪受气委屈的标签词重复；原轻微新严重并存，不用旧低评级覆盖新评级。')
match('op61', 'gem', 1, 2,
      [old('op61', 'gem', 3), old('op61', 'gem', 2, cycle='r60')],
      '同一S09两小节短促惊跳，却铺二元心理归因和无答案的密度/体感不符，旧两份分别在目标2/3已明确全部事实；目标号码改变不创造新机制。')
match('op61', 'gem', 1, 3, [old('op61', 'gem', 1)],
      '同一S13管风琴圣咏/八度强烈能量与日常过日子/静下来不匹配，旧严重意见已含完整高潮及退守生活判断；不引入必须宏大崇高新标准。')
match('op61', 'gem', 1, 4,
      [old('op61', 'gem', 2), old('op61', 'g56', 3, 2)],
      '同一S12冒号并列A真B真、哪样不用硬说假，呈咨询总结/论点提纲腔，旧原句及机制完全对应。')

unresolved = [(rid('op60', 'gem'), 3), (rid('op61', 'g6'), 2)]
expected = {(r['rid'], i) for r in assessment['review_rows']
            for i, p in enumerate(B.V.parse(r['rid'])['problems']) if p['severity'] != '轻微'}
assert len(matches) == 26 and len({(m['rid'], m['problem_index']) for m in matches}) == 26
assert {(m['rid'], m['problem_index']) for m in matches} | set(unresolved) == expected
data = {'tag': I.TAG, 'scope_sha256': assessment['scope_sha256'],
        'classification': 'specific_executor_audit_not_convergence',
        'all_medium_instances': len(expected), 'specific_known_instances': len(matches),
        'matches': matches, 'remaining': [
            {'rid': unresolved[0][0], 'problem_index': 3, 'status': 'disputed_new_specific_pain_cause_claim_I02_in_flight'},
            {'rid': unresolved[1][0], 'problem_index': 2, 'status': 'fixed_bead_editorial_scope_preexists_outside_line_repair'}],
        'minor_findings': [{'rid': r['rid'], 'minor': B.V.parse(r['rid'])['minor'],
                           'light_problems': [p for p in B.V.parse(r['rid'])['problems'] if p['severity'] == '轻微']}
                          for r in assessment['review_rows']],
        'boundary': 'Known means previously specifically recorded, not solved, acceptable or downrated. All fresh raw observations remain immutable; no new review calls made. I14 remains unproven pending the disputed finding and the original I02 tasks.'}
B.write_frozen(I.FOLDER / 'specific_matches.json', B.json_text(data))
print(B.json_text({'medium': len(expected), 'known_specific': len(matches), 'remaining': len(unresolved), 'calls': 0}))
