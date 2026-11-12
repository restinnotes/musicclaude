"""Read only a known research request's page; no navigation or actions."""
import asyncio,json,sys
from patchright.async_api import async_playwright
async def main():
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            text=await page.locator('body').inner_text()
            if sys.argv[1] in text:
                buttons=await page.evaluate('''() => [...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width>0 && e.getBoundingClientRect().height>0 && /stop|停止|skip|跳过/i.test((e.getAttribute('aria-label')||'')+' '+e.innerText+' '+(e.getAttribute('data-testid')||''))).map(e=>({label:e.getAttribute('aria-label'),text:e.innerText,testid:e.getAttribute('data-testid')}))''')
                print(json.dumps({'job_id':sys.argv[1],'tail':text[-2500:],'stop_buttons':buttons},ensure_ascii=False))
asyncio.run(main())
