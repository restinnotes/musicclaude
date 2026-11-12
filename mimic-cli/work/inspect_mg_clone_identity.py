"""Read native identity from an idle owned clone; no navigation or request send."""
import argparse
from datetime import datetime, timezone
import json
import sys
from build_mg_storage_pair import OUT, docker
sys.path.insert(0,str(OUT.parents[2]/'cli'))
import mg


def main(condition):
    details=json.loads((OUT/'matched-pair.json').read_text())['clones'][condition]
    mg.CONTAINER=details['container'];mg.API=details['api_url']
    state=mg.http_json('/v1/tabs',mg.read_auth())[1]['concurrency']
    assert state['in_flight']==0 and state['waiting']==0
    code='''import asyncio,json,os
from patchright.async_api import async_playwright
async def run():
 async with async_playwright() as driver:
  browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
  pages=[p for c in browser.contexts for p in c.pages if p.url.startswith('https://chatgpt.com/')]
  if not pages:raise RuntimeError('Owned app page unavailable')
  result=await pages[0].evaluate("""async () => {
    const high = navigator.userAgentData ? await navigator.userAgentData.getHighEntropyValues(
      ['architecture','bitness','platformVersion','fullVersionList','uaFullVersion']) : null;
    return {platform:navigator.platform,userAgent:navigator.userAgent,
      uaDataPlatform:navigator.userAgentData?.platform,
      architecture:high?.architecture,bitness:high?.bitness,
      platformVersion:high?.platformVersion,uaFullVersion:high?.uaFullVersion};
  }""")
  result['native_identity_opt_in']=os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY')=='1'
  print(json.dumps(result))
  await browser.close()
asyncio.run(run())
'''
    identity=json.loads(docker('exec','-w','/app',mg.CONTAINER,'/opt/venv/bin/python','-c',code))
    report=dict(utc=datetime.now(timezone.utc).isoformat(),condition=condition,
        browser_read_only=True,model_sent=False,identity=identity)
    (OUT/('identity-'+condition+'.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('condition',choices=['control','local_storage','native_identity'])
    args=parser.parse_args()
    main(args.condition)
