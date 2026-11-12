"""Collect actual responses and conservative metadata, including first manual calls.
No calls are made and raw outputs are never changed.
"""
from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_calls import safe,parse_gpt2
R=Path(__file__).resolve().parents[1]
def j(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(safe(d),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def main():
 rows=[]
 for path in sorted((R/'calls').glob('*')):
  req=path/'request.json'
  if not req.exists():continue
  info=j(req); row=dict(info,dir=str(path.relative_to(R)),status='running')
  if (path/'exit.txt').exists():
   exitcode=int((path/'exit.txt').read_text(encoding='utf-8-sig').strip());row['exit_code']=exitcode
   try:
    body,metadata,errs=parse_gpt2((path/'raw.json').read_bytes(),{'job':{'model':info['requested_model']},'attachments':[]})
    row.update(status='ok' if not errs and exitcode==0 else 'failed_validation',errors=errs,actual_model=metadata['provider_metadata'].get('model'),server_model_slugs=metadata['server_model_slugs'],response_sha256=sha(body.encode()),response_chars=len(body),actual_effort=metadata['provider_metadata'].get('thinking_effort'))
    (path/'response.txt').write_text(body,encoding='utf-8',newline='\n')
    write(path/'metadata.json',dict(row,**metadata))
   except Exception as e:row.update(status='failed',parse_error=type(e).__name__)
  rows.append(row)
 for path in sorted((R/'scripts/call_results').glob('*')):
  if not path.is_dir():continue
  jf=path/'job.json';mf=path/'metadata.json'
  if not jf.exists():continue
  job=j(jf);meta=j(mf) if mf.exists() else {}
  rows.append({'job_id':job['job_id'],'dir':str(path.relative_to(R)),'status':meta.get('status','running'),'requested_model':job['model'],'requested_channel':job['channel'],**job.get('labels',{}),'prompt_sha256':sha((path/'prompt.txt').read_bytes()),'response_chars':len((path/'response.txt').read_text(encoding='utf-8')) if (path/'response.txt').exists() else None,'metadata_file':str(mf.relative_to(R)) if mf.exists() else None})
 write(R/'experiments/ACTUAL_CALLS.json',rows)
 out=['# 实际调用清单','', '每条对应实际落盘调用。planned jobs 不等于已调用；失败保留原输出，不暗中降配置或缩输入。','', '| Job | 模型请求标识 | 段 | 来源数 | 方法 | 状态 | 正文 |','|---|---|---|---|---|---|---|']
 for row in rows:
  rel=row['dir'].replace('\\','/')+'/response.txt';out.append('| '+ ' | '.join([row['job_id'],row['requested_model'],row.get('segment',''),str(row.get('source_count','')),row.get('method',''),row['status'],f'[原始响应](../{rel})' if (R/rel).exists() else '—'])+' |')
 (R/'experiments/ACTUAL_CALLS.md').write_text('\n'.join(out)+'\n',encoding='utf-8',newline='\n')
 print(json.dumps([{k:r.get(k) for k in ['job_id','status','response_chars']} for r in rows],ensure_ascii=False))
if __name__=='__main__':main()
