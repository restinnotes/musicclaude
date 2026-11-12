"""Persistent hidden sequential pipeline; every transition requires real completed artifacts."""
import json
import re
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent

def now():return datetime.now(timezone.utc).isoformat()

def status(stage,**extra):
    from coordinator import write_json
    write_json(HERE/'pipeline-status.json',{'utc':now(),'stage':stage,
        'model':'gpt-5.6-sol','effort':'xhigh','research_and_audits':'mg',**extra})

def command(script,*args):
    result=subprocess.run([sys.executable,str(HERE/script),*args],cwd=str(HERE),
        capture_output=True,text=True,encoding='utf-8',errors='replace',
        creationflags=subprocess.CREATE_NO_WINDOW)
    with (HERE/'pipeline-commands.jsonl').open('a',encoding='utf-8') as handle:
        handle.write(json.dumps({'utc':now(),'script':script,'arguments':list(args),
            'exit_code':result.returncode,'stdout':result.stdout[-6000:],'stderr':result.stderr[-6000:]},ensure_ascii=False)+'\n')
    if result.returncode:
        status('needs_coordinator_repair',script=script,exit_code=result.returncode,
            stderr=result.stderr[-3000:],no_automatic_resend=True)
        raise RuntimeError(script+' failed; original results preserved')
    return result

def require_success(job):
    from completed_reports import completed_files
    completed_files(job)

def input_incomplete(text):
    # A completed judge can explicitly say "不标 INPUT_INCOMPLETE".
    # Treat a standalone status heading as failure, not a negated mention.
    return bool(re.search(r'(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?INPUT_INCOMPLETE(?:\*\*)?(?:\s|[。:：]|$)',text))

def initial_ready(domestic_only=False):
    initial=['W1-'+r for r in 'ABC']+['W2-'+r for r in 'ABC']+[s+'-'+r for s in ('W6','W7','W8') for r in 'ABC']
    if domestic_only:initial=[j for j in initial if j.startswith(('W1-','W2-'))]
    for job in initial:
        try:require_success(job)
        except ValueError:return False
    audits=['R1-W1-'+r for r in 'ABC']+[f'R2-domestic-batch{i:02d}' for i in range(1,7)]+['R-'+s+'-sources' for s in ('W6','W7','W8')]
    if domestic_only:audits=[j for j in audits if j.startswith(('R1-','R2-'))]
    for job in audits:
        from completed_reports import resolved_folder
        folder=resolved_folder(job)
        p=folder/'evidence.json';rp=folder/'result.json'
        if not p.exists() or not rp.exists():return False
        result=json.loads(rp.read_text(encoding='utf-8'));d=json.loads(p.read_text(encoding='utf-8'))
        if not result.get('transport_success') or d.get('review_performed') is not True or d.get('web_research_available') is not True:return False
    return True

def wait_initial(domestic_only=False):
    status('waiting_for_mg_initial_research_and_audits')
    while not initial_ready(domestic_only):
        lock=HERE/'coordinator-initial-and-audits.lock'
        if not lock.exists():
            status('initial_runner_stopped_before_required_reports',no_automatic_resend=True)
            raise RuntimeError('Initial runner stopped; coordinator reconciliation required')
        pid=int(lock.read_text(encoding='utf-8').strip())
        import ctypes
        from ctypes import wintypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x1000,False,pid)
        if not handle:
            status('initial_runner_process_missing',pid=pid,no_automatic_resend=True)
            raise RuntimeError('Initial owner is no longer running')
        kernel.CloseHandle(handle)
        status('waiting_for_mg_initial_research_and_audits',initial_owner_pid=pid)
        time.sleep(30)
    if not domestic_only:
        while (HERE/'coordinator-initial-and-audits.lock').exists():time.sleep(5)

def main():
    if not (HERE/'sample-freeze-v1.json').exists():
        wait_initial(domestic_only=True)
        status('compiling_mg_reviewed_domestic_sample')
        if not (HERE/'reviewed-domestic-sample-input.json').exists():command('build_reviewed_sample.py')
        command('freeze_sample.py',str(HERE/'reviewed-domestic-sample-input.json'),
            '--review-mode','delegated_coordinator','--approval-reference',
            'Human user instruction in this thread: 继续啊全部做完再叫我; delegated-completion-authorization.json')
    if not (HERE/'post-freeze-batch-plan.json').exists():command('prepare_postfreeze_batches.py')
    status('mg_postfreeze_research_and_source_audits')
    command('coordinator.py','post-freeze-batches')
    wait_initial()
    for n in range(1,9):
        for r in 'ABC':require_success(f'W{n}-{r}')
    status('compiling_complete_mg_evidence_for_independent_judges')
    if not (HERE/'judge-evidence-pack.json').exists():
        command('build_audited_observation_ledger.py')
        command('compile_mg_audit_pack.py')
        command('prepare_reviews.py','judges')
    status('four_independent_mg_judges_same_immutable_evidence')
    command('coordinator.py','judges')
    judge_ids=['J1-methodology','J2-economic','J3-bear','J4-bull']
    judge_manifest=json.loads((HERE/'judge-evidence-pack.json').read_text(encoding='utf-8'))
    for job in judge_ids:
        require_success(job)
        from completed_reports import completed_files
        text=completed_files(job)[1].read_text(encoding='utf-8')
        if input_incomplete(text):
            status('judge_reports_input_capacity_limitation',job_id=job,no_automatic_resend=True)
            raise RuntimeError('Judge cannot attest complete input inspection')
        missing=[row['job_id'] for row in judge_manifest['raw_reports']
                 if row['job_id'] not in text or row['response_sha256'] not in text]
        if missing:
            status('judge_completeness_table_missing_inputs',job_id=job,missing=missing,no_automatic_resend=True)
            raise RuntimeError('Judge omitted required report identities/hashes')
    status('mg_final_synthesis')
    if not (HERE/'jobs'/'S1-final'/'prompt.txt').exists():command('prepare_reviews.py','synthesis')
    command('coordinator.py','synthesis')
    require_success('S1-final')
    from completed_reports import completed_files
    text=completed_files('S1-final')[1].read_text(encoding='utf-8')
    if input_incomplete(text):
        status('synthesis_reports_input_capacity_limitation',no_automatic_resend=True)
        raise RuntimeError('Synthesis cannot attest complete input inspection')
    # A final answer is a reviewable deliverable, not an automatic proof that all
    # task requirements are satisfied. Root checks completeness before notifying.
    (HERE/'FINAL_RESEARCH_REPORT.txt').write_text(text,encoding='utf-8')
    status('mg_final_deliverable_quality_audit')
    if not (HERE/'jobs'/'Q-final-completeness'/'prompt.txt').exists():command('prepare_final_quality_audit.py')
    command('coordinator.py','final-quality-audit')
    require_success('Q-final-completeness')
    from completed_reports import resolved_folder
    qa_path=resolved_folder('Q-final-completeness')/'evidence.json'
    if not qa_path.exists():raise RuntimeError('Final mg audit lacks structured acceptance')
    qa=json.loads(qa_path.read_text(encoding='utf-8'))
    if qa.get('input_complete') is not True or qa.get('accepted') is not True:
        status('final_mg_audit_requires_material_repairs',audit=qa,no_automatic_resend=True)
        raise RuntimeError('Final mg quality audit did not accept the report')
    status('final_mg_report_ready_for_coordinator_acceptance',
        report=str(HERE/'FINAL_RESEARCH_REPORT.txt'),user_notified=False,
        not_claimed_complete_until_final_acceptance=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        with (HERE/'pipeline-errors.jsonl').open('a',encoding='utf-8') as h:
            h.write(json.dumps({'utc':now(),'error_type':type(error).__name__,'message':str(error),'no_automatic_resend':True},ensure_ascii=False)+'\n')
        raise
