"""Continue the accepted r49b local revision route, stopping for full reads.

prepare sends nothing; collect owns the frozen requests and never applies edits.
No change to standards, production engine or acceptance thresholds.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo

os.environ.setdefault('JV', '2')
import experiment_batch as B

ROOT = B.ROOT / 'runs/_batches/round50_from_r49b'

PROMPT = """下面是已经通过比较验收的一稿“线”：一个人在器乐作品里经历的一件事，按音乐段落写分段要点。另有固定的听感记录（珠子）与它合写，以及读者对当前稿的具体意见。

请在当前好稿上做有限的局部修订。保留它平常、具体的口气，未改的条目逐字不动，不另写一整稿。

本次只检验这个方向：
{FOCUS}

共同要求：
- 读完整篇后再动笔，检查改动怎样影响后面引用、转折和最后选择；已经成立的推进和珠子的主要落脚处保住。
- 已有的处境和人物自己的愿望、顾虑可保留；不能为了补逻辑新增他人的举动、心理事实、对白、外部事件、前史或物件。事实不够时可将结论写成有分寸的推测，但后面的恐惧、选择也必须相应接得上，不能前面降为猜测、后面又当作确定事实。
- 不把珠子的画面、比喻、情节搬成真的发生的事。不改珠子、Center、分段、小节或条目顺序；不靠泛泛心理总结填补缺口。
- 最多影响8条原条目，包括被合并、删除的条目；优先改已有的一条而非删薄一段。每段2–4条，每条一句完整自然的话，全文不比原稿更长。
- 若两个念头各有独立用途，不为变短硬塞进一句；读者建议只是线索，不照抄示范，不为得票恢复重复。
- 未改的正文一字不动，不顺手润色。不能改好的地方可以留着；允许edits为空，不能编改动凑数。
- 原有段落关系由后续同一个重标节点处理，本步不改标签。保留条目编号，只引用确实仍存在且先出现的条目；引用不是证明，不要给缺依据的结论仅增加一个标记。

【当前线，含原条目编号】
{LINE}

【固定珠子】
{BEADS}

【当前稿的两位读者意见及独立阅读诊断，保留原文；分数不作门槛】
{REVIEWS}

只输出JSON：{{"edits":[{{"id":"S03-2","op":"replace","text":"改后的一句"}},{{"id":"S04-2","op":"delete"}}],"note":"具体说明修了哪个因果或重复，以及保留了什么；未能修的风险如实说明"}}。
不在text里抄引用标记，脚本按原字段处理；不输出JSON以外文字。"""

FOCUS = {
    'basis': '先处理读者认为缺少依据的关键认识：检查它由前面哪些真实已写出的经历支持；不能把希望、接纳或相处未变偷偷当成他人另一个确定态度。尽量只动这条依据链涉及的条目；保持心理发展的力度和具体所求，不把整条经历降成可能、也许的含糊概括。其余重复这次不顺手改。',
    'progress': '先处理跨段重复：相近心事再次出现时，保留这一次由前面经历带来的具体不同，不把同一矛盾从头重讲。优先重分已有条目的作用而非删除推进环节；段落发生得少可短，但不能把前后转折需要的桥删掉。结尾已有独立选择，本轮不改结尾，不以更响亮的口号制造进步。'
}


def prepare():
    path = ROOT / 'manifest.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    human = json.loads((B.V.OUT / 'human_score_qurefs_r49b_h23.json').read_text(encoding='utf-8'))
    source_hashes = {w: B.digest((B.V.OUT / f'{w}_r49b.json').read_text(encoding='utf-8')) for w in B.F.WORKS}
    tasks = []
    for mode in ('basis', 'progress'):
        for repeat in (1, 2):
            tag = f'r50{mode}{repeat}'
            for w in B.F.WORKS:
                evidence = {'current_human_readers': human[w]['r49b'],
                            'current_standalone_readers': {j: B.V.parse(f'al2_{w}_{j}_r49b') for j in B.F.JUDGES}}
                if len(evidence['current_human_readers']) != 2 or any(v is None for v in evidence['current_standalone_readers'].values()):
                    raise ValueError('missing current-r49b reader evidence')
                message = PROMPT.format(FOCUS=FOCUS[mode], LINE=B.V.view(B.V.graph_of(w, 'r49b'), ids=True),
                                        BEADS=B.V.beads(w), REVIEWS=B.json_text(evidence))
                rid = f'sc{tag}_{w}_A5'
                B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', message)
                tasks.append({'tag': tag, 'work': w, 'mode': mode, 'repeat': repeat,
                              'rid': rid, 'input_sha256': B.digest(message)})
    manifest = {'frozen_at': datetime.now(ZoneInfo('America/New_York')).isoformat(), 'base': 'r49b',
                'source_hashes': source_hashes, 'workers': 4, 'route': 'mimic',
                'hypotheses': FOCUS, 'tasks': tasks, 'next': 'full_read_before_apply_then_relabel_then_balanced_blind_vs_r49b'}
    B.write_frozen(path, B.json_text(manifest))
    B.write_frozen(ROOT / 'continuation_policy.json', B.json_text({
        'authorization': '用户：在他成功的路线上继续做更好版本；继续迭代直到收敛，最后生成最后版本vsr49b的md。',
        'production': '延续r49b已成功路线MimicGate GPT6/High局部修订，评审GPT6/GPT5.6仍优先gpt3/max；不切账号不改强度。',
        'base': 'r49b，固定起点哈希；所有新候选直接比当前已验收主线，最终另写vsr49b的md。',
        'acceptance': '正反8票，>=6新版、>=6不退步、单独/啰嗦/人话净胜非负，原覆盖/单独读底线；标准和门槛不改。',
        'execution': '2个不同机制各2份双曲；第一阶段8次生产，最多4工作并发。全文读后才套用，模型局部修订+必要回补，不手改成品。',
        'stopping': '不沿用无新问题就停的旧推断。至少连续两批真实的不同机制修订及必要回补均不能胜过当前主线，且已指出的可行动改法已实际检验或有明确放弃依据，才评估搜索收敛；报告仍未解决的问题，不称完美或普遍无解。未经检验的旧重大问题不因重复而算解决。',
        'infrastructure': '普通终态错误60秒退避；明确可疑行为30分钟共享暂停，按原故障时间，不重读重置；旧请求只收不争抢。',
        'final_artifact': '最终版本_vs_r49b.md，包含两曲具体前后句、验收/底线、路线变化、未解决点与成品链接。'
    }))
    return manifest


def collect(route='mimic'):
    import msvcrt
    os.environ['THREAD_ROUTE'] = route
    B.F.configure()
    m = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    for w, digest in m['source_hashes'].items():
        if B.digest((B.V.OUT / f'{w}_r49b.json').read_text(encoding='utf-8')) != digest:
            raise ValueError('frozen baseline changed')
    with (ROOT / 'receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        previous = ROOT / 'collection_result.json'
        if previous.exists():
            stamp = datetime.now(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%S%fZ')
            B.write_frozen(ROOT / f'collection_before_{stamp}.json', previous.read_text(encoding='utf-8'))
        def one(task):
            rid = task['rid']
            msg = (B.evo.RUNS / rid / 'prepared_input.txt').read_text(encoding='utf-8')
            assert B.digest(msg) == task['input_sha256']
            if not B.evo.done(rid):
                import mg_schedule
                try:
                    response = B.evo.call(rid, msg, model=B.evo.G6, meta={'stage': 'r50_local_revision', 'web': True})
                except mg_schedule.CoolingDown as exc:
                    return {**task, 'status': 'not_submitted_cooldown', 'reason': str(exc)}
                if not response:
                    return {**task, 'status': 'incomplete_inspect_original_receiver_before_retry'}
            return {**task, 'status': 'full_read_required', 'output_sha256': B.digest(B.evo.output(rid))}
        with ThreadPoolExecutor(max_workers=m['workers']) as pool:
            rows = list(pool.map(one, m['tasks']))
        (ROOT / 'collection_result.json').write_text(B.json_text({'receiver_terminal': True, 'actual_requested_route': route, 'tasks': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('prepare', 'collect'))
    p.add_argument('--route', choices=('mimic', 'gpt3s'), default='mimic', help='Authorized alternate route only after original receivers are terminal')
    a = p.parse_args()
    if a.action == 'prepare':
        d = prepare()
        print(B.json_text({'tasks': len(d['tasks']), 'hypotheses': list(FOCUS), 'new_model_calls': 0}))
    else:
        collect(a.route)
