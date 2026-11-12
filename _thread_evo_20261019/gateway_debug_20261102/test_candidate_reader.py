"""Run all existing reader/guard regressions against the next reader candidate."""
import importlib.util
from pathlib import Path
import unittest

root = Path(__file__).parent
spec = importlib.util.spec_from_file_location('reader_regressions', root / 'test_reader_fix.py')
suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(suite)
suite.fixed = suite.module('candidate_reader', 'detector_copy_boundary_fixed.py')


def load_tests(loader, tests, pattern):
    return loader.loadTestsFromModule(suite)


if __name__ == '__main__':
    unittest.main()
