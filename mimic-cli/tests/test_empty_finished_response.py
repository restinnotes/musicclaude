import unittest
from unittest.mock import AsyncMock, patch
from src.chatgpt import detector
from src.chatgpt.standard_mode import StandardStateError


class EmptyFinishedTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, snapshots, clock):
        with patch.object(detector, 'raise_on_response_error', AsyncMock()), \
             patch.object(detector, '_latest_assistant_turn_snapshot', AsyncMock(side_effect=snapshots)), \
             patch.object(detector, '_conversation_snapshot', AsyncMock(return_value={})), \
             patch.object(detector, 'capture_response_diagnostics', AsyncMock()), \
             patch.object(detector, '_count_copy_buttons', AsyncMock(return_value=0)), \
             patch.object(detector.asyncio, 'sleep', AsyncMock()), \
             patch.object(detector.time, 'monotonic', side_effect=clock), \
             patch.object(detector.Config, 'POLL_INTERVAL_MS', 1000):
            return await detector._wait_for_copy_button_or_image(object(), 0, 100000, 'old')

    async def test_stopped_blank_turn_fails_after_grace(self):
        blank = {'signature':'new', 'text':'ChatGPT said:', 'hasStopButton':False}
        with self.assertRaises(StandardStateError) as caught:
            await self.exercise([
                {'signature':'new','hasStopButton':True}, blank, blank], [0,31])
        self.assertEqual(caught.exception.kind, 'incomplete_response')

    async def test_delayed_body_within_grace_can_succeed(self):
        result = await self.exercise([
            {'signature':'new','hasStopButton':True},
            {'signature':'new','text':'ChatGPT said:','hasStopButton':False},
            {'signature':'new','text':'Complete answer','hasStopButton':False,'hasCopyButton':True}], [0])
        self.assertEqual(result, 'copy')

    async def test_resumed_generation_resets_blank_grace(self):
        blank = {'signature':'new','text':'ChatGPT said:','hasStopButton':False}
        result = await self.exercise([
            {'signature':'new','hasStopButton':True}, blank,
            {'signature':'new','hasStopButton':True}, blank,
            {'signature':'new','text':'Complete answer','hasStopButton':False,'hasCopyButton':True}], [0,100])
        self.assertEqual(result, 'copy')


if __name__ == '__main__':
    unittest.main()
