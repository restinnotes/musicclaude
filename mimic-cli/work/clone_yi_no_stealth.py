"""Offline full-profile comparison; never resets or edits the original profile."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1313Z'
ORIGINAL = 'yi-mimicgate-20261002'
CLONE = 'yi-rca-no-stealth-20261006'


def docker(*args, timeout=180):
    result = subprocess.run(['docker', *args], capture_output=True, text=True,
        encoding='utf-8', timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Docker operation failed: ' + args[0])
    return result.stdout


def main():
    global CLONE
    sys.stdout.reconfigure(encoding='utf-8')
    sys.path.insert(0, str(ROOT / 'work'))
    import finish_yi_rca
    capacity = len(sys.argv) > 1 and sys.argv[1] == 'capacity'
    if capacity:
        CLONE = 'yi-rca-capacity-20261006'
    finish_yi_rca.OUT = OUT
    source = json.loads(docker('inspect', ORIGINAL))[0]
    if source['State']['Running']:
        finish_yi_rca.main()
    source = json.loads(docker('inspect', ORIGINAL))[0]
    assert not source['State']['Running']
    image = docker('commit', ORIGINAL, 'mimicgate-yi-rca:20261006').strip()
    volumes = {}
    destinations = {'/app/browser_data': 'browser', '/app/state': 'state', '/config': 'config', '/app/logs': 'logs'}
    for mount in source['Mounts']:
        destination = mount['Destination']
        if destination not in destinations:
            continue
        name = CLONE + '-' + destinations[destination]
        docker('volume', 'create', name)
        volumes[destination] = name
        if destination == '/app/logs':
            continue
        docker('run', '--rm', '--network', 'none', '--entrypoint', '/bin/sh',
            '-v', mount['Name'] + ':/source:ro', '-v', name + ':/destination',
            image, '-c', 'cp -a /source/. /destination/', timeout=300)
    args = ['create', '--name', CLONE, '--shm-size', str(source['HostConfig']['ShmSize'])]
    for container_port in source['HostConfig']['PortBindings']:
        port = container_port.split('/')[0]
        original_host = source['HostConfig']['PortBindings'][container_port][0]['HostPort']
        host_port = {'8652': '8662', '5802': '5812'}.get(original_host)
        if host_port:
            args.extend(['-p', '127.0.0.1:' + host_port + ':' + port])
    for env in source['Config']['Env']:
        args.extend(['-e', env])
    for destination, volume in volumes.items():
        args.extend(['-v', volume + ':' + destination])
    args.append(image)
    docker(*args)
    if capacity:
        for file in ('cookie_capacity.py', 'request_observer.py', 'session_observer.py',
                     'browser/manager.py', 'api/browser_gate.py', 'api/standard_completion.py',
                     'api/probe_evidence.py', 'api/openai_routes.py', 'chatgpt/client.py'):
            docker('cp', str(ROOT / 'src' / file), CLONE + ':/app/src/' + file)
        test_source = ROOT / 'src/cookie_capacity.py'
    else:
        stealth = (ROOT / 'src/browser/stealth.py').read_text(encoding='utf-8')
        marker = '    if _IN_DOCKER:\n'
        assert stealth.count(marker) == 1
        modified = stealth.replace(marker, '    return  # Diagnostic clone: omit additional stealth patches.\n' + marker)
        test_source = OUT / 'stealth.diagnostic-no-patches.py'
        test_source.write_text(modified, encoding='utf-8')
        docker('cp', str(test_source), CLONE + ':/app/src/browser/stealth.py')
    docker('start', CLONE)
    result = {'utc': datetime.now(timezone.utc).isoformat(), 'container': CLONE, 'original_container_stopped': True,
              'profile_copy': 'complete_offline_copy', 'original_volumes_modified': False,
              'image_id': image, 'api_url': 'http://127.0.0.1:8662', 'viewer_url': 'http://127.0.0.1:5812',
              'single_change': 'Temporary cookie retention enabled; original stealth retained' if capacity else 'additional playwright-stealth patches disabled',
              'diagnostic_source_sha256': hashlib.sha256(test_source.read_bytes()).hexdigest()}
    (OUT / ('capacity-clone-experiment.json' if capacity else 'clone-experiment.json')).write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
