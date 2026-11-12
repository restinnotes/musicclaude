"""Real DOM regression: user Copy within a shared turn is not assistant Copy."""
import unittest
import os
import importlib.util
from pathlib import Path
from patchright.async_api import async_playwright
from src.chatgpt import detector

if os.environ.get('TEST_FIXED_READER') == '1':
    spec = importlib.util.spec_from_file_location('boundary_fixed', Path(__file__).with_name('detector_copy_boundary_fixed.py'))
    detector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(detector)


class CopyBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_nearby_user_copy_after_assistant_is_not_borrowed(self):
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                page = await browser.new_page()
                await page.set_content('''<main>
                  <div data-content-search-unit-key="turn-0:assistant">Complete answer</div>
                  <div><div data-content-search-unit-key="turn-1:user">Question</div>
                    <button aria-label="Copy" onclick="this.dataset.clicked='yes'">Copy</button></div>
                </main>''')
                snapshot = await page.evaluate(detector._CONVERSATION_SNAPSHOT_JS)
                self.assertFalse(snapshot['latestAssistant']['hasCopyButton'])
                click = await page.evaluate(detector._CLICK_LATEST_COPY_BUTTON_JS, None)
                self.assertFalse(click['clicked'])
                self.assertIsNone(await page.locator('button').get_attribute('data-clicked'))
            finally:
                await browser.close()

    async def test_shared_turn_user_copy_never_finishes_empty_assistant(self):
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                page = await browser.new_page()
                await page.set_content('''<main><div data-content-search-turn-key="turn-0">
                  <div data-content-search-unit-key="turn-0:user">Question</div>
                  <button aria-label="Copy" onclick="this.dataset.clicked='yes'">Copy</button>
                  <div data-content-search-unit-key="turn-0:assistant"><h4>ChatGPT said:</h4>
                    <div data-markdown-text-style="assistant-message"></div></div>
                </div></main>''')
                snapshot = await page.evaluate(detector._CONVERSATION_SNAPSHOT_JS)
                self.assertFalse(snapshot['latestAssistant']['hasCopyButton'])
                click = await page.evaluate(detector._CLICK_LATEST_COPY_BUTTON_JS, None)
                self.assertFalse(click['clicked'])
                self.assertIsNone(await page.locator('button').get_attribute('data-clicked'))
            finally:
                await browser.close()

    async def test_assistant_sibling_copy_in_shared_turn_still_works(self):
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                page = await browser.new_page()
                await page.set_content('''<main><div data-content-search-turn-key="turn-0">
                  <div><div data-content-search-unit-key="turn-0:user">Question</div>
                    <button id="wrong" aria-label="Copy" onclick="this.dataset.clicked='yes'">Copy</button></div>
                  <div><div data-content-search-unit-key="turn-0:assistant">
                    <div data-markdown-text-style="assistant-message">Complete answer</div></div>
                    <button id="right" aria-label="Copy" onclick="this.dataset.clicked='yes'">Copy</button></div>
                </div></main>''')
                snapshot = await page.evaluate(detector._CONVERSATION_SNAPSHOT_JS)
                self.assertTrue(snapshot['latestAssistant']['hasCopyButton'])
                click = await page.evaluate(detector._CLICK_LATEST_COPY_BUTTON_JS, None)
                self.assertTrue(click['clicked'])
                self.assertEqual(await page.locator('#right').get_attribute('data-clicked'), 'yes')
                self.assertIsNone(await page.locator('#wrong').get_attribute('data-clicked'))
            finally:
                await browser.close()


    async def test_shared_body_user_before_assistant_and_external_action_bar(self):
        async with async_playwright() as runtime:
            browser = await runtime.chromium.launch(headless=True, args=['--no-sandbox'])
            try:
                page = await browser.new_page()
                await page.set_content('''<main><div data-content-search-turn-key="turn-0">
                  <div data-talvt-turn-state="complete"><div>
                    <div data-content-search-unit-key="turn-0:0:user">Question
                      <button id="user" aria-label="Copy message">wrong</button></div>
                    <div><div data-content-search-unit-key="turn-0:2:assistant">Complete answer</div></div>
                  </div><div><button id="assistant" aria-label="Copy"
                    onclick="this.dataset.clicked='yes'">right</button></div></div>
                </div></main>''')
                snapshot = await page.evaluate(detector._CONVERSATION_SNAPSHOT_JS)
                self.assertTrue(snapshot['latestAssistant']['hasCopyButton'])
                click = await page.evaluate(detector._CLICK_LATEST_COPY_BUTTON_JS, None)
                self.assertTrue(click['clicked'])
                self.assertEqual(await page.locator('#assistant').get_attribute('data-clicked'), 'yes')
                self.assertIsNone(await page.locator('#user').get_attribute('data-clicked'))
            finally:
                await browser.close()


if __name__ == '__main__':
    unittest.main()
