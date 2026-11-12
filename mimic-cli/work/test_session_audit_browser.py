"""Isolated incognito context, intercepted fake responses, no real credentials."""
import asyncio
import json
from pathlib import Path
from patchright.async_api import async_playwright
from src import session_observer as audit

async def main():
    events=[]
    original_emit=audit.emit
    audit.emit=lambda event,**fields:events.append({'event':event,**fields})
    report={'test':'isolated intercepted response integration','real_network_requests':0}
    async with async_playwright() as p:
        browser=await p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        real=browser.contexts[0]
        before=sum(c['name'].startswith(audit.AUTH_PREFIX) for c in await real.cookies('https://chatgpt.com/'))
        context=await browser.new_context()
        phase=0
        async def route_response(route):
            if phase==0:
                header=audit.AUTH_PREFIX+'=SYNTHETIC_FIXTURE_ONLY; Secure; HttpOnly; Path=/; Max-Age=3600'
                status=200
            elif phase==1:
                header=audit.AUTH_PREFIX+'=; Secure; HttpOnly; Path=/; Max-Age=0'
                status=200
            else:
                header=None
                status=401
            headers={'content-type':'text/html'}
            if header is not None:
                headers['set-cookie']=header
            await route.fulfill(status=status,headers=headers,body='<html><body>Isolated audit fixture</body></html>')
        await context.route('**/*',route_response)
        audit.attach_context_audit(context)
        page=await context.new_page()
        try:
            await page.goto('https://chatgpt.com/',wait_until='load')
            first=await audit.request_auth_snapshot(page)
            assert first['session_cookie_count']==1
            phase=1
            await page.reload(wait_until='load')
            second=await audit.request_auth_snapshot(page)
            assert second['session_cookie_count']==0
            phase=2
            await page.reload(wait_until='load')
            for _ in range(20):
                if any(e['event']=='http_auth_or_access_error' for e in events):
                    break
                await asyncio.sleep(.05)
            deleted=any(e['event']=='auth_cookie_response' and e.get('deletion_directive') for e in events)
            denied=any(e['event']=='http_auth_or_access_error' and e.get('status')==401 for e in events)
            assert deleted and denied
            assert 'SYNTHETIC_FIXTURE_ONLY' not in json.dumps(events)
            report.update({'auth_before_fake_deletion':first['session_cookie_count'],
              'auth_after_fake_deletion':second['session_cookie_count'],
              'browser_response_deletion_captured':deleted,'browser_401_captured':denied,
              'cookie_value_absent_from_events':True,'events':events.copy()})
        finally:
            await context.close()
            after=sum(c['name'].startswith(audit.AUTH_PREFIX) for c in await real.cookies('https://chatgpt.com/'))
            report['real_profile_session_count_before']=before
            report['real_profile_session_count_after']=after
            assert before==after
            await browser.close()
            audit.emit=original_emit
    Path('/app/state/yi-session-audit-integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

asyncio.run(main())
