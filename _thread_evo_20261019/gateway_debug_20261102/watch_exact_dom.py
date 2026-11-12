"""Passive one-second UI state timeline; no text content or model submissions."""
import asyncio
import json
import time
from pathlib import Path
from patchright.async_api import async_playwright
from src.chatgpt.detector import _latest_assistant_turn_snapshot, normalize_assistant_text


async def main():
    dest = Path('/app/state/gateway-fix-20261102/exact-stream/dom-timeline.jsonl')
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for _ in range(600):
            for page in browser.contexts[0].pages:
                if 'chatgpt.com/c/' not in page.url:
                    continue
                try:
                    snapshot = await _latest_assistant_turn_snapshot(page)
                    row = {'epoch': time.time(), 'page': id(page),
                        'signature': snapshot.get('signature'),
                        'characters': len(normalize_assistant_text(snapshot.get('text'))),
                        'copy': snapshot.get('hasCopyButton'), 'stop': snapshot.get('hasStopButton'),
                        'height': snapshot.get('rect', {}).get('height')}
                    with dest.open('a', encoding='utf-8') as handle:
                        handle.write(json.dumps(row) + '\n')
                except Exception:
                    pass
            if dest.with_name('capture.json').exists():
                await asyncio.sleep(20)
                break
            await asyncio.sleep(1)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
