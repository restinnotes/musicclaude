"""v4 六缺口与磁盘 finalization 回归；所有模型/CLI 只 mock。"""
import contextlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import execution_integrity_v4 as I
import gpt2_adapter_v4 as A
import runner_v4 as R
import experiment_calls_v4 as E


def payload(completed=True, response="完整离线回答", metadata=None):
    meta = {"headless": True, "provider_interface": True, "no_auto_retry": True,
            "model": "gpt-5-6-thinking", "response_sha256": I.sha_text(response),
            "prepared_response_validation": {"successful_assistant_terminal_observed": True,
                "unsupported_work_continuation_observed": False},
            "server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}
    if metadata is not None:
        meta.update(metadata)
    return json.dumps({"completed": completed, "response": response, "metadata": meta}, ensure_ascii=False).encode()


def codex(events=None, body="完整离线回答"):
    rows = [{"type": "thread.started", "thread_id": "FICTIONAL_THREAD"}, {"type": "turn.started"}]
    rows += events or []
    rows += [{"type": "item.completed", "item": {"id": "fake-item", "type": "agent_message", "text": body}},
             {"type": "turn.completed", "usage": {}}]
    return "\n".join(json.dumps(row, ensure_ascii=False) for row in rows).encode()


def opencode(body="完整离线回答"):
    rows = []
    for i, (kind, part) in enumerate((
        ("step_start", {"type": "step-start"}),
        ("text", {"type": "text", "text": body, "time": {"end": 1}}),
        ("step_finish", {"type": "step-finish", "reason": "stop"}))):
        part.update(sessionID="FICTIONAL_SESSION", messageID="FICTIONAL_MESSAGE", id="fake-%d" % i)
        rows.append({"type": kind, "sessionID": "FICTIONAL_SESSION", "part": part})
    return "\n".join(json.dumps(row, ensure_ascii=False) for row in rows).encode()


class IntegrityTests(unittest.TestCase):
    def test_unknown_codex_events_rejected(self):
        for event in ("turn.cancelled", "turn.failed", "error", "thread.resumed", "totally_unknown"):
            with self.subTest(event=event), self.assertRaises(ValueError):
                I.parse_codex(codex([{"type": event}]).decode())

    def test_cancelled_item_rejected(self):
        for status in ("failed", "error", "cancelled", "canceled"):
            with self.subTest(status=status), self.assertRaises(ValueError):
                I.parse_codex(codex([{"type": "item.completed", "item": {
                    "id": "extra", "type": "reasoning", "status": status}}]).decode())

    def test_success_and_after_terminal(self):
        self.assertEqual(I.parse_codex(codex().decode())[0], "完整离线回答")
        with self.assertRaises(ValueError):
            I.parse_codex(codex().decode() + '\n{"type":"turn.started"}')

    def test_strict_json(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                I.strict_json(text)

    def test_handle_keys_and_strings_redacted(self):
        fake = "FICTIONAL_HANDLE"
        obj = {"sessionID": fake, "thread_id": fake, "nested": {"parentID": fake},
               "text": "sessionID=" + fake + " thread_id='" + fake + "'"}
        self.assertNotIn(fake, json.dumps(I.safe_metadata(obj)))
        for value in (json.dumps(obj), "sessionID=" + fake, "log thread_id='" + fake + "'",
                      "{\"sessionID\":\"" + fake + "\"\n malformed", json.dumps(obj, indent=2)):
            with self.subTest(value=value):
                self.assertNotIn(fake, I.safe_records(value))

    def test_body_preserved_or_rejected_not_scrubbed(self):
        text = "challenge 403 429 普通音乐正文"
        I.assert_content_safe(text)
        for text in ("thread_id=FICTIONAL", "secret=FICTIONAL"):
            with self.assertRaises(ValueError):
                I.assert_content_safe(text)

    def test_backend_root_contract_only(self):
        for obj in ({"debug": {"resolved_model_slugs": ["gpt-5-6-thinking"]}},
                    {"model": "gpt-5-6-thinking"},
                    {"server_metadata_summary": {"debug": {"resolved_model_slugs": ["gpt-5-6-thinking"]}}}):
            self.assertEqual(I.model_evidence(obj, "gpt-5-6-thinking")["verdict"], "unverified")
        self.assertEqual(I.model_evidence({"server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}},
                                         "gpt-5-6-thinking")["verdict"], "match")
        self.assertEqual(I.model_evidence({"server_metadata_summary": {"model_slug": "gpt-6-thinking"}},
                                         "gpt-5-6-thinking")["verdict"], "mismatch")

    def test_policy(self):
        for key in ("opus", "opus_web", "sol", "sol61", "muse", "muse_exec", "unknown"):
            with self.assertRaises(I.PolicyBlocked):
                R.check_policy(key)

    def test_ticket_survives_hold_disk_failure_cross_process(self):
        with tempfile.TemporaryDirectory() as temp:
            hold = Path(temp) / "provider/queue_hold.json"
            ticket = I.submission_ticket(hold, Path(temp) / "run", "a", {"fake": True})
            with mock.patch.object(I, "hold", side_effect=OSError("fictional hold failure")):
                self.assertIn("OSError", I.classify_stop(hold, "a", "run", "test"))
            self.assertTrue(ticket.is_file())
            self.assertFalse(I.queue_open(hold))
            script = "import sys;sys.path.insert(0,sys.argv[1]);import execution_integrity_v4 as I;assert not I.queue_open(sys.argv[2])"
            result = subprocess.run([sys.executable, "-I", "-c", script, str(TOOLS), str(hold)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            with self.assertRaises(I.PolicyBlocked):
                I.submission_ticket(hold, Path(temp) / "another", "b", {"fake": False})


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root / "run"
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        self.stack.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        self.stack.enter_context(mock.patch.object(A, "HOLD_FILE", self.root / "slots/gpt2web/hold.json"))
        self.stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **kw: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(A, "producer_identity", return_value={"route": "MOCK_ONLY", "cli": "stub",
            "cli_version": "test", "cli_sha256": "1" * 64, "cli_source": {"missing": False}, "implementation": "v4"}))
        self.process = self.stack.enter_context(mock.patch.object(A, "RUN_PROCESS",
            return_value=subprocess.CompletedProcess([], 0, payload(), b"")))

    def call(self, name="one", **kw):
        return A.call_web_gpt("gpt56w", "冻结输入\n第二行", run_id="MOCK_ONLY", job_id=name, out_dir=self.out, **kw)

    def test_success_resume_readonly_and_cache_reference(self):
        first = self.call(sampling_key="shared")
        before = (self.out / "meta/one.json").read_bytes()
        self.assertTrue(self.call(sampling_key="shared")["resumed"])
        second = self.call("two", sampling_key="shared")
        self.assertEqual(first["status"], "ok")
        self.assertTrue(second["cache_hit"])
        self.assertEqual(before, (self.out / "meta/one.json").read_bytes())
        self.assertEqual(self.process.call_count, 1)
        cache = I.strict_json(next((self.out / "cache").glob("*.json")).read_text())
        self.assertEqual(cache["source_job_id"], "one")
        self.assertNotIn("response", cache)
        self.assertTrue(I.queue_open(A.HOLD_FILE))

    def test_missing_cache_no_resubmit(self):
        self.call(sampling_key="shared")
        next((self.out / "cache").glob("*.json")).unlink()
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_pending_without_cache_no_resubmit(self):
        identity = A.request_identity("gpt56w", "max", "冻结输入\n第二行", sampling_key="shared")
        I.reserve(self.out, "orphan", identity)
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 0)

    def test_tampered_source_and_finalization(self):
        self.call(sampling_key="shared")
        (self.out / "finalized/one.json").write_bytes(b"{}")
        with self.assertRaises(I.ArtifactConflict):
            self.call()
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_tampered_body(self):
        self.call(sampling_key="shared")
        (self.out / "outputs/one.md").write_bytes(b"changed")
        with self.assertRaises(I.ArtifactConflict):
            self.call("two", sampling_key="shared")
        self.assertEqual(self.process.call_count, 1)

    def test_hold_write_failure_next_job_stays_blocked(self):
        self.process.side_effect = OSError("fictional launch failure")
        with mock.patch.object(I, "hold", side_effect=OSError("fictional hold write failure")):
            first = self.call()
        self.assertTrue(first["queue_stop"])
        self.assertIn("OSError", first["hold_write_error"])
        self.assertFalse(A.HOLD_FILE.exists())
        self.process.side_effect = None
        second = self.call("two", sampling_key="different")
        self.assertTrue(second["queue_stop"])
        self.assertEqual(second["attempts"], 0)
        self.assertEqual(self.process.call_count, 1)

    def test_ticket_write_failure_never_launches(self):
        original = I.exclusive_json
        def write(path, obj):
            if "inflight_v4" in Path(path).parts:
                raise OSError("fictional disk full before launch")
            return original(path, obj)
        with mock.patch.object(I, "exclusive_json", side_effect=write), self.assertRaises(OSError):
            self.call()
        self.assertEqual(self.process.call_count, 0)

    def test_cache_write_failure_never_resumes_unsealed_success(self):
        original = I.sample_record
        def sample(directory, job_id, identity, state, meta=None):
            if state == "ok":
                raise OSError("fictional final cache failure")
            return original(directory, job_id, identity, state, meta)
        with mock.patch.object(I, "sample_record", side_effect=sample), self.assertRaises(I.ArtifactConflict):
            self.call()
        with self.assertRaises(I.ArtifactConflict):
            self.call()
        self.assertFalse(I.queue_open(A.HOLD_FILE))
        self.assertEqual(self.process.call_count, 1)

    def test_metadata_handles_never_persist(self):
        fake = "FICTIONAL_HANDLE"
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(metadata={
            "sessionID": fake, "thread_id": fake, "text": "parentID=" + fake}), b"")
        self.assertEqual(self.call()["status"], "ok")
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertNotIn(fake.encode(), path.read_bytes())

    def test_body_protection_words_are_content(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(response="challenge rate limit 429 403 普通正文"), b"")
        self.assertEqual(self.call()["status"], "ok")

    def test_sensitive_body_rejected_not_rewritten(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, payload(response="thread_id=FICTIONAL_HANDLE"), b"")
        self.assertTrue(self.call()["queue_stop"])
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertNotIn(b"FICTIONAL_HANDLE", path.read_bytes())

    def test_completed_strict_and_terminal_metadata_required(self):
        for index, value in enumerate(("true", 1, False, None)):
            with self.subTest(value=value), mock.patch.object(A, "HOLD_FILE", self.root / ("provider%d/hold.json" % index)):
                self.out = self.root / ("run%d" % index)
                self.process.return_value = subprocess.CompletedProcess([], 0, payload(completed=value), b"")
                self.assertTrue(self.call()["queue_stop"])
        with self.assertRaises(ValueError):
            A.terminal_payload({"completed": True, "response": "x", "metadata": {}}, "gpt-5-6-thinking")

    def test_pre_submit_contract_not_just_phase(self):
        good = {"completed": False, "phase": "pre_submit", "error_code": "headless_runner_or_evidence_failed", "automatic_retry": False}
        self.process.return_value = subprocess.CompletedProcess([], 1, b"", json.dumps(good).encode())
        meta = self.call()
        self.assertTrue(meta["retry_safe"])
        self.assertFalse(meta["queue_stop"])
        self.assertTrue(I.queue_open(A.HOLD_FILE))
        for obj in ({"phase": "pre_submit"}, dict(good, model_request_sent=True), dict(good, automatic_retry=True)):
            self.assertFalse(A.pre_submit_payload(obj))

    def test_post_submit_unknown_timeout_and_protection_hold(self):
        for index, result in enumerate((subprocess.CompletedProcess([], 1, b"", b'{"phase":"post_submit_ambiguous"}'),
                                        subprocess.CompletedProcess([], 0, b"{", b""),
                                        subprocess.CompletedProcess([], 0, payload(), b"HTTP 429"))):
            with mock.patch.object(A, "HOLD_FILE", self.root / ("provider%d/hold.json" % index)):
                self.out = self.root / ("run%d" % index)
                self.process.return_value = result
                self.assertTrue(self.call()["queue_stop"])
        self.out = self.root / "timeout"
        self.process.side_effect = subprocess.TimeoutExpired("stub", 1, output=b"partial")
        self.assertTrue(self.call()["queue_stop"])

    def test_backend_unknown_or_wrong_not_success(self):
        for index, summary in enumerate(({}, {"model_slug": "gpt-6-thinking"}, {"debug": {"model_slug": "gpt-5-6-thinking"}})):
            self.out = self.root / ("run%d" % index)
            self.process.return_value = subprocess.CompletedProcess([], 0, payload(metadata={"server_metadata_summary": summary}), b"")
            meta = self.call()
            self.assertEqual(meta["status"], "failed")
            self.assertTrue(meta["terminal_verified"])

    def test_real_gate_closed_and_route_blocked(self):
        with mock.patch.object(I, "REAL_EXECUTION_APPROVED", False):
            meta = self.call()
        self.assertTrue(meta["queue_stop"])
        self.assertEqual(meta["attempts"], 0)
        with mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "blocked"}), self.assertRaises(I.PolicyBlocked):
            self.call("other")
        self.assertEqual(self.process.call_count, 0)


class RunnerFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        self.stack.enter_context(mock.patch.object(R, "SLOT_DIR", self.root / "slots"))
        self.stack.enter_context(mock.patch.object(R, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(R.legacy, "_build_task", return_value=([str(Path(__file__).resolve()), "-"], "raw", "MOCK_ONLY")))
        self.stack.enter_context(mock.patch.object(R.legacy, "_ensure_init"))
        self.stack.enter_context(mock.patch.object(R.legacy, "_STATE", {"env": {"PATH": "MOCK_ONLY"}}))
        self.process = self.stack.enter_context(mock.patch.object(R, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, codex(), b"")))

    def job(self, name="one", model="luna_noweb", **extra):
        return dict({"job_id": name, "model_key": model, "prompt": "冻结输入", "forbid_tools": ["bash"]}, **extra)


class RunnerTests(RunnerFixture):
    def test_codex_success_exact_resume(self):
        first = R.run_job(self.root / "run", self.job())
        self.assertEqual(first["status"], "ok")
        self.assertTrue(R.run_job(self.root / "run", self.job())["resumed"])
        self.assertEqual(self.process.call_count, 1)

    def test_opencode_success_handles_redacted(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, opencode(), b"")
        result = R.run_job(self.root / "run", self.job(model="gflash"))
        self.assertEqual(result["status"], "ok")
        raw = (self.root / "run" / result["stdout_file"]).read_text()
        self.assertNotIn("FICTIONAL_SESSION", raw)
        self.assertNotIn("FICTIONAL_MESSAGE", raw)

    def test_unknown_event_stops_later_provider_job(self):
        self.process.return_value = subprocess.CompletedProcess([], 0, codex([{"type": "turn.cancelled"}]), b"")
        results = R.run_jobs(self.root / "run", [self.job(), self.job("two")])
        self.assertTrue(results[0]["queue_stop"])
        self.assertEqual(results[1]["status"], "skipped_queue_stop")
        self.assertEqual(self.process.call_count, 1)

    def test_hold_write_failure_retains_ticket(self):
        self.process.side_effect = OSError("fictional process failure")
        with mock.patch.object(I, "hold", side_effect=OSError("fictional hold failure")):
            self.assertTrue(R.run_job(self.root / "run", self.job())["queue_stop"])
        second = R.run_job(self.root / "run", self.job("two"))
        self.assertTrue(second["queue_stop"])
        self.assertEqual(self.process.call_count, 1)

    def test_final_argv_identity_contains_sandbox_and_images(self):
        image = self.root / "fixture.png"
        image.write_bytes(b"synthetic not an actual image")
        ident = R.request_identity_for(self.job(model="luna", extra={"images": [str(image)]}))
        argv = ident["producer"]["argv"]
        self.assertIn("-i", argv)
        self.assertIn("workspace-write", argv)
        self.assertIn("sandbox_workspace_write.network_access=true", argv)
        changed = R.request_identity_for(self.job(model="luna"))
        self.assertNotEqual(ident, changed)

    def test_forbidden_tool_failed_with_complete_terminal(self):
        events = [{"type": "item.completed", "item": {"id": "command", "type": "command_execution", "status": "completed"}}]
        self.process.return_value = subprocess.CompletedProcess([], 0, codex(events), b"")
        result = R.run_job(self.root / "run", self.job())
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["terminal_verified"])
        self.assertFalse(result["queue_stop"])

    def test_real_gate_never_process(self):
        with mock.patch.object(I, "REAL_EXECUTION_APPROVED", False):
            result = R.run_job(self.root / "run", self.job())
        self.assertTrue(result["queue_stop"])
        self.assertEqual(self.process.call_count, 0)


class ExperimentTests(RunnerFixture):
    def test_wrapper_exact_rerun_zero_new_submissions(self):
        parser = lambda text: ({"value": text}, None)
        args = (self.root / "experiment", "why", "MOCK_ONLY", "luna_noweb", "冻结输入", parser, [2], "v4-test")
        first = E.call(*args, max_attempts=1)
        second = E.call(*args, max_attempts=1)
        self.assertTrue(first["parse_ok"])
        self.assertTrue(second["cached"])
        self.assertEqual(first["new_model_submissions"], 1)
        self.assertEqual(second["new_model_submissions"], 0)
        self.assertEqual(self.process.call_count, 1)

    def test_wrapper_fake_log_and_parser_error_never_success(self):
        out = self.root / "experiment"
        I.write_json(out / "cache_why_exact.json", {"records": [{"parse_ok": True, "parsed": {"fake": True}}]})
        parser = lambda text: ({"fake": True}, "must reject")
        result = E.call(out, "why", "MOCK_ONLY", "luna_noweb", "冻结输入", parser, [2], "v4-test", max_attempts=1)
        self.assertFalse(result["parse_ok"])
        self.assertIsNone(result["parsed"])
        self.assertEqual(self.process.call_count, 1)


if __name__ == "__main__":
    unittest.main()
