"""Stopped third arm: same frozen MG/profile, native browser identity opt-in."""
from datetime import datetime, timezone
import hashlib
import json
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker

NAME = 'yi-mg-native-identity-20261007'


def main():
    path = OUT / 'matched-pair.json'
    manifest = json.loads(path.read_text())
    if 'native_identity' in manifest['clones']:
        raise RuntimeError('Identity clone already registered; do not recreate')
    source = json.loads(docker('inspect', SOURCE))[0]
    if source['State']['Running'] or source['State']['FinishedAt'] != manifest['source_finished_at']:
        raise RuntimeError('Stopped source changed after initial freeze')
    if NAME in docker('ps', '-a', '--format', '{{.Names}}').splitlines():
        raise RuntimeError('Identity clone name already exists')
    image = manifest['frozen_image']
    suffixes = {'/config':'config','/app/browser_data':'browser','/app/logs':'logs','/app/state':'state'}
    volumes = {}
    for mount in source['Mounts']:
        destination = mount['Destination']
        if destination not in suffixes:
            continue
        assert mount['Type'] == 'volume'
        volume = NAME + '-' + suffixes[destination]
        docker('volume', 'create', volume)
        volumes[destination] = volume
        if destination != '/app/logs':
            docker('run', '--rm', '--network', 'none', '--memory', '256m', '--memory-swap', '256m',
                '--entrypoint', '/bin/sh', '-v', mount['Name'] + ':/source:ro',
                '-v', volume + ':/destination', image, '-c', 'cp -a /source/. /destination/')
    assert set(volumes) == set(suffixes)
    # Environment values remain in the child process, never in printed output.
    import os, subprocess
    env = os.environ.copy()
    for entry in source['Config']['Env']:
        key,value = entry.split('=',1)
        env[key] = value
    env.update(MIMICGATE_FORENSIC_ASSETS='1',MIMICGATE_NATIVE_BROWSER_IDENTITY='1')
    keys = {entry.split('=',1)[0] for entry in source['Config']['Env']} | {
        'MIMICGATE_FORENSIC_ASSETS','MIMICGATE_NATIVE_BROWSER_IDENTITY'}
    args = ['docker','create','--name',NAME,'--memory','1536m','--memory-swap','1536m',
        '--shm-size',str(source['HostConfig']['ShmSize']),
        '-p','127.0.0.1:8670:8000','-p','127.0.0.1:5820:5800']
    for key in sorted(keys):args += ['-e',key]
    for destination,volume in volumes.items():args += ['-v',volume + ':' + destination]
    result = subprocess.run(args + [image], env=env,capture_output=True,
        creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError('Stopped identity clone creation failed')
    installed = {}
    for file in ['request_observer.py','browser/stealth.py']:
        local = ROOT / 'src' / file
        docker('cp',str(local),NAME + ':/app/src/' + file)
        dest = OUT / 'code-readback/native_identity' / file
        dest.parent.mkdir(parents=True,exist_ok=True)
        docker('cp',NAME + ':/app/src/' + file,str(dest))
        assert dest.read_bytes() == local.read_bytes()
        installed[file] = hashlib.sha256(dest.read_bytes()).hexdigest()
    manifest['clones']['native_identity'] = dict(container=NAME,volumes=volumes,
        api_url='http://127.0.0.1:8670',viewer_url='http://127.0.0.1:5820',
        memory_limit_bytes=1536*1024**2,swap_allowed=False,stopped=True,
        change='Native platform, userAgent, userAgentData and sec_ch_ua; other Stealth settings retained',
        expected_local_storage_clear=False,installed_hashes=installed)
    path.write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(dict(clone=NAME,created_stopped=True,source_preserved=True,
        installed_hashes=installed)),flush=True)


if __name__=='__main__':main()
