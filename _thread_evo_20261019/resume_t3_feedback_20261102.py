"""I12/I13 third author attempt; freeze complete evidence, never edit prose."""
import argparse
import hashlib
import json
from pathlib import Path

import evo
import mg_schedule
import pipe
import v6fix as V

ROOT=Path(__file__).resolve().parent
RID='resume20261102_g6_candidate_feedback3'

def prepare():
    spec=pipe.load_spec(ROOT/'schemes/R26T2.json')
    prompts={s['prompt_file']:spec['_texts'][s['prompt_file']] for s in spec['steps']}
    lines={tag:{w:V.view(V.graph_of(w,tag),center=True) for w in ('op60','op61')} for tag in ('qu','r26t2')}
    raw={}
    missing=[]
    for prefix in ('cov2','al2','tr2','v6b2'):
        for w in ('op60','op61'):
            for j in ('g6','g56'):
                run=f'{prefix}_{w}_{j}_r26t2'+('_vsqu' if prefix=='v6b2' else '')
                if evo.done(run):raw[run]=evo.output(run)
                else:missing.append(run)
    blind=[r for r in raw if r.startswith('v6b2_')]
    assert len(blind)==3,blind
    summary=json.loads((V.OUT/'blind2_r26t2_vsqu.json').read_text(encoding='utf-8'))
    assert len(summary)==3 and all(r['better']=='qu' for r in summary.values())
    prior=json.loads((V.OUT/'resume20261102_g6_candidate_feedback2.parsed.json').read_text(encoding='utf-8'))
    rules=(ROOT/'迭代准则.md').read_text(encoding='utf-8')
    limits=rules[rules.index('## 二、迭代范围和硬约束'):rules.index('## 三、流程')]
    message=(
        '按I12/I13把你第二版R26T2/r26t2的完整产物和全部已完成原始评审交回你。当前主线仍qu。'
        '这是这一方向的第三次修改机会，请判断值得最后修改一次还是放弃，不要求一定返回修改。\n'
        '【确定的判定】三份完整盲比全部选qu并判新版实质退步，第四份基础设施失败；'
        '即使缺的一份选新版，也最多1/4，达不到3/4，所以已经提前淘汰。'
        '覆盖和单独读等未完成项均缺测，不算零分，也不能说全套快筛已经完成。\n'
        '【需要你诊断】前版解决了某些凭空事实，却把具体所求、顾虑、两难及其发展抽掉，'
        '后半只反复幸福、留恋、无保证或认真生活。请结合各段原始理由判断造成这一点的任务定义，'
        '不只加一条要具体或不要重复。也要查选路层为什么放过了这个问题。\n'
        '评委原文是证据，不是额外标准；其中可能把主线未成立的新事实也当优点，'
        '不得照搬这种事实来换回票数。遵守既有输入与人的前面经历，不能靠新编事件、前史、对方反应、'
        '含糊的事情已经完成、或者办法反复试验来推进。也不要把所有发展削成抽象情绪。'
        '不把本次作品、人物、句子或段号例子写进通用生产提示词。\n'
        '【标准】\n'+(ROOT/'标准.md').read_text(encoding='utf-8')
        +'\n【硬约束】\n'+limits
        +'\n【你上次的诊断】\n'+str(prior.get('analysis',''))
        +'\n【你第二版的实际四层提示词】\n'+json.dumps(prompts,ensure_ascii=False)
        +'\n【双曲主线和本候选的完整成品】\n'+json.dumps(lines,ensure_ascii=False)
        +'\n【全部已完成原始评审，不是摘录】\n'+json.dumps(raw,ensure_ascii=False)
        +'\n【缺测列表】\n'+json.dumps(missing,ensure_ascii=False)
        +'\n【实验历史】\n'+(ROOT/'试验记录.md').read_text(encoding='utf-8')[-20000:]
        +'\n【输出】只输出JSON对象：'
        '{"decision":"放弃或改了再试","analysis":"为什么这条路不行，或根因和最后改法及风险",'
        '"files":{"原提示词文件名":"修改后完整提示词"}}。未改的层不要返回，放弃时files为空。'
        '保持当前四步接口及JSON结构。A1保留{NAME} {SECTIONS} {CENTER} {K}；'
        'A4保留{SECTIONS} {CENTER} {ROUTES} {TARGETS}；A2候选在末尾附加，A3不改。'
        '双曲同一套通用提示词，每段2–4条、每条一句，联网权限和模型不变。'
        '你返回的方案先审查泛化和标准，再决定是否运行；不要直接重写当前成品。'
    )
    folder=evo.RUNS/RID
    folder.mkdir(exist_ok=True)
    path=folder/'prepared_input.txt'
    if path.exists():
        assert path.read_text(encoding='utf-8')==message,'Frozen input changed; use a new run id'
    else:path.write_text(message,encoding='utf-8')
    manifest={'run_id':RID,'candidate':'r26t2','base':'qu','prompts':len(prompts),'complete_reviews':list(raw),
              'missing':missing,'characters':len(message),'sha256':hashlib.sha256(message.encode()).hexdigest(),
              'decision_evidence':'3 completed losses; best possible 1/4 < 3/4'}
    (folder/'prepared_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False),flush=True)
    return message

def run():
    frozen=evo.RUNS/RID/'prepared_input.txt'
    message=frozen.read_text(encoding='utf-8') if frozen.exists() else prepare()
    mg_schedule.check()
    answer=evo.call(RID,message,model=evo.G6,meta={'stage':'I12/I13 third author feedback','base':'qu','web':True})
    if not answer:raise SystemExit('No verified response; use shared failure state, never duplicate an in-flight request')
    print('AUTHOR_RETURNED_REVIEW_REQUIRED',RID,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if args.prepare:prepare()
    elif args.run:run()
    else:parser.error('choose --prepare or --run')
