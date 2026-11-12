import unittest
from src.chatgpt.effort_policy import choose_effort

class EffortPolicyTests(unittest.TestCase):
    def test_extra_high_always_preferred(self):
        self.assertEqual(choose_effort({'High': 2, 'Extra High': 3}, True), ('Extra High', 3, None))
    def test_strict_account_refuses_fallback(self):
        with self.assertRaises(ValueError):
            choose_effort({'Medium': 1, 'High': 2})
    def test_plus_high_requires_explicit_authorization(self):
        self.assertEqual(choose_effort({'Medium': 1, 'High': 2}, True),
                         ('High', 2, 'extra_high_unavailable_high_authorized'))
    def test_missing_high_fails_closed(self):
        with self.assertRaises(ValueError):
            choose_effort({'Instant': 0, 'Medium': 1}, True)

if __name__ == '__main__':
    unittest.main()
