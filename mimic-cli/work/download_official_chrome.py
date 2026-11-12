"""Download and checksum the official public Debian Chrome package only."""
from datetime import datetime,timezone
import hashlib
import json
import os
import urllib.request
from build_mg_storage_pair import OUT


def main():
    meta=max(OUT.glob('official-chrome-releases-*.json'),key=lambda f:f.stat().st_mtime)
    item=json.loads(meta.read_text())['google_stable']
    assert item['Package']=='google-chrome-stable' and item['Architecture']=='amd64'
    assert item['Filename'].startswith('pool/main/g/google-chrome-stable/') and '..' not in item['Filename']
    assert 0<int(item['Size'])<250*1024*1024
    folder=OUT/('official-chrome-package-'+datetime.now(timezone.utc).strftime('%H%M%S'))
    folder.mkdir(exist_ok=False)
    url='https://dl.google.com/linux/chrome/deb/'+item['Filename']
    file=folder/'google-chrome-stable.deb';digest=hashlib.sha256();size=0
    print(json.dumps(dict(downloading_public_package=True,version=item['Version'],folder=str(folder))),flush=True)
    with urllib.request.urlopen(url,timeout=30) as reply,file.open('xb') as dst:
        while True:
            part=reply.read(1024*1024)
            if not part:break
            size+=len(part)
            if size>int(item['Size']):raise RuntimeError('Package length exceeded metadata')
            digest.update(part);dst.write(part)
    assert size==int(item['Size']) and digest.hexdigest()==item['SHA256']
    record=dict(utc=datetime.now(timezone.utc).isoformat(),public_url=url,
        bytes=size,sha256=digest.hexdigest(),matches_google_apt_metadata=True,
        version=item['Version'],download_only=True,native_windows_install=False,
        browser_profile_accessed=False,package=str(file))
    (folder/'report.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record),flush=True)


if __name__=='__main__':main()
