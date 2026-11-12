"""Frozen broader search after reopening the premature local stopping claim.

Preparation is local only. Collection stops before proposal selection or prose
application, uses the existing transport, and never changes the standards.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('JV', '2')
import experiment_batch as B

BASE = 'r50progress1rr'
ROOT = B.ROOT / 'runs/_batches/round54_broader'
PREFIX = 'r54'


def reopen():
    receipt = ROOT / 'reopen.json'
    if receipt.exists():
        return
    now = datetime.now(ZoneInfo('America/New_York')).isoformat()
    files = {}
    for name in ('STATUS.md', '最终版本_vs_r49b.md'):
        raw = (B.ROOT / name).read_text(encoding='utf-8')
        B.write_frozen(ROOT / ('before_reopen_' + name), raw)
        files[name] = B.digest(raw)
    status = f'''# 当前接续：r50progress1rr仍为已验收主线，扩大探索，尚未证明收敛

最后更新：{now}。

- 当前goal active，目标仍是继续迭代直到收敛，最终写vsr49b的md；固定起点r49b，所有新候选先比当前主线r50progress1rr。
- 撤回12:39“目标完成/本轮终态”的结论：只检验局部删减和含义一致性两批，不能代替更完整的方法探索；完整开放评审仍有可行动中等问题。旧测量和旧报告原文保存在runs/_batches/round54_broader/before_reopen_*，不删除历史。
- r50progress1rr验收本身仍有效：8/8新版、7/8不退步，净胜+20/+2/+13/+12，原底线通过。未称覆盖总数全面提高或没有缺点。
- 新批R54先请多位顾问读现行四步与写后修订提示词、上游产物、当前双曲、完整I01、历史及负例，提出不同机制的完整通用提示词；不再自行把候选限制为最多8条修改、结尾逐字不动。构思仍不看珠子、其余硬约束及门槛原样保持。
- 新请求只由round54_advisors.py collect唯一父收取，顾问输出需全文读、泛化/接口/历史检查后再生产；准备不代表提交。原R50–53已知父均终态，不恢复旧列表。
- 生产保留原GPT6/High成功通路，顾问及评审优先gpt3；普通终态故障60秒，明确suspicious才共享30分钟，按原故障时间，不重读延长。总在途≤10。heartbeat保持PAUSED，由active goal推进，不动watchdog/缓存保温。
- 珠线片段对应功能已完成但绑定r49b，不将旧偏移自动套到新正文。此前浏览器视觉检查未完成，离线检查结果有效。

---
以下为过程历史；最新接续状态优先。

'''
    (B.ROOT / 'STATUS.md').write_text(status + (B.ROOT / 'STATUS.md').read_text(encoding='utf-8'), encoding='utf-8')
    report = B.ROOT / '最终版本_vs_r49b.md'
    report.write_text('> **状态更正：这是阶段性对比，收敛尚未证明。** 当前已验收主线仍为r50progress1rr；下面“最终/结束”的表述为12:39局部搜索的历史结论，已被R54扩大探索取代。验收数据保持有效，后续完成时重写最终结论。\n\n' + report.read_text(encoding='utf-8'), encoding='utf-8')
    with (B.ROOT / '试验记录.md').open('a', encoding='utf-8') as f:
        f.write(f'\n\n- {now}：R54重新开放探索。撤回12:39目标完成判断，有限局部搜索不等于原目标收敛；r50progress1rr验收有效、仍为唯一主线。原终态报告/STATUS逐字备份及哈希见round54_broader/reopen.json；多顾问先诊断不同层和新机制，不只再做局部删减。标准、门槛、硬约束和成品正文均未改。\n')
    B.write_frozen(receipt, B.json_text({'at': now, 'prior_hashes': files, 'base': BASE,
                                      'supersedes': 'round52_current/convergence.json local stopping claim',
                                      'goal': 'active; convergence not established'}))


def prepare():
    if BASE == 'r50progress1rr' and ROOT.name == 'round54_broader':
        reopen()
    else:
        acceptance = json.loads((B.ROOT / 'runs/_batches/round50_from_r49b' / f'{BASE}_acceptance.json').read_text(encoding='utf-8'))
        assert acceptance['fair']['pass'] and acceptance['floor']['status'] == 'pass'
    spec = B.pipe.load_spec(B.ROOT / 'schemes/Q15.json')
    rules = (B.ROOT / '迭代准则.md').read_text(encoding='utf-8')
    materials = {
        'standard': (B.ROOT / '标准.md').read_text(encoding='utf-8'),
        'rules': rules,
        'dag': (B.ROOT / 'DAG.md').read_text(encoding='utf-8'),
        'four_step_prompts': spec['_texts'],
        'accepted_revision_prompts': {p.name: p.read_text(encoding='utf-8') for p in (B.ROOT / 'DAG/prompts/N05e_写后修订').glob('*.txt') if '实发' not in p.name},
        'accepted_global_reweave_prompt': {p.name: p.read_text(encoding='utf-8') for p in (B.ROOT / 'DAG/prompts/N05f_全篇重组').glob('*.txt') if '实发' not in p.name},
        'upstream_outputs': {w: {s: B.evo.output(f'scqu_{w}_{s}') for s in ('A1', 'A2', 'A3')} for w in B.F.WORKS},
        'current_products': {w: {'line': B.V.view(B.V.graph_of(w, BASE), ids=True), 'fixed_beads': B.V.beads(w)} for w in B.F.WORKS},
        'history': (B.ROOT / '试验记录.md').read_text(encoding='utf-8'),
        'user_judgments': (B.ROOT / '用户判定.md').read_text(encoding='utf-8'),
        'current_open_reviews': [],
        'negative_experiments': {p.name: json.loads(p.read_text(encoding='utf-8')) for p in (B.ROOT / 'runs/_batches/round52_current').glob('*_quick_reviewed.json')},
        'scope_audit': json.loads((B.ROOT / 'runs/_batches/round52_current/open_input_scope_audit.json').read_text(encoding='utf-8')),
        'broader_mechanisms_and_outcomes': {p.name: json.loads(p.read_text(encoding='utf-8')) for p in (B.ROOT / 'runs/_batches/round54_broader').glob('*_disposition.json')},
    }
    if BASE != 'r50progress1rr':
        materials['current_acceptance'] = acceptance
        manifest = json.loads((B.ROOT / 'runs/_batches/round54_broader/candidates.json').read_text(encoding='utf-8'))
        materials['tested_broader_prompt_mechanisms'] = []
        for candidate in manifest['candidates']:
            entry = dict(candidate)
            entry['full_prompts'] = []
            for step in candidate['steps']:
                text = (B.ROOT / step['path']).read_text(encoding='utf-8')
                assert B.digest(text) == step['sha256']
                entry['full_prompts'].append(text)
            materials['tested_broader_prompt_mechanisms'].append(entry)
        materials['parent_comparison_raw'] = []
        import round50_measure as M
        for rid, _, _ in M.jobs('fair', BASE, acceptance['base']):
            assert B.reviewed(rid), rid
            materials['parent_comparison_raw'].append({'rid': rid, 'raw': B.evo.output(rid)})
    for w in B.F.WORKS:
        for j in ('g6', 'g56', 'gem'):
            for k in ((1,) if j == 'gem' else (1, 2)):
                rid = f'eo2_{w}_{BASE}_{j}_r{k}'
                assert B.reviewed(rid), rid
                materials['current_open_reviews'].append({'rid': rid, 'raw': B.evo.output(rid)})
    assert all(all(x for x in per.values()) for per in materials['upstream_outputs'].values())
    B.write_frozen(ROOT / 'materials.json', B.json_text(materials))
    tasks = []
    for judge, count, lens in (
        ('g6a', 4, '优先寻找整层写线重写、结构吸收、跨段作用重新组织的不同办法；也可说明为什么应保留当前上游。'),
        ('g6b', 3, '独立诊断；优先从稿件重构、必要的上游重抽/选择、组合和另一条因果组织路线找未试机制，不重做换词删句。'),
        ('g56', 3, '独立诊断；寻找能保住具体情感支点却消除回返和解释腔的结构机制，并审查现有分层是否造成问题。'),
    ):
        message = f'''你是写作流程顾问。当前最好已验收稿是{BASE}，并未收敛。请读完材料，诊断哪层哪句任务定义造成哪些成品问题，再提{count}套彼此有实质区别、尚未被历史否定的可运行方案。
{lens}
可以删层、并层、改顺序、整层重写，也可保留已验收稿重写组织；优先只动一层，确需多层则明确依赖。不要把“最多改8条、结尾逐字不动、不能更长”当用户标准，它们只是前批实验限制。不要机械把全部事实降为猜测，也不为变短删掉必要支点。
必须遵守材料中标准与六条硬约束。构思新经历的阶段不得看珠子；综合写线或写后修订可以看。珠子/分段/Center不改；每段2–4条，每条一句完整自然话，引用真实先前条目，原三类关系。生产GPT6/High及验收不改。
诊断可以引用具体作品数据；可复用prompt内不能写具体作品/情节例子或某一段特例。不要照搬评委中新增事件、心理事实、碎句、少于2条、必须崇高的意见；评级及分歧保留，按标准判断。
每个方案给出完整通用提示词与输入接口，不能只写一句方向。可用已有四步A4接口{{SECTIONS}}/{{CENTER}}/{{ROUTES}}/{{TARGETS}}，或写后整稿接口{{SECTIONS}}/{{CENTER}}/{{LINE}}/{{BEADS}}/{{REVIEWS}}；新增无珠子构思用{{SECTIONS}}/{{CENTER}}/{{LINE}}但不能含BEADS/TARGETS。输入只来自相应已有或本方案新增步骤，列清步骤依赖。完整输出可以是现有A4 segments JSON（sec/relation/items[id,text,cite]），也可在单步写后输出edits替换/删除原id；别创造执行者写正文的步骤。
仅输出JSON：{{"diagnosis":"问题、原因层、历史与风险","candidates":[{{"name":"英文短名","hypothesis":"不同机制及预期得失","changed_layer":"A4/postwrite/upstream","reuse":"哪些真实输入能复用","steps":[{{"id":"step_id","inputs":["占位符名"],"prompt":"完整通用prompt含输出格式"}}],"risk":"具体失败方式与为何不同于旧失败"}}]}}。
【完整材料】
''' + B.json_text(materials)
        rid = f'{PREFIX}_advisor_{judge}'
        B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', message)
        tasks.append({'rid': rid, 'model': 'g56' if judge == 'g56' else 'g6', 'count': count, 'input_sha256': B.digest(message)})
    B.write_frozen(ROOT / 'advisors.json', B.json_text({'base': BASE, 'tasks': tasks, 'workers': 3, 'materials_sha256': B.digest(B.json_text(materials))}))
    print(B.json_text({'prepared': len(tasks), 'plans_requested': 10, 'material_chars': len(B.json_text(materials)), 'calls': 0}), flush=True)


def collect():
    import msvcrt
    B.F.configure()
    manifest = json.loads((ROOT / 'advisors.json').read_text(encoding='utf-8'))
    with (ROOT / 'receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        def one(t):
            msg = (B.evo.RUNS / t['rid'] / 'prepared_input.txt').read_text(encoding='utf-8')
            assert B.digest(msg) == t['input_sha256']
            try:
                B.F.submit([(t['rid'], msg, B.V.JUDGES[t['model']], 'I02 broader-search adviser')], 1)
                return {**t, 'status': 'full_read_required'}
            except Exception as e:
                return {**t, 'status': 'inspect_failure', 'error': str(e)}
        with ThreadPoolExecutor(max_workers=3) as pool:
            rows = list(pool.map(one, manifest['tasks']))
        (ROOT / 'collection.json').write_text(B.json_text({'terminal': True, 'rows': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare', 'collect'))
    p.add_argument('--base', default=BASE)
    p.add_argument('--batch', default=ROOT.name)
    p.add_argument('--prefix', default=PREFIX)
    args = p.parse_args()
    assert all(x and all(c.isalnum() or c in '_-' for c in x) for x in (args.base, args.batch, args.prefix))
    BASE, ROOT, PREFIX = args.base, B.ROOT / 'runs/_batches' / args.batch, args.prefix
    prepare() if args.action == 'prepare' else collect()
