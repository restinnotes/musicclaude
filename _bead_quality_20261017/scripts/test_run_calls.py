"""Offline tests only: fixture bytes and a synthetic local Python child, never model clients."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bead_run_calls", ROOT / "run_calls.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="_runner_offline_", dir=ROOT)
        self.base = Path(self.temp.name).resolve()
        assert self.base.is_relative_to(ROOT)
        self.addCleanup(self.temp.cleanup)
        self.prompt = self.base / "p.txt"
        self.prompt.write_bytes("\ufeff完整输入\r\n保留正文和尾部空白  \r\n".encode("utf-8"))
        self.job = {"job_id": "fixture", "channel": "gpt2", "model": "gpt-6-thinking",
                    "prompt_file": "p.txt", "timeout_seconds": 5}
        r.STOP.clear()

    def prepared(self, **changes):
        return r.validate_job({**self.job, **changes}, self.base)

    def gpt_payload(self, prepared, body="完整的测试正文"):
        return {"completed": True, "response": body, "metadata": {
            "model": prepared["job"]["model"], "thinking_effort": "max", "session_handle": "private-fixture",
            "response_sha256": r.sha(body.encode()),
            "attachments": [{k: x[k] for k in ("name", "size", "sha256")} for x in prepared["attachments"]],
            "stream_completion": {"sse_done": True, "message_completed": True, "continuation_expected": False},
            "prepared_response_validation": {"successful_assistant_terminal_observed": True},
            "server_metadata_summary": {"model_slug": prepared["job"]["model"]}}}

    def test_complete_prompt_bytes_and_documented_normalization(self):
        p = self.prepared()
        self.assertEqual(p["raw"], self.prompt.read_bytes())
        self.assertEqual(p["prompt_sha256"], r.file_sha(self.prompt))
        self.assertEqual(p["normalized_prompt_sha256"], r.sha("完整输入\n保留正文和尾部空白".encode()))

    def test_hash_mismatch_and_bad_model_fail(self):
        for change in ({"prompt_sha256": "0" * 64}, {"model": "gpt-5.6w"}, {"reasoning_effort": "low"}):
            with self.subTest(change=change), self.assertRaises(r.Invalid):
                self.prepared(**change)

    def test_byte_guard_not_only_character_guard(self):
        self.prompt.write_text("中" * 25000, encoding="utf-8")
        with patch.dict(os.environ, {"MUSIC_RESEARCH_LARGE_NATIVE_BODY": "0"}), self.assertRaisesRegex(r.Invalid, "native_JSON_byte_limit"):
            self.prepared()
        # Full text remains valid for an explicitly selected Flash job; never truncated.
        p = self.prepared(channel="opencode", model=r.FLASH)
        self.assertEqual(p["prompt_bytes"], 75000)

    def test_native_attachment_bound_to_bytes(self):
        pool = self.base / "pool.txt"
        pool.write_bytes("段落".encode() * 12000)
        p = self.prepared(attachments=[{"path": "pool.txt", "sha256": r.file_sha(pool)}])
        good = self.gpt_payload(p)
        body, meta, errors = r.parse_gpt2(json.dumps(good).encode(), p)
        self.assertFalse(errors)
        self.assertTrue(meta["attachment_upload_verified"])
        good["metadata"]["attachments"] = []
        self.assertIn("gpt2_attachment_manifest_mismatch", r.parse_gpt2(json.dumps(good).encode(), p)[2])
        with self.assertRaises(r.Invalid):
            self.prepared(channel="opencode", model=r.FLASH, attachments=["pool.txt"])

    def test_incomplete_wrong_model_effort_hash_are_failures(self):
        p = self.prepared()
        for field, value, code in (("model", "gpt-5-6-thinking", "gpt2_model_or_effort_mismatch"),
                ("thinking_effort", "high", "gpt2_model_or_effort_mismatch"),
                ("response_sha256", "0" * 64, "gpt2_response_sha256_mismatch"),
                ("stream_completion", {"sse_done": False}, "gpt2_stream_not_complete")):
            data = self.gpt_payload(p)
            data["metadata"][field] = value
            self.assertIn(code, r.parse_gpt2(json.dumps(data).encode(), p)[2])

    def test_opencode_completion_errors_tools_and_metadata(self):
        event = {"type": "text", "part": {"type": "text", "text": "full body", "time": {"end": 5}}}
        raw = json.dumps(event).encode()
        text, meta, errors = r.parse_opencode(raw)
        self.assertEqual(text, "full body")
        self.assertFalse(errors)
        self.assertFalse(meta["server_completion_verified"])
        self.assertNotIn("text", meta["events"][0]["part"])
        for extra, expected in (({"type": "error"}, "opencode_error_event"),
            ({"type": "tool_use", "part": {"type": "tool", "tool": "read", "state": {"status": "completed"}}}, "opencode_tool_event_in_tool_free_job"),
            ({"type": "step_finish", "part": {"type": "step-finish", "reason": "length"}}, "opencode_terminal_not_successful")):
            self.assertIn(expected, r.parse_opencode(raw + b"\n" + json.dumps(extra).encode())[2])
        event["part"]["time"] = {}
        self.assertIn("opencode_text_not_closed", r.parse_opencode(json.dumps(event).encode())[2])

    def synthetic_run(self, prepared, payload, exit_code=0, sleep_seconds=0):
        child = self.base / "synthetic_child.py"
        child.write_text("import sys,time\ntime.sleep(" + repr(sleep_seconds) + ")\n"
                         + "sys.stdout.buffer.write(" + repr(payload) + ")\n"
                         + "sys.stderr.buffer.write(b'fixture stderr\\r\\n')\n"
                         + "sys.exit(" + str(exit_code) + ")\n", encoding="utf-8")
        output = self.base / "results"
        output.mkdir(exist_ok=True)
        with patch.object(r, "build_command", return_value=([sys.executable, "-B", str(child)], dict(os.environ), {"synthetic_test": True})):
            result = r.run_job(prepared, output, "fixture_manifest")
        return result, output / prepared["job"]["job_id"]

    def test_process_capture_no_overwrite_and_secret_not_in_metadata(self):
        p = self.prepared()
        raw = json.dumps(self.gpt_payload(p), ensure_ascii=False).encode()
        result, directory = self.synthetic_run(p, raw)
        self.assertEqual(result["status"], "ok")
        self.assertEqual((directory / "stdout.raw").read_bytes(), raw)
        self.assertEqual((directory / "stderr.raw").read_bytes(), b"fixture stderr\r\n")
        self.assertEqual((directory / "prompt.txt").read_bytes(), self.prompt.read_bytes())
        self.assertNotIn("private-fixture", (directory / "metadata.json").read_text(encoding="utf-8"))
        original_hash = r.file_sha(directory / "metadata.json")
        with patch.object(r, "build_command", side_effect=AssertionError("must not launch")):
            second = r.run_job(p, directory.parent, "different_manifest")
        self.assertEqual(second["status"], "exists_not_overwritten")
        self.assertEqual(original_hash, r.file_sha(directory / "metadata.json"))

    def test_nonzero_exit_preserves_response_but_fails(self):
        p = self.prepared()
        result, directory = self.synthetic_run(p, json.dumps(self.gpt_payload(p)).encode(), 7)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exit_code"], 7)
        self.assertTrue((directory / "response.txt").stat().st_size)

    def test_timeout_is_ambiguous_and_not_retried(self):
        p = self.prepared(timeout_seconds=1)
        result, directory = self.synthetic_run(p, b"", sleep_seconds=10)
        self.assertEqual(result["status"], "timeout")
        meta = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["submission_state"], "unknown_do_not_automatically_replay")
        self.assertFalse(meta["automatic_retry"])

    def test_preflight_failure_saves_evidence(self):
        output = self.base / "invalid_results"
        output.mkdir()
        r.save_preflight_failure({"job_id": "fixture", "error": "prompt_sha256_mismatch"}, self.job, output, self.base, "manifest")
        d = output / "fixture"
        meta = json.loads((d / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["status"], "failed_preflight")
        self.assertEqual((d / "prompt.txt").read_bytes(), self.prompt.read_bytes())
        self.assertEqual((d / "stdout.raw").read_bytes(), b"")

    def test_filter_default_dry_run_and_worker_limit(self):
        manifest = self.base / "jobs.json"
        spec = {"schema_version": 1, "output_dir": "results", "jobs": [self.job, {**self.job, "job_id": "other", "prompt_file": "missing.txt"}]}
        manifest.write_text(json.dumps(spec), encoding="utf-8")
        with patch.object(r, "build_command", return_value=([], {}, {})), patch.object(r.subprocess, "Popen", side_effect=AssertionError("no subprocess in dry run")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(r.main(["--jobs", str(manifest), "--job-id", "fixture"]), 0)
            self.assertFalse((self.base / "results").exists())
            spec["max_workers"] = 3
            manifest.write_text(json.dumps(spec), encoding="utf-8")
            self.assertEqual(r.main(["--jobs", str(manifest)]), 2)


if __name__ == "__main__":
    unittest.main()
