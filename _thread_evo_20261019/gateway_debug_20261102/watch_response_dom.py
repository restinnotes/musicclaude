"""Bounded passive sampling of the one existing worker, no submission/navigation."""
import asyncio,json,time
from pathlib import Path
from patchright.async_api import async_playwright
from src.chatgpt.detector import _conversation_snapshot

async def main():
    root=Path('/app/state/gateway-fix-20261102/dom-watch')
    root.mkdir(exist_ok=True)
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for n in range(25):
            pages=[p for c in browser.contexts for p in c.pages if 'chatgpt.com/c/' in p.url]
            if not pages:break
            for p in pages:
                snapshot=await _conversation_snapshot(p)
                a=snapshot.get('latestAssistant') or {}
                state=await p.evaluate('''() => {
                    const root=document.querySelector('[data-content-search-unit-key$=":assistant"]');
                    return {assistant:root?.outerHTML, parent:root?.parentElement?.outerHTML,
                        buttons:[...document.querySelectorAll('button')].map(b=>({aria:b.getAttribute('aria-label'),testid:b.getAttribute('data-testid'),text:b.innerText.slice(0,50)}))};
                }''',isolated_context=True)
                state.update(time=time.time(),stop=snapshot.get('hasStopButton'),copy=a.get('hasCopyButton'),text=a.get('text'))
                (root/f'{n:02d}.json').write_text(json.dumps(state,ensure_ascii=False),encoding='utf-8')
                print(json.dumps({'n':n,'stop':state['stop'],'copy':state['copy'],'chars':len(state.get('text') or '')}),flush=True)
            await asyncio.sleep(3)
        await browser.close()

asyncio.run(main())
