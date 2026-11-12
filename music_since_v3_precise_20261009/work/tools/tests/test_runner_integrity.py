"""通用 runner 的新身份/byte-exact输入/单提交/失败落盘，离线桩。"""
import contextlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner as R
import execution_integrity as E


def payload(text):
    return json.dumps({"part": {"type": "text", "text": text,
                      "session_handle": "private-do-not-save"}}, ensure_ascii=False).encode("utf-8")


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        for target, val in (("_SLOT_DIR", self.d / "slots"), ("GPT2_KEYS", ()), ("MG_KEYS", ())):
            p = mock.patch.object(R, target, val)
            p.start()
            self.addCleanup(p.stop)
        p = mock.patch.object(R, "_GlobalSlot", side_effect=lambda *a, **k: contextlib.nullcontext())
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(R, "_ensure_init")
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.dict(R._STATE, {"env": {}, "init": True})
        p.start()
        self.addCleanup(p.stop)
        p = mock.patch.object(R, "_build_task", return_value=(["stub"], "raw", "gemini-test"))
        p.start()
        self.addCleanup(p.stop)
        self.build = p

    def job(self, **kw):
        return dict({"job_id": "j", "model_key": "gflash", "prompt": "甲\n乙\r\n丙",
                     "prompt_version": "v0", "max_attempts": 5}, **kw)

    def test_byte_exact_input_output_and_same_job_readonly_resume(self):
        output = "一\n二\r\n三"
        with mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess([], 0, payload(output), b"")) as run:
            m = R.run_job(self.d, self.job())
            self.assertEqual(m["status"], "ok")
            self.assertEqual((self.d / m["prompt_file"]).read_bytes(), self.job()["prompt"].encode())
            self.assertEqual((self.d / m["output_file"]).read_bytes(), output.encode())
            before = (self.d / "meta/j.json").read_bytes()
            resumed = R.run_job(self.d, self.job())
            self.assertTrue(resumed["resumed"])
            self.assertEqual(run.call_count, 1)
            self.assertEqual(before, (self.d / "meta/j.json").read_bytes())
            self.assertNotIn(b"private-do-not-save", (self.d / m["stdout_file"]).read_bytes())

    def test_initialization_failure_has_identity_and_no_process(self):
        with mock.patch.object(R, "_build_task", side_effect=FileNotFoundError("not installed")), \
             mock.patch.object(R, "run_process") as run:
            m = R.run_job(self.d, self.job())
            self.assertEqual(m["status"], "failed")
            self.assertEqual(m["attempts"], 0)
            self.assertTrue(m["request_identity"])
            self.assertEqual(m["failure_phase"], "local_initialization")
            self.assertTrue(m["retry_safe"])
            run.assert_not_called()

    def test_nonzero_exit_never_automatically_resubmitted(self):
        with mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess([], 1, b"", b"failed")) as run:
            m = R.run_job(self.d, self.job())
            self.assertEqual(m["status"], "failed")
            self.assertEqual(m["attempts"], 1)
            self.assertFalse(m["automatic_retry"])
            self.assertEqual(run.call_count, 1)

    def test_protection_stops_other_jobs_in_same_provider(self):
        with mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess([], 1, b"", b"429 rate limited")) as run:
            first = R.run_job(self.d, self.job())
            second = R.run_job(self.d, self.job(job_id="next"))
            self.assertTrue(first["queue_stop"])
            self.assertTrue(second["queue_stop"])
            self.assertEqual(second["attempts"], 0)
            self.assertEqual(run.call_count, 1)

    def test_timeout_holds_provider_and_never_resubmits(self):
        with mock.patch.object(R, "run_process", side_effect=subprocess.TimeoutExpired("stub", 1)) as run:
            m = R.run_job(self.d, self.job(), timeout=1)
            self.assertTrue(m["queue_stop"])
            self.assertFalse(m["retry_safe"])
            self.assertTrue((self.d / "slots/gemini/queue_hold.json").is_file())
            self.assertEqual(run.call_count, 1)

    def test_zero_attempt_budget_is_failed_not_empty_success(self):
        with mock.patch.object(R, "run_process") as run:
            m = R.run_job(self.d, self.job(max_attempts=0))
            self.assertEqual(m["status"], "failed")
            self.assertEqual(m["attempts"], 0)
            run.assert_not_called()

    def test_prompt_path_cannot_escape_resume_root(self):
        i = {"producer": {}, "prompt_sha256": E.sha_text("question")}
        E.write_text(self.d / "outputs/j.md", "answer")
        outside = self.d.parent / (self.d.name + "_outside.txt")
        E.write_text(outside, "question")
        self.addCleanup(outside.unlink)
        E.write_json(self.d / "meta/j.json", {"status": "ok", "request_identity": i,
            "output_file": "outputs/j.md", "response_sha256": E.sha_text("answer"),
            "prompt_file": str(outside)})
        with self.assertRaises(E.ArtifactConflict):
            E.checked_resume(self.d, "j", i)

    def codex_payload(self, *item_types):
        events = [{"type": "item.completed", "item": {"type": t}}
                  for t in item_types]
        events.append({"type": "item.completed", "item": {
            "type": "agent_message", "text": "完成回答"}})
        events.append({"type": "turn.completed", "usage": {}})
        return "\n".join(json.dumps(x, ensure_ascii=False) for x in events).encode("utf-8")

    def test_codex_completed_tool_invalidates_tool_free_job(self):
        for tool in ("command_execution", "web_search", "file_change", "mcp_tool_call"):
            with self.subTest(tool=tool), mock.patch.object(R, "run_process", return_value=
                    subprocess.CompletedProcess([], 0, self.codex_payload(tool), b"")) as run:
                job = self.job(job_id=tool, model_key="luna_noweb", forbid_tools=["all"])
                meta = R.run_job(self.d, job)
                self.assertEqual(meta["status"], "failed")
                self.assertIn(tool, meta["error"])
                self.assertEqual(meta["tool_counts"][tool], 1)
                self.assertEqual((self.d / meta["output_file"]).read_bytes(), b"")
                self.assertEqual(run.call_count, 1)
                self.assertFalse(meta["automatic_retry"])

    def test_codex_reasoning_and_todo_do_not_invalidate_tool_free_job(self):
        with mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess(
                [], 0, self.codex_payload("reasoning", "todo_list"), b"")):
            meta = R.run_job(self.d, self.job(model_key="luna_noweb", forbid_tools=["all"]))
            self.assertEqual(meta["status"], "ok", meta["error"])
            self.assertEqual(meta["output_chars"], len("完成回答"))

    def test_codex_tool_allowed_when_job_does_not_forbid_tools(self):
        with mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess(
                [], 0, self.codex_payload("web_search"), b"")):
            meta = R.run_job(self.d, self.job(model_key="luna_noweb"))
            self.assertEqual(meta["status"], "ok", meta["error"])
            self.assertEqual(meta["tool_counts"]["web_search"], 1)

    def test_missing_image_never_submits_or_writes_success_artifacts(self):
        job = self.job(model_key="luna_noweb", extra={"images": [str(self.d / "missing.png")]})
        with mock.patch.object(R, "run_process") as run, self.assertRaises(FileNotFoundError):
            R.run_job(self.d, job)
        run.assert_not_called()
        self.assertFalse((self.d / "meta/j.json").exists())
        self.assertFalse((self.d / "outputs/j.md").exists())

    def test_jsonl_and_headers_redacted(self):
        s = '{"session_handle": "private one", "nested":{"api_key":"private two"}}\nCookie: abc=1; def=2\nAuthorization: Basic xxx\n'
        result = E.safe_records(s)
        for value in ("private one", "private two", "abc=1", "def=2", "Basic xxx"):
            self.assertNotIn(value, result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
