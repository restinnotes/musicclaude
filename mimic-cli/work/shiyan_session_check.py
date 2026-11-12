"""Check the existing Shiyan browser without exposing authentication values."""
import asyncio
import json
import time
import sys
from pathlib import Path
from patchright.async_api import async_playwright

async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        cookies = await context.cookies('https://chatgpt.com/')
        sessions = [c for c in cookies if c['name'].startswith('__Secure-next-auth.session-token')]
        result = {'timestamp': time.time(), 'session_cookie_count': len(sessions),
                  'session_expiries': [c.get('expires') for c in sessions]}
        page = await context.new_page()
        try:
            await page.goto('https://chatgpt.com/', wait_until='domcontentloaded', timeout=45000)
            for _ in range(60):
                profile = page.locator('button[aria-label="Open profile menu"]:visible')
                login = page.get_by_role('button', name='Log in', exact=True)
                if await profile.count() or await login.count():
                    break
                await asyncio.sleep(.5)
            result.update({'fresh_page_authenticated': bool(await profile.count()),
                'login_control_present': bool(await login.count()),
                'model_label': await page.locator('button[aria-label="Select ChatGPT model"]').inner_text()
                    if await page.locator('button[aria-label="Select ChatGPT model"]').count() else None,
                'challenge': 'Just a moment' in await page.title()})
            await page.screenshot(path='/app/state/shiyan-login-check.png')
        finally:
            await page.close()
            await browser.close()
        tag = sys.argv[1] if len(sys.argv) > 1 else 'latest'
        if not tag.replace('-', '').isalnum():
            raise ValueError('Invalid observation tag')
        Path('/app/state/shiyan-login-' + tag + '.json').write_text(json.dumps(result), encoding='utf-8')
        print(json.dumps(result), flush=True)

asyncio.run(main())
