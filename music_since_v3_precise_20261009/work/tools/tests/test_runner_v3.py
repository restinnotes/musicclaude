"""隔离回归：所有 CLI/槽位均为桩，真实模型请求为零。"""
import contextlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import execution_integrity_v3 as I
import runner_v3 as R


def codex(text="完整回答", tools=()):
    rows = [{"type": "thread.started", "thread_id": "mock-thread"}, {"type": "turn.started"}]
    for index, tool in enumerate(tools):
        rows.append({"type": "item.completed", "item": {"id": "tool%d" % index, "type": tool}})
    rows.extend([{"type": "item.completed", "item": {"id": "answer", "type": "agent_message", "text": text}},
                 {"type": "turn.completed", "usage": {}}])
    return rows


def opencode(text="完整回答", reason="stop"):
    base = {"sessionID": "mock-session"}
    common = {"sessionID": "mock-session", "messageID": "mock-message"}
    return [dict(base, type="step_start", part=dict(common, id="start", type="step-start")),
            dict(base, type="text", part=dict(common, id="text", type="text", text=text, time={"end": 1})),
            dict(base, type="step_finish", part=dict(common, id="finish", type="step-finish", reason=reason))]


def stream(rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.directory = self.root / "run"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.object(R, "SLOT_DIR", self.root / "slots"))
        self.stack.enter_context(mock.patch.object(R, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(R.legacy, "_build_task", return_value=([str(Path(__file__).resolve())], "raw", "offline_stub")))
        self.stack.enter_context(mock.patch.object(R.legacy, "_ensure_init"))
        self.stack.enter_context(mock.patch.dict(R.legacy._STATE, {"env": {}, "init": True}))
        self.process = self.stack.enter_context(mock.patch.object(R, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, stream(opencode()), b"")))

    def job(self, name="one", model="gflash", **extra):
        return dict(job_id=name, model_key=model, prompt="冻结输入\n第二行", max_attempts=1, **extra)

    def test_success_and_readonly_resume(self):
        first = R.run_job(self.directory, self.job())
        meta = self.directory / "meta/one.json"
        before = meta.read_bytes()
        resumed = R.run_job(self.directory, self.job())
        self.assertEqual(first["status"], "ok")
        self.assertTrue(resumed["resumed"])
        self.assertEqual(meta.read_bytes(), before)
        self.assertEqual(self.process.call_count, 1)
        self.assertEqual((self.directory / "prompts/one.txt").read_bytes(), "冻结输入\n第二行".encode())

    def test_missing_codex_terminal_stops(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(codex()[:-1]), b"")
        meta = R.run_job(self.directory, self.job(model="luna_noweb"))
        self.assertEqual(meta["status"], "failed")
        self.assertTrue(meta["queue_stop"])
        self.assertTrue((self.root / "slots/codex/queue_hold.json").exists())

    def test_missing_opencode_terminal_stops(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(opencode()[:-1]), b"")
        results = R.run_jobs(self.directory, [self.job(), self.job("two")])
        self.assertTrue(results[0]["queue_stop"])
        self.assertEqual(results[1]["status"], "skipped_queue_stop")
        self.assertEqual(self.process.call_count, 1)
        self.assertFalse((self.directory / "prompts/two.txt").exists())

    def test_body_protection_word_does_not_hold(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(opencode("challenge 403 429 rate limit 只是正文词")), b"")
        meta = R.run_job(self.directory, self.job())
        self.assertEqual(meta["status"], "ok")
        self.assertFalse(meta["queue_stop"])

    def test_error_hold_exists_before_slot_exit(self):
        hold = self.root / "slots/gemini/queue_hold.json"
        @contextlib.contextmanager
        def slot(*a, **k):
            yield
            self.assertTrue(hold.is_file())
        with mock.patch.object(R, "Slot", side_effect=slot):
            self.process.side_effect = OSError("offline error")
            self.assertTrue(R.run_job(self.directory, self.job())["queue_stop"])
        self.assertEqual(self.process.call_count, 1)

    def test_timeout_holds(self):
        self.process.side_effect = subprocess.TimeoutExpired("stub", 1, output=b"partial")
        self.assertTrue(R.run_job(self.directory, self.job())["queue_stop"])

    def test_stderr_protection_holds(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(opencode()), b"HTTP 429")
        self.assertTrue(R.run_job(self.directory, self.job())["queue_stop"])

    def test_nonzero_holds(self):
        self.process.return_value = subprocess.CompletedProcess([], 1, stream(opencode()), b"unknown")
        self.assertTrue(R.run_job(self.directory, self.job())["queue_stop"])

    def test_shared_sample_cache_uses_source_not_body(self):
        first = R.run_job(self.directory, self.job(sampling_key="shared"))
        second = R.run_job(self.directory, self.job("two", sampling_key="shared"))
        self.assertEqual(first["status"], "ok")
        self.assertTrue(second["cache_hit"])
        self.assertEqual(self.process.call_count, 1)
        cache = I.strict_json(next((self.directory / "cache").glob("*.json")).read_text())
        self.assertNotIn("response", cache)
        self.assertEqual(cache["source_job_id"], "one")

    def test_cache_tamper_never_resubmits(self):
        R.run_job(self.directory, self.job(sampling_key="shared"))
        (self.directory / "outputs/one.md").write_bytes(b"changed")
        with self.assertRaises(I.ArtifactConflict):
            R.run_job(self.directory, self.job("two", sampling_key="shared"))
        self.assertEqual(self.process.call_count, 1)

    def test_bad_cache_never_resubmits(self):
        R.run_job(self.directory, self.job(sampling_key="shared"))
        next((self.directory / "cache").glob("*.json")).write_bytes(b"{")
        with self.assertRaises(I.ArtifactConflict):
            R.run_job(self.directory, self.job("two", sampling_key="shared"))
        self.assertEqual(self.process.call_count, 1)

    def test_pending_never_resubmits(self):
        identity = R.request_identity_for(self.job())
        I.reserve(self.directory, "one", identity)
        with self.assertRaises(I.ArtifactConflict):
            R.run_job(self.directory, self.job())
        self.assertEqual(self.process.call_count, 0)

    def test_forbidden_tool_no_output(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(codex(tools=["command_execution"])), b"")
        meta = R.run_job(self.directory, self.job(model="luna_noweb"))
        self.assertEqual(meta["status"], "failed")
        self.assertEqual((self.directory / meta["output_file"]).read_bytes(), b"")

    def test_policy(self):
        for key in ("opus", "sol61_cx", "muse", "grok"):
            with self.assertRaises(I.PolicyBlocked):
                R.run_job(self.directory, self.job(model=key))
        self.assertEqual(self.process.call_count, 0)

    def test_sensitive_body_rejected_without_plaintext(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(opencode("secret=NOT_A_REAL_SECRET")), b"")
        meta = R.run_job(self.directory, self.job())
        self.assertEqual(meta["status"], "failed")
        for path in self.directory.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"NOT_A_REAL_SECRET", path.read_bytes())

    def test_raw_handles_redacted(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, stream(codex()), b"")
        R.run_job(self.directory, self.job(model="luna_noweb"))
        raw = (self.directory / "outputs/raw/one.stdout.txt").read_text()
        self.assertNotIn("mock-thread", raw)


class ParserTests(unittest.TestCase):
    def assert_rejected(self, parser, rows):
        with self.assertRaises((ValueError, TypeError)):
            parser(stream(rows).decode())

    def test_codex_valid(self):
        self.assertEqual(I.parse_codex(stream(codex()).decode())[0], "完整回答")

    def test_codex_missing_start_or_terminal(self):
        for rows in (codex()[2:], codex()[:-1], codex()[1:]):
            self.assert_rejected(I.parse_codex, rows)

    def test_codex_tail_or_second_turn(self):
        for tail in ({"type": "turn.started"}, {"type": "error"}, codex()[2], []):
            self.assert_rejected(I.parse_codex, codex() + [tail])

    def test_codex_pending_item(self):
        rows = codex()
        rows.insert(2, {"type": "item.started", "item": {"id": "p", "type": "reasoning"}})
        self.assert_rejected(I.parse_codex, rows)

    def test_codex_unknown_item(self):
        rows = codex()
        rows[2]["item"]["type"] = "unknown"
        self.assert_rejected(I.parse_codex, rows)

    def test_opencode_valid(self):
        self.assertEqual(I.parse_opencode(stream(opencode()).decode())[0], "完整回答")

    def test_opencode_finish_reasons(self):
        for reason in ("length", "content-filter", "error", "tool-calls", None):
            self.assert_rejected(I.parse_opencode, opencode(reason=reason))

    def test_opencode_session_message_shape(self):
        for field in ("sessionID", "messageID"):
            rows = opencode()
            rows[1]["part"][field] = "other"
            self.assert_rejected(I.parse_opencode, rows)
        rows = opencode()
        del rows[1]["part"]["time"]
        self.assert_rejected(I.parse_opencode, rows)

    def test_bad_json_duplicate_keys(self):
        for text in ("{", '[]', '{"type":"x","type":"y"}'):
            with self.assertRaises(ValueError):
                I.parse_codex(text)


if __name__ == "__main__":
    unittest.main()
