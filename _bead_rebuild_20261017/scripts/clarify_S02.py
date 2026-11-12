from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
edits=read(R/'FINAL_EDITS.json')
changes=[
 ('S02-B08','同一句话说三遍，可以听成：','在7、9、11小节那几次同音停留里，像同一句话说三遍：','安慰犹豫疼附上该来源明确的位置，不扩为其他两套读法共享的精确映射。'),
 ('S02-B08','也像“我们在这里”变成','\n\n另一种三次变化是：“我们在这里”变成','两套三次变化分别成立，不暗示逐项翻译。'),
 ('S02-B11','才给后面的释放留出余地。','才给后面的释放留出余地。\n\n也可以是有话想说，又把话收住；若有悲伤，是知道好时光不会长留，还不到绝望或失恋的沉痛。','保留有限好时光而非绝望失恋的限定，不以一般微痛顶替。')]
for b,old,new,reason in changes:
 if not any(x['block_id']==b and x.get('old')==old for x in edits):edits.append(dict(segment='S02',block_id=b,old=old,new=new,reason=reason))
put(R/'FINAL_EDITS.json',edits);assemble.main()
pages=read(R/'CONTENT.json')['pages'];p=next(p for p in pages if p['segment']=='S02');cov={x['id']:x for x in read(R/'COVERAGE.json')};over=read(R/'COVERAGE_OVERRIDES.json')
for i,b,reason in [('S02-A074','S02-B08','另一套三次变化明确分段，确认—疑问—期限顺序保留，不等同安慰—犹豫—疼。'),('S02-A082','S02-B08','7、9、11同音停留及安慰、犹豫、疼的三次顺序均在。'),('S02-A060','S02-B11','想说又收住、悲伤若有是因好时光有限、非绝望失恋沉痛，均明确写出。')]:
 x=cov[i];x.update(status='full',span=next(x['text'] for x in p['blocks'] if x['id']==b),reason=reason,block_ids=[b],adjudicator='main_editor')
 over=[z for z in over if z['id']!=i];over.append(x)
put(R/'COVERAGE_OVERRIDES.json',over);assemble.main()
