#!/usr/bin/env python3
"""Safe explicit gpt2 batch runner for independent repeats and frozen generated review prompts.

No automatic retry. Existing success/failure evidence never overwritten.
Without --execute, prints scheduled calls but makes NO external calls.
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODEL={'gpt6w':'gpt-6-thinking','gpt56w':'gpt-5-6-thinking'}

def sha(b): return hashlib.sha256(b).hexdigest()
def save(p,text):
 p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): raise FileExistsError(f'Would overwrite immutable evidence: {p}')
 tmp=p.with_name('.'+p.name+'.writing')
 tmp.write_text(text,encoding='utf-8')
 tmp.replace(p)
def compact(o):return json.dumps(o,ensure_ascii=False,indent=2)+'\n'

def tasks(a):
 if a.phase=='trial':
  m=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf-8'))
  for r in range(a.round_start,a.round_end+1):
   for j in m['jobs']:
    id=j['job_id']; tr=id[0]
    if a.track!='ALL' and tr!=a.track:continue
    if a.only_job and id not in a.only_job:continue
    first=j['first_model'] if r%2 else ('gpt56w' if j['first_model']=='gpt6w' else 'gpt6w')
    second='gpt56w' if first=='gpt6w' else 'gpt6w'
    for model in (first,second):
     prompt=ROOT/j['model_prompt_paths'][model]
     prefix=ROOT/'results'/'trials'/model/id/f'r{r:02d}'
     yield {'id':f'{id}:r{r:02d}:{model}','model':model,'prompt':prompt,'prefix':prefix,'prompt_hash':j['input_sha256']}
 else:
  jpath=ROOT/'jobs/reviews/review_manifest.json'
  if not jpath.exists(): raise FileNotFoundError(f'Build judge prompts first: {jpath}')
  j=json.loads(jpath.read_text(encoding='utf-8'))
  for row in j['jobs']:
   if a.track!='ALL' and row['kind']!=a.track:continue
   if a.only_job and row['job_id'] not in a.only_job:continue
   yield {'id':row['job_id'],'model':row['judge_model'],
    'prompt':ROOT/row['prompt_file'],
    'prefix':ROOT/'results'/'reviews'/row['judge_model']/row['job_id'],
    'prompt_hash':row['prompt_sha256']}

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--phase',choices=['trial','review'],default='trial')
 p.add_argument('--round-start',type=int,default=1);p.add_argument('--round-end',type=int,default=5)
 p.add_argument('--track',default='ALL',help='trial: A/B/C, review: D/G/F, or ALL')
 p.add_argument('--only-job',action='append',help='e.g. C02; may repeat; for review use exact generated review job_id')
 p.add_argument('--limit',type=int,default=0)
 p.add_argument('--execute',action='store_true',help='WITHOUT this flag, NO gpt2 calls are made')
 p.add_argument('--retry-confirmed-pre-submit',action='store_true',help='MANUAL only; archive verified pre-submit failure before explicit retry')
 p.add_argument('--timeout-seconds',type=int,default=1200)
 a=p.parse_args()
 if a.round_start<1 or a.round_end<a.round_start or a.round_end>12: p.error('range must be within 1..12')
 if a.track!='ALL' and a.track not in ({'A','B','C'} if a.phase=='trial' else {'D','G','F'}):p.error('invalid track for phase')
 if a.retry_confirmed_pre_submit and (not a.execute or not a.only_job or a.round_start!=a.round_end):
  p.error('--retry-confirmed-pre-submit requires --execute, --only-job, one exact round; no bulk retries')
 jobs=list(tasks(a))
 if a.limit>0:jobs=jobs[:a.limit]
 print(f'PHASE={a.phase} EXECUTE={a.execute} count={len(jobs)}',flush=True)
 gpt2=shutil.which('gpt2') if a.execute else None
 if a.execute and not gpt2: raise RuntimeError('gpt2 not found on PATH. Use T3 in a shell where gpt2 --help succeeds.')
 for n,job in enumerate(jobs,1):
  prefix=job['prefix']; meta_file=Path(str(prefix)+'.meta.json'); response_file=Path(str(prefix)+'.txt')
  if meta_file.exists() or response_file.exists():
   if a.retry_confirmed_pre_submit and meta_file.exists() and not response_file.exists():
    prior=json.loads(meta_file.read_text(encoding='utf-8'))
    if prior.get('status')=='confirmed_pre_submit_failure' and prior.get('phase')=='pre_submit':
     retry_index=1
     while Path(str(prefix)+f'.attempt{retry_index:02d}.meta.json').exists():retry_index+=1
     for suffix in ('.meta.json','.stderr.txt','.raw.json'):
      source=Path(str(prefix)+suffix)
      if source.exists():
       dest=Path(str(prefix)+f'.attempt{retry_index:02d}'+suffix)
       source.rename(dest)
     print(f'{n}/{len(jobs)} ARCHIVED confirmed pre-submit failure attempt{retry_index:02d}; explicit retry: {job["id"]}',flush=True)
    else:
     print(f'{n}/{len(jobs)} PRESERVED: not a confirmed pre-submit failure: {job["id"]}',flush=True);continue
   else:
    print(f'{n}/{len(jobs)} PRESERVED existing: {job["id"]}',flush=True);continue
  data=job['prompt'].read_bytes();actual=sha(data)
  if actual!=job['prompt_hash']:raise RuntimeError('Immutable prompt hash mismatch: '+job['id'])
  if len(data.decode('utf-8'))>65536:raise RuntimeError('gpt2 65536-char input limit: '+job['id'])
  if not a.execute:
   print(f'{n}/{len(jobs)} PLAN {job["id"]} input_bytes={len(data)} sha={actual[:12]}',flush=True);continue
  cmd=[gpt2,'ask','--file',str(job['prompt']),'--model',MODEL[job['model']],'--json']
  start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
  ret=None;stdout='';stderr='';error=None
  try:
   ret=subprocess.run(cmd,capture_output=True,encoding='utf-8',errors='replace',timeout=a.timeout_seconds)
   stdout=ret.stdout;stderr=ret.stderr
  except subprocess.TimeoutExpired as e:
   error='TIMEOUT_STATUS_UNKNOWN: subprocess was interrupted; check server evidence before retrying'
   stdout=(e.stdout or b'').decode('utf-8',errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '')
   stderr=(e.stderr or b'').decode('utf-8',errors='replace') if isinstance(e.stderr,bytes) else (e.stderr or '')
  except Exception as e:
   error=str(e)
  elapsed=round(time.monotonic()-start,3)
  output=None;wrapper={};server_meta={};response=''
  try:
   output=json.loads(stdout.strip().lstrip('\ufeff'))
   if isinstance(output,dict):
    wrapper=output;server_meta=output.get('metadata') or {};response=output.get('response') or ''
  except (ValueError,TypeError): pass
  route=server_meta.get('model');effort=server_meta.get('thinking_effort')
  success=(error is None and ret is not None and ret.returncode==0 and wrapper.get('completed') is True and
   isinstance(response,str) and len(response.strip())>0 and route==MODEL[job['model']] and effort=='max')
  phase=wrapper.get('phase')
  for blob in (stderr,stdout):
   if '"phase": "pre_submit"' in blob or '"phase":"pre_submit"' in blob:phase='pre_submit'
  status=('success' if success else ('confirmed_pre_submit_failure' if phase=='pre_submit' else 'failure_or_ambiguous'))
  meta={'id':job['id'],'model_requested':MODEL[job['model']],'model_reported':route,'thinking_effort':effort,
   'prompt_sha256':actual,'response_sha256_observed':sha(response.encode('utf-8')) if response else None,
   'response_sha256_reported':server_meta.get('response_sha256'),
   'completed':wrapper.get('completed'),'exit_code':ret.returncode if ret else None,
   'elapsed_seconds':elapsed,'utc_start':utc,'status':status,'phase':phase,'error':error,
   'new_session':True,'runner':'gpt2 ask --file --model --json','no_automatic_retry':True,
   'response_chars':len(response)}
  save(Path(str(prefix)+'.meta.json'),compact(meta))
  save(Path(str(prefix)+'.stderr.txt'),stderr)
  save(Path(str(prefix)+'.raw.json'),stdout)
  if success:save(response_file,response)
  print(f'{n}/{len(jobs)} {status}: {job["id"]} {elapsed:.1f}s {len(response)} chars',flush=True)
  if not success:
   print('STOP: preserve evidence and investigate; do not auto retry or count as model failure.',flush=True)
   return 2
 print('COMPLETED_OR_ALREADY_RECORDED',flush=True);return 0
if __name__=='__main__':sys.exit(main())
