"""D13: immutable evidence, bead-free chained generation, no G25 fallback."""
import os
os.environ.setdefault('THREAD_GPT','gpt4')
os.environ.setdefault('EVO_ATTEMPTS','1')
import json, hashlib, shutil, sys, csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import evo, seg, covjudge
if os.environ.get('D13_TRANSPORT_NO_BUFFERING')=='1':
 assert evo.ACCOUNT=='gpt4'
 evo.GPT3=str(Path(__file__).with_name('d13_transport.cmd'))

R=evo.ROOT
O=R/'evaluations'/'d13_20261025'
O.mkdir(exist_ok=True)
SCORES={'op60':Path('D:/musicclaude/op60_score.pdf'), 'op61':Path('D:/musicclaude/unified_run_handoff_20260924/unified_run_handoff_20260924/tools/op61.pdf')}
TAGS={'op60':'C25whole60','op61':'C25op61body2'}
def rd(p): return Path(p).read_text(encoding='utf-8-sig')
def load(p): return json.loads(rd(p))
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def call(key,prompt,model=evo.G56,attach=()):
 rid='D13_'+key+'_'+hashlib.sha256((model+prompt+''.join(sha(p) for p in attach)).encode()).hexdigest()[:12]
 # Preserve every failed run rather than overwriting its attempt evidence.
 base=rid;attempt=1
 while (evo.RUNS/rid).exists() and not evo.done(rid) and list((evo.RUNS/rid).glob('call_fail*')):
  attempt+=1;rid=base+f'_attempt{attempt}'
 text=evo.call(rid,prompt,model=model,attach=attach,cli_args=('--allow-topic-stream',),meta={'stage':'D13','key':key,'no_G25_fallback':True,'topic_reception_enabled':True,'attempt_identity':attempt})
 if not text: raise RuntimeError('no verified response: '+rid)
 try:parsed=evo.parse_json(text)
 except json.JSONDecodeError:
  # Preserve response verbatim. Accept a complete leading JSON object when only a
  # duplicate closing delimiter/fence follows; never repair semantic fields.
  start=text.find('{');parsed,end=json.JSONDecoder().raw_decode(text[start:])
  tail=text[start+end:].strip()
  assert not tail or set(tail)<=set('}`\n\r\t ]'),('unrecognized trailing data',rid,tail[:80])
  save(O/f'format_recovery/{rid}.json',{'raw_response_sha256':sha(evo.RUNS/rid/'output.txt'),'action':'parsed complete leading JSON; ignored trailing delimiters only','trailing':tail})
 return parsed,rid

CAL_RULES='''你是Thread因果评委。逐条判断，不奖励字数、History编号或故事完整。
一个有信息的历史因果必须指出：前面实际新增了什么具体心理事实；该事实如何通过一个明确的桥改变当前体验；如果删掉这个事实，当前为什么不会同样出现。第一格只有“更在乎/更成熟/经历更多/不是第一次/更有分量”，失败。
音乐主题回来、变亮、高潮不能证明获得对方回应、保证或外部关系恢复。相似感受不等于因果。同义复述、抽象汇合均失败。允许延续、没有新增History；不要要求每颗体验独立原因。首段可确立当下心理起点，不伪造前史，不能因无History自动失败。
正例也不能把“亲近重新出现”未经支持确认为外部世界回应；作为已经给定的当下主观体验可以推理。机制具体不保证其输入前提真实，分开判。
'''
FIXTURES=[
 ('N1','熟悉的亲近重新出现以后，他已经不是第一次那个只满足于眼前的人了。',False),
 ('N2','经历过前面的事情，所以现在不一样了。',False),
 ('N3','H3、H6使这份感情有了新的分量。',False),
 ('N4','他比以前更珍惜，更深地理解了自己的感情。',False),
 ('N5','以前的经历改变了现在的意义，因为更加在乎，所以感受更加强烈。',False),
 ('N6','主题回来，因此他再次得到了回应，关系恢复了。',False),
 ('N7','珠子说手越握越紧；解释是他更想抓住这份幸福。',False),
 ('N8','过去与现在在这里重新汇合。',False),
 ('N9','越在乎，越舍不得。',False),
 ('P1','前面他第一次希望这种亲近不只属于眼前，还能继续；能否继续却不由他一个人决定。当前重新感到亲近，只满足了眼前，没有回答以后，所以快乐会带着急切和舍不得。当前亲近是给定的主观体验，不是假定对方做出新回应。',True),
 ('P2','前面他已体验到，即使独处，喜欢留在心里仍能让自己快乐。现在亲近重新可感时，它便不必独自承担保证全部幸福的任务，因此可以充分投入而仍不确定未来。没有那次独自快乐的经验，全部幸福仍只能压在眼前亲近上。',True),
 ('P3','这一段没有值得新增的历史变化，仍延续H2已经建立的想念。不把延续当作新因果发现，也不新增History。',True),
 ('N10','他上段学会接受失去，现在庄严的主题使他知道自己重新获得了尊严。',False),
 ('P4','上段真正尝过短暂的满足，愿望却没有消失。现在满足仍可感而身体还在向前；得到某次满足不等于耗尽已经积起的依恋，这能解释释放与余势共存，不声称外部世界发生改变。',True)
]
def calibrate():
 prompt=CAL_RULES+'''\n评下面全部案例。只输出JSON {"cases":[{"id":"...","pass":true,"increment":"前面具体新增事实，或无/首段/延续","bridge":"具体桥或为何不存在","counterfactual":"删除前提的差别","why":"原因"}]}。'''+json.dumps([{'id':a,'text':b} for a,b,c in FIXTURES],ensure_ascii=False)
 def one(m):
  j,rid=call('calibration_'+m,prompt,model=m)
  got={x['id']:x for x in j['cases']}
  errors=[{'id':a,'expected':c,'actual':got.get(a)} for a,b,c in FIXTURES if got.get(a,{}).get('pass') is not c]
  save(O/f'calibration/{m}.json',{'run_id':rid,'fixtures':[{'id':a,'text':b,'expected':c} for a,b,c in FIXTURES],'review':j,'errors':errors,'passed':not errors})
 with ThreadPoolExecutor(2) as ex: list(ex.map(one,[evo.G56,evo.G6]))

CAL_V2_EXTRA='''还须区分：说明某种变化“可以发生/不必等于退出/允许共存”，不等于说明目标体验为什么实际出现。音乐或感受的连续性不能代替亲近、舒服、迫切、阻力的心理原因。主体验和侧面标签均不决定重要性；不能只解释一个贴标签的主轮廓就把明显重要的暗流/阻力遗漏后判段落通过。无需无限追加中介，但必须有改变当前内容的真实因果桥。\n'''
def calibrate_v2():
 fixtures=FIXTURES+[
 ('N11','先前他已经把少显露与离开体验分开。因此当前表达可以短促、反复、停顿而不必等于退出。这就解释了此段为什么舒服陶醉，又有急切和暗流阻力。',False),
 ('N12','之前他已经增强又收住，所以当前仍可以增强又收住；这证明已经解释了此处为什么想抓紧幸福、却越用力越失衡。',False),
 ('P5','前面真正体验到独处时喜欢也能带来快乐。现在相伴不再被迫承担保证全部幸福的任务，因而更能投入。它不能解释当前所有侧面，但具体减少单一支撑负担的桥成立；未涵盖的侧面仍留作缺口。',True)]
 prompt=CAL_RULES+CAL_V2_EXTRA+'\n输出JSON {"cases":[{"id":"...","pass":true,"increment":"...","bridge":"...","counterfactual":"...","why":"..."}]}。逐项判断：'+json.dumps([{'id':a,'text':b} for a,b,c in fixtures],ensure_ascii=False)
 def one(m):
  j,rid=call('calibration_v2_'+m,prompt,model=m);got={x['id']:x for x in j['cases']}
  errors=[{'id':a,'expected':c,'actual':got.get(a)} for a,b,c in fixtures if got.get(a,{}).get('pass') is not c]
  save(O/f'calibration_v2/{m}.json',{'run_id':rid,'fixtures':[{'id':a,'text':b,'expected':c} for a,b,c in fixtures],'review':j,'errors':errors,'passed':not errors})
 with ThreadPoolExecutor(2) as ex:list(ex.map(one,[evo.G56,evo.G6]))

def music():
 def one(w):
  sections=seg.load(w)['segments']
  prompt='''只读所附肖邦乐谱，为下面固定区间提取纯音乐事实，供一个尚未看到任何心理解释的写作者使用。不要看网页。不要提供任何心理情绪、意象、人物、哲理、珠子或Thread答案。只写可从谱面核对的：织体、声部、节奏/音型、力度/速度记号、主题材料同异与局部变化。不可把主题回归等同任何人物事件。不确定的小节/记号必须写uncertain，不猜。每段给PDF页码(1-based)和核查用短说明；不要改变区间。每段只列3至6条简短事实。输出JSON {"work":"...","sections":[{"sec":"S01","start":1,"end":3,"facts":["..."],"pdf_pages":[1],"uncertain":[]}]}。区间：'''+json.dumps(sections,ensure_ascii=False)
  j,rid=call('score_facts_'+w,prompt,attach=[SCORES[w]])
  assert [s['sec'] for s in j['sections']]==[s['id'] for s in sections]
  save(O/f'inputs/music_{w}.json',{'source':str(SCORES[w]),'source_sha256':sha(SCORES[w]),'run_id':rid,**j})
 with ThreadPoolExecutor(2) as ex: list(ex.map(one,['op60','op61']))

def prepare():
 files=[R/'PLAN_解释池_20261023.md',R/'PLAN_逐段构建线_20261023.md',R/'draft10.py',R/'draft11.py',R/'draft12.py',R/'pool.py',R/'pool_v2.py']
 files+=list((R/'evaluations/draft10').glob('d1*.json'))
 files+=list((R/'evaluations/pool/C25whole').glob('**/*.json'))
 files+=list((R/'evaluations/synth').glob('C25*/**/*.json'))
 files+=list((R/'evaluations/continuation_20261025/finalization').glob('*.json'))
 files+=list(Path('C:/Users/zuoyi/Documents/Codex/2026-10-25/n-n/outputs').glob('*Thread*'))
 manifest=[]
 for p in sorted(set(files)):
  content=p.read_bytes()
  manifest.append({'path':str(p),'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
 save(O/'source_manifest.json',manifest)
 for w,t in TAGS.items():
  d=load(R/f'evaluations/synth/{t}_{w}/run.json')
  ds=[load(p) for p in sorted((R/'evaluations/draft10').glob(f'd1*_{w}_*.json'))]
  counts=[]
  for section in seg.load(w)['segments']:
   sec=section['id']; v=d['state'][sec]; p=load(R/f'evaluations/pool/C25whole/{w}/{sec}.json')
   raw=[]
   for draft in ds:
    cur=next(x for x in draft['sections'] if x['sec']==sec)
    # Full current source and declared used text; all prior concrete new facts, not just a nearest-section window.
    prior=[{'sec':x['sec'],'new':x.get('new',[])} for x in draft['sections'] if x['sec']<sec]
    raw.append({'source':draft['name'],'current':cur,'prior_history':prior})
   evidence={'work':w,'sec':sec,'chosen_G25_or_M':v['chosen'],'final_prior_history':[h for h in v.get('history_before',[])],
    'original_drafts':raw,'pool_mechanisms':p['mechs'],'unmerged_candidates':p.get('unmerged_candidates',[]),
    'excluded':load(R/f'evaluations/pool/C25whole/{w}/manifest.json').get('excluded_contrary',{}).get(sec,[])}
   save(O/f'forensics/inputs/{w}_{sec}.json',evidence)
   counts.append({'sec':sec,'selected':len(v['chosen']),'direct_pool':sum(all(not s.startswith('G25') for s in c['from']) for c in v['chosen'])})
  save(O/f'forensics/{w}_source_counts.json',counts)
 print('source manifests and full source section evidence ready',flush=True)

FORENSIC='''审计原始Thread到包3最终机制的来源，不写新Thread或新补缺。
你得到本段所有D10/D11/D12原稿原文、各自之前new History、原池条目和最终chosen。逐个最终chosen机制分类：A 原稿已有同一前提+因果桥+结果；B 近似想法但缺桥/前提不完整；C 所有原稿均没有。以原稿实文为准，不以旧覆盖标签为准。源文本是空泛“更在乎/更有分量”不能当作A。第一段可建立当下状态，但不要把同义描述说成因果进步。
A再分 pool_loss/selection_history_incompatible/retained_not_selected。必须检查同一来源稿的前史，不因结果词相似判同机制。分开指出G25本身是否仍有伪因果。按D10、D11、D12分别报告最佳匹配，给source、从当前原文逐字引用的quote、具体差别。C是这次给定全集中的没有，不宣称世界上首次。
另逐条审查pool的合并：前提结构+因果桥+结果三者才可去重。不同前提的或合并必须标bad_merge并列原始source候选拆分，不设条数上限。覆盖标签union不证明合并文字在任一历史路径上覆盖。
输出JSON {"sec":"S01","targets":[{"index":1,"class":"A|B|C","cause":"generation_missing|pool_loss|history_incompatible|retained_not_selected|mixed","valuable":true,"causal_increment_test":{"new_fact":"...","bridge":"...","without":"..."},"g25_weaknesses":[],"families":{"D10":{"class":"...","source":"...","quote":"...","gap":"..."},"D11":{},"D12":{}},"why":"..."}],"merges":[{"id":"M1","bad_merge":false,"why":"...","split_source_groups":[["d12..."]]}],"section_conclusion":"..."}。每个最终chosen都必须有一项，不漏项。不复述长文章。'''

def forensic():
 def one(p):
  dst=O/'forensics/reviews'/p.name
  if dst.exists(): return
  d=load(p)
  # Keep each family's full evidence. Late sections can exceed one request; never truncate a history.
  base={k:v for k,v in d.items() if k!='original_drafts'}
  full=FORENSIC+'\n'+json.dumps(d,ensure_ascii=False)
  if len(full)<63000:
   j,rid=call('forensic_'+p.stem,full); save(dst,{'run_id':rid,'scope':'all_families',**j})
  else:
   parts=[]
   for family in ['d10','d11','d12']:
    sub=base|{'original_drafts':[x for x in d['original_drafts'] if x['source'].startswith(family)]}
    j,rid=call('forensic_'+p.stem+'_'+family,FORENSIC+'\n仅有'+family+'原稿，其他家族标not_supplied，不推测。\n'+json.dumps(sub,ensure_ascii=False))
    parts.append({'family':family,'run_id':rid,'review':j})
   j,rid=call('forensic_merge_'+p.stem,FORENSIC+'\n把这三个已看完各自全集的分家族审计合并成全家族结论，引用保留原文。\n'+json.dumps({'target':base,'family_reviews':parts},ensure_ascii=False))
   save(dst,{'run_id':rid,'scope':'all_families_split_without_truncation','parts':parts,**j})
 with ThreadPoolExecutor(8) as ex:
  fs=[ex.submit(one,p) for p in sorted((O/'forensics/inputs').glob('*.json'))]
  for f in as_completed(fs):
   try:f.result()
   except Exception as e:print('FORENSIC FAILED',repr(e),flush=True)

BASE='''你正在独立构建一条贯穿整首作品的Thread。这轮只处理当前Section。
Thread不是另一份音乐描写；你的任务是理解：一个人此前真实经历过什么，使当前感受现在以这种方式出现。这里只给自己的已建立History、当前音乐事实、必要相邻结构和宽松方向；没有珠子或标准答案。
判断当前最值得解释的心理状态；哪条具体History造成它；中间的因果桥；是否有以后可用的新心理事实。
规则：不要为了续故事编新决定、劝说、领悟或外部事件。不要求每段转折，允许延续、共存、没有新认识。不要把“经历过所以更在乎/更深/更有分量/不是原来的人”当因果。音乐主题回归、高潮、力度变化，不能证明对方回应、保证、关系恢复或心理问题解决。一个理由能解释多个相容感受时不要拆步骤。允许含糊，不强定怕什么或希望谁做什么。普通人一遍能懂，不写哲理总结。
History只记以后真能用的具体心理事实，不单记更在乎/成熟/复杂/新意义。新事实必须由本段当前理解真正建立，不可为了后文预埋答案。
每段问：前面哪件具体发生过的事，使当前体验具有这种形态？只有“更喜欢/更投入”，继续想。没有值得新增的历史解释，可明确写只是延续，不伪造原因。
自检：删掉引用的History解释是否几乎一样？是否只说更深？是否偷把音乐事件当外部事实？是否能原封不动放到很多别段？发现后在当前回答内修正。
'''
VAR={'A':'','B':'优先寻找过去已经获得什么、开始需要什么、发现什么不能由自己决定、哪种旧办法曾有效而此刻不足等具体差异；这些只是方向，不要求必须出现。\n','C':'尽量用最少的心理事实解释当前段落；一条History足够，不制造第二条。\n'}
FORMAT='''输出一个JSON，不输出别的：{"understanding":"当前理解","why_now":{"earlier_fact":"前面新增的具体事实，首段或延续可明说","bridge":"怎样作用于当前","current":"为什么现在这样","without":"如果没有前述事实，当前为何不同；若只是延续就明说无新增"},"used":["H1"],"new_history":["本段建立的具体事实；没有用空列表"],"self_check":{"history_effective":true,"pseudo_cause":false,"music_as_external_fact":false,"generic":false,"note":"自检结果，不必强行全通过"}}。
'''
V2_RULE='''实验新增一条：当前理解应说清人在乎的具体内容，不能只说“显露强度改变、体验仍连续”或改述谱面。允许自定一条没有具体身份和旧事的轻量人类关切作为本条起点；它是候选理解，不是得到外部回应的证据，不需要编人物事件来证明。不要把不编外部事件误解成只能谈感受的强度和形式；没有必要依据时仍可含糊。\n'''
V3_RULE='''这些限制约束写作者，不是主人公的心理目标。不要因为提示词禁止你虚构回应，就自动写他正在练习“不索取、不逼问、不押上期待、保持开放、学会区分表达和保证”。只有本条实际前史确实使这些关切必要时才写；否则去理解他实际在乎和承受的具体内容。\n'''
V4_RULE='''主观体验可以真实发生：当下感到亲近、得到片刻满足、得到安慰，不等于证实对方做出回应。不要因不能虚构外部事件，就把所有体验一律降成“想靠近但尚未发生”；也不要用表达是否连续替代真正的感受。允许已经得到的主观体验成为History，再看它实际带来什么需要或限制，不要求人物形成新的认识。\n'''
def generate(variant,w,repeat,end,version='v1'):
 name=f'd13{version}{variant}_56_{w}_r{repeat}'
 target=O/f'drafts/{name}.json'
 done=load(target)['sections'] if target.exists() else []
 music_path=O/f'inputs/music_{w}.json'
 if w=='op61' and (O/'inputs/music_op61_pilot.json').exists():music_path=O/'inputs/music_op61_pilot.json'
 music=load(music_path)['sections']
 direction='开放方向：让一个人的当下体验逐渐带有自己经历过的来处；不预定主题、结局或关系对象。'
 for i,s in enumerate(seg.load(w)['segments'][:end]):
  if i<len(done):continue
  history=[h for x in done for h in x['established_history']]
  labels=seg.load(w)['segments']
  adjacent=[{'sec':x['id'],'bars':f"{x['start']}–{x['end']}",'structure':x.get('label','')} for x in labels[max(0,i-1):i+2]]
  inp={'work':seg.load(w)['work'],'direction':direction,'history':history,'current_music':music[i],'adjacent_structure_only':adjacent}
  prompt=BASE+VAR[variant]+FORMAT+'\n输入：\n'+json.dumps(inp,ensure_ascii=False)
  if version in ('v2','v3','v4'):
   prompt=BASE+VAR[variant]+V2_RULE+(V3_RULE if version in ('v3','v4') else '')+(V4_RULE if version=='v4' else '')+FORMAT+'\n输入：\n'+json.dumps(inp,ensure_ascii=False)
  j,rid=call(name+'_'+s['id'],prompt)
  valid={h['id'] for h in history}
  assert isinstance(j.get('used'),list) and set(j['used'])<=valid, (name,s['id'],'invalid history reference')
  assert isinstance(j.get('new_history'),list)
  established=[{'id':f'H{len(history)+k+1}','sec':s['id'],'text':x} for k,x in enumerate(j['new_history'])]
  done.append({'sec':s['id'],'bars':f"{s['start']}–{s['end']}",'run_id':rid,'model':evo.G56,'input_sha256':sha(evo.RUNS/rid/'input.txt'),**j,'established_history':established})
  save(target,{'name':name,'model':evo.G56,'version':version,'variant':variant,'repeat':repeat,'bead_free':True,'sections':done})
 return name

def generators(phase):
 jobs=[]
 if phase in ('pilot1','pilot60','pilot61'): jobs=[(v,w,1,5 if w=='op60' else 3,'v1') for v in VAR for w in TAGS if phase=='pilot1' or w==('op60' if phase=='pilot60' else 'op61')]
 elif phase=='repeat': jobs=[(v,w,j,5 if w=='op60' else 3,'v1') for v in VAR for w in TAGS for j in (2,3)]
 elif phase=='extend': jobs=[(v,'op60',j,13,'v1') for v in VAR for j in (1,2,3)]
 elif phase=='full': jobs=[(v,w,j,14 if w=='op60' else 13,'v1') for v in VAR for w in TAGS for j in (1,2,3)]
 elif phase in ('v2pilot','v2pilot60','v2pilot61'):jobs=[(v,w,j,5 if w=='op60' else 3,'v2') for v in VAR for w in TAGS for j in (1,2,3) if phase=='v2pilot' or w==('op60' if phase=='v2pilot60' else 'op61')]
 elif phase=='v3pilot60':jobs=[(v,'op60',1,5,'v3') for v in VAR]
 elif phase=='v3repeat':jobs=[(v,w,j,5 if w=='op60' else 3,'v3') for v in VAR for w in TAGS for j in (1,2,3)]
 elif phase=='v3extend':jobs=[(v,'op60',j,13,'v3') for v in VAR for j in (1,2,3)]
 elif phase=='v4pilot60':jobs=[(v,'op60',1,5,'v4') for v in VAR]
 elif phase=='v4repeat':jobs=[(v,w,j,5 if w=='op60' else 3,'v4') for v in VAR for w in TAGS for j in (1,2,3)]
 elif phase=='v4extend':jobs=[(v,'op60',j,13,'v4') for v in VAR for j in (1,2,3)]
 for v in VAR:
  p=O/f'prompts/D13-{v}_v1.txt';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(BASE+VAR[v]+FORMAT,encoding='utf-8')
  (O/f'prompts/D13-{v}_v2.txt').write_text(BASE+VAR[v]+V2_RULE+FORMAT,encoding='utf-8')
  (O/f'prompts/D13-{v}_v3.txt').write_text(BASE+VAR[v]+V2_RULE+V3_RULE+FORMAT,encoding='utf-8')
  (O/f'prompts/D13-{v}_v4.txt').write_text(BASE+VAR[v]+V2_RULE+V3_RULE+V4_RULE+FORMAT,encoding='utf-8')
 with ThreadPoolExecutor(9) as ex:
  fs=[ex.submit(generate,*a) for a in jobs]
  for f in as_completed(fs):
   try: print('DRAFT',f.result(),flush=True)
   except Exception as e: print('GENERATION FAILED',repr(e),flush=True)

if __name__=='__main__':
 op=sys.argv[1]
 if op=='prepare':prepare()
 elif op=='calibrate':calibrate()
 elif op=='calibrate_v2':calibrate_v2()
 elif op=='music':music()
 elif op=='forensic':forensic()
 else:generators(op)
