import asyncio
import json
from patchright.async_api import async_playwright
from src.chatgpt.client import ChatGPTClient

async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page = await browser.contexts[0].new_page()
        try:
            await page.goto('https://chatgpt.com/', wait_until='domcontentloaded')
            client = ChatGPTClient(page)
            try:
                await client.ensure_model('gpt-5.6-sol', reasoning_effort='xhigh')
                print(json.dumps({'selection': client._last_yi_selection_evidence}))
            except Exception as exc:
                print(json.dumps({'exception_class': type(exc).__name__,
                    'static_policy_error': str(exc) if str(exc).startswith('yi ') else None}))
            picker = page.locator("button[aria-label='Select ChatGPT model']:visible")
            if not await page.locator('[role="menu"]:visible').count():
                await picker.click()
            print(json.dumps(await page.locator('[role="menu"]:visible').evaluate_all('''els=>els.map(e=>({text:e.innerText,
                controls:[...e.querySelectorAll('[role=slider],[role=menuitemradio]')].map(s=>({text:s.innerText,
                checked:s.getAttribute('aria-checked'),now:s.getAttribute('aria-valuenow'),
                min:s.getAttribute('aria-valuemin'),max:s.getAttribute('aria-valuemax')}))}))''')))
            await page.screenshot(path='/app/state/shiyan-effort.png')
        finally:
            await page.close()
            await browser.close()

asyncio.run(main())
