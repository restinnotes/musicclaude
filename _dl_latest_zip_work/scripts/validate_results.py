#!/usr/bin/env python3
"""Validate paired outputs without new calls; never rewrite results."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
M=json.loads((R/'jobs/manifest.json').read_text(encoding='utf8'))
ALLOWED_A={'insight','restatement','manufactured','imported','undetermined'}
ALLOWED_B={'valuable_new_link','restatement','unsupported_causality','premature_lock','not_enough_evidence'}
ALLOWED_C={'KEEP','RETIRE','REPLACE','APPEND','SILENCE'}
def parse(s):
 s=s.strip()
 if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
 return json.loads(s)
rows=[]
for j in M['jobs']:
 for model in M['models']:
  p=R/'results'/model/(j['job_id']+'.txt')
  d={'job':j['job_id'],'model':model,'status':'missing'}
  if not p.exists():rows.append(d);continue
  try:
   o=parse(p.read_text(encoding='utf8'))
   assert isinstance(o,dict)
   if j['track']=='A_E5':
    assert o['batch_id']==j['job_id']
    assert [v['blind_id'] for v in o['reviews']]==j['cases']
    assert all(v['verdict'] in ALLOWED_A for v in o['reviews'])
    raw=(R/f"inputs/e5/{j['job_id']}_source.txt").read_text(encoding='utf8')
    for v in o['reviews']:
     assert isinstance(v['evidence'],list) and v['evidence']
     for q in v['evidence']:
      assert isinstance(q['item_number'],int) and q['item_number']>0
      assert q['quote'] in raw
   elif j['track']=='B_RELATION':
    original=json.loads((R/f"inputs/op60/B_k{j['k']:02d}.json").read_text(encoding='utf8'))
    ids=[v['id'] for name in ('thread_hypotheses','why_hypotheses','mech_hypotheses') for v in original[name]]
    reviews=o['reviews']
    assert o['station_k']==j['k'] and o['task']=='B'
    assert len(reviews)==len(ids) and set(r['hypothesis_id'] for r in reviews)==set(ids)
    assert all(r['verdict'] in ALLOWED_B for r in reviews)
   else:
    original=json.loads((R/f"inputs/op60/C_k{j['k']:02d}.json").read_text(encoding='utf8'))
    assert o['station_k']==j['k'] and o['task']=='C'
    assert o['action'] in ALLOWED_C
    previous={v['id']:v['text'] for v in original['screen_before']}
    candidates={v['id'] for v in original['current_candidates']}
    keeps=o['keep_ids'];retires=o['retire_ids']
    assert len(keeps)==len(set(keeps)) and len(retires)==len(set(retires))
    assert set(keeps).isdisjoint(retires)
    assert set(keeps)|set(retires)==set(previous)
    assert all(x.get('text') and x.get('source_ids') and set(x['source_ids'])<=candidates for x in o['new_screen_items'])
    assert set(o.get('expand_ids',[]))<=candidates
    assert set(o.get('recap_ids',[]))<=candidates
    expect=[previous[v['id']] for v in original['screen_before'] if v['id'] in keeps]+[x['text'] for x in o['new_screen_items']]
    assert o['final_screen_text']==expect
    if o['action']=='KEEP':assert not o['new_screen_items'] and not retires
    if o['action']=='SILENCE':assert not keeps and not o['new_screen_items']
   d['status']='valid'
  except Exception as e:
   d.update(status='invalid',error=str(e)[:300])
  rows.append(d)
(R/'reports').mkdir(exist_ok=True)
(R/'reports/output_validation.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for v in rows:print(v['job'],v['model'],v['status'],v.get('error',''))
print('valid',sum(v['status']=='valid' for v in rows),'missing',sum(v['status']=='missing' for v in rows),'invalid',sum(v['status']=='invalid' for v in rows))
