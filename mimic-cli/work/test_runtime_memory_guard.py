"""Protect against the real failure: free physical RAM with exhausted commit."""
import unittest
from unittest.mock import patch
from runtime_memory_guard import ProbeMemoryTimeline, headroom_error

class CommitHeadroomTests(unittest.TestCase):
    def test_free_physical_ram_does_not_hide_commit_exhaustion(self):
        self.assertIn('commit', headroom_error({'available_physical_gib':10,'available_commit_gib':1}))

    def test_physical_exhaustion_also_blocks(self):
        self.assertIn('physical', headroom_error({'available_physical_gib':2,'available_commit_gib':10}))

    def test_both_headrooms_allow_probe(self):
        self.assertIsNone(headroom_error({'available_physical_gib':3,'available_commit_gib':3}))

    def test_rejected_probe_does_not_start_background_sampler(self):
        guard = ProbeMemoryTimeline('test')
        with patch.object(guard,'sample',return_value={'available_physical_gib':10,'available_commit_gib':1}):
            with self.assertRaisesRegex(RuntimeError,'not submitted.*commit'):
                guard.__enter__()
        self.assertIsNone(guard.thread)

    def test_stress_budget_is_separate_and_stricter(self):
        row = {'available_physical_gib':10,'available_commit_gib':4}
        self.assertIsNone(headroom_error(row))
        self.assertIn('commit',headroom_error(row,8,8))

if __name__ == '__main__':
    unittest.main()
