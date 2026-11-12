"""One authorized real Windows background probe, with memory and screenshot evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from runtime_memory_guard import ProbeMemoryTimeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1625Z'
WRAPPERS = ROOT / 'experiments/yi-rootcause/20261006T1313Z'
CONTAINER = 'yi-mimicgate-20261002'

def main():
    before = set((ROOT / 'runs').glob('2026*'))
    started = datetime.now(timezone.utc).isoformat()
    with ProbeMemoryTimeline(CONTAINER) as memory:
        result = subprocess.run(['powershell.exe','-NoProfile','-NonInteractive',
            '-WindowStyle','Hidden','-ExecutionPolicy','Bypass','-File',
            str(ROOT / 'scripts/cup_scheduler.ps1')],cwd=ROOT,capture_output=True,
            timeout=2500,creationflags=subprocess.CREATE_NO_WINDOW)
    created = set((ROOT / 'runs').glob('2026*')) - before
    candidates = [p for p in created if (p / 'diagnostics.json').exists()]
    if len(candidates) != 1:
        record = {'utc':datetime.now(timezone.utc).isoformat(),
            'worker_exit_code':result.returncode,'new_run_count':len(candidates),
            'memory':memory.summary(),'diagnostic_not_submitted':len(candidates)==0}
        (OUT / 'windows-worker-no-run.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        print(json.dumps(record))
        return 1
    run = candidates[0]
    diagnostic = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
    screenshot = diagnostic.get('diagnostics',{}).get('screenshot_evidence',{})
    evidence_complete = bool(screenshot.get('success') and len(screenshot.get('files',[]))==2)
    for item in screenshot.get('files',[]):
        filename = item['filename']
        assert Path(filename).name == filename
        local = run / 'screenshots' / filename
        if not local.exists() or hashlib.sha256(local.read_bytes()).hexdigest() != item['sha256']:
            evidence_complete = False
    record = {'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
        'condition':'original yi production after graceful Docker restart; no cookie reimport; Windows hidden cup worker',
        'container':CONTAINER,'run_path':str(run),'exit_code':result.returncode,
        'assessment':diagnostic.get('probe_assessment'),'memory':memory.summary(),
        'screenshot_evidence':screenshot,'evidence_complete':evidence_complete,
        'worker_create_no_window':True,'worker_window_style':'Hidden',
        'container_automatically_started_by_worker':False}
    (WRAPPERS / ('clone-probe-' + run.name + '.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
    (OUT / 'windows-worker-validation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record))
    return 0 if result.returncode==0 and evidence_complete and diagnostic.get('success') else 1

if __name__ == '__main__':
    sys.exit(main())
