"""v4 六缺口与磁盘 finalization 回归；所有模型/CLI 只 mock。"""
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import execution_integrity_v8 as I
import gpt2_adapter_v8 as A
import runner_v8 as R
import experiment_calls_v8 as E


def payload(completed=True, response="完整离线回答", metadata=None):
    meta = {"headless": True, "provider_interface": True, "no_auto_retry": True,
            "model": "gpt-5-6-thinking", "thinking_effort": "max", "response_sha256": I.sha_text(response),
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
            script = "import sys;sys.path.insert(0,sys.argv[1]);import execution_integrity_v8 as I;assert not I.queue_open(sys.argv[2])"
            child_argv = [sys.executable, "-X", "utf8", "-I", "-B", "-c", script, str(TOOLS), str(hold)]
            child_started = time.perf_counter()
            result = subprocess.run(child_argv, capture_output=True)
            child_runtime = round(time.perf_counter() - child_started, 6)
            child_stdout = result.stdout.decode("utf-8", "replace")
            child_stderr = result.stderr.decode("utf-8", "replace")
            report_dir = TOOLS.parent / "notes/research/integrity_v8_luna_impl_20261009_r1"
            report_dir.mkdir(parents=True, exist_ok=True)
            I.write_json(report_dir / "queue_child_run.json", {
                "argv": child_argv, "returncode": result.returncode,
                "elapsed_seconds": child_runtime,
                "stdout_bytes": len(result.stdout),
                "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
                "stdout": child_stdout,
                "stderr_bytes": len(result.stderr),
                "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
                "stderr": child_stderr,
                "purpose": "read-only queue_open cross-process check",
            })
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            with self.assertRaises(I.PolicyBlocked):
                I.submission_ticket(hold, Path(temp) / "another", "b", {"fake": False})

    def test_legacy_version_tickets_and_hold_are_preserved_and_block_queue(self):
        with tempfile.TemporaryDirectory() as temp:
            hold = Path(temp) / "provider/queue_hold.json"
            hold.parent.mkdir(parents=True)
            hold.write_text('{"legacy":"opaque"}', encoding="utf-8")
            self.assertFalse(I.queue_open(hold))
            self.assertEqual(hold.read_text(encoding="utf-8"), '{"legacy":"opaque"}')
            hold.unlink()
            for version in ("inflight_v4", "inflight_v5", "inflight_v6"):
                ticket = hold.parent / version / "retained.json"
                ticket.parent.mkdir(parents=True)
                ticket.write_text('{"legacy":"opaque"}', encoding="utf-8")
                with self.subTest(version=version):
                    self.assertFalse(I.queue_open(hold))
                    with self.assertRaises(I.PolicyBlocked):
                        I.submission_ticket(hold, Path(temp) / "new-run", "new-job", {})
                    self.assertTrue(ticket.is_file())
                ticket.unlink()


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
            "cli_version": "test", "cli_sha256": "1" * 64, "cli_source": {"missing": False}, "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT), "implementation": "v7"}))
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
        completion = I.strict_json((self.out / "meta/one.json").read_text(encoding="utf-8"))
        self.assertEqual(completion["execution_argv_sha256"], I.digest(completion["execution_argv"]))

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
            if "inflight_v8" in Path(path).parts:
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
        def source_bound_failure(argv, **kwargs):
            prompt_path = Path(argv[argv.index("--file") + 1])
            prompt_text = prompt_path.read_text(encoding="utf-8")
            producer = A.producer_identity()
            identity = A.request_identity("gpt56w", "max", prompt_text, producer=producer,
                                          sampling_key=prompt_path.stem)
            proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                     "provider_error_type": "ProviderError", "phase": "pre_submit", "retryable": True,
                     "ambiguous": False, "submit_callback_reached": False, "model_request_sent": False,
                     "automatic_retry": False, "request_identity_sha256": I.identity_digest(identity),
                     "producer_identity_sha256": I.identity_digest(producer),
                     "source_files": producer["active_provider_sources"]["files"]}
            good = {"completed": False, "phase": "pre_submit", "error_code": "headless_runner_or_evidence_failed",
                    "automatic_retry": False, "model_request_sent": False, "pre_submit_proof": proof}
            return subprocess.CompletedProcess(argv, 1, b"", json.dumps(good).encode())
        self.process.side_effect = source_bound_failure
        meta = self.call()
        self.assertTrue(meta["retry_safe"])
        self.assertFalse(meta["queue_stop"])
        self.assertTrue(I.queue_open(A.HOLD_FILE))
        for obj in ({"phase": "pre_submit"},
                    {"completed": False, "phase": "pre_submit", "error_code": "headless_runner_or_evidence_failed",
                     "automatic_retry": False, "model_request_sent": True},
                    {"completed": False, "phase": "pre_submit", "error_code": "headless_runner_or_evidence_failed",
                     "automatic_retry": True}):
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
        self.stack.enter_context(mock.patch.object(R, "build_task", return_value=([str(Path(__file__).resolve()), "-"], "raw", "MOCK_ONLY")))
        self.process = self.stack.enter_context(mock.patch.object(R, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, codex(), b"")))

    def job(self, name="one", model="luna_noweb", **extra):
        return dict({"job_id": name, "model_key": model, "prompt": "冻结输入", "forbid_tools": ["bash"]}, **extra)


class RunnerTests(RunnerFixture):
    def test_codex_success_exact_resume(self):
        first = R.run_job(self.root / "run", self.job())
        self.assertEqual(first["status"], "ok")
        self.assertTrue(R.run_job(self.root / "run", self.job())["resumed"])
        self.assertEqual(self.process.call_count, 1)

    def test_use_cache_false_returns_exact_source_without_alias_or_resubmit(self):
        first = R.run_job(self.root / "run", self.job("one", sampling_key="shared"))
        result = R.run_job(self.root / "run", self.job("two", sampling_key="shared", use_cache=False))
        self.assertEqual(first["status"], "ok")
        self.assertEqual(result["job_id"], "one")
        self.assertTrue(result["cache_hit"])
        self.assertFalse(result["cache_requested"])
        self.assertFalse((self.root / "run/meta/two.json").exists())
        self.assertFalse((self.root / "run/finalized/two.json").exists())
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


class GapClosureTests(RunnerFixture):
    def test_codex_status_is_allowlisted_by_event_and_phase(self):
        bad_rows = (
            [{"type": "item.completed", "item": {"id": "reason", "type": "reasoning", "status": "in_progress"}}],
            [{"type": "item.started", "item": {"id": "reason", "type": "reasoning", "status": "completed"}}],
            [{"type": "turn.completed", "usage": {}, "status": "failed"}],
            [{"type": "item.completed", "item": {"id": "reason", "type": "reasoning", "status": "mystery"}}],
        )
        for events in bad_rows:
            with self.subTest(events=events), self.assertRaises(ValueError):
                I.parse_codex(codex(events).decode("utf-8"))
        # The omission is admitted only for the exact legacy synthetic fixture shape.
        self.assertEqual(I.parse_codex(codex().decode("utf-8"))[0], "完整离线回答")

    def test_opencode_conflicting_finish_status_rejected(self):
        rows = json.loads("[" + opencode().decode("utf-8").replace("\n", ",") + "]")
        rows[-1]["part"]["status"] = "failed"
        stream = "\n".join(json.dumps(row, ensure_ascii=False) for row in rows)
        with self.assertRaises(ValueError):
            I.parse_opencode(stream)

    def test_default_parse_failure_stops_after_one_complete_sample(self):
        calls = 0
        def parser(text):
            nonlocal calls
            calls += 1
            return None, "synthetic parse failure"
        result = E.call(self.root / "parse-stop", "why", "MOCK_ONLY", "luna_noweb",
                        "frozen prompt", parser, [2], "v7-default-stop", max_attempts=2)
        self.assertFalse(result["parse_ok"])
        self.assertFalse(result["new_sample_taken"])
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(calls, 1)
        self.assertEqual(self.process.call_count, 1)
        self.assertEqual(result["new_model_submissions"], 1)
        self.assertTrue((self.root / "parse-stop" / result["attempts"][0]["output_file"]).is_file())

    def test_explicit_new_sample_may_keep_prompt_and_changes_sampling_identity(self):
        parsed = 0
        def parser(text):
            nonlocal parsed
            parsed += 1
            if parsed == 1:
                return None, "first sample parse failure"
            return {"value": "accepted fixture"}, None
        out = self.root / "explicit-same-prompt"
        result = E.call(out, "why", "MOCK_ONLY", "luna_noweb", "same frozen prompt",
                        parser, [2], "v7-sample", max_attempts=2,
                        allow_new_sample_on_parse_failure=True,
                        new_sample_reason="explicit offline resampling authorization",
                        new_sampling_key="declared-sample-two")
        self.assertTrue(result["parse_ok"])
        self.assertTrue(result["new_sample_taken"])
        self.assertEqual(result["new_sample_prompt_sha256"], I.sha_text("same frozen prompt"))
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(result["new_model_submissions"], 2)
        self.assertEqual(self.process.call_count, 2)
        self.assertEqual(len({row["request_identity_sha256"] for row in result["attempts"]}), 2)

    def test_explicit_second_sample_parse_failure_is_recorded_without_success(self):
        out = self.root / "explicit-second-fails"
        result = E.call(out, "why", "MOCK_ONLY", "luna_noweb", "same frozen prompt",
                        lambda text: (None, "parse still fails"), [2], "v7-sample-fail",
                        max_attempts=2, allow_new_sample_on_parse_failure=True,
                        new_sample_reason="explicit second sample only", new_sampling_key="sample-two")
        self.assertFalse(result["parse_ok"])
        self.assertIsNone(result["parsed"])
        self.assertTrue(result["new_sample_taken"])
        self.assertEqual(result["new_sample_reason"], "explicit second sample only")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(self.process.call_count, 2)
        for row in result["attempts"]:
            self.assertTrue((out / row["output_file"]).is_file())
            self.assertFalse(row["parse_ok"])

    def test_parser_exception_is_failure_and_does_not_resubmit(self):
        def parser(_text):
            raise RuntimeError("synthetic parser exception")
        result = E.call(self.root / "parser-exception", "why", "MOCK_ONLY", "luna_noweb",
                        "frozen prompt", parser, [2], "v7-parser-error", max_attempts=2)
        self.assertFalse(result["parse_ok"])
        self.assertIsNone(result["parsed"])
        self.assertIn("RuntimeError", result["parse_error"])
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(self.process.call_count, 1)

    def test_new_sample_requires_reason_key_and_budget(self):
        parser = lambda text: (None, "parse failure")
        for kwargs in ({"allow_new_sample_on_parse_failure": True},
                       {"allow_new_sample_on_parse_failure": True, "new_sample_reason": "reason"},
                       {"allow_new_sample_on_parse_failure": True, "new_sample_reason": "reason",
                        "new_sampling_key": "new", "max_attempts": 1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                E.call(self.root / "invalid-opt-in", "why", "MOCK_ONLY", "luna_noweb",
                       "frozen", parser, [2], "v7-invalid", **kwargs)
        self.assertEqual(self.process.call_count, 0)

    def test_ambiguous_post_submit_is_never_retried(self):
        self.process.side_effect = subprocess.TimeoutExpired("mock-provider", 1, output=b"partial")
        result = E.call(self.root / "ambiguous", "why", "MOCK_ONLY", "luna_noweb",
                        "frozen prompt", lambda text: ({"ok": True}, None), [2], "v7-ambiguous",
                        max_attempts=3)
        self.assertFalse(result["parse_ok"])
        self.assertTrue(result["queue_stop"])
        self.assertEqual(len(result["attempts"]), 1)
        self.assertEqual(self.process.call_count, 1)


class LedgerGapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.addCleanup(self.temp.cleanup)
        self.stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        self.stack.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        self.stack.enter_context(mock.patch.object(A, "HOLD_FILE", self.root / "slots/gpt2web/hold.json"))
        self.stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **kw: contextlib.nullcontext()))
        producer = {"route": "MOCK_ONLY", "cli": "stub", "cli_version": "test",
                    "cli_sha256": "1" * 64, "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT),
                    "implementation": "v7"}
        self.stack.enter_context(mock.patch.object(A, "producer_identity", return_value=producer))
        self.process = self.stack.enter_context(mock.patch.object(
            A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload(), b"")))
        self.out = self.root / "run"

    def call(self, name="one", prompt="冻结输入\n第二行", sampling_key="shared", **kwargs):
        return A.call_web_gpt("gpt56w", prompt, run_id="MOCK_ONLY", job_id=name,
                              out_dir=self.out, sampling_key=sampling_key, **kwargs)

    def test_retained_legacy_seal_blocks_same_sample_after_ledgers_removed(self):
        first = self.call()
        for folder in ("cache", "pending", "meta"):
            for path in (self.out / folder).glob("*.json"):
                path.unlink()
        with self.assertRaises(I.ArtifactConflict):
            self.call("second")
        self.assertEqual(first["status"], "ok")
        self.assertEqual(self.process.call_count, 1)
        self.assertTrue((self.out / "finalized/one.json").is_file())

    def test_bad_and_legacy_ledger_shapes_fail_closed(self):
        cases = {
            "legacy_seal": ("finalized", "old", {"schema": "20261009.v4", "job_id": "old"}),
            "bad_schema": ("pending", "old", {"schema": "wrong", "job_id": "old"}),
            "bad_job_id": ("pending", "old", {"schema": I.VERSION, "job_id": "different",
                                                   "request_identity": {}, "request_identity_sha256": "0" * 64}),
            "missing_identity": ("pending", "old", {"schema": I.VERSION, "job_id": "old"}),
        }
        for index, (name, (folder, stem, value)) in enumerate(cases.items()):
            target = self.root / ("case%d" % index)
            I.write_json(target / folder / (stem + ".json"), value)
            with self.subTest(name=name), self.assertRaises(I.ArtifactConflict):
                A.call_web_gpt("gpt56w", "fresh", run_id="MOCK_ONLY", job_id="new-%d" % index,
                               out_dir=target, sampling_key="unique-%d" % index)
        self.assertEqual(self.process.call_count, 0)

    def test_nonobject_and_unreadable_ledgers_fail_closed(self):
        for index, contents in enumerate((b"[]", b"{broken")):
            target = self.root / ("corrupt%d" % index)
            path = target / "meta" / ("broken%d.json" % index)
            path.parent.mkdir(parents=True)
            path.write_bytes(contents)
            with self.subTest(index=index), self.assertRaises(I.ArtifactConflict):
                A.call_web_gpt("gpt56w", "fresh", run_id="MOCK_ONLY", job_id="new%d" % index,
                               out_dir=target, sampling_key="unique%d" % index)
        self.assertEqual(self.process.call_count, 0)

    def test_orphan_prompt_and_output_fail_closed(self):
        for index, folder in enumerate(("prompts", "outputs")):
            target = self.root / ("orphan%d" % index)
            path = target / folder / ("stray%d.txt" % index)
            if folder == "outputs":
                path = target / folder / ("stray%d.md" % index)
            path.parent.mkdir(parents=True)
            path.write_text("orphan", encoding="utf-8")
            with self.subTest(folder=folder), self.assertRaises(I.ArtifactConflict):
                A.call_web_gpt("gpt56w", "fresh", run_id="MOCK_ONLY", job_id="new%d" % index,
                               out_dir=target, sampling_key="unique%d" % index)
        self.assertEqual(self.process.call_count, 0)

    def test_valid_unrelated_sample_does_not_block_new_identity(self):
        self.assertEqual(self.call("one", prompt="prompt one", sampling_key="one")['status'], "ok")
        second = A.call_web_gpt("gpt56w", "prompt two", run_id="MOCK_ONLY", job_id="two",
                                out_dir=self.out, sampling_key="two")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(self.process.call_count, 2)

    def test_use_cache_false_returns_exact_source_without_alias_or_submission(self):
        first = self.call("one", sampling_key="same")
        result = self.call("two", sampling_key="same", use_cache=False)
        self.assertEqual(first["status"], "ok")
        self.assertTrue(result["cache_hit"])
        self.assertFalse(result["cache_requested"])
        self.assertTrue(result["cache_bypassed"])
        self.assertEqual(result["job_id"], "one")
        self.assertFalse((self.out / "meta/two.json").exists())
        self.assertFalse((self.out / "finalized/two.json").exists())
        self.assertEqual(self.process.call_count, 1)

    def test_cache_index_cannot_be_redirected_to_cache_alias(self):
        self.call("one", sampling_key="shared")
        alias = self.call("two", sampling_key="shared")
        cache_path = next((self.out / "cache").glob("*.json"))
        cache = I.strict_json(cache_path.read_text(encoding="utf-8"))
        cache["source_job_id"] = "two"
        cache["source_meta_sha256"] = I.sha_file(self.out / "meta/two.json")
        I.write_json(cache_path, cache)
        with self.assertRaises(I.ArtifactConflict):
            self.call("three", sampling_key="shared")
        self.assertTrue(alias["cache_hit"])
        self.assertEqual(self.process.call_count, 1)

    def test_finalize_or_cache_failure_cannot_be_reported_as_success(self):
        original = I.sample_record
        def fail_cache(directory, job_id, identity, state, meta=None):
            raise OSError("synthetic cache fsync failure")
        with mock.patch.object(I, "sample_record", side_effect=fail_cache), self.assertRaises(I.ArtifactConflict):
            self.call()
        self.assertEqual(self.process.call_count, 1)
        self.assertFalse(I.queue_open(A.HOLD_FILE))


class EnvironmentGapTests(unittest.TestCase):
    def test_proxy_cases_and_known_behavior_values_change_identity(self):
        for name in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy",
                     "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy",
                     "GPT2AGENT_TURN_TIMEOUT_SECONDS", "GPT2AGENT_MAX_ACTIVE_TURNS",
                     "GPT2AGENT_SUSPECTED_FALLBACK_SECONDS", "GPT2AGENT_TEXT_ONLY",
                     "GPT2AGENT_PREPARE_PROFILE", "GPT2AGENT_PAYLOAD_PROFILE",
                     "GPT2AGENT_HTTP_PROFILE", "GPT2AGENT_PREPARE_WAIT_SECONDS"):
            base = {"PATH": "stable", name: "value-a"}
            changed = {"PATH": "stable", name: "value-b"}
            with self.subTest(name=name):
                self.assertNotEqual(I.environment_identity(base), I.environment_identity(changed))

    def test_proxy_userinfo_or_query_is_rejected_not_silently_skipped(self):
        for value in ("http://user:pass@proxy.invalid:8080", "http://proxy.invalid:8080/?token=not-real"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                I.environment_identity({"HTTPS_PROXY": value})

    def test_unknown_gpt2agent_name_refused_without_reading_value(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key == "GPT2AGENT_UNKNOWN_SECRET_OVERRIDE":
                    raise AssertionError("unknown value must not be read")
                return super().__getitem__(key)
        env = Guard({"GPT2AGENT_UNKNOWN_SECRET_OVERRIDE": "synthetic"})
        with self.assertRaises(ValueError):
            I.environment_identity(env)

    def test_known_private_session_variable_is_excluded_without_reading_value(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key == "GPT2AGENT_BROWSER_SESSION_FILE":
                    raise AssertionError("private path value must not be read")
                return super().__getitem__(key)
        identity = I.environment_identity(Guard({"GPT2AGENT_BROWSER_SESSION_FILE": "synthetic-private-path"}))
        self.assertEqual(identity["excluded_private_variable_names"], ["GPT2AGENT_BROWSER_SESSION_FILE"])
        self.assertNotIn("GPT2AGENT_BROWSER_SESSION_FILE", identity["nonprivate_sha256"])

    def test_inline_private_config_value_is_not_read_or_hashed(self):
        class Guard(dict):
            def __getitem__(self, key):
                if key == "OPENCODE_CONFIG_CONTENT":
                    raise AssertionError("inline private config must not be read")
                return super().__getitem__(key)
        with self.assertRaises(ValueError):
            I.environment_identity(Guard({"OPENCODE_CONFIG_CONTENT": "synthetic-private-config"}))

    def test_seal_limitation_and_real_gate_are_explicit(self):
        self.assertFalse(I.REAL_EXECUTION_APPROVED)
        self.assertIn("not a MAC", I.SEAL_LIMITATION)


class GPT2ExperimentGapTests(unittest.TestCase):
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
        producer = {"route": "MOCK_ONLY", "cli": "stub", "cli_version": "test",
                    "cli_sha256": "1" * 64, "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT),
                    "implementation": "v7"}
        self.stack.enter_context(mock.patch.object(A, "producer_identity", return_value=producer))
        self.process = self.stack.enter_context(mock.patch.object(
            A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload(), b"")))

    def _identity(self, prompt="冻结输入", job_id="one", producer=None):
        return A.request_identity("gpt56w", "max", prompt, producer=producer or A.producer_identity(),
                                  sampling_key=job_id)

    def test_requested_effort_must_match_exact_returned_string(self):
        base = json.loads(payload().decode("utf-8"))
        for value in (None, "low", 1, ["max"]):
            changed = json.loads(json.dumps(base))
            if value is None:
                changed["metadata"].pop("thinking_effort", None)
            else:
                changed["metadata"]["thinking_effort"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                A.terminal_payload(changed, "gpt-5-6-thinking", "max")

    def test_nonempty_arbitrary_hash_is_not_source_bound_retry_proof(self):
        identity = self._identity()
        active = identity["producer"]["active_provider_sources"]["files"]
        proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                 "provider_error_type": "ProviderError", "phase": "pre_submit", "retryable": True,
                 "ambiguous": False, "submit_callback_reached": False, "model_request_sent": False,
                 "automatic_retry": False, "request_identity_sha256": "a" * 64,
                 "producer_identity_sha256": "b" * 64, "source_files": active}
        obj = {"completed": False, "automatic_retry": False, "phase": "pre_submit",
               "error_code": "headless_runner_or_evidence_failed", "model_request_sent": False,
               "pre_submit_proof": proof}
        self.assertFalse(A.pre_submit_payload(obj, identity))
        proof["request_identity_sha256"] = I.identity_digest(identity)
        proof["producer_identity_sha256"] = I.identity_digest(identity["producer"])
        proof["source_files"] = dict(active, **{"src/chatgpt_provider/gpt2agent_provider.py": "c" * 64})
        self.assertFalse(A.pre_submit_payload(obj, identity))

    def test_use_cache_false_never_creates_alias_or_resubmits(self):
        first = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="one",
                               out_dir=self.out, sampling_key="shared")
        result = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="two",
                                out_dir=self.out, sampling_key="shared", use_cache=False)
        self.assertEqual(first["status"], "ok")
        self.assertTrue(result["cache_hit"])
        self.assertFalse(result["cache_requested"])
        self.assertEqual(result["job_id"], "one")
        self.assertFalse((self.out / "meta/two.json").exists())
        self.assertEqual(self.process.call_count, 1)

    def test_source_bound_pre_submit_retry_uses_same_frozen_prompt_new_attempt(self):
        calls = 0
        real_run = R.run_job
        def make_pre_submit(directory, job, timeout):
            nonlocal calls
            calls += 1
            if calls > 1:
                return real_run(directory, job, timeout)
            identity = R.request_identity_for(job)
            job_id = job["job_id"]
            I.reserve(directory, job_id, identity)
            prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
            I.write_text(I.run_artifact_path(directory, prompt_rel), job["prompt"])
            I.write_text(I.run_artifact_path(directory, output_rel), "")
            producer = identity["producer"]
            proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                     "provider_error_type": "ProviderError", "phase": "pre_submit", "retryable": True,
                     "ambiguous": False, "submit_callback_reached": False, "model_request_sent": False,
                     "automatic_retry": False, "request_identity_sha256": I.identity_digest(identity),
                     "producer_identity_sha256": I.identity_digest(producer),
                     "source_files": producer["active_provider_sources"]["files"]}
            meta = {"schema": I.VERSION, "job_id": job_id,
                    "request_identity": identity, "request_identity_sha256": I.identity_digest(identity),
                    "producer_identity": producer, "prompt_file": prompt_rel,
                    "output_file": output_rel, "prompt_sha256": I.sha_text(job["prompt"]),
                    "status": "failed", "terminal_verified": False, "queue_stop": False,
                    "retry_safe": True, "failure_phase": "pre_submit",
                    "submission_state": "proven_not_submitted", "pre_submit_proof": proof,
                    "error": "source-bound pre-submit failure", "attempts": 1,
                    "provider_submissions": 0}
            I.write_json(I.run_artifact_path(directory, "meta/" + job_id + ".json"), meta)
            I.finalize(directory, job_id, meta)
            return meta
        out = self.root / "experiment-pre-submit"
        with mock.patch.object(E.runner, "run_job", side_effect=make_pre_submit):
            result = E.call(out, "why", "MOCK_ONLY", "gpt56w", "same exact prompt",
                            lambda text: ({"value": text}, None), [2], "v7-transport",
                            max_attempts=2)
        self.assertTrue(result["parse_ok"])
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(result["attempts"][0]["attempt_kind"], "proven_pre_submit_transport_failure")
        self.assertEqual(result["new_model_submissions"], 1)
        self.assertEqual(self.process.call_count, 1)
        first_prompt = next((out / "prompts").glob("*s0_t0.txt"))
        second_prompt = next((out / "prompts").glob("*s0_t1.txt"))
        self.assertEqual(first_prompt.read_bytes(), second_prompt.read_bytes())

    def test_cache_alias_does_not_overwrite_original_source(self):
        A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="one",
                       out_dir=self.out, sampling_key="shared")
        alias = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="two",
                               out_dir=self.out, sampling_key="shared")
        cache_path = next((self.out / "cache").glob("*.json"))
        cache = I.strict_json(cache_path.read_text(encoding="utf-8"))
        self.assertEqual(cache["source_job_id"], "one")
        self.assertTrue(alias["cache_hit"])
        self.assertEqual(self.process.call_count, 1)


class V8RegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        self.stack.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        self.stack.enter_context(mock.patch.object(A, "HOLD_FILE", self.root / "slots/gpt2web/hold.json"))
        self.stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *args, **kwargs: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(R, "SLOT_DIR", self.root / "slots"))
        self.stack.enter_context(mock.patch.object(R, "Slot", side_effect=lambda *args, **kwargs: contextlib.nullcontext()))
        self.stack.enter_context(mock.patch.object(
            R, "build_task", return_value=([str(Path(__file__).resolve()), "-"], "raw", "MOCK_ONLY")))
        producer = {
            "route": "MOCK_ONLY", "cli": "stub", "cli_version": "test",
            "cli_sha256": "1" * 64,
            "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT),
            "implementation": "v8 synthetic fixture",
        }
        self.stack.enter_context(mock.patch.object(A, "producer_identity", return_value=producer))
        self.provider_process = self.stack.enter_context(mock.patch.object(
            A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload(), b"")))
        self.runner_process = self.stack.enter_context(mock.patch.object(
            R, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, codex(), b"")))

    def _valid_pre_submit(self):
        files = {name: "a" * 64 for name in I.ACTIVE_PROVIDER_SOURCE_RELATIVE}
        producer = {"active_provider_sources": {"complete": True, "files": files}, "route": "synthetic"}
        identity = {
            "schema": I.VERSION, "producer": producer, "model_key": "gpt56w",
            "requested_model": "gpt-5-6-thinking", "requested_effort": "max",
            "prompt_sha256": "b" * 64, "sampling_key": "synthetic-sample",
        }
        proof = {
            "schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
            "provider_error_type": "ProviderError", "phase": "pre_submit",
            "retryable": True, "ambiguous": False, "submit_callback_reached": False,
            "model_request_sent": False, "automatic_retry": False,
            "request_identity_sha256": I.identity_digest(identity),
            "producer_identity_sha256": I.identity_digest(producer), "source_files": files,
        }
        meta = {
            "status": "failed", "failure_phase": "pre_submit", "retry_safe": True,
            "queue_stop": False, "terminal_verified": False,
            "submission_state": "proven_not_submitted", "pre_submit_proof": proof,
        }
        return meta, identity

    def test_pre_submit_flags_are_exact_booleans_for_each_field(self):
        meta, identity = self._valid_pre_submit()
        self.assertTrue(I.verify_pre_submit_proof(meta, identity))
        expected = {
            "retryable": True, "ambiguous": False, "submit_callback_reached": False,
            "model_request_sent": False, "automatic_retry": False,
        }
        malformed = (0, 1, 0.0, 1.0, "false", "true", None, [], {},)
        for field, required in expected.items():
            for value in (*malformed, not required):
                candidate = json.loads(json.dumps(meta))
                candidate["pre_submit_proof"][field] = value
                with self.subTest(field=field, value=value):
                    self.assertFalse(I.verify_pre_submit_proof(candidate, identity))
            candidate = json.loads(json.dumps(meta))
            del candidate["pre_submit_proof"][field]
            with self.subTest(field=field, value="missing"):
                self.assertFalse(I.verify_pre_submit_proof(candidate, identity))

    def test_pre_submit_requires_complete_identity_source_and_verifier(self):
        meta, identity = self._valid_pre_submit()
        self.assertTrue(I.verify_pre_submit_proof(meta, identity))
        tamper_cases = []
        for field, value in (("model_key", "gpt6w"), ("prompt_sha256", "c" * 64),
                             ("requested_effort", "low"), ("sampling_key", "changed")):
            changed = json.loads(json.dumps(identity))
            changed[field] = value
            tamper_cases.append(("identity." + field, meta, changed))
        changed = json.loads(json.dumps(identity))
        changed["producer"]["route"] = "other-producer"
        tamper_cases.append(("producer", meta, changed))
        changed = json.loads(json.dumps(meta))
        changed["pre_submit_proof"]["request_identity_sha256"] = "f" * 64
        tamper_cases.append(("request digest only", changed, identity))
        changed = json.loads(json.dumps(meta))
        changed["pre_submit_proof"]["producer_identity_sha256"] = "f" * 64
        tamper_cases.append(("producer digest only", changed, identity))
        changed = json.loads(json.dumps(meta))
        first = I.ACTIVE_PROVIDER_SOURCE_RELATIVE[0]
        changed["pre_submit_proof"]["source_files"][first] = "f" * 64
        tamper_cases.append(("proof source file", changed, identity))
        changed = json.loads(json.dumps(identity))
        changed["producer"]["active_provider_sources"]["files"][first] = "f" * 64
        tamper_cases.append(("identity source file", meta, changed))
        for name, candidate, candidate_identity in tamper_cases:
            with self.subTest(tamper=name):
                self.assertFalse(I.verify_pre_submit_proof(candidate, candidate_identity))

        unknown = dict(meta, submission_state="unknown_after_ticket")
        self.assertFalse(I.verify_pre_submit_proof(unknown, identity))
        outer_flag_tamper = dict(meta, queue_stop=0)
        self.assertFalse(I.verify_pre_submit_proof(outer_flag_tamper, identity))
        envelope = {
            "completed": False, "automatic_retry": False, "phase": "pre_submit",
            "error_code": "headless_runner_or_evidence_failed", "model_request_sent": False,
            "pre_submit_proof": meta["pre_submit_proof"],
        }
        self.assertFalse(A.pre_submit_payload(envelope))
        self.assertTrue(A.pre_submit_payload(envelope, identity))

    def test_strict_json_rejects_scalars_duplicate_nonfinite_and_multiple_documents(self):
        self.assertEqual(I.strict_json('{"safe":true}'), {"safe": True})
        for text in ('true', '0', 'null', '"scalar"', '{} {}', '[]\n[]',
                     '{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                I.strict_json(text)

    def test_retained_v7_inflight_ticket_blocks_v8_without_mutation(self):
        hold = self.root / "provider/queue_hold.json"
        ticket = hold.parent / "inflight_v7/retained.json"
        ticket.parent.mkdir(parents=True)
        ticket.write_text('{"legacy":"opaque"}', encoding="utf-8")
        before = ticket.read_bytes()
        self.assertFalse(I.queue_open(hold))
        with self.assertRaises(I.PolicyBlocked):
            I.submission_ticket(hold, self.root / "another-run", "new-job", {})
        self.assertEqual(ticket.read_bytes(), before)

    def test_explicit_new_sample_budget_three_rejects_before_any_write_or_process(self):
        for index, budget in enumerate((3, 4, 2.0, True)):
            out = self.root / ("new-sample-budget-%d" % index)
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                E.call(out, "why", "MOCK_ONLY", "gpt56w", "frozen prompt",
                       lambda _text: (None, "parse failure"), [2], "v8-budget",
                       max_attempts=budget, allow_new_sample_on_parse_failure=True,
                       new_sample_reason="explicit synthetic authorization",
                       new_sampling_key="different-sampling-key")
            self.assertFalse(out.exists())
        self.assertEqual(self.provider_process.call_count, 0)
        self.assertEqual(self.runner_process.call_count, 0)

    def _write_pre_submit_attempt(self, directory, job, timeout=3600):
        identity = R.request_identity_for(job)
        job_id = job["job_id"]
        I.reserve(directory, job_id, identity)
        prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
        I.write_text(I.run_artifact_path(directory, prompt_rel), job["prompt"])
        I.write_text(I.run_artifact_path(directory, output_rel), "")
        producer = identity["producer"]
        proof = {
            "schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
            "provider_error_type": "ProviderError", "phase": "pre_submit",
            "retryable": True, "ambiguous": False, "submit_callback_reached": False,
            "model_request_sent": False, "automatic_retry": False,
            "request_identity_sha256": I.identity_digest(identity),
            "producer_identity_sha256": I.identity_digest(producer),
            "source_files": producer["active_provider_sources"]["files"],
        }
        meta = {
            "schema": I.VERSION, "job_id": job_id, "request_identity": identity,
            "request_identity_sha256": I.identity_digest(identity),
            "producer_identity": producer, "prompt_file": prompt_rel,
            "output_file": output_rel, "prompt_sha256": I.sha_text(job["prompt"]),
            "status": "failed", "terminal_verified": False, "queue_stop": False,
            "retry_safe": True, "failure_phase": "pre_submit",
            "submission_state": "proven_not_submitted", "pre_submit_proof": proof,
            "error": "synthetic source-bound pre-submit failure", "attempts": 1,
            "provider_submissions": 0,
        }
        I.write_json(I.run_artifact_path(directory, "meta/" + job_id + ".json"), meta)
        I.finalize(directory, job_id, meta)
        return meta

    def test_default_three_attempt_transport_budget_remains_proof_bounded(self):
        out = self.root / "default-transport-budget"
        with mock.patch.object(E.runner, "run_job", side_effect=self._write_pre_submit_attempt) as run_job:
            result = E.call(out, "why", "MOCK_ONLY", "gpt56w", "same frozen prompt",
                            lambda text: ({"value": text}, None), [2], "v8-transport-default")
        self.assertFalse(result["parse_ok"])
        self.assertFalse(result["new_sample_taken"])
        self.assertEqual(len(result["attempts"]), 3)
        self.assertEqual(run_job.call_count, 3)
        self.assertEqual(result["new_model_submissions"], 0)
        self.assertEqual(self.provider_process.call_count, 0)
        self.assertEqual(self.runner_process.call_count, 0)

    def test_explicit_two_sample_failure_retains_both_exact_terminal_artifacts(self):
        out = self.root / "two-sample-terminal-failure"
        reason = "explicit synthetic second sample"
        result = E.call(out, "why", "MOCK_ONLY", "gpt56w", "same frozen prompt",
                        lambda _text: (None, "complete parse failure"), [2], "v8-two-samples",
                        max_attempts=2, allow_new_sample_on_parse_failure=True,
                        new_sample_reason=reason, new_sampling_key="new-sampling-identity")
        self.assertFalse(result["parse_ok"])
        self.assertTrue(result["new_sample_taken"])
        self.assertEqual(result["new_sample_reason"], reason)
        self.assertEqual(result["new_sample_prompt_sha256"], I.sha_text("same frozen prompt"))
        self.assertEqual(result["new_sample_sampling_key_sha256"], I.sha_text("new-sampling-identity"))
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(len({row["request_identity_sha256"] for row in result["attempts"]}), 2)
        for row in result["attempts"]:
            meta = I.strict_json((out / "meta" / (row["job_id"] + ".json")).read_text(encoding="utf-8"))
            self.assertTrue(meta["terminal_verified"])
            self.assertTrue((out / meta["stdout_file"]).is_file())
            self.assertTrue((out / meta["stderr_file"]).is_file())
        self.assertEqual(self.provider_process.call_count, 2)
        self.assertEqual(self.runner_process.call_count, 0)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
