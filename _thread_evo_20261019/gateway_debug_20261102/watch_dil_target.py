"""Read-only runtime error observation for the existing DIL rendering iframe."""
import asyncio
import json
import time
from pathlib import Path
from patchright.async_api import async_playwright


async def main():
    dest = Path('/app/state/gateway-fix-20261102/dil_errors.jsonl')
    def record(event, data):
        with dest.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'time': time.time(), 'event': event, 'data': data}, ensure_ascii=False) + '\n')
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        session = await browser.new_browser_cdp_session()
        attached = {}
        def received(event):
            message = json.loads(event['message'])
            if message.get('method') in ('Runtime.exceptionThrown', 'Log.entryAdded'):
                record(message['method'], message.get('params'))
            elif message.get('method') == 'Runtime.consoleAPICalled' and message.get('params', {}).get('type') in ('error', 'warning', 'warn'):
                record('console_error', message.get('params'))
        session.on('Target.receivedMessageFromTarget', received)
        for _ in range(120):
            for target in (await session.send('Target.getTargets'))['targetInfos']:
                if target['targetId'] in attached or not ('/deployments/dil/' in target.get('url', '') or target.get('type') == 'worker'):
                    continue
                result = await session.send('Target.attachToTarget', {'targetId': target['targetId'], 'flatten': False})
                sid = result['sessionId']
                attached[target['targetId']] = sid
                for index, method in enumerate(('Runtime.enable', 'Log.enable')):
                    await session.send('Target.sendMessageToTarget', {'sessionId': sid, 'message': json.dumps({'id': index+1, 'method': method})})
                record('attached', {'url': target['url']})
            await asyncio.sleep(3)
        for sid in attached.values():
            try:
                await session.send('Target.detachFromTarget', {'sessionId': sid})
            except Exception:
                pass
        await session.detach()
        await browser.close()


asyncio.run(main())
