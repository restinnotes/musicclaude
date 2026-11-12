"""Start only the existing causal clone; keep the original and other arms off."""
from datetime import datetime, timezone
import json
import sys
import time
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker
import runtime_memory_guard

sys.path.insert(0, str(ROOT / 'cli'))
import mg


def main():
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    source_before = json.loads(docker('inspect', SOURCE))[0]['State']
    assert not source_before['Running']
    arm = manifest['clones']['native_identity']
    for other in manifest['clones'].values():
        assert not json.loads(docker('inspect', other['container']))[0]['State']['Running']
    target = json.loads(docker('inspect', arm['container']))[0]
    assert target['Image'] == manifest['frozen_image']
    assert {m['Destination']: m['Name'] for m in target['Mounts'] if m['Type']=='volume'} == arm['volumes']
    assert target['HostConfig']['Memory'] in (1610612736, 2147483648)
    assert target['HostConfig']['MemorySwap'] == target['HostConfig']['Memory']
    memory = runtime_memory_guard.snapshot()
    reason = runtime_memory_guard.headroom_error(memory, 2, 5)
    if reason:
        raise RuntimeError(reason)
    record = {'utc':datetime.now(timezone.utc).isoformat(), 'container':arm['container'],
        'memory_before_start':memory, 'previous_memory_cap':target['HostConfig']['Memory'],
        'matched_treatment_memory_cap':2147483648, 'api_ready':False,
        'original_started':False, 'profile_or_cookie_changed':False}
    # Source reached 1.51 GiB, above the old 1.5 GiB clone cap. Use the same
    # 2 GiB/no-swap cap for BOTH treatments, preventing that confound.
    docker('update', '--memory', '2g', '--memory-swap', '2g', arm['container'])
    docker('start', arm['container'])
    mg.CONTAINER = arm['container']
    mg.API = arm['api_url']
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
    source_after = json.loads(docker('inspect', SOURCE))[0]['State']
    assert not source_after['Running'] and source_after['FinishedAt'] == source_before['FinishedAt']
    record['source_state_unchanged'] = True
    path = OUT / ('causal-start-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json')
    assert not path.exists()
    path.write_text(json.dumps(record, indent=2))
    print(json.dumps({'report':str(path), **record}), flush=True)
    if not record['api_ready']:
        raise RuntimeError('Readiness observation expired; inspect the running clone, never restart blindly')
    code = '''import json
from pathlib import Path
from src.config import Config
from src.browser.identity_policy import patchright_only_mode
print(json.dumps({'patchright_only':patchright_only_mode(),'policy':json.loads(Path('/app/state/.mg-patchright-only.json').read_text()),'native_hints':json.loads(Path('/app/state/.mg-native-hints.json').read_text())}))
'''
    policy = json.loads(docker('exec', '-w', '/app', arm['container'], '/opt/venv/bin/python', '-c', code))
    assert policy['patchright_only'] is (not policy['policy']['additional_stealth'])
    assert policy['native_hints'] == {'mode':'baseline','park_idle_control':True}
    record['verified_policy'] = policy
    path.write_text(json.dumps(record, indent=2))
    print(json.dumps(policy), flush=True)


if __name__ == '__main__':
    main()
