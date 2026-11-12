"""Mechanical provenance and denominator checks; does not invent estimates or prices."""
import csv
import hashlib
import json
from pathlib import Path
from completed_reports import resolved_folder

HERE=Path(__file__).resolve().parent

def build():
    frozen=json.loads((HERE/'sample-freeze-v1.json').read_text(encoding='utf-8'))
    sha=hashlib.sha256((HERE/'sample-freeze-v1.json').read_bytes()).hexdigest()
    population={s['sku_id']:s for s in frozen['skus']}
    observations=[]
    count_rows=[]
    for stream,number in [('W3',3),('W4',4)]:
        for replica in 'ABC':
            seen=set()
            for batch in range(1,7):
                job=f'{stream}-{replica}-batch{batch:02d}'
                folder=resolved_folder(job)
                result=json.loads((folder/'result.json').read_text(encoding='utf-8'))
                data=json.loads((folder/'evidence.json').read_text(encoding='utf-8'))
                scope=json.loads((folder/'task-input.json').read_text(encoding='utf-8'))
                if not result.get('transport_success') or data.get('frozen_sample_sha256')!=sha:
                    raise SystemExit(job+' is not completed on the immutable sample')
                rows=data.get('observations' if stream=='W3' else 'coverage',[])
                actual=[row.get('sku_id') for row in rows]
                if len(actual)!=len(set(actual)) or set(actual)!=set(scope['assigned_sku_ids']):
                    raise SystemExit(job+' changed its assigned denominator')
                audit_job=f'R{number}-batch{batch:02d}'
                audit_folder=resolved_folder(audit_job)
                audit_result=json.loads((audit_folder/'result.json').read_text(encoding='utf-8'))
                audit=json.loads((audit_folder/'evidence.json').read_text(encoding='utf-8'))
                if not audit_result.get('transport_success') or audit.get('review_performed') is not True:
                    raise SystemExit(audit_job+' not completed')
                for row in rows:
                    sku=row['sku_id']
                    if sku in seen:raise SystemExit(job+' repeats a frozen SKU from another batch')
                    seen.add(sku)
                    checks=[a for a in audit.get('observation_audits',[]) if resolved_folder(a.get('original_job_id')).name==resolved_folder(job).name and a.get('sku_id')==sku]
                    if len(checks)!=1:raise SystemExit(audit_job+' lacks a unique audit for '+job+':'+sku)
                    original=population[sku]
                    observations.append({'workstream':stream,'replicate':replica,'job_id':job,
                        'sku_id':sku,'category_id':original['category_id'],'sampling_stratum':original['sampling_stratum'],
                        'head_status_verified':original.get('head_status_verified',False),
                        'exact_variant_verified':original.get('exact_variant_verified',False),
                        'frozen_sample_sha256':sha,'raw_observation':row,'mg_source_audit':checks[0],
                        'mg_source_audit_job':audit_job,
                        'raw_response_sha256':hashlib.sha256((folder/'response.md').read_bytes()).hexdigest(),
                        'audit_response_sha256':hashlib.sha256((audit_folder/'response.md').read_bytes()).hexdigest(),
                        'statistical_policy':'One row per frozen SKU per independent replicate; never pool repeats as independent SKU draws. Audit flags and missingness constrain valid descriptive statistics. No arbitrary category weights.'})
            if seen!=set(population):raise SystemExit(stream+'-'+replica+' failed full-sample denominator check')
            relevant=[x for x in observations if x['workstream']==stream and x['replicate']==replica]
            count_rows.append({'workstream':stream,'replicate':replica,'frozen_denominator':len(population),
                'observed_or_missing_rows':len(relevant),
                'mg_audited_exact_price_comparison_count':sum(x['mg_source_audit'].get('usable_exact_price_comparison') is True for x in relevant),
                'mg_audited_verified_landed_savings_count':sum(x['mg_source_audit'].get('usable_verified_landed_savings') is True for x in relevant),
                'mg_audited_exact_coverage_observation_count':sum(x['mg_source_audit'].get('usable_exact_coverage_observation') is True for x in relevant),
                'demand_weighted_population_estimate':None,
                'unweighted_descriptive_distribution':'Requires actual compatible audited numeric observations; sample is not probability-based'})
    with (HERE/'audited-sku-observations.jsonl').open('w',encoding='utf-8') as h:
        for row in observations:h.write(json.dumps(row,ensure_ascii=False)+'\n')
    (HERE/'audited-denominator-checks.json').write_text(json.dumps(count_rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (HERE/'audited-denominator-checks.csv').open('w',encoding='utf-8-sig',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(count_rows[0]));writer.writeheader();writer.writerows(count_rows)
    print(json.dumps({'frozen_skus':len(population),'audited_observation_rows':len(observations),'six_independent_replicate_denominators_checked':True}))

if __name__=='__main__':build()
