"""Cold toggle of one public policy in the existing diagnostic clone only."""
import argparse
from datetime import datetime, timezone
import json
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker


def main(enabled):
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    arm = manifest['clones']['native_identity']
    source = json.loads(docker('inspect', SOURCE))[0]
    assert not source['State']['Running'], 'Source must be idle and stopped first'
    source_volumes = {m['Name'] for m in source['Mounts'] if m['Type'] == 'volume'}
    for clone in manifest['clones'].values():
        assert not json.loads(docker('inspect', clone['container']))[0]['State']['Running']
    target = json.loads(docker('inspect', arm['container']))[0]
    assert target['Image'] == manifest['frozen_image']
    assert 'MIMICGATE_NATIVE_BROWSER_IDENTITY=1' in target['Config']['Env']
    mounts = {m['Destination']: m['Name'] for m in target['Mounts'] if m['Type'] == 'volume'}
    assert mounts == arm['volumes'] and not source_volumes.intersection(mounts.values())
    state_volume = mounts['/app/state']
    code = '''import json
from pathlib import Path
p=Path('/app/state/.mg-patchright-only.json')
h=Path('/app/state/.mg-native-hints.json')
assert p.is_file() and not p.is_symlink() and p.stat().st_size <= 128
old=json.loads(p.read_text())
assert set(old)=={'additional_stealth'} and type(old['additional_stealth']) is bool
assert h.is_file() and not h.is_symlink() and h.stat().st_size <= 128
assert json.loads(h.read_text())=={'mode':'baseline','park_idle_control':True}
new={'additional_stealth':ENABLED}
p.write_text(json.dumps(new))
assert json.loads(p.read_text())==new
u=Path('/app/state/.mg-causal-utility.json')
assert not u.is_symlink()
u.write_text(json.dumps({'enabled':True}))
print(json.dumps({'before':old,'after':new,'native_hints_unchanged':True}))
'''.replace('ENABLED', repr(enabled))
    result = json.loads(docker('run', '--rm', '--network', 'none', '--memory', '128m',
        '--memory-swap', '128m', '--entrypoint', '/opt/venv/bin/python',
        '--mount', 'type=volume,source=' + state_volume + ',target=/app/state',
        manifest['frozen_image'], '-c', code))
    after = json.loads(docker('inspect', SOURCE))[0]['State']
    assert not after['Running'] and after['FinishedAt'] == source['State']['FinishedAt']
    report = {'utc': datetime.now(timezone.utc).isoformat(), 'target': arm['container'],
        'single_treatment': 'additional_stealth', 'enabled': enabled, **result,
        'source_state_unchanged': True, 'source_volumes_mounted': False,
        'cookie_or_profile_modified': False, 'browser_or_model_started': False}
    path = OUT / ('causal-policy-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json')
    assert not path.exists()
    path.write_text(json.dumps(report, indent=2))
    print(json.dumps({'report': str(path), **report}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['on', 'off'])
    main(parser.parse_args().mode == 'on')
