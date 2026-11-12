"""Mechanical final integrity checks only; substantive audit stays with mg."""
import json,hashlib,re
from pathlib import Path
from completed_reports import completed_files,resolved_folder
from prepare_reviews import ROLES
HERE=Path(__file__).resolve().parent
def main():
    rows=[]
    for n in range(1,9):
        for r in 'ABC':
            job=f'W{n}-{r}'; result,report=completed_files(job)
            rows.append({'job_id':job,'path':str(report.relative_to(HERE)),
                'sha256':hashlib.sha256(report.read_bytes()).hexdigest()})
    manifest=json.loads((HERE/'judge-evidence-pack.json').read_text(encoding='utf-8'))
    assert len(rows)==24 and len(manifest['raw_reports'])==24
    frozen_path=HERE/'sample-freeze-v1.json'
    frozen_sha=hashlib.sha256(frozen_path.read_bytes()).hexdigest()
    assert frozen_sha==(HERE/'sample-freeze-v1.sha256').read_text(encoding='utf-8').split()[0]
    frozen=json.loads(frozen_path.read_text(encoding='utf-8'))
    assert len(frozen['skus'])==54 and len({s['sku_id'] for s in frozen['skus']})==54
    pack=HERE/'judge-evidence-pack.txt'
    assert hashlib.sha256(pack.read_bytes()).hexdigest()==manifest['evidence_pack_sha256']
    source_index=json.loads((HERE/'coordinator-source-audit.json').read_text(encoding='utf-8'))
    assert source_index['review_performed'] is True and len(source_index['source_audits'])==25
    audit_file=HERE/'mg-source-audits-untruncated.txt'
    # compile_mg_audit_pack records the LF text hash, while Windows writes CRLF.
    assert hashlib.sha256(audit_file.read_text(encoding='utf-8').encode('utf-8')).hexdigest()==source_index['raw_audit_pack_sha256']
    judges=[]
    for job in ROLES:
        result,report=completed_files(job);text=report.read_text(encoding='utf-8')
        assert not re.search(r'^\s*#{0,6}\s*INPUT_INCOMPLETE',text,re.M),job
        inspected=[j['job_id'] for j in rows if j['job_id'] in text]
        assert len(inspected)==24,(job,'missing report identities')
        a=json.loads((resolved_folder(job)/'attachments.json').read_text(encoding='utf-8'))
        assert a['files'][0]['sha256']==manifest['evidence_pack_sha256']
        judges.append({'job_id':job,'resolved_job':resolved_folder(job).name,
            'sha256':hashlib.sha256(report.read_bytes()).hexdigest(),
            'all_24_report_identities_present':True})
    audit=json.loads((resolved_folder('Q-final-completeness')/'evidence.json').read_text(encoding='utf-8'))
    assert audit.get('input_complete') is True and audit.get('accepted') is True
    audit_folder=resolved_folder('Q-final-completeness')
    label_note=None
    if audit['job_id']!=audit_folder.name:
        note_path=audit_folder/'audit-label-reconciliation.json'
        label_note=json.loads(note_path.read_text(encoding='utf-8'))
        assert label_note['execution_job_id']==audit_folder.name and label_note['model_declared_label']==audit['job_id']
        assert label_note['raw_model_json_unchanged'] is True
        assert label_note['response_sha256']==hashlib.sha256((audit_folder/'response.md').read_bytes()).hexdigest()
    final=HERE/'FINAL_RESEARCH_REPORT.txt'
    assert final.read_text(encoding='utf-8')==completed_files('S1-final')[1].read_text(encoding='utf-8')
    assert len(final.read_text(encoding='utf-8'))>5000
    row={'raw_research_reports':rows,'judges':judges,'evidence_pack_sha256':manifest['evidence_pack_sha256'],
        'final_report_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
        'immutable_frozen_sample_sha256':frozen_sha,
        'final_mg_audit_accepted':True,'substantive_audit_by':'mg','mechanical_checks_passed':True,
        'final_audit_execution_job_id':audit_folder.name,'final_audit_model_declared_label':audit['job_id'],
        'audit_label_reconciliation':label_note,
        'independent_source_audits':25,'audited_candidates':len(source_index['candidate_checks']),
        'audited_observations':len(source_index['observation_checks']),
        'raw_audit_normalized_lf_sha256':source_index['raw_audit_pack_sha256'],
        'raw_audit_original_file_byte_sha256':hashlib.sha256(audit_file.read_bytes()).hexdigest(),
        'root_final_review_still_required':True}
    (HERE/'final-delivery-integrity.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(row,ensure_ascii=False))
if __name__=='__main__':main()
