"""Faithful graph -> plain language -> Center, deliberately in that order.
Each stage is separately reviewable. No result becomes accepted just because a model returned JSON.
"""
import hashlib
import copy
import json
import sys
from pathlib import Path
import evo
import node2b
import synth_v2

OUT=evo.ROOT/'evaluations/continuation_20261025/finalization'
OUT.mkdir(parents=True,exist_ok=True)
GRAPH='''把已经逐段验收的Thread整理成关系图。现在不写Center；Center只在全曲关系图及人话版完成后归纳。
忠实保留所有有内容的因果、矛盾、对照、限定及远处历史关系，不替作者补新理解。不照原文逗号切句，不按所求/恐惧/办法等人为类别拆。
每个条目是一句普通人能理解的话、一个念头或一步。一般20–45字；字数服从保留关键理由，太长可拆成自然的因果两条。不要为了短删掉有内容的抽象判断，也不机械禁词。
同段后一条真由上一条推出才标follows:true；情绪并存、例子并列、时间先后本身都不算因果。每条有id和清楚的短语key。
跨段because只是历史关系字段名，实际只连原文明确/明显成立的理由、限制、改写或唤起，不按主题相似乱连，不凑每条都有箭头。改写指后来经历改变早先的意义或作用，不是同义换说法；单纯前后阶段、复述、对照或指代也不够。每种关系不都等于唯一充分的因为所以；需写清早先经历在此刻实际起什么作用。from必须更早段，to当前段；rel只取提供理由/动摇/限制/改写/唤起。how只在补充两端未说出的关系时填写。
原稿回顾前史的长句，尽量以跨段箭头承载；仍须让当前条目读得懂。不要把过去事实误写成当前的新发现。远处经历的具体内容与作用不能丢。
原稿的比喻、限定、相容体验、替代读法不可以自行变成人物事件。画面/音响不作心理原因。
分析者给出的心理原因，不可自动改成主人公当下主动想通、决定、或对自己说的一段话。
输出JSON：{"segments":[{"sec":"S01","bars":"1–3","items":[{"id":"I1","text":"一句","key":"清楚短语","follows":false,"sources":[1],"explains":["S01-B1"]}],"because":[{"from":"I1","to":"I7","rel":"限制","how":"必要时一句"}]}]}。
sources为此段原文第几条选中解释，可以同条多次或一条涵盖数条。每项experiences依据只用本段听感ID，不强制每颗都一项；不把替代听法强编入主线。所有段按源顺序且bars照抄。
'''
PLAIN='''把关系图里的条目写得更自然、具体、鲜活，让普通人一遍能读懂；保留每个有内容的抽象判断、重要矛盾、因果前提、否定和限定。
这不是另写故事：不改人物处境、不补往事/对白/事件/心理决定，不把暂时感受升级为永久认识。修改须指出真实阅读缺陷，若原句已清楚就照留。不因“抽象”二字一概抹掉判断，不用机械禁词表。
不要把解释者的因果分析改写成人物的顿悟、决定、自我劝说或内心台词。
保持全部id、sec、bars、sources、explains、follows和because不变，只改text/key；若不拆不足以保留内容，可以保留较长一句并在edits中注明，不因45字丢理由。
尤其保住比较基线和正向增量：更清楚地感到，不能压成仅仅没有消失；先前已经有什么、如今多出什么须分清。两种原因共同造成不同感受，不能压成同一原因；已得到而仍未解除的两面也不能互相顶替。
只返回有实际缺陷的条目修改，不重复整图；程序会将修改应用到相同id，结构保持原样。before必须完整照抄当前原句。每一处改动给出defect（具体原缺陷）与loss_check（原内容和限定如何保住）。无缺陷不改，不能为说明改动而编造原文缺陷。
若发现结构或内容的错误不能通过忠实改措辞解决，请列blocked_edits，不擅自换理由。
输出JSON：{"edits":[{"id":"I1","before":"完整原句","after":"新句","key":"清楚短语","defect":"具体缺陷","loss_check":"信息检查"}],"blocked_edits":[]}。
'''
VERIFY='''请以原始逐段综合为基准，绝对验收这张人话关系图，不能只看流畅。
交付记录包含两层：items是单一Thread，bead_dispositions逐字保存独立珠子、相容及替代读法与去处。它们不得被强并为主线中的心理步骤；原文和去处在独立记录中完整保留，就不算从交付中删掉。
because只是沿用的字段名，实际按rel核查提供理由/动摇/限制/改写/唤起这五种真实历史作用，不把每种都误读成唯一充分的“因为所以”。改写指后来经历改变早先的意义或作用，不是同义改写；但仅有前后阶段、相似、无作用的引用或对照仍不合格。follows只用于真实因果或心理推出，单纯指代上一条不要求加箭头，也不因一条箭头没有独占全部前因就判它无效。
标准继承：具体why-now、真实History因果、一件事持续发展、关键旧稿价值不退步；比喻不实化，不靠新前史、对白、事件、主动想通的情节。合理心理推导允许超出珠子逐字内容。
图必须保住源稿全部实质理解、关键矛盾、对照、限定和远处因果。逐段写原有实质内容与图中对应条目，遗漏不靠想象替图补回。
每一条同段follows与跨段because都核对：是真因果，还是并列、先后、相似；箭头能否独立承载原稿省去的前因。每个实质失真给出原句、图中具体ID与最小修法。
文字需具体、鲜活、独立可读、有效率；有内容的抽象判断是允许的，不能为了短机械删。正式Center尚未归纳，因此不因没Center判失败，也不提前写它。
关键位置：Op60的S03舒服+急切+暗流共存，S04第二次迫切的增量，S05支撑失效，S06–07另一种快乐与S06被利用，S11延迟释放，S12早期亲近与40–61真实经验相遇且自身退后，S13已达满足却仍难停止；Op61的S01无对象恍惚与尊严/疲惫，S02脆弱且控制更费力，S03焦躁至温柔刺痛，S04反刍与被时间催着走的身体压力有不同原因，二者不能互相顶替，S06愿望敞开更迫切，S07异质打断并不硬编材料身份，S13柔软凭前史成为力量而非“变坚强”标签。
只输出JSON：{"pass":true,"segments":[{"sec":"S01","retained":["原义→ID"],"missing":[],"invented":[]}],"arrow_problems":[],"problems":[],"reason":"具体总体理由"}。pass真必须missing/invented/arrow_problems/problems都无实质问题，建议另写suggestions。
'''
CENTER='''根据已经完成的人话关系图，事后归纳3个候选Center。Center是整条Thread围绕的最小关系句，以核心名词和关系构成；不能以“他如何做/学会/选择”为中心，不能列几个情绪，不预告发展路线或结局，不用空泛的“爱与失去”等两词并列。
一句抓住：什么确实重要，以及什么关系使它不能轻易得到安顿。简洁服从具体意思，不为字数丢核心。不要强求把全曲每段逐字塞入Center，也不能只概括开头或最后答案。
三个选项须有实际差别；指出每项覆盖、偏差及为何无法提前从开头定稿。
输出JSON：{"options":[{"id":"C1","text":"最小关系句","basis":["具体跨段关系"],"risk":"偏差"}],"recommendation":"C1"}。
'''
CSCORE='''请独立绝对验收三个事后归纳的Center，允许全不合格。继承标准：最小名词关系句，具体同一件事的核心困难，不写人物行动、不列情绪、不预告路线/结局，不以结尾领悟代替核心矛盾。不因最短就优先；不强制每段都在想Center。
根据整图判断是否遗漏实质发展、把允许的轻处境扩大为确定剧情、过早缩到一个局部。不替选项改写成更好句后判原句通过。
每个通过选项再给全部段落与它的关系，relation只能正在面对/还说不清/没在想，真实判断，无比例要求。
正在面对指此刻实际在想、承受或处理核心问题；还说不清指感到牵动但尚不能辨明；没在想指沉浸于别的感受，核心问题暂时不在心上，即使因果上受历史影响。不要把分析者写出的因果解释都当成人物正在给自己讲道理。
没有主动概念化、不在全部注意的中心，不自动等于还说不清；还说不清须有尚不能辨明的证据。实际承受核心困难的痛感或牵扯，也可以是正在面对。
输出JSON：{"options":[{"id":"C1","pass":true,"why":"理由","relations":[{"sec":"S01","relation":"还说不清","why":"具体理由"}]}],"choice":"C1或无","reason":"理由"}。
'''

def call(label,msg,model):
 rid='finish25_'+label+'_'+hashlib.sha256((model+msg).encode()).hexdigest()[:12]
 if not evo.done(rid):node2b.job(rid,msg,{'stage':'finalization','label':label},w=model)[1]()
 return synth_v2.judge_synth_v3.parse(evo.output(rid))

def validate(g,source):
 expected=list(source['state']);ss=g.get('segments',[])
 if [s.get('sec') for s in ss]!=expected:raise ValueError('wrong segment inventory/order')
 ids={};rels={'提供理由','动摇','限制','改写','唤起'}
 for k,s in enumerate(ss):
  seg=next(z for z in synth_v2.synth.draft10.segs(source['work']) if z['id']==s['sec']) if 'work' in source else None
  if seg and s['bars']!=str(seg['start'])+'–'+str(seg['end']):raise ValueError('graph changed original section boundaries')
  for n,item in enumerate(s['items']):
   if item['id'] in ids:raise ValueError('duplicate item id')
   if n==0 and item.get('follows'):raise ValueError('first item cannot follow absent same-section item')
   if not item.get('text') or not item.get('key') or not item.get('sources'):raise ValueError('empty or untraceable item')
   if any(not 1<=i<=len(source['state'][s['sec']]['chosen']) for i in item['sources']):raise ValueError('invalid source mechanism')
   ids[item['id']]=k
 for k,s in enumerate(ss):
  for a in s.get('because',[]):
   if a['from'] not in ids or a['to'] not in ids or not ids[a['from']]<k or ids[a['to']]!=k or a['rel'] not in rels:raise ValueError('invalid cross-segment arrow')

def attach_independent_records(g,work,source):
 """Keep every original bead and disposition outside the selected protagonist's steps."""
 import covjudge
 beads=covjudge.beads(work)
 for s in g['segments']:
  st=source['state'][s['sec']]
  s['bead_dispositions']=[{'original':b,'author_disposition':st['pick']['fate'].get(b['id'],'演奏条件；不作为人物心理步骤'),'independent_check':next((z for z in st['check']['coverage'] if z['id']==b['id']),None)} for b in beads if b['sec']==s['sec']]
 return g

if __name__=='__main__':
 tag,work,stage=sys.argv[1:4];key=tag+'_'+work
 source=json.loads((evo.ROOT/f'evaluations/synth/{key}/run.json').read_text(encoding='utf-8'))
 if len(source['state'])!=(14 if work=='op60' else 13) or any(not s['check'].get('pass') for s in source['state'].values()):raise ValueError('whole source not locally accepted')
 segs={s['id']:s for s in synth_v2.draft10.segs(work)} if hasattr(synth_v2,'draft10') else {s['id']:s for s in synth_v2.synth.draft10.segs(work)}
 src=[{'sec':sec,'bars':str(segs[sec]['start'])+'–'+str(segs[sec]['end']),'chosen':s['chosen'],'hist':s['hist'],'fate':s['pick']['fate']} for sec,s in source['state'].items()]
 if stage=='graph':
  g=call(key+'_graph',GRAPH+'\n【原稿】'+json.dumps(src,ensure_ascii=False),'g6');validate(g,source);attach_independent_records(g,work,source);synth_v2.dump(OUT/(key+'_graph.json'),g)
 elif stage=='plain':
  g=json.loads((OUT/(key+'_graph.json')).read_text(encoding='utf-8'))
  edits=call(key+'_plain',PLAIN+'\n【原始综合，仅作意义核对，不能另改理由】'+json.dumps(src,ensure_ascii=False)+'\n【当前关系图】'+json.dumps(g,ensure_ascii=False),'g56')
  p=copy.deepcopy(g);index={i['id']:i for s in p['segments'] for i in s['items']};seen=set()
  for e in edits.get('edits',[]):
   if e['id'] in seen or e['id'] not in index:raise ValueError('unknown or duplicated plain-language edit')
   item=index[e['id']]
   if item['text']!=e['before'] or not e.get('after') or not e.get('defect') or not e.get('loss_check'):raise ValueError('untraceable or unjustified plain-language edit')
   seen.add(e['id']);item['text']=e['after'];item['key']=e.get('key') or item['key']
  p.update(edits=edits.get('edits',[]),blocked_edits=edits.get('blocked_edits',[]));validate(p,source)
  def structural(x):return [{**s,'items':[{k:v for k,v in i.items() if k not in ('text','key')} for i in s['items']]} for s in x['segments']]
  if structural(p)!=structural(g):raise ValueError('plain-language rewrite changed graph structure')
  synth_v2.dump(OUT/(key+'_plain.json'),p)
 elif stage in ('verify','verify-repaired'):
  g=json.loads((OUT/(key+'_plain.json')).read_text(encoding='utf-8'))
  # Review the actual delivered content, not long rewrite receipts or other judges' rationales.
  review=copy.deepcopy({'segments':g['segments']})
  for s in review['segments']:
   if 'bead_dispositions' in s:
    s['bead_dispositions']=[{k:b[k] for k in ('original','author_disposition')} for b in s['bead_dispositions']]
  scope='本次只验收肖邦《船歌》Op.60。Op.61另有独立任务；不要把另一首未出现在本次输入中判成本次缺陷。' if work=='op60' else '本次只验收肖邦《幻想波兰舞曲》Op.61。Op.60另有独立任务；不要把另一首未出现在本次输入中判成本次缺陷。'
  msg=VERIFY+'\n【本次范围】'+scope+'\n【原始综合】'+json.dumps(src,ensure_ascii=False)+'\n【人话关系图及独立保留记录】'+json.dumps(review,ensure_ascii=False)
  from concurrent.futures import ThreadPoolExecutor
  with ThreadPoolExecutor(max_workers=2) as ex:results=list(ex.map(lambda m:call(key+'_verify',msg,m),('g6','g56')))
  suffix='_verify_repaired.json' if stage=='verify-repaired' else '_verify.json'
  synth_v2.dump(OUT/(key+suffix),dict(zip(('g6','g56'),results)))
 elif stage=='center':
  g=json.loads((OUT/(key+'_plain.json')).read_text(encoding='utf-8'))
  c=call(key+'_center',CENTER+'\n'+json.dumps(g,ensure_ascii=False),'g6');synth_v2.dump(OUT/(key+'_center_candidates.json'),c)
 elif stage=='center-review':
  g=json.loads((OUT/(key+'_plain.json')).read_text(encoding='utf-8'));c=json.loads((OUT/(key+'_center_candidates.json')).read_text(encoding='utf-8'))
  msg=CSCORE+'\n【全图】'+json.dumps(g,ensure_ascii=False)+'\n【候选】'+json.dumps(c,ensure_ascii=False)
  from concurrent.futures import ThreadPoolExecutor
  with ThreadPoolExecutor(max_workers=2) as ex:rs=list(ex.map(lambda m:call(key+'_center_review',msg,m),('g6','g56')))
  synth_v2.dump(OUT/(key+'_center_reviews.json'),dict(zip(('g6','g56'),rs)))
 else:raise ValueError('unknown stage')
 print(key,stage,'saved; final acceptance remains explicit',flush=True)
