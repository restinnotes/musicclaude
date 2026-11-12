"""Install experimental header control into the stopped, owned clone only."""
from datetime import datetime, timezone
import hashlib
import json
from build_mg_storage_pair import ROOT, OUT, SOURCE, docker


def main():
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    state=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not state['Running'] and state['FinishedAt']==manifest['source_finished_at']
    name=manifest['clones']['native_identity']['container']
    assert not json.loads(docker('inspect',name))[0]['State']['Running']
    folder=OUT/('native-hint-deployment-'+datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    before=folder/'previous-standard-completion.py'
    docker('cp',name+':/app/src/api/standard_completion.py',str(before))
    files={ROOT/'src/api/standard_completion.py':'/app/src/api/standard_completion.py',
           ROOT/'src/browser/environment_evidence.py':'/app/src/browser/environment_evidence.py',
           ROOT/'src/api/probe_evidence.py':'/app/src/api/probe_evidence.py',
           ROOT/'work/mg_native_hint_settings.py':'/app/src/mg_native_hint_settings.py'}
    hashes={}
    for file,target in files.items():
        if file.name == 'probe_evidence.py':
            docker('cp',name+':'+target,str(folder/'previous-probe-evidence.py'))
        docker('cp',str(file),name+':'+target)
        readback=folder/file.name
        docker('cp',name+':'+target,str(readback))
        assert readback.read_bytes()==file.read_bytes()
        hashes[target]=hashlib.sha256(readback.read_bytes()).hexdigest()
    record=dict(utc=datetime.now(timezone.utc).isoformat(),container=name,
        original_container_modified=False,browser_profile_modified=False,
        stopped_during_install=True,installed_sha256=hashes,
        previous_completion_sha256=hashlib.sha256(before.read_bytes()).hexdigest(),
        experiment='Per-request real native high-entropy UA hints; unchanged UI and prompt body')
    (folder/'report.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record))


if __name__=='__main__':main()
