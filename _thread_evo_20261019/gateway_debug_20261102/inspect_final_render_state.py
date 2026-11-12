"""Passive shape check for the latest assistant's public final message only."""
import asyncio
import json
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        results = []
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:
                continue
            row = await page.evaluate('''() => {
                const root=[...document.querySelectorAll('[data-content-search-unit-key$=":assistant"]')].at(-1);
                if(!root)return {found:false};
                const fiberKey=Object.keys(root).find(k=>k.startsWith('__reactFiber'));
                let fiber=root[fiberKey]; const rows=[];
                function messageShape(m){
                    if(!m || typeof m!=='object' || m.author?.role!=='assistant' || m.channel!=='final')return null;
                    const d=m.metadata?.model_dil_v2 || {};
                    return {channel:m.channel,status:m.status,end_turn:m.end_turn,kind:m.content?.content_type,
                        parts:m.content?.parts?.map(p=>typeof p==='string'?p.length:typeof p),
                        fallback:typeof d.fallbackMarkdown==='string'?d.fallbackMarkdown.length:null,
                        code:typeof d.code==='string'?d.code.length:null,keys:Object.keys(m.metadata||{})};
                }
                for(let n=0;fiber&&n<35;n++,fiber=fiber.return){
                    const p=fiber.memoizedProps||{};
                    const candidates=Object.entries(p).filter(([k,v])=>v&&typeof v==='object'&&!['children','style'].includes(k));
                    rows.push({n,keys:Object.keys(p),messages:candidates.map(([key,v])=>({key,
                        message:messageShape(v),nested:messageShape(v.message)})).filter(v=>v.message||v.nested)});
                }
                return {found:true, stop:!!document.querySelector('button[data-testid="stop-button"]'),
                    characters:root.innerText.length,rows};
            }''', isolated_context=False)
            results.append(row)
        Path('/app/state/gateway-fix-20261102/final_render_state.json').write_text(json.dumps(results,indent=2))
        print(json.dumps(results,indent=2))
        await browser.close()


asyncio.run(main())
