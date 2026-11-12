"""Reproduce Chromium cookie eviction using only public fake cookies."""
import asyncio
import json
import tempfile
import time
from pathlib import Path
from patchright.async_api import async_playwright
from src.cookie_capacity import ensure_cookie_headroom, retire_temporary_conversation_cookies

DOMAIN = 'capacity-fixture.invalid'
AUTH = '__Secure-next-auth.session-token'


async def main():
    rows = []
    with tempfile.TemporaryDirectory(prefix='mg-cookie-capacity-', dir='/tmp') as directory:
        async with async_playwright() as driver:
            context = await driver.chromium.launch_persistent_context(directory, headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage'])
            try:
                def cookie(name):
                    return {'name': name, 'value': 'PUBLIC_FAKE_VALUE', 'domain': DOMAIN, 'path': '/',
                        'expires': time.time() + 86400, 'httpOnly': True, 'secure': True, 'sameSite': 'Lax'}
                await context.add_cookies([cookie(AUTH)])
                for index in range(181):
                    await context.add_cookies([cookie('conv_key_fixture_' + str(index))])
                    if index in (177, 178, 179, 180):
                        cookies = await context.cookies('https://' + DOMAIN)
                        rows.append({'added_conversation_cookies': index + 1, 'remaining_cookies': len(cookies),
                            'fake_auth_cookie_present': any(c['name'] == AUTH for c in cookies)})
                # The second scenario contains no real data and never navigates
                # to the real site. Test exact targeted deletion in Chromium.
                await context.clear_cookies()
                def chat_cookie(name):
                    result = cookie(name)
                    result['domain'] = 'chatgpt.com'
                    return result
                await context.add_cookies([chat_cookie(AUTH)])
                for index in range(80):
                    guid = f'{index:08x}-1111-1111-1111-111111111111'
                    await context.add_cookies([chat_cookie('conv_key_' + guid), chat_cookie('history_off_' + guid)])
                retention = await ensure_cookie_headroom(context, directory)
                count = retention['cookie_count']
                for index in range(100):
                    guid = f'{index + 1000:08x}-2222-2222-2222-222222222222'
                    await context.add_cookies([chat_cookie('conv_key_' + guid), chat_cookie('history_off_' + guid)])
                    await retire_temporary_conversation_cookies(context, guid)
                    actual = await context.cookies('https://chatgpt.com/')
                    assert len(actual) == count
                    assert any(c['name'] == AUTH for c in actual)
                retention.update(fake_auth_cookie_preserved_after_100_rounds=True, repeated_retirement_count=100)
                for wave in range(50):
                    guids = [f'{10000 + wave * 8 + index:08x}-3333-3333-3333-333333333333' for index in range(8)]
                    await asyncio.gather(*(context.add_cookies([chat_cookie('conv_key_' + guid),
                        chat_cookie('history_off_' + guid)]) for guid in guids))
                    peak = await context.cookies('https://chatgpt.com/')
                    assert len(peak) == count + 16
                    assert any(c['name'] == AUTH for c in peak)
                    # Real worker recycling is serialized by browser_ui_lock.
                    for guid in guids:
                        await retire_temporary_conversation_cookies(context, guid)
                    actual = await context.cookies('https://chatgpt.com/')
                    assert len(actual) == count and any(c['name'] == AUTH for c in actual)
                retention.update(eight_concurrent_cookie_creations_per_wave=8,
                    concurrent_waves=50, concurrent_peak_cookie_count=count + 16,
                    fake_auth_cookie_preserved_after_concurrent_waves=True)
            finally:
                await context.close()
    assert rows[1]['remaining_cookies'] == 180 and rows[1]['fake_auth_cookie_present']
    assert rows[2]['remaining_cookies'] == 150 and not rows[2]['fake_auth_cookie_present']
    print(json.dumps({'real_site_contacted': False, 'real_credentials_used': False,
        'production_profile_touched': False, 'observations': rows, 'eviction_reproduced': True,
        'retention_validation': retention}, indent=2))


asyncio.run(main())
