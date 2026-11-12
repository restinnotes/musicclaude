"""Concrete source-fidelity repairs. Preserve rejected reviews and all original artifacts."""
import copy
import hashlib
import json
import covjudge
import evo
import synth_v2
import finish_thread_25 as finish

def edit(ix,iid,text,key,why,receipt):
 i=ix[iid];receipt.append({'id':iid,'before':i['text'],'after':text,'why':why});i['text']=text;i['key']=key

if __name__=='__main__':
 for key in ['C25whole60_op60','C25op61body2_op61']:
  work=key.rsplit('_',1)[1];p=finish.OUT/(key+'_plain.json');g=json.loads(p.read_text(encoding='utf-8'));old=p.read_bytes()
  backup=finish.OUT/(key+'_plain_before_fidelity_repair.json')
  if backup.exists():raise ValueError('repair already applied')
  backup.write_bytes(old)
  source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
  ix={i['id']:i for s in g['segments'] for i in s['items']};edits=[];removed=[];changed=[]
  if work=='op60':
   edit(ix,'I15','先前亲近尚能暂时安定；如今越充分，延续需要越真切，反而更难安住眼前。','同样亲近如今更难安定','明确原来有效、如今功能改变的准确基线，不只把谨慎暂松当充分历史。',edits)
   edit(ix,'I25','用力退下带来松动，未解的牵挂留下孤单；轻下来的并不是已经想通的心。','身体松动与未解牵挂分属两因','恢复松动和孤单各自原因，以及并非想通的关键排除项。',edits)
   edit(ix,'I81','亲近与独自快乐都已真实发生；以后虽无保证，它们已不只是尚待实现的可能。','两种幸福都不再只是可能','在本条明确两种经验共同承担的前提，保留以后未知。',edits)
   ix['I81']['follows']=False
   drop={('I3','I5'),('I5','I9'),('I6','I10'),('I5','I22'),('I13','I25'),('I5','I27'),('I23','I29'),('I28','I34'),('I3','I39'),('I3','I53'),('I23','I55'),('I60','I67'),('I72','I78'),('I3','I79'),('I28','I80')}
   for s in g['segments']:
    keep=[]
    for a in s['because']:
     pair=a['from'],a['to']
     if pair in drop:removed.append({'sec':s['sec'],**a});continue
     if pair==('I30','I33'):
      changed.append({'before':copy.deepcopy(a),'why':'真正支持再靠近的是更清楚仍想亲近的I31，不是只感到余温的I30。'});a['from']='I31'
     if pair==('I39','I44'):a['rel']='提供理由'
     if pair==('I5','I15'):a['how']='同样的亲近曾可暂时安定；新增延续需要改变了它如今的作用。'
     if pair==('I23','I26'):a['how']='失去眼前的安顿之后，仍能独自快乐，使空落不等于已经失去全部美好。'
     if pair==('I19','I60'):a['how']='24–34曾因深情不能保证以后而哽住；无保证也能快乐的经历，使这部分热切如今能释放。'
     if pair==('I67','I72'):
      a['rel']='限制';a['how']='继续涌动不等于先前没有释放；刚才充分展开的幸福确实已经得到。'
     keep.append(a)
    s['because']=keep
   next(s for s in g['segments'] if s['sec']=='S11')['because'].append({'from':'I23','to':'I58','rel':'提供理由','how':'失去过直接安慰，后来重新真切的温柔便带着不舍与心疼。'})
  else:
   edit(ix,'I13','曾珍惜的生活显出分量，先前说不清的难受，也就有了足以牵动他的内容。','熟悉生活使难受有了内容','补明当前内容增加的原因，而不是以前的模糊造成如今清楚。',edits)
   edit(ix,'I33','先前至少还能靠不断用力使自己不至停住，如今连维持这股用力的力气也渐渐耗尽。','连维持用力也渐渐无力','保住旧支撑至少能防止停滞的具体功能，不只笼统写撑着自己。',edits)
   edit(ix,'I42','想重新相连的盼望，使愿望的表达变得更充实、更迫切。','愿望表达更充实迫切','恢复歌唱所指的表达层增量，不改成柔情的强度，也不实化为实际开口唱。',edits)
   edit(ix,'I43','愿望已有位置，却仍没有回应；即使充分敞开，这份表达也还未真正完成。','敞开而未回应也未完成','恢复两个不同限制：没有回应，以及表达本身尚未完成。',edits)
   edit(ix,'I45','熟悉生活的零星亲切感忽然闯入，没顺着深沉的祈求继续，反而猛地照出缺席。','零星熟悉感突然照出缺席','恢复零星这一原有限定，保留异质突入。',edits)
   edit(ix,'I47','那一下惊悸是身体先碰到落差；鲜明的舞步听感并不排斥同时的寒意。','舞步听感鲜明而仍有寒意','保留具体听感对照，明确舞步属于听感而非人物真的跳舞。',edits)
   edit(ix,'I58','长久反复耗去力气，此刻只能断续触到珍惜之物；虽仍珍惜，也已难以完整沉入其中。','疲惫使珍惜之物难再充分进入','明确疲惫使他难以完整进入感受，避免错写成客体进入当下的主语转换；保留此刻与仍然重要。',edits)
   sg=next(s for s in g['segments'] if s['sec']=='S11')
   sg['items'].append({'id':'I82','text':'压力仍在，但继续前行已不必先把柔弱排除在自己之外。','key':'前行不以排除柔弱为条件','follows':False,'sources':[2],'explains':['S11-B2']})
   ix['I61']['follows']=True
   sg7=next(s for s in g['segments'] if s['sec']=='S07');byid={i['id']:i for i in sg7['items']}
   sg7['items']=[byid[iid] for iid in ['I44','I45','I47','I46','I48','I49','I50']]
   ix['I46']['follows']=False;ix['I47']['follows']=True;ix['I48']['follows']=True
   drop={('I8','I12'),('I1','I13'),('I14','I21'),('I3','I39'),('I41','I48')}
   for s in g['segments']:
    keep=[]
    for a in s['because']:
     if (a['from'],a['to']) in drop:removed.append({'sec':s['sec'],**a})
     else:keep.append(a)
    s['because']=keep
   next(s for s in g['segments'] if s['sec']=='S04')['because'].append({'from':'I15','to':'I29','rel':'提供理由','how':'早先用力反使眷恋更可感；此刻温暖更鲜活，原有的不安又被加剧。'})
   next(s for s in g['segments'] if s['sec']=='S06')['because'].append({'from':'I35','to':'I39','rel':'提供理由','how':'强撑已经无以为继，才有片刻愿望不必随强硬立即压回。'})
  # Deliver the main Thread and the unchanged independent bead/readings record as separate layers.
  # This annex is explicitly not a set of new thoughts in the protagonist's causal story.
  for s in g['segments']:
   st=source['state'][s['sec']]
   s['bead_dispositions']=[{'original':b,'author_disposition':st['pick']['fate'].get(b['id'],'演奏条件；不作为人物心理步骤'),'independent_check':next((z for z in st['check']['coverage'] if z['id']==b['id']),None)} for b in covjudge.beads(work) if b['sec']==s['sec']]
  g['record_scope']='items为单一Thread；bead_dispositions为逐字保留的独立珠子与听法记录，不强并为人物心理步骤。because是历史关系字段，rel=改写指后来经历改变早先意义或作用，不是同义转述；只有真实历史作用才能连。'
  g['fidelity_repairs']=edits
  finish.validate(g,source);synth_v2.dump(p,g)
  synth_v2.dump(finish.OUT/(key+'_fidelity_repairs.json'),{'before_sha256':hashlib.sha256(old).hexdigest(),'text_repairs':edits,'removed_arrows':removed,'corrected_arrows':changed,'independent_records':'All original beads and their exact dispositions retained in separate per-section annex; no forced insertion into main Thread.','non_adopted_review_rules':['Do not treat all rel=改写 as synonymous paraphrase or disallow it just because the field is named because; user explicitly permits genuine retrospective changes of meaning.','No follows merely for a demonstrative reference or chronological next step.','Independent and alternative readings stay outside the selected psychological chain.'],'center_scope_unchanged':'Repairs restore original distinctions; no source-selected story or Center basis is replaced. Existing independently accepted Center candidates remain subject to final main comparison.'})
  print(key,'fidelity repairs saved',len(edits),'text edits;',len(removed),'arrows removed',flush=True)
