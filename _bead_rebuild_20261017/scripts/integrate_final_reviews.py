from pathlib import Path
import json
import assemble
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
edits=read(R/'FINAL_EDITS.json'); pages=read(R/'CONTENT.json')['pages'];pm={p['segment']:p for p in pages}
def fix(s,b,old,new,reason):
 if any(x.get('old')==old and x['segment']==s and x['block_id']==b for x in edits):return
 assert old in next(x for x in pm[s]['blocks'] if x['id']==b)['text'],(s,b,old)
 edits.append(dict(segment=s,block_id=b,old=old,new=new,reason=reason))
fix('S04','S04-B08','上面的歌声悬着，下面的水波还推着它走。','上面的歌声悬着，下面的水波却推着人不得不往前走。','回原A恢复受动者为听者，不是歌声。')
fix('S07','S07-B10','好不容易想象出一个温暖的地方，','\n\n另一幅画面里，好不容易想象出一个温暖的地方，','新鲜地方与幻想住所为并列图像，不是同一行程。')
fix('S07','S07-B10','想享受当下，脑子又飘到旧事和未来：','\n\n也可以是想享受当下，脑子又飘到旧事和未来：','想象住所与走神旧事未来分别成立。')
fix('S07','S07-B08','久坐后起来走走，半夜睡不着翻身，想找回刚才的感觉却找不到：','像久坐后起来走走，也像半夜睡不着翻身。想找回刚才的感觉，却找不到：','恢复两种身体比喻，不串作一个人先走后失眠的经历。')
fix('S04','S04-B10','酸楚也可能指向不同的东西。一种像快乐旅行途中，','一种酸楚，像快乐旅行途中，','删抽象分类导语，直接进入具体旅行。')
fix('S13','S13-B04','m.103 以后，长期寻找的东西已经真的得到，问题也换了方向：','m.103 以后，也可以像终于得到了长期向往的东西，反而不知怎样承受：','可选心理类比不升级成此人确实获得某物的事件。')
fix('S13','S13-B17','还有一种清明，是发现自己原来可以如此强烈，同时也如此平静。像吵过架后真正和好，或大哭一场后替爱人擦脸，轻里带着照料与原谅；和先前 mm.33 那种想逃的轻相比，它更像落地。','','暂停Muse-int2错位单元的独立局部背书，保留另有有效来源的玩心。')
fix('S14','S14-B19','也可以把这个结尾听成漫长旅程之后，终于得以从容面对死亡的宁静。','回看整首作品，也可以像经历漫长旅程之后，终于得以从容面对死亡的宁静。','恢复原稿全曲范围；末页回看不等于尾声独有意义。')
for s,b,old,new,reason in [
 ('S12','S12-B03','也可以把这持续的狂喜感到像一场高烧：肉体与精神在顶点完全合一，整个人都在同一阵热里。','这持续的狂喜也像一场高烧，肉体与精神在顶点完全合一。','修搭配，删重复总结。'),
 ('S12','S12-B14','景象也从运河里的涟漪扩成外海大浪；水面的尺度，带着人的意志一起改变。','运河里的涟漪像扩成了外海大浪，也映出这份要求幸福的意志。','理顺意志与水面比喻的对应方向。'),
 ('S12','S12-B19','还有一种读法，从先前的精神涤荡回到尘世，把眼前的爆发感到像生命熄灭前最后的燃烧。','也可以感到，先前精神涤荡之后回到尘世，眼前的爆发像生命熄灭前最后的燃烧。','去除把读法当回归主体及生硬搭配。'),
 ('S13','S13-B05','这两种暴露，一种是藏不住，一种是愿意撤下防护；都来自事情太重要，已经无法平静承受。','事情太重要，已经无法平静承受。','具体区别已在前文，删除编辑再分类。'),
 ('S13','S13-B19','这两种演法，把结束前的心情带向不同地方。','','演奏条件及各自效果已写清，删泛泛总结。'),
 ('S14','S14-B18','光亮没有把这些疲惫抹掉。','','用力代价和光荣地累已在，删审计自证式收尾。')]:fix(s,b,old,new,reason)
removed=[('S12','S12-B21','水晶瀑布和高烧后冷汗依附于已否定的93–102全面退潮链，暂无独立局部支持。'),('S14','S14-B10','溺水求生及转瞬失败依附未核111–113极高上冲触发，不能删除小节号后当作合法局部听法。')]
quarantine=[]
for s,b,reason in removed:
 block=next(x for x in pm[s]['blocks'] if x['id']==b);quarantine.append(dict(segment=s,block=block,reason=reason))
 if not any(x.get('remove_block') and x['block_id']==b for x in edits):edits.append(dict(segment=s,block_id=b,remove_block=True,reason=reason))
put(R/'FINAL_EDITS.json',edits);put(R/'QUARANTINED_BLOCKS.json',quarantine)
cov=read(R/'COVERAGE.json');over=read(R/'COVERAGE_OVERRIDES.json')
for x in cov:
 for s,b,reason in removed:
  if b in x.get('block_ids',[]):
   entry=dict(id=x['id'],segment=s,status='pending',span='',reason='未作为本段正文保留：'+reason,block_ids=[],adjudicator='main_editor',quarantined_block=b)
   over=[z for z in over if z['id']!=x['id']];over.append(entry)
put(R/'COVERAGE_OVERRIDES.json',over)
assemble.main()
# Explicitly update the one repaired subject, not every row mentioning that block.
c={x['id']:x for x in read(R/'COVERAGE.json')};x=c['S04-A002'];x.update(status='full',reason='右手歌声悬停，左手水波迫使听者前行；受动者已回原A修正。')
over=[z for z in over if z['id']!='S04-A002'];over.append(x);put(R/'COVERAGE_OVERRIDES.json',over)
assemble.main()
