"""An independent I02 direction, while the GPT author's final revision is pending."""
import argparse
import hashlib
import json
from pathlib import Path

import evo
import mg_schedule
import pipe
import v6fix as V

ROOT = Path(__file__).resolve().parent
RID = 'resume20261102_g56_round27'


def prepare():
    spec = pipe.load_spec(ROOT / 'schemes/Q15.json')
    prompts = {s['prompt_file']: spec['_texts'][s['prompt_file']] for s in spec['steps']}
    rules = (ROOT / '迭代准则.md').read_text(encoding='utf-8')
    limits = rules[rules.index('## 二、迭代范围和硬约束'):rules.index('## 三、流程')]
    open_reviews = {p.parent.name: p.read_text(encoding='utf-8')
                    for p in sorted((ROOT / 'runs').glob('eo2_*_qu_*/output.txt'))}
    assert len(open_reviews) == 10
    products = {t: {w: V.view(V.graph_of(w, t), center=True) for w in ('op60', 'op61')}
                for t in ('qu', 'qr', 'r26t2', 'r26g3')}
    results = {t: json.loads((V.OUT / f'blind2_{t}_vsqu.json').read_text(encoding='utf-8'))
               for t in ('r26t2', 'r26g3')}
    summary = {t: {rid: {k: val for k, val in r.items() if k not in ('lost_new', 'lost_base')}
                   for rid, r in records.items()} for t, records in results.items()}
    message = (
        'I02：请作为独立GPT-5.6顾问判断一条与最近两条失败方向有实质差别的通用设计。'
        '主线qu仍有开放评审列出的中等问题，尚未收敛；R26G3已四份盲比0/4淘汰且作者放弃，'
        'R26T2三份全负、最多1/4已提前淘汰，原GPT作者正在最后修改。'
        '你不是给它们第四版，而是提出一个独立、最多改三次的新假设；没有可信方向可明确放弃。\n'
        '这次仍保持用户认可的四步：A1不看珠子构思人的经历、A2不看珠子选路、'
        'A3去掉珠子画面情节、A4一次写完整线。A3不改，其他可整层重写，不增加成品修补层。'
        '生产模型仍GPT-6/High，不改其他输入、联网权限、标准和阈值。'
        '不得把原标准的禁止新编事件偷换成禁止真实的人际处境或一切初始所求，'
        '也不得通过往前补事件使原来的凭空转折变合法。\n'
        '请先判断造成具体所求和顾虑消失、后半重复的任务定义，指出实际提示词原句与机制。'
        '避免再次仅仅添加禁令、事实账本或让每段强造一个心理变化；不能抽空成幸福/无保证等情绪。'
        'Q13/qr曾保留共存矛盾并过当时快筛，但成品每条多句、形态不合；'
        '可判断其未试透之处是否仍有价值，也可明确不用。不能把旧快筛胜率当作它已优于当前qu。'
        '提示词不得出现这些作品、人物、段号、故事例子或仅针对眼前的反例。'
        '评委可能赞赏旧主线未经建立的新事实，不能为赢票恢复。\n'
        '【标准】\n' + (ROOT / '标准.md').read_text(encoding='utf-8')
        + '\n【硬约束】\n' + limits
        + '\n【当前主线四层实际提示词】\n' + json.dumps(prompts, ensure_ascii=False)
        + '\n【旧Q13骨架提示词】\n' + (ROOT / 'schemes/Q13_A1.txt').read_text(encoding='utf-8')
        + '\n【qu及三个候选完整双曲，供诊断而非生产例子】\n' + json.dumps(products, ensure_ascii=False)
        + '\n【主线全部10份完整开放评审】\n' + json.dumps(open_reviews, ensure_ascii=False)
        + '\n【新候选逐份盲比票数，未测不当0】\n' + json.dumps(summary, ensure_ascii=False)
        + '\n【Gem已完整结案诊断，仅为假说，不能采用违反四步的建议】\n'
        + evo.output('resume20261102_gem_g3_postmortem')
        + '\n【完整实验历史】\n' + (ROOT / '试验记录.md').read_text(encoding='utf-8')
        + '\n【用户判定】\n' + (ROOT / '用户判定.md').read_text(encoding='utf-8')
        + '\n只输出JSON：{"decision":"放弃或改了再试","hypothesis":"与已失败方向实质区别",'
        '"analysis":"诊断、证据、为何未重复旧路、风险",'
        '"files":{"Q6_A1.txt":"若改此层则完整提示词","Q6_A2.txt":"若改此层则完整提示词",'
        '"Q15_A4.txt":"若改此层则完整提示词"}}。未改的层不返回；放弃时files为空。'
        '保持JSON接口：A1 {NAME} {SECTIONS} {CENTER} {K}；A2路线在末尾追加；'
        'A4 {SECTIONS} {CENTER} {ROUTES} {TARGETS}。两曲同一套通用提示词，每段2–4条，每条一句，保留引用及关系标签。'
    )
    folder = evo.RUNS / RID
    folder.mkdir(exist_ok=True)
    target = folder / 'prepared_input.txt'
    if target.exists():
        assert target.read_text(encoding='utf-8') == message, 'Frozen input changed'
    else:
        target.write_text(message, encoding='utf-8')
    manifest = {'run_id': RID, 'characters': len(message), 'open_reviews': len(open_reviews),
                'sha256': hashlib.sha256(message.encode()).hexdigest(), 'base': 'qu',
                'model': evo.G56, 'purpose': 'Independent I02 direction, no fourth revision of retired G3'}
    (folder / 'prepared_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def run():
    mg_schedule.check()
    message = (evo.RUNS / RID / 'prepared_input.txt').read_text(encoding='utf-8')
    answer = evo.call(RID, message, model=evo.G56, meta={'stage': 'I02 independent round27', 'base': 'qu', 'web': True})
    if not answer:
        raise SystemExit('No verified response; inspect shared failure state and existing request before retry')
    print('INDEPENDENT_PROPOSAL_REVIEW_REQUIRED', flush=True)


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
