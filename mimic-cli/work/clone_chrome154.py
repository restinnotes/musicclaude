"""Offline copied profile; only the Chrome executable differs from the source."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261006T1625Z/chrome154'
SOURCE = 'yi-rca-capacity-20261006'
TARGET = 'yi-rca-chrome154-20261006'
sys.path.insert(0, str(ROOT / 'work'))
from clone_yi_no_stealth import docker

def main():
    OUT.mkdir(exist_ok=False)
    source = json.loads(docker('inspect', SOURCE))[0]
    assert source['State']['Status'] == 'exited' and source['State']['ExitCode'] == 0
    image = docker('commit', SOURCE, 'mimicgate-yi-chrome154-diagnostic:20261006').strip()
    destinations = {'/app/browser_data':'browser','/app/state':'state','/config':'config','/app/logs':'logs'}
    volumes = {}
    for mount in source['Mounts']:
        if mount['Destination'] not in destinations:
            continue
        name = TARGET + '-' + destinations[mount['Destination']]
        docker('volume', 'create', name)
        volumes[mount['Destination']] = name
        if mount['Destination'] != '/app/logs':
            docker('run', '--rm', '--network', 'none', '--memory', '256m', '--memory-swap', '256m', '--entrypoint', '/bin/sh',
                '-v', mount['Name'] + ':/source:ro', '-v', name + ':/destination',
                image, '-c', 'cp -a /source/. /destination/', timeout=300)
    args = ['create','--name',TARGET,'--memory','4g','--memory-swap','6g','--shm-size',str(source['HostConfig']['ShmSize'])]
    for port, bindings in source['HostConfig']['PortBindings'].items():
        for binding in bindings:
            args.extend(['-p','127.0.0.1:' + binding['HostPort'] + ':' + port.split('/')[0]])
    for env in source['Config']['Env']:
        args.extend(['-e',env])
    for destination, volume in volumes.items():
        args.extend(['-v',volume+':'+destination])
    args.append(image)
    docker(*args)
    before = OUT / 'manager.before.py'
    docker('cp', SOURCE + ':/app/src/browser/manager.py', str(before))
    text = before.read_text(encoding='utf-8')
    marker = '        launch_kwargs = dict(\n'
    assert text.count(marker) == 1
    text = text.replace(marker, marker + '            executable_path="/opt/mg-diagnostic/chrome154/chrome-linux64/chrome",\n')
    modified = OUT / 'manager.chrome154.py'
    modified.write_text(text, encoding='utf-8')
    docker('cp', str(modified), TARGET + ':/app/src/browser/manager.py')
    record = {'utc':datetime.now(timezone.utc).isoformat(),'container':TARGET,'source_container':SOURCE,
        'profile_copy':'complete offline copy','source_profile_modified':False,
        'original_profile_modified':False,'single_change':'Chrome executable 153 to official Chrome for Testing 154.0.8037.92',
        'image_id':image,'manager_sha256':hashlib.sha256(modified.read_bytes()).hexdigest()}
    (OUT / 'experiment.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    docker('start',TARGET)
    print(json.dumps(record))

if __name__ == '__main__':
    main()
