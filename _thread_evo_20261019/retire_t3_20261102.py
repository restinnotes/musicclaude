"""Return a mathematically rejected final T3 attempt to its author, no revision 4."""
import argparse
import hashlib
import json
from pathlib import Path
import evo
import mg_schedule
import pipe
import v6fix as V

ROOT=Path(__file__).parent
RID='resume20261102_g6_t3_postmortem'


def prepare():
    summary=json.loads((V.OUT/'blind2_r26t3_vsqu.json').read_text(encoding='utf-8'))
    assert len(summary)<=4
    lost=sum(row['better']!='新版' for row in summary.values())
    assert lost>=2, 'No early rejection without two non-winning complete reviews'
    reviews={rid:evo.output(rid) for rid in summary}
    assert all(reviews.values())
    spec=pipe.load_spec(ROOT/'schemes/R26T3.json')
    prompts={step['prompt_file']:spec['_texts'][step['prompt_file']] for step in spec['steps']}
    works={tag:{w:V.view(V.graph_of(w,tag),center=True) for w in ('op60','op61')} for tag in ('qu','r26t3')}
    message=(
        '按I12/I13把R26T方向第三次、最后修正的完整结果交回原GPT提出者。'
        f'四份快筛中已有{len(summary)}份完整返回，其中{lost}份未选新版，剩余即使全选新版也达不到3/4；'
        '因此本方向终止，不再给第四版提示词、不重写成品。未完成评审及底线缺测不算0。'
        '请结合全部原文解释任务定义、路线筛选或最终写线怎样造成失败，区分局部进展与未证实推测。'
        '评委赞赏旧主线未经建立的现实事实，不等于这些事实合法；不得为赢票要求恢复它们。'
        '不要因这一方向终止宣称流程收敛，当前主线中等以上问题仍未解决。\n'
        '【标准】\n'+(ROOT/'标准.md').read_text(encoding='utf-8')
        +'\n【实际四层提示词】\n'+json.dumps(prompts,ensure_ascii=False)
        +'\n【两版双曲全文】\n'+json.dumps(works,ensure_ascii=False)
        +'\n【全部已完成原始盲比，未返回的不算已测】\n'+json.dumps(reviews,ensure_ascii=False)
        +'\n【实验历史】\n'+(ROOT/'试验记录.md').read_text(encoding='utf-8')[-18000:]
        +'\n只输出JSON：{"decision":"放弃本方向","analysis":"根因与证据",'
        '"do_not_repeat":["不值得重复的方法"],"useful_observations":["局部发现与局限"]}。')
    folder=evo.RUNS/RID;folder.mkdir(exist_ok=True);frozen=folder/'prepared_input.txt'
    if frozen.exists():assert frozen.read_text(encoding='utf-8')==message, 'Frozen input changed'
    else:frozen.write_text(message,encoding='utf-8')
    manifest={'run_id':RID,'candidate':'r26t3','base':'qu','raw_reviews':list(reviews),
        'characters':len(message),'sha256':hashlib.sha256(message.encode()).hexdigest(),
        'purpose':'final failure returned to original author; no fourth revision'}
    (folder/'prepared_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False),flush=True)


def run():
    mg_schedule.check()
    message=(evo.RUNS/RID/'prepared_input.txt').read_text(encoding='utf-8')
    answer=evo.call(RID,message,model=evo.G6,meta={'stage':'I12/I13 final postmortem','base':'qu'})
    if not answer:raise SystemExit('No verified answer; inspect existing result before retry')
    print('POSTMORTEM_RETURNED_REVIEW_REQUIRED',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare',action='store_true');parser.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if args.prepare:prepare()
    elif args.run:run()
    else:parser.error('choose --prepare or --run')
