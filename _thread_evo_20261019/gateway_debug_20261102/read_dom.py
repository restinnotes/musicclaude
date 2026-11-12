"""Read assistant markup only; never navigate, submit, or alter the current task."""
import asyncio
import json
from pathlib import Path
from patchright.async_api import async_playwright

async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        rows = []
        for context in browser.contexts:
            for page in context.pages:
                if 'chatgpt.com/c/' not in page.url:
                    continue
                rows.append(await page.evaluate('''() => {
                    const roots = [...document.querySelectorAll('[data-content-search-unit-key$=":assistant"]')];
                    const root = roots.at(-1);
                    if (!root) return {found:false};
                    const parent = root.parentElement;
                    return {found:true, stop:!!document.querySelector('button[data-testid="stop-button"]'),
                        inner:root.innerText, text:root.textContent, html:root.outerHTML,
                        parent:parent.outerHTML.slice(-15000)};
                }''', isolated_context=True))
        dest=Path('/app/state/gateway-fix-20261102')
        dest.mkdir(exist_ok=True)
        (dest/'live_dom.json').write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
        print(json.dumps([{'found':r.get('found'),'stop':r.get('stop'),
            'inner_chars':len(r.get('inner','')),'text_chars':len(r.get('text','')),
            'html_chars':len(r.get('html',''))} for r in rows]))
        await browser.close()

asyncio.run(main())
