"""Auditable mg-only research coordinator. Each worker is a fresh browser session."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
MG_ROOT = HERE.parents[1]
ATTACHMENT = Path(r'C:\Users\zuoyi\.codex\attachments\cbc22c6a-c33d-4d78-b239-fd5eef159231\已粘贴的文本.txt')
sys.path.insert(0, str(MG_ROOT / 'cli'))
sys.path.insert(0, str(MG_ROOT / 'work'))
import mg
from runtime_memory_guard import snapshot

WORKSTREAMS = {
    'W1': 'US Demand Map', 'W2': 'China Domestic Market Map',
    'W3': 'Price Spread Audit', 'W4': 'Temu / AliExpress Coverage',
    'W5': 'Logistics / Superbuy Infrastructure', 'W6': 'Regulation / Structural Boundary',
    'W7': 'Competitive Landscape / Why Doesnt This Exist', 'W8': 'Thesis Falsification',
}

def utc():
    return datetime.now(timezone.utc).isoformat()

def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    # Windows readers can briefly open the old file without FILE_SHARE_DELETE.
    for attempt in range(30):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(0.1)

class AdoptedWorker:
    """Observe an original worker after coordinator restart without resubmitting."""
    def __init__(self, pid, expected_started):
        self.pid = pid
        self.expected_started = datetime.fromisoformat(expected_started).timestamp()
        self.returncode = None

    def poll(self):
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, self.pid)
        if not handle:
            self.returncode = -1
            return self.returncode
        try:
            creation, exited, system, user = (wintypes.FILETIME() for _ in range(4))
            if not kernel.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exited),
                                         ctypes.byref(system), ctypes.byref(user)):
                self.returncode = -1
                return self.returncode
            born = ((creation.dwHighDateTime << 32) | creation.dwLowDateTime) / 10**7 - 11644473600
            if abs(born - self.expected_started) > 10:
                self.returncode = -1  # A reused PID must not be mistaken for our worker.
                return self.returncode
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                self.returncode = -1
                return self.returncode
            self.returncode = None if code.value == 259 else code.value
            return self.returncode
        finally:
            kernel.CloseHandle(handle)

def event(kind, **fields):
    with (HERE / 'events.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps({'utc': utc(), 'event': kind, **fields}, ensure_ascii=False) + '\n')

def setup():
    brief = ATTACHMENT.read_text(encoding='utf-8-sig')
    (HERE / 'original-brief.txt').write_text(brief, encoding='utf-8')
    digest = hashlib.sha256(brief.encode('utf-8')).hexdigest()
    rows = []
    for stream, title in WORKSTREAMS.items():
        for replicate in 'ABC':
            identifier = stream + '-' + replicate
            folder = HERE / 'jobs' / identifier
            folder.mkdir(parents=True, exist_ok=True)
            assigned = (
                f'You are independent researcher {identifier}. Your ONLY assigned workstream is '
                f'{stream}: {title}. Other researchers cannot see this session and you must not '
                'assume any findings from them. The master brief below is shared protocol, not a request '
                'to execute other workstreams or to invent their outcomes.\n'
                'Use actual live web search and read the source pages. If your session cannot browse, '
                'say WEB RESEARCH UNAVAILABLE prominently; do not substitute memory for research. '
                'State your actual retrieval UTC timestamps and the newest available data dates. '
                'The research as-of date is 2026-10-06; do not fabricate future-dated publications. '
                'Do not claim access to a logged-in shopping account, quotations or paid datasets '
                'that you did not actually access. Sources that you cannot open must be marked '
                'UNVERIFIED or AUTHENTICATED DATA REQUIRED. Search snippets cannot establish '
                'transaction prices, model variants, seller IDs, or demand rankings.\n'
            )
            if stream in ('W1', 'W2'):
                assigned += (
                    '\nPRE-FREEZE STAGE: No research into specific-SKU overseas prices, availability, '
                    'coverage, import savings or selection using internationalized brand visibility. '
                    'W1 may examine aggregate US category demand and retail structure, never select '
                    'SKU candidates by overseas price. W2 must select solely from Chinese domestic '
                    'consumer evidence and cannot assert US obscurity before the freeze. Cover ALL '
                    '18 categories, including difficult/heavy products. Missing evidence stays missing. '
                    'No need to propose a startup or UI.\n'
                )
            if stream == 'W1':
                assigned += (
                    '\nFor all 18 categories, output category IDs C01..C18 in the brief order. '
                    'Separate US sales from global, online from all-channel, retail from wholesale; '
                    'keep years, currencies, category boundaries, overlap and proxy limitations explicit. '
                    'Provide a demand ranking only to the extent supported by comparable evidence. '
                    'Propose a reproducible demand-weighting method and uncertainty treatment, '
                    'rather than manufacture numeric weights for missing category GMV.\n'
                )
            if stream == 'W2':
                assigned += (
                    '\nFor each C01..C18, attempt three clearly specified domestic candidate variants: '
                    'two head candidates from domestic ranking/flagship sales evidence and one candidate '
                    'from strong domestic consumer/community purchasing evidence. These are proposed '
                    'slots, not a license to fill absent evidence. Provide exact brand/model/variant, '
                    'Chinese product URL/item ID/seller ID where observed, domestic head evidence, '
                    'source access state and date, and price-type distinctions. Rank evidence quality. '
                    'If a candidate is only provisional, explicitly mark PROVISIONAL; do not call '
                    'an undated review a verified bestseller. Do not exclude batteries, large goods, '
                    'voltage/firmware/compatibility difficulties; record feasibility flags separately. '
                    'Do not begin overseas comparisons. Include an executable, deterministic sampling '
                    'rule and exact manual data fields for authenticated-data gaps.\n'
                )
            assigned += (
                '\nWrite your report in Chinese, using the ten report sections in the brief. '
                'Aim for substantive, well-supported research; source count alone is not a quality measure. '
                'For every key finding give explicit source URLs, dates and opposing evidence. '
                'Do not hide URLs in citation-only labels; include the literal full URLs. '
                'After the report, append one valid JSON object in a ```json fence with schema '
                '{"job_id":"' + identifier + '","web_research_available":true,'
                '"sources":[{"source_id":"S01","url":"https://...","title":"...",'
                '"published_at":null,"retrieved_at":"UTC ISO time or null if unavailable",'
                '"source_type":"official|government|filing|secondary|community",'
                '"access_state":"read_full_page|snippet_only|blocked|login_required",'
                '"claims_supported":["C01"]}],'
                '"claims":[{"claim_id":"C01","claim":"...","classification":"FACT|INFERENCE|HYPOTHESIS",'
                '"source_ids":["S01"],"confidence":"high|medium|low","counterevidence":"..."}],'
                '"categories":[],"sku_candidates":[],"data_gaps":[],"pre_freeze_compliance":true}. '
                'Populate categories/sku_candidates with your actual tables as structured objects; '
                'keep missing numbers null. If browsing unavailable use false. Never invent retrieval times.\n'
                '\n=== FULL USER MASTER BRIEF (protocol, not prior evidence) ===\n' + brief
                + '\n=== END BRIEF ===\n'
                f'Remember: execute ONLY {identifier}, {title}. No overseas SKU checks before freeze '
                'for W1/W2. Begin your independent web research now.\n'
            )
            path = folder / 'prompt.txt'
            if not path.exists():
                path.write_text(assigned, encoding='utf-8')
            rows.append({'job_id': identifier, 'workstream': stream, 'title': title,
                         'prompt_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'stage': 'pre_freeze' if stream in ('W1', 'W2') else 'after_freeze',
                         'status': 'pending'})
    manifest = HERE / 'manifest.json'
    if not manifest.exists():
        write_json(manifest, {'created_utc': utc(), 'brief_sha256': digest,
            'model': 'gpt-5.6-sol', 'effort': 'xhigh', 'profile': 'yi',
            'container': mg.CONTAINER, 'research_jobs': rows,
            'judges': ['methodology', 'economic', 'bear', 'bull'], 'synthesizers': 1,
            'independence': 'no peer outputs included before each replicate reports',
            'sample_gate': 'W1/W2 complete -> coordinator source/model review -> human freeze review -> timestamp/hash/version -> W3/W4/W5',
            'exclusions': ['counterfeit', 'wrong target product type', 'variant entirely undefinable',
                           'nonphysical', 'clearly illegal/prohibited shipment'],
            'missing_overseas_sku_is_not_exclusion': True,
            'sources_require_coordinator_verification': True})
    print(str(manifest))

def worker(identifier):
    folder = HERE / 'jobs' / identifier
    if (folder / 'result.json').exists():
        return 0
    stream = identifier.split('-')[0]
    prompt = (folder / 'prompt.txt').read_text(encoding='utf-8')
    if stream in ('W3', 'W4', 'W5'):
        frozen = HERE / 'sample-freeze-v1.json'
        frozen_hash = HERE / 'sample-freeze-v1.sha256'
        if not frozen.exists() or not frozen_hash.exists():
            raise SystemExit('Sample gate is not satisfied; no mg request was sent')
        digest = hashlib.sha256(frozen.read_bytes()).hexdigest()
        if frozen_hash.read_text(encoding='utf-8').split()[0] != digest:
            raise SystemExit('Frozen sample hash mismatch; no mg request was sent')
        frozen_text = frozen.read_text(encoding='utf-8')
        scope_path = folder / 'task-input.json'
        if scope_path.exists():
            scope = json.loads(scope_path.read_text(encoding='utf-8'))
            full_sample = json.loads(frozen_text)
            if scope.get('frozen_sample_sha256') != digest:
                raise SystemExit('Scoped assignment frozen hash mismatch; no request sent')
            assigned = [s for s in full_sample['skus'] if s['category_id'] in scope['category_ids']]
            if [s['sku_id'] for s in assigned] != scope['assigned_sku_ids']:
                raise SystemExit('Scoped assignment changed the frozen subset; no request sent')
            frozen_text = json.dumps({'version':full_sample['version'], 'full_sample_sha256':digest,
                'full_sample_sku_count':len(full_sample['skus']), 'assigned_category_ids':scope['category_ids'],
                'skus':assigned, 'scope_policy':'This is a disjoint execution partition, not a different sample. Six batches cover the whole immutable denominator; unassigned SKUs are handled in other batches, not excluded.'},ensure_ascii=False)
        prompt += ('\n=== FROZEN DOMESTIC-FIRST SAMPLE; SHA256 ' + digest + ' ===\n'
            + frozen_text + '\nDo not remove or replace any frozen SKU. '
            'Keep missing, unobserved, inaccessible and proven unavailable distinct in your denominator. '
            'Report each frozen sku_id you could and could not evaluate, with exact reasons. '
            'For costs retain all component prices, currency, observation date, variant, weight/dimensions, '
            'shipping structure, tariff classification/source and quote assumptions. A/B/C statistics '
            'remain separate. Do not manufacture savings or tariff rates for missing components. '
            'Preserve all four shipment structures separately; explicitly state the comparison endpoint '
            'and treatment of US sales tax. Sources attested by the model still await coordinator review.\n')
        if stream == 'W5':
            prompt += ('\nBound this infrastructure investigation to about 15 minutes, concise ten '
                'sections and compact evidence JSON. Do not claim a negotiated B2B discount from '
                'a marketing promise or retail estimator. No purchases, contacts or account changes. '
                'Actual quotes require destination ZIP10001, weight/dimensions, batteries, date, '
                'route, all mandatory fees and tax assumptions; missing dimensions and rates stay '
                'missing. Explicitly preserve four structures, including commercial aggregation '
                'of 1000 separately fulfilled orders distinct from physical consolidation.\n')
    elif stream in ('W6', 'W7', 'W8'):
        prompt += ('\nSTRUCTURAL RESEARCH ONLY. This work does not select domestic candidates or '
            'compare specific-SKU overseas prices/availability/coverage. Do not conduct those checks '
            'before sample freeze. Investigate architecture-level rules, primary histories or '
            'testable falsification mechanisms for your assigned workstream. Preserve all requested '
            'subquestions but keep the ten report sections concise, approximately 2500 Chinese '
            'characters excluding evidence JSON. Do not expand into the other workstreams. '
            'Finish bounded web research within about 15 minutes; mark unresolved sources/data '
            'instead of repeatedly attempting blocked sources. No actual contacts, purchases or '
            'paid access. A missing page proves neither a factual claim nor a legal exemption.\n')
    (folder / 'submitted-prompt.txt').write_text(prompt, encoding='utf-8')
    # Persistent one-shot claim prevents a crashed coordinator from silently resending.
    claim = folder / 'submission.claim'
    try:
        with claim.open('x', encoding='utf-8') as handle:
            handle.write(json.dumps({'claimed_utc': utc(), 'pid': __import__('os').getpid()}))
    except FileExistsError:
        raise SystemExit('This job already has a submission claim; inspect its original browser request before any retry')
    record = {'job_id': identifier, 'timestamp': utc(), 'profile': 'yi',
        'command': 'research', 'requested_model': mg.MODEL, 'requested_reasoning_effort': mg.EFFORT,
        'prompt_sha256': hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
        'success': False, 'response': '', 'diagnostics': {}}
    # Reuse mg's existing UI transport and evidence capture; do not modify its runtime.
    original_http = mg.http_json
    def captured_http(path, *args, **kwargs):
        if path == '/v1/chat/completions':
            kwargs['capture_probe'] = True
            attachment_manifest = folder / 'attachments.json'
            if attachment_manifest.exists():
                from mg_attachment_transport import call as attachment_call
                manifest=json.loads(attachment_manifest.read_text(encoding='utf-8'))
                record['attachment_transport']='existing mg client, original browser, isolated request page, retained standard verification'
                return attachment_call(folder,prompt,manifest['files'],mg,args[0] if args else kwargs.get('token',''))
        return original_http(path, *args, **kwargs)
    mg.http_json = captured_http
    started = time.monotonic()
    write_json(folder / 'running.json', {'started_utc': utc(), 'pid': __import__('os').getpid()})
    try:
        answer = mg.standard_call(prompt, record)
        record['success'] = True
        (folder / 'response.md').write_text(answer, encoding='utf-8')
    except mg.CLIError as error:
        record['error'] = {'type': error.kind, 'message': str(error)}
        if error.diagnostics:
            record['diagnostics'] = error.diagnostics
    except Exception as error:
        record['error'] = {'type': type(error).__name__, 'message': 'Research worker failed; no automatic resend'}
    finally:
        if record.get('diagnostics', {}).get('request_id'):
            record['local_screenshot_evidence'] = mg.save_probe_screenshots(record, folder)
        record['elapsed_seconds'] = round(time.monotonic() - started, 3)
        write_json(folder / 'diagnostics.json', record)
        answer = record.get('response', '')
        if answer and not (folder / 'response.md').exists():
            (folder / 'response.md').write_text(answer, encoding='utf-8')
        urls = sorted(set(re.findall(r'https?://[^\s<>\]\)"`]+', answer)))
        data = None
        for block in re.findall(r'```json\s*([\s\S]*?)```', answer):
            try:
                parsed = json.loads(block)
                if isinstance(parsed, dict) and parsed.get('job_id') == identifier:
                    data = parsed
            except ValueError:
                pass
        if data is not None:
            write_json(folder / 'evidence.json', data)
        write_json(folder / 'urls.json', urls)
        result = {'job_id': identifier, 'completed_utc': utc(), 'transport_success': record['success'],
            'elapsed_seconds': record['elapsed_seconds'], 'urls_count': len(urls),
            'structured_evidence': data is not None,
            'web_research_available_claim': data.get('web_research_available') if data else None,
            'source_verification': 'pending_coordinator_review',
            'status': 'needs_review' if record['success'] else 'failed',
            'screenshots_complete': record.get('local_screenshot_evidence', {}).get('complete', False),
            'error': record.get('error')}
        write_json(folder / 'result.json', result)
    return 0 if record['success'] else 1

def run_stage(stage):
    # No peer outputs are provided to a replicate within its research stage.
    if stage == 'pre-freeze':
        jobs = ['W1-A', 'W2-A', 'W1-B', 'W2-B', 'W1-C', 'W2-C']
    elif stage == 'domestic-batches':
        plan = json.loads((HERE / 'domestic-batch-plan.json').read_text(encoding='utf-8'))
        jobs = plan['jobs']
        amendment = HERE / 'domestic-batch-amendment-C.json'
        if amendment.exists():
            jobs += json.loads(amendment.read_text(encoding='utf-8'))['jobs']
    elif stage == 'structural':
        jobs = [stream + '-' + replicate for replicate in 'ABC' for stream in ('W6', 'W7', 'W8')]
    elif stage == 'mg-audits':
        from prepare_mg_audits import prepare_ready
        jobs = prepare_ready()
    elif stage == 'initial-and-audits':
        plan = json.loads((HERE / 'domestic-batch-plan.json').read_text(encoding='utf-8'))
        jobs = list(plan['jobs']) + [s + '-' + r for r in 'ABC' for s in ('W6','W7','W8')]
        amendment = HERE / 'domestic-batch-amendment-C.json'
        if amendment.exists():
            jobs += json.loads(amendment.read_text(encoding='utf-8'))['jobs']
        from prepare_mg_audits import prepare_ready
        jobs += prepare_ready()
        from prepare_w1_continuation import prepare_ready as prepare_continuation
        jobs += prepare_continuation()
        from prepare_domestic_audit_recovery import register_ready as register_audit_recovery
        jobs += [j for j in register_audit_recovery() if j not in jobs]
        for recovery in (HERE/'jobs').glob('*/completion-resolution.json'):
            replacement=json.loads(recovery.read_text(encoding='utf-8'))['replacement_job_id']
            if not replacement.endswith('-recovery-bundle') and replacement not in jobs:jobs.append(replacement)
    elif stage == 'post-freeze-batches':
        plan = json.loads((HERE / 'post-freeze-batch-plan.json').read_text(encoding='utf-8'))
        jobs = list(plan['jobs'])
        from prepare_mg_audits import prepare_ready
        jobs += [j for j in prepare_ready() if j.startswith(('R3-','R4-')) or j=='R-W5-sources']
        for recovery in (HERE/'jobs').glob('W[345]-*/completion-resolution.json'):
            replacement=json.loads(recovery.read_text(encoding='utf-8'))['replacement_job_id']
            if not replacement.endswith('-recovery-bundle') and replacement not in jobs:jobs.append(replacement)
    elif stage == 'post-freeze':
        if not (HERE / 'sample-freeze-v1.json').exists():
            raise SystemExit('No reviewed frozen sample; post-freeze stage cannot run')
        jobs = [stream + '-' + replicate for replicate in 'ABC' for stream in list(WORKSTREAMS)[2:]]
    elif stage == 'judges':
        if not (HERE / 'judge-evidence-pack.json').exists():
            raise SystemExit('Raw evidence and coordinator source audit pack is not ready')
        jobs = ['J1-methodology', 'J2-economic', 'J3-bear', 'J4-bull']
        if any(not (HERE / 'jobs' / j / 'prompt.txt').exists() for j in jobs):
            raise SystemExit('Four independent judge prompts have not been prepared')
    elif stage == 'synthesis':
        jobs = ['S1-final']
        if not (HERE / 'jobs' / jobs[0] / 'prompt.txt').exists():
            raise SystemExit('All 24 raw reports and four judges must first be assembled')
    elif stage == 'final-quality-audit':
        jobs=['Q-final-completeness']
        if not (HERE/'jobs'/jobs[0]/'prompt.txt').exists():
            raise SystemExit('Final mg report must exist before quality audit')
    else:
        raise SystemExit('Unknown research stage')
    if stage in ('judges','synthesis','final-quality-audit'):
        from completed_reports import resolved_folder
        jobs=[resolved_folder(j).name for j in jobs]
    dedicated = stage in ('domestic-batches', 'structural', 'mg-audits', 'initial-and-audits','post-freeze-batches')
    lock = HERE / ('coordinator-' + stage + '.lock' if dedicated else 'coordinator.lock')
    status_path = HERE / (stage + '-status.json' if dedicated else 'status.json')
    if stage == 'domestic-batches':
        status_path = HERE / 'domestic-batch-status.json'
    import os
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit('Coordinator already has a lock; inspect PID before resuming')
    with os.fdopen(descriptor, 'w') as handle:
        handle.write(str(os.getpid()))
    active = {}
    last_launch = time.monotonic()  # Resume conservatively preserves submission spacing.
    last_heartbeat = 0.0
    token = mg.read_auth()
    try:
        for identifier in jobs:
            folder = HERE / 'jobs' / identifier
            running = folder / 'running.json'
            if (folder / 'result.json').exists() or not running.exists():
                continue
            original = json.loads(running.read_text(encoding='utf-8'))
            claim = folder / 'submission.claim'
            if not claim.exists():
                with claim.open('x', encoding='utf-8') as handle:
                    handle.write(json.dumps({'claimed_utc': original['started_utc'], 'pid': original['pid'],
                        'recovered_from_original_running_record': True}))
            adopted = AdoptedWorker(original['pid'], original['started_utc'])
            if adopted.poll() is None:
                active[identifier] = adopted
                event('original_worker_adopted', job_id=identifier, pid=original['pid'], no_resend=True)
            else:
                event('original_submission_needs_reconciliation', job_id=identifier, no_resend=True)
        while True:
            if stage == 'initial-and-audits':
                from prepare_domestic_audit_recovery import register_ready as register_audit_recovery, assemble_ready as assemble_audit_recovery
                for recovery_job in register_audit_recovery():
                    if recovery_job not in jobs:jobs.append(recovery_job)
                assemble_audit_recovery()
                from prepare_w1_continuation import prepare_ready as prepare_continuation, assemble_ready as assemble_continuation
                assemble_continuation()
                for continuation in prepare_continuation():
                    if continuation not in jobs:
                        jobs.insert(0,continuation)
            if stage in ('mg-audits','initial-and-audits','post-freeze-batches'):
                from prepare_mg_audits import prepare_ready
                for audit in prepare_ready():
                    if stage=='initial-and-audits' and not (audit.startswith(('R1-','R2-')) or audit in ('R-W6-sources','R-W7-sources','R-W8-sources')):continue
                    if stage=='post-freeze-batches' and not (audit.startswith(('R3-','R4-')) or audit=='R-W5-sources'):continue
                    if audit not in jobs:
                        jobs.append(audit)
            if stage in ('domestic-batches','initial-and-audits'):
                # A scoped replacement is only allowed after the original C has
                # returned a terminal failure and its generation stop was verified.
                original_c = HERE / 'jobs' / 'W2-C' / 'result.json'
                if original_c.exists() and not json.loads(original_c.read_text(encoding='utf-8')).get('transport_success'):
                    amendment = HERE / 'domestic-batch-amendment-C.json'
                    if amendment.exists():
                        amended_jobs = json.loads(amendment.read_text(encoding='utf-8'))['jobs']
                    else:
                        from prepare_domestic_batches import prepare
                        amended_jobs = prepare('C', amendment=True)
                    for amended_job in amended_jobs:
                        if amended_job not in jobs:
                            jobs.append(amended_job)
                            event('scoped_domestic_job_registered', job_id=amended_job,
                                  original_failure_preserved=True, not_a_resend=True)
            for identifier, process in list(active.items()):
                if process.poll() is not None:
                    event('worker_finished', job_id=identifier, exit_code=process.returncode)
                    active.pop(identifier)
            pending = [j for j in jobs if j not in active and not (HERE / 'jobs' / j / 'result.json').exists()
                       and not (HERE / 'jobs' / j / 'submission.claim').exists()]
            if stage == 'initial-and-audits':
                def dependency_priority(j):
                    if j.startswith('W1-C-continuation'): return (0,0,j)
                    if j.startswith('R2-'): return (1,0,j)
                    if j.startswith('W2-') and '-batch' in j:
                        # Complete A/B/C for one category group before moving
                        # farther, so an independent mg sample audit can begin.
                        return (2,int(j.rsplit('batch',1)[1].split('-',1)[0]),j)
                    if j.startswith('R1-'): return (3,0,j)
                    return (4,0,j)
                pending.sort(key=dependency_priority)
            if stage=='post-freeze-batches':
                pending.sort(key=lambda j:(0 if '-recovery' in j else 1 if j.startswith(('R3-','R4-','R-W5-')) else 2 if j.startswith('W5-') else 3,j))
            memory = snapshot()
            try:
                _, state = mg.http_json('/v1/mimic-cli/concurrency', token, timeout=10)
            except mg.CLIError as error:
                event('gateway_poll_failed', error_type=error.kind, memory=memory)
                time.sleep(10)
                continue
            # Capacity is eight, but launch ramp reserves physical RAM for the user's apps.
            free_physical = memory['available_physical_gib']
            # Respect other clients using the same gateway. Ramp up one request
            # at a time only when physical memory supports the extra browser work.
            shared_ceiling = 8 if free_physical >= 5.0 else 6 if free_physical >= 4.0 else 4
            shared_ceiling = min(shared_ceiling, state.get('max_concurrency', 8))
            own_ceiling = (6 if free_physical >= 6.5 else 4) if dedicated else 6
            if stage in ('judges','synthesis','final-quality-audit'):
                own_ceiling=1
                shared_ceiling=1
            # Closed-evidence review uses one existing-browser tab with no web
            # research fanout. Keep a larger commit reserve and serialize it;
            # the research stages retain the original physical-memory floor.
            closed_review=stage in ('judges','synthesis','final-quality-audit')
            can_launch = (memory['available_physical_gib'] >= (1.5 if closed_review else 3.0)
                and memory['available_commit_gib'] >= (8.0 if closed_review else 6.0)
                and len(active) < own_ceiling
                and state.get('in_flight', 8) < shared_ceiling and state.get('waiting', 1) == 0
                and time.monotonic() - last_launch >= 45)
            if pending and can_launch:
                identifier = pending[0]
                folder = HERE / 'jobs' / identifier
                with (folder / 'worker.stdout.log').open('a', encoding='utf-8') as out, \
                     (folder / 'worker.stderr.log').open('a', encoding='utf-8') as err:
                    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'worker', identifier],
                        cwd=str(HERE), stdout=out, stderr=err, creationflags=subprocess.CREATE_NO_WINDOW)
                active[identifier] = process
                last_launch = time.monotonic()
                pending = [j for j in pending if j != identifier]
                event('worker_launched', job_id=identifier, pid=process.pid, memory=memory,
                      gateway_in_flight=state['in_flight'])
            if time.monotonic() - last_heartbeat >= 15:
                if stage in ('domestic-batches','initial-and-audits'):
                    from completed_reports import assemble_ready
                    for assembled in assemble_ready():
                        event('independent_domestic_replicate_bundled', job_id=assembled,
                              original_failure_preserved=True, no_peer_evidence=True)
                if stage == 'post-freeze-batches':
                    from completed_reports import assemble_post_ready
                    for assembled in assemble_post_ready():
                        event('independent_postfreeze_replicate_bundled', job_id=assembled,
                              immutable_sample=True, no_peer_evidence=True)
                status = {'utc': utc(), 'stage': stage, 'active': list(active), 'pending': pending,
                    'results': {j: json.loads((HERE / 'jobs' / j / 'result.json').read_text(encoding='utf-8'))
                        for j in jobs if (HERE / 'jobs' / j / 'result.json').exists()},
                    'memory': memory, 'gateway_concurrency': state,
                    'next_gate': {'pre-freeze': 'source review and human review of concrete domestic SKU sample',
                        'domestic-batches': 'all six category batches per independent replicate, then source review',
                        'structural': 'primary-source architecture and falsification audit; no SKU checks before freeze',
                        'mg-audits': 'mg source verification before evidence adjudication',
                        'initial-and-audits': 'mg domestic-source audits and immutable domestic sample freeze',
                        'post-freeze-batches': 'all pricing/coverage batches and mg audits, then four independent judges',
                        'post-freeze': 'source/claim adjudication before independent judges',
                        'judges': 'all four independent judges before synthesis',
                        'synthesis': 'mg final deliverable quality audit',
                        'final-quality-audit': 'deliver only after mg acceptance and artifact completeness checks'}[stage],
                    'scheduler': 'hidden local Python; no Codex scheduled task; no automatic resend'}
                write_json(status_path, status)
                event('heartbeat', active=list(active), pending=pending, memory=memory)
                last_heartbeat = time.monotonic()
            if not pending and not active:
                if stage in ('mg-audits','initial-and-audits'):
                    audit_streams = ('W6','W7','W8') if stage == 'initial-and-audits' else ('W5','W6','W7','W8')
                    required_audits = ['R1-W1-' + r for r in 'ABC'] + [f'R2-domestic-batch{i:02d}' for i in range(1,7)] + ['R-' + s + '-sources' for s in audit_streams]
                    if any(not (HERE/'jobs'/j/'result.json').exists() for j in required_audits):
                        time.sleep(5)
                        continue
                if stage == 'post-freeze-batches':
                    required_audits = [f'R{number}-batch{i:02d}' for number in (3,4) for i in range(1,7)] + ['R-W5-sources']
                    if any(not (HERE/'jobs'/j/'result.json').exists() for j in required_audits):
                        time.sleep(5)
                        continue
                unresolved = [j for j in jobs if not (HERE / 'jobs' / j / 'result.json').exists()]
                review = subprocess.run([sys.executable, str(HERE / 'review.py')], capture_output=True,
                    text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
                status.update(stage='needs_submission_reconciliation' if unresolved else 'awaiting_coordinator_review',
                    active=[], pending=[], unresolved_submissions=unresolved,
                    indexer_exit_code=review.returncode, finished_utc=utc())
                write_json(status_path, status)
                event('research_stage_finished', research_stage=stage,
                    next_gate='source review and sample freeze' if stage == 'pre-freeze' else 'evidence adjudication and four judges',
                    unresolved=unresolved)
                break
            time.sleep(5)
    finally:
        lock.unlink(missing_ok=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['setup', 'pre-freeze', 'domestic-batches', 'structural', 'mg-audits', 'initial-and-audits', 'post-freeze-batches', 'post-freeze', 'judges', 'synthesis', 'final-quality-audit', 'worker', 'status'])
    parser.add_argument('job_id', nargs='?')
    args = parser.parse_args()
    if args.command == 'setup': setup()
    elif args.command in ('pre-freeze', 'domestic-batches', 'structural', 'mg-audits', 'initial-and-audits', 'post-freeze-batches','post-freeze', 'judges', 'synthesis','final-quality-audit'): run_stage(args.command)
    elif args.command == 'worker': raise SystemExit(worker(args.job_id))
    else: print((HERE / 'status.json').read_text(encoding='utf-8'))
