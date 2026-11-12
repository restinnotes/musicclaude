import asyncio
import json
from pathlib import Path
import sqlite3
from patchright.async_api import async_playwright


async def main():
    rows = [json.loads(line) for line in Path('/app/state/yi-session-observer.jsonl').read_text().splitlines()]
    print(json.dumps([r for r in rows if r.get('utc', '') > '2026-10-06T13:31:00'
        and any(k in r['event'] for k in ('auth', 'cookie', 'closed'))][-20:]))
    db = sqlite3.connect('file:/app/browser_data/Default/Cookies?mode=ro', uri=True)
    print('persisted_auth_count', db.execute('select count(*) from cookies where name like ?',
        ('__Secure-next-auth.session-token%',)).fetchone()[0])
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        for context in browser.contexts:
            cookies = await context.cookies('https://chatgpt.com/')
            print(json.dumps({'cookie_count': len(cookies), 'relevant': [{'name': c['name'], 'domain': c['domain'],
                'expires': c['expires']} for c in cookies if 'auth' in c['name'] or c['name'] == 'oai-did']}))
        await browser.close()


asyncio.run(main())
