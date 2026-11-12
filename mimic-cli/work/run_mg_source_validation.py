"""One normal source CLI invocation, with resource evidence and no replay."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker
import runtime_memory_guard
from run_mg_storage_probe import container_memory_snapshot

sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main(label):
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    for arm in manifest['clones'].values():
        assert not json.loads(docker('inspect', arm['container']))[0]['State']['Running']
    source = json.loads(docker('inspect', SOURCE))[0]
    assert source['State']['Running']
    state = mg.http_json('/v1/tabs', mg.read_auth())[1]['concurrency']
    assert state['in_flight'] == 0 and state['waiting'] == 0
    folder = OUT / ('source-cup-' + label)
    folder.mkdir(exist_ok=False)
    record = {'started_utc': datetime.now(timezone.utc).isoformat(), 'container': SOURCE,
              'api_url': mg.API, 'source_started_at': source['State']['StartedAt'],
              'command': 'mg probe cup', 'automatic_replay': False, 'cli_started': False,
              'container_memory_before': container_memory_snapshot(SOURCE), 'success': False}
    policy_code = '''import json,hashlib
from pathlib import Path
from src.config import Config
from src.browser.identity_policy import patchright_only_mode
files=['/app/src/api/standard_completion.py','/app/src/request_observer.py','/app/src/browser/stealth.py','/app/state/.mg-patchright-only.json','/app/state/.mg-native-hints.json']
print(json.dumps({'files_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},'patchright_only':patchright_only_mode(),'pre_send_environment_evaluation': 'await observe_environment' in Path(files[0]).read_text()}))
'''
    policy = json.loads(docker('exec', '-w', '/app', SOURCE, '/opt/venv/bin/python', '-c', policy_code))
    assert policy['patchright_only'] and not policy['pre_send_environment_evaluation']
    (folder / 'runtime-policy-and-code.json').write_text(json.dumps(policy, indent=2))
    (folder / 'started.json').write_text(json.dumps(record, indent=2))
    print(json.dumps({'preparing_one_normal_source_cli_probe': True, 'folder': str(folder)}), flush=True)
    runtime_memory_guard.OUT = folder / 'memory'
    runtime_memory_guard.OUT.mkdir()
    timeline = runtime_memory_guard.ProbeMemoryTimeline(SOURCE, minimum_physical_gib=1, minimum_commit_gib=3)
    started = time.monotonic()
    try:
        with timeline:
            record['cli_started'] = True
            (folder / 'started.json').write_text(json.dumps(record, indent=2))
            # Execute the exact installed alias, in a hidden subprocess. The
            # trusted fixed path has no shell metacharacters or user input.
            result = subprocess.run(['cmd.exe', '/d', '/c', str(ROOT / 'bin/mg.cmd'), 'probe', 'cup'],
                capture_output=True, encoding='utf-8', errors='strict', timeout=2100,
                creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(ROOT))
        (folder / 'cli-stdout.txt').write_text(result.stdout, encoding='utf-8')
        (folder / 'cli-stderr.txt').write_text(result.stderr, encoding='utf-8')
        record['cli_exit_code'] = result.returncode
        paths = re.findall(r'^Run: (.+)$', result.stderr, re.MULTILINE)
        assert len(paths) == 1
        run = Path(paths[0].strip()).resolve()
        assert run.parent == (ROOT / 'runs').resolve()
        diagnostics = run / 'diagnostics.json'
        data = json.loads(diagnostics.read_text(encoding='utf-8'))
        assert data['profile'] == 'yi' and data['command'] == 'probe' and data['probe'] == 'cup'
        record.update(cli_run=str(run), diagnostic_sha256=hashlib.sha256(diagnostics.read_bytes()).hexdigest(),
                      success=data['success'], probe_assessment=data.get('probe_assessment'),
                      cli_error=data.get('error'), cli_elapsed_seconds=data.get('elapsed_seconds'),
                      screenshot_evidence_complete=data.get('local_screenshot_evidence', {}).get('complete', False),
                      ui_thinking_time=data.get('local_screenshot_evidence', {}).get('thinking_time_ui_labels', []))
    except Exception as error:
        record['validation_error_class'] = type(error).__name__
        record['success'] = False
    finally:
        record['finished_utc'] = datetime.now(timezone.utc).isoformat()
        record['total_seconds'] = round(time.monotonic()-started, 3)
        record['memory'] = timeline.summary()
        record['container_memory_after'] = container_memory_snapshot(SOURCE)
        before = record['container_memory_before'].get('events', {})
        after = record['container_memory_after'].get('events', {})
        if 'oom_kill' in before and 'oom_kill' in after:
            record['oom_kill_delta'] = after['oom_kill'] - before['oom_kill']
            if record['oom_kill_delta']:
                record['success'] = False
        # Read only the existing observer's sanitized, allowlisted events.
        # No browser attachment, retry, request interception or extra sender.
        observer_code = '''import json
from pathlib import Path
rows=[]
for line in Path('/app/state/yi-session-observer.jsonl').open():
 try: row=json.loads(line)
 except ValueError: continue
 if row.get('utc','') >= AFTER and row.get('event') in EVENTS: rows.append(row)
print(json.dumps(rows))
'''.replace('AFTER', repr(record['started_utc'])).replace('EVENTS', repr([
    'generation_wire_request', 'generation_wire_cookie_metadata', 'generation_stream_metadata',
    'generation_stream_finished', 'generation_stream_error', 'generation_observation_error',
    'standard_request_failed']))
        try:
            observer_file = folder / 'observer-terminal.json'
            observer_file.write_text(json.dumps(json.loads(docker('exec', SOURCE,
                '/opt/venv/bin/python', '-c', observer_code)), indent=2), encoding='utf-8')
            record['observer_sha256'] = hashlib.sha256(observer_file.read_bytes()).hexdigest()
        except Exception as error:
            record['observer_collection_error_class'] = type(error).__name__
        (folder / 'result.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'folder': str(folder), **record}, ensure_ascii=False), flush=True)
    return 0 if record['success'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--label', required=True)
    args = p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9]{1,24}', args.label):
        p.error('Use a short alphanumeric label')
    raise SystemExit(main(args.label))
