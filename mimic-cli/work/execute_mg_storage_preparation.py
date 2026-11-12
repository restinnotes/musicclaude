"""Run exactly one network-isolated owned profile preparation; no model call."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from build_mg_storage_pair import OUT, ROOT, SOURCE, docker
from mg_private_cookie import dpapi_json
import runtime_memory_guard as memory

COOKIE_FILE = OUT / 'native-cookie-refresh-09d/native-cookies.dpapi.json'


def main(condition):
    manifest = json.loads((OUT / 'matched-pair.json').read_text())
    details = manifest['clones'][condition]
    name = details['container']
    report_file = OUT / ('preparation-' + condition + '.json')
    if report_file.exists():
        raise RuntimeError('Preparation already attempted; preserve its evidence')
    source = json.loads(docker('inspect', SOURCE))[0]
    clone = json.loads(docker('inspect', name))[0]
    if source['State']['Running'] or clone['State']['Running']:
        raise RuntimeError('Only stopped source and clone can prepare')
    source_volumes = {mount.get('Name') for mount in source['Mounts']}
    if any(volume in source_volumes for volume in details['volumes'].values()):
        raise RuntimeError('Source profile mount forbidden')
    if any(json.loads(docker('inspect', d['container']))[0]['State']['Running']
            for d in manifest['clones'].values()):
        raise RuntimeError('A matched diagnostic browser is already running')
    before = memory.snapshot()
    # This stage only opens blank/local-fixture documents with Docker network
    # disabled. A 768-MiB hard cap plus 1.25 GiB host headroom bounds that work;
    # online model probes have a separate, larger launch budget.
    reason = memory.headroom_error(before, minimum_physical_gib=1.25, minimum_commit_gib=3)
    if reason:
        print(json.dumps(dict(submitted=False, reason=reason, memory=before)), flush=True)
        return 2
    encrypted = json.loads(COOKIE_FILE.read_text())
    if encrypted.get('format') != 'mimicgate-native-cookie-dpapi-v1':
        raise RuntimeError('Wrong encrypted cookie bundle')
    private = dpapi_json(encrypted['payload'], decrypt=True)
    env = os.environ.copy()
    keys = []
    for item in source['Config']['Env']:
        key, value = item.split('=', 1)
        env[key] = value
        keys.append(key)
    # No secret value appears in child argv. DISPLAY is shared preparation state.
    env['DISPLAY'] = ':99'
    keys.append('DISPLAY')
    args = ['docker', 'run', '--rm', '-i', '--name', name + '-offline-prep',
        '--network', 'none', '--memory', '768m', '--memory-swap', '768m',
        '--shm-size', str(source['HostConfig']['ShmSize']),
        '--user', env.get('USER_ID', '1000') + ':' + env.get('GROUP_ID', '1000'),
        '--entrypoint', '/bin/sh', '-w', '/app']
    for key in sorted(set(keys)):
        args += ['-e', key]
    for destination, volume in details['volumes'].items():
        args += ['-v', volume + ':' + destination]
    script = ROOT / 'work/prepare_mg_storage_clone.py'
    args += ['-v', str(script) + ':/app/work/prepare_mg_storage_clone.py:ro']
    marker = dict(schema=1, owned_clone=True, source_profile_mounted=False, network_isolated=True)
    marker_text = json.dumps(marker, separators=(',', ':'))
    # Fixed local launcher: marker is public provenance, cookies use private stdin.
    command = "/opt/venv/bin/python -c 'from pathlib import Path; Path(\"/app/browser_data/.mg-storage-clone-owned.json\").write_text(\"" + marker_text.replace('"', '\\"') + "\")'\n"
    # The frozen image ships Xvnc, not Xvfb. Xvnc requires an RFB listener;
    # constrain it to the network-none container loopback with no host port.
    command += '/opt/base/bin/Xvnc :99 -geometry 1366x768 -depth 24 -rfbport 5900 -localhost -nolisten tcp >/dev/null 2>&1 &\n'
    command += 'i=0; while [ ! -S /tmp/.X11-unix/X99 ] && [ "$i" -lt 30 ]; do sleep 0.1; i=$((i+1)); done\n'
    preparation_mode = 'control' if condition == 'native_identity' else condition
    command += 'exec /opt/venv/bin/python /app/work/prepare_mg_storage_clone.py --mode ' + preparation_mode
    args += [manifest['frozen_image'], '-c', command]
    started = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(dict(cookies=private['cookies'])).encode()
    result = subprocess.run(args, input=payload, capture_output=True, env=env,
        timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
    del payload, private, encrypted
    try:
        preparation = json.loads(result.stdout)
    except Exception:
        preparation = dict(completed=False, error_code='safe_preparation_report_unavailable')
    preparation.update(started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
        condition=condition, clone=name, source_profile_mounted=False,
        network_mode='none', memory_limit_bytes=768 * 1024**2,
        memory_before=before, memory_after=memory.snapshot(),
        cookie_bundle_sha256=hashlib.sha256(COOKIE_FILE.read_bytes()).hexdigest(),
        preparation_script_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
        return_code=result.returncode, stderr_present=bool(result.stderr))
    preparation['success'] = bool(result.returncode == 0 and preparation.get('completed')
        and preparation.get('browser_closed') and preparation.get('cookies_exactly_unchanged'))
    report_file.write_text(json.dumps(preparation, indent=2), encoding='utf-8')
    print(json.dumps(preparation), flush=True)
    return 0 if preparation['success'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('condition', choices=['control', 'local_storage','native_identity'])
    args = parser.parse_args()
    try:
        code = main(args.condition)
    except Exception as error:
        print(json.dumps(dict(submitted=False, error='Owned preparation ended; preserve container and evidence',
            exception_class=type(error).__name__)), flush=True)
        code = 1
    raise SystemExit(code)
