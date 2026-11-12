"""Main editorial disposition of every model rewrite; keep raw patches and concrete reasons."""
import copy
import json
import hashlib
import evo
import synth_v2
import finish_thread_25 as finish

FIXES={
 'C25whole60_op60':{
  'I23':('原先，眼前的亲近还足以让他暂时安定；如今却已不够，空落只能由自己承受。','眼前亲近已不足以暂时安定','模型漏掉暂时限定；早段并非完全消除谨慎或获得永久安心。'),
  'I46':('想继续的冲动卡在这里，注意反而更集中，心里仍有没落定的余响。','冲动凝住而注意集中','原综合没有指定注意集中于未来疑问；删掉润色时新增的注意对象。'),
  'I59':('有过无保证也能快乐的经验，充分感受自己的深情，此刻也有了价值。','无保证的快乐改变深情的价值','保住已实际经历的原因和此刻限定，去掉重复长句；I39箭头仍承载该经验。'),
  'I61':('最初相伴的安稳，和后来独自仍有的快乐，此刻一同充满重新真切的亲近。','两种快乐一同充满亲近','保留两个经验同时在场及重新直接感到亲近，不靠长修饰串或混为一种。'),
  'I64':('眼前已有这么多值得珍惜的东西，心思不再只围着自己得到多少打转，而被丰盛吸引。','丰盛使心思离开自身得失','承接I63的具体价值和结果限制，保留主体退后的原因；避免把答案当成美好的成员或作道德评判。'),
  'I67':('直到情感真正充分展开，仍被“能否延续”悬着的那部分热切才得到释放。','仍悬着的热切得到释放','S11已有部分释放，故不用一直暗示至此未曾释放；保住S12尚有期待、牵扯与此刻充分展开。'),
  'I71':('身体仍被刚才幸福的分量牵动；越觉得确实得到了，越舍不得让它过去。','幸福越真实越舍不得过去','幸福对象在句内交代；不把得到扩为对方承诺，也不删已达满足和仍不舍。'),
  'I72':('刚才悬着的热切已经释放，他却仍有停不下、想继续向前的冲动。','热切释放后仍想向前','保留已释放与仍不能停的真实区别，不用长指代补句制造重复。'),
  'I73':('亲近与深情越真切，越显出它们既留不住时间，也不能替对方决定以后。','真切仍不能留住时间或决定对方','保留时间流逝与他人意愿两个不同限制，直接表达各自关系，不合为含混的替时间决定。')},
 'C25op61body2_op61':{
  'I17':('抗拒不只为体面：珍惜之物仍与他有关，他不愿自己连同这份关联被失落抹去。','抗拒也为守住自己与关联','接受模型恢复自身不被抹去、纠正有关不等于已相连；保留原因和对照，去掉重复指代。'),
  'I38':('暂时少了防备，才有仿佛与外界隔开的安宁；失落并未因此得到外界的弥补。','少一层防备的暂时安宁','保留安宁的心理原因、暂时性、仿佛和失落未获外界弥补的限制。'),
  'I42':('想重新相连的盼望，使柔情越来越充实，也越来越迫切。','盼望使柔情更充实迫切','原综合用歌唱表达听感，此处写其心理意义；不凭空写人物实际开口唱歌，也不把音乐作为心理原因。'),
  'I43':('愿望已有了位置，却仍没有回应；充分敞开，也还不能使这份盼望获得着落。','愿望敞开仍未获着落','保留愿望被完整感到却仍未完成的关系，不把音乐句子未说完实化为人物实际说过一句话。'),
  'I45':('熟悉生活的亲切感忽然闯入，没顺着深沉的祈求继续，反而猛地照出缺席。','熟悉感突然照出缺席','保留突兀、异质性及当下缺席的反向作用；不是由祈求必然引出记忆。'),
  'I47':('那一下惊悸是身体先碰到这种落差；鲜活的亲切与寒意可以同时存在。','亲切鲜活与寒意共存','原稿舞步鲜明是感受的音乐呈现，不能暗示人物真实跳舞；保住鲜活亲切与寒意的同时性。'),
  'I49':('心思在想靠近与无处靠近之间反复；惊悸过后，身体仍像有事未了，不能停住。','惊悸后身体仍停不下来','采纳模型反对主动不肯的意见，同时把无事可做限定为当下身体感，不能扩大为客观上一切可能都已不存在。'),
  'I54':('挺立、温暖的刺痛和敞开愿望的经历，使最初无从安放的失落不再空无内容。','经历让失落有了内容','接受恢复三种已经发生的经历；此处辨认的是牵挂的感受内容，不断言已认出一个具体人物或往事。'),
  'I57':('再次触到最初的失落：挺立带不回过去，安宁也不能让愿望得到回应。','挺立与安宁各有不能替代的事','两种状态各自的限制不能只靠空泛归处替代；下条继续承接它们真实有效却不足以安顿的判断。'),
  'I65':('早先主要靠用力维持姿态，如今柔弱中的向往也能推着他走，压力仍在。','向往也进入向前的力量','不采纳模型恢复过去必须排除柔弱的措辞。H4/H6已确立早期力量、脆弱、自控共存；阶段变化是向往也成为动力。保留压力，未添加新决定。'),
  'I69':('站稳不是从未受伤；原本私下才能敞开的愿望，如今也能向外显露。','私密愿望也能向外显露','保留内外表达的真实对照，不把公开存在升级为现实公众场合或集体活动。')}
}

if __name__=='__main__':
 for key,fixes in FIXES.items():
  p=finish.OUT/(key+'_plain.json');raw=p.read_bytes();g=json.loads(raw.decode('utf-8'))
  backup=p.with_name(key+'_plain_before_main_review.json')
  if backup.exists():raise ValueError('main review already applied; inspect receipt rather than applying twice')
  backup.write_bytes(raw)
  ix={i['id']:i for s in g['segments'] for i in s['items']};edits=[]
  for iid,(after,keytext,why) in fixes.items():
   item=ix[iid];edits.append({'id':iid,'before':item['text'],'after':after,'defect':why,'loss_check':'核对原始综合、当前History和相邻条目及箭头；未新增人物事件、主动顿悟或永久结论。'})
   item['text']=after;item['key']=keytext
  if key.startswith('C25op61body2'):
   ix['I65']['sources']=[1,2]
   sg=next(s for s in g['segments'] if s['sec']=='S10')
   sg['items'].insert(1,{'id':'I81','text':'它们仍会触动他，却哪一种都不足以让他整个人安顿下来。','key':'真实有效仍不足以安顿','follows':True,'sources':[1],'explains':['S10-B1','S10-B2']})
  g['main_edits']=edits
  g['main_review_note']='All model edits read. Accepted changes keep their original defect/loss receipts. Main corrections preserve temporary qualifications and distinguish analytical reasons from conscious decisions. One long S10 Op61 thought split into two natural units without removing either limit.'
  source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
  finish.validate(g,source)
  synth_v2.dump(p,g)
  synth_v2.dump(finish.OUT/(key+'_plain_main_review.json'),{'model_plain_sha256':hashlib.sha256(raw).hexdigest(),'all_model_edits_read':True,'model_blocked_edits':g['blocked_edits'],'main_corrections':edits,'structural_corrections':(['I65 sources include both original explanations','I57 long causal thought split; new I81 retains effective-yet-insufficient judgment'] if key.startswith('C25op61body2') else []),'status':'Main review complete; independent full fidelity checks pending'})
  print(key,'reviewed; main corrections',len(edits),'over45',[(i['id'],len(i['text'])) for s in g['segments'] for i in s['items'] if len(i['text'])>45],flush=True)
