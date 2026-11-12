"""Restore only the missing session cookie from the confirmed original yi source."""
import asyncio
import json
from pathlib import Path
import urllib.request
from patchright.async_api import async_playwright


async def main():
    auth_path = Path('/app/state/mg-session-repair.json')
    try:
        state = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/v1/tabs', timeout=5).read())
        if state['concurrency']['in_flight']:
            raise RuntimeError('Active requests prevent session maintenance')
        cookies = json.loads(auth_path.read_text())
        if not cookies or any(not c['name'].startswith('__Secure-next-auth.session-token') or c['domain'] != '.chatgpt.com' for c in cookies):
            raise RuntimeError('Unexpected cookie repair input')
        async with async_playwright() as driver:
            browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
            context = browser.contexts[0]
            before = await context.cookies('https://chatgpt.com/')
            count_before = sum(c['name'].startswith('__Secure-next-auth.session-token') for c in before)
            if count_before:
                raise RuntimeError('Session cookie already exists; refusing to overwrite it')
            await context.add_cookies(cookies)
            auth_path.unlink()
            del cookies
            page = context.pages[-1]
            await page.goto('https://chatgpt.com/', wait_until='domcontentloaded', timeout=45000)
            await page.locator('button[aria-label="Open profile menu"]').wait_for(state='visible', timeout=30000)
            await page.locator('button[aria-label="Temporary chat"]').wait_for(state='visible', timeout=30000)
            result = {'session_cookie_count_before': count_before, 'session_cookie_count_restored': 1,
                'profile_menu_verified': True, 'temporary_control_verified': True,
                'container_auth_file_deleted': not auth_path.exists(), 'credential_values_printed': False,
                'profile_replaced': False}
            print(json.dumps(result), flush=True)
            await page.goto('about:blank')
            await browser.close()
    finally:
        auth_path.unlink(missing_ok=True)


asyncio.run(main())
