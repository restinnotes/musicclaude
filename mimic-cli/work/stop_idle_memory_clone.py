"""Prepared action: stop one identified idle clone ONLY after user approval."""
from datetime import datetime, timezone
import json
import urllib.request
from build_mg_storage_pair import OUT, SOURCE, docker


def main():
    approval_subject = json.loads((OUT / 'memory-block-idle-unowned-clone.json').read_text())
    name = 'yi-mg-clone-20261007'
    assert approval_subject['container'] == name
    target = json.loads(docker('inspect', name))[0]
    source = json.loads(docker('inspect', SOURCE))[0]
    assert target['Id'] == approval_subject['container_id'] and target['State']['Running']
    target_volumes = {m['Name'] for m in target['Mounts'] if m['Type']=='volume'}
    source_volumes = {m['Name'] for m in source['Mounts'] if m['Type']=='volume'}
    assert target_volumes == set(approval_subject['mount_names'])
    assert not target_volumes.intersection(source_volumes)
    with urllib.request.urlopen('http://127.0.0.1:8662/v1/tabs', timeout=10) as response:
        concurrency = json.loads(response.read())['concurrency']
    assert concurrency['in_flight'] == 0 and concurrency['waiting'] == 0
    folder = OUT / ('approved-idle-clone-stop-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(exist_ok=False)
    (folder / 'before.json').write_text(json.dumps({'container':name,'container_id':target['Id'],
        'concurrency':concurrency,'mount_names':sorted(target_volumes)}, indent=2))
    docker('stop', '--timeout', '60', target['Id'])
    after = json.loads(docker('inspect', name))[0]
    assert after['Id'] == target['Id'] and after['Mounts'] == target['Mounts']
    assert not after['State']['Running']
    record = {'container':name,'stopped':True,'exit_code':after['State']['ExitCode'],
        'container_and_volumes_preserved':True,'source_container_touched':False,
        'profile_or_cookie_reimported':False}
    (folder / 'result.json').write_text(json.dumps(record, indent=2))
    print(json.dumps(record), flush=True)


if __name__ == '__main__':
    main()
