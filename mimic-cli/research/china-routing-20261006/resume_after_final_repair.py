"""After explicit full mg revision, run a fresh mg acceptance audit, preserving v1."""
import time,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
import run_pipeline
from completed_reports import completed_files,resolved_folder
from prepare_final_quality_audit import prepare
HERE=Path(__file__).resolve().parent
run_pipeline.status('mg_full_final_revision_after_material_audit_rejection')
while (HERE/'coordinator.lock').exists():time.sleep(5)
_,report=completed_files('S1-final')
text=report.read_text(encoding='utf-8')
if run_pipeline.input_incomplete(text):raise RuntimeError('Revised synthesis input incomplete; original request preserved')
(HERE/'FINAL_RESEARCH_REPORT.txt').write_text(text,encoding='utf-8')
parent=resolved_folder('Q-final-completeness')
qa=json.loads((parent/'evidence.json').read_text(encoding='utf-8'))
assert qa['accepted'] is False
job=parent.name+'-recovery01';filename='final-quality-audit-recovery01-input.txt'
prepare(job,filename)
folder=HERE/'jobs'/job
row={'original_job_id':parent.name,'replacement_job_id':job,
     'replacement_prompt_sha256':hashlib.sha256((folder/'prompt.txt').read_bytes()).hexdigest(),
     'reason':'Fresh independent mg quality audit of full revised report; previous rejected audit is preserved',
     'original_result_preserved':True,'utc':datetime.now(timezone.utc).isoformat()}
with (parent/'completion-resolution.json').open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
run_pipeline.main()
