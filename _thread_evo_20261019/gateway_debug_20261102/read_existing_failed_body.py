"""Read only the browser's already completed resource; no HTTP re-fetch."""
import asyncio
import base64
import json
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    root = Path('/app/state/gateway-fix-20261102/existing-failure')
    root.mkdir(exist_ok=True)
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:
                continue
            session = await page.context.new_cdp_session(page)
            try:
                body = await session.send('Network.getResponseBody', {'requestId': '2116.630'})
                content = body['body']
                raw = base64.b64decode(content) if body.get('base64Encoded') else content.encode()
                (root / 'response.sse').write_bytes(raw)
                print('EXISTING_BODY_BYTES', len(raw))
            except Exception as error:
                print('BODY_UNAVAILABLE', type(error).__name__)
            finally:
                await session.detach()
        await browser.close()


asyncio.run(main())
