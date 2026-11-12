"""Independent presentation pipeline; never writes the content DAG or delivery zip."""
import argparse, hashlib, json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVO = ROOT.parent / '_thread_evo_20261019'
OLD = ROOT.parent / '_video_design_20261103'
WORKS = {
 'op60': {'title':'肖邦 · 船歌 Op.60', 'performer':'迪努·利帕蒂', 'audio':str(ROOT.parent/'bead_video/remotion_b/public/audio.m4a')},
 'op61': {'title':'肖邦 · 幻想波兰舞曲 Op.61', 'performer':'斯维亚托斯拉夫·里赫特', 'audio':r'D:\archive\classical-op52-legacy-2026-08-29\classical\里赫特 61 布拉格_trimmed.m4a'},
}

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bounds(s):
 n=list(map(int,re.findall(r'\d+',s))); return min(n),max(n)

def freeze():
 parsed=read(OLD/'r54weave_parsed.json'); manifest={}
 for w,cfg in WORKS.items():
  graph=read(EVO/f'evaluations/v6fix/{w}_r54weave.json')['graph']
  joined=EVO/f'deliver_20261103_r54weave/{w}_线与珠子_r54weave.md'
  joined_text=joined.read_text(encoding='utf-8')
  segs=[]
  for g,p in zip(graph['segments'],parsed[w]):
   assert p['lines']==[x['text'] for x in g['items']]
   beads=[]
   for i,b in enumerate(p['beads']):
    assert b['text'] in joined_text, (w,g['sec'],b['text'])
    beads.append({**b,'id':f"{g['sec']}-B{i+1}"})
   segs.append({**g,'beads':beads})
  assert len(segs)==len(graph['segments'])==len(parsed[w])
  out={**cfg,'work':w,'tag':'r54weave','segments':segs}
  path=ROOT/f'input/{w}.json'
  if path.exists(): assert read(path)==out,'Frozen input changed'
  else: write(path,out)
  music=ROOT/f'input/{w}_music.json'
  if not music.exists(): shutil.copyfile(OLD/f'work/{w}_music_v3.json',music)
  manifest[w]={'graph':str(EVO/f'evaluations/v6fix/{w}_r54weave.json'),'graph_sha256':sha(EVO/f'evaluations/v6fix/{w}_r54weave.json'), 'joined':str(joined),'joined_sha256':sha(joined),'input_sha256':sha(path),'music_sha256':sha(music),'audio':cfg['audio'],'audio_sha256':sha(cfg['audio']), 'segments':len(segs),'lines':sum(len(s['items']) for s in segs),'beads':sum(len(s['beads']) for s in segs)}
 write(ROOT/'input/manifest.json',manifest)
 return manifest

PROMPT='''为已定稿音乐体验文字制作展示标注，不改任何正文。这是内容流水线之后的独立DAG2。
目的：完整的线和珠子按原配对相邻摆放；右栏是从线压缩出的层级提纲；局部相近的线/珠子文字可同色。原始全文必须完整保留。
请一次完成此作品的计划：
1. 每段一个短语 label，8–22字，必须是该段某句线的连续原文（不拼接、不改字、不含省略号）。提供 line_id。共每段一条，不漏。
2. 全曲分5–6个故事阶段，阶段必须由连续的整段构成，覆盖每段且不重叠。按故事进展分，非单按音乐。阶段标题 title 8–22字，必须从本阶段某句线里连续摘取，提供 line_id。避免各阶段标题同义重复。阶段标题与每段短语是两个层级，不要求标题强概括整阶段，但不得歪曲。
3. 逐颗检查 bead，标出和该颗已配对的线（after索引，0起）相近的具体连续文字片段。每颗0–2条link即可，保留确实对应的最小意义片段，双方quote都必须在对应原文中唯一逐字出现。不要为了上色强配；没有的列unlinked说明。可标偏弱但这种不显示颜色。颜色只是关系提示，不代表情绪类别；不决定具体色值。不同听法不要编成先后故事，线不能当作音乐事实。
4. 珠子说具体音的物理对应由机械脚本另作，本任务不猜秒数/音符。不要把一句珠子所有音统一认作同一声部。
只输出JSON，结构严格如下：
{"outline":[{"sec":"S01","label":"线的连续原话","line_id":"S01-1"}],"phases":[{"title":"线的连续原话","line_id":"S01-1","sections":["S01","S02"]}],"links":[{"line_id":"S01-1","line_quote":"连续原文","bead_id":"S01-B1","bead_quote":"连续原文","strength":"相近","why":"一句理由"}],"unlinked":[{"bead_id":"S01-B2","reason":"一句理由"}],"notes":"需要注意的边界"}
输入如下（items为线，beads为全部珠子，after为珠子当前已收下的摆放关系）：
'''

def prepare():
 for w in WORKS:
  src=read(ROOT/f'input/{w}.json')
  msg=PROMPT+json.dumps({'work':w,'segments':src['segments']},ensure_ascii=False)
  p=ROOT/f'runs/{w}_plan_v1/prepared_input.txt'; p.parent.mkdir(parents=True,exist_ok=True)
  if p.exists(): assert p.read_text(encoding='utf8')==msg
  else: p.write_text(msg,encoding='utf8')

def call(w):
 os.environ['THREAD_ROUTE']='gpt3s'; os.environ.setdefault('JV','2')
 sys.path.insert(0,str(EVO)); import evo
 rid=f'dag2_20261104_{w}_plan_v1'
 p=ROOT/f'runs/{w}_plan_v1'; msg=(p/'prepared_input.txt').read_text(encoding='utf8')
 answer=evo.call(rid,msg,model=evo.G6,meta={'stage':'DAG2-display-plan','web':True,'content':'frozen-r54weave'})
 if answer: (p/'output.txt').write_text(answer,encoding='utf8')
 write(p/'receipt.json',{'run_id':rid,'answer':bool(answer),'prepared_sha256':sha(p/'prepared_input.txt'),'evidence':str(EVO/'runs'/rid)})
 print(w,'returned',bool(answer),flush=True)

def parse(text):
 text=text.strip()
 if text.startswith('```'): text=re.sub(r'^```(?:json)?\s*|\s*```$','',text)
 start=text.find('{'); return json.JSONDecoder().raw_decode(text[start:])[0]

def validate(w,plan=None):
 src=read(ROOT/f'input/{w}.json'); segs=src['segments']
 if plan is None:
  compiled=ROOT/f'plans/{w}_v1.json'
  plan=read(compiled) if compiled.exists() else parse((ROOT/f'runs/{w}_plan_v1/output.txt').read_text(encoding='utf8'))
 lines={i['id']:i for s in segs for i in s['items']}
 beads={b['id']:(s,b) for s in segs for b in s['beads']}
 sections=[s['sec'] for s in segs]
 assert [x['sec'] for x in plan['outline']]==sections
 for x in plan['outline']:
  assert x['line_id'].startswith(x['sec']+'-') and x['label'] in lines[x['line_id']]['text']
 assert 5<=len(plan['phases'])<=6
 assert [s for p in plan['phases'] for s in p['sections']]==sections
 for p in plan['phases']:
  assert p['line_id'].split('-')[0] in p['sections']
  assert p['title'] in lines[p['line_id']]['text']
 seen=set(); valid=[]
 for x in plan['links']:
  s,b=beads[x['bead_id']]; assert s['items'][b['after']]['id']==x['line_id'],x
  for key,text in [('line',lines[x['line_id']]['text']),('bead',b['text'])]:
   q=x[key+'_quote']; assert q and text.count(q)==1,(key,q)
   x[key+'_span']=[text.index(q),text.index(q)+len(q)]
  seen.add(x['bead_id']);valid.append(x)
 for x in plan['unlinked']: assert x['bead_id'] in beads;seen.add(x['bead_id'])
 assert seen==set(beads),('uninspected',set(beads)-seen)
 # Mechanical partition into relation components. Overlapping text uses one colour.
 for s in segs:
  links=[x for x in valid if x['line_id'].startswith(s['sec']+'-') and x['strength']=='相近']
  parent=list(range(len(links)))
  def find(a):
   while parent[a]!=a: a=parent[a]
   return a
  for i,a in enumerate(links):
   for j,b in enumerate(links[:i]):
    for k in ['line','bead']:
     if a[k+'_id']==b[k+'_id'] and max(a[k+'_span'][0],b[k+'_span'][0])<min(a[k+'_span'][1],b[k+'_span'][1]): parent[find(i)]=find(j)
  groups={}
  for i,x in enumerate(links):
   root=find(i);groups.setdefault(root,len(groups));x['group']=groups[root]
 plan['source_sha256']=sha(ROOT/f'input/{w}.json')
 plan['qa']={'sections':len(segs),'phases':len(plan['phases']),'beads_inspected':len(seen),'exact_spans':len(valid),'pass':True}
 write(ROOT/f'plans/{w}_v1.json',plan); print(w,plan['qa'],flush=True)
 return plan

def repair_headers():
 """One bounded review after mechanical quotation and semantic-scope inspection."""
 sources={};problems=[]
 for w in WORKS:
  src=read(ROOT/f'input/{w}.json');p=parse((ROOT/f'runs/{w}_plan_v1/output.txt').read_text(encoding='utf8'))
  lines={i['id']:i for s in src['segments'] for i in s['items']};beads={b['id']:b for s in src['segments'] for b in s['beads']}
  invalid=[]
  for i,l in enumerate(p['links']):
   if any(d[l[k+'_id']]['text'].count(l[k+'_quote'])!=1 for k,d in [('line',lines),('bead',beads)]): invalid.append({'index':i,'link':l,'bead_source':beads[l['bead_id']],'line_source':lines[l['line_id']]})
  sources[w]={'outline':p['outline'],'phases':p['phases'],'lines':list(lines.values()),'invalid_links':invalid}
  # Human inspection found a lost negative scope; model must quote it intact.
  if w=='op61':sources[w]['scope_review']=[{'index':31,'link':p['links'][31],'line_source':lines[p['links'][31]['line_id']],'bead_source':beads[p['links'][31]['bead_id']]}]
 msg='''审查并修补DAG2展示标注，正文不可改。原计划有以下实质问题：部分标题只截到条件/时间从句；op61 S02短语从“怕…忘了”截成“忘了”，会把担心说成已发生；op60第4阶段“他真盼着以后对方想要人陪的时候”没有主句，第6阶段“既然喜欢已经让对方看见”没有后半句。所有标题都必须从提供原文连续摘录，尽量8–22字，语义自足，不截掉怕、不肯、也许、条件或否定而反转原意。阶段可维持分组。逐个检查全部标签，必要才替换。invalid_links是逐字定位失败，必须替换为正确ID和连续原文，或者删除并记unlinked。scope_review片段漏掉否定，请扩大quote保留完整否定态度或改标偏弱，不准把被否定动作当作肯定。只输出JSON：{"works":{"op60":{"outline_replacements":[{"sec":"S01","label":"原文","line_id":"S01-1"}],"phase_replacements":[{"index":0,"title":"原文","line_id":"S01-1"}],"link_replacements":[{"index":0,"replacement":null,"unlinked":{"bead_id":"...","reason":"..."}}],"notes":""},"op61":{同样四个数组和notes}}}。link replacement若不删除，则为完整link对象，字段沿用旧结构；不涉及的不要输出。\n'''+json.dumps(sources,ensure_ascii=False)
 folder=ROOT/'runs/plan_repair_v1';folder.mkdir(parents=True,exist_ok=True);inp=folder/'prepared_input.txt'
 if inp.exists(): assert inp.read_text(encoding='utf8')==msg
 else:inp.write_text(msg,encoding='utf8')
 os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo
 answer=evo.call('dag2_20261104_plan_repair_v1',msg,model=evo.G6,meta={'stage':'DAG2-repair-exact-quotes-and-label-scope','web':True})
 if not answer:return
 (folder/'output.txt').write_text(answer,encoding='utf8');patch=parse(answer)
 for w,q in patch['works'].items():
  p=parse((ROOT/f'runs/{w}_plan_v1/output.txt').read_text(encoding='utf8'))
  for x in q['outline_replacements']:p['outline'][next(i for i,a in enumerate(p['outline']) if a['sec']==x['sec'])]=x
  for x in q['phase_replacements']:p['phases'][x['index']].update({k:v for k,v in x.items() if k!='index'})
  for x in sorted(q['link_replacements'],key=lambda z:z['index'],reverse=True):
   if x['replacement'] is None:
    p['links'].pop(x['index']);p['unlinked'].append(x['unlinked'])
   else:p['links'][x['index']]=x['replacement']
  p['repair_notes']=q['notes'];validate(w,p)

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 p=argparse.ArgumentParser();p.add_argument('command',choices=['freeze','prepare','call','validate','repair']);p.add_argument('--work',choices=list(WORKS));a=p.parse_args()
 if a.command=='freeze': print(json.dumps(freeze(),ensure_ascii=False,indent=2))
 elif a.command=='prepare': prepare()
 elif a.command=='call': call(a.work)
 elif a.command=='repair': repair_headers()
 else:
  for w in ([a.work] if a.work else WORKS):validate(w)
