"""Diagnostic clone only: align oai-did, preserving every login cookie."""
import asyncio
import hashlib
import json
from pathlib import Path
import urllib.request
from patchright.async_api import async_playwright


async def main():
    source = Path('/app/state/diagnostic-device-import.private.json')
    try:
        activity = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/v1/tabs', timeout=5).read())
        assert activity['concurrency']['in_flight'] == 0 and activity['concurrency']['waiting'] == 0
        cookies = json.loads(source.read_text())
        assert len(cookies) == 1 and cookies[0]['name'] == 'oai-did' and cookies[0]['domain'] == '.chatgpt.com'
        async with async_playwright() as driver:
            browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
            context = browser.contexts[0]
            before = await context.cookies('https://chatgpt.com/')
            auth_before = {c['name']: c['value'] for c in before if c['name'].startswith('__Secure-next-auth.session-token')}
            assert auth_before, 'Existing login must remain present'
            device_before = next((c for c in before if c['name'] == 'oai-did'), None)
            await context.add_cookies(cookies)
            after = await context.cookies('https://chatgpt.com/')
            auth_after = {c['name']: c['value'] for c in after if c['name'].startswith('__Secure-next-auth.session-token')}
            assert auth_after == auth_before, 'Device alignment must not change login cookies'
            device_after = next(c for c in after if c['name'] == 'oai-did')
            assert device_after['value'] == cookies[0]['value']
            result = {'cookie_name': 'oai-did', 'login_cookies_unchanged': True,
                'before_sha256': hashlib.sha256(device_before['value'].encode()).hexdigest() if device_before else None,
                'after_sha256': hashlib.sha256(device_after['value'].encode()).hexdigest(),
                'cookie_values_saved_in_result': False, 'source_file_removed': True}
            source.unlink()
            await browser.close()
            print(json.dumps(result))
    finally:
        source.unlink(missing_ok=True)


asyncio.run(main())
