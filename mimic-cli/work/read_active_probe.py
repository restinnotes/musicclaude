"""Inspect existing pages without navigation, prompting, or cookie mutation."""
import asyncio
import json
from patchright.async_api import async_playwright
from src.chatgpt.detector import _conversation_snapshot

async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        rows = []
        for context in browser.contexts:
            for page in context.pages:
                if 'chatgpt.com' not in page.url:
                    continue
                snapshot = await _conversation_snapshot(page)
                latest = snapshot.get('latestAssistant') or {}
                rows.append({'assistant_count': snapshot.get('assistantCount'),
                    'user_count': snapshot.get('userCount'), 'stop_visible': snapshot.get('hasStopButton'),
                    'latest_text_length': latest.get('textLength'), 'latest_has_copy': latest.get('hasCopyButton'),
                    'temporary_url_flag': 'temporary-chat=true' in page.url})
        print(json.dumps(rows))
        await browser.close()

asyncio.run(main())
