"""Passive CDP exception evidence; never submits, navigates or changes a request."""
import asyncio
import json
import time
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    dest = Path('/app/state/gateway-fix-20261102/renderer_errors.jsonl')
    sessions = []
    seen = set()
    def record(event, **fields):
        with dest.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'time': time.time(), 'event': event, **fields}, ensure_ascii=False) + '\n')
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for _ in range(150):
            for context in browser.contexts:
                for page in [target for parent in context.pages for target in [parent, *parent.frames[1:]]]:
                    if page in seen or not any(host in page.url for host in ('chatgpt.com', 'cdn.platform.openai.com')):
                        continue
                    seen.add(page)
                    session = await context.new_cdp_session(page)
                    sessions.append(session)
                    session.on('Runtime.exceptionThrown', lambda event: record('exception', details=event.get('exceptionDetails')))
                    session.on('Runtime.consoleAPICalled', lambda event: record('console_error', args=event.get('args')) if event.get('type') == 'error' else None)
                    await session.send('Runtime.enable')
                    record('attached', page_url=page.url)
            await asyncio.sleep(3)
        for session in sessions:
            await session.detach()
        await browser.close()


asyncio.run(main())
