"""Return the final G3 failure to its original author; no fourth revision."""
import argparse
import hashlib
import json
from pathlib import Path

import evo
import mg_schedule
import pipe
import v6fix as V

ROOT = Path(__file__).resolve().parent
RID = 'resume20261102_gem_g3_postmortem'


def prepare():
    spec = pipe.load_spec(ROOT / 'schemes/R26G3.json')
    prompts = {s['prompt_file']: spec['_texts'][s['prompt_file']] for s in spec['steps']}
    reviews = {}
    for w in ('op60', 'op61'):
        for j in ('g6', 'g56'):
            rid = f'v6b2_{w}_{j}_r26g3_vsqu'
            assert evo.done(rid), rid
            reviews[rid] = evo.output(rid)
    result = json.loads((V.OUT / 'blind2_r26g3_vsqu.json').read_text(encoding='utf-8'))
    assert len(result) == 4 and all(v['better'] == 'qu' for v in result.values())
    works = {tag: {w: V.view(V.graph_of(w, tag), center=True) for w in ('op60', 'op61')}
             for tag in ('qu', 'r26g3')}
    message = (
        '按I12/I13把最后修正的R26G3完整运行结果交回原提出者。四份盲比全部选旧主线qu，'
        '全部判候选实质退步，因此这一方向终止，不再提交第四版提示词或重写成品。'
        '覆盖与单独读诊断未另行补测，不把缺测当零分。请只给出诚实的失败诊断和结案判断。\n'
        '请解释为什么当前A1/A2/A4没有拦住这些问题，区分任务定义失败和抽样风险；'
        '哪些局部进展值得保留为观察、哪些办法不值得再重复。'
        '不要把评委赞赏的旧主线未经建立的新事实当作必须恢复的优点。'
        '不要为了结案宣称收敛；既有主线中等问题仍未解决。\n'
        '【标准】\n' + (ROOT / '标准.md').read_text(encoding='utf-8')
        + '\n【实际提示词】\n' + json.dumps(prompts, ensure_ascii=False)
        + '\n【两版双曲全文】\n' + json.dumps(works, ensure_ascii=False)
        + '\n【全部四份完整原始盲比】\n' + json.dumps(reviews, ensure_ascii=False)
        + '\n【实验历史】\n' + (ROOT / '试验记录.md').read_text(encoding='utf-8')[-18000:]
        + '\n只输出JSON：{"decision":"放弃本方向","analysis":"根因与证据",'
        '"do_not_repeat":["不值得重复的方法"],"useful_observations":["局部发现与局限"]}。'
    )
    folder = evo.RUNS / RID
    folder.mkdir(exist_ok=True)
    frozen = folder / 'prepared_input.txt'
    if frozen.exists():
        assert frozen.read_text(encoding='utf-8') == message, 'Frozen input changed'
    else:
        frozen.write_text(message, encoding='utf-8')
    manifest = {'run_id': RID, 'candidate': 'r26g3', 'base': 'qu', 'raw_reviews': list(reviews),
                'characters': len(message), 'sha256': hashlib.sha256(message.encode()).hexdigest(),
                'purpose': 'Final failure returned to original author; no fourth revision'}
    (folder / 'prepared_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def run():
    mg_schedule.check()
    message = (evo.RUNS / RID / 'prepared_input.txt').read_text(encoding='utf-8')
    answer = evo.call_gemini_direct(RID, message, meta={'stage': 'I12/I13 final postmortem', 'base': 'qu'})
    if not answer:
        if not mg_schedule.status().get('cooling'):
            mg_schedule.fail(RID, 'Gemini final postmortem returned no complete answer')
        raise SystemExit('No verified answer; inspect existing failure before any retry')
    print('POSTMORTEM_RETURNED_REVIEW_REQUIRED', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--prepare', action='store_true')
    p.add_argument('--run', action='store_true')
    args = p.parse_args()
    if args.prepare:
        prepare()
    elif args.run:
        run()
    else:
        p.error('Choose --prepare or --run')
