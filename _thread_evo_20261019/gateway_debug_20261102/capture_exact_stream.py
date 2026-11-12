"""Bounded passive evidence for one authorized retry; never submits or replays.

Raw response stays in the private local diagnostic directory, never in reports.
Only the exact frozen prompt hash is captured. Detach after terminal stream.
"""
import asyncio
import base64
import json
import os
import time
from pathlib import Path
from patchright.async_api import async_playwright
from src.request_observer import request_metadata

ROOT = Path(os.environ.get('CAPTURE_DIRECTORY', '/app/state/gateway-fix-20261102/exact-stream'))
HASH = os.environ.get('CAPTURE_PROMPT_HASH', '3b36588f62ee52c9e0d4533efc76c802b87afd78ba401f13988611542694f7aa')
LIMIT = 64 * 1024 * 1024  # disk bound; long final code-block patches exceed 8 MiB
BUFFER = 8 * 1024 * 1024


async def main():
    ROOT.mkdir(exist_ok=True)
    finished = asyncio.Event()
    sessions, tracked = [], {}
    async with async_playwright() as runtime:
        browser = await runtime.chromium.connect_over_cdp('http://127.0.0.1:9222')
        async def attach(page):
            session = await page.context.new_cdp_session(page)
            sessions.append(session)
            def requested(event):
                request = event.get('request', {})
                if (request.get('method') == 'POST'
                        and request_metadata(request.get('postData', '{}')).get('text_sha256') == HASH):
                    if tracked or request.get('url', '').endswith('/init'):
                        return
                    tracked[(id(session), event['requestId'])] = {
                        'file': (ROOT / 'response.sse').open('xb'), 'bytes': 0,
                        'bytes_observed': 0, 'truncated': False, 'early': [],
                        'enabled': False, 'epoch': time.time()}
            def consume(entry, chunk):
                entry['bytes_observed'] += len(chunk)
                available = max(0, LIMIT - entry['bytes'])
                saved = chunk[:available]
                entry['file'].write(saved)
                entry['bytes'] += len(saved)
                entry['truncated'] |= len(saved) != len(chunk)
            async def response(event):
                entry = tracked.get((id(session), event['requestId']))
                if entry is None:
                    return
                entry['status'] = event.get('response', {}).get('status')
                try:
                    result = await session.send('Network.streamResourceContent', {'requestId': event['requestId']})
                    consume(entry, base64.b64decode(result.get('bufferedData', '')))
                    entry['enabled'] = True
                    for chunk in entry['early']:
                        consume(entry, chunk)
                    entry['early'].clear()
                except Exception as error:
                    entry['capture_error'] = type(error).__name__
            def data(event):
                entry = tracked.get((id(session), event['requestId']))
                if entry is None or not event.get('data'):
                    return
                chunk = base64.b64decode(event['data'])
                if entry['enabled']:
                    consume(entry, chunk)
                elif sum(map(len, entry['early'])) + len(chunk) <= LIMIT:
                    entry['early'].append(chunk)
                else:
                    entry['truncated'] = True
            def terminal(event):
                entry = tracked.get((id(session), event['requestId']))
                if entry is None:
                    return
                if 'file' not in entry:
                    return
                entry.pop('file').close()
                entry.pop('early')
                entry.update(network_error=event.get('errorText'), canceled=event.get('canceled'),
                             finished_epoch=time.time())
                (ROOT / 'capture.json').write_text(json.dumps(entry, indent=2))
                finished.set()
            session.on('Network.requestWillBeSent', requested)
            session.on('Network.responseReceived', response)
            session.on('Network.dataReceived', data)
            session.on('Network.loadingFinished', terminal)
            session.on('Network.loadingFailed', terminal)
            await session.send('Network.enable', {'maxTotalBufferSize': BUFFER, 'maxResourceBufferSize': BUFFER})
        context = browser.contexts[0]
        for page in context.pages:
            await attach(page)
        tasks = set()
        def page_created(page):
            task = asyncio.create_task(attach(page))
            tasks.add(task)
            task.add_done_callback(tasks.discard)
        context.on('page', page_created)
        (ROOT / 'ready.json').write_text(json.dumps({'ready': True, 'epoch': time.time()}))
        try:
            await asyncio.wait_for(finished.wait(), 900)
        except asyncio.TimeoutError:
            (ROOT / 'timeout.json').write_text(json.dumps({'timed_out': True}))
        finally:
            context.remove_listener('page', page_created)
            for entry in tracked.values():
                if 'file' in entry:
                    entry.pop('file').close()
            for task in list(tasks):
                task.cancel()
            for session in sessions:
                try:
                    await session.detach()
                except Exception:
                    pass
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
