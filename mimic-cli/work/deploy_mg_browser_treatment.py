"""Change only additional JS patches in the stopped owned diagnostic clone."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from build_mg_storage_pair import ROOT,OUT,SOURCE,docker


def main(mode):
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    name=manifest['clones']['native_identity']['container']
    source=json.loads(docker('inspect',SOURCE))[0]['State']
    assert not source['Running'] and source['FinishedAt']==manifest['source_finished_at']
    assert not json.loads(docker('inspect',name))[0]['State']['Running']
    folder=OUT/('browser-treatment-'+datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    docker('cp',name+':/app/src/browser/stealth.py',str(folder/'previous-stealth.py'))
    hashes={}
    for basename in ('stealth.py','identity_policy.py'):
        file=ROOT/'src/browser'/basename;target='/app/src/browser/'+basename
        docker('cp',str(file),name+':'+target)
        readback=folder/basename;docker('cp',name+':'+target,str(readback))
        assert file.read_bytes()==readback.read_bytes()
        hashes[basename]=hashlib.sha256(readback.read_bytes()).hexdigest()
    marker=folder/'mode.json';marker.write_text(json.dumps({'additional_stealth':mode=='extra_patches'}))
    docker('cp',str(marker),name+':/app/state/.mg-patchright-only.json')
    readback=folder/'mode-readback.json';docker('cp',name+':/app/state/.mg-patchright-only.json',str(readback))
    assert marker.read_bytes()==readback.read_bytes()
    record=dict(utc=datetime.now(timezone.utc).isoformat(),container=name,mode=mode,
        source_container_or_profile_modified=False,installed_hashes=hashes,
        browser_binary_changed=False,manual_headers_changed=False,stopped_during_install=True)
    (folder/'report.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['patchright_only','extra_patches'])
    main(p.parse_args().mode)
