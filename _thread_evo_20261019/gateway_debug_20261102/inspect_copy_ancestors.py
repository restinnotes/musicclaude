"""Record copy layout boundaries, no message text."""
import asyncio,json
from pathlib import Path
from patchright.async_api import async_playwright

async def main():
    async with async_playwright() as runtime:
        browser=await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:continue
            row=await page.evaluate('''() => {
                const root=[...document.querySelectorAll('[data-content-search-unit-key$=":assistant"]')].at(-1);
                if(!root)return {found:false};
                const rows=[];let p=root;
                for(let n=0;p&&n<14;n++,p=p.parentElement){
                    rows.push({n,tag:p.tagName,attributes:[...p.attributes].filter(a=>a.name.startsWith('data-')).map(a=>[a.name,a.value]),
                        units:[...p.querySelectorAll('[data-content-search-unit-key]')].map(x=>({key:x.getAttribute('data-content-search-unit-key'),after:!!(root.compareDocumentPosition(x)&Node.DOCUMENT_POSITION_FOLLOWING)})),
                        buttons:[...p.querySelectorAll('button[aria-label*="Copy" i]')].map(b=>({label:b.getAttribute('aria-label'),
                            after:!!(root.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING),contains:root.contains(b),
                            owner:b.closest('[data-content-search-unit-key]')?.getAttribute('data-content-search-unit-key'),
                            html:b.outerHTML.slice(0,600)}))});
                    if(p.matches('main'))break;
                }
                return {found:true,rows};
            }''')
            Path('/app/state/gateway-fix-20261102/copy_ancestors.json').write_text(json.dumps(row,indent=2))
            print(json.dumps(row,indent=2))
            if row.get('found'):
                html=await page.evaluate('''() => {const r=[...document.querySelectorAll('[data-content-search-unit-key$=":assistant"]')].at(-1);return r.closest('[data-content-search-turn-key]')?.outerHTML||r.parentElement.outerHTML;}''')
                Path('/app/state/gateway-fix-20261102/copy_turn_fixture.html').write_text(html,encoding='utf-8')
        await browser.close()
asyncio.run(main())
