"""Bundle completed mg source audits without inventing coordinator verification."""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone
from completed_reports import completed_files, resolved_folder

HERE=Path(__file__).resolve().parent

def compile_pack():
    research=[f'W{i}-{r}' for i in range(1,9) for r in 'ABC']
    for job in research:
        completed_files(job)
    audits=['R1-W1-'+r for r in 'ABC']+[f'R2-domestic-batch{i:02d}' for i in range(1,7)]+['R-'+s+'-sources' for s in ('W5','W6','W7','W8')]+[f'R{n}-batch{i:02d}' for n in (3,4) for i in range(1,7)]
    inputs,checks,candidate_checks,observation_checks,gaps=[],[],[],[],[]
    sections=[]
    for job in audits:
        folder=resolved_folder(job)
        rp,ep=folder/'result.json',folder/'evidence.json'
        if not rp.exists() or not ep.exists():raise SystemExit(job+' mg audit is incomplete')
        result=json.loads(rp.read_text(encoding='utf-8'))
        data=json.loads(ep.read_text(encoding='utf-8'))
        if not result.get('transport_success') or data.get('review_performed') is not True or data.get('web_research_available') is not True:
            raise SystemExit(job+' lacks an actual completed mg browsing audit')
        raw=(folder/'response.md').read_text(encoding='utf-8')
        sha=hashlib.sha256(raw.encode('utf-8')).hexdigest()
        inputs.append({'job_id':job,'response_sha256':sha,'raw_report':str(folder/'response.md'),
            'screenshots_complete':result.get('screenshots_complete',False)})
        sources={s.get('source_id'):s for s in data.get('sources',[]) if isinstance(s,dict)}
        for c in data.get('claim_audits',[]):
            checks.append({**c,'audit_job_id':job,'audit_source_records':[sources[s] for s in c.get('source_ids',[]) if s in sources],
                'original_job_id':c.get('original_job_id') or data.get('audited_job_id')})
        candidate_checks.extend({**c,'audit_job_id':job} for c in data.get('candidate_audits',[]))
        observation_checks.extend({**c,'audit_job_id':job} for c in data.get('observation_audits',[]))
        gaps.extend({'audit_job_id':job,'gap':g} for g in data.get('data_gaps',[]))
        sections.append('\n=== UNTRUNCATED MG SOURCE AUDIT '+job+'; SHA256 '+sha+' ===\n'+raw)
    pack=''.join(sections)
    (HERE/'mg-source-audits-untruncated.txt').write_text(pack,encoding='utf-8')
    payload={'compiled_at_utc':datetime.now(timezone.utc).isoformat(),'review_performed':True,
        'reviewer':'independent mg source-audit sessions; coordinator compilation only',
        'source_audits':inputs,'raw_audit_pack_sha256':hashlib.sha256(pack.encode('utf-8')).hexdigest(),
        'claim_checks':checks,'candidate_checks':candidate_checks,'observation_checks':observation_checks,'data_gaps':gaps,
        'legacy_coordinator_audit':'w1-independent-coordinator-audit.json retained as prior work, not substituted for mg audits',
        'status_policy':'Blocked/not checked/page shell/conflict/incomplete components remain unverified; model claims cannot self-upgrade. Only primary-page observations actually attested by the mg auditors carry their explicit status and caveats.',
        'raw_reports_untruncated':True,'human_review_performed':False}
    (HERE/'coordinator-source-audit.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'mg_source_audits':len(inputs),'claim_checks':len(checks),'candidate_checks':len(candidate_checks),'observation_checks':len(observation_checks)}))

if __name__=='__main__':compile_pack()
