import asyncio
import json
from patchright.async_api import async_playwright
from src.chatgpt.detector import _latest_assistant_turn_snapshot, normalize_assistant_text


async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:
                continue
            snapshot = await _latest_assistant_turn_snapshot(page)
            print(json.dumps({'characters': len(normalize_assistant_text(snapshot.get('text'))),
                'stop': snapshot.get('hasStopButton'), 'copy': snapshot.get('hasCopyButton')}))
        await browser.close()


asyncio.run(main())
