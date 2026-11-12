"""Replay tab recycling/CDP inspection in an isolated browser with a fake cookie.

Never opens the production profile or contacts ChatGPT. Every fixture URL is
fulfilled locally, and the only cookie value is a public test constant.
"""
import asyncio
import json
from pathlib import Path
import tempfile
import time
from patchright.async_api import async_playwright

ORIGIN = 'https://session-fixture.invalid'
COOKIE_NAME = '__Secure-next-auth.session-token'
COOKIE_VALUE = 'PUBLIC_FAKE_COOKIE_FOR_LOCAL_LIFECYCLE_TEST'


async def main():
    results = []
    with tempfile.TemporaryDirectory(prefix='mg-cookie-fixture-', dir='/tmp') as directory:
        profile = Path(directory).resolve()
        if profile.parent != Path('/tmp') or not profile.name.startswith('mg-cookie-fixture-'):
            raise RuntimeError('Unexpected isolated fixture path')
        async with async_playwright() as driver:
            context = await driver.chromium.launch_persistent_context(str(profile), headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9234'])
            try:
                await context.route('**/*', lambda route: route.fulfill(status=200, content_type='text/html',
                    body='<html><body>Local fake-cookie fixture</body></html>'))
                await context.add_cookies([{'name':COOKIE_NAME,'value':COOKIE_VALUE,'domain':'session-fixture.invalid',
                    'path':'/','expires':time.time()+90*86400,'httpOnly':True,'secure':True,'sameSite':'Lax'}])
                async def observe(stage):
                    cookies = await context.cookies(ORIGIN)
                    found = [c for c in cookies if c['name'] == COOKIE_NAME]
                    results.append({'stage':stage,'fake_cookie_present':len(found)==1,
                        'fake_cookie_value_unchanged':len(found)==1 and found[0]['value']==COOKIE_VALUE,
                        'pages':len(context.pages)})
                await observe('initial_import')
                main_page = context.pages[0]
                await main_page.goto(ORIGIN)
                workers = await asyncio.gather(*(context.new_page() for _ in range(2)))
                await asyncio.gather(*(page.goto(ORIGIN+'/?temporary-chat=true') for page in workers))
                await observe('two_worker_tabs_loaded')
                await context.grant_permissions(['clipboard-read','clipboard-write'])
                await asyncio.gather(*(page.goto('about:blank') for page in workers))
                await observe('two_workers_recycled_to_blank')
                async with async_playwright() as inspection_driver:
                    attached = await inspection_driver.chromium.connect_over_cdp('http://127.0.0.1:9234')
                    await observe('extra_cdp_connection_attached')
                    await attached.close()
                await observe('extra_cdp_connection_disconnected')
                workers += await asyncio.gather(*(context.new_page() for _ in range(2)))
                await asyncio.gather(*(page.goto(ORIGIN) for page in workers))
                await observe('four_worker_tabs_loaded')
                async with async_playwright() as inspection_driver:
                    attached = await inspection_driver.chromium.connect_over_cdp('http://127.0.0.1:9234')
                    inspect_context = attached.contexts[0]
                    fresh = await inspect_context.new_page()
                    await fresh.goto(ORIGIN)
                    await fresh.close()
                    await attached.close()
                await observe('second_inspector_created_and_closed_tab')
                await asyncio.gather(*(page.close() for page in workers[2:]))
                await observe('extra_idle_worker_tabs_closed')
            finally:
                await context.close()
    print(json.dumps({'isolated_profile':True,'real_credentials_used':False,'real_site_requests':False,
        'production_profile_touched':False,'observations':results,
        'all_cookie_checks_passed':all(r['fake_cookie_present'] and r['fake_cookie_value_unchanged'] for r in results)}, indent=2))


asyncio.run(main())
