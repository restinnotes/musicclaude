"""Adopt degree/provenance corrections found by the five-field candidate audit.
The causal mechanism remains the depth-reviewed proposal; previous raw reviews are unchanged.
"""
import copy
import json
from concurrent.futures import ThreadPoolExecutor
import evo
import synth_v2

if __name__=='__main__':
 src=json.loads((evo.ROOT/'evaluations/synth/C25editor5_op60/run.json').read_text(encoding='utf-8'))
 run=synth_v2.Run('C25editor6','op60','g6','C25pilot');run.state=copy.deepcopy(src['state'])
 changes={
  'S04':('第一次，他可以单凭正在发生的亲近安心','先前，眼前的亲近仍足以让他暂时安定，不必立刻追问延续'),
  'S05':('初次相伴时，只要亲近正在发生，他就能安心','先前，正在发生的亲近还足以给他暂时的安慰，不必立刻追问延续')}
 for sec,(a,b) in changes.items():
  st=run.state[sec]
  for c in st['chosen']:c['text']=c['text'].replace(a,b)
  st['pick']['chosen']=copy.deepcopy(st['chosen'])
  for c in st['extra']:c['text']=c['text'].replace(a,b)
 run.state['S05']['chosen'][0]['depends']=['H2','H3','H4','H5','H6']
 run.state['S05']['pick']['chosen']=copy.deepcopy(run.state['S05']['chosen'])
 h='熟悉的亲近感再次出现时仍给得出早先的舒服，却也使已经生出的延续需要更加真切；眼前满足已不能完全容纳这个需要，因而这次的欢喜更迫切、更难舍。'
 run.state['S04']['hist'][0]['text']=h;run.state['S04']['pick']['new_history'][0]['text']=h
 # Full audit text is stored as an audit, not silently attributed to the original author.
 a=json.loads((evo.ROOT/'evaluations/continuation_20261025/choice_audit_C25editor4_op60.json').read_text(encoding='utf-8'))
 b=json.loads((evo.ROOT/'evaluations/continuation_20261025/choice_audit_C25editor5_op60.json').read_text(encoding='utf-8'))
 for sec in run.state:
  r=a[sec] if sec<'S03' else b[sec]
  run.state[sec]['pick']['eval']=copy.deepcopy(r['eval'])
  run.state[sec]['candidate_audit_provenance']={'review_run':r['review_run'],'scope':'五项逐候选判断；原始报告保留。S04/S05程度与来源修正另复核。'}
 run.status='precision_revision_pending';run.save()
 def check(sec):
  pk=run.state[sec]['pick'];msg=run.check_msg(sec,pk);ck=run.call(sec+'_B',msg,'g6',{'sec':sec})
  errs=run.validate_check(sec,pk,ck)
  ck['pass']=ck.get('section_pass') is True and all(m.get('usable') for m in ck.get('mechanisms',[])) and not ck.get('problems') and not errs
  if errs:ck['problems']=ck.get('problems',[])+errs
  return ck
 with ThreadPoolExecutor(max_workers=3) as ex:
  f4=ex.submit(check,'S04');f5=ex.submit(check,'S05');fg=ex.submit(run.glob_check,'S05')
  c4,c5,g=f4.result(),f5.result(),fg.result()
 for sec,ck in (('S04',c4),('S05',c5)):
  run.state[sec]['check']=ck;synth_v2.dump(run.dir/f'{sec}.json',run.state[sec]);print(sec,ck['pass'],ck.get('problems'),flush=True)
 run.checkpoints['S05']=g
 run.status='pilot_passed:S05' if c4['pass'] and c5['pass'] and g.get('ok') else 'needs_precision_revision'
 run.save();print(run.status,flush=True)
