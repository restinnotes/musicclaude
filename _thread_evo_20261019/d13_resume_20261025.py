"""User-authorized continuation through the existing provider, one request at a time."""
import os
os.environ['THREAD_GPT']='gpt4'
os.environ['EVO_ATTEMPTS']='1'
os.environ.pop('D13_TRANSPORT_NO_BUFFERING',None)
import json,time,traceback
from datetime import datetime,timezone
from concurrent.futures import ThreadPoolExecutor as Executor
import d13_experiment as ex
import d13_original_prompt as original
import d13_evaluate as ev
import d13_forensic_finalize as forensic

O=ex.O
STATE=O/'resume_20261025_state.json'
EVENTS=O/'resume_20261025_events.jsonl'

def stamp():return datetime.now(timezone.utc).isoformat()
class ProviderUnusable(BaseException):pass
class SerialExecutor(Executor):
 def __init__(self,*args,**kwargs):
  kwargs.pop('max_workers',None)
  super().__init__(max_workers=1)

state={'started_utc':stamp(),'user_authorization':'Continue using this provider until almost unusable; no new hard lock.',
 'account_entry':'gpt4','generation_model':ex.evo.G56,'workers':1,
 'stop_rule':'three consecutive newly submitted requests without a verified complete response; or six failures in last eight new requests',
 'consecutive_failures':0,'new_calls':[],'tasks':[],'status':'running'}

def persist():ex.save(STATE,state)
def event(value):
 value={'utc':stamp(),**value}
 with EVENTS.open('a',encoding='utf-8')as f:f.write(json.dumps(value,ensure_ascii=False)+'\n')
 print(json.dumps(value,ensure_ascii=False),flush=True)

real_call=ex.evo.call
def tracked_call(run_id,*args,**kwargs):
 if ex.evo.done(run_id):return real_call(run_id,*args,**kwargs)
 recent=state['new_calls'][-8:]
 if state['consecutive_failures']>=3 or (len(recent)==8 and sum(not x['complete'] for x in recent)>=6):
  raise ProviderUnusable('Serial continuation failure threshold already reached; no new request sent')
 event({'event':'request_started','run_id':run_id,'model':kwargs.get('model')})
 result=real_call(run_id,*args,**kwargs)
 complete=bool(result)
 record={'run_id':run_id,'complete':complete,'ended_utc':stamp()}
 state['new_calls'].append(record)
 state['consecutive_failures']=0 if complete else state['consecutive_failures']+1
 persist();event({'event':'request_finished',**record})
 tail=state['new_calls'][-8:]
 if state['consecutive_failures']>=3 or (len(tail)==8 and sum(not x['complete'] for x in tail)>=6):
  raise ProviderUnusable('No useful complete answers in the recent serial continuation requests')
 return result

def task(label,fn):
 record={'task':label,'started_utc':stamp(),'status':'running'}
 state['tasks'].append(record);persist();event({'event':'task_started','task':label})
 try:
  fn();record['status']='returned'
 except ProviderUnusable:
  record['status']='provider_unusable';raise
 except Exception as error:
  record.update(status='incomplete',error=repr(error))
  event({'event':'task_incomplete','task':label,'error':repr(error)})
 finally:
  record['ended_utc']=stamp();persist()

def main():
 # This queue starts only after the first serial continuation process exits.
 # Include every newly submitted Section, including any failed final Section.
 seed=list(ex.evo.RUNS.glob('D13_d13v8A_56_op60_r1_S*'))
 seed=[p for p in seed if (p/'input.txt').exists() and (p/'input.txt').stat().st_mtime>datetime(2026,10,25,23,15,tzinfo=timezone.utc).timestamp()]
 for p in sorted(seed,key=lambda p:(p/'input.txt').stat().st_mtime):
  complete=bool(ex.evo.done(p.name))
  state['new_calls'].append({'run_id':p.name,'complete':complete,'seed_from_first_serial_request':True})
  state['consecutive_failures']=0 if complete else state['consecutive_failures']+1
 ex.evo.call=tracked_call
 for module in (ex,ev,original,forensic):module.ThreadPoolExecutor=SerialExecutor
 persist()
 try:
  task('complete existing v2 Op61 B repeat3',lambda:ex.generate('B','op61',3,3,'v2'))
  task('continue latest v8 A pilot',lambda:original.generate_original('A','op60',1,5,'v8'))
  task('latest v8 B pilot',lambda:original.generate_original('B','op60',1,5,'v8'))
  task('latest v8 C pilot',lambda:original.generate_original('C','op60',1,5,'v8'))
  task('evaluate v8 completed pilot prefixes',lambda:ev.evaluate('v8'))
  task('evaluate v2 existing repeats incl Op61',lambda:ev.evaluate('v2'))
  task('continue v2 A repeat1 through S13 without jumping',lambda:ex.generate('A','op60',1,13,'v2'))
  task('evaluate v2 long-distance chains',lambda:ev.evaluate('v2',long=True))
  for w in ex.TAGS:
   task('build v2 pool '+w,lambda w=w:ev.pool_build('v2',w))
   task('select v2 coherent path '+w,lambda w=w:ev.path_select('v2',w))
   task('independent verification of v2 path '+w,lambda w=w:ev.path_verify('v2',w))
  for w in ex.TAGS:task('contextual source audit '+w,lambda w=w:forensic.finalize(w))
  state['status']='queue_finished_needs_result_review'
 except ProviderUnusable as error:
  state.update(status='provider_unusable',stop_reason=str(error))
  event({'event':'provider_unusable','reason':str(error)})
 finally:
  state['ended_utc']=stamp();persist()
  event({'event':'queue_ended','status':state['status'],'calls':len(state['new_calls'])})

if __name__=='__main__':main()
