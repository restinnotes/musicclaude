"""Three unchanged local ModelTrace challenges over the current music provider."""
import argparse,hashlib,importlib.util,json,math,os,subprocess,time
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
BASE=Path('C:/Users/zuoyi/Documents/Codex/2026-09-26/j/work/modeltrace-ab-20260927')
PROJECT=BASE/'ModelTrace'
CLI=Path('D:/musicclaude/gpt2agent-safechain/bin/gpt4.cmd')
MODEL='gpt-5-6-thinking'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp():return datetime.now(timezone.utc).isoformat()
def main():
 global MODEL
 parser=argparse.ArgumentParser()
 parser.add_argument('--model',choices=['gpt-5-6-thinking','gpt-6-thinking'],default=MODEL)
 MODEL=parser.parse_args().model
 OUT=ROOT/'evaluations/d13_20261025'/('modeltrace_'+MODEL+'_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
 OUT.mkdir(parents=True,exist_ok=False)
 spec=importlib.util.spec_from_file_location('local_modeltrace',PROJECT/'fingerprint.py')
 fp=importlib.util.module_from_spec(spec);spec.loader.exec_module(fp)
 challenges=read(BASE/'challenges/official_modeltrace_challenges.json')
 bank_path=PROJECT/'data/unified_bank.json';bank=fp.load_bank(bank_path)
 save(OUT/'bank_snapshot.json',bank)
 save(OUT/'plan.json',{'started_utc':stamp(),'provider':'gpt4','requested_model':MODEL,'effort':'max',
  'maximum_new_requests':3,'serial_within_test':True,'automatic_retry':False,
  'prompt_source':str(BASE/'challenges/official_modeltrace_challenges.json'),
  'bank_source':str(bank_path),'bank_sha256':digest(bank_path),'scorer_source':str(PROJECT/'fingerprint.py'),
  'scorer_sha256':digest(PROJECT/'fingerprint.py'),'candidate_labels':[m['id']for m in bank['models']],
  'limitation':'Closed-set behavioral similarity, not authenticated backend identity or a reasoning-effort measurement.'})
 # Re-score historical responses against exactly the same frozen candidate bank.
 historical={}
 for arm in ['chrome-control','safechain']:
  old=[]
  for c in challenges:
   p=BASE/arm/(c['id']+'.txt')
   if p.exists():old.append({'text':p.read_text(encoding='utf-8-sig'),'expected_count':c['expected_count']})
  if old:historical[arm]=fp.analyze_global_outputs(old,bank)
 save(OUT/'historical_rescored.json',historical)
 outputs=[];records=[]
 print(json.dumps({'started':True,'directory':str(OUT),'historical_arms':list(historical)}),flush=True)
 for i,c in enumerate(challenges):
  probe=OUT/c['id'];probe.mkdir();prompt=probe/'prompt.txt';prompt.write_text(c['prompt'],encoding='utf-8')
  save(probe/'started.json',{'utc':stamp(),'requested_model':MODEL,'prompt_sha256':digest(prompt)})
  start=time.monotonic()
  cp=subprocess.run([str(CLI),'ask','--file',str(prompt),'--model',MODEL,'--json','--allow-topic-stream'],capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
  value={}
  for line in cp.stdout.decode('utf-8','replace').splitlines():
   try:x=json.loads(line)
   except ValueError:continue
   if isinstance(x,dict):value=x
  err={}
  for line in cp.stderr.decode('utf-8','replace').splitlines():
   try:x=json.loads(line)
   except ValueError:continue
   if isinstance(x,dict)and x.get('error_code'):err=x
  md=value.get('metadata')or{}
  complete=cp.returncode==0 and value.get('completed')is True and bool(value.get('response'))
  answer=value.get('response','') if complete else ''
  count=len(fp.parse_numbers(answer));accepted=complete and count>=max(80,math.ceil(c['expected_count']*.55))
  record={'probe':i+1,'completed':complete,'accepted':accepted,'elapsed_seconds':round(time.monotonic()-start,3),
   'expected_count':c['expected_count'],'parsed_numbers':count,'exit_code':cp.returncode,'ended_utc':stamp(),
   'model':md.get('model'),'thinking_effort':md.get('thinking_effort'),'job_directory':md.get('job_directory')or err.get('job_directory'),
   'error_code':err.get('error_code'),'automatic_retry':False}
  if answer:
   (probe/'response.txt').write_text(answer,encoding='utf-8');record['response_sha256']=digest(probe/'response.txt')
  if accepted:
   outputs.append({'text':answer,'expected_count':c['expected_count']})
   record['single_probe_analysis']=fp.analyze_global_outputs([outputs[-1]],bank)
  save(probe/'result.json',record);records.append(record)
  analysis=fp.analyze_global_outputs(outputs,bank)if outputs else None
  save(OUT/'analysis.json',{'updated_utc':stamp(),'requested_model':MODEL,'valid_probe_count':len(outputs),
   'three_probe_test_complete':len(outputs)==3,'probes':records,'modeltrace':analysis,
   'historical_rescored':historical,'bank_unchanged':read(bank_path)==bank,
   'limitations':['Candidate-bank probabilities do not authenticate backend identity.','Numeric fingerprint does not measure music quality or actual thinking duration.','Historical transport/account/model settings differ; historical scores are context, not a controlled before/after experiment.']})
  print(json.dumps({'probe':i+1,'completed':complete,'accepted':accepted,'seconds':record['elapsed_seconds'],
   'numbers':count,'model':record['model'],'error_code':record['error_code'],
   'prediction':analysis['prediction']if analysis else None,'closed_set_probability':analysis['probability']if analysis else None}),flush=True)
  if not accepted:break
  if i<2:time.sleep(6)
 print(json.dumps({'finished':True,'directory':str(OUT),'valid_probes':len(outputs)}),flush=True)
if __name__=='__main__':
 os.environ['PYTHONIOENCODING']='utf-8'
 main()
