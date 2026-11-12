"""Read bounded UI progress metadata from existing mg pages; no navigation, focus or sends."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CODE = '''
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as driver:
        browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        rows = []
        for context in browser.contexts:
            for index, page in enumerate(context.pages):
                if not page.url.startswith('https://chatgpt.com'):
                    continue
                try:
                    row = await page.evaluate("""() => {
                        const assistants = [...document.querySelectorAll('[data-content-search-unit-key$=":assistant"], [data-message-author-role=assistant]')];
                        const users = [...document.querySelectorAll('[data-content-search-unit-key$=":user"], [data-message-author-role=user]')];
                        const buttons = [...document.querySelectorAll('button')];
                        const answerText = assistants.map(e=>e.innerText||'').join(' ');
                        const promptStart = users.map(e=>e.textContent||'').join(' ').slice(0,500);
                        const jobMatch = promptStart.match(/(?:researcher|研究员|审计员|auditor)\\s+(R1-W1-[ABC]|R2-domestic-batch[0-9]{2}|R[34]-batch[0-9]{2}|R-W[5-8]-sources|Q-final-completeness|W[1-8]-[ABC](?:-batch[0-9]{2}|-continuation[0-9]{2})?)(?:-recovery(?:[0-9]{2}|-C[0-9]{2}))?/);
                        const visible = e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().height > 0;
                        return {job_id:jobMatch?jobMatch[0].replace(/^(?:researcher|研究员|审计员|auditor)\\s+/,""):null, assistant_messages:assistants.length,
                            assistant_characters:assistants.reduce((n,e)=>n+(e.innerText||'').length,0),
                            user_messages:users.length,
                            web_unavailable_marker:answerText.includes('WEB RESEARCH UNAVAILABLE'),
                            structured_web_false_marker:/"web_research_available"\\s*:\\s*false/.test(answerText),
                            generation_active:buttons.some(e=>visible(e) &&
                                (/^(Stop generating|Stop answering|Stop responding|Stop|停止生成|停止回答)$/i.test(e.getAttribute('aria-label')||'') || e.getAttribute('data-testid')==='stop-button')),
                            assistant_external_links:assistants.reduce((n,e)=>n+[...e.querySelectorAll('a[href]')].filter(a=>/^https?:/.test(a.href) && !a.href.startsWith('https://chatgpt.com')).length,0),
                            thinking_labels:[...document.querySelectorAll('button')].filter(e=>/^(Worked for|Thought for)\\s/.test(e.innerText||'')).map(e=>e.innerText.slice(0,80)).slice(0,5)};
                    }""")
                    row['page_index'] = index
                    row['temporary_url_flag'] = 'temporary-chat=true' in page.url
                    rows.append(row)
                except Exception as error:
                    rows.append({'page_index':index,'error_type':type(error).__name__})
        print(json.dumps(rows))
        # Closing this Playwright transport disconnects this observer, not the existing browser.
asyncio.run(main())
'''
result = subprocess.run(['docker', 'exec', 'yi-mimicgate-20261002', '/opt/venv/bin/python', '-c', CODE],
    capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
if result.returncode:
    raise SystemExit('Passive page progress unavailable')
record = {'captured_utc':datetime.now(timezone.utc).isoformat(), 'read_only':True, 'pages':json.loads(result.stdout)}
with (HERE / 'page-progress.jsonl').open('a', encoding='utf-8') as handle:
    handle.write(json.dumps(record) + '\n')
print(json.dumps(record))
