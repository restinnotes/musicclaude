"""Run only after explicit user approval to stop the separate idle lab container."""
import json
from datetime import datetime, timezone
import urllib.request
from build_mg_storage_pair import OUT, SOURCE, docker
import runtime_memory_guard

TARGET = 'lab-mimicgate'
EXPECTED_ID = '062dc16eb01b0bc453c839c000c3006d1b1587e75954d42500592184c6f1e145'


def volumes(info):
    return {m['Destination']:m['Name'] for m in info['Mounts'] if m['Type']=='volume'}


def main():
    source = json.loads(docker('inspect', SOURCE))[0]
    before = json.loads(docker('inspect', TARGET))[0]
    assert before['Id'] == EXPECTED_ID and before['State']['Running']
    assert before['Config'].get('Labels', {}).get('com.docker.compose.project.working_dir') == r'D:\shared\chatgpt-gateway-lab\compose'
    assert not set(volumes(before).values()).intersection(volumes(source).values())
    with urllib.request.urlopen('http://127.0.0.1:8650/v1/gateway/activity', timeout=8) as response:
        state = json.load(response)['concurrency']
    assert state['in_flight'] == 0 and state['waiting'] == 0
    report = {'utc':datetime.now(timezone.utc).isoformat(), 'container':TARGET,
        'container_id':before['Id'], 'api_in_flight':0, 'api_waiting':0,
        'mounts_before':before['Mounts'], 'memory_before':runtime_memory_guard.snapshot(),
        'original_mg_running_before':source['State']['Running'], 'original_mg_not_restarted':True,
        'container_or_volume_removed':False, 'profile_or_cookie_imported':False,
        'user_chrome_modified':False}
    folder = OUT / ('approved-idle-lab-stop-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S'))
    folder.mkdir(exist_ok=False)
    (folder/'before.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    docker('stop', '--timeout', '60', before['Id'])
    after = json.loads(docker('inspect', TARGET))[0]
    source_after = json.loads(docker('inspect', SOURCE))[0]
    assert after['Id'] == before['Id'] and after['Mounts'] == before['Mounts']
    assert not after['State']['Running']
    assert source_after['Id'] == source['Id'] and source_after['State']['StartedAt'] == source['State']['StartedAt']
    assert source_after['State']['Running'] == source['State']['Running']
    report.update(stopped=True, exit_code=after['State']['ExitCode'], same_container_and_mounts=True,
        memory_after=runtime_memory_guard.snapshot())
    (folder/'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'report':str(folder/'result.json'),'stopped':True,'exit_code':after['State']['ExitCode'],
        'container_and_login_volumes_preserved':True,'original_mg_untouched':True}))


if __name__ == '__main__':
    main()
