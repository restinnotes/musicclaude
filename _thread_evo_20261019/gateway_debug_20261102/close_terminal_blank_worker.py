"""Release only the diagnosed completed blank worker, without resubmission."""
import asyncio
from patchright.async_api import async_playwright
from src.chatgpt.detector import _latest_assistant_turn_snapshot, normalize_assistant_text, capture_response_diagnostics


async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        targets = [p for p in browser.contexts[0].pages if 'chatgpt.com/c/' in p.url]
        assert len(targets) == 1, 'Do not touch other requests'
        page = targets[0]
        snapshot = await _latest_assistant_turn_snapshot(page)
        assert not snapshot.get('hasStopButton') and not snapshot.get('hasCopyButton')
        assert not normalize_assistant_text(snapshot.get('text'))
        await capture_response_diagnostics(page, 'confirmed-terminal-blank-manual-release',
            extra={'terminal_stream_utc':'2026-11-02T23:31:21.985620+00:00',
                   'renderer_source_is_empty_return_null':True,
                   'release_reason':'completed empty body; old wait would consume full 30 minute budget'})
        await page.close()
        print('RELEASED_ONLY_TERMINAL_BLANK_WORKER')
        await browser.close()


asyncio.run(main())
