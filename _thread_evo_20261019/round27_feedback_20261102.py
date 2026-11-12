"""Return complete phase-candidate output to its author before spending on prose."""
import argparse
import hashlib
import json
from pathlib import Path

import evo
import mg_schedule
import pipe

ROOT = Path(__file__).resolve().parent
RID = 'resume20261102_g56_r27p_feedback2'


def prepare():
    spec = pipe.load_spec(ROOT / 'schemes/R27P.json')
    prompts = {s['prompt_file']: spec['_texts'][s['prompt_file']] for s in spec['steps']}
    raw = {w: evo.output(f'scr27p_{w}_A1') for w in ('op60', 'op61')}
    assert all(raw.values())
    message = (
        '按I12/I13退回独立方案R27P第一次实际运行的完整双曲A1。尚未运行A2/A4、无成品、无质量测量。'
        '执行者发现硬约束问题，已在首个检查点停止，没有挑一条改写。请作为原GPT-5.6提出者判断放弃还是第二次修改。\n'
        '【问题】Op.60 R01明知即将分别、双方原生活不能放弃被写成事实；R03把关系结束、曾共同生活写成前史，'
        '以重排生活安排作后续；R02把没有共同生活约定和安排受阻确立为发展支点。'
        'Op.61 R01已离开共同生活但关系未断，R02不能独立维持生活需要帮衬，R03发言权下降，'
        '都超出输入。后续的责任接回来、获得作主余地等更被写成已发生结果。'
        '把事实放在starting_condition里不能自动使其合规。这正是运行前识别的风险，实际已发生。\n'
        '【输入全部事实】Op.60 Center：亲密的幸福与留不住它的痛楚难以分开；'
        'Op.61 Center：维持尊严的行动与对旧日生活及归属的怀念反复拉扯。'
        '各自还输入了作品名称、作曲家及段落顺序/小节范围，没有上述外部事实。'
        '不要把维持尊严只允许纯内省，也不要因为要具体就增加现实处境当证据。'
        '请诊断“可以写已经存在的处境”“先把起点写实”以及固定阶段后果要求是否授权了补造；'
        '判断稀疏phase的独立假设仍值不值得试，而不是仅为眼前例子增加禁令。\n'
        '可保留少量phase与具体所求，也可以放弃；不要求一定给修改。不得让A1/A2看珠子，A3不改，'
        '仍四步，A4一次写全文，双曲同套通用提示词，模型/High/联网不改。'
        '通用生产提示词不能含以上作品/故事/具体反例或段号例子。'
        '若修改，只改任务定义与提示词，不重写已有路线或成品。\n'
        '【标准】\n' + (ROOT / '标准.md').read_text(encoding='utf-8')
        + '\n【原完整诊断及方案】\n' + evo.output('resume20261102_g56_round27')
        + '\n【实际运行四层提示词】\n' + json.dumps(prompts, ensure_ascii=False)
        + '\n【第一次完整双曲A1原始输出】\n' + json.dumps(raw, ensure_ascii=False)
        + '\n【完整实验历史】\n' + (ROOT / '试验记录.md').read_text(encoding='utf-8')
        + '\n只输出JSON：{"decision":"放弃或改了再试","analysis":"任务根因、改法及残余风险",'
        '"files":{"R27P_A1.txt":"若改则完整新提示词","R27P_A2.txt":"若改则完整新提示词",'
        '"R27P_A4.txt":"若改则完整新提示词"}}。未改的层不返回，放弃时files为空。'
        'A1保留{NAME} {SECTIONS} {CENTER} {K}；A2候选追加；A4保留{SECTIONS} {CENTER} {ROUTES} {TARGETS}，'
        '保留最终segments/items/text/cite/covers/relation接口，每段2–4条、每条一句。'
    )
    folder = evo.RUNS / RID
    folder.mkdir(exist_ok=True)
    target = folder / 'prepared_input.txt'
    if target.exists():
        assert target.read_text(encoding='utf-8') == message, 'Frozen input changed'
    else:
        target.write_text(message, encoding='utf-8')
    manifest = {'run_id': RID, 'characters': len(message), 'candidate': 'r27p', 'stage': 'I12/I13 second revision',
                'sha256': hashlib.sha256(message.encode()).hexdigest(), 'raw_A1': list(raw), 'quality_measurements': 0}
    (folder / 'prepared_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def run():
    mg_schedule.check()
    message = (evo.RUNS / RID / 'prepared_input.txt').read_text(encoding='utf-8')
    result = evo.call(RID, message, model=evo.G56, meta={'stage': 'I12/I13 R27P failure feedback', 'base': 'qu', 'web': True})
    if not result:
        raise SystemExit('No verified response; inspect existing request and shared failure before retry')
    print('AUTHOR_SECOND_RETURN_REQUIRES_REVIEW', flush=True)


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
