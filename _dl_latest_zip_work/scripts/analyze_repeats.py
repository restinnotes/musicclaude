#!/usr/bin/env python3
"""Read independent repeats and summarize categorical stability/coverage only; NEVER assign aesthetic scores."""
import collections,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf-8'))
GT=json.loads((ROOT/'private/historical_main_verdicts_DO_NOT_SHOW_MODELS.json').read_text(encoding='utf-8'))
ALLOWED_A={'insight','restatement','manufactured','imported','undetermined'}
ALLOWED_B={'valuable_new_link','restatement','unsupported_causality','premature_lock','not_enough_evidence'}
ALLOWED_C={'KEEP','RETIRE','REPLACE','APPEND','SILENCE'}
def parse(s):
 s=s.strip().lstrip('\ufeff')
 if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
 return json.loads(s)
def normalize(j,m,r):
 p=ROOT/'results'/'trials'/m/j['job_id']/f'r{r:02d}'
 mp=Path(str(p)+'.meta.json');txt=Path(str(p)+'.txt')
 if not mp.exists():return 'missing',None
 try:
  meta=json.loads(mp.read_text(encoding='utf-8'));assert meta['status']=='success'
  assert meta['model_reported']=={'gpt6w':'gpt-6-thinking','gpt56w':'gpt-5-6-thinking'}[m]
  assert meta['prompt_sha256']==j['input_sha256']
  assert txt.is_file()
  obj=parse(txt.read_text(encoding='utf-8'))
  if j['track']=='A_E5':
   assert obj['batch_id']==j['job_id'];rev=obj['reviews'];assert [q['blind_id'] for q in rev]==j['cases']
   assert all(q['verdict'] in ALLOWED_A for q in rev)
   sourcetext=(ROOT/f"inputs/e5/{j['job_id']}_source.txt").read_text(encoding='utf-8')
   assert all(q['quote'] in sourcetext for row in rev for q in row['evidence'])
  elif j['track']=='B_RELATION':
   orig=json.loads((ROOT/f"inputs/op60/B_k{j['k']:02d}.json").read_text(encoding='utf-8'))
   ids={z['id'] for typ in ('thread_hypotheses','why_hypotheses','mech_hypotheses') for z in orig[typ]}
   assert obj['station_k']==j['k'] and obj['task']=='B'
   assert {q['hypothesis_id'] for q in obj['reviews']}==ids
   assert all(q['verdict'] in ALLOWED_B for q in obj['reviews'])
  else:
   orig=json.loads((ROOT/f"inputs/op60/C_k{j['k']:02d}.json").read_text(encoding='utf-8'))
   assert obj['station_k']==j['k'] and obj['task']=='C' and obj['action'] in ALLOWED_C
   previous={z['id']:z['text'] for z in orig['screen_before']}
   candidates={z['id'] for z in orig['current_candidates']}
   keep=obj['keep_ids'];retire=obj['retire_ids']
   assert set(keep)|set(retire)==set(previous) and not(set(keep)&set(retire))
   assert all(z['text'] and z['source_ids'] and set(z['source_ids'])<=candidates for z in obj['new_screen_items'])
   assert obj['final_screen_text']==[z['text'] for z in orig['screen_before'] if z['id'] in keep]+[z['text'] for z in obj['new_screen_items']]
  return 'valid',obj
 except Exception as e:
  return 'invalid:'+str(e)[:200],None

def main():
 # Examine up to r12 whether or not they exist.
 rs={};A=collections.defaultdict(list);B=collections.defaultdict(list);C=collections.defaultdict(list)
 for j in M['jobs']:
  for m in M['models']:
   for r in range(1,13):
    st,obj=normalize(j,m,r)
    rs[f'{j["job_id"]}/{m}/r{r:02d}']=st
    if st!='valid':continue
    if j['track']=='A_E5':
     for z in obj['reviews']:A[(m,z['blind_id'])].append((r,z['verdict']))
    elif j['track']=='B_RELATION':
     for z in obj['reviews']:B[(m,j['job_id'],z['hypothesis_id'])].append((r,z['verdict']))
    else:
     ids=[x for item in obj['new_screen_items'] for x in item['source_ids']]
     C[(m,j['job_id'])].append({'r':r,'action':obj['action'],'n_new_screen_items':len(obj['new_screen_items']),
      'source_ids':list(dict.fromkeys(ids)),
      'screen_fingerprint':hashlib.sha256('\n'.join(obj['final_screen_text']).encode()).hexdigest()[:16]})
 cases={}
 for (m,c),values in sorted(A.items()):
  cnt=dict(collections.Counter(x for _,x in values));classes=list(cnt)
  cases[f'{m}/{c}']={'trials':values,'verdict_counts':cnt,'unstable':len(classes)>1,
    'historical_verdict':GT.get(c),'historical_agreements':sum(x==GT.get(c) for _,x in values) if c in GT else None,
    'historical_is_not_ground_truth':True}
 threads={f'{m}/{j}/{h}':{'trials':v,'verdict_counts':dict(collections.Counter(x for _,x in v)),'unstable':len(set(x for _,x in v))>1} for (m,j,h),v in sorted(B.items())}
 screens={}
 for (m,j),v in sorted(C.items()):
  src=collections.Counter(x for row in v for x in row['source_ids'])
  screens[f'{m}/{j}']={'trials':v,'action_counts':dict(collections.Counter(row['action'] for row in v)),
   'selected_source_frequency':dict(src),
   'semantic_saturation':'NOT_MACHINE_MEASURABLE: read independent F judge outputs',
   'single_output_cannot_establish_model_quality':True}
 report={'method':'fixed inputs, independent gpt2 sessions; historical labels not ground truth',
 'statuses':rs,'A_case_stability':cases,'B_hypothesis_stability':threads,'C_editing_variability':screens,
 'warnings':['repeats within case/station are NOT independent test examples',
             'source ID stability is not semantic saturation',
             'judge label counts without audit are not musical truth',
             'pre_submit failures are not SILENCE']}
 out=ROOT/'reports/repeated_stability_summary.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('WROTE',out)
 base={k:v for k,v in rs.items() if int(k.split('/r')[-1])<=5}
 ext={k:v for k,v in rs.items() if int(k.split('/r')[-1])>5}
 print('base r01-r05: valid',sum(v=='valid' for v in base.values()),'missing',sum(v=='missing' for v in base.values()),'invalid/failed',sum(v not in ('valid','missing') for v in base.values()))
 print('optional r06-r12: valid',sum(v=='valid' for v in ext.values()),'not_run',sum(v=='missing' for v in ext.values()))
 print('E5 cases unstable',sum(v['unstable'] for v in cases.values()),'/',len(cases))
 print('Thread hypotheses unstable',sum(v['unstable'] for v in threads.values()),'/',len(threads))
if __name__=='__main__':main()
