"""Mechanically compile mg-reviewed choices; never look up overseas SKU information."""
import hashlib
import json
import unicodedata
from pathlib import Path
from datetime import datetime, timezone
from completed_reports import resolved_folder

HERE = Path(__file__).resolve().parent

def candidate_id(row):
    return row.get('candidate_sku_id') or row.get('sku_candidate_id') or row.get('候选sku_id') or row.get('sku_id')

def build():
    skus, exclusions, gaps, reviews = [], [], [], []
    for batch in range(1,7):
        job=f'R2-domestic-batch{batch:02d}'
        folder=resolved_folder(job)
        result_path=folder/'result.json'
        evidence_path=folder/'evidence.json'
        if not result_path.exists() or not evidence_path.exists():
            raise SystemExit(job+' mg audit has not finished')
        result=json.loads(result_path.read_text(encoding='utf-8'))
        evidence=json.loads(evidence_path.read_text(encoding='utf-8'))
        if not result.get('transport_success') or evidence.get('review_performed') is not True or evidence.get('pre_freeze_compliance') is not True:
            raise SystemExit(job+' is not a completed compliant mg source/model review')
        if evidence.get('web_research_available') is not True:
            raise SystemExit(job+' did not attest actual browsing')
        selections=evidence.get('recommended_selection')
        if not isinstance(selections,list):
            raise SystemExit(job+' has no explicit selection list')
        audits=evidence.get('candidate_audits',[])
        expected=set()
        for replica in 'ABC':
            original_job=f'W2-{replica}-batch{batch:02d}'
            original_evidence=json.loads((resolved_folder(original_job)/'evidence.json').read_text(encoding='utf-8'))
            expected.update((resolved_folder(original_job).name,candidate_id(c)) for c in original_evidence.get('sku_candidates',[]))
        covered=[(resolved_folder(a.get('original_job_id')).name,a.get('original_candidate_id')) for a in audits]
        if set(covered)!=expected or len(covered)!=len(set(covered)):raise SystemExit(job+' failed complete original-candidate audit coverage')
        cats={f'C{i:02d}' for i in range((batch-1)*3+1,batch*3+1)}
        counts={c:0 for c in cats}
        strata={c:{"domestic_head":0,"domestic_opportunity":0} for c in cats}
        unique_variants=set()
        for choice in selections:
            origin_id=choice.get('original_job_id')
            if not origin_id or not origin_id.startswith('W2-') or '/' in origin_id or '\\' in origin_id:
                raise SystemExit(job+' invalid candidate provenance')
            origin=json.loads((resolved_folder(origin_id)/'evidence.json').read_text(encoding='utf-8'))
            matches=[c for c in origin.get('sku_candidates',[]) if candidate_id(c)==choice.get('original_candidate_id')]
            if len(matches)!=1:
                raise SystemExit(job+' cannot uniquely resolve an original candidate; no substitute inferred')
            original=matches[0]
            cat=original.get('category_id')
            if cat not in cats or choice.get('category_id')!=cat:
                raise SystemExit(job+' selection category mismatch')
            if counts[cat]>=3:
                raise SystemExit(job+' exceeds the pre-registered per-category maximum')
            grade=choice.get('quality_grade')
            if grade in ('EXCLUDE_ALLOWED_REASON','UNVERIFIED_BLOCKED'):
                raise SystemExit(job+' selected an excluded or inaccessible candidate without model verification')
            audited=[a for a in audits if a.get('original_job_id')==origin_id and a.get('original_candidate_id')==choice.get('original_candidate_id')]
            if len(audited)!=1:
                raise SystemExit(job+' selection lacks a unique candidate audit')
            a=audited[0]
            if not a.get('model_exists_verified'):
                raise SystemExit(job+' selected a model that the mg audit has not verified exists')
            source_ids=choice.get('source_ids',[])
            sources=[s for s in evidence.get('sources',[]) if s.get('source_id') in source_ids]
            if not sources or not any(s.get('access_state')=='read_full_page' for s in sources):
                raise SystemExit(job+' selection lacks an actually read domestic source')
            stratum=choice.get('sampling_stratum')
            if stratum not in strata[cat]:raise SystemExit(job+' invalid sampling stratum')
            if strata[cat][stratum]>=(2 if stratum=='domestic_head' else 1):raise SystemExit(job+' exceeds pre-registered sampling stratum maximum')
            variant_key=(cat,)+tuple(unicodedata.normalize('NFKC',str(choice.get(k) or original.get(k) or '')).casefold().strip() for k in ('brand','model','exact_variant'))
            if variant_key in unique_variants:raise SystemExit(job+' duplicates an exact variant; mg reconciliation required')
            unique_variants.add(variant_key)
            strata[cat][stratum]+=1
            counts[cat]+=1
            row={**original,'sku_id':f'{cat}-S{counts[cat]:02d}',
                'brand':choice.get('brand') or original.get('brand'),
                'model':choice.get('model') or original.get('model'),
                'exact_variant':choice.get('exact_variant') or original.get('exact_variant'),
                'sampling_stratum':choice.get('sampling_stratum'),
                'domestic_evidence':{'original':original.get('domestic_evidence'),
                    'mg_audit_job':job,'mg_audit_grade':grade,'mg_audit_sources':sources,
                    'head_status_verified':bool(a.get('head_status_verified')),
                    'exact_variant_verified':bool(a.get('exact_variant_verified')),
                    'domestic_consumer_evidence_verified':bool(a.get('domestic_consumer_evidence_verified')),
                    'caveat':a.get('caveat')},
                'domestic_selection_rule':{'preregistration':'sampling-preregistration-v1.json',
                    'mg_selection_reason':choice.get('reason'),
                    'original_job_id':origin_id,'original_candidate_id':choice.get('original_candidate_id')},
                'mg_audit_grade':grade,'head_status_verified':bool(a.get('head_status_verified')),
                'exact_variant_verified':bool(a.get('exact_variant_verified')),
                'current_transaction_price_verified':False,
                'source_audit_job':job,'source_audit_response_sha256':hashlib.sha256((folder/'response.md').read_bytes()).hexdigest()}
            skus.append(row)
        exclusions.extend({'audit_job':job,'record':x} for x in evidence.get('exclusion_log',[]))
        gaps.extend({'audit_job':job,'record':x} for x in evidence.get('category_gaps',[]))
        gaps.extend({'category_id':c,'gap':'No verified mg-recommended candidate'} for c,n in counts.items() if n==0)
        reviews.append({'job_id':job,'response_sha256':hashlib.sha256((folder/'response.md').read_bytes()).hexdigest(),
            'review_performed':True,'category_counts':counts})
    payload={'skus':skus,'exclusion_log':exclusions,'category_gaps':gaps,
        'overseas_sku_research_before_freeze':False,'mg_domestic_audits':reviews,
        'verified_head_statistics_policy':'Only head_status_verified plus exact_variant_verified rows enter verified-head exact-SKU statistics; all other frozen rows remain in the denominator and separate provisional strata',
        'sampling_preregistration_sha256':hashlib.sha256((HERE/'sampling-preregistration-v1.json').read_bytes()).hexdigest()}
    path=HERE/'reviewed-domestic-sample-input.json'
    if path.exists():
        raise SystemExit('Concrete reviewed sample already exists; do not overwrite it')
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    review={'review_performed':True,'review_mode':'delegated_coordinator',
        'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
        'reviewed_input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'human_review_performed':False,
        'method':'Six independent mg domestic-source/model audits supply candidate reviews and choices; coordinator mechanically validates original-candidate provenance, actual read domestic sources, model-existence attestations and per-category counts. No overseas data inspected.',
        'source_model_reviews':reviews,'authority':'delegated-completion-authorization.json'}
    (HERE/'domestic-sample-coordinator-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'reviewed_sample':str(path),'sku_count':len(skus),'verified_head_count':sum(s['head_status_verified'] and s['exact_variant_verified'] for s in skus)}))

if __name__=='__main__':build()
