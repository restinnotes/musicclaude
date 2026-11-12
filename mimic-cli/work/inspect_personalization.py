import asyncio,json
from patchright.async_api import async_playwright
async def main():
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page=next(p for p in browser.contexts[0].pages if p.url.startswith('https://chatgpt.com'))
        await page.get_by_role('button',name='Personalized',exact=True).click()
        await asyncio.sleep(.3)
        print('MENU',json.dumps(await page.locator('[role="menu"]:visible').evaluate_all('els=>els.map(e=>({text:e.innerText,html:e.outerHTML}))'),ensure_ascii=False))
        await browser.close()
asyncio.run(main())
