"""Restore the missing session cookie from the authorized original yi source."""
import asyncio
import json
import time
from pathlib import Path
import urllib.request
from patchright.async_api import async_playwright

async def main():
    auth_path = Path('/app/state/mg-yi-cookie-import.json')
    try:
        pool = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/v1/tabs',timeout=5).read())
        if pool['concurrency']['in_flight'] or pool['concurrency'].get('waiting'):
            raise RuntimeError('Active requests prevent session maintenance')
        cookies = json.loads(auth_path.read_text())
        if not cookies or any(not c['name'].startswith('__Secure-next-auth.session-token') or
                c['domain'] not in {'.chatgpt.com','chatgpt.com'} for c in cookies):
            raise RuntimeError('Unexpected original-session import input')
        async with async_playwright() as driver:
            browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
            context = browser.contexts[0]
            before = await context.cookies('https://chatgpt.com/')
            count_before = sum(c['name'].startswith('__Secure-next-auth.session-token') for c in before)
            if count_before:
                raise RuntimeError('Session cookie already exists; inspect before replacing it')
            await context.add_cookies(cookies)
            imported = len(cookies)
            auth_path.unlink()
            del cookies, before
            page = await context.new_page()
            try:
                await page.goto('https://chatgpt.com/',wait_until='domcontentloaded',timeout=45000)
                await page.locator('button[aria-label="Open profile menu"]').wait_for(state='visible',timeout=30000)
                await page.locator('button[aria-label="Temporary chat"]').wait_for(state='visible',timeout=30000)
                await page.reload(wait_until='domcontentloaded')
                await page.locator('button[aria-label="Open profile menu"]').wait_for(state='visible',timeout=30000)
                result = {'timestamp':time.time(),'source':'original yi / Chrome Default',
                    'session_count_before':count_before,'session_count_imported':imported,
                    'fresh_page_authenticated':True,'refresh_authenticated':True,
                    'container_auth_file_deleted':not auth_path.exists(),
                    'profile_replaced':False,'container_restarted':False}
                await page.screenshot(path='/app/state/yi-session-restored.png')
                Path('/app/state/yi-session-restored.json').write_text(json.dumps(result),encoding='utf-8')
                print(json.dumps(result),flush=True)
            finally:
                await page.close()
                await browser.close()
    finally:
        auth_path.unlink(missing_ok=True)

asyncio.run(main())
