"""Two frozen local-revision batches against the accepted current mainline.

Preparation requires all current open reviews to have been read. Collection
never applies prose or advances the mainline. Existing engine and limits apply.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault('JV', '2')
import experiment_batch as B
import round50_continue as R

BASE = 'r50progress1rr'
ROOT = B.ROOT / 'runs/_batches/round52_current'
FOCUS = {
    'r52trim': '只检验局部的重复和解释腔：同一段两条若在说同一个念头，保留其中独立的愿望、顾虑和转折，减少重复陈述；不能只换近义词。优先修真正冗余的句子或半句，不为每段制造新进展。保住每次回返真正不同的作用，不把既有具体关系降成泛泛亲近，也不新增任何事实。结尾最终选择逐字不动。',
    'r53coherence': '只检验关键心理变化的前后一致性：行为是主动还是无意、愿望与推测还是已经知道的事实、一次轻松还是已经作出的选择，要让前后用法相容。已有结论若缺依据，不补造经历，不只加引用；修到后文实际依赖它的恐惧和选择也接得上。保留已成立的具体相互关系及情感力度，不能把全文降为含糊猜测，不能借解释动机重复剧情。结尾最终选择逐字不动。',
}


def prepare():
    tasks = []
    for mode, focus in FOCUS.items():
        for draw in (1, 2):
            tag = f'{mode}{draw}'
            for w in B.F.WORKS:
                evidence = []
                for j in ('g6', 'g56', 'gem'):
                    for k in ((1,) if j == 'gem' else (1, 2)):
                        rid = f'eo2_{w}_{BASE}_{j}_r{k}'
                        assert B.reviewed(rid), f'Full read missing: {rid}'
                        evidence.append({'rid': rid, 'raw': B.evo.output(rid)})
                reviews = {
                    'full_current_open_reviews': evidence,
                    'fixed_boundaries': '保留原评级和读者分歧。意见不是标准，不采改珠子、改关系定义、少于两条、额外编场景或必须崇高的建议；同一方向之前删去相互需要与中途必要选择曾失败，具体事实/感受不能只为降重而删除。',
                }
                msg = R.PROMPT.format(FOCUS=focus,
                                      LINE=B.V.view(B.V.graph_of(w, BASE), ids=True),
                                      BEADS=B.V.beads(w), REVIEWS=B.json_text(reviews))
                rid = f'sc{tag}_{w}_A5'
                B.write_frozen(B.evo.RUNS / rid / 'prepared_input.txt', msg)
                tasks.append({'tag': tag, 'work': w, 'mode': mode, 'draw': draw,
                              'rid': rid, 'input_sha256': B.digest(msg)})
    manifest = {'base': BASE, 'focus': FOCUS, 'tasks': tasks,
                'source_hashes': {w: B.digest((B.V.OUT / f'{w}_{BASE}.json').read_text(encoding='utf-8')) for w in B.F.WORKS},
                'route': 'mimic', 'workers': 4,
                'next': 'full_read_then_mechanical_apply_then_balanced_quick4_against_current_mainline',
                'stopping': 'Two distinct batches; a later accepted mainline invalidates their old-base superiority claims.'}
    B.write_frozen(ROOT / 'manifest.json', B.json_text(manifest))
    print('Frozen 8 requests, 2 distinct mechanisms x 2 draws x 2 works; no calls', flush=True)


def collect(route='mimic'):
    import msvcrt
    import mg_schedule
    os.environ['THREAD_ROUTE'] = route
    B.F.configure()
    manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))
    for w, sha in manifest['source_hashes'].items():
        assert B.digest((B.V.OUT / f'{w}_{BASE}.json').read_text(encoding='utf-8')) == sha
    with (ROOT / 'receiver.lock').open('a+') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)

        def one(t):
            msg = (B.evo.RUNS / t['rid'] / 'prepared_input.txt').read_text(encoding='utf-8')
            assert B.digest(msg) == t['input_sha256']
            if not B.evo.done(t['rid']):
                try:
                    state = mg_schedule.status()
                    if state['cooling']:
                        mg_schedule.check()
                    answer = B.evo.call(t['rid'], msg, model=B.evo.G6,
                                        meta={'stage': 'current-local-revision', 'web': True})
                except mg_schedule.CoolingDown as exc:
                    return {**t, 'status': 'not_submitted_cooldown', 'reason': str(exc)}
                if not answer:
                    return {**t, 'status': 'incomplete_inspect_original_receiver'}
            return {**t, 'status': 'full_read_required'}

        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(one, manifest['tasks']))
        (ROOT / 'collection_result.json').write_text(B.json_text({'terminal': True, 'rows': rows}), encoding='utf-8')
        print(B.json_text(rows), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('prepare', 'collect'))
    parser.add_argument('--route', choices=('mimic', 'gpt3s'), default='mimic',
                        help='Only after the existing collector has terminated; completed requests are reused.')
    args = parser.parse_args()
    prepare() if args.action == 'prepare' else collect(args.route)
