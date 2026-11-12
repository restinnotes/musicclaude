"""Install tested passive focus into only the stopped native identity clone."""
from datetime import datetime,timezone
import hashlib
import json
from build_mg_storage_pair import OUT,ROOT,SOURCE,docker


def main():
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    source=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not source['Running'] and source['FinishedAt']==manifest['source_finished_at']
    arm=manifest['clones']['native_identity'];name=arm['container']
    assert not json.loads(docker('inspect',name))[0]['State']['Running']
    stamp=datetime.now(timezone.utc).strftime('%H%M%S')
    folder=OUT/('hint-observer-deployment-'+stamp);folder.mkdir(exist_ok=False)
    observer=ROOT/'src/request_observer.py'
    backup=folder/'previous-request-observer.py'
    docker('cp',name+':/app/src/request_observer.py',str(backup))
    docker('cp',str(observer),name+':/app/src/request_observer.py')
    readback=folder/'request-observer.py'
    docker('cp',name+':/app/src/request_observer.py',str(readback))
    assert observer.read_bytes()==readback.read_bytes()
    marker=folder/'focus.json';marker.write_text(json.dumps(['7078','646436']),encoding='utf-8')
    docker('cp',str(marker),name+':/app/state/.mg-forensic-asset-prefixes.json')
    marker_readback=folder/'focus-readback.json'
    docker('cp',name+':/app/state/.mg-forensic-asset-prefixes.json',str(marker_readback))
    assert marker.read_bytes()==marker_readback.read_bytes()
    report=dict(utc=datetime.now(timezone.utc).isoformat(),container=name,
        stopped_during_install=True,source_profile_or_code_modified=False,
        previous_observer_sha256=hashlib.sha256(backup.read_bytes()).hexdigest(),
        observer_sha256=hashlib.sha256(readback.read_bytes()).hexdigest(),
        focused_asset_prefixes=json.loads(marker_readback.read_text()),
        focus_reason='Retain actual hashes of the request-builder and browser-context modules within existing asset byte budget',
        model_body_or_headers_changed=False)
    (folder/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
