#!/usr/bin/env python3
"""Import verified prior A01/B02 completed gpt2 pilot into r01. Never import failures or overwrite."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'jobs/manifest.json').read_text(encoding='utf-8'))
byid={x['job_id']:x for x in M['jobs']}
model_names={'gpt6w':'gpt-6-thinking','gpt56w':'gpt-5-6-thinking'}

def sha(s):return hashlib.sha256(s).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--pilot-root',required=True);a=p.parse_args()
 base=Path(a.pilot_root);src=base/'results';done=[];skipped=[]
 for job in ('A01','B02'):
  j=byid[job]
  for mdl,full in model_names.items():
   stem=src/(f'{job}__{mdl}');mfile=Path(str(stem)+'.meta.json');rawfile=Path(str(stem)+'.json')
   out=ROOT/'results'/'trials'/mdl/job/'r01'
   if Path(str(out)+'.meta.json').exists() or Path(str(out)+'.txt').exists():skipped.append([job,mdl,'destination exists']);continue
   if not mfile.exists() or not rawfile.exists():skipped.append([job,mdl,'source absent']);continue
   try:
    m=json.loads(mfile.read_text(encoding='utf-8-sig'))
    raw=rawfile.read_text(encoding='utf-8-sig')
    obj=json.loads(raw)
    response=obj['response'];server=obj['metadata']
    assert m.get('success') is True and m.get('returncode')==0
    assert m.get('prompt_sha256')==j['input_sha256']
    assert m.get('model_requested')==full==m.get('model_reported')==server.get('model')
    assert m.get('effort')=='max'==server.get('thinking_effort')
    assert obj.get('completed') is True and isinstance(response,str) and response.strip()
    assert hashlib.sha256((ROOT/j['model_prompt_paths'][mdl]).read_bytes()).hexdigest()==j['input_sha256']
    if server.get('response_sha256') and m.get('response_sha256'):
     assert server['response_sha256']==m['response_sha256']
   except Exception as e:
    skipped.append([job,mdl,'not validated: '+str(e)[:150]]);continue
   out.parent.mkdir(parents=True,exist_ok=True)
   d={'id':f'{job}:r01:{mdl}','model_requested':full,'model_reported':server['model'],
      'thinking_effort':server['thinking_effort'],'prompt_sha256':j['input_sha256'],
      'response_sha256_observed':sha(response.encode('utf-8')),
      'response_sha256_reported':server.get('response_sha256'),
      'completed':True,'exit_code':0,'elapsed_seconds':m.get('seconds'),
      'utc_start':m.get('utc'),'status':'success','phase':'completed',
      'new_session':True,'no_automatic_retry':True,'response_chars':len(response),
      'imported_from_pilot':str(stem),'context_warning':'legacy pilot earlier time window'}
   def save(ext,s): Path(str(out)+ext).write_text(s,encoding='utf-8')
   save('.txt',response);save('.meta.json',json.dumps(d,ensure_ascii=False,indent=2)+'\n')
   save('.raw.json',raw)
   stderr=Path(str(stem)+'.stderr.txt')
   save('.stderr.txt',stderr.read_text(encoding='utf-8',errors='replace') if stderr.exists() else '')
   done.append([job,mdl])
 print(json.dumps({'imported':done,'skipped':skipped,'note':'only verified successful A01/B02 imported; pre_submit C02 intentionally excluded'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
