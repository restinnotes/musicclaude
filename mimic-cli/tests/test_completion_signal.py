"""Regression: a Copy button cannot finish a response while Stop is active."""
import unittest
from unittest.mock import AsyncMock, patch
from src.chatgpt import detector

class CompletionSignalTests(unittest.IsolatedAsyncioTestCase):
    async def test_copy_during_generation_waits_for_stop_to_disappear(self):
        snapshots = [
            {'signature': 'new', 'hasCopyButton': True, 'hasStopButton': True},
            {'signature': 'new', 'hasCopyButton': True, 'hasStopButton': False},
        ]
        with patch.object(detector, '_latest_assistant_turn_snapshot', AsyncMock(side_effect=snapshots)) as read, \
             patch.object(detector.asyncio, 'sleep', AsyncMock()), \
             patch.object(detector.Config, 'POLL_INTERVAL_MS', 1):
            result = await detector._wait_for_copy_button_or_image(object(), 0, 100, 'old')
            self.assertEqual(result, 'copy')
            self.assertEqual(read.await_count, 2)

    async def test_copy_count_fallback_cannot_override_stop(self):
        snapshots = [
            {'signature': 'new', 'hasCopyButton': False, 'hasStopButton': True},
            {'signature': 'new', 'hasCopyButton': True, 'hasStopButton': False},
        ]
        with patch.object(detector, '_latest_assistant_turn_snapshot', AsyncMock(side_effect=snapshots)) as read, \
             patch.object(detector, '_count_copy_buttons', AsyncMock(return_value=1)) as count, \
             patch.object(detector.asyncio, 'sleep', AsyncMock()), \
             patch.object(detector.Config, 'POLL_INTERVAL_MS', 1):
            result = await detector._wait_for_copy_button_or_image(object(), 0, 100, None)
            self.assertEqual(result, 'copy')
            self.assertEqual(read.await_count, 2)
            count.assert_not_awaited()

if __name__ == '__main__':
    unittest.main()
