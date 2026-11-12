"""A cleared/remounted composer must not acknowledge a message that was never sent."""
import unittest
from unittest.mock import AsyncMock, patch
from src.chatgpt.client import ChatGPTClient


class SubmissionConfirmationTests(unittest.IsolatedAsyncioTestCase):
    async def run_wait(self, signatures, states):
        client = object.__new__(ChatGPTClient)
        client._page = object()
        client._composer_state = AsyncMock(side_effect=states)
        with patch('src.chatgpt.client.get_latest_user_turn_signature', AsyncMock(side_effect=signatures)), \
             patch('src.chatgpt.client.time.monotonic', side_effect=[0, 0, .6, 1.2]), \
             patch('src.chatgpt.client.asyncio.sleep', AsyncMock()):
            return await client._wait_for_message_submission('old', 'first line\nsecond line', timeout_ms=1000)

    async def test_normalized_or_cleared_editor_is_not_submission(self):
        self.assertFalse(await self.run_wait(['old', 'old'], [
            {'composerText': 'first line second line', 'hasStopButton': False},
            {'composerText': '', 'hasStopButton': False}]))

    async def test_new_user_turn_confirms(self):
        self.assertTrue(await self.run_wait(['new'], []))

    async def test_generation_confirms_without_a_user_turn_selector(self):
        self.assertTrue(await self.run_wait([None], [{'hasStopButton': True}]))


if __name__ == '__main__':
    unittest.main()
