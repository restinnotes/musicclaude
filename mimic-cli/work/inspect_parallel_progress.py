import asyncio
import json
from patchright.async_api import async_playwright
from src.chatgpt.detector import _latest_assistant_turn_snapshot


async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        results = []
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:
                continue
            result = await page.evaluate('''() => ({
                stop: !!document.querySelector('button[data-testid="stop-button"]'),
                assistant_chars: [...document.querySelectorAll('[data-message-author-role="assistant"]')].map(e=>e.innerText.length),
                body_tail: document.body.innerText.slice(-180)
            })''')
            result['thread'] = page.url.split('/c/')[1].split('?')[0]
            snapshot = await _latest_assistant_turn_snapshot(page)
            result['completion_signals'] = {k: snapshot.get(k) for k in ['hasCopyButton','hasStopButton','textLength']}
            result.pop('body_tail', None)
            results.append(result)
        print(json.dumps(results, ensure_ascii=False))
        await browser.close()


asyncio.run(main())
