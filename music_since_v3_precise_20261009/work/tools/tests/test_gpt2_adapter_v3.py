"""gpt2 v3 全离线：拒假终态/缓存改动/未知提交，零真实调用。"""
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_integrity_v3 as I
import gpt2_adapter_v3 as A


def payload(completed=True, response="完整回答", metadata=None):
    return json.dumps({"completed": completed, "response": response,
                       "metadata": metadata or {"server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}},
                      ensure_ascii=False).encode()


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root / "run"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        self.stack.enter_context(mock.patch.object(A, "HOLD_FILE", self.root / "hold.json"))
        self.stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(A, "producer_identity", return_value={"route": "stub", "cli": "stub",
            "cli_version": "test", "cli_sha256": "1" * 64, "cli_source": {"missing": False}, "implementation": "v3"}))
        self.process = self.stack.enter_context(mock.patch.object(A, "RUN_PROCESS",
            return_value=subprocess.CompletedProcess([], 0, payload(), b"")))

    def call(self, name="one", **kwargs):
        return A.call_web_gpt("gpt56w", "冻结输入\n第二行", run_id="probe", job_id=name, out_dir=self.out, **kwargs)

    def test_success_resume_readonly(self):
        first = self.call()
        mp = self.out / "meta/one.json"
        before = mp.read_bytes()
        again = self.call()
        self.assertEqual(first["status"], "ok")
        self.assertTrue(again["resumed"])
        self.assertEqual(before, mp.read_bytes())
        self.assertEqual(self.process.call_count, 1)

    def test_completed_is_strict_bool(self):
        for value in ("true", 1, [], None, False):
            with self.subTest(value=value):
                self.out = self.root / ("run" + str(value))
                with mock.patch.object(A, "HOLD_FILE", self.root / ("hold" + str(value))):
                    self.process.return_value = subprocess.CompletedProcess([], 0, payload(value), b"")
                    meta = self.call()
                    self.assertEqual(meta["status"], "failed")
                    self.assertTrue(meta["queue_stop"])

    def test_unknown_exception_holds_before_exit(self):
        @contextlib.contextmanager
        def slot(*a, **k):
            yield
            self.assertTrue(A.HOLD_FILE.is_file())
        self.process.side_effect = OSError("offline exception")
        with mock.patch.object(A, "Slot", side_effect=slot):
            self.assertTrue(self.call()["queue_stop"])

    def test_timeout_holds(self):
        self.process.side_effect = subprocess.TimeoutExpired("stub", 1, output=b"partial")
        self.assertTrue(self.call()["queue_stop"])
        self.assertEqual(self.process.call_count, 1)

    def test_invalid_json_holds(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, b"{", b"")
        self.assertTrue(self.call()["queue_stop"])

    def test_body_protection_words_are_content(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(response="challenge rate limit 429 403 普通正文"), b"")
        self.assertEqual(self.call()["status"], "ok")
        self.assertFalse(A.HOLD_FILE.exists())

    def test_protection_stderr_holds(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(), b"HTTP 429")
        self.assertTrue(self.call()["queue_stop"])

    def test_pre_submit_failure_not_held(self):
        self.process.return_value = subprocess.CompletedProcess([], 1, b"", b'{"phase":"pre_submit","error":"not submitted"}')
        meta = self.call()
        self.assertTrue(meta["retry_safe"])
        self.assertFalse(meta["queue_stop"])
        self.assertFalse(A.HOLD_FILE.exists())

    def test_post_submit_failure_held(self):
        self.process.return_value = subprocess.CompletedProcess([], 1, b"", b'{"phase":"post_submit_ambiguous"}')
        self.assertTrue(self.call()["queue_stop"])

    def test_backend_unknown_or_wrong_rejected(self):
        for index, slug in enumerate((None, "gpt-6-thinking")):
            self.out = self.root / ("run%d" % index)
            self.process.return_value = subprocess.CompletedProcess([], 0,
                payload(metadata={"server_metadata_summary": {"model_slug": slug}}), b"")
            meta = self.call()
            self.assertEqual(meta["status"], "failed")
            self.assertTrue(meta["terminal_verified"])

    def test_cache_reference_has_no_body(self):
        self.call(sampling_key="shared")
        second = self.call("two", sampling_key="shared")
        cache = I.strict_json(next((self.out / "cache").glob("*.json")).read_text())
        self.assertNotIn("response", cache)
        self.assertEqual(cache["source_job_id"], "one")
        self.assertTrue(second["cache_hit"])
        self.assertEqual(self.process.call_count, 1)

    def test_source_meta_tamper_rejected(self):
        self.call(sampling_key="shared")
        (self.out / "meta/one.json").write_bytes(b"{}")
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_source_body_tamper_rejected(self):
        self.call(sampling_key="shared")
        (self.out / "outputs/one.md").write_bytes(b"changed")
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_failed_sample_never_resubmits(self):
        self.process.return_value = subprocess.CompletedProcess([], 1, b"", b'{"phase":"pre_submit"}')
        self.call(sampling_key="shared")
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_sensitive_body_not_saved_or_resubmitted(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(response="secret=NOT_A_REAL_SECRET"), b"")
        first = self.call(sampling_key="shared")
        self.assertEqual(first["status"], "failed")
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"NOT_A_REAL_SECRET", path.read_bytes())

    def test_default_route_blocked(self):
        with mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "blocked"}):
            with self.assertRaises(I.PolicyBlocked):
                self.call()
        self.assertEqual(self.process.call_count, 0)


if __name__ == "__main__":
    unittest.main()
