"""Resume the same original MG after the single-browser causal comparison."""
from datetime import datetime, timezone
import hashlib
import json
import sys
import time
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker
import runtime_memory_guard

sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main():
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    for arm in manifest['clones'].values():
        assert not json.loads(docker('inspect', arm['container']))[0]['State']['Running']
    before = json.loads(docker('inspect', SOURCE))[0]
    assert before['Id'] == '2565aa0a85ac5bb28a4411bd67ce188a51547814a5e6a72d8083b0688abf521c'
    volumes = {m['Destination']: m['Name'] for m in before['Mounts'] if m['Type'] == 'volume'}
    assert volumes == {
        '/config':'yi-mimicgate-20261002-config',
        '/app/browser_data':'yi-mimicgate-20261002-browser',
        '/app/logs':'yi-mimicgate-20261002-logs',
        '/app/state':'yi-mimicgate-20261002-state',
    }
    assert not before['State']['Running']
    assert before['HostConfig']['Memory'] == 0 and before['HostConfig']['MemorySwap'] == 0
    memory = runtime_memory_guard.snapshot()
    reason = runtime_memory_guard.headroom_error(memory, 2, 5)
    if reason:
        raise RuntimeError(reason)
    camera_hash = hashlib.sha256((ROOT / 'src/api/probe_evidence.py').read_bytes()).hexdigest()
    record = {'utc': datetime.now(timezone.utc).isoformat(), 'container': SOURCE,
        'container_id': before['Id'], 'volumes': volumes, 'memory_before_start': memory,
        'api_ready': False, 'profile_or_cookie_reimported': False, 'user_chrome_modified': False}
    docker('start', SOURCE)
    mg.configure_profile('yi')
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        try:
            status, _ = mg.http_json('/healthz')
            if status == 200:
                record['api_ready'] = True
                break
        except (mg.CLIError, OSError) as error:
            record['last_readiness_error_class'] = type(error).__name__
        time.sleep(2)
    after = json.loads(docker('inspect', SOURCE))[0]
    assert after['Id'] == before['Id'] and after['Image'] == before['Image']
    assert {m['Destination']:m['Name'] for m in after['Mounts'] if m['Type']=='volume'} == volumes
    record['same_container_and_volumes'] = True
    record['started_at'] = after['State']['StartedAt']
    path = OUT / ('original-resumed-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json')
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    if not record['api_ready']:
        raise RuntimeError('Readiness expired; inspect this running original, never restart blindly')
    code = '''import hashlib,json,os
from pathlib import Path
from src.config import Config
from src.browser.identity_policy import patchright_only_mode
print(json.dumps({'native_identity':os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY'),
 'patchright_only':patchright_only_mode(),
 'policy':json.loads(Path('/app/state/.mg-patchright-only.json').read_text()),
 'native_hints':json.loads(Path('/app/state/.mg-native-hints.json').read_text()),
 'causal_utility_reader_enabled':Path('/app/state/.mg-causal-utility.json').exists(),
 'camera_sha256':hashlib.sha256(Path('/app/src/api/probe_evidence.py').read_bytes()).hexdigest()}))
'''
    policy = json.loads(docker('exec', '-w', '/app', SOURCE, '/opt/venv/bin/python', '-c', code))
    assert policy['native_identity'] == '1' and policy['patchright_only'] is True
    assert policy['policy'] == {'additional_stealth':False}
    assert policy['native_hints'] == {'mode':'baseline','park_idle_control':True}
    assert policy['causal_utility_reader_enabled'] is False
    assert policy['camera_sha256'] == camera_hash
    record['verified_policy'] = policy
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps({'report':str(path), **record}), flush=True)


if __name__ == '__main__':
    main()
