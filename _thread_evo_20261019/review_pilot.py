"""Blind acceptance of the full 1–39 pilot against earlier best local explanations."""
import hashlib
import json
import random
import sys
import covjudge
import draft10
import evo
import judge_synth_v3 as judge
import node2b

RULES='''请验收一条音乐Thread的前五段（肖邦《船歌》1–39）。历史材料只用于找出旧版局部已经达到的价值，不能塞入新解释池，也不要求照搬其中虚构的前史或心理动作。
先独立读完听感、旧材料与新试跑，再给绝对合格判断。每个判断有具体理由，可以全部不合格。新版本不因流程更顺而抵销某个关键位置的退步。
先对17–23、24–34、35–39各找旧材料中最好的局部解释，指出真实价值及缺陷；再看新稿是否保住或用更好的理解替代了它。
验收标准：
1. 具体为什么此刻来自此前真正建立的经历，不能只给结果换名字。局部可以延续，不强制每段新领悟。
2. 17–23的舒服漂浮、急切与暗流可同时成立，不能只留一种；不能以侧面为由丢掉急切或暗流。
3. 24–34须说明第二次亲近为什么更迫切，不只是更喜欢、更投入；35–39须说明原先支撑为什么突然不再够用，不能写成热情的延续或主动想通后放松。
4. 每颗核查，但不逐颗造心理步骤。相容解释可并存；真正替代读法留在听感中，不强拼；听感画面与声音不是待复述的剧情。
5. 不靠具体往事、对白、人物习惯、新外部事件。允许固定的轻处境、当下心理起点和感受本身的时间性质。心理解释允许包含珠子没有逐字说出的信息。
6. 五段是同一件事在发展，具体前后关系有积累，不是一段段独立心理标签，也不应每段重贴同一个“珍贵所以怕失去”。Center不提前定稿。
7. 鲜活、具体、独立可读、理解有深度；保留有内容的抽象判断、必要对照与矛盾，不机械禁词。当前还未压缩，不以字数判失败，但多余心理步骤和空话要指出。
只输出JSON：{"old_best":[{"sec":"S03","source":"O1","valuable":"内容","limits":"缺陷"}],"new":[{"id":"N1","pass":false,"valuable":"具体新价值","non_regression":[{"sec":"S03","verdict":"保住/改进/回退","why":"理由"}],"continuity":"具体跨段关系与问题","problems":[{"sec":"S03","why":"问题","action":"如何修，不能靠强造情节"}],"reason":"总体判断"}],"compare":"若有多稿比较具体差别；没有可以只评一稿"}。
'''

def historical():
    segs=draft10.segs('op60'); records=[]
    for name in covjudge.OLD['op60']:
        records.append((name,[{'sec':s['id'],'text':t} for s,t in zip(segs,covjudge.sections(name))][:5]))
    for letter in 'defg':
        name='60'+letter
        path=evo.ROOT/'evaluations/beam'/name/'graph.json'
        if path.exists():
            d=json.loads(path.read_text(encoding='utf-8'))
            records.append((name,d['segments'][:5]))
    random.Random(2510).shuffle(records)
    return records

if __name__=='__main__':
    root=evo.ROOT/'evaluations/synth'; records=historical();oldmap={f'O{i}':name for i,(name,_) in enumerate(records,1)}
    old=[{'id':f'O{i}','segments':segments} for i,(_,segments) in enumerate(records,1)]
    new=[];newmap={}
    for i,tag in enumerate(sys.argv[1:],1):
        run=json.loads((root/f'{tag}_op60'/'run.json').read_text(encoding='utf-8'))
        if run['status']!='pilot_passed:S05': raise ValueError(f'{tag}: pilot not accepted locally')
        newmap[f'N{i}']=tag
        new.append({'id':f'N{i}','segments':[{'sec':sec,'chosen':state['chosen'],'hist':state['hist'],
                     'fate':state['pick']['fate']} for sec,state in run['state'].items()]})
    beads=[b for b in covjudge.beads('op60') if b['sec']<='S05' and b['role']!='演奏条件']
    msg=RULES+'\n【听感原文】\n'+json.dumps(beads,ensure_ascii=False)+'\n【旧材料】\n'+json.dumps(old,ensure_ascii=False)+'\n【新试跑】\n'+json.dumps(new,ensure_ascii=False)
    digest=hashlib.sha256(msg.encode()).hexdigest()[:12]
    out=evo.ROOT/'evaluations/continuation_20261025'/f'pilot_review_{digest}.json'
    jobs=[]
    for mdl in ('g6','g56'):
        rid=f'pr25_{mdl}_{digest}'
        if not evo.done(rid):jobs.append(node2b.job(rid,msg,{'stage':'pilot_non_regression'},w=mdl))
    print('prompt chars',len(msg),flush=True)
    evo.run_parallel(jobs,len(jobs) or 1)
    reviews={mdl:judge.parse(evo.output(f'pr25_{mdl}_{digest}')) for mdl in ('g6','g56')}
    out.write_text(json.dumps({'old_map':oldmap,'new_map':newmap,'reviews':reviews},ensure_ascii=False,indent=2),encoding='utf-8')
    print(out,flush=True)
    for mdl,result in reviews.items():print(mdl,json.dumps(result,ensure_ascii=False),flush=True)
