from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
p=read(R/'drafts/S06_compact_experiment.json')['pages'][0]
fixes=[]
def fix(block,old,new,reason):
 b=next(b for b in p['blocks'] if b['id']==block)
 assert old in b['text']
 fixes.append(dict(segment='S06',block_id=block,old=old,new=new,reason=reason))
fix('S06-C07','心事不愿公开，反复自辩：','有些心事不愿公开，念头却一遍遍回来：','原文是念头回来，不是替自己辩白。')
fix('S06-C07','双人的听法里，两人说心里话，靠近却留着防备，各自还有心事；享受亲密又转为“我有话想告诉你”。','两人说心里话，靠近却留着防备。也可以是两人想靠近，各自却有心事。\n\n另一种变化是：从享受亲密，转为“我有话想告诉你”。','三份来源的双人关系分别成立，只有第三份内部支持从享受到倾诉的转变。')
fix('S06-C10','极度温柔里待不久，记忆会走神。刚才还盯着水面，','极度温柔里待不久，记忆会走神。\n\n另一种听法是寻找刚才的感觉：刚才还盯着水面，','温柔无法久驻与找不回感觉分别保留，后一条的烦躁仍有自己的原因。')
fix('S06-C06','美好夜晚里的疑问则是：','美好夜晚里，忽然冒出疑问：','恢复原文疑问突然闯入的时点；不与另一旅行画面混用。')
fix('S06-C02','若留意高处，','\n\n若留意高处，','唱声质地与高处跳动分段，减少同一句里切换观察。')
fix('S06-C05','被爱仍会孤单，','\n\n被爱仍会孤单，','自己的意识及内心的限度与被爱仍孤单分段。')
fix('S06-C05','孤独可以使爱更深；','\n\n孤独可以使爱更深；','两个有来源的加深机制单列停顿，不使它们成为上一例必然后果。')
edits=read(R/'FINAL_EDITS.json') if (R/'FINAL_EDITS.json').exists() else []
edits=[x for x in edits if x['segment']!='S06']+fixes
if not any(x['segment']=='S07' and x['block_id']=='S07-B09' for x in edits):
 edits.append(dict(segment='S07',block_id='S07-B09',old='这份不甘，也从心底翻上来。',new='',reason='前文已具体表达不甘，删除空泛重复。'))
put(R/'FINAL_EDITS.json',edits)
put(R/'ACTIVE_VERSIONS.json',{'pages':{'S06':'drafts/S06_compact_experiment.json'},'reviews':['reviews/early_semantic_review.json','reviews/pilot_semantic_review.json','reviews/S06_compact_review.json'],'note':'S06在独立压缩复核后采用，复核发现的三种错误连接另有精确修补记录；全量后续复核完成后更新选择。'})
print('selected S06; tracked final edits',len(edits))
if __name__=='__main__':pass
