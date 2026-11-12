"""I02 diagnosis of a disputed new subfinding, with original standards intact."""
import argparse
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
os.environ.setdefault('JV', '2')
os.environ.setdefault('THREAD_ROUTE', 'gpt3s')
import experiment_batch as B
import collect_i14_after_r62 as I
import round54_advisors as receiver

ROOT = B.ROOT / 'runs/_batches/round64_diagnosis'


def prepare():
    I.validate_scope()
    assessment = json.loads((I.FOLDER / 'assessment.json').read_text(encoding='utf-8'))
    assert assessment['status'] == 'not_proven_unmatched_medium_subfinding'
    source = json.loads((B.ROOT / 'runs/_batches/round61_new_findings/materials.json').read_text(encoding='utf-8'))
    # r49b is the final report reference, not the objective for new proposals.
    material = {k: v for k, v in source.items() if k not in (
        'actual_direct_fixed_start_comparison', 'fresh_current_reviews', 'fresh_I14_assessment')}
    material.update({
        'standard': (B.ROOT / '标准.md').read_text(encoding='utf-8'),
        'rules': (B.ROOT / '迭代准则.md').read_text(encoding='utf-8'),
        'dag': (B.ROOT / 'DAG.md').read_text(encoding='utf-8'),
        'history': (B.ROOT / '试验记录.md').read_text(encoding='utf-8'),
        'latest_assessment': assessment,
        'all_prior_current_review_raw': [{'rid': r['rid'], 'raw': B.evo.output(r['rid'])} for r in I.validate_scope()['prior_issue_sources']],
        'fresh_current_reviews': [],
        'recent_trial_records': {},
        'latest_advisers': []})
    for row in assessment['review_rows']:
        rid = row['rid']
        assert B.reviewed(rid) and B.digest(B.evo.output(rid)) == row['output_sha256']
        material['fresh_current_reviews'].append({'rid': rid, 'raw': B.evo.output(rid)})
    for rid in ('r61_advisor_g6a', 'r61_advisor_g6b', 'r61_advisor_g56'):
        assert B.reviewed(rid)
        material['latest_advisers'].append({'rid': rid, 'raw': B.evo.output(rid)})
    for folder, names in {
        'round61_boundary': ['candidates.json', 'production_verified.json', 'r61bridge_final_disposition.json'],
        'round62_sample_checkpoint': ['placement_audit.json', 'r54sample_quick.json', 'r54sample_final_disposition.json'],
    }.items():
        for name in names:
            p = B.ROOT / 'runs/_batches' / folder / name
            material['recent_trial_records'][str(p.relative_to(B.ROOT))] = json.loads(p.read_text(encoding='utf-8'))
    for work in B.F.WORKS:
        assert material['current_products'][work]['line'] == B.V.view(B.V.graph_of(work, 'r54weave'), ids=True)
        assert material['current_products'][work]['fixed_beads'] == B.V.beads(work)
    B.write_frozen(ROOT / 'materials.json', B.json_text(material))
    tasks = []
    for judge, count, lens in (
        ('g6a', 4, '先核对新S11疼痛原因意见是否忽略同段上一条，区分真实覆盖缺口与要求每条重复覆盖；再看有无通用的组织机制。'),
        ('g6b', 3, '独立从原四步分工和因果结构诊断，允许删层、合层、重构，不默认再做局部换词；查全历史避免重试已否定方向。'),
        ('g56', 3, '独立审查意见和反证，特别是同段多种体验共存与保护已验收支点；没有新可行动机制就明确放弃，不为凑数写方案。'),
    ):
        msg = f'''你是音乐文字流程顾问。当前唯一已验收主线r54weave；新候选正式验收必须对它，接纳后随主线推进，r49b只用于最终报告。
本次I01十份完整返回，一条中等子意见在冻结旧意见中未找到精确机制匹配，但成立性存在反证，执行者暂记未证明收敛，没有把它认定成必须修的新事实。请从头完整读材料，先判断此意见究竟指出真实未满足标准的地方，还是忽略完整同段/把个人偏好加成用户标准。不可把顾问多数票、评委分数或执行者判断当新标准。原评级、反证和分歧都保留。
{lens}
标准要求同段能找到情境相近原因、大体覆盖，允许几种体验并存，不要求每条覆盖全段，也不强制崇高、身体性、线性解决。不能把“原文已写过但新评委忽略”作为补写重复的理由。canonical固定珠子与交付N03i措辞的范围问题另存，不改珠子。
请诊断实际哪层哪句造成哪些仍可行动的问题，最多给{count}套有实质区别且历史未试过的可运行机制；不为凑10套重提同义方案。可以明确decline，不能为了给答案重做R55整体修订/R57锚点删句/R58保支点重建/R59目标耦合及顺序翻转/R61表达状态桥接/R62已实际失败的两次抽样择一。若新提案与这些有本质区别，请写出可检验的差别。
遵守标准和六项硬约束：泛化、模型全部生产、构思不看珠子、珠子/Center/分段不改、允许联网、双曲同一通用prompt。每段2–4条每条一句，引用真实先前条目，原三类关系。可删层/并层/重写，优先单层，需上游明确依赖。不可用固定珠子反向编造经历、添加身体动作物件前史，不额外买审稿步骤，不改变原GPT6/High生产及评审门槛。
接口：写后{{SECTIONS}}/{{CENTER}}/{{LINE}}/{{BEADS}}/{{REVIEWS}}；A4 {{SECTIONS}}/{{CENTER}}/{{ROUTES}}/{{TARGETS}}；无珠子构思步骤可用{{SECTIONS}}/{{CENTER}}/{{LINE}}，不得含BEADS/TARGETS/REVIEWS。新增步骤列清下游输入和完整JSON输出；现有segments[sec,relation,items[id,text,cite]]或edits[op,id,text]均可；空edits应允许。通用prompt不写具体作品例子/眼前某段特例。
仅输出JSON：{{"diagnosis":"先判争议意见成立性，再列实际可行动缺点、责任层、历史和边界","candidates":[{{"name":"英文短名","hypothesis":"独立机制与可检验收益代价","changed_layer":"A4/postwrite/upstream","reuse":"可复用真实输入","steps":[{{"id":"step_id","inputs":["占位符名"],"prompt":"完整通用prompt含输出JSON格式"}}],"risk":"失败方式及与具体旧机制的差别"}}],"declined_directions":[{{"direction":"方向","reason":"依据与反证"}}]}}。
【完整材料】
''' + B.json_text(material)
        rid = 'r64_advisor_' + judge
        B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', msg)
        tasks.append({'rid': rid, 'model': 'g56' if judge == 'g56' else 'g6', 'count': count, 'input_sha256': B.digest(msg)})
    B.write_frozen(ROOT / 'advisors.json', B.json_text({'base': 'r54weave', 'tasks': tasks, 'workers': 3,
        'frozen_at': datetime.now(ZoneInfo('America/New_York')).isoformat(), 'materials_sha256': B.digest(B.json_text(material))}))
    print(B.json_text({'prepared': 3, 'max_plans': 10, 'material_chars': len(B.json_text(material)), 'calls': 0}))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('prepare', 'collect'))
    args = p.parse_args()
    if args.action == 'prepare':
        prepare()
    else:
        receiver.ROOT = ROOT
        receiver.collect()
