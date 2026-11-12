import asyncio,json
from patchright.async_api import async_playwright
from src.chatgpt.client import ChatGPTClient
async def main():
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page=next(p for p in browser.contexts[0].pages if p.url.startswith('https://chatgpt.com'))
        await page.get_by_role('menuitemradio',name='Unpersonalized',exact=False).click()
        await asyncio.sleep(.3)
        await page.get_by_role('button',name='Unpersonalized',exact=True).click()
        row=page.get_by_role('menuitemradio',name='Unpersonalized',exact=False)
        print('PERSONALIZATION',json.dumps({'label':await row.inner_text(),'checked':await row.get_attribute('aria-checked')}))
        await page.keyboard.press('Escape')
        client=ChatGPTClient(page)
        await client.ensure_model('gpt-5.6-sol',reasoning_effort='xhigh')
        print('MODEL',json.dumps(client._last_yi_selection_evidence))
        await page.get_by_role('button',name='Select ChatGPT model',exact=True).click()
        print('MODEL_MENU',json.dumps(await page.locator('[role="menu"]:visible').evaluate_all('els=>els.map(e=>({text:e.innerText,controls:Array.from(e.querySelectorAll("[role=slider],[role=menuitemradio]")).map(s=>({text:s.innerText,role:s.getAttribute("role"),checked:s.getAttribute("aria-checked"),now:s.getAttribute("aria-valuenow"),min:s.getAttribute("aria-valuemin"),max:s.getAttribute("aria-valuemax")}))}))')))
        await page.keyboard.press('Escape')
        await page.screenshot(path='/app/state/mg-standard-inspect.png')
        await browser.close()
asyncio.run(main())
