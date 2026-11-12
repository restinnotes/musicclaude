"""Passive forensic observer. No navigation, sends, imports, or profile cleanup."""
import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
import hashlib
from http.cookies import SimpleCookie
import json
import os
from pathlib import Path
import signal
import sqlite3
import time
from urllib.parse import urlsplit

AUTH_PREFIX = '__Secure-next-auth.session-token'
STATE = Path('/app/state')
LOG = STATE / 'yi-session-observer.jsonl'

def stamp():
    return datetime.now(timezone.utc).isoformat()

def classify_url(url):
    p = urlsplit(url)
    return {'host': p.hostname, 'path_category': 'logout' if 'logout' in p.path.lower()
            else 'auth' if '/auth/' in p.path or p.hostname in ('auth.openai.com','auth0.openai.com')
            else 'root' if p.path == '/' else 'other'}

def auth_header_metadata(header, now=None):
    now = time.time() if now is None else now
    first = header.split(';', 1)[0]
    name = first.partition('=')[0].strip()
    if not name.startswith(AUTH_PREFIX):
        return None
    parsed = SimpleCookie()
    try:
        parsed.load(header)
        morsel = parsed.get(name)
        if morsel is None:
            return {'name':name,'metadata_parse_error':True}
        max_age = int(morsel['max-age']) if morsel['max-age'] else None
        expiry = parsedate_to_datetime(morsel['expires']).timestamp() if morsel['expires'] else None
        return {'name':name,'max_age':max_age,'expires_utc':expiry,
                'deletion_directive': (max_age is not None and max_age <= 0) or (expiry is not None and expiry <= now),
                'empty_value':not bool(morsel.value)}
    except (ValueError, TypeError, OverflowError):
        return {'name':name,'metadata_parse_error':True}

def emit(kind, **data):
    event = {'utc':stamp(),'event':kind,**data}
    fd = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    with os.fdopen(fd, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event, ensure_ascii=False)+'\n')

def attach_context_audit(context):
    """Installed before first navigation on the next backend startup."""
    async def response_event(response):
        try:
            url=classify_url(response.url)
            if url['host'] not in ('chatgpt.com','auth.openai.com','auth0.openai.com'):
                return
            for item in await response.headers_array():
                if item['name'].lower()=='set-cookie':
                    metadata=auth_header_metadata(item['value'])
                    if metadata is not None:
                        emit('auth_cookie_response',source='backend',status=response.status,**url,**metadata)
            if response.status in (401,403):
                emit('http_auth_or_access_error',source='backend',status=response.status,**url)
        except Exception as error:
            emit('response_observation_error',source='backend',exception_type=type(error).__name__)
    context.on('response',response_event)
    context.on('close',lambda: emit('backend_context_closed'))
    emit('backend_context_audit_attached',pid=os.getpid(),page_count=len(context.pages))

async def request_auth_snapshot(page):
    cookies=await page.context.cookies('https://chatgpt.com/')
    auth=[c for c in cookies if c['name'].startswith(AUTH_PREFIX)]
    return {'session_cookie_count':len(auth),'expiries':sorted(c.get('expires',-1) for c in auth)}

def db_auth_count():
    path = Path('/app/browser_data/Default/Cookies')
    try:
        db=sqlite3.connect(f'file:{path}?mode=ro',uri=True,timeout=.2)
        try:
            return db.execute('SELECT count(*) FROM cookies WHERE name LIKE ?', (AUTH_PREFIX+'%',)).fetchone()[0]
        finally:
            db.close()
    except sqlite3.Error:
        return None

async def observe_connection(driver, stop):
    browser = await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    tasks=set()
    last_snapshot=None
    last_values=None
    last_cookie_time=None
    last_heartbeat=0
    previous_ui={}

    async def response_event(response):
        try:
            url=classify_url(response.url)
            if url['host'] not in ('chatgpt.com','auth.openai.com','auth0.openai.com'):
                return
            # Metadata only. Neither bodies nor header/cookie values enter logs.
            headers=await response.headers_array()
            for item in headers:
                if item['name'].lower()=='set-cookie':
                    metadata=auth_header_metadata(item['value'])
                    if metadata is not None:
                        emit('auth_cookie_response',status=response.status,**url,**metadata)
            if response.status in (401,403):
                emit('http_auth_or_access_error',status=response.status,**url)
        except Exception as error:
            emit('response_observation_error',exception_type=type(error).__name__)

    def response_received(response):
        task=asyncio.create_task(response_event(response))
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    context.on('response',response_received)
    emit('browser_connected',page_count=len(context.pages))
    try:
        while not stop.is_set():
            cookies=await context.cookies('https://chatgpt.com/')
            auth=[c for c in cookies if c['name'].startswith(AUTH_PREFIX)]
            snapshot={'session_cookie_count':len(auth),'expiries':sorted(c.get('expires',-1) for c in auth),
                      'database_session_rows':db_auth_count()}
            # Fingerprints exist only in RAM, to observe rotation without storing tokens.
            values=tuple(sorted(hashlib.sha256(c['value'].encode()).digest() for c in auth))
            now=time.time()
            status={'observed_epoch':now,'observer_pid':os.getpid(),**snapshot}
            status_temp=STATE/'yi-session-status.tmp'
            status_temp.write_text(json.dumps(status),encoding='utf-8')
            status_temp.chmod(0o600)
            status_temp.replace(STATE/'yi-session-status.json')
            if snapshot!=last_snapshot or values!=last_values:
                emit('cookie_change' if last_snapshot is not None else 'initial_cookie_state',
                     previous=last_snapshot,current=snapshot,cookie_value_changed=(values!=last_values and last_values is not None),
                     previous_observation_utc=last_cookie_time)
            last_snapshot=snapshot
            last_values=values
            last_cookie_time=stamp()
            if now-last_heartbeat>=60:
                emit('heartbeat',**snapshot,page_count=len(context.pages))
                last_heartbeat=now
            for page in list(context.pages):
                if urlsplit(page.url).hostname!='chatgpt.com':
                    continue
                try:
                    ui=await page.evaluate('''() => {
                       const visible=e=>!!e.getClientRects().length;
                       const b=[...document.querySelectorAll('button')].filter(visible);
                       return {profile:b.some(e=>e.getAttribute('aria-label')==='Open profile menu'),
                          login:b.some(e=>/^(Log in|登录)$/i.test((e.innerText||'').trim())),
                          temporary:b.some(e=>/temporary|临时/i.test((e.getAttribute('aria-label')||'')+' '+(e.innerText||'')))};
                    }''')
                    if previous_ui.get(id(page))!=ui:
                        emit('page_auth_state',page_observer_id=id(page),**ui)
                        previous_ui[id(page)]=ui
                except Exception:
                    pass
            try:
                await asyncio.wait_for(stop.wait(),timeout=5)
            except asyncio.TimeoutError:
                pass
    finally:
        context.remove_listener('response',response_received)
        for task in list(tasks):
            task.cancel()
        await browser.close()  # CDP disconnect; the user's Chromium remains running.

async def main():
    from patchright.async_api import async_playwright
    lock=open(STATE/'yi-session-observer.lock','a')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return
    stop=asyncio.Event()
    loop=asyncio.get_running_loop()
    for sig in (signal.SIGTERM,signal.SIGINT):
        loop.add_signal_handler(sig,stop.set)
    (STATE/'yi-session-observer.pid').write_text(str(os.getpid()),encoding='ascii')
    emit('collector_started',pid=os.getpid(),passive=True,sample_interval_seconds=5)
    async with async_playwright() as driver:
        while not stop.is_set():
            try:
                await observe_connection(driver,stop)
            except Exception as error:
                emit('browser_connection_lost',exception_type=type(error).__name__)
                try:
                    await asyncio.wait_for(stop.wait(),timeout=5)
                except asyncio.TimeoutError:
                    pass
    emit('collector_stopped')

if __name__=='__main__':
    asyncio.run(main())
