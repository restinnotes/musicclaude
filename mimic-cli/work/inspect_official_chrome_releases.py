"""Read public Google release metadata; no browser/account traffic."""
from datetime import datetime,timezone
import gzip
import hashlib
import json
import urllib.request
from build_mg_storage_pair import OUT


def fetch(url,limit):
    with urllib.request.urlopen(url,timeout=30) as r:
        body=r.read(limit+1)
    if len(body)>limit:raise RuntimeError('Public metadata exceeds bound')
    return body


def main():
    url='https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
    body=fetch(url,16*1024*1024);data=json.loads(body)
    releases=[]
    for item in data['versions']:
        if int(item['version'].split('.')[0])!=153:continue
        linux=[d['url'] for d in item.get('downloads',{}).get('chrome',[]) if d['platform']=='linux64']
        if linux:releases.append(dict(version=item['version'],linux64_url=linux[0]))
    apt_url='https://dl.google.com/linux/chrome/deb/dists/stable/main/binary-amd64/Packages.gz'
    apt=fetch(apt_url,2*1024*1024)
    text=gzip.decompress(apt)
    if len(text)>4*1024*1024:raise RuntimeError('APT metadata exceeds bound')
    stable={}
    for block in text.decode().split('\n\n'):
        fields={line.split(': ',1)[0]:line.split(': ',1)[1] for line in block.splitlines() if ': ' in line and not line.startswith(' ')}
        if fields.get('Package')=='google-chrome-stable':
            stable={k:fields[k] for k in ('Package','Version','Architecture','Filename','SHA256','Size')}
    report=dict(utc=datetime.now(timezone.utc).isoformat(),source_urls=[url,apt_url],
        known_good_metadata_sha256=hashlib.sha256(body).hexdigest(),
        google_stable=stable,latest_153=releases[-6:],
        exact_existing_version=next((r for r in releases if r['version']=='153.0.8010.12'),None),
        browser_or_profile_started=False)
    file=OUT/('official-chrome-releases-'+datetime.now(timezone.utc).strftime('%H%M%S')+'.json')
    file.write_text(json.dumps(report,indent=2))
    print(json.dumps(report))


if __name__=='__main__':main()
