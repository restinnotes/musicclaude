"""Observe session presence only; retain no cookie values or raw headers."""
import asyncio
import json
import time
from pathlib import Path
from patchright.async_api import async_playwright

async def main():
    path = Path('/app/state/shiyan-session-observations.json')
    observations = []
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        for _ in range(3600):
            cookies = await context.cookies('https://chatgpt.com/')
            sessions = [c for c in cookies if c['name'].startswith('__Secure-next-auth.session-token')]
            observations.append({'timestamp': time.time(), 'present': bool(sessions),
                'count': len(sessions), 'expiries': [c.get('expires') for c in sessions]})
            path.write_text(json.dumps(observations), encoding='utf-8')
            del cookies, sessions
            if not observations[-1]['present']:
                print(json.dumps({'session_lost': True, 'timestamp': time.time()}), flush=True)
                break
            if Path('/app/state/shiyan-monitor-stop').exists():
                break
            await asyncio.sleep(2)
        await browser.close()
    print(json.dumps({'samples': len(observations), 'all_present': all(i['present'] for i in observations)}), flush=True)

asyncio.run(main())
