import asyncio
import json
from patchright.async_api import async_playwright


async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        output = []
        for page in list(browser.contexts[0].pages):
            try:
                state = await page.evaluate('''() => ({
                    body: document.body.innerText.slice(0,1800),
                    controls: [...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width>0).map(e=>({text:e.innerText,aria:e.getAttribute('aria-label'),testid:e.getAttribute('data-testid')}))
                })''')
                state['url'] = page.url
                output.append(state)
            except Exception:
                pass
        print(json.dumps(output, ensure_ascii=False))
        try:
            await browser.close()
        except Exception:
            pass


asyncio.run(main())
