"""Continue only C's archived own partial after its original request has stopped."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
JOB = 'W1-C-continuation01'

def prepare_ready():
    original = HERE / 'jobs' / 'W1-C'
    result = original / 'result.json'
    if not result.exists() or json.loads(result.read_text(encoding='utf-8')).get('transport_success'):
        return []
    diagnostics = json.loads((original/'diagnostics.json').read_text(encoding='utf-8'))
    if not diagnostics.get('diagnostics',{}).get('generation_stop_verified'):
        reconciliation = original/'server-reconciliation.json'
        if not reconciliation.exists() or json.loads(reconciliation.read_text(encoding='utf-8')).get('generation_inactive_reconciled') is not True:
            return []
    partials = list(original.glob('partial-observation-*.txt'))
    if not partials:
        return []
    partial = max(partials,key=lambda p:p.stat().st_size)
    folder = HERE / 'jobs' / JOB
    folder.mkdir(exist_ok=True)
    prompt_path = folder / 'prompt.txt'
    if not prompt_path.exists():
        original_prompt = (original/'prompt.txt').read_text(encoding='utf-8').replace('W1-C',JOB)
        prompt = original_prompt + '\n=== CONTINUATION OF ONLY YOUR OWN INDEPENDENT REPLICATE ===\n'
        prompt += ('The original C session did independent research and began its answer, but the UI '
            'stream remained incomplete and the original request reached its 30-minute timeout. '
            'That request has now stopped. No A/B peer results are provided. Below is the unedited '
            'partial from ONLY the original C, not a finished or verified report. Continue this '
            'same independent replicate, verify the most important primary numerical anchors '
            'through actual browsing and complete the report. Do not claim you re-read a source '
            'unless you actually did; sources known only from the own partial remain unverified. '
            'Do not research overseas specific-SKU prices or availability. Keep ALL 18 categories '
            'and all ten requested sections but keep prose approximately 2000 Chinese characters '
            'and append compact complete JSON. Missing metrics remain null. Do not repeat the '
            'entire partial verbatim. Finish a bounded approximately 12-minute investigation '
            'rather than expand source collection. job_id must be ' + JOB + '.\n')
        prompt += partial.read_text(encoding='utf-8') + '\n=== END OWN PARTIAL ===\n'
        prompt_path.write_text(prompt,encoding='utf-8')
        (folder/'continuation-input.json').write_text(json.dumps({'parent_replicate':'W1-C',
            'original_failed_request_preserved':True,'contains_peer_outputs':False,
            'partial_file':str(partial.relative_to(HERE)),
            'partial_sha256':hashlib.sha256(partial.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    return [JOB]

def assemble_ready():
    folder = HERE/'jobs'/JOB
    parent = HERE/'jobs'/'W1-C'
    if (parent/'assembled-result.json').exists():
        return
    result = folder/'result.json'
    if not result.exists() or not json.loads(result.read_text(encoding='utf-8')).get('transport_success'):
        return
    evidence = folder/'evidence.json'
    if not evidence.exists():
        return
    data = json.loads(evidence.read_text(encoding='utf-8'))
    if data.get('web_research_available') is not True or data.get('pre_freeze_compliance') is not True:
        return
    categories = {c.get('category_id') for c in data.get('categories',[]) if isinstance(c,dict)}
    if categories != {f'C{i:02d}' for i in range(1,19)}:
        return
    inputs = json.loads((folder/'continuation-input.json').read_text(encoding='utf-8'))
    partial = HERE/inputs['partial_file']
    if hashlib.sha256(partial.read_bytes()).hexdigest()!=inputs['partial_sha256']:
        raise ValueError('Own partial was changed')
    raw = (folder/'response.md').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    combined = ('This is ONE independent W1-C replicate, comprising its unedited incomplete original '
        'and a completed mg continuation using only that own partial. It is not two independent '
        'replicates. Original timeout, stalled UI observation and screenshots remain preserved. '
        'The partial is not a successful response or verified source.\n'
        '\n=== ORIGINAL INCOMPLETE OWN PARTIAL ===\n'+partial.read_text(encoding='utf-8')+
        '\n=== COMPLETED INDEPENDENT CONTINUATION; SHA256 '+digest+' ===\n'+raw.decode('utf-8')).encode('utf-8')
    with (parent/'assembled-response.md').open('xb') as h:h.write(combined)
    result_data={'job_id':'W1-C','transport_success':True,'status':'needs_review',
        'completion_mode':'continuation_of_archived_own_partial','expected_input_count':1,
        'completed_utc':datetime.now(timezone.utc).isoformat(),'original_attempt_success':False,
        'batch_inputs':[{'job_id':JOB,'response_sha256':digest}],
        'partial_inputs':[{'path':inputs['partial_file'],'sha256':inputs['partial_sha256']}],
        'category_ids':sorted(categories),'source_verification':'pending_mg_source_audit',
        'response_sha256':hashlib.sha256(combined).hexdigest()}
    with (parent/'assembled-result.json').open('x',encoding='utf-8') as h:json.dump(result_data,h,ensure_ascii=False,indent=2)
