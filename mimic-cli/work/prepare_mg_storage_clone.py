"""One offline, exclusively owned MG clone; no account navigation or model POST.

CLI: --mode control|local_storage. Stdin is {"cookies": [native CDP cookies]}.
The caller must create a source-free, network-none container and an owned marker
at /app/browser_data/.mg-storage-clone-owned.json. No gpt2agent dependency.
Cookie values and file fingerprints stay only in RAM; stdout is a safe report.
"""
import argparse
import asyncio
import contextlib
import copy
import hashlib
import json
import logging
import math
from pathlib import Path
import platform
import sys
import time
import traceback

PROFILE = Path('/app/browser_data')
EXECUTABLE = Path('/opt/ms-playwright/chromium-1243/chrome-linux64/chrome')
VENDOR_CHROME = Path('/opt/google/chrome/chrome')
MANAGER_SOURCE = Path('/app/src/browser/manager.py')
MARKER = '.mg-storage-clone-owned.json'
ORIGIN = 'https://chatgpt.com'
FIXTURE_URL = ORIGIN + '/__owned_mg_storage_preparation_fixture__'
FIXTURE_TITLE = 'Owned offline storage fixture'
MAX_STDIN = 512 * 1024
WRITE_FIELDS = ('name','value','domain','path','expires','secure','httpOnly',
                'sameSite','priority','sameParty','sourceScheme','sourcePort','partitionKey')
CATEGORIES = {'indexeddb': ('Default/IndexedDB',),
              'service_worker_and_cache_storage': ('Default/Service Worker',),
              'http_and_code_cache': ('Default/Cache','Default/Code Cache')}


class CloneError(ValueError):
    """Only static error codes; never preserve library exception messages."""


def require(condition, code):
    if not condition:raise CloneError(code)


def cookie_key(cookie):
    partition=cookie.get('partitionKey')
    return (cookie['name'],cookie['domain'],cookie['path'],
            None if partition is None else (partition['topLevelSite'],partition['hasCrossSiteAncestor']))


def convert_cookies(cookies, *, now):
    require(type(cookies) is list and 1 <= len(cookies) <= 100,'cookie_selection_invalid')
    result=[];keys=set()
    for cookie in cookies:
        require(type(cookie) is dict,'cookie_metadata_invalid')
        name,value,domain,path=(cookie.get(k) for k in ('name','value','domain','path'))
        require(type(name) is str and 0 < len(name) <= 1024
                and not any(c in name for c in '\r\n;=\0')
                and not name.startswith(('conv_key_','history_off_')),'cookie_metadata_invalid')
        require(type(value) is str and len(value) <= 32768
                and not any(c in value for c in '\r\n\0'),'cookie_metadata_invalid')
        require(domain in ('chatgpt.com','.chatgpt.com') and type(path) is str
                and path.startswith('/') and len(path)<=4096
                and not any(c in path for c in '\r\n\0'),'cookie_metadata_invalid')
        require(type(cookie.get('secure')) is bool and type(cookie.get('httpOnly')) is bool,
                'cookie_metadata_invalid')
        expires=cookie.get('expires')
        require(type(expires) in (int,float) and math.isfinite(expires)
                and (expires == -1 or expires > now),'cookie_expired_or_invalid')
        require('partitionKeyOpaque' not in cookie or cookie['partitionKeyOpaque'] is False,
                'cookie_partition_unsupported')
        partition=cookie.get('partitionKey')
        if partition is not None:
            require(type(partition) is dict and set(partition)=={'topLevelSite','hasCrossSiteAncestor'}
                    and partition['topLevelSite']==ORIGIN
                    and partition['hasCrossSiteAncestor'] is False,'cookie_partition_unsupported')
        if 'sameSite' in cookie:
            require(cookie['sameSite'] in ('Strict','Lax','None')
                    and (cookie['sameSite']!='None' or cookie['secure']),'cookie_metadata_invalid')
        if 'priority' in cookie:require(cookie['priority'] in ('Low','Medium','High'),'cookie_metadata_invalid')
        if 'sameParty' in cookie:require(type(cookie['sameParty']) is bool,'cookie_metadata_invalid')
        if 'sourceScheme' in cookie:
            require(cookie['sourceScheme'] in ('Unset','NonSecure','Secure'),'cookie_metadata_invalid')
        if 'sourcePort' in cookie:
            require(type(cookie['sourcePort']) is int and
                    (cookie['sourcePort']==-1 or 1<=cookie['sourcePort']<=65535),'cookie_metadata_invalid')
        item=copy.deepcopy({k:cookie[k] for k in WRITE_FIELDS if k in cookie})
        key=cookie_key(item)
        require(key not in keys,'cookie_selection_ambiguous');keys.add(key);result.append(item)
    require(sum(c['name'].startswith('__Secure-next-auth.session-token') for c in result)==1
            and sum(c['name']=='oai-did' for c in result)==1,'cookie_auth_device_missing_or_ambiguous')
    require(all(c['value'] for c in result if c['name']=='oai-did'
                or c['name'].startswith('__Secure-next-auth.session-token')),
            'cookie_auth_device_missing_or_ambiguous')
    return result


def cookies_import_matches(actual, imported):
    lookup={}
    for cookie in actual:
        key=cookie_key(cookie)
        if key in lookup:return False
        lookup[key]=cookie
    return all(cookie_key(c) in lookup and all(lookup[cookie_key(c)].get(k)==v for k,v in c.items())
               for c in imported)


def cookies_exactly_equal(before, after):
    # Order is not semantic. Compare complete CDP metadata and values in RAM.
    try:
        left={cookie_key(c):c for c in before};right={cookie_key(c):c for c in after}
        return len(left)==len(before) and len(right)==len(after) and left==right
    except (KeyError,TypeError):return False


def profile_guard(config):
    require(platform.system()=='Linux','clone_linux_required')
    require(PROFILE.is_dir() and not PROFILE.is_symlink()
            and Path(config.BROWSER_DATA_DIR).resolve()==PROFILE,'clone_profile_path_invalid')
    marker=PROFILE/MARKER
    require(marker.is_file() and not marker.is_symlink() and marker.stat().st_size<=4096,
            'clone_owned_marker_missing')
    try:value=json.loads(marker.read_text(encoding='utf-8'))
    except Exception:raise CloneError('clone_owned_marker_invalid') from None
    require(value=={'schema':1,'owned_clone':True,'source_profile_mounted':False,
                    'network_isolated':True},'clone_owned_marker_invalid')
    require(config.BROWSER_CHANNEL in ('','chromium','bundled','chrome'),'clone_browser_channel_invalid')
    if config.BROWSER_CHANNEL=='chrome':
        require(not VENDOR_CHROME.exists() and not VENDOR_CHROME.is_symlink(),
                'clone_vendor_chrome_unexpected')
    require(EXECUTABLE.is_file() and not EXECUTABLE.is_symlink(),'clone_browser_path_invalid')


def check_browser_processes(*, launched=False):
    live=matched=0
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():continue
        try:
            comm=(entry/'comm').read_text().strip().lower()
            status=(entry/'stat').read_text();state=status[status.rfind(')')+2:].split()[0]
            if state=='Z' or not any(x in comm for x in ('chrome','chromium','crashpad')):continue
            live+=1
            executable=(entry/'exe').resolve()
            if executable==EXECUTABLE:
                args=(entry/'cmdline').read_bytes().split(b'\0')
                if b'--user-data-dir=/app/browser_data' in args:matched+=1
            elif 'crashpad' not in comm:
                raise CloneError('clone_browser_path_invalid')
        except (FileNotFoundError,ProcessLookupError):continue
        except OSError:raise CloneError('clone_process_inspection_failed') from None
    if launched:require(matched==1,'clone_browser_process_binding_invalid')
    else:require(live==0,'clone_existing_live_browser')
    return {'owned_browser_process_binding_verified':bool(launched and matched==1),
            'no_live_browser_verified':live==0}


class _ChromiumProxy:
    def __init__(self,actual):self._actual=actual
    def __getattr__(self,name):return getattr(self._actual,name)
    async def launch_persistent_context(self,*args,**kwargs):
        require(not args and Path(kwargs.get('user_data_dir','')).resolve()==PROFILE,
                'clone_profile_path_invalid')
        require(Path(self._actual.executable_path).resolve()==EXECUTABLE,'clone_browser_path_invalid')
        require('executable_path' not in kwargs and kwargs.get('channel') in (None,'chrome'),
                'clone_browser_path_invalid')
        if kwargs.get('channel')=='chrome':
            require(not VENDOR_CHROME.exists() and not VENDOR_CHROME.is_symlink(),
                    'clone_vendor_chrome_unexpected')
        options=dict(kwargs);options['offline']=True
        return await self._actual.launch_persistent_context(**options)


class _PlaywrightProxy:
    def __init__(self,actual):self._actual=actual;self.chromium=_ChromiumProxy(actual.chromium)
    def __getattr__(self,name):return getattr(self._actual,name)


@contextlib.contextmanager
def offline_launch(manager_module):
    original=manager_module.async_playwright
    class Factory:
        async def start(self):return _PlaywrightProxy(await original().start())
    manager_module.async_playwright=Factory
    try:yield
    finally:manager_module.async_playwright=original


async def local_storage_count(context,page,cdp):
    try:
        result=await cdp.send('DOMStorage.getDOMStorageItems',
            {'storageId':{'securityOrigin':ORIGIN,'isLocalStorage':True}})
        entries=result.get('entries')
        if type(entries) is list:return len(entries),'blank_target_CDP'
    except Exception:pass  # No raw protocol error survives this fallback.
    fixture_fulfilled=False
    async def fixture(route):
        nonlocal fixture_fulfilled
        require(route.request.url==FIXTURE_URL and route.request.method=='GET','clone_fixture_request_invalid')
        await route.fulfill(status=200,content_type='text/html',
                            body='<!doctype html><meta charset="utf-8"><title>'+FIXTURE_TITLE+'</title>')
        fixture_fulfilled=True
    await context.route(FIXTURE_URL,fixture)
    try:
        await page.goto(FIXTURE_URL,wait_until='domcontentloaded',timeout=5000)
        require(fixture_fulfilled,'clone_fixture_not_fulfilled')
        require(page.url==FIXTURE_URL and await page.title()==FIXTURE_TITLE,
                'clone_fixture_document_invalid')
        require(await page.locator('script').count()==0,'clone_fixture_scripts_present')
        count=await page.evaluate('() => localStorage.length')
        require(type(count) is int and count>=0,'clone_local_storage_count_invalid')
        await page.goto('about:blank',timeout=5000)
        return count,'owned_offline_origin_fixture'
    finally:
        await context.unroute(FIXTURE_URL,fixture)


async def prepare_context(manager,imported,mode,report,*,process_guard=check_browser_processes):
    require(mode in ('control','local_storage'),'clone_mode_invalid')
    report['stage']='offline_browser_start'
    page=await manager.start();context=manager.context
    require(context.pages and all(p.url=='about:blank' for p in context.pages),'clone_restored_page_rejected')
    process_guard(launched=True)
    cdp=await context.new_cdp_session(page)
    try:
        version=await cdp.send('Browser.getVersion')
        require(str(version.get('product','')).startswith('Chrome/153.'),'clone_browser_version_invalid')
        report['browser_major']=153
        report['stage']='native_cookie_import'
        await cdp.send('Network.setCookies',{'cookies':imported})
        before=(await cdp.send('Network.getAllCookies'))['cookies']
        require(cookies_import_matches(before,imported),'clone_cookie_import_readback_mismatch')
        count=sum(c.get('domain','').lstrip('.')=='chatgpt.com' for c in before)
        require(count<160,'clone_cookie_capacity_scope_invalid')
        report.update(imported_cookie_count=len(imported),cookie_count_before_clear=len(before),
                      imported_values_and_writable_metadata_verified=True)
        report['stage']='local_storage_observation_before'
        before_count,basis=await local_storage_count(context,page,cdp)
        report['local_storage_count_before']=before_count
        report['local_storage_count_before_basis']=basis
        report['stage']='local_storage_control'
        if mode=='local_storage':
            await cdp.send('Storage.clearDataForOrigin',{'origin':ORIGIN,'storageTypes':'local_storage'})
        report['clear_executed']=mode=='local_storage'
        after_count,after_basis=await local_storage_count(context,page,cdp)
        report.update(local_storage_count_after=after_count,local_storage_count_after_basis=after_basis)
        require(after_count==0 if mode=='local_storage' else after_count==before_count,
                'clone_local_storage_postcondition_failed')
        after=(await cdp.send('Network.getAllCookies'))['cookies']
        report['cookies_exactly_unchanged']=cookies_exactly_equal(before,after)
        report['cookie_count_after_clear']=len(after)
        require(report['cookies_exactly_unchanged'],'clone_cookie_changed_during_preparation')
        report['stage']='offline_preparation_verified'
    finally:
        await cdp.detach()


def closed_file_fingerprints(profile):
    result={};deadline=time.monotonic()+5
    for name,folders in CATEGORIES.items():
        files={};size=0
        try:
            for folder in folders:
                base=profile/folder
                if not base.exists():continue
                require(base.is_dir() and not base.is_symlink(),'clone_storage_boundary_invalid')
                for path in base.rglob('*'):
                    require(not path.is_symlink(),'clone_storage_boundary_invalid')
                    if not path.is_file():continue
                    size+=path.stat().st_size
                    if size>128*1024*1024 or len(files)>=10000 or time.monotonic()>deadline:
                        raise CloneError('clone_storage_observation_budget')
                    digest=hashlib.sha256()
                    with path.open('rb') as f:
                        for chunk in iter(lambda:f.read(65536),b''):digest.update(chunk)
                    files[str(path.relative_to(profile))]=digest.digest()
            result[name]={'available':True,'files':files}
        except CloneError:result[name]={'available':False}
        except OSError:result[name]={'available':False}
    return result


def closed_file_comparison(before,after):
    result={}
    for name in CATEGORIES:
        left=before.get(name,{});right=after.get(name,{})
        observed=left.get('available') is True and right.get('available') is True
        row={'observed':observed,'content_file_set_equal':None,
             'browser_housekeeping_is_not_excluded':True}
        if observed:
            a=left['files'];b=right['files']
            row.update(file_count_before=len(a),file_count_after=len(b),content_file_set_equal=a==b,
                       differing_file_count=sum(a.get(k)!=b.get(k) for k in a.keys()|b.keys()))
        result[name]=row
    return result


async def execute(mode,cookies,report):
    root=Path('/app')
    if str(root) not in sys.path:sys.path.insert(0,str(root))
    from src.config import Config
    profile_guard(Config)
    report['owned_clone_marker_verified']=True
    check_browser_processes()
    imported=convert_cookies(cookies,now=time.time())
    before=closed_file_fingerprints(PROFILE)
    # Disable production logging before importing modules that create handlers.
    from src import log
    original_logging=log.setup_logging
    log.setup_logging=lambda *args,**kwargs:logging.getLogger('owned_mg_storage_preparation')
    manager=None
    try:
        from src.browser import manager as module
        require(Path(module.__file__).resolve()==MANAGER_SOURCE,'clone_manager_source_invalid')
        manager=module.BrowserManager()
        # Capacity checking remains in the real manager. Reject a snapshot that
        # could invoke its pruning before start; no guard is disabled or replaced.
        database=PROFILE/'Default/Cookies'
        if database.exists():
            import sqlite3
            with contextlib.closing(sqlite3.connect('file:'+str(database)+'?mode=ro',uri=True)) as db:
                count=db.execute("SELECT count(*) FROM cookies WHERE host_key='chatgpt.com' OR host_key='.chatgpt.com' OR host_key LIKE '%.chatgpt.com'").fetchone()[0]
            require(count<160,'clone_cookie_capacity_scope_invalid')
        with offline_launch(module):
            await asyncio.wait_for(prepare_context(manager,imported,mode,report),timeout=45)
        report['completed']=True
    finally:
        log.setup_logging=original_logging
        if manager is not None:
            try:
                await asyncio.wait_for(manager.close(),timeout=15)
                report['no_live_browser_verified']=check_browser_processes()['no_live_browser_verified']
                report['browser_closed']=report['no_live_browser_verified']
            except BaseException:
                report['browser_closed']=False;report['completed']=False
                report['cleanup_error_code']='clone_browser_close_unverified'
        after=closed_file_fingerprints(PROFILE) if report.get('browser_closed') else {}
        report['closed_storage_file_comparison']=closed_file_comparison(before,after)
        imported=cookies=None


class _Discard:
    def write(self,value):return len(value)
    def flush(self):pass


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',required=True,choices=('control','local_storage'))
    args=parser.parse_args(argv)
    report={'schema':1,'mode':args.mode,'completed':False,'stage':'input_validation',
            'offline_launch_required':True,'network_none_externally_required':True,
            'source_mounts_forbidden_externally':True,'account_navigation_performed':False,
            'model_generation_permitted':False,'clear_executed':False,
            'cookies_keys_values_or_fingerprints_logged':False,
            'other_storage_types_requested_for_clear':False,'browser_closed':False}
    old_disabled=logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        with contextlib.redirect_stdout(_Discard()),contextlib.redirect_stderr(_Discard()):
            raw=sys.stdin.buffer.read(MAX_STDIN+1)
            require(0<len(raw)<=MAX_STDIN,'clone_input_size_invalid')
            try:data=json.loads(raw)
            except Exception:raise CloneError('clone_input_json_invalid') from None
            require(type(data) is dict and set(data)=={'cookies'},'clone_input_schema_invalid')
            asyncio.run(execute(args.mode,data['cookies'],report))
            raw=data=None
    except CloneError as error:
        report.update(completed=False,error_code=str(error),error_type='CloneError')
    except BaseException as error:
        report.update(completed=False,error_code='clone_preparation_failed',
                      error_type='timeout' if isinstance(error,(TimeoutError,asyncio.TimeoutError)) else 'operation_failed')
        report['exception_class']=type(error).__name__
        if report.get('stage')=='offline_browser_start':
            message=str(error).lower()
            patterns={'executable_missing':"executable doesn't exist",
                'permission_denied':'permission denied','eacces':'eacces',
                'display_missing':'missing x server','display_mentioned':'display',
                'launch_target_closed':'target page, context or browser has been closed',
                'protocol_error':'protocol error','dependency_missing':'missing dependencies',
                'spawn_failure':'spawn','profile_access':'data directory',
                'operation_not_permitted':'operation not permitted'}
            report['launch_error_categories']=[code for code,pattern in patterns.items() if pattern in message]
            message=None
        # Stack locations only: no exception text, locals or cookie material.
        report['exception_locations']=[{'file':Path(frame.filename).name,
            'line':frame.lineno,'function':frame.name}
            for frame in traceback.extract_tb(error.__traceback__)[-12:]]
    finally:logging.disable(old_disabled)
    try:
        report['container_memory_peak_bytes']=int(Path('/sys/fs/cgroup/memory.peak').read_text().strip())
    except (OSError,ValueError):
        report['container_memory_peak_bytes']=None
    print(json.dumps(report,sort_keys=True),flush=True)
    return 0 if report['completed'] and report['browser_closed'] else 1


if __name__=='__main__':raise SystemExit(main())
