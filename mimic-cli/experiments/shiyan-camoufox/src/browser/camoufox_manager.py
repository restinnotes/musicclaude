"""Isolated Camoufox browser for the user-authorized same-account comparison."""
import json
import time
from pathlib import Path
from camoufox.async_api import AsyncCamoufox
from src.browser.chromium_manager import BrowserManager as ChromiumManager
from src.config import Config
from src.log import setup_logging

log = setup_logging('camoufox_browser')


class BrowserManager(ChromiumManager):
    async def start(self):
        Config.ensure_dirs()
        self._camoufox_cm = AsyncCamoufox(
            headless=False, humanize=True, geoip=True, locale='en-US',
            block_webrtc=True, os='windows', persistent_context=True,
            user_data_dir=str(Config.BROWSER_DATA_DIR), window=(1366, 768),
            i_know_what_im_doing=True,
        )
        self._context = await self._camoufox_cm.__aenter__()
        marker = Config.BROWSER_DATA_DIR / '.shiyan-imported'
        import_path = Path('/imports/shiyan-transfer/cookies.json')
        if not marker.exists():
            cookies = json.loads(import_path.read_text(encoding='utf-8'))
            allowed = {'name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure', 'sameSite'}
            cookies = [{k: v for k, v in cookie.items() if k in allowed}
                       for cookie in cookies
                       if cookie.get('domain', '').lstrip('.').endswith(('chatgpt.com', 'openai.com'))
                       and (cookie.get('expires', -1) <= 0 or cookie['expires'] > time.time())]
            if not any(c['name'].startswith('__Secure-next-auth.session-token') for c in cookies):
                raise RuntimeError('Authorized Shiyan session cookies are missing; no navigation performed')
            await self._context.add_cookies(cookies)
            marker.write_text('Imported authorized Shiyan cookies before first navigation.\n', encoding='utf-8')
            marker.chmod(0o600)
            # Record counts and configuration only, never cookie values or public IP.
            evidence = {'imported_cookie_count': len(cookies),
                        'session_cookie_count': sum(c['name'].startswith('__Secure-next-auth.session-token') for c in cookies),
                        'browser': 'Camoufox 152.0.4-beta.31 / Gecko',
                        'os': 'windows', 'humanize': True, 'geoip': True,
                        'locale': 'en-US', 'block_webrtc': True,
                        'proxy': 'none; same Docker network exit as baseline',
                        'imported_at': time.time()}
            Path('/app/state/cookie-import-evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
        self._page = self._context.pages[0] if self._context.pages else await self._context.new_page()
        return self._page

    async def apply_stealth_patches(self):
        # Camoufox controls fingerprint generation; Chrome-specific JS patches
        # would introduce contradictory browser properties.
        log.info('Using native Camoufox configuration; no Chromium JS stealth overlay')

    async def close(self):
        try:
            if getattr(self, '_camoufox_cm', None):
                await self._camoufox_cm.__aexit__(None, None, None)
        finally:
            self._context = self._page = self._playwright = None
