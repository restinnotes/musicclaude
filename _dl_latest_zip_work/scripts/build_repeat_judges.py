#!/usr/bin/env python3
"""Deterministic, frozen prompt expansion for D/G/F review. No model calls.

D: each model's r01/r05 new screen vs old run124, opposite-model judge, both candidate orders.
G: direct 6w vs 5.6w for same station/repeat, both judge models, both orders.
F: r01..r05 (r08/r12 optionally) semantic novelty judged by the other model.
Reviews are blinded in text; mappings stay private.
"""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf-8'))
PLAN=json.loads((ROOT/'jobs/repetition_plan.json').read_text(encoding='utf-8'))
MODELS=['gpt6w','gpt56w']
TEMPLATE={kind:(ROOT/f'prompts/{fname}').read_text(encoding='utf-8') for kind,fname in {
 'D':'D_BLIND_COMPARISON_v1.txt','G':'G_DIRECT_BLIND_PAIRWISE_v1.txt','F':'F_E7_SEMANTIC_SATURATION_v1.txt'}.items()}

def parse(s):
 s=s.strip().lstrip('\ufeff')
 if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
 return json.loads(s)
def load_c(model,k,r):
 job=f'C{k:02d}'
 p=ROOT/'results/trials'/model/job/f'r{r:02d}'
 mp=Path(str(p)+'.meta.json');txt=Path(str(p)+'.txt')
 if not (mp.exists() and txt.exists()):return None
 try:
  meta=json.loads(mp.read_text(encoding='utf-8'))
  assert meta.get('status')=='success'
  assert meta.get('model_reported')==PLAN['models'][model]
  obj=parse(txt.read_text(encoding='utf-8'))
  assert obj.get('task')=='C' and obj.get('station_k')==k
  assert isinstance(obj.get('new_screen_items'),list)
  return obj
 except (KeyError,ValueError,AssertionError):return None

def representation(x):
 return json.dumps({z:x.get(z) for z in ('action','keep_ids','retire_ids','new_screen_items','final_screen_text','expand_ids','recap_ids','editorial_tradeoff')},ensure_ascii=False,indent=2)

def add(kind,judge,jid,txt,meta,jobs,maps):
 rel=f'jobs/reviews/{judge}/{jid}.txt'
 content=txt.strip()+'\n'
 if len(content)>65536:raise ValueError(f'{jid} > gpt2 65536 character limit ({len(content)})')
 dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True)
 # NOTE(2026-10-10): write with newline='\n' so on-disk bytes equal the
 # hashed content. Default text-mode would emit CRLF on Windows and break
 # the runner's immutable prompt-hash check (88/88 mismatch observed).
 dest.write_text(content,encoding='utf-8',newline='\n')
 j={'job_id':jid,'kind':kind,'judge_model':judge,'prompt_file':rel,
    'prompt_sha256':hashlib.sha256(content.encode('utf-8')).hexdigest(),
    'station_k':meta['k']}
 jobs.append(j);maps.append({'job_id':jid,'kind':kind,'judge_model':judge,**meta})

def source(k):
 path=ROOT/f'inputs/op60/C_k{k:02d}.json'
 return json.loads(path.read_text(encoding='utf-8'))

def main():
 jobs=[];maps=[]; missing=[]; optional_future=[];counts={'D':0,'G':0,'F':0}
 picks=[1,5,8,12]
 for k in (2,11,18,20,23):
  inp=source(k)
  evidence=('【音乐位置（既有研究文字，非独立谱面事实）】\n'+str(inp['meta']['section_title'])+
   '\n【屏幕先前状态】\n'+json.dumps(inp['screen_before'],ensure_ascii=False,indent=2)+
   '\n【可用当前素材】\n'+json.dumps(inp['current_candidates'],ensure_ascii=False,indent=2)+'\n')
  oldtxt=(ROOT/f'private/legacy_target_k{k:02d}.txt').read_text(encoding='utf-8').split('\n\n',1)[1]
  # D requires individual preselected sample and opposite-model reviewer.
  for gen in MODELS:
   judge='gpt56w' if gen=='gpt6w' else 'gpt6w'
   for r in picks:
    x=load_c(gen,k,r)
    if x is None:
     (missing if r<=5 else optional_future).append(f'D k{k:02d} {gen} r{r:02d} not yet completed');continue
    new='\n'.join('- '+item['text'] for item in x['new_screen_items']) if x['new_screen_items'] else '(此段没有新增文字)'
    for order in ('AB','BA'):
     # AB: A=new; BA: B=new; judge gets no writer identity, but both orderings.
     aa,bb=(new,oldtxt) if order=='AB' else (oldtxt,new)
     jid=f'D_k{k:02d}_r{r:02d}_gen{gen}_judge{judge}_{order}'
     txt=TEMPLATE['D']+f'\n【站点】k{k:02d}\n'+evidence+f'【匿名版本 A】\n{aa}\n【匿名版本 B】\n{bb}\n'
     add('D',judge,jid,txt,{'k':k,'repeat':r,'generating_model':gen,'new_side':'A' if order=='AB' else 'B','old_side':'B' if order=='AB' else 'A'},jobs,maps);counts['D']+=1
  # G directly compares two models, with two reviewer models and swapped side.
  for r in picks:
   xx={m:load_c(m,k,r) for m in MODELS}
   if any(xx[m] is None for m in MODELS):
    (missing if r<=5 else optional_future).append(f'G k{k:02d} r{r:02d} not both completed');continue
   for judge in MODELS:
    for order in ('AB','BA'):
     a_model='gpt6w' if order=='AB' else 'gpt56w'
     b_model='gpt56w' if order=='AB' else 'gpt6w'
     jid=f'G_k{k:02d}_r{r:02d}_judge{judge}_{order}'
     txt=(TEMPLATE['G']+f'\n【站点】k{k:02d}\n'+evidence+
       '\n【匿名版本 A（含屏幕编辑操作）】\n'+representation(xx[a_model])+
       '\n【匿名版本 B（含屏幕编辑操作）】\n'+representation(xx[b_model])+'\n')
     add('G',judge,jid,txt,{'k':k,'repeat':r,'A_model':a_model,'B_model':b_model,'judge_may_be_self':True},jobs,maps);counts['G']+=1
  # F independently looks across all 5/8/12 outputs from one generating model.
  for n in (5,8,12):
   for gen in MODELS:
    xs=[load_c(gen,k,r) for r in range(1,n+1)]
    if any(v is None for v in xs):
     (missing if n<=5 else optional_future).append(f'F k{k:02d} {gen} n{n:02d} incomplete');continue
    judge='gpt56w' if gen=='gpt6w' else 'gpt6w'
    rendered=[]
    for r,ob in enumerate(xs,1):
     # The judge sees all edited content/actions, with no model names or output hashes.
     short={a:ob.get(a) for a in ('action','new_screen_items','keep_ids','retire_ids','final_screen_text','editorial_tradeoff')}
     rendered.append(f'【T{r}】\n'+json.dumps(short,ensure_ascii=False,indent=2))
    jid=f'F_k{k:02d}_n{n:02d}_judge{judge}'
    txt=(TEMPLATE['F']+f'\n【station_k】{k}\n【sample_count】{n}\n'+evidence+
      '\n【同一匿名作者在独立会话中的各次输出】\n'+'\n'.join(rendered)+'\n')
    add('F',judge,jid,txt,{'k':k,'sample_count':n,'generating_model':gen,'independent_review':True},jobs,maps);counts['F']+=1
 # Save a consistent deterministic manifest; review files rewritten only before they're used.
 out=ROOT/'jobs/reviews/review_manifest.json';out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps({'schema':'music-blind-reviews-v2','jobs':jobs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 priv=ROOT/'private/review_mapping_DO_NOT_SHOW_JUDGES.json'
 priv.write_text(json.dumps({'jobs':maps,'note':'Never pass this mapping to D/G/F review models'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 dest=ROOT/'reports/judge_build_summary.json';dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(json.dumps({'counts':counts,'missing_base_inputs':missing,'optional_future_inputs_not_run':optional_future,'note':'Not yet generated jobs are NOT quality failures'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('BUILT',counts,'review jobs',len(jobs),'base outputs pending',len(missing),'optional future pending',len(optional_future))
if __name__=='__main__':main()
