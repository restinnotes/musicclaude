"""Freeze a stopped source and create two stopped, memory-bounded MG clones."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments/yi-rootcause/20261007T2135Z'
SOURCE = 'yi-mimicgate-20261002'
PAIRS = {'control': ('yi-mg-storage-control-20261007', 8668, 5818),
         'local_storage': ('yi-mg-storage-ls-20261007', 8669, 5819)}


def docker(*args, timeout=300):
    reply = subprocess.run(['docker', *args], capture_output=True, text=True,
        encoding='utf-8', timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
    if reply.returncode:
        raise RuntimeError('Clone Docker operation failed: ' + args[0])
    return reply.stdout


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = OUT / 'matched-pair.json'
    if manifest.exists():
        raise RuntimeError('Clone experiment already frozen; do not overwrite')
    source = json.loads(docker('inspect', SOURCE))[0]
    if source['State']['Running']:
        raise RuntimeError('Source must be stopped; builder will not stop it')
    names = set(docker('ps', '-a', '--format', '{{.Names}}').splitlines())
    if any(name in names for name, _, _ in PAIRS.values()):
        raise RuntimeError('New clone name already exists')
    image = docker('commit', SOURCE, 'mimicgate-yi-storage-rca:20261007-2135').strip()
    report = dict(utc=datetime.now(timezone.utc).isoformat(), source=SOURCE,
        source_image=source['Image'], frozen_image=image,
        source_finished_at=source['State']['FinishedAt'], source_volumes_read_only=True,
        source_started=False, source_profile_modified=False, clones={},
        intended_single_variable='ChatGPT origin local_storage clear only; same native cookie bundle')
    destinations = {'/app/browser_data': 'browser', '/app/state': 'state', '/config': 'config', '/app/logs': 'logs'}
    for condition, (name, api, viewer) in PAIRS.items():
        volumes = {}
        for mount in source['Mounts']:
            destination = mount['Destination']
            if destination not in destinations:
                continue
            if mount['Type'] != 'volume':
                raise RuntimeError('Expected named source volumes only')
            volume = name + '-' + destinations[destination]
            docker('volume', 'create', volume)
            volumes[destination] = volume
            if destination == '/app/logs':
                continue
            docker('run', '--rm', '--network', 'none', '--memory', '256m', '--memory-swap', '256m',
                '--entrypoint', '/bin/sh', '-v', mount['Name'] + ':/source:ro',
                '-v', volume + ':/destination', image, '-c', 'cp -a /source/. /destination/')
        if set(volumes) != set(destinations):
            raise RuntimeError('Source clone is missing required mounts')
        env = [entry for entry in source['Config']['Env'] if not entry.startswith('MIMICGATE_FORENSIC_ASSETS=')]
        env.append('MIMICGATE_FORENSIC_ASSETS=1')
        args = ['create', '--name', name, '--memory', '2g', '--memory-swap', '2g',
            '--shm-size', str(source['HostConfig']['ShmSize'])]
        for container_port, bindings in source['HostConfig']['PortBindings'].items():
            host = bindings[0]['HostPort']
            target = api if host == '8652' else viewer if host == '5802' else None
            if target:
                args += ['-p', '127.0.0.1:' + str(target) + ':' + container_port.split('/')[0]]
        for entry in env:
            args += ['-e', entry]
        for path, volume in volumes.items():
            args += ['-v', volume + ':' + path]
        args.append(image)
        docker(*args)
        report['clones'][condition] = dict(container=name, volumes=volumes,
            api_url='http://127.0.0.1:' + str(api), viewer_url='http://127.0.0.1:' + str(viewer),
            memory_limit_bytes=2 * 1024**3, swap_allowed=False, stopped=True)
        print(json.dumps(dict(condition=condition, clone_created_stopped=True)), flush=True)
    current = json.loads(docker('inspect', SOURCE))[0]
    if current['State']['Running'] or current['State']['FinishedAt'] != source['State']['FinishedAt']:
        raise RuntimeError('Source state changed during cloning')
    manifest.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(dict(manifest=str(manifest), source_preserved=True)), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps(dict(error='Stopped clone preparation failed', exception_class=type(error).__name__)), flush=True)
        sys.exit(1)
