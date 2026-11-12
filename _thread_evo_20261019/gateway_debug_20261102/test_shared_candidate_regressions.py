import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).parent


def module(name, filename):
    spec=importlib.util.spec_from_file_location(name,ROOT/filename)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


candidate=module('shared_reader_candidate','detector_shared_layout_fixed.py')
reader=module('shared_reader_tests','test_reader_fix.py');reader.fixed=candidate
boundary=module('shared_boundary_tests','test_turn_copy_boundary.py');boundary.detector=candidate
empty=module('shared_empty_tests','test_empty_finished_response.py');empty.detector=candidate
guards=module('shared_guard_tests','test_response_completion_worker_logging.py');guards.detector=candidate


def load_tests(loader,tests,pattern):
    return unittest.TestSuite(loader.loadTestsFromModule(m) for m in (reader,boundary,empty,guards))
