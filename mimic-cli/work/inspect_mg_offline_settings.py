"""Inspect copied localStorage offline; never return arbitrary setting values."""
import asyncio
import hashlib
import json
import logging
from pathlib import Path
import re
import sys
import traceback
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/work')
from prepare_mg_storage_clone import offline_launch, profile_guard, check_browser_processes


def safe_name(value):
    if not isinstance(value, str) or len(value) > 160 or not re.fullmatch(r'[A-Za-z0-9_./:$ -]+', value):
        return '<redacted-key>'
    value = re.sub(r'[A-Fa-f0-9]{8}-[A-Fa-f0-9-]{20,}', '<id>', value)
    value = re.sub(r'user-[A-Za-z0-9_-]{8,}', 'user-<id>', value)
    value = re.sub(r'[A-Fa-f0-9]{16,}|\d{8,}', '<id>', value)
    return value


def shape(value, depth=0):
    if depth > 2:
        return dict(type=type(value).__name__)
    if type(value) is bool or value is None:
        return dict(type=type(value).__name__, value=value)
    if type(value) in (int, float):
        return dict(type='number')
    if isinstance(value, dict):
        return dict(type='object', fields={safe_name(k):shape(v, depth+1)
            for k,v in list(value.items())[:32]}, field_count=len(value))
    if isinstance(value, list):
        return dict(type='array', count=len(value), items=[shape(v,depth+1) for v in value[:8]])
    return dict(type='string', characters=len(str(value)))


async def inspect():
    from src.config import Config
    from src.browser import manager as manager_module
    profile_guard(Config)
    check_browser_processes()
    manager = manager_module.BrowserManager()
    report = dict(model_sent=False, network_mode='none', account_navigation=False,
                  arbitrary_values_logged=False, completed=False)
    with offline_launch(manager_module):
        try:
            page = await manager.start()
            assert all(p.url == 'about:blank' for p in manager.context.pages)
            url='https://chatgpt.com/__owned_mg_setting_inspection__'
            fulfilled=False
            async def fixture(route):
                nonlocal fulfilled
                assert route.request.url == url and route.request.method == 'GET'
                await route.fulfill(status=200,content_type='text/html',
                    body='<!doctype html><title>Owned offline setting inspection</title>')
                fulfilled=True
            await manager.context.route(url,fixture)
            await page.goto(url,wait_until='domcontentloaded',timeout=5000)
            assert fulfilled and await page.locator('script').count() == 0
            entries=await page.evaluate('() => Object.entries(localStorage)')
            result=[]
            for key, raw in entries:
                try:
                    value=json.loads(raw)
                except (ValueError,TypeError):
                    value=raw
                result.append(dict(name=safe_name(key),
                    key_sha256=hashlib.sha256(key.encode()).hexdigest(),
                    value_shape=shape(value)))
                if key == 'codex.browser.appThemes.v1' and isinstance(value,dict):
                    css=value.get('css','')
                    if isinstance(css,str) and len(css)<=65536:
                        rules=[]
                        for selector,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
                            if not re.search(r'model|reasoning|slider',selector,re.I):continue
                            properties={}
                            for prop,item in re.findall(r'([A-Za-z-]+)\s*:\s*([^;]+)',body):
                                prop=prop.strip().lower(); item=item.strip().replace('!important','').strip()
                                if prop in ('display','visibility','opacity','pointer-events'):
                                    properties[prop]=item if item in ('none','block','flex','grid','inline',
                                        'inline-flex','inline-block','hidden','visible','auto','0','1') else '<other-value>'
                            if properties:rules.append(dict(selector=safe_name(selector.strip()),properties=properties))
                        report['theme_model_visibility_rules']=rules[:32]
            persisted=await page.evaluate('''async () => {
                const existing=await indexedDB.databases();
                if (!existing.some(item=>item.name==='codex-browser-host')) return {present:false};
                return await new Promise((resolve,reject)=>{
                    const req=indexedDB.open('codex-browser-host');
                    req.onupgradeneeded=()=>{req.transaction.abort();reject(new Error('No creation'));};
                    req.onerror=()=>reject(new Error('Open failed'));
                    req.onsuccess=()=>{
                        const db=req.result;
                        if (!db.objectStoreNames.contains('records')) {db.close();resolve({present:true,record_present:false});return;}
                        const tx=db.transaction('records','readonly');
                        const query=tx.objectStore('records').get('codex.browser.persistedAtomState');
                        query.onsuccess=()=>{const value=query.result;db.close();resolve({present:true,record_present:value!==undefined,value});};
                        query.onerror=()=>{db.close();reject(new Error('Read failed'));};
                    };
                });
            }''')
            report['persisted_atom_state_present']=bool(persisted.get('record_present'))
            if persisted.get('record_present'):
                value=persisted.get('value')
                if isinstance(value,str) and len(value)<=524288:
                    try:value=json.loads(value)
                    except ValueError:pass
                report['persisted_atom_state_shape']=shape(value)
            report['local_storage_count']=len(result)
            report['local_storage']=result
            await page.goto('about:blank')
            report['completed']=True
        finally:
            await manager.close()
            report['browser_closed']=True
            report.update(check_browser_processes())
    peak=Path('/sys/fs/cgroup/memory.peak')
    report['memory_peak_bytes']=int(peak.read_text()) if peak.exists() else None
    print(json.dumps(report),flush=True)


if __name__ == '__main__':
    logging.disable(logging.CRITICAL)
    try:
        asyncio.run(inspect())
    except Exception as error:
        print(json.dumps(dict(completed=False,error_class=type(error).__name__,
            stack=[dict(file=Path(frame.filename).name,line=frame.lineno,function=frame.name)
                for frame in traceback.extract_tb(error.__traceback__)[-4:]],
            exception_text_logged=False)),flush=True)
        raise SystemExit(1)
