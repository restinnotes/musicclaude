import asyncio
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

spec=importlib.util.spec_from_file_location('prepare_mg_storage_clone',
    Path(__file__).with_name('prepare_mg_storage_clone.py'))
probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)


def cookies():
    common={'domain':'.chatgpt.com','path':'/','expires':9999,'secure':True,'httpOnly':True,
            'sameSite':'None','priority':'Medium','sourceScheme':'Secure','sourcePort':443,
            'size':100,'session':False}
    return [{**common,'name':'__Secure-next-auth.session-token','value':'PRIVATE-SESSION'},
            {**common,'name':'oai-did','value':'PRIVATE-DEVICE'},
            {**common,'name':'cf_clearance','value':'PRIVATE-CLEARANCE','partitionKey':
             {'topLevelSite':probe.ORIGIN,'hasCrossSiteAncestor':False}}]


def test_native_cdp_converter_preserves_writable_metadata_without_mutating_or_flattening():
    original=cookies();before=copy.deepcopy(original)
    result=probe.convert_cookies(original,now=100)
    assert original==before
    assert result[-1]['partitionKey']==original[-1]['partitionKey']
    assert all('size' not in c and 'session' not in c for c in result)
    assert all(c['sameSite']=='None' and c['priority']=='Medium' and c['sourcePort']==443 for c in result)
    result[-1]['partitionKey']['topLevelSite']='modified'
    assert original==before


@pytest.mark.parametrize('mutation',['foreign','expired','opaque','partition-ancestor','partition-site',
    'duplicate','temporary','sameSite','sourcePort','no-auth','no-device','empty-auth','expiry-bool'])
def test_bad_cookie_metadata_rejected_with_static_errors(mutation):
    value=cookies()
    if mutation=='foreign':value[0]['domain']='private.example'
    elif mutation=='expired':value[0]['expires']=10
    elif mutation=='opaque':value[0]['partitionKeyOpaque']=True
    elif mutation=='partition-ancestor':value[-1]['partitionKey']['hasCrossSiteAncestor']=True
    elif mutation=='partition-site':value[-1]['partitionKey']['topLevelSite']='https://private.example'
    elif mutation=='duplicate':value.append(copy.deepcopy(value[0]))
    elif mutation=='temporary':value[-1]['name']='conv_key_PRIVATE-ID'
    elif mutation=='sameSite':value[0]['sameSite']='PRIVATE-FLAG'
    elif mutation=='sourcePort':value[0]['sourcePort']=True
    elif mutation=='no-auth':value.pop(0)
    elif mutation=='no-device':value.pop(1)
    elif mutation=='empty-auth':value[0]['value']=''
    else:value[0]['expires']=True
    with pytest.raises(probe.CloneError) as raised:probe.convert_cookies(value,now=100)
    assert 'PRIVATE' not in str(raised.value) and 'example' not in str(raised.value)


def test_session_expiry_and_missing_same_site_remain_native_semantics():
    value=cookies();value[0]['expires']=-1;value[0].pop('sameSite')
    converted=probe.convert_cookies(value,now=100)
    assert converted[0]['expires']==-1 and 'sameSite' not in converted[0]


@pytest.mark.parametrize('change',['missing-marker','wrong-marker','other-profile','other-channel'])
def test_owned_profile_marker_and_browser_channel_are_required_before_launch(tmp_path,monkeypatch,change):
    profile=tmp_path/'profile';profile.mkdir();executable=tmp_path/'chrome';executable.write_bytes(b'offline-fixture')
    monkeypatch.setattr(probe,'PROFILE',profile)
    monkeypatch.setattr(probe,'EXECUTABLE',executable)
    monkeypatch.setattr(probe.platform,'system',lambda:'Linux')
    marker=profile/probe.MARKER
    marker.write_text(json.dumps({'schema':1,'owned_clone':True,'source_profile_mounted':False,
                                  'network_isolated':True}))
    config=SimpleNamespace(BROWSER_DATA_DIR=profile,BROWSER_CHANNEL='chromium')
    probe.profile_guard(config)
    if change=='missing-marker':marker.unlink()
    elif change=='wrong-marker':marker.write_text('{"owned_clone":true,"PRIVATE":true}')
    elif change=='other-profile':config.BROWSER_DATA_DIR=tmp_path/'private-profile'
    else:config.BROWSER_CHANNEL='msedge'
    with pytest.raises(probe.CloneError) as raised:probe.profile_guard(config)
    assert 'PRIVATE' not in str(raised.value)


class CDP:
    def __init__(self,context,*,blank_read_fails=False,mutate_cookie=False):
        self.context=context;self.commands=[];self.blank_read_fails=blank_read_fails
        self.mutate_cookie=mutate_cookie;self.get_cookie_calls=0;self.detached=False
    async def send(self,command,args=None):
        self.commands.append((command,copy.deepcopy(args)))
        if command=='Browser.getVersion':return {'product':'Chrome/153.0.8010.12'}
        if command=='Network.setCookies':
            self.context.cookies=copy.deepcopy(args['cookies']);return {}
        if command=='Network.getAllCookies':
            self.get_cookie_calls+=1
            result=copy.deepcopy(self.context.cookies)
            if self.mutate_cookie and self.get_cookie_calls>1:result[0]['value']='PRIVATE-CHANGED'
            return {'cookies':result}
        if command=='DOMStorage.getDOMStorageItems':
            assert args=={'storageId':{'securityOrigin':probe.ORIGIN,'isLocalStorage':True}}
            if self.blank_read_fails:raise RuntimeError('PRIVATE-CDP-ERROR')
            return {'entries':[['PRIVATE-KEY','PRIVATE-VALUE']]*self.context.local_count}
        if command=='Storage.clearDataForOrigin':
            assert args=={'origin':probe.ORIGIN,'storageTypes':'local_storage'}
            self.context.local_count=0;return {}
        raise AssertionError(command)
    async def detach(self):self.detached=True


class Page:
    def __init__(self,context,url='about:blank'):self.context=context;self.url=url;self.navigations=[]
    async def goto(self,url,**kwargs):
        self.navigations.append(url)
        assert url in ('about:blank',probe.FIXTURE_URL)
        if url==probe.FIXTURE_URL:
            assert self.context.handler is not None
            class Route:
                request=SimpleNamespace(url=url,method='GET')
                async def fulfill(inner,**options):
                    assert options['status']==200 and '<script' not in options['body']
                    self.context.fulfilled=True
            await self.context.handler(Route())
        self.url=url
    async def evaluate(self,code):
        assert code=='() => localStorage.length'
        assert self.context.fulfilled and self.url==probe.FIXTURE_URL
        return self.context.local_count
    async def title(self):return probe.FIXTURE_TITLE
    def locator(self,selector):
        assert selector=='script'
        class Locator:
            async def count(self):return 0
        return Locator()


class Context:
    def __init__(self,**kwargs):
        self.local_count=2;self.cookies=[];self.handler=None;self.fulfilled=False
        self.page=Page(self);self.pages=[self.page];self.cdp=CDP(self,**kwargs)
    async def new_cdp_session(self,page):assert page is self.page;return self.cdp
    async def route(self,url,handler):assert url==probe.FIXTURE_URL;self.handler=handler
    async def unroute(self,url,handler):assert self.handler is handler;self.handler=None


class Manager:
    def __init__(self,context):self.context=context
    async def start(self):return self.context.page


@pytest.mark.parametrize('mode',['control','local_storage'])
@pytest.mark.parametrize('fallback',[False,True])
def test_offline_context_control_or_exact_clear_preserves_cookies_and_has_no_account_navigation(mode,fallback):
    context=Context(blank_read_fails=fallback);report={}
    asyncio.run(probe.prepare_context(Manager(context),probe.convert_cookies(cookies(),now=100),mode,report,
                                     process_guard=lambda **kwargs:None))
    clears=[x for x in context.cdp.commands if x[0]=='Storage.clearDataForOrigin']
    assert len(clears)==(mode=='local_storage')
    assert report['cookies_exactly_unchanged'] is True
    assert report['local_storage_count_before']==2
    assert report['local_storage_count_after']==(0 if mode=='local_storage' else 2)
    assert context.cdp.detached and context.handler is None
    assert context.page.url=='about:blank'
    assert 'PRIVATE' not in json.dumps(report)
    assert all(x in (probe.FIXTURE_URL,'about:blank') for x in context.page.navigations)


def test_cookie_change_rejected_without_printing_changed_value():
    context=Context(mutate_cookie=True);report={}
    with pytest.raises(probe.CloneError,match='^clone_cookie_changed_during_preparation$'):
        asyncio.run(probe.prepare_context(Manager(context),probe.convert_cookies(cookies(),now=100),
            'local_storage',report,process_guard=lambda **kwargs:None))
    assert context.cdp.detached and 'PRIVATE' not in json.dumps(report)


@pytest.mark.parametrize('change,code',[
    ('service-worker','clone_fixture_not_fulfilled'),
    ('title','clone_fixture_document_invalid'),
    ('url','clone_fixture_document_invalid'),
    ('script','clone_fixture_scripts_present'),
])
def test_fixture_fallback_rejects_unfulfilled_or_nonempty_document_before_storage_read(change,code):
    context=Context(blank_read_fails=True)
    class UntrustedPage(Page):
        async def goto(self,url,**kwargs):
            if change=='service-worker':
                self.url=url  # SW returned a cached page; route handler was never called.
                return
            await super().goto(url,**kwargs)
            if change=='url':self.url='https://chatgpt.com/PRIVATE-CACHED-PAGE'
        async def title(self):
            return 'PRIVATE-CACHED-TITLE' if change=='title' else probe.FIXTURE_TITLE
        def locator(self,selector):
            assert selector=='script'
            class Locator:
                async def count(self):return 1 if change=='script' else 0
            return Locator()
        async def evaluate(self,code):pytest.fail('Untrusted document must never be used to read storage')
    page=UntrustedPage(context);context.page=page;context.pages=[page]
    with pytest.raises(probe.CloneError,match='^'+code+'$') as raised:
        asyncio.run(probe.local_storage_count(context,page,context.cdp))
    assert 'PRIVATE' not in str(raised.value) and context.handler is None
    assert not any(command[0]=='Storage.clearDataForOrigin' for command in context.cdp.commands)


def test_restored_account_page_rejected_before_cookie_import_or_clear():
    context=Context();context.page.url=probe.ORIGIN;report={}
    with pytest.raises(probe.CloneError,match='^clone_restored_page_rejected$'):
        asyncio.run(probe.prepare_context(Manager(context),cookies(),'local_storage',report,
                                         process_guard=lambda **kwargs:None))
    assert context.cdp.commands==[]


def test_offline_wrapper_preserves_all_real_manager_launch_arguments_except_offline(monkeypatch):
    # Test the Linux absolute-path contract without launching anything on Windows.
    monkeypatch.setattr(probe,'PROFILE',probe.PROFILE.resolve())
    monkeypatch.setattr(probe,'EXECUTABLE',probe.EXECUTABLE.resolve())
    launched=[]
    class Chromium:
        executable_path=str(probe.EXECUTABLE)
        async def launch_persistent_context(self,**kwargs):launched.append(kwargs);return 'context'
    actual=SimpleNamespace(chromium=Chromium(),stop=lambda:None)
    class Factory:
        async def start(self):return actual
    module=SimpleNamespace(async_playwright=Factory)
    options={'user_data_dir':str(probe.PROFILE),'headless':False,'slow_mo':99,'locale':'en-US',
             'timezone_id':'America/Los_Angeles','args':['--existing-flag'],'no_viewport':True}
    before=copy.deepcopy(options)
    async def flow():
        with probe.offline_launch(module):
            wrapped=await module.async_playwright().start()
            assert await wrapped.chromium.launch_persistent_context(**options)=='context'
        assert module.async_playwright is Factory
    asyncio.run(flow())
    assert options==before and launched==[{**before,'offline':True}]


@pytest.mark.parametrize('change',['profile','executable','channel'])
def test_launch_boundary_rejects_non_owned_profile_or_browser(change):
    class Chromium:
        executable_path=str(probe.EXECUTABLE)
        async def launch_persistent_context(self,**kwargs):pytest.fail('Boundary must fail before launch')
    actual=Chromium();options={'user_data_dir':str(probe.PROFILE)}
    if change=='profile':options['user_data_dir']='/private/profile'
    elif change=='executable':actual.executable_path='/private/browser'
    else:options['channel']='msedge'
    with pytest.raises(probe.CloneError):asyncio.run(probe._ChromiumProxy(actual).launch_persistent_context(**options))


def test_actual_chrome_configuration_preserves_original_attempt_then_bundled_fallback(tmp_path,monkeypatch):
    monkeypatch.setattr(probe,'PROFILE',tmp_path/'profile')
    monkeypatch.setattr(probe,'EXECUTABLE',tmp_path/'bundled-chrome')
    monkeypatch.setattr(probe,'VENDOR_CHROME',tmp_path/'absent-vendor-chrome')
    attempts=[]
    class Chromium:
        executable_path=str(probe.EXECUTABLE)
        async def launch_persistent_context(self,**kwargs):
            attempts.append(copy.deepcopy(kwargs))
            if kwargs.get('channel')=='chrome':raise RuntimeError('vendor Chrome not installed')
            return 'bundled-context'
    chromium=probe._ChromiumProxy(Chromium())
    original={'user_data_dir':str(probe.PROFILE),'headless':False,'slow_mo':99,
              'locale':'en-US','timezone_id':'America/Los_Angeles','args':['--original-flag']}
    async def original_manager_sequence():
        try:
            return await chromium.launch_persistent_context(channel='chrome',**original)
        except Exception:
            return await chromium.launch_persistent_context(**original)
    assert asyncio.run(original_manager_sequence())=='bundled-context'
    assert attempts==[{**original,'channel':'chrome','offline':True},{**original,'offline':True}]
    assert 'offline' not in original


def test_chrome_config_allowed_only_with_absent_vendor_and_guard_never_launches_vendor(tmp_path,monkeypatch):
    profile=tmp_path/'profile';profile.mkdir();executable=tmp_path/'bundled';executable.write_bytes(b'fixture')
    vendor=tmp_path/'vendor-chrome'
    monkeypatch.setattr(probe,'PROFILE',profile);monkeypatch.setattr(probe,'EXECUTABLE',executable)
    monkeypatch.setattr(probe,'VENDOR_CHROME',vendor)
    monkeypatch.setattr(probe.platform,'system',lambda:'Linux')
    (profile/probe.MARKER).write_text(json.dumps({'schema':1,'owned_clone':True,
        'source_profile_mounted':False,'network_isolated':True}))
    config=SimpleNamespace(BROWSER_DATA_DIR=profile,BROWSER_CHANNEL='chrome')
    probe.profile_guard(config)
    vendor.write_bytes(b'unexpected-installed-browser')
    with pytest.raises(probe.CloneError,match='^clone_vendor_chrome_unexpected$'):probe.profile_guard(config)
    class Chromium:
        executable_path=str(executable)
        async def launch_persistent_context(self,**kwargs):pytest.fail('No vendor browser may be launched')
    with pytest.raises(probe.CloneError,match='^clone_vendor_chrome_unexpected$'):
        asyncio.run(probe._ChromiumProxy(Chromium()).launch_persistent_context(
            channel='chrome',user_data_dir=str(profile)))


def test_full_cookie_comparison_includes_metadata_and_order_is_not_semantic():
    original=cookies()
    assert probe.cookies_exactly_equal(original,list(reversed(copy.deepcopy(original))))
    for field in ['value','sameSite','sourcePort','expires','partitionKey']:
        changed=copy.deepcopy(original);changed[-1][field]='PRIVATE-CHANGED'
        assert not probe.cookies_exactly_equal(original,changed)


def test_closed_storage_comparison_exposes_only_counts_and_booleans(tmp_path):
    directory=tmp_path/'Default/IndexedDB';directory.mkdir(parents=True)
    private=directory/'PRIVATE-KEY';private.write_bytes(b'PRIVATE-VALUE')
    before=probe.closed_file_fingerprints(tmp_path)
    private.write_bytes(b'PRIVATE-CHANGED')
    after=probe.closed_file_fingerprints(tmp_path)
    report=probe.closed_file_comparison(before,after)
    assert report['indexeddb']['content_file_set_equal'] is False
    assert report['indexeddb']['differing_file_count']==1
    assert report['indexeddb']['browser_housekeeping_is_not_excluded'] is True
    assert 'PRIVATE' not in json.dumps(report)


def test_main_library_exception_is_static_and_secret_stdout_stderr_discarded(monkeypatch,capsys):
    import io
    async def failed(mode,cookies,report):
        print('PRIVATE-COOKIE')
        print('PRIVATE-CREDENTIAL',file=probe.sys.stderr)
        raise RuntimeError('PRIVATE-ERROR')
    monkeypatch.setattr(probe,'execute',failed)
    monkeypatch.setattr(probe.sys,'stdin',SimpleNamespace(buffer=io.BytesIO(b'{"cookies":[]}')))
    assert probe.main(['--mode','control'])==1
    output=capsys.readouterr()
    assert not output.err and 'PRIVATE' not in output.out
    result=json.loads(output.out)
    assert result['error_code']=='clone_preparation_failed' and result['completed'] is False


def test_main_rejects_bare_cookie_list_before_any_runtime_action(monkeypatch,capsys):
    import io
    async def forbidden(*args):pytest.fail('Invalid input must never create a browser')
    monkeypatch.setattr(probe,'execute',forbidden)
    monkeypatch.setattr(probe.sys,'stdin',SimpleNamespace(buffer=io.BytesIO(b'[]')))
    assert probe.main(['--mode','local_storage'])==1
    assert json.loads(capsys.readouterr().out)['error_code']=='clone_input_schema_invalid'
