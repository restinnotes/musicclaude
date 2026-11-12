"""Keep actual mg audit contents unchanged; reconcile a prompt label shadowing typo."""
import json,re,hashlib,time
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent
JOB='Q-final-completeness-recovery01'
folder=HERE/'jobs'/JOB
while not (folder/'result.json').exists():time.sleep(.5)
result=json.loads((folder/'result.json').read_text(encoding='utf-8'))
assert result['transport_success'] is True
prompt=(folder/'submitted-prompt.txt').read_text(encoding='utf-8')
assert '你是独立mg最终交付审计员 J4-bull。' in prompt
assert 'final-quality-audit-recovery01-input.txt' in prompt
assert '8f89495cc2646803766e6363d2535d7cf645d32f294e711e7e15b205e0411d5b' in prompt
parent=json.loads((HERE/'jobs'/'Q-final-completeness'/'completion-resolution.json').read_text(encoding='utf-8'))
assert parent['replacement_job_id']==JOB
assert hashlib.sha256((folder/'prompt.txt').read_bytes()).hexdigest()==parent['replacement_prompt_sha256']
response=(folder/'response.md').read_text(encoding='utf-8')
matches=[]
for block in re.findall(r'```json\s*([\s\S]*?)```',response):
    try:data=json.loads(block)
    except ValueError:continue
    if data.get('job_id')=='J4-bull' and isinstance(data.get('input_complete'),bool) and isinstance(data.get('accepted'),bool) and isinstance(data.get('checks'),list):matches.append(data)
assert len(matches)==1
# Do not change job_id, accepted, input_complete, findings, or any other model field.
raw=matches[0]
with (folder/'evidence.json').open('x',encoding='utf-8') as f:json.dump(raw,f,ensure_ascii=False,indent=2)
record={'execution_job_id':JOB,'model_declared_label':'J4-bull',
    'reason':'prepare_final_quality_audit loop variable shadowed the requested execution label; fixed for future calls',
    'submitted_prompt_preserved':True,'raw_model_json_unchanged':True,'audit_semantics_unchanged':True,
    'not_a_fifth_judge':True,'response_sha256':hashlib.sha256((folder/'response.md').read_bytes()).hexdigest(),
    'utc':datetime.now(timezone.utc).isoformat()}
(folder/'audit-label-reconciliation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'execution_job_id':JOB,'model_declared_label':'J4-bull','accepted':raw['accepted'],'raw_model_json_unchanged':True}))
