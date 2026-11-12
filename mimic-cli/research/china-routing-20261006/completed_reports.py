"""Read original responses or a traceable bundle of completed domestic batches."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def resolved_folder(job, seen=None):
    seen=set() if seen is None else seen
    if job in seen:raise ValueError('Recovery resolution cycle')
    seen.add(job)
    folder=HERE/'jobs'/job
    resolution=folder/'completion-resolution.json'
    if not resolution.exists():return folder
    row=json.loads(resolution.read_text(encoding='utf-8'))
    replacement=row.get('replacement_job_id','')
    if not replacement.startswith(job+'-recovery') or '/' in replacement or '\\' in replacement:
        raise ValueError(job+' invalid recovery identity')
    replacement_folder=HERE/'jobs'/replacement
    if hashlib.sha256((replacement_folder/'prompt.txt').read_bytes()).hexdigest()!=row['replacement_prompt_sha256']:
        raise ValueError(job+' recovery prompt was changed')
    return resolved_folder(replacement,seen)

def completed_files(job):
    folder = resolved_folder(job)
    original = folder / 'result.json'
    if original.exists() and json.loads(original.read_text(encoding='utf-8')).get('transport_success'):
        if job.startswith('W'):
            evidence = folder / 'evidence.json'
            if not evidence.exists() or json.loads(evidence.read_text(encoding='utf-8')).get('web_research_available') is not True:
                raise ValueError(job + ' lacks a structured attestation of actual web research')
        return original, folder / 'response.md'
    result_path = folder / 'assembled-result.json'
    report_path = folder / 'assembled-response.md'
    if not result_path.exists() or not report_path.exists():
        raise ValueError(job + ' has no successful original or completed independent batch bundle')
    result = json.loads(result_path.read_text(encoding='utf-8'))
    if not result.get('transport_success') or len(result.get('batch_inputs', [])) != result.get('expected_input_count',6):
        raise ValueError(job + ' incomplete domestic bundle')
    if hashlib.sha256(report_path.read_bytes()).hexdigest() != result['response_sha256']:
        raise ValueError(job + ' assembled report hash mismatch')
    for row in result['batch_inputs']:
        batch = resolved_folder(row['job_id'])
        if hashlib.sha256((batch / 'response.md').read_bytes()).hexdigest() != row['response_sha256']:
            raise ValueError(row['job_id'] + ' original response hash mismatch')
    for row in result.get('partial_inputs',[]):
        if hashlib.sha256((HERE/row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(job + ' archived own partial hash mismatch')
    return result_path, report_path

def assemble_ready():
    plan_path = HERE / 'domestic-batch-plan.json'
    if not plan_path.exists():
        return []
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    amendment = HERE / 'domestic-batch-amendment-C.json'
    if amendment.exists():
        addition = json.loads(amendment.read_text(encoding='utf-8'))
        plan['jobs'] += addition['jobs']
        plan['replicates'] += addition['replicates']
    assembled = []
    for replicate in plan['replicates']:
        parent = 'W2-' + replicate
        folder = HERE / 'jobs' / parent
        if (folder / 'assembled-result.json').exists():
            completed_files(parent)
            continue
        batches = [j for j in plan['jobs'] if j.startswith(parent + '-batch')]
        if len(batches) != 6:
            continue
        inputs, reports, covered = [], [], set()
        valid = True
        for batch in batches:
            batch_folder = resolved_folder(batch)
            result_path = batch_folder / 'result.json'
            evidence_path = batch_folder / 'evidence.json'
            if not result_path.exists() or not evidence_path.exists():
                valid = False
                break
            result = json.loads(result_path.read_text(encoding='utf-8'))
            evidence = json.loads(evidence_path.read_text(encoding='utf-8'))
            if not result.get('transport_success') or evidence.get('pre_freeze_compliance') is not True:
                valid = False
                break
            category_ids = {r.get('category_id') for r in evidence.get('categories', [])}
            batch_number = int(batch[-2:])
            expected = {f'C{i:02d}' for i in range((batch_number-1)*3+1, batch_number*3+1)}
            if category_ids != expected or category_ids & covered:
                valid = False
                break
            covered.update(category_ids)
            report = (batch_folder / 'response.md').read_bytes()
            sha = hashlib.sha256(report).hexdigest()
            inputs.append({'job_id': batch, 'response_sha256': sha,
                           'screenshots_complete': result.get('screenshots_complete', False)})
            reports.append('\n\n=== UNEDITED DOMESTIC BATCH ' + batch + '; SHA256 ' + sha + ' ===\n'
                           + report.decode('utf-8'))
        if not valid or covered != {f'C{i:02d}' for i in range(1,19)}:
            continue
        report_bytes = ('This is a mechanical, untruncated bundle of six independently researched '
            'category batches for the SAME replicate. It is not an additional model synthesis. '
            'The original timed-out attempt remains preserved in result.json and diagnostics.json. '
            'No batch received peer results. All claims still require coordinator verification.\n'
            + ''.join(reports)).encode('utf-8')
        with (folder / 'assembled-response.md').open('xb') as handle:
            handle.write(report_bytes)
        result = {'job_id': parent, 'transport_success': True, 'status': 'needs_review',
            'completion_mode': 'six_category_batches', 'original_attempt_success': False,
            'batch_inputs': inputs, 'category_ids': sorted(covered),
            'response_sha256': hashlib.sha256(report_bytes).hexdigest(),
            'source_verification': 'pending_coordinator_review'}
        with (folder / 'assembled-result.json').open('x', encoding='utf-8') as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
        assembled.append(parent)
    return assembled

def assemble_post_ready():
    plan_path=HERE/'post-freeze-batch-plan.json'
    if not plan_path.exists():return []
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    assembled=[]
    for stream in plan['streams']:
        for replicate in plan['replicates']:
            parent=stream+'-'+replicate
            folder=HERE/'jobs'/parent
            if (folder/'assembled-result.json').exists():
                completed_files(parent)
                continue
            batches=[j for j in plan['jobs'] if j.startswith(parent+'-batch')]
            inputs,reports,covered=[],[],set()
            valid=True
            for batch in batches:
                bf=resolved_folder(batch)
                rp,ep=bf/'result.json',bf/'evidence.json'
                if not rp.exists() or not ep.exists():valid=False;break
                result=json.loads(rp.read_text(encoding='utf-8'))
                data=json.loads(ep.read_text(encoding='utf-8'))
                scope=json.loads((bf/'task-input.json').read_text(encoding='utf-8'))
                if not result.get('transport_success') or data.get('web_research_available') is not True:
                    valid=False;break
                if data.get('frozen_sample_sha256')!=plan['frozen_sample_sha256']:
                    valid=False;break
                rows=data.get('observations' if stream=='W3' else 'coverage',[])
                ids={x.get('sku_id') for x in rows if isinstance(x,dict)}
                if ids!=set(scope['assigned_sku_ids']) or ids&covered:
                    valid=False;break
                covered.update(ids)
                raw=(bf/'response.md').read_bytes();sha=hashlib.sha256(raw).hexdigest()
                inputs.append({'job_id':batch,'response_sha256':sha})
                reports.append('\n=== UNEDITED '+batch+'; SHA256 '+sha+' ===\n'+raw.decode('utf-8'))
            full=json.loads((HERE/'sample-freeze-v1.json').read_text(encoding='utf-8'))
            if not valid or len(batches)!=6 or covered!={s['sku_id'] for s in full['skus']}:continue
            raw=('ONE independent '+parent+' replicate, mechanically bundled from six disjoint '
                 'category batches. No peer results were supplied. All frozen SKU IDs are retained; '
                 'unobserved and blocked rows remain in the denominator. Original reports are untruncated.\n'
                 +''.join(reports)).encode('utf-8')
            with (folder/'assembled-response.md').open('xb') as h:h.write(raw)
            result={'job_id':parent,'transport_success':True,'status':'needs_review',
                'completion_mode':'six_disjoint_postfreeze_batches','expected_input_count':6,
                'batch_inputs':inputs,'frozen_sample_sha256':plan['frozen_sample_sha256'],
                'covered_sku_ids':sorted(covered),'response_sha256':hashlib.sha256(raw).hexdigest(),
                'source_verification':'pending_mg_source_audit'}
            with (folder/'assembled-result.json').open('x',encoding='utf-8') as h:json.dump(result,h,ensure_ascii=False,indent=2)
            assembled.append(parent)
    return assembled
