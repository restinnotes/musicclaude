"""Freeze next I02 evidence, explicitly retaining any original screen still pending."""
import json
from pathlib import Path

import experiment_batch as B


def read_bound(rid):
    receipt = json.loads((B.evo.RUNS / rid / 'inspection.json').read_text(encoding='utf-8'))
    if not receipt.get('read_complete') or receipt.get('output_sha256') != B.digest(B.evo.output(rid)):
        raise ValueError(f'{rid}: complete bound read required before freezing')
    return B.V.parse(rid)


def prepare():
    name = 'round30_forward'
    evidence = {}
    for tag in ('round29_controlc01', 'round29_g6c01', 'round29_g6c02'):
        state = B.F.blind_state(tag, 'qurefs')
        if state['status'] not in ('reject', 'pending'):
            raise ValueError(f'{tag}: a survivor requires acceptance; invalid evidence must be resolved')
        evidence[tag] = {
            'state': state,
            'full_completed_reviews': {row['rid']: read_bound(row['rid']) for row in state['rows']},
            'prompts': B.pipe.load_spec(B.ROOT / 'schemes' / f'{tag}.json')['_texts'],
            'outputs': {w: {s: B.V.parse(f'sc{tag}_{w}_{s}') for s in ('A1', 'A2', 'A3', 'A4')}
                        for w in B.F.WORKS},
        }
    rejected = {}
    for tag, folder, result in (
        ('round29_g56c01', 'round29_g56_a1', 'hard_constraint_results.json'),
        ('round29_g56c02', 'round29_g56', 'selection_stop.json'),
    ):
        rejected[tag] = {
            'reason': json.loads((B.ROOT / 'runs' / '_batches' / folder / result).read_text(encoding='utf-8')),
            'prompts': B.pipe.load_spec(B.ROOT / 'schemes' / f'{tag}.json')['_texts'],
            'outputs': {},
        }
        for w in B.F.WORKS:
            rid = f'sc{tag}_{w}_' + ('A4' if tag.endswith('c01') else 'A2')
            rejected[tag]['outputs'][w] = read_bound(rid)
    audit = B.ROOT / 'runs' / '_batches' / 'i14_novelty_20261102'
    group = json.loads((audit / 'current_group_complete.json').read_text(encoding='utf-8'))
    current_open = {row['rid']: read_bound(row['rid']) for row in group['review_slots']}
    if len(current_open) != 10:
        raise ValueError('both complete five-review groups are required')
    rules = (B.ROOT / '迭代准则.md').read_text(encoding='utf-8')
    material = {
        'standard': (B.ROOT / '标准.md').read_text(encoding='utf-8'),
        'hard_constraints': rules[rules.index('## 二、迭代范围和硬约束'):rules.index('## 三、流程')],
        'history': (B.ROOT / '试验记录.md').read_text(encoding='utf-8'),
        'user_judgments': (B.ROOT / '用户判定.md').read_text(encoding='utf-8'),
        'mainline': {w: B.V.view(B.V.graph_of(w, 'qurefs'), center=True) for w in B.F.WORKS},
        'mainline_prompts': B.pipe.load_spec(B.ROOT / 'schemes' / 'Q15.json')['_texts'],
        'lawful_base': B.pipe.load_spec(B.ROOT / 'schemes' / 'round29_controlc01.json'),
        'round28_summary': json.loads((B.ROOT / 'runs/_batches/round28_cross_more/completed_round_summary.json').read_text(encoding='utf-8')),
        'round29_measured': evidence,
        'round29_other_terminal_cases': rejected,
        'all_current_open_reviews': current_open,
        'i14_assessment': json.loads((audit / 'assessment.json').read_text(encoding='utf-8')),
        'rejected_gem_prompts': B.V.parse('batch_round29_layers_advisor_gem'),
        'executor_limits': 'A blind preference for old invented relationship facts does not authorize those facts. '
                           'Any pending screen above is genuinely undecided; its missing votes are not zero. '
                           'The original parent continues collecting it, and any survivor takes priority for acceptance. '
                           'This next independent advisory batch is planning in parallel, not declaring that screen failed. '
                           'A2 can reject supplied routes but cannot author missing experience. Sparse phases and '
                           'more detailed causal metadata have not yet produced a measured improvement. '
                           'Repeated findings are not fixes, and severity disagreement is not permission to erase an issue.',
    }
    # Expanded source spec contains pathlib/private cache fields; serialize only the public spec and prompt texts.
    spec = material.pop('lawful_base')
    material['lawful_base'] = {k: v for k, v in spec.items() if not k.startswith('_')}
    material['lawful_base_prompts'] = spec['_texts']
    prefix = (
        '你是下一轮I02独立顾问。完整阅读标准、硬约束、双曲实际产物与全部完整评审后，'
        '材料若有pending候选，未决结果不得猜作失败；原父继续收取，幸存者优先验收。'
        '提出最多{COUNT}套机制确实不同、可独立证伪的完整通用提示词方案。'
        '优先每套只改A1/A2/A3/A4中的一层，固定另三层；不强迫继续上一轮两种上游机制。'
        '先诊断哪些具体任务定义造成哪些可观察的问题、哪些只是猜测；若一层不足则说明，不能许诺会过。'
        '四步职责和顺序保持：A1不看珠子构思本人经历，A2不看珠子诊断选路、不改稿，'
        'A3从固定珠子提取性质、不构思故事，A4综合并一次产出最终分段要点。'
        '保留原层占位符及JSON输入输出语义、Center/分段/珠子、生产模型/强度/联网权限。'
        'A2若prompt含{ROUTES}，注明append为空；其他append机制不暗改。'
        '不在通用prompt放当前作品、当前情节或当前段落的示例和专用补丁；'
        '不得强制所有作品按同样数量的转折、不可逆成长或情感曲线行进。'
        '形态始终每段2–4条、每条一句，引用与三个关系标签保持，不机械禁词。'
        '不得新增外部事件/前史/对白/物件/他人反应/隐秘事实推动发展，'
        '人物自己的选择、期待与切身承受可以成为经历；也不能缩成抽象原则证明和心理管理循环。'
        '请正面重构生成、信息使用或选路机制，不只是堆禁令或改名。'
        '对照已试历史逐案说明差异，复用旧机制的同义方案不交；无独立方案可少交，不能凑数。'
        '不要直接修改现有成品。仅输出JSON：'
        '{"analysis":"有证据的诊断、限制和不确定性","candidates":['
        '{"layer":"A1/A2/A3/A4","hypothesis":"机制、历史区别和证伪预期",'
        '"prompt":"完整可运行原文","risk":"风险、占位符/append与原另外三层兼容性"}]}。\n【完整材料】\n'
    )
    tasks = []
    for judge, count in (('g6', 4), ('g56', 3), ('gem', 3)):
        rid = f'batch_{name}_advisor_{judge}'
        message = prefix.replace('{COUNT}', str(count)) + B.json_text(material)
        B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', message)
        tasks.append({'run_id': rid, 'judge': judge, 'requested': count, 'sha256': B.digest(message)})
    manifest = {'name': name, 'base': 'qurefs', 'scheme': 'schemes/round29_controlc01.json',
                'count': 10, 'source_tags': ['r27p2', 'qu', 'round29_controlc01'],
                'workers': 4, 'advisors': tasks, 'scheme_sha256': B.spec_hash(spec)}
    target = B.ROOT / 'runs' / '_batches' / name / 'advisors.json'
    B.write_frozen(target, B.json_text(manifest))
    print(B.json_text({'path': str(target), 'material_chars': len(B.json_text(material)), 'new_model_calls': 0}))


if __name__ == '__main__':
    prepare()
