#!/usr/bin/env python3
"""Offline source-grounded comparison. Requires results/<model>/Axx.txt containing JSON."""
import json, re, collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
G=json.loads((ROOT/'private/historical_main_verdicts_DO_NOT_SHOW_MODELS.json').read_text(encoding='utf8'))
MAN=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf8'))
CLASSES=['insight','restatement','manufactured','imported','undetermined']
def parse_json(s):
 try:return json.loads(s)
 except json.JSONDecodeError:
  s=s.strip();s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
  return json.loads(s)
def review(model):
 out={};fail=[]
 for j in MAN['jobs']:
  if j['track']!='A_E5':continue
  p=ROOT/'results'/model/(j['job_id']+'.txt')
  if not p.exists():fail.append((j['job_id'],'missing'));continue
  try:
   obj=parse_json(p.read_text(encoding='utf8'))
   revs=obj['reviews']; assert len(revs)==6
   ids=[r['blind_id'] for r in revs]
   assert ids==j['cases'],(j['job_id'],ids,j['cases'])
   for row in revs:
    assert row['verdict'] in CLASSES
    out[row['blind_id']]=row
  except Exception as e: fail.append((j['job_id'],str(e)[:200]))
 return out,fail
res={}
for model in ['gpt6w','gpt56w']:
 x,errors=review(model); k=[b for b in G if b in x]
 correct=sum(x[b]['verdict']==G[b]['verdict'] for b in k)
 classes=sorted({G[b]['verdict'] for b in k}|{x[b]['verdict'] for b in k})
 by_class={v:{'support':sum(G[b]['verdict']==v for b in k),
               'correct':sum(x[b]['verdict']==v==G[b]['verdict'] for b in k)} for v in classes}
 wrong=[{'case':b,'previous_main':G[b]['verdict'],'model':x[b]['verdict']} for b in k if x[b]['verdict']!=G[b]['verdict']]
 res[model]={'returned_cases':len(x),'calibration_total':len(k), 'calibration_matches':correct,
             'note':'历史模型主会话裁决只是 input-level 参考；不要把一致率解释成真正音乐质量',
             'by_class':by_class,'disagreements':wrong,'errors':errors}
a,ea=review('gpt6w');b,eb=review('gpt56w')
res['paired_differences']=[{'case':case,'gpt6w':a[case]['verdict'],'gpt56w':b[case]['verdict']} for case in a if case in b and a[case]['verdict']!=b[case]['verdict']]
(ROOT / 'reports').mkdir(exist_ok=True)
(ROOT/'reports/e5_calibration_summary.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Wrote reports/e5_calibration_summary.json')
