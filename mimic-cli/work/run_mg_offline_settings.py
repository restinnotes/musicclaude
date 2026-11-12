"""Copy stopped MG profiles into network-isolated inspections with a hard cap."""
from datetime import datetime,timezone
import argparse
import json
import os
import subprocess
from build_mg_storage_pair import OUT,ROOT,SOURCE,docker
import runtime_memory_guard as memory


def main(conditions):
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    source=json.loads(docker('inspect',SOURCE))[0]
    assert not source['State']['Running']
    assert source['State']['FinishedAt']==manifest['source_finished_at']
    assert all(not json.loads(docker('inspect',arm['container']))[0]['State']['Running']
        for arm in manifest['clones'].values())
    stamp=datetime.now(timezone.utc).strftime('%H%M%S')
    original={m['Destination']:m['Name'] for m in source['Mounts'] if m['Type']=='volume'}
    env=os.environ.copy();keys=[]
    for item in source['Config']['Env']:
        key,value=item.split('=',1);env[key]=value;keys.append(key)
    env['DISPLAY']=':99';keys.append('DISPLAY')
    results=[]
    for condition,volume in [('source',original['/app/browser_data']),
        ('control',manifest['clones']['control']['volumes']['/app/browser_data']),
        ('local_storage',manifest['clones']['local_storage']['volumes']['/app/browser_data'])]:
        if condition not in conditions:continue
        file=OUT/('offline-settings-'+condition+'-'+stamp+'.json')
        assert not file.exists()
        before=memory.snapshot()
        # Previous blank/fixture-only inspections peaked at 350-353 MiB.
        # Bound this narrower stage at 512 MiB with 1 GiB host reserve.
        reason=memory.headroom_error(before,1,3)
        if reason:
            print(json.dumps(dict(started=False,condition=condition,reason=reason,memory=before)))
            return 2
        temporary='yi-mg-settings-inspect-'+stamp+'-'+condition
        docker('volume','create',temporary)
        temporary_config=temporary+'-config'
        docker('volume','create',temporary_config)
        docker('run','--rm','--network','none','--memory','256m','--memory-swap','256m',
            '--entrypoint','/bin/sh','-v',original['/config']+':/source:ro','-v',temporary_config+':/destination',
            manifest['frozen_image'],'-c','cp -a /source/. /destination/')
        docker('run','--rm','--network','none','--memory','256m','--memory-swap','256m',
            '--entrypoint','/bin/sh','-v',volume+':/source:ro','-v',temporary+':/destination',
            manifest['frozen_image'],'-c','cp -a /source/. /destination/')
        args=['docker','run','--rm','--name',temporary,'--network','none',
            '--memory','512m','--memory-swap','512m','--shm-size',str(source['HostConfig']['ShmSize']),
            '--user',env.get('USER_ID','1000')+':'+env.get('GROUP_ID','1000'),
            '--entrypoint','/bin/sh','-w','/app','-v',temporary+':/app/browser_data',
            '-v',temporary_config+':/config',
            '--tmpfs','/app/state:rw,uid=1000,gid=1000,mode=0770,size=32m',
            '--tmpfs','/app/logs:rw,uid=1000,gid=1000,mode=0770,size=32m']
        for key in sorted(set(keys)):args+=['-e',key]
        for script in ['prepare_mg_storage_clone.py','inspect_mg_offline_settings.py']:
            args+=['-v',str(ROOT/'work'/script)+':/app/work/'+script+':ro']
        command='/opt/venv/bin/python -c \'from pathlib import Path; Path("/app/browser_data/.mg-storage-clone-owned.json").write_text("{\\"schema\\":1,\\"owned_clone\\":true,\\"source_profile_mounted\\":false,\\"network_isolated\\":true}")\'\n'
        command+='/opt/base/bin/Xvnc :99 -geometry 1366x768 -depth 24 -rfbport 5900 -localhost -nolisten tcp >/dev/null 2>&1 &\n'
        command+='i=0; while [ ! -S /tmp/.X11-unix/X99 ] && [ "$i" -lt 30 ]; do sleep 0.1; i=$((i+1)); done\n'
        command+='exec /opt/venv/bin/python /app/work/inspect_mg_offline_settings.py'
        args += [manifest['frozen_image'],'-c',command]
        done=subprocess.run(args,capture_output=True,env=env,timeout=90,
            creationflags=subprocess.CREATE_NO_WINDOW)
        try:result=json.loads(done.stdout)
        except ValueError:result=dict(completed=False,error_code='inspection_report_unavailable')
        result.update(condition=condition,utc=datetime.now(timezone.utc).isoformat(),
            source_browser_volume_mounted_read_only_only_in_copy=True,
            arbitrary_values_logged=False,memory_before=before,return_code=done.returncode)
        file.write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps(dict(condition=condition,file=str(file),completed=result.get('completed'),
            local_storage_count=result.get('local_storage_count'),memory_peak_bytes=result.get('memory_peak_bytes'))),flush=True)
        results.append(result)
        if done.returncode or not result.get('completed'):return 1
    after=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not after['Running'] and after['FinishedAt']==source['State']['FinishedAt']
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--conditions',nargs='+',choices=['source','control','local_storage'],
        default=['source','control','local_storage'])
    raise SystemExit(main(parser.parse_args().conditions))
