"""Read observed script URLs in an idle existing clone; fetch public JS only."""
from datetime import datetime, timezone
import hashlib
import json
import re
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
from build_mg_storage_pair import OUT,ROOT,docker
import sys
sys.path.insert(0,str(ROOT/'cli'))
import mg


def main():
    mg.CONTAINER='yi-mg-clone-20261007';mg.API='http://127.0.0.1:8662'
    state=mg.http_json('/v1/tabs',mg.read_auth())[1]['concurrency']
    assert state['in_flight']==0 and state['waiting']==0
    code='''import asyncio,json
from patchright.async_api import async_playwright
async def main():
 async with async_playwright() as driver:
  browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
  pages=[p for c in browser.contexts for p in c.pages if p.url.startswith('https://chatgpt.com/')]
  if not pages:raise RuntimeError('No existing app page')
  urls=[]
  for page in pages:
   urls.extend(await page.evaluate("""() => {
    const result=Array.from(document.querySelectorAll('script[src]')).map(s=>s.src);
    for (const link of document.querySelectorAll('link[rel="modulepreload"][href]')) result.push(link.href);
    for (const script of document.querySelectorAll('script[type="module"]')) {
      const matches=script.textContent.matchAll(/(?:from\\s*|import\\s*(?:\\(\\s*)?)["']([^"']+\\.js(?:\\?[^"']*)?)["']/g);
      for (const match of matches) result.push(new URL(match[1], document.baseURI).href);
    }
    return result;
  }"""))
  print(json.dumps(urls))
  await browser.close()
asyncio.run(main())
'''
    urls=json.loads(docker('exec','-w','/app',mg.CONTAINER,'/opt/venv/bin/python','-c',code))
    stamp=datetime.now(timezone.utc).strftime('%H%M%S')
    directory=OUT/('public-frontend-'+stamp);directory.mkdir(exist_ok=False)
    evidence=[];total=0
    observed_summary=[dict(host=urlsplit(url).hostname,
        basename=urlsplit(url).path.rsplit('/',1)[-1][:100],
        query_present=bool(urlsplit(url).query)) for url in urls[:32]]
    for url in list(dict.fromkeys(urls))[:32]:
        parsed=urlsplit(url)
        name=parsed.path.rsplit('/',1)[-1]
        if parsed.scheme!='https' or parsed.hostname not in ('cdn.oaistatic.com','chatgpt.com') or parsed.query:
            continue
        if '/assets/' not in parsed.path:continue
        if not re.fullmatch(r'[A-Za-z0-9._-]{1,100}\.js',name):continue
        request=Request(url,headers={'Accept-Encoding':'identity','Accept':'application/javascript'})
        record=dict(basename=name,observed_in_existing_document=True,
            account_cookies_sent=False,body_saved=False)
        try:
            with urlopen(request,timeout=20) as response:
                if urlsplit(response.url).hostname not in ('cdn.oaistatic.com','chatgpt.com'):raise ValueError('Unexpected public host')
                data=response.read(2*1024*1024+1)
                record['http_status']=response.status
            if len(data)>2*1024*1024 or total+len(data)>12*1024*1024:
                record['error']='public_asset_budget';evidence.append(record);continue
            text=data.decode('utf-8')
            (directory/name).write_bytes(data);total+=len(data)
            hits={}
            for needle in ('browser_context','instance_id','chatgpt-last-selected-model-v1',
                'codex.browser.appThemes.v1','browserInstanceId','chatgpt-work-models-v1'):
                matches=list(re.finditer(re.escape(needle),text))
                if matches:
                    hits[needle]=[text[max(0,m.start()-160):m.end()+200] for m in matches[:3]]
            record.update(body_saved=True,sha256=hashlib.sha256(data).hexdigest(),
                bytes=len(data),bounded_code_matches=hits)
        except Exception as error:
            record['error_class']=type(error).__name__
        evidence.append(record)
    report=dict(utc=datetime.now(timezone.utc).isoformat(),existing_idle_clone_read_only=True,
        browser_navigation=False,model_post=False,public_assets_only=True,
        total_downloaded_bytes=total,assets=evidence)
    report['observed_script_url_summary']=observed_summary
    (directory/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(directory=str(directory),total_bytes=total,
        matches=[dict(basename=r['basename'],needles=list(r.get('bounded_code_matches',{})))
            for r in evidence if r.get('bounded_code_matches')],asset_count=len(evidence),
            observed_script_urls=observed_summary)))


if __name__=='__main__':
    main()
