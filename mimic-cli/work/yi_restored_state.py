"""Capture the restored yi standard UI without sending another prompt."""
import asyncio
import json
from pathlib import Path
from patchright.async_api import async_playwright
from src.chatgpt.client import ChatGPTClient

async def main():
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        page=await browser.contexts[0].new_page()
        try:
            client=ChatGPTClient(page)
            await client.prepare_standard_chat()
            evidence=client._standard_evidence
            Path('/app/state/yi-restored-standard-ui.json').write_text(json.dumps(evidence),encoding='utf-8')
            await page.screenshot(path='/app/state/yi-restored-standard-ui.png')
            print(json.dumps({'temporary':evidence['temporary_chat']['verified'],
                'unpersonalized':evidence['non_personalized']['verified'],
                'actual_effort':evidence['model']['selected_effort'],'model':evidence['model']['model']}))
        finally:
            await page.close()
            await browser.close()

asyncio.run(main())
