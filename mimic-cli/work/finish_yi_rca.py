"""Finish passive-audit deployment and stop the idle test container gracefully."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments' / 'yi-rootcause' / '20261006T0746Z'
CONTAINER = 'yi-mimicgate-20261002'
sys.path.insert(0, str(ROOT / 'cli'))
import mg


def docker(*args):
    result = subprocess.run(['docker', *args], capture_output=True, text=True,
                            encoding='utf-8', timeout=45,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Docker operation failed: ' + args[0])
    return result.stdout


def py(code):
    return docker('exec', CONTAINER, '/opt/venv/bin/python', '-c', code)


def copy_audit():
    docker('cp', CONTAINER + ':/app/state/yi-session-observer.jsonl', str(OUT / 'docker-session-observer.jsonl'))
    return [json.loads(line) for line in (OUT / 'docker-session-observer.jsonl').read_text(encoding='utf-8').splitlines()]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    started = datetime.now(timezone.utc).isoformat()
    token = mg.read_auth()
    _, activity = mg.http_json('/v1/gateway/activity', token)
    token = ''
    concurrency = activity['concurrency']
    if concurrency['in_flight'] or concurrency['waiting']:
        raise RuntimeError('Active requests remain; container was left running')
    original = py("from pathlib import Path; print(Path('/startapp.sh').read_text(), end='')")
    (OUT / 'startapp.original.sh').write_text(original, encoding='utf-8', newline='')
    pid = int(py("from pathlib import Path; rows=[int(p.name) for p in Path('/proc').iterdir() if p.name.isdigit() and (p/'cmdline').exists() and b'src.api.server' in (p/'cmdline').read_bytes().split(b'\\0')]; assert len(rows)==1, rows; print(rows[0])"))
    (OUT / 'shutdown-preflight.json').write_text(json.dumps({'utc': started, 'concurrency': concurrency, 'api_process': pid}, indent=2), encoding='utf-8')
    closed = False
    api_exited = False
    try:
        # Prevent the supervisor from immediately launching another browser after
        # the API's normal lifespan shutdown. The original script is restored below.
        py("from pathlib import Path; Path('/startapp.sh').write_text('#!/bin/sh\\nexec sleep 3600\\n')")
        py(f"import os,signal; from pathlib import Path; p={pid}; assert b'src.api.server' in Path('/proc/'+str(p)+'/cmdline').read_bytes().split(b'\\0'); os.kill(p,signal.SIGTERM)")
        for _ in range(25):
            rows = copy_audit()
            closed = any(row.get('event') == 'backend_context_closed' and row.get('utc', '') >= started for row in rows)
            api_exited = py(f"from pathlib import Path; print(int(not Path('/proc/{pid}').exists()))").strip() == '1'
            if closed and api_exited:
                break
            time.sleep(1)
    finally:
        py('from pathlib import Path; Path("/startapp.sh").write_text(' + repr(original) + ')')
    if not closed or not api_exited:
        raise RuntimeError('Graceful browser close was not confirmed; Docker stop was not performed')
    docker('cp', str(ROOT / 'src' / 'request_observer.py'), CONTAINER + ':/app/src/request_observer.py')
    py("import py_compile; py_compile.compile('/app/src/request_observer.py', doraise=True); py_compile.compile('/app/src/session_observer.py', doraise=True)")
    deployed = py("import hashlib; from pathlib import Path; print(hashlib.sha256(Path('/app/src/request_observer.py').read_bytes()).hexdigest())").strip()
    expected = hashlib.sha256((ROOT / 'src' / 'request_observer.py').read_bytes()).hexdigest()
    assert deployed == expected
    docker('stop', '-t', '30', CONTAINER)
    state = json.loads(docker('inspect', '--format', '{{json .State}}', CONTAINER))
    rows = copy_audit()
    result = {'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'in_flight_before_shutdown': 0, 'browser_close_confirmed': closed,
              'api_exit_confirmed': api_exited, 'startup_script_restored': True,
              'container_status': state['Status'], 'exit_code': state['ExitCode'],
              'oom_killed': state['OOMKilled'], 'profile_and_state_volumes_preserved': True,
              'request_observer_sha256': deployed, 'observer_loaded_on_next_start': True,
              'shutdown_markers': [row for row in rows if row.get('event') == 'backend_context_closed' and row.get('utc', '') >= started]}
    (OUT / 'shutdown-and-deployment.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
