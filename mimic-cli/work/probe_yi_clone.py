"""Explicit diagnostic target; leaves the production CLI aliases unchanged."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1313Z'
CLONE = 'yi-rca-no-stealth-20261006'
sys.path.insert(0, str(ROOT / 'cli'))
import mg
from runtime_memory_guard import ProbeMemoryTimeline


def main():
    global CLONE
    if len(sys.argv) > 1 and sys.argv[1] == 'capacity':
        CLONE = 'yi-rca-capacity-20261006'
    elif len(sys.argv) > 1 and sys.argv[1] == 'chrome154':
        CLONE = 'yi-rca-chrome154-20261006'
    elif len(sys.argv) > 1 and sys.argv[1] == 'auth-only':
        CLONE = 'yi-rca-auth-only-20261006'
    elif len(sys.argv) > 1 and sys.argv[1] == 'production':
        CLONE = 'yi-mimicgate-20261002'
    sys.stdout.reconfigure(encoding='utf-8')
    before = set(ROOT.joinpath('runs').glob('2026*'))
    configure = mg.configure_profile
    def configure_diagnostic(profile):
        configure(profile)
        mg.API = 'http://127.0.0.1:8652' if CLONE == 'yi-mimicgate-20261002' else 'http://127.0.0.1:8662'
        mg.CONTAINER = CLONE
    mg.configure_profile = configure_diagnostic
    started = datetime.now(timezone.utc).isoformat()
    with ProbeMemoryTimeline(CLONE) as memory:
        code = mg.main(['probe', 'cup'])
    created = set(ROOT.joinpath('runs').glob('2026*')) - before
    candidates = [p for p in created if (p / 'diagnostics.json').exists()]
    assert len(candidates) == 1
    run = candidates[0]
    record = json.loads((run / 'diagnostics.json').read_text(encoding='utf-8'))
    shot = record.get('diagnostics', {}).get('screenshot_evidence', {})
    request_id = record.get('diagnostics', {}).get('request_id')
    directory = shot.get('directory')
    evidence_complete = False
    if directory == '/app/state/probe-artifacts/' + str(request_id):
        dest = run / 'screenshots'
        dest.mkdir(exist_ok=True)
        result = subprocess.run(['docker', 'cp', CLONE + ':' + directory + '/.', str(dest)],
            capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        assert result.returncode == 0
        for item in shot.get('files', []):
            path = dest / item['filename']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
        evidence_complete = bool(shot.get('success') and len(shot.get('files', [])) == 2)
    result = {'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'condition': sys.argv[2] if len(sys.argv) > 2 else None,
              'memory': memory.summary(),
              'container': CLONE, 'run_path': str(run), 'exit_code': code,
              'assessment': record.get('probe_assessment'), 'screenshot_evidence': shot,
              'evidence_complete': evidence_complete}
    (OUT / ('clone-probe-' + run.name + '.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
