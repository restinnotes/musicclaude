"""Freeze I02 material for independent A1-only / A2-only proposals; no calls."""
import json
import experiment_batch as B


def prepare():
    name = 'round29_layers'
    spec = B.pipe.load_spec(B.ROOT / 'schemes' / 'R27P2.json')
    rules = (B.ROOT / '迭代准则.md').read_text(encoding='utf-8')
    limits = rules[rules.index('## 二、迭代范围和硬约束'):rules.index('## 三、流程')]
    tags = ['round28_crossc01', 'round28_crossc02'] + [f'round28_cross_morec{i:02d}' for i in range(1, 5)]
    evidence = {}
    for tag in tags:
        state = B.F.blind_state(tag, 'qurefs')
        if state['status'] not in ('reject', 'pass'):
            raise ValueError(f'{tag}: wait for existing blind parent, do not freeze an incomplete round')
        reviews = {}
        for row in state['rows']:
            rid = row['rid']
            receipt = B.evo.RUNS / rid / 'inspection.json'
            if not receipt.exists():
                raise ValueError(f'{rid}: full executor read receipt missing')
            read = json.loads(receipt.read_text(encoding='utf-8'))
            if not read.get('read_complete') or read.get('output_sha256') != B.digest(B.evo.output(rid)):
                raise ValueError(f'{rid}: unbound read receipt')
            reviews[rid] = B.V.parse(rid)
        evidence[tag] = {
            'state': state, 'full_completed_reviews': reviews,
            'prompts': B.pipe.load_spec(B.ROOT / 'schemes' / f'{tag}.json')['_texts'],
            'products': {w: B.V.view(B.V.graph_of(w, tag), center=True) for w in B.F.WORKS},
        }
    open_reviews = {}
    for w in B.F.WORKS:
        for j, k in (('g6', 2 if w == 'op60' else 1), ('g56', 1)):
            rid = f'eo2_{w}_qurefs_{j}_r{k}'
            if not B.evo.done(rid):
                raise ValueError(f'{rid}: existing I01 parent still owns result')
            read = json.loads((B.evo.RUNS / rid / 'inspection.json').read_text(encoding='utf-8'))
            if not read.get('read_complete') or read.get('output_sha256') != B.digest(B.evo.output(rid)):
                raise ValueError(f'{rid}: read before including as reviewed evidence')
            open_reviews[rid] = B.V.parse(rid)
    material = {
        'standard': (B.ROOT / '标准.md').read_text(encoding='utf-8'),
        'hard_constraints': limits,
        'history': (B.ROOT / '试验记录.md').read_text(encoding='utf-8'),
        'user_judgments': (B.ROOT / '用户判定.md').read_text(encoding='utf-8'),
        'current_mainline': {w: B.V.view(B.V.graph_of(w, 'qurefs'), center=True) for w in B.F.WORKS},
        'mainline_prompts': B.pipe.load_spec(B.ROOT / 'schemes' / 'Q15.json')['_texts'],
        'lawful_upstream_prompts': spec['_texts'],
        'lawful_upstream_outputs': {w: {s: B.V.parse(f'scr27p2_{w}_{s}') for s in ('A1', 'A2')} for w in B.F.WORKS},
        'open_reviews': open_reviews,
        'round28': evidence,
        'fixed_writer': B.pipe.load_spec(B.ROOT / 'schemes' / 'Q15.json')['_texts']['Q15_A4.txt'],
        'executor_findings': (
            'Q1 original upstream produced concrete but unsupported external premises in all four paired A4 candidates; '
            'R27P2 upstream removed those premises in all six paired writer crosses, yet independent blind reviews still prefer qu. '
            'This supports investigating upstream alternatives; it is not a controlled quantitative proof that upstream alone causes the quality loss. '
            'R27P2 A2 already flags Op60 R1 P2/P3 near-duplicate and Op61 abstract action criteria, but retains them. '
            'We must improve lawful inner experience without restoring invented external facts. '
            'A review praising unsupported old events does not authorize them. Suggestions to rename labels or add other-person responses do not change the standard.'
        ),
    }
    request = (
        '你是I02新一轮的独立顾问。读完标准、硬约束、实际上游、六套交叉成品及全部已完成正式理由后，'
        '给两套实质不同的完整提示词：第一套只改A1，第二套只改A2。两套各自独立试，不合并、不同时动写线。'
        '我们固定生产模型/强度/联网、四步顺序、Center、分段、珠子、A3，并固定同一Q15 A4作共同写线层。'
        '基底是R27P2的A1和A2；A1-only须与原R27P2 A2及Q15 A4兼容；A2-only须能选择现有R27P2 A1路线并与Q15 A4兼容。'
        '只改A1时保持原占位符{NAME}/{SECTIONS}/{CENTER}/{K}及center_input/routes/stakes/phases输出语义；'
        '只改A2时保留追加{ROUTES}机制及routes/selected接口，仍只能诊断选路，不能改稿或补写故事。'
        '正面重构生成或选择机制，不只增加禁令、换词、强制转折数、把已有phase/stake改名。'
        '已有顾问多种A4手段已测，不能把它们冒充新上游假设；两位顾问可能独立想到同案，会查重，不必凑数。'
        '不要强制机械情感映射，不做作品专用补丁，提示词里不得出现这两首作品或情节示例。'
        '事实边界仍严格：构思不看珠子，不新增外部事件/背景/对白/物件/他人反应或隐秘事实驱动发展，'
        '也不因禁止外部事实就把人的经历缩成抽象价值证明或反复调节心情。'
        '要检查提出的办法究竟有现有输出和评审支持，还是仅假说；不能许诺会过线。'
        '可以认为某层不适合再试，并说明理由而少交方案；不为凑数写同义版本。'
        '只输出JSON：{"analysis":"逐条有据的诊断、层间限制和仍不确定之处",'
        '"candidates":[{"layer":"A1或A2","hypothesis":"独立机制和可证伪预期",'
        '"prompt":"完整通用提示词原文", "risk":"风险与兼容性说明"}]}。\n【完整材料】\n'
    ) + B.json_text(material)
    tasks = []
    for judge in ('g6', 'g56', 'gem'):
        rid = f'batch_{name}_advisor_{judge}'
        B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', request)
        tasks.append({'run_id': rid, 'judge': judge, 'requested': 2, 'sha256': B.digest(request)})
    manifest = {'name': name, 'base': 'qurefs', 'scheme': 'schemes/R27P2.json',
                'count': 6, 'source_tags': ['r27p2', 'qu'], 'workers': 4,
                'advisors': tasks, 'scheme_sha256': B.spec_hash(spec),
                'fixed_writer': 'schemes/Q15.json', 'changes': 'one layer per candidate: A1 or A2'}
    p = B.ROOT / 'runs' / '_batches' / name / 'advisors.json'
    B.write_frozen(p, B.json_text(manifest))
    print(B.json_text({'path': str(p), 'chars': len(request), 'hash': B.digest(request), 'new_model_calls': 0}))


if __name__ == '__main__':
    prepare()
