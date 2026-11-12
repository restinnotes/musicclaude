"""Read bounded render-component shapes only; never log message text/state."""
import asyncio
import json
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for page in browser.contexts[0].pages:
            if 'chatgpt.com/c/' not in page.url:
                continue
            state = await page.evaluate('''() => {
                const root = document.querySelector('[data-dil-message-id]');
                if (!root) return {found:false};
                const key=Object.keys(root).find(k=>k.startsWith('__reactFiber'));
                let fiber=root[key]; const rows=[];
                const shape=(v)=>v===null?'null':Array.isArray(v)?'array':typeof v;
                for(let n=0;fiber&&n<22;n++,fiber=fiber.return){
                    const props=fiber.memoizedProps||{};
                    rows.push({tag:fiber.tag, component:typeof fiber.type==='function'?fiber.type.name:typeof fiber.type==='string'?fiber.type:'other',
                        keys:Object.keys(props).slice(0,40).map(k=>({key:k,type:shape(props[k]),length:typeof props[k]==='string'?props[k].length:undefined})),
                        settings:Object.fromEntries(['diagnostics','preparing','recoverSafeStartupPeers','recoverPreReadyFrame'].filter(k=>typeof props[k]==='boolean').map(k=>[k,props[k]])),
                        flags:fiber.flags, hasChild:Boolean(fiber.child)});
                }
                return {found:true, children:root.childElementCount, rows};
            }''', isolated_context=False)
            dest=Path('/app/state/gateway-fix-20261102/empty_renderer_shape.json')
            dest.write_text(json.dumps(state,indent=2))
            dil = await page.evaluate('''() => {
                const root=document.querySelector('[data-dil-message-id]');
                let fiber=root?.[Object.keys(root).find(k=>k.startsWith('__reactFiber'))];
                for(let n=0;fiber&&n<15;n++,fiber=fiber.return){if(typeof fiber.memoizedProps?.dil==='string')return fiber.memoizedProps.dil;}
                return null;
            }''',isolated_context=False)
            if dil:
                dest.with_name('empty_renderer_source.txt').write_text(dil,encoding='utf-8')
            print(json.dumps({'found':state.get('found'),'children':state.get('children'),
                'settings':[r.get('settings') for r in state.get('rows',[]) if r.get('settings')],
                'dil_characters':len(dil or '')}))
        await browser.close()


asyncio.run(main())
