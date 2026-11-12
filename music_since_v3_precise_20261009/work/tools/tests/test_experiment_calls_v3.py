"""实验层的成功证据不得由 parse_ok/cache 自述代替。"""
import contextlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import execution_integrity_v3 as I
import experiment_calls_v3 as E
import runner_v3 as R
from test_runner_v3 import opencode, stream


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root / "run"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.object(R, "SLOT_DIR", self.root / "slots"))
        self.stack.enter_context(mock.patch.object(R, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(R.legacy, "_build_task", return_value=([str(Path(__file__).resolve())], "raw", "offline_stub")))
        self.stack.enter_context(mock.patch.object(R.legacy, "_ensure_init"))
        self.stack.enter_context(mock.patch.dict(R.legacy._STATE, {"env": {}, "init": True}))
        self.process = self.stack.enter_context(mock.patch.object(R, "RUN_PROCESS",
            return_value=subprocess.CompletedProcess([], 0, stream(opencode('{"ok":true}')), b"")))

    def call(self, parser=lambda text: (I.strict_json(text), None), attempts=1):
        return E.call(self.out, "audit", "case", "gflash", "冻结输入", parser, [1], "v0", max_attempts=attempts)

    def test_success_then_exact_revalidation(self):
        first, second = self.call(), self.call()
        self.assertTrue(first["parse_ok"])
        self.assertEqual(first["new_model_submissions"], 1)
        self.assertEqual(second["resume_validations"], 1)
        self.assertEqual(second["new_model_submissions"], 0)
        self.assertEqual(self.process.call_count, 1)

    def test_cache_log_only_does_not_return_fake(self):
        self.out.mkdir()
        (self.out / "cache_audit_exact.json").write_text(json.dumps({"records": [{"parse_ok": True, "parsed": "fake"}]}))
        result = self.call()
        self.assertEqual(result["parsed"], {"ok": True})
        self.assertEqual(self.process.call_count, 1)

    def test_mock_success_without_artifacts_rejected(self):
        with mock.patch.object(R, "run_job", return_value={"status": "ok", "output_file": "outputs/fake.md"}):
            with self.assertRaises(I.ArtifactConflict):
                self.call()
        self.assertEqual(self.process.call_count, 0)

    def test_output_tamper_rejected(self):
        result = self.call()
        (self.out / result["output_file"]).write_bytes(b"changed")
        with self.assertRaises(I.ArtifactConflict):
            self.call()
        self.assertEqual(self.process.call_count, 1)

    def test_parser_failure_new_attempt_not_overwrite(self):
        self.process.side_effect = [subprocess.CompletedProcess([], 0, stream(opencode("bad")), b""),
                                    subprocess.CompletedProcess([], 0, stream(opencode('{"ok":true}')), b"")]
        result = self.call(attempts=2)
        self.assertTrue(result["parse_ok"])
        self.assertEqual(len(result["attempts"]), 2)
        self.assertNotEqual(result["attempts"][0]["job_id"], result["attempts"][1]["job_id"])
        self.assertEqual(self.process.call_count, 2)

    def test_unknown_terminal_no_new_attempt(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(opencode()[:-1]), b"")
        result = self.call(attempts=3)
        self.assertFalse(result["parse_ok"])
        self.assertTrue(result["queue_stop"])
        self.assertEqual(self.process.call_count, 1)

    def test_parser_value_plus_error_not_accepted(self):
        result = self.call(parser=lambda text: ({"not": "valid"}, "schema error"))
        self.assertFalse(result["parse_ok"])

    def test_policy_before_call(self):
        with self.assertRaises(I.PolicyBlocked):
            E.call(self.out, "audit", "case", "opus", "input", lambda t: (t, None), [], "v0")
        self.assertEqual(self.process.call_count, 0)


if __name__ == "__main__":
    unittest.main()
