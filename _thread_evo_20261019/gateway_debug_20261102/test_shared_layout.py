import importlib.util
import os
import unittest
from pathlib import Path
from patchright.async_api import async_playwright

spec=importlib.util.spec_from_file_location('shared_fixed',Path(__file__).with_name(
    'detector_before_shared_layout.py' if os.environ.get('TEST_BEFORE') else 'detector_shared_layout_fixed.py'))
detector=importlib.util.module_from_spec(spec);spec.loader.exec_module(detector)


class SharedLayoutTests(unittest.IsolatedAsyncioTestCase):
    async def check(self, html, expected):
        async with async_playwright() as runtime:
            browser=await runtime.chromium.launch(headless=True,args=['--no-sandbox'])
            try:
                page=await browser.new_page()
                await page.set_content(html)
                snapshot=await page.evaluate(detector._CONVERSATION_SNAPSHOT_JS)
                self.assertEqual(snapshot['latestAssistant']['hasCopyButton'],expected)
                clicked=await page.evaluate(detector._CLICK_LATEST_COPY_BUTTON_JS,None)
                self.assertEqual(clicked['clicked'],expected)
                return await page.locator('[data-clicked]').count()
            finally:
                await browser.close()

    async def test_real_completed_review_layout(self):
        await self.check('<main>'+Path(__file__).with_name('copy_turn_fixture.html').read_text(encoding='utf-8')+'</main>',True)

    async def test_shared_body_and_separate_action_bar(self):
        clicked=await self.check('''<main><div data-content-search-turn-key="t"><div data-talvt-turn-state="complete">
          <div><div data-content-search-unit-key="t:0:user">Question<button aria-label="Copy">user</button></div>
          <div><div data-content-search-unit-key="t:2:assistant">Complete answer<pre><button aria-label="Copy code">code</button></pre></div></div></div>
          <div><button aria-label="Copy" onclick="this.dataset.clicked='yes'">right</button></div>
          </div></div></main>''',True)
        self.assertEqual(clicked,1)

    async def test_following_user_bar_still_rejected(self):
        await self.check('''<main><div data-content-search-turn-key="t"><div data-content-search-unit-key="t:0:assistant">Answer</div>
          <div><div data-content-search-unit-key="t:1:user">Next</div><button aria-label="Copy">wrong</button></div></div></main>''',False)

    async def test_preceding_user_copy_only_still_rejected(self):
        await self.check('''<main><div data-content-search-turn-key="t"><div data-content-search-unit-key="t:0:user">Question</div>
          <button aria-label="Copy">wrong</button><div data-content-search-unit-key="t:2:assistant">Answer</div></div></main>''',False)


if __name__=='__main__':unittest.main()
