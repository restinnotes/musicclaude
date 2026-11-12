"""User-authorized native cookie bundle into an idle diagnostic or original browser."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import urllib.request
from patchright.async_api import async_playwright
from src.cookie_capacity import backup_encrypted_cookie_database, site_cookies
from src.config import Config

async def main():
    role = sys.argv[1] if len(sys.argv) > 1 else 'diagnostic'
    assert role in ('diagnostic', 'production')
    source = Path('/app/state/native-cookie-import.private.json')
    try:
        activity = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/v1/tabs', timeout=5).read())
        assert not activity['concurrency']['in_flight'] and not activity['concurrency']['waiting']
        cookies = json.loads(source.read_text())
        assert 1 <= len(cookies) <= 100
        assert all(c['domain'].lstrip('.') == 'chatgpt.com' for c in cookies)
        native_auth = [c for c in cookies if c['name'].startswith('__Secure-next-auth.session-token')]
        assert native_auth
        async with async_playwright() as driver:
            browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
            try:
                context = browser.contexts[0]
                before = await site_cookies(context)
                identities = lambda items: {(c['name'], c['domain'], c['path']) for c in items}
                before_values = {(c['name'], c['domain'], c['path']): c['value'] for c in before}
                imported_changes = [{'name': c['name'], 'domain': c['domain'], 'path': c['path'],
                    'identity_previously_present': (c['name'], c['domain'], c['path']) in before_values,
                    'value_equal_before_import': before_values.get((c['name'], c['domain'], c['path'])) == c['value']}
                    for c in cookies]
                assert len(identities(before) | identities(cookies)) < 160, 'Import would approach cookie capacity'
                backup = backup_encrypted_cookie_database(Config.BROWSER_DATA_DIR)
                await context.add_cookies(cookies)
                after = await site_cookies(context)
                values = {(c['name'], c['domain'], c['path']): c['value'] for c in after}
                assert all(values[(c['name'], c['domain'], c['path'])] == c['value'] for c in native_auth)
                result = {'utc': datetime.now(timezone.utc).isoformat(), 'native_cookie_count_imported': len(cookies),
                    'destination_role': role,
                    'native_login_cookie_import_verified': True, 'site_cookie_count_before': len(before),
                    'site_cookie_count_after': len(after), 'encrypted_backup': backup,
                    'cookie_values_saved_in_result': False, 'source_file_removed': True,
                    'imported_cookie_changes': imported_changes,
                    'original_container_profile_modified': role == 'production', 'native_chrome_modified': False}
                source.unlink()
                print(json.dumps(result))
            finally:
                await browser.close()
    finally:
        source.unlink(missing_ok=True)

asyncio.run(main())
