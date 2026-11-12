"""Fetch only public JS whose URL is evidenced by frozen source cache keys."""
from datetime import datetime,timezone
import argparse
import hashlib
import json
import re
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from build_mg_storage_pair import OUT,ROOT,SOURCE,docker


def main(prefixes):
    source=json.loads(docker('inspect',SOURCE))[0]
    assert not source['State']['Running']
    manifest=json.loads((OUT/'matched-pair.json').read_text())
    assert source['State']['FinishedAt']==manifest['source_finished_at']
    volume=next(m['Name'] for m in source['Mounts'] if m['Destination']=='/app/browser_data')
    scan=json.loads(docker('run','--rm','--network','none','--memory','64m','--memory-swap','64m',
        '--entrypoint','/opt/venv/bin/python','-v',volume+':/source-profile:ro',
        '-v',str(ROOT/'work/read_mg_public_cache_keys.py')+':/read-public-cache.py:ro',
        manifest['frozen_image'],'/read-public-cache.py'))
    stamp=datetime.now(timezone.utc).strftime('%H%M%S')
    directory=OUT/('cached-public-frontend-'+stamp);directory.mkdir(exist_ok=False)
    # URLs have already passed the fixed public-host/asset-path cache-key filter.
    (directory/'cache-key-evidence.json').write_text(json.dumps(scan,indent=2),encoding='utf-8')
    assets=[];total=0
    # Prefer most recently written cache entries, with the observed entry module
    # first; mtime is cache provenance, not a claimed deployment timestamp.
    selected=sorted(scan['public_asset_urls'],key=lambda u:(
        '/entry.client' not in u,-scan['public_asset_cache_mtime'].get(u,0)))[:48]
    if prefixes:
        selected=[url for url in scan['public_asset_urls']
            if urlsplit(url).path.rsplit('/',1)[-1].split('.')[0] in prefixes][:48]
    for url in selected:
        basename=urlsplit(url).path.rsplit('/',1)[-1]
        record=dict(basename=basename,account_cookies_sent=False,
            url_observed_in_frozen_cache_header=True)
        try:
            with urlopen(Request(url,headers={'Accept-Encoding':'identity','Accept':'application/javascript'}),timeout=10) as response:
                if urlsplit(response.url).hostname not in ('chatgpt.com','cdn.oaistatic.com'):
                    raise ValueError('Public host changed')
                body=response.read(2*1024*1024+1)
            if len(body)>2*1024*1024 or total+len(body)>12*1024*1024:
                record['error']='asset_budget';assets.append(record);continue
            total+=len(body);(directory/basename).write_bytes(body)
            text=body.decode('utf-8')
            matches={}
            for needle in ('browser_context','instance_id','browserInstanceId','chatgpt-last-selected-model-v1',
                'codex.browser.appThemes.v1','chatgpt-work-models-v1'):
                hits=list(re.finditer(re.escape(needle),text))
                if hits:matches[needle]=[text[max(0,m.start()-150):m.end()+220] for m in hits[:4]]
            record.update(sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),bounded_code_matches=matches)
            record['cache_mtime_epoch']=scan['public_asset_cache_mtime'][url]
        except Exception as error:record['error_class']=type(error).__name__
        assets.append(record)
    report=dict(utc=datetime.now(timezone.utc).isoformat(),source_profile_read_only=True,
        browser_started=False,model_sent=False,public_js_only=True,total_bytes=total,assets=assets)
    (directory/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(directory=str(directory),scan_files=scan['files_scanned'],
        recognized_headers=scan['recognized_simple_cache_headers'],cached_asset_urls=len(scan['public_asset_urls']),
        fetched_assets=len(assets),total_bytes=total,
        matches=[dict(basename=r['basename'],needles=list(r.get('bounded_code_matches',{})))
            for r in assets if r.get('bounded_code_matches')])),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prefix',nargs='+')
    main(parser.parse_args().prefix)
