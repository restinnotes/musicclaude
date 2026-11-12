"""Check actual completed finalization jobs; no model invocation and no resubmission."""
import hashlib
import json
import re
from pathlib import Path
import evo
import synth_v2

if __name__=='__main__':
 receipts=[]
 for p in sorted(evo.RUNS.glob('finish25_*/call.log')):
  rec=json.loads(p.read_text(encoding='utf-8'));run=p.parent
  if not rec.get('completed'):raise ValueError('incomplete finalization call '+run.name)
  match=re.search(r'--model\s+(\S+)',rec['command']);requested=match[1]
  job=Path(rec['job_directory']);r=json.loads((job/'result.json').read_text(encoding='utf-8'))
  if not(r.get('ok') is True and r.get('model')==requested and r.get('thinkingEffort')=='max'):
   raise ValueError('model/effort evidence mismatch '+run.name)
  prompt=(run/'input.txt').read_text(encoding='utf-8-sig').strip()
  assert prompt==(job/'prompt.txt').read_text(encoding='utf-8-sig').strip(),run.name
  original=run/'output_before_trailing_comma_repair.txt'
  output=(original if original.exists() else run/'output.txt').read_text(encoding='utf-8-sig').strip()
  assert output==(job/'response.txt').read_text(encoding='utf-8-sig').strip(),run.name
  receipts.append({'run_id':run.name,'model':requested,'effort':'max','seconds':rec['seconds'],'recovered_without_resubmission':bool(rec.get('recovered_from_job')),'job_directory':str(job),'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'actual_response_sha256':hashlib.sha256(output.encode()).hexdigest()})
 out=evo.ROOT/'evaluations/continuation_20261025/finalization/model_provenance_verification.json'
 synth_v2.dump(out,{'passed':True,'calls_checked':len(receipts),'calls':receipts})
 print('verified actual prompt/model/max/response for',len(receipts),'completed finalization jobs',flush=True)
