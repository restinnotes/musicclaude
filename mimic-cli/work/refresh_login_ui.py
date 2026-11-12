"""Try normal Log in navigation using the existing browser session; no credential reads."""
import asyncio
import json
from urllib.parse import urlparse
from patchright.async_api import async_playwright


async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.pages[1]
        await page.bring_to_front()
        await page.goto('https://chatgpt.com/', wait_until='domcontentloaded')
        login = page.get_by_role('button', name='Log in', exact=True).first
        await login.wait_for(state='visible', timeout=15000)
        await login.click()
        await asyncio.sleep(12)
        data = await page.evaluate('''() => ({
            title: document.title,
            input_types: [...document.querySelectorAll('input')].map(e=>({type:e.type,name:e.name})),
            button_names: [...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.getAttribute('aria-label') || e.innerText),
            temporary: !!document.querySelector('button[aria-label="Temporary chat"]')
        })''')
        parsed = urlparse(page.url)
        data['page'] = parsed.scheme + '://' + parsed.netloc + parsed.path
        print(json.dumps(data, ensure_ascii=False))
        await browser.close()


asyncio.run(main())
