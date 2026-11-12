"""Real DOM regressions, no account/profile/network or model requests."""
import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from patchright.async_api import async_playwright

def module(name, filename):
    spec=importlib.util.spec_from_file_location(name,Path(__file__).parent/filename)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

before=module('reader_before','detector_before.py')
fixed=module('reader_fixed','detector_fixed.py')
guard=module('guard_fixed','completion_guard_fixed.py')

class ReaderDOMTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.runtime=await async_playwright().start()
        self.browser=await self.runtime.chromium.launch(headless=True,args=['--no-sandbox'])
        self.page=await self.browser.new_page()

    async def asyncTearDown(self):
        await self.browser.close()
        await self.runtime.stop()

    async def markup(self,body):
        await self.page.set_content('<main>'+body+'</main>')

    async def test_sibling_action_bar_reproduces_old_bug(self):
        await self.markup('''<div><div data-content-search-unit-key="turn:assistant"><div data-markdown-text-style="assistant-message">A complete response.</div></div><div><button aria-label="Copy" onclick="this.dataset.clicked='yes'">Copy</button></div></div>''')
        old=await self.page.evaluate(before._CONVERSATION_SNAPSHOT_JS)
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertFalse(old['latestAssistant']['hasCopyButton'])
        self.assertTrue(new['latestAssistant']['hasCopyButton'])
        clicked=await self.page.evaluate(fixed._CLICK_LATEST_COPY_BUTTON_JS,None)
        self.assertTrue(clicked['clicked'])
        self.assertEqual(await self.page.locator('button').get_attribute('data-clicked'),'yes')

    async def test_semantic_body_does_not_become_accessibility_header(self):
        await self.markup('''<div data-content-search-unit-key="turn:assistant"><h4>ChatGPT said:</h4><div data-markdown-text-style="assistant-message" style="display:none">A complete response hidden during layout replacement.</div></div>''')
        old=await self.page.evaluate(before._CONVERSATION_SNAPSHOT_JS)
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertEqual(old['latestAssistant']['text'],'ChatGPT said:')
        self.assertEqual(new['latestAssistant']['text'],'A complete response hidden during layout replacement.')

    async def test_empty_answer_stays_incomplete(self):
        await self.markup('''<div><div data-content-search-unit-key="turn:assistant"><h4>ChatGPT said:</h4><div data-markdown-text-style="assistant-message"></div></div><button aria-label="Copy">Copy</button></div>''')
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertTrue(fixed.is_incomplete_response_text(new['latestAssistant']['text']))
        self.assertEqual(await fixed._extract_via_dom(self.page), '')

    async def test_user_copy_is_never_borrowed(self):
        await self.markup('''<div><div data-content-search-unit-key="turn:user">Question</div><button aria-label="Copy">Copy</button><div data-content-search-unit-key="turn:assistant"><div data-markdown-text-style="assistant-message">A complete response.</div></div></div>''')
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertFalse(new['latestAssistant']['hasCopyButton'])
        self.assertFalse((await self.page.evaluate(fixed._CLICK_LATEST_COPY_BUTTON_JS,None))['clicked'])

    async def test_old_turn_copy_is_never_borrowed(self):
        await self.markup('''<div><div data-content-search-unit-key="old:assistant">Older answer</div><button aria-label="Copy">Copy</button><div data-content-search-unit-key="new:assistant">New answer</div></div>''')
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertFalse(new['latestAssistant']['hasCopyButton'])

    async def test_code_copy_is_never_response_copy(self):
        await self.markup('''<div><div data-content-search-unit-key="turn:assistant">A complete response.</div><pre><button aria-label="Copy">Copy</button></pre></div>''')
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertFalse(new['latestAssistant']['hasCopyButton'])

    async def test_stop_control_still_blocks_completion(self):
        await self.markup('''<div><div data-content-search-unit-key="turn:assistant">A complete response.</div><button aria-label="Copy">Copy</button></div><button data-testid="stop-button">Stop</button>''')
        new=await self.page.evaluate(fixed._CONVERSATION_SNAPSHOT_JS)
        self.assertTrue(new['latestAssistant']['hasCopyButton'])
        self.assertTrue(new['hasStopButton'])

    async def test_literal_error_inside_new_body_is_not_a_ui_error(self):
        await self.markup('''<div data-content-search-unit-key="turn:user">question</div><div data-content-search-unit-key="turn:assistant"><div data-markdown-text-style="assistant-message">Error in message stream</div></div>''')
        state=await self.page.evaluate(guard._RESPONSE_ERROR_JS)
        self.assertIsNone(state['error'])

    async def test_actual_ui_error_stays_failure(self):
        await self.markup('''<div data-content-search-unit-key="turn:user">question</div><div data-content-search-unit-key="turn:assistant"><div data-markdown-text-style="assistant-message">partial text</div><div>Error in message stream</div></div>''')
        state=await self.page.evaluate(guard._RESPONSE_ERROR_JS)
        self.assertEqual(state['error'],'message_stream_error')

    async def test_explicit_suspicious_warning_is_preserved(self):
        for text in ["We've detected suspicious activity from your device.", 'Unusual activity has been detected from your device.', 'Our systems have detected unusual activity from your system.', '检测到可疑行为，请稍后再试']:
            with self.subTest(text=text):
                await self.markup('<div data-content-search-unit-key="turn:user">question</div><div role="alert">'+text+'</div>')
                self.assertEqual((await self.page.evaluate(guard._RESPONSE_ERROR_JS))['error'],'suspicious_behavior')
                with self.assertRaises(guard.StandardStateError) as caught:
                    await guard.raise_on_response_error(self.page)
                self.assertEqual(caught.exception.kind,'suspicious_behavior')

    async def test_quoted_warning_in_prompt_or_answer_is_not_a_protection_signal(self):
        await self.markup('''<div data-content-search-unit-key="turn:user">Suspicious behavior</div><div data-content-search-unit-key="turn:assistant"><div data-markdown-text-style="assistant-message">We've detected suspicious activity from your device.</div></div>''')
        self.assertIsNone((await self.page.evaluate(guard._RESPONSE_ERROR_JS))['error'])

class ClipboardTests(unittest.IsolatedAsyncioTestCase):
    async def test_identical_answer_is_valid_after_clipboard_was_cleared(self):
        page=SimpleNamespace(context=SimpleNamespace(grant_permissions=AsyncMock()),
            evaluate=AsyncMock(side_effect=['A complete response.',True,{'clicked':True,'signature':'new'},'A complete response.']))
        with patch.object(fixed,'_latest_assistant_turn_snapshot',AsyncMock(return_value={})),patch.object(fixed.asyncio,'sleep',AsyncMock()):
            self.assertEqual(await fixed._extract_last_response_via_copy_unlocked(page),'A complete response.')

    async def test_unchanged_clipboard_is_rejected_when_clear_failed(self):
        page=SimpleNamespace(context=SimpleNamespace(grant_permissions=AsyncMock()),
            evaluate=AsyncMock(side_effect=['old response',False,{'clicked':True,'signature':'new'},'old response']))
        with patch.object(fixed,'_latest_assistant_turn_snapshot',AsyncMock(return_value={})),patch.object(fixed.asyncio,'sleep',AsyncMock()),patch.object(fixed,'_extract_via_dom',AsyncMock(return_value='')):
            self.assertEqual(await fixed._extract_last_response_via_copy_unlocked(page),'')

if __name__=='__main__':unittest.main(verbosity=2)
