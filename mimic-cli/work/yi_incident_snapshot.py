"""Read-only incident evidence; never export cookie values or prompt bodies."""
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from patchright.async_api import async_playwright

REPORT = Path('/app/state/yi-incident-20261005.json')

async def page_state(page):
    parts = urlsplit(page.url)
    if parts.hostname not in ('chatgpt.com', 'auth.openai.com', 'auth0.openai.com'):
        return {'host': parts.hostname, 'blank': page.url == 'about:blank'}
    state = await page.evaluate('''() => {
      const vis = e => !!(e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
      const buttons = [...document.querySelectorAll('button')].filter(vis);
      const txt = b => (b.innerText || b.getAttribute('aria-label') || '').trim();
      const body = document.body.innerText;
      return { profile_menu: buttons.some(b => b.getAttribute('aria-label') === 'Open profile menu'),
        login: buttons.some(b => /^(Log in|登录)$/i.test(txt(b))),
        signup: buttons.some(b => /^(Sign up|注册)$/i.test(txt(b))),
        temporary_controls: buttons.filter(b => /temporary|临时/i.test(txt(b))).map(b => txt(b).slice(0,120)),
        personalization_controls: buttons.filter(b => /personaliz|个性化/i.test(txt(b))).map(b => txt(b).slice(0,120)),
        composer: !!document.querySelector('#prompt-textarea'),
        stop: buttons.some(b => /stop streaming|stop generating|停止/i.test(b.getAttribute('aria-label') || '')),
        challenge: /Just a moment|Verify you are human|Checking your browser/.test(body),
        page_loading: document.readyState !== 'complete',
        ui_error: /Something went wrong|Unable to load|Try again|出了点问题/.test(body),
        selected_model: buttons.filter(b => b.getAttribute('aria-label') === 'Select ChatGPT model').map(txt)
      };
    }''')
    return {'host': parts.hostname, 'path_kind': 'conversation' if parts.path.startswith('/c/') else parts.path,
            'temporary_url': 'temporary-chat=true' in parts.query, **state}

async def main():
    report = {'captured_utc': datetime.now(timezone.utc).isoformat(), 'existing_pages': []}
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        cookies = await context.cookies('https://chatgpt.com/')
        auth = [c for c in cookies if c['name'].startswith('__Secure-next-auth.session-token')]
        now = datetime.now(timezone.utc).timestamp()
        report['session_cookie_count'] = len(auth)
        report['session_cookie_expiries'] = [c.get('expires') for c in auth]
        report['session_cookie_expired_count'] = sum(0 < c.get('expires', -1) <= now for c in auth)
        report['total_chatgpt_cookie_count'] = len(cookies)
        for page in list(context.pages):
            try:
                report['existing_pages'].append(await page_state(page))
            except Exception as error:
                report['existing_pages'].append({'inspection_error_type': type(error).__name__})
        page = await context.new_page()
        try:
            await page.goto('https://chatgpt.com/', wait_until='domcontentloaded', timeout=45000)
            for _ in range(50):
                state = await page_state(page)
                if state.get('profile_menu') or state.get('login') or state.get('challenge'):
                    break
                await asyncio.sleep(.4)
            report['fresh_page'] = state
            await page.screenshot(path='/app/state/yi-incident-20261005-fresh.png')
        except Exception as error:
            report['fresh_page_error_type'] = type(error).__name__
        finally:
            await page.close()
            await browser.close()
    report['source_hashes'] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in
        [Path('/app/src/browser/manager.py'), Path('/app/src/chatgpt/client.py'), Path('/app/src/api/standard_completion.py')]}
    logs = []
    pattern = re.compile(r'Temporary Chat activation|Removed stale|Browser started|Browser closed|[Bb]rowser.*(?:launch|start|stop|crash)|cleanup|profile.*(?:use|lock)|session.*(?:expir|invalid)|Standard.*(?:fail|error)|StandardStateError|Traceback|ERROR')
    for name in ('browser_20261005.log','chatgpt_client_20261005.log','browser_gate_20261005.log','openai_routes_20261005.log','api_routes_20261005.log'):
        path = Path('/app/logs') / name
        if not path.exists():
            continue
        matches = [line for line in path.read_text(encoding='utf-8', errors='replace').splitlines() if pattern.search(line)]
        safe = []
        for line in matches[-60:]:
            line = re.sub(r'(?i)(Bearer\s+)\S+', r'\1[REDACTED]', line)
            line = re.sub(r'(?i)((?:session-token|api[_-]?key|token|password|cookie)\s*[=:]\s*)[^\s,;]+', r'\1[REDACTED]', line)
            line = re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[EMAIL]', line)
            safe.append(line[:800])
        logs.append({'file':name, 'total_matching_lines':len(matches),'last_matching_lines':safe})
    report['logs'] = logs
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

asyncio.run(main())
