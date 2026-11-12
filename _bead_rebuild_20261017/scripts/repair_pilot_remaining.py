from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
edits=read(R/'FINAL_EDITS.json'); ledger=read(R/'reference/S02_ledger.json');old={x['id']:x for x in ledger}
def change(b,oldtext,newtext,ids,reason,s='S02'):
 if any(x['segment']==s and x['block_id']==b and x['old']==oldtext for x in edits):return
 evidence=[]
 for i in ids:evidence+=old[i]['evidence']
 edits.append(dict(segment=s,block_id=b,old=oldtext,new=newtext,reason=reason,extra_evidence=evidence))
change('S02-B05','仍能自然笑谈，却已知道这样的时刻并非取之不尽；','仍能自然笑谈，却已知道这样的时刻并非取之不尽。经历过离别，再遇到极温柔的时刻，会先防备地想：“还能多久？”',[ 'S02-A009'],'恢复经历离别到防卫预问的原文动因，不以泛泛时刻有限顶替。')
change('S02-B04','只是眼前太值得留恋。','只是眼前太值得留恋。\n\n美好夜晚散步时，也会多看对方一眼，确认这份亲近是真的。',['S02-A040'],'自己看对方以确认真实，与对方看自己而满足分开。')
change('S02-B06','眼前越好，越想让它慢一点：','眼前这个人、这个下午、这种亲近很重要，不想再做什么，只盼时间慢一点。也有一种更酸楚的预感：',['S02-A043'],'保留重要而无需行动的满足；另起酸楚画面，不把不同人的场景绑定。')
change('S02-B11','向上也先收住，不急着把感情全部放出来；','向上也先收住，不急着把感情全部放出来。也可以是感情很深，却不愿把自己完全暴露；',['S02-A045'],'自我暴露的动因独立保留，不与维护气氛或演奏留余地等同。')
change('S02-B12','小峰顶一过，就像梯田一层层落下来。','小峰顶一过，就像梯田一层层落下来。\n\n到16小节附近，也可以听出忽明忽暗：从这里开始担心，眼前的美好会不会变。',['S02-A058'],'保住16附近的明暗及从此开始担心，不借7/9/11尾音变色充当对应。')
change('S02-B03','两个人的呼吸和体温贴得化不开。','两个人的呼吸和体温贴得化不开。\n\n也能听到感官的陶醉和小心翼翼并存：珍惜此刻的亲近，却不敢信它能持续。',['S02-A063'],'感官陶醉与持续性不信任在同一读法中保留。')
# Add two sound readings without turning the private duet into one fixed cast.
pages=read(R/'CONTENT.json')['pages'];p=next(p for p in pages if p['segment']=='S02');b=next(b for b in p['blocks'] if b['id']=='S02-B07')
if not any(x['segment']=='S02' and x['block_id']=='S02-B07' and '女高音' in x['new'] for x in edits):
 change('S02-B07',b['text'],b['text']+'\n\n三度、六度的歌，也像意大利歌剧里的女高音。另有一种更沉的二重唱：一对恋人贴着唱，死亡却威胁着他们。',['S02-A077','S02-A081'],'保留女高音与受死亡威胁恋人的两种声音比喻，不补未核的评论家署名。')
change('S04-B01','同样的歌再来，更动情，也更不安分，却仍先按住：想开心，又不敢全开心。','同样的歌再来，更动情，也更不安分，却仍先按住：想开心，又不敢全开心。\n\n从12到34小节连着听，也像情绪终于不必藏得那么好；高兴起来了，问题却还没解决，反而越美越舍不得。',['S02-A062'],'12–34跨段发展的读法放在S04，保留放开情绪与问题未解决的区别。',s='S04')
put(R/'FINAL_EDITS.json',edits)
assemble.main()
pages=read(R/'CONTENT.json')['pages'];pm={p['segment']:p for p in pages};over=read(R/'COVERAGE_OVERRIDES.json')
assign={'S02-A009':('S02','S02-B05'),'S02-A040':('S02','S02-B04'),'S02-A043':('S02','S02-B06'),'S02-A045':('S02','S02-B11'),'S02-A058':('S02','S02-B12'),'S02-A063':('S02','S02-B03'),'S02-A077':('S02','S02-B07'),'S02-A081':('S02','S02-B07'),'S02-A062':('S04','S04-B01')}
for i,(s,b) in assign.items():
 block=next(x for x in pm[s]['blocks'] if x['id']==b)
 reason=next(x['reason'] for x in reversed(edits) if x['segment']==s and x['block_id']==b)
 x=dict(id=i,segment='S02',status='full',span=block['text'],reason=reason,block_ids=[b],preserved_in_segment=s,adjudicator='main_editor',source_evidence=old[i]['evidence'])
 over=[z for z in over if z['id']!=i];over.append(x)
put(R/'COVERAGE_OVERRIDES.json',over)
assemble.main()
