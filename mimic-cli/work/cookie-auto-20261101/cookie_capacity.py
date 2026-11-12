"""Bound the cookie footprint of finished Temporary Chats without touching auth."""
from datetime import datetime, timezone
from pathlib import Path
import re
import sqlite3
from urllib.parse import urlsplit, parse_qs
import uuid

GUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
COOKIE_NAME = re.compile(r'^(conv_key|history_off)_(' + GUID + r')$', re.I)
DOMAINS = {'chatgpt.com', '.chatgpt.com'}
TARGET_COUNT = 100
SAFE_COUNT = 160  # Admission reserves headroom for the configured concurrency.


async def site_cookies(context):
    return [c for c in await context.cookies() if c.get('domain', '').lstrip('.') == 'chatgpt.com'
            or c.get('domain', '').lstrip('.').endswith('.chatgpt.com')]


def temporary_conversation_id(url):
    parsed = urlsplit(url)
    match = re.fullmatch(r'/c/(' + GUID + r')', parsed.path, re.I)
    if parsed.hostname == 'chatgpt.com' and match and parse_qs(parsed.query).get('temporary-chat') == ['true']:
        return match[1].lower()


def active_conversation_ids(context):
    active = set()
    for page in context.pages:
        parsed = urlsplit(page.url)
        match = re.fullmatch(r'/c/(' + GUID + r')', parsed.path, re.I)
        if parsed.hostname == 'chatgpt.com' and match:
            active.add(match[1].lower())
    return active


def inactive_temporary_cookies(cookies, active):
    candidates = []
    temporary_ids = set()
    for cookie in cookies:
        match = COOKIE_NAME.fullmatch(cookie.get('name', ''))
        if (match and cookie.get('domain') in DOMAINS and cookie.get('path') == '/'
                and match[1].lower() == 'history_off'):
            temporary_ids.add(match[2].lower())
    for cookie in cookies:
        match = COOKIE_NAME.fullmatch(cookie.get('name', ''))
        if (match and cookie.get('domain') in DOMAINS and cookie.get('path') == '/'
                and match[2].lower() in temporary_ids - active):
            candidates.append(cookie)
    return sorted(candidates, key=lambda c: (c.get('expires', 0), c['name']))


def backup_encrypted_cookie_database(profile):
    """SQLite backup preserves Chrome's encrypted values and WAL state."""
    profile = Path(profile).resolve()
    database = profile / 'Default' / 'Cookies'
    target_dir = profile / '.yi-diagnostics'
    target_dir.mkdir(exist_ok=True, mode=0o700)
    target = target_dir / ('cookies-before-retention-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        + '-' + uuid.uuid4().hex[:8] + '.sqlite')
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True, timeout=2) as source:
        with sqlite3.connect(target) as destination:
            source.backup(destination)
    target.chmod(0o600)
    return target.name


async def ensure_cookie_headroom(context, profile, *, allow_prune=True,
                                 protected_ids=(), recycle_at=SAFE_COUNT):
    from src.session_observer import emit
    cookies = await site_cookies(context)
    count = len(cookies)
    if count < recycle_at:
        return {'cookie_count': count, 'removed': 0}
    protected = active_conversation_ids(context) | set(protected_ids)
    eligible = inactive_temporary_cookies(cookies, protected)
    candidates = eligible if allow_prune else []
    if count - len(candidates) >= recycle_at:
        emit('cookie_capacity_guard', cookie_count=count, inactive_temporary_cookie_count=len(candidates),
             action='submission_blocked', authentication_modified=False,
             eligible_temporary_cookie_count=len(eligible), pruning_allowed=allow_prune,
             protected_conversation_count=len(protected), recycle_at=recycle_at)
        raise RuntimeError('ChatGPT cookie capacity is near its limit; no safe inactive Temporary cookies can be recycled')
    backup = backup_encrypted_cookie_database(profile)
    removed = 0
    session = await context.new_cdp_session(context.pages[0])
    try:
        groups = {}
        for cookie in candidates:
            groups.setdefault(COOKIE_NAME.fullmatch(cookie['name'])[2].lower(), []).append(cookie)
        for group in groups.values():
            if count - removed <= TARGET_COUNT:
                break
            # Playwright's filtered clear_cookies clears the entire jar and
            # re-adds retained cookies. Exact CDP deletion never touches auth.
            for cookie in group:
                await session.send('Network.deleteCookies', {'name': cookie['name'],
                    'domain': cookie['domain'], 'path': cookie['path']})
                removed += 1
    finally:
        await session.detach()
    after = await site_cookies(context)
    auth_before = {(c['name'], c['domain'], c['path']) for c in cookies
                   if c['name'].startswith('__Secure-next-auth.session-token')}
    auth_after = {(c['name'], c['domain'], c['path']) for c in after
                  if c['name'].startswith('__Secure-next-auth.session-token')}
    if not auth_before.issubset(auth_after):
        raise RuntimeError('Authentication changed during Temporary-cookie retention; refusing further submission')
    if len(after) >= recycle_at:
        raise RuntimeError('Temporary-cookie retention did not restore safe headroom')
    result = {'cookie_count_before': count, 'cookie_count': len(after), 'removed': removed,
              'encrypted_backup': backup, 'authentication_modified': False}
    emit('temporary_cookie_retention', **result)
    return result


async def retire_temporary_conversation_cookies(context, conversation_id):
    if not conversation_id or not re.fullmatch(GUID, conversation_id, re.I):
        return
    if conversation_id.lower() in active_conversation_ids(context):
        return
    cookies = await context.cookies('https://chatgpt.com/')
    removed = 0
    session = await context.new_cdp_session(context.pages[0])
    try:
        for cookie in inactive_temporary_cookies(cookies, set()):
            match = COOKIE_NAME.fullmatch(cookie['name'])
            if match[2].lower() == conversation_id.lower():
                await session.send('Network.deleteCookies', {'name': cookie['name'],
                    'domain': cookie['domain'], 'path': cookie['path']})
                removed += 1
    finally:
        await session.detach()
    if removed:
        from src.session_observer import emit
        emit('finished_temporary_cookie_recycled', removed=removed, authentication_modified=False)
