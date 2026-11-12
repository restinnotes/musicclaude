import asyncio,json,urllib.request
from src.config import Config
from patchright.async_api import async_playwright
async def main():
    req=urllib.request.Request('http://127.0.0.1:8000/v1/models',headers={'Authorization':'Bearer '+Config.API_TOKEN})
    with urllib.request.urlopen(req,timeout=60) as response:
        print('MODELS',response.read().decode())
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for index,page in enumerate(browser.contexts[0].pages):
            if not page.url.startswith('https://chatgpt.com'): continue
            controls=await page.locator('button,[role="switch"],[role="menuitem"],[role="menuitemradio"]').evaluate_all('''els=>els.filter(e=>e.getBoundingClientRect().width&&e.getBoundingClientRect().height).map(e=>({text:e.innerText.slice(0,160),aria:e.getAttribute('aria-label'),role:e.getAttribute('role'),checked:e.getAttribute('aria-checked'),pressed:e.getAttribute('aria-pressed'),testid:e.getAttribute('data-testid'),title:e.getAttribute('title')}))''')
            print('PAGE',json.dumps({'index':index,'path':page.url.split('chatgpt.com')[-1],'controls':controls},ensure_ascii=False))
        await browser.close()
asyncio.run(main())
