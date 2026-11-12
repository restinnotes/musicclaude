import asyncio,json
from patchright.async_api import async_playwright
async def main():
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page=next(p for p in browser.contexts[0].pages if p.url.startswith('https://chatgpt.com'))
        # already temporary
        await asyncio.sleep(1)
        print('PATH',page.url.split('chatgpt.com')[-1])
        print('BODY',(await page.locator('body').inner_text())[-2500:])
        print('CONTROLS',json.dumps(await page.locator('button,[role="switch"]').evaluate_all('''els=>els.filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height).filter(e=>e.getBoundingClientRect().left>400).map(e=>({text:e.innerText,aria:e.getAttribute('aria-label'),role:e.getAttribute('role'),checked:e.getAttribute('aria-checked'),pressed:e.getAttribute('aria-pressed'),html:e.outerHTML.slice(0,2000)}))'''),ensure_ascii=False))
        await page.screenshot(path='/app/state/mg-temporary-inspect.png')
        await browser.close()
asyncio.run(main())

