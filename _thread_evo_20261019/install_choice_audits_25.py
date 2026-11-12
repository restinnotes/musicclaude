"""Install complete independent candidate assessments without changing selected meaning or History."""
import copy
import hashlib
import json
from pathlib import Path
import evo
import synth_v2

ROOT=evo.ROOT/'evaluations/continuation_20261025'

def meaning(d):
 return json.dumps({s:{k:st[k] for k in ('chosen','hist')}|{'fate':st['pick']['fate']} for s,st in d['state'].items()},ensure_ascii=False,sort_keys=True)

def install(tag,work,groups):
 p=evo.ROOT/f'evaluations/synth/{tag}_{work}/run.json';d=json.loads(p.read_text(encoding='utf-8'));before=meaning(d)
 reports={}
 for name,secs in groups:
  path=ROOT/name;rs=json.loads(path.read_text(encoding='utf-8'))
  for sec in secs:
   if sec in reports:raise ValueError('audit overlap')
   reports[sec]=(rs[sec],name)
 for sec,(r,name) in reports.items():
  if r.get('selection_acceptable') is not True or r.get('schema_errors'):raise ValueError('selection audit failed: '+sec)
  if r.get('problems'):raise ValueError('unresolved selection audit problems: '+sec)
  run=synth_v2.Run(tag,work,'g6','C25whole');run.state=d['state']
  expected={m['id'] for m in run.mechs(sec)};es=r['eval']
  if len(es)!=len(expected) or {e['id'] for e in es}!=expected:raise ValueError('candidate inventory changed')
  bids={b['id'] for b in run.beads if b['sec']==sec and b['role']!='演奏条件'}
  if any(not set(e.get('explains',[]))<=bids for e in es):raise ValueError('unknown/other-section bead in candidate audit')
  st=d['state'][sec];st['pick']['eval']=copy.deepcopy(es)
  st['candidate_audit_final']={'artifact':name,'review_run':r['review_run'],'selection_acceptable':True,'limitations':r.get('limitations',[]),'suggestions':r.get('suggestions',[]),'reason':r.get('reason','')}
  synth_v2.dump(p.parent/f'{sec}.json',st)
 if meaning(d)!=before:raise ValueError('audit installation changed selected meaning')
 d['candidate_audit_installation']={'sections':list(reports),'selected_meaning_sha256':hashlib.sha256(before.encode()).hexdigest(),'does_not_change':'chosen/History/fate; only installs independent assessments and their qualifications'}
 synth_v2.dump(p,d);print(tag,'installed',list(reports),flush=True)

if __name__=='__main__':
 import sys
 if sys.argv[1]=='op60':
  install('C25whole60','op60',[
   ('choice_audit_C25middle_op60_S08-S10-S13.json',['S08','S10','S13']),
   ('choice_audit_C25middle_op60_S06-S07-S09-S11-S12.json',['S06','S07','S09','S11','S12']),
   ('choice_audit_C25whole60_op60_S14.json',['S14'])])
 else:
  install('C25op61body2','op61',[
   ('choice_audit_C25op61_op61.json',['S01','S02']),
   ('choice_audit_C25op61classified_op61_S03-S04-S06-S07-S08-S10-S11-S12-S13.json',['S03']),
   ('choice_audit_C25op61body2_op61_S04.json',['S04']),
   ('choice_audit_C25op61body2_op61_S05-S06-S07-S08-S09-S10-S11-S12-S13.json',['S05','S06','S07','S08','S09','S10','S11','S12','S13'])])
