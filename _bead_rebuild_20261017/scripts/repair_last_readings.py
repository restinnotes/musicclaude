from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
edits=read(R/'FINAL_EDITS.json');pages=read(R/'CONTENT.json')['pages'];pm={p['segment']:p for p in pages}
def fix(s,b,old,new,reason):
 if any(x.get('old')==old and x['segment']==s and x['block_id']==b for x in edits):return
 assert old in next(x for x in pm[s]['blocks'] if x['id']==b)['text']
 edits.append(dict(segment=s,block_id=b,old=old,new=new,reason=reason))
for s,b,old,new,reason in [
 ('S10','S10-B04','听得更远时，整个钢琴音响仿佛化成纯粹的光与空气。','整个钢琴音响也仿佛化成纯粹的光与空气。','删来源未给的远近层级。'),
 ('S08','S08-B03','轻快也可以有不同的人物位置：像在水面上跳舞，','轻快得像在水面上跳舞，','直接进入身体图像，删分类导语。'),
 ('S10','S10-B03','到 80–83，也有更大的水势可供想象：音流从极高处如飞瀑倾泻，带着落水声。','到 80–83，音流又像从极高处倾泻的飞瀑，带着落水声。','删写作者素材分配式导语。'),
 ('S11','S11-B06','另一层极端的对照是：身体正在瓦解，','另一个画面里，身体正在瓦解，','保留有来源的强烈对照，不先命名修辞。'),
 ('S07','S07-B07','另一种听感里，先前的平静被打破，热度又回来；','另一种听感里，平静填不满灵魂深处的空洞，渴望又被点燃，热度回来；','恢复渴望再燃的空洞动因，非以热度回返代替。')]:fix(s,b,old,new,reason)
for s,b,extra,reason in [
 ('S04','S04-B09','\n\n也可以像情绪已经冲上来了，却没有能安放它的地方，只得离开这里。','保留已冲上来而无处安放所以离开的另一峰顶读法，不用尚未冲出去顶替。'),
 ('S04','S04-B08','\n\n演奏时，可以让每次重复的摇晃略有不同，像船随波来回。','保留原A的演奏变化建议，不署名为已核名家原话或作曲意图。'),
 ('S10','S10-B01','\n\n也可以像风暴过后，原以为会坠入悲剧，迎来的却是甜美的倾吐。','保留结局预期的分岔；风暴为听觉比喻，不宣称前段客观已是巨型风暴。')]:
 old=next(x for x in pm[s]['blocks'] if x['id']==b)['text']
 if not any(x['segment']==s and x['block_id']==b and extra in x.get('new','') for x in edits):fix(s,b,old,old+extra,reason)
put(R/'FINAL_EDITS.json',edits)
assemble.main()
cov={x['id']:x for x in read(R/'COVERAGE.json')};pages=read(R/'CONTENT.json')['pages'];pm={p['segment']:p for p in pages};over=read(R/'COVERAGE_OVERRIDES.json')
for i,s,b,reason in [
 ('S04-A028','S04','S04-B09','已冲上来、没有安放处、所以必须离开独立写出，保留另一完整峰顶读法。'),
 ('S04-A033','S04','S04-B08','演奏重复摇晃每次略异、如船随波来回的建议已在；不含未核署名。'),
 ('S07-A015','S07','S07-B07','填不满灵魂空洞导致渴望再燃的动因恢复，与另一感官沉醉读法分开。'),
 ('S10-A002','S10','S10-B01','风暴后原以为悲剧、却转甜美倾吐的心理预期分岔明确保留。')]:
 x=cov[i];x.update(status='full',span=next(x['text'] for x in pm[s]['blocks'] if x['id']==b),reason=reason,block_ids=[b],adjudicator='main_editor')
 over=[z for z in over if z['id']!=i];over.append(x)
put(R/'COVERAGE_OVERRIDES.json',over);assemble.main()
