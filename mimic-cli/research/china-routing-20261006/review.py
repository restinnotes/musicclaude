"""Index completed mg artifacts without upgrading agent claims into verified facts."""
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent

def rows_to_csv(path, rows):
    if not rows:
        path.write_text('', encoding='utf-8-sig')
        return
    keys = sorted({key for row in rows for key in row})
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list))
                else value for key, value in row.items()})

def main():
    sources, claims, candidates, gaps, reviews = [], [], [], [], []
    verification_file = HERE / 'source-verification-notes.json'
    verification = json.loads(verification_file.read_text(encoding='utf-8')) if verification_file.exists() else {}
    checks_by_source = {}
    checks_by_claim = {}
    for check in verification.get('checks', []):
        for identifier in check.get('source_ids', []):
            checks_by_source.setdefault(check['job_id'] + ':' + identifier, []).append(check)
        for identifier in check.get('claim_ids', []):
            checks_by_claim.setdefault(check['job_id'] + ':' + identifier, []).append(check)
    # Later source verification is performed by fresh mg audit sessions. Preserve
    # their provenance and caveats in the ledger rather than replacing it with
    # the coordinator's earlier partial checks.
    for audit_folder in sorted((HERE/'jobs').iterdir()):
        if not audit_folder.name.startswith('R'): continue
        audit_result=audit_folder/'result.json'
        audit_evidence=audit_folder/'evidence.json'
        if not audit_result.exists() or not audit_evidence.exists(): continue
        if not json.loads(audit_result.read_text(encoding='utf-8')).get('transport_success'): continue
        audit=json.loads(audit_evidence.read_text(encoding='utf-8'))
        if audit.get('review_performed') is not True: continue
        for row in audit.get('claim_audits',[]):
            original_job=row.get('original_job_id') or audit.get('audited_job_id')
            original_claim=row.get('original_claim_id')
            if not original_job or not original_claim: continue
            check={**row,'verification_performer':'independent mg source audit',
                'audit_job_id':audit_folder.name,'audit_artifact':str(audit_folder/'response.md'),
                'audit_response_sha256':hashlib.sha256((audit_folder/'response.md').read_bytes()).hexdigest()}
            checks_by_claim.setdefault(original_job+':'+original_claim,[]).append(check)
            for source_id in row.get('original_source_ids',[]):
                checks_by_source.setdefault(original_job+':'+source_id,[]).append(check)
    for folder in sorted((HERE / 'jobs').iterdir()):
        result_path = folder / 'result.json'
        if not result_path.exists():
            continue
        result = json.loads(result_path.read_text(encoding='utf-8'))
        evidence_path = folder / 'evidence.json'
        data = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
        job = folder.name
        checks = []
        if not result['transport_success']: checks.append('transport_failed')
        if not data: checks.append('structured_evidence_missing')
        if data.get('web_research_available') is not True: checks.append('live_web_research_not_attested')
        if not result['screenshots_complete']: checks.append('screenshot_evidence_missing')
        if data.get('pre_freeze_compliance') is not True: checks.append('sample_gate_compliance_not_attested')
        source_ids = {str(row.get('source_id')) for row in data.get('sources', []) if isinstance(row, dict)}
        for source in data.get('sources', []):
            if not isinstance(source, dict):
                checks.append('invalid_source_record')
                continue
            row = {**source, 'job_id': job, 'global_source_id': job + ':' + str(source.get('source_id')),
                'artifact': str(folder / 'response.md'), 'coordinator_verification': 'UNVERIFIED',
                'first_indexed_utc': datetime.now(timezone.utc).isoformat()}
            audited = checks_by_source.get(row['global_source_id'], [])
            if audited:
                row['coordinator_verification'] = [check['status'] for check in audited]
                row['coordinator_checks'] = audited
            if not re.match(r'^https?://', str(source.get('url', ''))):
                checks.append('invalid_source_url')
            if source.get('access_state') != 'read_full_page':
                row['usable_as_transaction_price'] = False
            sources.append(row)
        for claim in data.get('claims', []):
            if not isinstance(claim, dict): continue
            cited = [str(x) for x in claim.get('source_ids', [])]
            unresolved = [identifier for identifier in cited if identifier not in source_ids]
            claim_row = {**claim, 'job_id': job, 'global_claim_id': job + ':' + str(claim.get('claim_id')),
                'global_source_ids': [job + ':' + identifier for identifier in cited],
                'unresolved_source_ids': unresolved, 'coordinator_verification': 'UNVERIFIED',
                'artifact': str(folder / 'response.md')}
            audited_claim = checks_by_claim.get(claim_row['global_claim_id'], [])
            if audited_claim:
                claim_row['coordinator_verification'] = 'PARTIALLY_AUDITED_SEE_CAVEATS'
                claim_row['coordinator_checks'] = audited_claim
            claims.append(claim_row)
            if unresolved: checks.append('claim_references_missing_source')
        for candidate in data.get('sku_candidates', []):
            if not isinstance(candidate, dict): continue
            canonical = json.dumps(candidate, sort_keys=True, ensure_ascii=False)
            candidates.append({**candidate, 'job_id': job,
                'proposal_id': job + ':' + hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:12],
                'sample_status': 'PROPOSED_NOT_FROZEN', 'coordinator_verification': 'UNVERIFIED',
                'artifact': str(folder / 'response.md')})
        for gap in data.get('data_gaps', []):
            gaps.append({'job_id': job, 'gap': gap, 'artifact': str(folder / 'response.md')})
        reviews.append({**result, 'review_flags': sorted(set(checks)),
            'source_records': len(data.get('sources', [])),
            'claim_records': len(data.get('claims', [])),
            'candidate_records': len(data.get('sku_candidates', [])),
            'source_verification_complete': False})
    for name, rows in [('sources', sources), ('claims', claims), ('sku-candidates', candidates), ('data-gaps', gaps)]:
        with (HERE / (name + '.jsonl')).open('w', encoding='utf-8') as handle:
            for row in rows: handle.write(json.dumps(row, ensure_ascii=False) + '\n')
        rows_to_csv(HERE / (name + '.csv'), rows)
    (HERE / 'review-status.json').write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'reports': len(reviews), 'sources': len(sources), 'claims': len(claims),
        'proposed_candidates': len(candidates),
        'sources_with_coordinator_checks':sum(row['coordinator_verification'] != 'UNVERIFIED' for row in sources),
        'sample_frozen': (HERE / 'sample-freeze-v1.json').exists()}, ensure_ascii=False))

if __name__ == '__main__': main()
