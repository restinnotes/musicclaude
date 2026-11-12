"""v5: user's verbatim short prompt, original five headings, deterministic parsing."""
from d13_experiment import *
import re

def parse_heading(text):
 names=['当前理解','Why now','使用的 History','新增 History','自检']
 matches=[]
 for n in names:
  m=re.search(r'^\s*#{1,5}\s*'+re.escape(n)+r'[^\n]*\n',text,re.M|re.I)
  if not m:m=re.search(r'^\s*\*{0,2}'+re.escape(n)+r'\*{0,2}\s*[:：]?\s*\n',text,re.M|re.I)
  assert m,('missing original heading',n)
  matches.append(m)
 assert [m.start() for m in matches]==sorted(m.start() for m in matches)
 return {n:text[m.end():matches[i+1].start() if i<4 else len(text)].strip() for i,(n,m) in enumerate(zip(names,matches))}

def parse_new_history(block):
 plain=re.sub(r'[*`_]','',block).strip()
 if re.match(r'^(?:无(?:[。\s]|$)|没有(?:新增|新的)|本段(?:没有|不新增)|不新增|暂不(?:建立|新增))',plain):return []
 paragraphs=[p.strip() for p in re.split(r'\n\s*\n',plain) if p.strip()]
 numbered=[p for p in paragraphs if re.match(r'^(?:[-\s]*H\d+|[-\s]*\d+[.、)])',p)]
 if numbered:return numbered
 # Unnumbered original prose is one record; commentary is retained in raw fields only.
 return paragraphs[:1]

BOOTSTRAP='''Thread是一条可被后续材料检验或否定的心理解释假说，不是已调查过的人生事实记录。S01应提出一个最小的当下心理假说；它不需要已有前史来证明，也不需要编造外部事件。以后History里的“真实经历”指这条候选假说内确已建立的主观事实，不能把尚未建立的后续变化或外部回应塞进去。不要把所有解释都无限期搁置为无足够证据。\n'''
def generate_original(var,w,repeat,end,version='v5'):
 name=f'd13{version}{var}_56_{w}_r{repeat}';target=O/f'drafts/{name}.json';done=load(target)['sections'] if target.exists() else []
 core=rd(O/'prompts/D13_用户建议原始prompt.txt')
 fullcore=core+('\n\n'+VAR[var] if VAR[var] else '')+('\n\n'+BOOTSTRAP if version in ('v6','v7','v8') else '')
 (O/f'prompts/D13-{var}_{version}.txt').write_text(fullcore,encoding='utf-8')
 mp=O/f'inputs/music_{w}.json'
 if w=='op61':mp=O/'inputs/music_op61_pilot.json'
 music=load(mp)['sections'];labels=seg.load(w)['segments']
 for i,s in enumerate(labels[:end]):
  if i<len(done):continue
  history=[h for x in done for h in x['established_history']]
  direction=('暂定宽松Center：'+('亲近与牵挂。' if w=='op60' else '眷恋与内在力量。')+'它只是观察方向，当前材料不支持时可以放弃；不预设外部事件、关系对象或结局。') if version=='v8' else '开放方向：让一个人的当下体验逐渐带有自己经历过的来处；不预定主题、结局或关系对象。'
  inp={'work':seg.load(w)['work'],'direction':direction,
       'history':history,'current_music':music[i],
       'adjacent_structure_only':[{'sec':x['id'],'bars':f"{x['start']}–{x['end']}",'structure':x.get('label','')} for x in labels[max(0,i-1):i+2]]}
  prompt=fullcore+'\n\n本段输入：\n'+json.dumps(inp,ensure_ascii=False)
  key=name+'_'+s['id'];rid='D13_'+key+'_'+hashlib.sha256((evo.G56+prompt).encode()).hexdigest()[:12]
  base=rid;attempt=1
  while (evo.RUNS/rid).exists() and not evo.done(rid) and list((evo.RUNS/rid).glob('call_fail*')):
   attempt+=1;rid=base+f'_attempt{attempt}'
  text=evo.call(rid,prompt,model=evo.G56,cli_args=('--allow-topic-stream',),meta={'stage':'D13','key':key,'verbatim_user_prompt':True,'format':'five_original_headings','no_G25_fallback':True})
  assert text,('no original response',rid)
  h=parse_heading(text);used=list(dict.fromkeys('H'+str(int(k[1:])) for k in re.findall(r'H\d+',h['使用的 History'])))
  assert set(used)<={x['id'] for x in history},('unknown used History',rid,used)
  raw_new=h['新增 History'].strip();new=parse_new_history(raw_new)
  established=[{'id':f'H{len(history)+k+1}','sec':s['id'],'text':x} for k,x in enumerate(new)]
  done.append({'sec':s['id'],'bars':f"{s['start']}–{s['end']}",'run_id':rid,'model':evo.G56,'input_sha256':sha(evo.RUNS/rid/'input.txt'),
   'original_five_fields':h,'understanding':h['当前理解'],
   'why_now':{'earlier_fact':'；'.join(x['text'] for x in history if x['id'] in used) or '无；首段或未引用History',
      'bridge':h['Why now'],'current':h['当前理解'],'without':'未强制单独输出；见原始自检'},
   'used':used,'new_history':new,'established_history':established,'self_check':{'original_text':h['自检']}})
  save(target,{'name':name,'model':evo.G56,'version':version,'variant':var,'repeat':repeat,'bead_free':True,'verbatim_user_prompt':version=='v5','base_user_prompt_verbatim':True,'bootstrap_clarification':version in ('v6','v7','v8'),'center_condition':direction,'history_parser_version':2,'format_change':'original five headings; deterministic parsing only','sections':done})
 return name

if __name__=='__main__':
 phase=sys.argv[1]
 version=next((v for v in ('v8','v7','v6') if phase.startswith(v)),'v5')
 jobs=[(v,w,j,5 if w=='op60' else 3,version) for v in VAR for w in TAGS for j in (1,2,3)] if phase in ('repeat','v6repeat','v7repeat','v8repeat') else [(v,'op60',1,5,version) for v in VAR]
 if phase in ('extend','v6extend','v7extend','v8extend'):jobs=[(v,'op60',j,13,version) for v in VAR for j in (1,2,3)]
 with ThreadPoolExecutor(6) as ex:
  fs=[ex.submit(generate_original,*a) for a in jobs]
  for f in as_completed(fs):
   try:print('DRAFT',f.result(),flush=True)
   except Exception as e:print('ORIGINAL PROMPT FAILED',repr(e),flush=True)
