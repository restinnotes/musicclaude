#!/usr/bin/env python3
"""Offline post-hoc blind-review analysis and adaptive extension candidates.

CANNOT declare actual artistic quality from judge majority; includes order and self-judge sensitivity.
"""
import collections,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
mapfile=R/'private/review_mapping_DO_NOT_SHOW_JUDGES.json'
if not mapfile.exists():raise SystemExit('Run build_repeat_judges.py first')
M=json.loads(mapfile.read_text(encoding='utf-8'))['jobs']

def parse(s):
 s=s.strip().lstrip('\ufeff')
 if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
 return json.loads(s)
rows=[];assess=collections.defaultdict(list);FS=[]
for job in M:
 judge=job['judge_model'];name=job['job_id'];p=R/'results/reviews'/judge/name
 txt=Path(str(p)+'.txt');meta=Path(str(p)+'.meta.json')
 line={'job_id':name,'kind':job['kind'],'judge':judge,'status':'missing'}
 if txt.exists() and meta.exists():
  try:
   m=json.loads(meta.read_text(encoding='utf-8'))
   assert m.get('status')=='success' and m.get('model_reported')=={'gpt6w':'gpt-6-thinking','gpt56w':'gpt-5-6-thinking'}[judge]
   x=parse(txt.read_text(encoding='utf-8'))
   assert x.get('task')==job['kind'] and x.get('station_k')==job['k']
   if job['kind'] in ('D','G'):
    assert x['winner'] in ('A','B','TIE','UNDETERMINED')
    if job['kind']=='D':
     winner=('new' if x['winner']==job['new_side'] else 'legacy' if x['winner']==job['old_side'] else x['winner'])
     key=(job['kind'],job['k'],job['repeat'],job['generating_model'],judge)
    else:
     winner=(job['A_model'] if x['winner']=='A' else job['B_model'] if x['winner']=='B' else x['winner'])
     key=(job['kind'],job['k'],job['repeat'],judge)
    line.update(status='valid',interpreted_winner=winner,side=x['winner'],order=x['job_id'][-2:] if 'job_id' in x else name[-2:])
    assess[key].append((name[-2:],winner))
   else:
    assert x.get('sample_count')==job['sample_count']
    assert x['saturation_assessment'] in ('SATURATED_WITHIN_SAMPLE','NOT_SATURATED','UNCERTAIN')
    line.update(status='valid',assessment=x['saturation_assessment'],recommend_more=x['recommend_more'],best_trial_candidate=x.get('best_trial_candidate'),
     late_new_unit_ids=x.get('late_round_new_valuable_unit_ids',[]))
    FS.append({'k':job['k'],'writer':job['generating_model'],'sample_count':job['sample_count'],
      'judge':judge,'assessment':x['saturation_assessment'],'recommend_more':x['recommend_more'],
      'late_new_valuable_units':x.get('late_round_new_valuable_unit_ids',[]),'best_trial_candidate_UNVERIFIED':x.get('best_trial_candidate'),
      'n_semantic_units':len(x.get('semantic_units',[]))})
  except Exception as e:
   line.update(status='invalid',error=str(e)[:250])
 elif meta.exists():line['status']='recorded_failure_or_missing_txt'
 rows.append(line)
# All 2-position review pairs: disagreement on AB-vs-BA is position effect / uncertainty.
order=[];candidates=collections.defaultdict(set)
for key,vals in sorted(assess.items()):
 outcomes={v for _,v in vals}
 rec={'kind':key[0],'comparison_key':str(key),'results':vals,'order_disagreement':len(outcomes)>1}
 order.append(rec)
 if len(outcomes)>1:
  candidates[key[1]].add('review_position_sensitive_or_underdetermined')
for x in FS:
 if x['recommend_more'] in ('YES','UNCERTAIN') or x['late_new_valuable_units'] or x['assessment']!='SATURATED_WITHIN_SAMPLE':
  candidates[x['k']].add('semantic_saturation_not_proven')
stable=json.loads((R/'reports/repeated_stability_summary.json').read_text(encoding='utf-8')) if (R/'reports/repeated_stability_summary.json').exists() else {}
for k,v in stable.get('A_case_stability',{}).items():
 if v['unstable']:
  candidates[k.split('/')[1]].add('E5_label_variability')
for k,v in stable.get('B_hypothesis_stability',{}).items():
 if v['unstable']:
  candidates[k.split('/')[1]].add('B_relation_verdict_variability')
output={'review_rows':rows,'order_sensitivity':order,'F_semantic_saturation':FS,
 'adaptation_candidates':{str(k):sorted(v) for k,v in candidates.items()},
 'interpretation_notes':[
  'A/B order flips indicate evaluator position sensitivity, not that the generating model changed.',
  'G both judges can evaluate their own anonymous texts; never treat as independent third-party truth.',
  'D opposite-model judge confounds candidate model with judge model, so D win rates cannot directly decide 6w vs 5.6w.',
  'F is a semantic proxy judge; evidence must be read before declaring saturation.',
  'E5 classification repeats within the same case are not additional independent cases.',
  'All extension flags are proposals for the local orchestrator, not permission to change prompts or production.'
 ]}
p=R/'reports/review_and_extension_summary.json';p.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('WROTE',p)
print('judge jobs valid',sum(x['status']=='valid' for x in rows),'/',len(rows),
      'order-sensitive comparisons',sum(x['order_disagreement'] for x in order),
      'saturation reviews',len(FS))
