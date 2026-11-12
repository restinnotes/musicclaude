"""Inspect scripts already loaded by the rendering frame, without new network requests."""
import asyncio
import base64
import hashlib
import json
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        session = await browser.new_browser_cdp_session()
        future = asyncio.get_running_loop().create_future()
        def received(event):
            message = json.loads(event['message'])
            if message.get('id') == 71 and not future.done():
                future.set_result(message)
        session.on('Target.receivedMessageFromTarget', received)
        targets = (await session.send('Target.getTargets'))['targetInfos']
        target = next(t for t in targets if '/deployments/dil/' in t.get('url', ''))
        sid = (await session.send('Target.attachToTarget', {'targetId': target['targetId'], 'flatten': False}))['sessionId']
        await session.send('Target.sendMessageToTarget', {'sessionId': sid, 'message': json.dumps({
            'id': 71, 'method': 'Runtime.evaluate', 'params': {'expression': 'JSON.stringify({html:document.documentElement.outerHTML, metas:[...document.querySelectorAll("meta[http-equiv]")].map(x=>x.outerHTML), scripts:[...document.scripts].map(s=>({src:s.src,text:s.textContent}))})', 'returnByValue': True}})})
        result = await asyncio.wait_for(future, 10)
        data = json.loads(result['result']['result']['value'])
        Path('/app/state/gateway-fix-20261102/dil_loaded_document.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        print(json.dumps({'metas': data['metas'], 'scripts': [{'src': s['src'], 'length': len(s['text']),
            'sha256': base64.b64encode(hashlib.sha256(s['text'].encode()).digest()).decode(),
            'preview': s['text'][:100]} for s in data['scripts']]}, ensure_ascii=False))
        await session.send('Target.detachFromTarget', {'sessionId': sid})
        await session.detach()
        await browser.close()


asyncio.run(main())
