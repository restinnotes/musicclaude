"""Original-author interface clarification only; no production prose edits."""
import os
os.environ['THREAD_ROUTE'] = 'gpt3s'
import experiment_batch as B
import round54_candidates as R

RID = 'r58trace_feedback_g56_interface_v2'

def prepare():
    original = 'r58trace_feedback_g56_v2'
    assert B.reviewed(original)
    warnings = {w: R.parsed(f'scr58trace_{w}_P1')['source_warnings'] for w in B.F.WORKS}
    message = ('你是刚才RecurrenceTrace_EvidenceBoundA4的原提出者。这里仅做投产前接口核对，不进行第二次质量退回；'
               'P1、成品、评审、标准和原修订方向都不变，不重新构思故事。你要求读取每条source_warning的handling并严格执行，'
               '但真实P1输出并不保证这个字段存在，部分只有location、source_item_ids、issue。'
               '请只修正这一处通用输入兼容性：缺少handling时如何依据实际已有字段遵守来源限制，'
               '不得推断或补造不存在的处理指令、心理事实，不要求改动既有P1 JSON。'
               '如原提示词已经兼容，也请明确说明。请返回完整可直接使用的通用A4提示词，'
               '其余机制、占位符、四步语义、2–4条每条一句、三标签与原JSON接口保持不变。'
               '不要加入具体作品或当前段落例子。只输出JSON：'
               '{"decision":"interface_corrected/unchanged","reason":"说明","prompt":"完整通用A4提示词"}。'
               '\n【原完整修订答复】\n' + B.evo.output(original)
               + '\n【两份真实P1来源警告，仅用于核对字段，不得写入通用提示词】\n' + B.json_text(warnings))
    B.write_frozen(B.evo.RUNS / RID / 'prepared_input.txt', message)
    B.write_frozen(B.ROOT / 'runs/_batches/round58_upstream/r58trace_interface_manifest.json', B.json_text({
        'rid': RID, 'original_author': 'r55_advisor_g56', 'quality_attempt': 2,
        'purpose': 'pre-production optional-field compatibility; unchanged P1 and quality hypothesis',
        'input_sha256': B.digest(message), 'original_feedback_sha256': B.digest(B.evo.output(original))}))
    return message

if __name__ == '__main__':
    msg = prepare()
    B.F.configure()
    if not B.evo.done(RID):
        B.evo.call(RID, msg, model=B.V.JUDGES['g56'], meta={'stage':'r59-interface-only', 'web':True})
    print(B.json_text({'rid':RID, 'complete':B.evo.done(RID), 'read_required':True}), flush=True)
