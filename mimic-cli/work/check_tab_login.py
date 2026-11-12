import asyncio
import json
from patchright.async_api import async_playwright


async def describe(page):
    return await page.evaluate('''() => ({
        login: [...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width>0 && /^Log in$/.test(e.innerText)).length,
        temporary: !!document.querySelector('button[aria-label="Temporary chat"]'),
        title: document.title,
        model: document.querySelector('button[aria-label="Select ChatGPT model"]')?.innerText || null,
        text_excerpt: document.body.innerText.slice(-450)
    })''')


async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        control = context.pages[0]
        created = []
        try:
            page = await context.new_page()
            created.append(page)
            await page.goto('https://chatgpt.com/', wait_until='domcontentloaded')
            await asyncio.sleep(5)
            print(json.dumps({'kind': 'new_page', 'state': await describe(page)}, ensure_ascii=False), flush=True)
            async with control.expect_popup() as event:
                await control.evaluate("window.open('https://chatgpt.com/', '_blank')")
            popup = await event.value
            created.append(popup)
            await popup.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(5)
            print(json.dumps({'kind': 'popup', 'state': await describe(popup)}, ensure_ascii=False), flush=True)
        finally:
            for page in created:
                await page.close()
            await browser.close()


asyncio.run(main())
