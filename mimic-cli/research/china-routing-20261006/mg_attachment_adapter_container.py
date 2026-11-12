"""Research-only adapter: existing mg standard UI checks plus explicit local text files. Never restart or close the existing browser/context."""
import asyncio,json,sys,hashlib,types
from pathlib import Path
from patchright.async_api import async_playwright
from src.api.browser_gate import configure_tab_pool
from src.chatgpt.client import ChatGPTClient
from src.config import Config

async def main():
    manifest=json.loads(Path(sys.argv[1]).read_text())
    files=manifest['files']
    for entry in files:
        if hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Attachment hash mismatch')
    source=Path('/app/src/api/standard_completion.py').read_text()
    needle='model="gpt-5.6-sol", reasoning_effort="xhigh")'
    assert source.count(needle)==1
    source=source.replace(needle,'model="gpt-5.6-sol", reasoning_effort="xhigh", file_paths=RESEARCH_ATTACHMENT_PATHS)')
    module=types.ModuleType('research_standard_attachment')
    module.__dict__['RESEARCH_ATTACHMENT_PATHS']=[e['path'] for e in files]
    exec(compile(source,'research_standard_attachment_adapter','exec'),module.__dict__)
    original_upload=ChatGPTClient._upload_files
    original_ready=ChatGPTClient._wait_for_attachments_ready
    async def checked_upload(self, paths):
        self._research_expected_names=[Path(p).name for p in paths]
        inputs=await self.page.query_selector_all("input[type='file']")
        general=[e for e in inputs if not (await e.get_attribute('accept') or '')]
        if not general:raise RuntimeError('No general attachment input; no message submitted')
        # The page contains a hidden stale composer before the live temporary-chat composer.
        await general[-1].set_input_files(paths)
        for attempt in range(120):
            visible=await self.page.evaluate('''() => Array.from(document.querySelectorAll('body *')).filter(e=>e.children.length===0 && !e.closest('[contenteditable],textarea') && e.getBoundingClientRect().width>0 && e.getBoundingClientRect().height>0).map(e=>e.textContent||'').join('\\n')''')
            if all(name in visible for name in self._research_expected_names):break
            await asyncio.sleep(.5)
        else:raise RuntimeError('No visible attachment chip after selecting files; no message submitted')
    async def checked_ready(self, max_wait_seconds=60.0):
        state=await original_ready(self,max_wait_seconds)
        expected=getattr(self,'_research_expected_names',[])
        snapshot=await self.page.evaluate('''() => ({text:document.body.innerText, inputs:Array.from(document.querySelectorAll('input[type=file]')).map(e=>({accept:e.accept,files:Array.from(e.files||[]).map(f=>({name:f.name,size:f.size}))}))})''')
        Path(manifest['result']).with_name('upload-dom.json').write_text(json.dumps(snapshot,ensure_ascii=False))
        await self.page.screenshot(path=str(Path(manifest['result']).with_name('attachment-before-send.png')),full_page=True)
        visible=await self.page.evaluate('''() => Array.from(document.querySelectorAll('body *')).filter(e=>e.children.length===0 && !e.closest('[contenteditable],textarea') && e.getBoundingClientRect().width>0 && e.getBoundingClientRect().height>0).map(e=>e.textContent||'').join('\\n')''')
        missing=[name for name in expected if name not in visible]
        if missing:raise RuntimeError('Attachment filename absent from visible composer; no message submitted: '+','.join(missing))
        await asyncio.sleep(8)
        return state
    ChatGPTClient._upload_files=checked_upload
    ChatGPTClient._wait_for_attachments_ready=checked_ready
    async with async_playwright() as driver:
        browser=await driver.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context=browser.contexts[0]
        created=[]
        class Adapter:
            page=None
            _context=context
            async def new_page(self):
                page=await context.new_page();created.append(page);return page
        adapter=Adapter();configure_tab_pool(adapter)
        # The original shared gateway must be idle; the coordinator permits one adapter at a time.
        base=ChatGPTClient(context.pages[0])
        request=types.SimpleNamespace(model='gpt-5.6-sol',reasoning_effort='xhigh',stream=False,thread_id=None,conversation_id=None,tools=None,read_aloud=False,n=1,reasoning=None,messages=[types.SimpleNamespace(role='user',content=Path(manifest['prompt']).read_text())])
        result=await module.execute_standard_completion(request,base,capture_probe=True)
        body=json.loads(result.body)
        body.setdefault('mimicgate_diagnostics',{})['research_attachment_transport']={'same_existing_browser':True,'existing_standard_mode_checks_retained':True,'gateway_api_not_modified':True,'files':[{'filename':Path(e['path']).name,'sha256':e['sha256'],'bytes':Path(e['path']).stat().st_size} for e in files]}
        Path(manifest['result']).write_text(json.dumps({'http_status':result.status_code,'body':body},ensure_ascii=False))
        # Only pages created by this request are closed; never browser.close or context.close.
        for page in created:
            if not page.is_closed():await page.close()
        configure_tab_pool(None)
asyncio.run(main())
