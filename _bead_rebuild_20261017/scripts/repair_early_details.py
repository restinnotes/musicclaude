from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
pages=read(R/'CONTENT.json')['pages']; edits=read(R/'FINAL_EDITS.json')
def change(s,b,old,new,reason,evidence=None):
 if any(x['segment']==s and x['block_id']==b and x['old']==old for x in edits):return
 edits.append(dict(segment=s,block_id=b,old=old,new=new,reason=reason,extra_evidence=evidence or []))
change('S01','S01-B06','恰恰因为太清楚想说什么，才格外谨慎。','恰恰因为太清楚想说什么，才格外谨慎，话出口前先沉默几秒。这停顿带着分量，不是在制造悬念。','补回同一读法的沉默与心理重量，不借用前一房间场景。',[{'uid':'SRC-gpt56w-int-3-U02','quote':'话还没出口，先有几秒钟沉默。'}])
change('S01','S01-B10','一个念头浮上来了，却还没有落定。','一个念头浮上来了，却还没有落定。等摇荡真正出现，心里那句话才像有了依托。','保住S01向随后摇荡过渡的完整关系。',[{'uid':'SRC-luna-web-2-U03','quote':'接着摇荡感真正出现时，像是心里那句话终于有了依托。'}])
for b in pages[0]['blocks']:
 if '什么都不想，先看天，意识散散地飘着。' in b['text']:
  change('S01',b['id'],'什么都不想，先看天，意识散散地飘着。','什么都不想，先看天，意识散散地飘着，不开心，也不难过。','本幅傍晚看天图像独立保留不分悲喜，不借用别的身体读法。')
change('S01','S01-B12','心事却已经露了出来。','心事却已经露了出来。\n\n还有几种古怪的比法：一碗意面、喝醉的船夫在唱、一首蹩脚的法国小调。','原A具体比法保留为主观听法；未核的演奏家引语归属不转述成事实。',[{'uid':'SRC-muse-web-2-U02','quote':'这像“一碗意面”，接着像“喝醉的船夫在唱”，又像“一首蹩脚的法国小调”'}])
for p in pages:
 if p['segment']=='S03':
  for b in p['blocks']:
   if '另一路里，音乐绕远、滞留，' in b['text']:
    change('S03',b['id'],'另一路里，音乐绕远、滞留，','也可听成亲密中第一次明显的阴影：音乐绕远、滞留，','恢复同一来源的首次明显阴影，保持与主动不愿动身读法分开。')
put(R/'FINAL_EDITS.json',edits)
assemble.main()
pages=read(R/'CONTENT.json')['pages'];pm={p['segment']:p for p in pages}
overrides=read(R/'COVERAGE_OVERRIDES.json') if (R/'COVERAGE_OVERRIDES.json').exists() else []
old={x['id']:x for x in read(R.parent/'_bead_full_audit_20261017/ALL_MEANINGS.json')}
def full(i,s,b,reason):
 block=next(x for x in pm[s]['blocks'] if x['id']==b)
 x=dict(id=i,segment=old[i]['segment'],status='full',span=block['text'],reason=reason,block_ids=[b],preserved_in_segment=s,adjudicator='main_editor',source_evidence=old[i]['evidence'])
 for n,z in enumerate(overrides):
  if z['id']==i:overrides[n]=x;break
 else:overrides.append(x)
for i,b,reason in [
 ('S01-A007','S01-B01','动作对象已从码头改回小舟；深抵水底、干燥沉重码头与猛推力度齐全。'),
 ('S01-A022','S01-B06','明确并非犹豫、也无恐惧，恢复原文排除关系。'),
 ('S01-A024','S01-B06','知道想说什么所以谨慎，先沉默几秒，停顿带分量而非悬念，均在同一读法。'),
 ('S01-A053','S01-B10','念头未落定到随后摇荡给话语依托的跨段关系完整写出。'),
 ('S01-A060',next(b['id'] for b in pm['S01']['blocks'] if '什么都不想，先看天' in b['text']),'未坐稳被水带走、傍晚躺船看天、意识散飘以及不分悲喜均在同一图像；未恢复错误6/8。'),
 ('S01-A066','S01-B12','一碗意面的古怪比法明确保留；无凭据的演奏家引语归属不作为事实。'),
 ('S01-A069','S01-B12','喝醉的船夫在唱，主体、醉态与动作明确保留。'),
 ('S01-A070','S01-B12','蹩脚的法国小调明确保留，未以泛泛玩笑感代替。')]:full(i,'S01',b,reason)
full('S03-A003','S03','S03-B04','思绪恢复为风吹碎倒影的比喻主体；装饰与细小颤动只保留触发关系。')
full('S03-A025','S03',next(b['id'] for b in pm['S03']['blocks'] if '第一次明显的阴影' in b['text']),'首次明显阴影、绕远挂住、20–22暗流牵制均在；另列主动不愿前行。')
full('S05-A016','S04','S04-B05','原文27–38跨S04/S05；确信增强且因太想确信更不安全已在S04明确表达，登记跨段保留，不谎称S05重演。')
full('S05-A042','S04','S04-B02','原文27–43跨段；开心怕冷场、语速快、笑里加料、身体前倾已在S04同一读法，保留位置明确。')
full('S05-A043','S04','S04-B02','原文27–43跨段；享受转轻微焦虑，怕冷场、想多留、更甜满而喘及不想结束写在一起，未以流连代替。')
full('S05-A041','S06','S06-C07','同一37–56广域读法在S06明确写越在意越难装无所谓、优雅克制撑不住；跨段归属有实际正文。')
full('S06-A092','S06','S06-C06','恢复美好夜晚里疑问忽然冒出的时点，与旅行中预知未来怀念分开。')
put(R/'COVERAGE_OVERRIDES.json',overrides)
assemble.main()
