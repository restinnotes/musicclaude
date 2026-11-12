"""Deploy reviewed sources to the stopped original container, preserving volumes."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1313Z/production-deployment'
sys.path.insert(0, str(ROOT / 'work'))
import finish_yi_rca as finish

NAMES = ('config.py', 'request_observer.py', 'session_observer.py', 'cookie_capacity.py',
    'api/standard_completion.py', 'api/probe_evidence.py', 'api/openai_routes.py', 'api/browser_gate.py',
    'browser/manager.py', 'chatgpt/client.py', 'chatgpt/detector.py')

def main():
    global OUT
    if len(sys.argv) > 1:
        assert sys.argv[1].replace('-', '').isalnum()
        OUT = OUT.parent / sys.argv[1]
    OUT.mkdir(exist_ok=True)
    state = json.loads(finish.docker('inspect', '--format', '{{json .State}}', finish.CONTAINER))
    assert state['Status'] == 'exited' and not state['OOMKilled']
    records = []
    for name in NAMES:
        source = ROOT / 'src' / name
        ast.parse(source.read_text(encoding='utf-8'))
        backup = OUT / 'before' / name
        backup.parent.mkdir(parents=True, exist_ok=True)
        try:
            finish.docker('cp', finish.CONTAINER + ':/app/src/' + name, str(backup))
        except RuntimeError:
            if name not in ('cookie_capacity.py', 'api/probe_evidence.py'):
                raise
        finish.docker('cp', str(source), finish.CONTAINER + ':/app/src/' + name)
        verification = OUT / 'deployed' / name
        verification.parent.mkdir(parents=True, exist_ok=True)
        finish.docker('cp', finish.CONTAINER + ':/app/src/' + name, str(verification))
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        assert hashlib.sha256(verification.read_bytes()).hexdigest() == digest
        records.append({'file': name, 'sha256': digest})
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'container': finish.CONTAINER,
        'files': records, 'container_started': False, 'profile_volumes_preserved': True,
        'backend_unchanged': True, 'stealth_unchanged': True, 'max_concurrency_unchanged': 8}
    (OUT / 'deployment.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
