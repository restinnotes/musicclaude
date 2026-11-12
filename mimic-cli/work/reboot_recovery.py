"""Read-only post-reboot audit before resuming any browser generation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1625Z'
sys.path.insert(0, str(ROOT / 'work'))
import finish_yi_rca as finish

def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for name in ('yi-mimicgate-20261002', 'yi-rca-capacity-20261006'):
        container = json.loads(finish.docker('inspect', name))[0]
        volume = next(m['Name'] for m in container['Mounts'] if m['Destination'] == '/app/browser_data')
        code = "import sqlite3,json;db=sqlite3.connect('file:/forensic/Default/Cookies?mode=ro',uri=True);rows=db.execute(\"SELECT host_key,name,expires_utc FROM cookies WHERE host_key LIKE '%chatgpt.com'\").fetchall();print(json.dumps({'site_cookie_count':len(rows),'auth_cookie_count':sum(n.startswith('__Secure-next-auth.session-token') for h,n,e in rows),'temporary_cookie_count':sum(n.startswith(('conv_key_','history_off_')) for h,n,e in rows),'auth_expiries_chrome_epoch':[e for h,n,e in rows if n.startswith('__Secure-next-auth.session-token')]}))"
        if container['State']['Running']:
            metadata = json.loads(finish.docker('exec', name, '/opt/venv/bin/python', '-c',
                code.replace('/forensic/Default', '/app/browser_data/Default')))
        else:
            metadata = json.loads(finish.docker('run', '--rm', '--network', 'none', '--entrypoint',
                '/opt/venv/bin/python', '-v', volume + ':/forensic:ro', container['Image'], '-c', code))
        state = container['State']
        row = {'container': name, 'already_running': state['Running'], 'exit_code': state['ExitCode'], 'oom_killed': state['OOMKilled'],
            'started_at': state['StartedAt'], 'finished_at': state['FinishedAt'], **metadata}
        dest = OUT / name
        dest.mkdir(exist_ok=True)
        for file in ('yi-session-status.json', 'yi-session-observer.jsonl'):
            try:
                finish.docker('cp', name + ':/app/state/' + file, str(dest / file))
            except RuntimeError:
                pass
        rows.append(row)
    deployment = json.loads((ROOT / 'experiments/yi-rootcause/20261006T1313Z/production-final/deployment.json').read_text())
    matched = []
    for item in deployment['files']:
        name = item['file']
        file = OUT / 'production-source' / name
        file.parent.mkdir(parents=True, exist_ok=True)
        finish.docker('cp', 'yi-mimicgate-20261002:/app/src/' + name, str(file))
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        assert digest == item['sha256'], 'Deployed source changed during reboot: ' + name
        matched.append({'file': name, 'sha256': digest})
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'containers': rows,
        'production_deployment_verified': matched, 'profile_modified': False,
        'browser_started': False, 'real_request_sent': False}
    (OUT / 'reboot-audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
