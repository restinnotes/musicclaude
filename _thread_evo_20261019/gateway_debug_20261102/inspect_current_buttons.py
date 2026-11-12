import asyncio,json
from pathlib import Path
from patchright.async_api import async_playwright

async def main():
    async with async_playwright() as runtime:
        browser=await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:continue
            rows=await page.evaluate('''() => [...document.querySelectorAll('main button')].map(b=>({
                label:b.getAttribute('aria-label'),test:b.getAttribute('data-testid'),
                state:b.getAttribute('data-state'),text:b.innerText.slice(0,40),
                visible:b.getBoundingClientRect().height>0,
                parent:b.parentElement.outerHTML.slice(0,700)}))''')
            Path('/app/state/gateway-fix-20261102/current_buttons.json').write_text(json.dumps(rows,indent=2))
            print(json.dumps(rows,indent=2))
        await browser.close()
asyncio.run(main())
