"""Present the accepted mg deliverable, preserving all original model output."""
import json,re,hashlib
from datetime import datetime,timezone
from pathlib import Path
from completed_reports import resolved_folder
HERE=Path(__file__).resolve().parent
integrity=json.loads((HERE/'final-delivery-integrity.json').read_text(encoding='utf-8'))
assert integrity['final_mg_audit_accepted'] and integrity['mechanical_checks_passed']
report=HERE/'FINAL_RESEARCH_REPORT.txt'
assert hashlib.sha256(report.read_bytes()).hexdigest()==integrity['final_report_sha256']
reader=HERE/'FINAL_RESEARCH_REPORT_READABLE.txt'
text=report.read_text(encoding='utf-8')
reader_text=re.sub(r':chatgpt-content-reference\{[^}]*\}','',text)
reader.write_text(reader_text,encoding='utf-8')
integrity.update({'root_final_review_still_required':False,'coordinator_accepted':True,
    'completed_utc':datetime.now(timezone.utc).isoformat(),
    'reader_copy_sha256':hashlib.sha256(reader.read_bytes()).hexdigest(),
    'reader_copy_transform':'Only remove unsupported native ChatGPT file-citation rendering tokens; all prose, tables, source URLs and evidence IDs preserved. Original output remains untouched.'})
(HERE/'final-delivery-integrity.json').write_text(json.dumps(integrity,ensure_ascii=False,indent=2),encoding='utf-8')
q=resolved_folder('Q-final-completeness')
lines=['Accepted mg research delivery','Completed UTC: '+integrity['completed_utc'],
    'Research and substantive audits: mg / GPT-5.6 Sol / xhigh',
    '24 independent logical research replicates; 25 source audits; 4 independent judges.',
    'Initial final report failed material audit; full mg revision passed fresh audit.',
    'Final input_complete=true; accepted=true; material_fixes=[]; unsupported_final_numbers=[].',
    '','Reader copy: '+str(reader),'Preserved original final report: '+str(report),
    'Accepted final mg audit: '+str(q/'response.md'),
    'Audit execution label reconciliation (raw conclusions unchanged): '+str(q/'audit-label-reconciliation.json'),
    'Mechanical integrity manifest: '+str(HERE/'final-delivery-integrity.json'),
    'Frozen 54-SKU sample: '+str(HERE/'sample-freeze-v1.json'),
    'Audited observations: '+str(HERE/'audited-sku-observations.jsonl'),
    'Source audit index: '+str(HERE/'coordinator-source-audit.json'),
    'Untruncated source audits: '+str(HERE/'mg-source-audits-untruncated.txt'),
    'Original brief: '+str(HERE/'original-brief.txt'),'','24 original logical reports:']
lines += [row['job_id']+': '+str(HERE/row['path']) for row in integrity['raw_research_reports']]
lines += ['','Four original independent judges:']
lines += [row['job_id']+': '+str(HERE/'jobs'/row['resolved_job']/'response.md') for row in integrity['judges']]
(HERE/'FINAL_DELIVERY_INDEX.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
state={'stage':'completed','completed_utc':integrity['completed_utc'],'model':'gpt-5.6-sol',
    'effort':'xhigh','research_and_audits':'mg','coordinator_accepted':True,
    'final_mg_audit_accepted':True,'report':str(report),'reader_copy':str(reader),
    'remaining_authorized_work':[],'user_notified':False}
(HERE/'pipeline-status.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'stage':'completed','reader_characters':len(reader_text),'final_report_sha256':integrity['final_report_sha256'],'audit_accepted':True},ensure_ascii=False))
