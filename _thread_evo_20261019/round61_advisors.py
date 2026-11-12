"""I02 after the fresh I14 group found a new concrete medium issue.

Uses complete original sources; preparation makes no calls. No product edits.
"""
import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
os.environ.setdefault('JV', '2')
os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
import experiment_batch as B
import round54_advisors as receiver
import collect_i14_after_r59 as I
import round50_measure as M
import build_version_comparison as comparison

ROOT = B.ROOT / 'runs/_batches/round61_new_findings'


def prepare():
    I.validate_scope()
    complete = json.loads((I.FOLDER / 'collection_result.json').read_text(encoding='utf-8'))
    assert complete['original_receiver_terminal']
    fresh = []
    for row in complete['review_slots']:
        assert row['status'] == 'full_read_required' and B.reviewed(row['rid'])
        assert row['output_sha256'] == B.digest(B.evo.output(row['rid']))
        fresh.append({'rid': row['rid'], 'raw': B.evo.output(row['rid'])})
    assert len(fresh) == 10
    assessment = json.loads((I.FOLDER / 'assessment.json').read_text(encoding='utf-8'))
    assert assessment['status'] == 'not_converged_new_medium_findings'
    old = json.loads((B.ROOT / 'runs/_batches/round55_current/materials.json').read_text(encoding='utf-8'))
    keys = ['four_step_prompts', 'accepted_revision_prompts', 'accepted_global_reweave_prompt',
            'upstream_outputs', 'current_products', 'current_open_reviews', 'scope_audit',
            'tested_broader_prompt_mechanisms', 'parent_comparison_raw', 'current_acceptance']
    material = {k: old[k] for k in keys}
    material.update({
        'standard': (B.ROOT / '标准.md').read_text(encoding='utf-8'),
        'rules': (B.ROOT / '迭代准则.md').read_text(encoding='utf-8'),
        'dag': (B.ROOT / 'DAG.md').read_text(encoding='utf-8'),
        'history': (B.ROOT / '试验记录.md').read_text(encoding='utf-8'),
        'user_judgments': (B.ROOT / '用户判定.md').read_text(encoding='utf-8'),
        'fresh_current_reviews': fresh,
        'fresh_I14_assessment': assessment,
        'later_actual_mechanisms': []})
    measured = comparison.comparison('r54weave', 'r49b')
    assert len(measured['rows']) == 8 and not measured['pending']
    material['actual_direct_fixed_start_comparison'] = {
        'summary': measured,
        'fixed_start_products': {w: B.V.view(B.V.graph_of(w, 'r49b'), ids=True) for w in B.F.WORKS},
        'complete_raw_balanced8': [{'rid': rid, 'X_version': 'r54weave' if rid.endswith('_newX') else 'r49b',
                                  'Y_version': 'r49b' if rid.endswith('_newX') else 'r54weave',
                                  'raw': B.evo.output(rid)} for rid, _, _ in M.jobs('fair', 'r54weave', 'r49b')],
        'boundary': '实际对r49b重新测的8票，不能累计父票或当它对父版的验收；保留原相互需要/安心等损失争议，不把旧版更高确信度自动认作事实。新候选实际验收基准仍r54weave。'}
    # Current products and upstream are byte-for-byte the existing mainline.
    for w in B.F.WORKS:
        assert material['current_products'][w]['line'] == B.V.view(B.V.graph_of(w, 'r54weave'), ids=True)
        assert material['current_products'][w]['fixed_beads'] == B.V.beads(w)
        for step, raw in material['upstream_outputs'][w].items():
            assert raw == B.evo.output(f'scqu_{w}_{step}')
    for batch in ('round55_current', 'round56_paired', 'round57_a4_checkpoint',
                  'round58_upstream', 'round59_trace_repair', 'round59_target_coupling', 'round59_a4_order'):
        folder = B.ROOT / 'runs/_batches' / batch
        manifest = json.loads((folder / 'candidates.json').read_text(encoding='utf-8'))
        for c in manifest['candidates']:
            entry = dict(c)
            entry['base'] = manifest['base']
            entry['full_prompts'] = []
            for step in c['steps']:
                text = (B.ROOT / step['path']).read_text(encoding='utf-8')
                assert B.digest(text) == step['sha256']
                entry['full_prompts'].append(text)
            if c.get('feedback_continuation'):
                step = c['feedback_continuation']['step']
                text = (B.ROOT / step['path']).read_text(encoding='utf-8')
                assert B.digest(text) == step['sha256']
                entry['continuation_full_prompt'] = text
            entry['dispositions'] = {p.name: json.loads(p.read_text(encoding='utf-8'))
                                     for p in folder.glob(c['tag'] + '*disposition.json')}
            material['later_actual_mechanisms'].append(entry)
    for path in (B.ROOT / 'runs/_batches/round55_current/r55restored_final_disposition.json',
                 B.ROOT / 'runs/_batches/round50_from_r49b/r55restored_manifest.json'):
        material[path.name] = json.loads(path.read_text(encoding='utf-8'))
    B.write_frozen(ROOT / 'materials.json', B.json_text(material))
    tasks = []
    for judge, count, lens in (
        ('g6a', 4, '重点诊断承接前一状态的真实心理过渡、未发生与已发生的边界，能否在不添经历事实下修好。'),
        ('g6b', 3, '独立判断复现的经历在各段到底有何新作用，是否有历史尚未测试的因果组织机制。'),
        ('g56', 3, '独立判断新问题是否确有可行动空间；保护已验收支点，寻找不同于整体重写、锚点保护和回补的办法。')):
        message = f'''你是音乐文字生产流程顾问。当前唯一已验收主线r54weave，未收敛。原I14新的一组评审出现具体新增中等意见，不能把它按“分析腔/重复”大类吞掉。请完整读材料，诊断问题是否成立、哪层哪句造成、历史实际试过什么；提出最多{count}套彼此有实际机制区别且未被历史否定的可运行方案。
{lens}
不为凑10套重提同义方案；若这些问题在固定事实与用户标准下没有可证实的新改法，可以明确说明放弃某一方向。评委意见与执行者的新颖性判断是证据，不能当新增用户标准；必须保留分歧，不照抄新增身体/外部事件、改珠子、改Center/分段、强制崇高等建议。过去某方案过qu检查点不等于胜当前r54weave；no_regress和其他原门槛不变。
可删层、并层、整层改写或保留主线作写后修订；优先只改一层，确有上游依赖则说清。构思新经历时不得看珠子，珠子最早综合时才允许进入；不得用听感反向编造成品经历。两曲同一套通用prompt，每段2–4条，每条一句完整自然话，引用真实先前条目，关系只有原三类。成品全部模型产出，无执行者手写句子。生产GPT6/High、联网、判定线不变。通用prompt不得放具体作品或该段特例。
接口可用写后{{SECTIONS}}/{{CENTER}}/{{LINE}}/{{BEADS}}/{{REVIEWS}}，或A4{{SECTIONS}}/{{CENTER}}/{{ROUTES}}/{{TARGETS}}；无珠子构思步骤可用{{SECTIONS}}/{{CENTER}}/{{LINE}}但不能含BEADS/TARGETS/REVIEWS。新增步骤输出必须完整说明下游输入，不能靠执行者补写。每方案附完整通用prompt和输出JSON格式，可为现有segments[sec,relation,items[id,text,cite]]或edits[op,id,text]替换/删除，不要只给方向或另加付费审稿层。
只输出JSON：{{"diagnosis":"具体问题、原因、历史与边界","candidates":[{{"name":"英文短名","hypothesis":"独立机制、收益和代价","changed_layer":"A4/postwrite/upstream","reuse":"真实可复用输入","steps":[{{"id":"step_id","inputs":["占位符名"],"prompt":"完整通用prompt含输出格式"}}],"risk":"失败方式及与旧失败的实际差别"}}],"declined_directions":[{{"direction":"方向","reason":"依据"}}]}}。
【完整材料】
''' + B.json_text(material)
        rid = 'r61_advisor_' + judge
        B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', message)
        tasks.append({'rid': rid, 'model': 'g56' if judge == 'g56' else 'g6',
                      'count': count, 'input_sha256': B.digest(message)})
    B.write_frozen(ROOT / 'advisors.json', B.json_text({'base': 'r54weave', 'tasks': tasks,
        'workers': 3, 'materials_sha256': B.digest(B.json_text(material)),
        'frozen_at': datetime.now(ZoneInfo('America/New_York')).isoformat()}))
    print(B.json_text({'prepared': 3, 'max_plans': 10, 'material_chars': len(B.json_text(material)), 'calls': 0}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare', 'collect'))
    a = p.parse_args()
    if a.action == 'prepare':
        prepare()
    else:
        receiver.ROOT = ROOT
        receiver.collect()
