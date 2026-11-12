"""Copy the unchanged production profile offline for an auth-cookie-only control."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import urllib.request

sys.path.insert(0, 'work')
from clone_yi_no_stealth import docker

def main():
    source = 'yi-mimicgate-20261002'
    target = 'yi-rca-auth-only-20261006'
    image = 'mimicgate-yi-session-guard:20261006'
    out = Path('experiments/yi-rootcause/20261006T1625Z/auth-only')
    out.mkdir(exist_ok=False)
    information = json.loads(docker('inspect', source))[0]
    assert information['State']['Status'] == 'exited' and information['State']['ExitCode'] == 0
    image_id = docker('image', 'inspect', '--format', '{{.Id}}', image).strip()
    assert image_id == 'sha256:02495f5c4da0ab64b206cb52da7b41bb82a52526c3517fa47a800daa328b1ae2'
    suffixes = {'/app/browser_data':'browser','/app/state':'state','/config':'config','/app/logs':'logs'}
    volumes = {}
    for mount in information['Mounts']:
        if mount['Destination'] not in suffixes:
            continue
        name = target + '-' + suffixes[mount['Destination']]
        docker('volume', 'create', name)
        volumes[mount['Destination']] = name
        if mount['Destination'] != '/app/logs':
            docker('run', '--rm', '--network', 'none', '--memory', '256m', '--memory-swap', '256m', '--entrypoint', '/bin/sh',
                '-v', mount['Name'] + ':/source:ro', '-v', name + ':/destination',
                image, '-c', 'cp -a /source/. /destination/', timeout=300)
    args = ['create', '--name', target, '--memory', '4g', '--memory-swap', '6g', '--shm-size', str(information['HostConfig']['ShmSize']),
        '-p', '127.0.0.1:8662:8000', '-p', '127.0.0.1:5812:5800']
    for setting in information['Config']['Env']:
        args.extend(['-e', setting])
    for destination, volume in volumes.items():
        args.extend(['-v', volume + ':' + destination])
    args.append(image)
    docker(*args)
    docker('cp', 'src/request_observer.py', target + ':/app/src/request_observer.py')
    record = {'utc':datetime.now(timezone.utc).isoformat(), 'container':target,
        'source_container':source, 'source_profile_modified':False,
        'profile_copy':'complete offline read-only source copy', 'image_id':image_id,
        'browser_version':'original Chrome 153', 'timezone':'America/Los_Angeles',
        'model_behavior_modified':False, 'auth_import_not_yet_performed':True}
    (out / 'clone-provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    docker('start', target)
    for _ in range(20):
        try:
            health = json.loads(urllib.request.urlopen('http://127.0.0.1:8662/healthz',timeout=2).read())
            assert health['status'] == 'ok'
            break
        except Exception:
            time.sleep(2)
    else:
        raise RuntimeError('Auth-only control did not become healthy; no probe sent')
    print(json.dumps(record))

if __name__ == '__main__':
    main()
