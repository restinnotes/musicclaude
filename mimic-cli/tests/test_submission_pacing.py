import asyncio
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('pacing',Path(__file__).resolve().parents[1]/'src/api/submission_pacing.py')
pacing=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pacing)

class PacingTests(unittest.IsolatedAsyncioTestCase):
    async def test_first_attempt_does_not_wait(self):
        pacing._last_attempt_monotonic=None
        result=await pacing.wait_for_submission_slot()
        self.assertEqual(result['waited_seconds'],0)

    async def test_next_tab_waits_until_five_seconds(self):
        now=[10.0]
        async def advance(delay):
            now[0]+=delay
        pacing._last_attempt_monotonic=None
        with patch.object(pacing.time,'monotonic',side_effect=lambda:now[0]),patch.object(pacing.asyncio,'sleep',advance):
            pacing.record_submission_attempt()
            now[0]+=1
            result=await pacing.wait_for_submission_slot()
            second=pacing.record_submission_attempt()
        self.assertEqual(result['waited_seconds'],4)
        self.assertEqual(second['previous_attempt_gap_seconds'],5)

    async def test_existing_long_gap_has_no_extra_delay(self):
        pacing._last_attempt_monotonic=10
        with patch.object(pacing.time,'monotonic',return_value=23):
            result=await pacing.wait_for_submission_slot()
        self.assertEqual(result['waited_seconds'],0)

if __name__=='__main__':
    unittest.main()
