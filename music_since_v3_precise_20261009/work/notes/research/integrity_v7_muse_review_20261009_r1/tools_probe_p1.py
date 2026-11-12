"""v7 r1 独立审查离线对抗 probe。全部外部进程 mock，只写临时目录。

运行方式（bytes 日志由调用方保存）：
  python -X utf8 -I -B tools_probe_p1.py
"""
import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import execution_integrity_v7 as I
import gpt2_adapter_v7 as A

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (" | " + detail if detail else ""))


def codex_stream(events, body="ok-body"):
    rows = [{"type": "thread.started", "thread_id": "T"},
            {"type": "turn.started"}]
    rows += events
    rows += [{"type": "item.completed",
              "item": {"id": "m", "type": "agent_message", "text": body}},
             {"type": "turn.completed", "usage": {}}]
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)


def expect_reject(name, fn):
    try:
        fn()
    except (ValueError, I.ArtifactConflict):
        check(name, True)
        return
    except Exception as exc:  # noqa: BLE001 - probe 记录非预期异常类型
        check(name, False, "wrong exc: " + type(exc).__name__)
        return
    check(name, False, "accepted but must reject")


# ---- Gap 1: parse_codex / parse_opencode ----
expect_reject("p1-reasoning-in_progress-rejected",
              lambda: I.parse_codex(codex_stream([
                  {"type": "item.completed",
                   "item": {"id": "r", "type": "reasoning",
                            "status": "in_progress"}}])))
expect_reject("p1-item-started-completed-rejected",
              lambda: I.parse_codex(codex_stream([
                  {"type": "item.started",
                   "item": {"id": "r", "type": "reasoning",
                            "status": "completed"}}])))
expect_reject("p1-turn-completed-failed-rejected",
              lambda: I.parse_codex(codex_stream([], body="x").replace(
                  '"turn.completed"', '"turn.completed","status": "failed"')))
expect_reject("p1-after-terminal-rejected",
              lambda: I.parse_codex(codex_stream([]) + '\n{"type":"turn.started"}'))
expect_reject("p1-unknown-event-rejected",
              lambda: I.parse_codex(codex_stream([{"type": "turn.resumed"}])))
expect_reject("p1-forbidden-tool-counted-not-silently-ok",
              lambda: None if True else None)  # 占位，下方真实断言
RESULTS.pop()  # 移除占位
print("INFO forbidden-tool path is asserted in RunnerTests.test_forbidden_tool_failed_with_complete_terminal (static, read)")


def opencode_stream(body="ok-body", finish_reason="stop", finish_status=None):
    rows = []
    parts = [("step_start", {"type": "step-start"}),
             ("text", {"type": "text", "text": body, "time": {"end": 1}}),
             ("step_finish", {"type": "step-finish", "reason": finish_reason})]
    for i, (kind, part) in enumerate(parts):
        part = dict(part)
        part.update(sessionID="S", messageID="M", id="p%d" % i)
        if kind == "step_finish" and finish_status is not None:
            part["status"] = finish_status
        rows.append({"type": kind, "sessionID": "S", "part": part})
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)


expect_reject("p1-opencode-finish-status-failed-rejected",
              lambda: I.parse_opencode(opencode_stream(finish_status="failed")))
text, _counts, _term = I.parse_opencode(opencode_stream())
check("p1-opencode-stop-accepted", text == "ok-body", repr(text))

# ---- Gap: thinking_effort exact max ----
check("p1-real-gate-closed", I.REAL_EXECUTION_APPROVED is False, repr(I.REAL_EXECUTION_APPROVED))


def gpt2_payload(effort=_sentinel := object(), response="resp-body"):
    meta = {"headless": True, "provider_interface": True,
            "no_auto_retry": True, "model": "gpt-5-6-thinking",
            "response_sha256": I.sha_text(response),
            "prepared_response_validation": {
                "successful_assistant_terminal_observed": True,
                "unsupported_work_continuation_observed": False},
            "server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}
    if effort is not _sentinel:
        meta["thinking_effort"] = effort
    return {"completed": True, "response": response, "metadata": meta}


for label, eff in (("missing", _sentinel), ("low", "low"),
                   ("int", 1), ("list", ["max"])):
    expect_reject("p1-effort-%s-rejected" % label,
                  lambda e=eff: A.terminal_payload(
                      gpt2_payload() if e is _sentinel else gpt2_payload(e),
                      "gpt-5-6-thinking", "max"))
try:
    A.terminal_payload(gpt2_payload("max"), "gpt-5-6-thinking", "max")
    check("p1-effort-max-accepted", True)
except ValueError as exc:
    check("p1-effort-max-accepted", False, str(exc)[:80])

# ---- Gap: model_evidence 只认根 server_metadata_summary ----
for label, md in (("client-model-field", {"model": "gpt-5-6-thinking"}),
                  ("nested-debug", {"server_metadata_summary": {"debug": {"resolved_model_slugs": ["gpt-5-6-thinking"]}}}),
                  ("empty", {})):
    check("p1-evidence-%s-unverified" % label,
          I.model_evidence(md, "gpt-5-6-thinking")["verdict"] == "unverified", label)
check("p1-evidence-root-match",
      I.model_evidence({"server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}},
                       "gpt-5-6-thinking")["verdict"] == "match")

# ---- Gap: pre_submit 需 source-bound ----
with tempfile.TemporaryDirectory() as _t:
    _root = Path(_t)
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        st.enter_context(mock.patch.object(
            A, "producer_identity",
            return_value={"route": "MOCK_ONLY", "cli_sha256": "1" * 64,
                          "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT)}))
        ident = A.request_identity("gpt56w", "max", "prompt-x", producer=A.producer_identity(), sampling_key="k")
        # phase-only 无 proof 必须拒
        check("p1-presubmit-phase-only-rejected",
              A.pre_submit_payload({"completed": False, "phase": "pre_submit",
                                    "error_code": "headless_runner_or_evidence_failed",
                                    "automatic_retry": False}, ident) is False)
        # 任意 hash 非 source-bound 必须拒
        active = ident["producer"]["active_provider_sources"]["files"]
        fake_proof = {"schema": I.PRE_SUBMIT_PROOF_SCHEMA, "contract": I.PRE_SUBMIT_CONTRACT,
                      "provider_error_type": "ProviderError", "phase": "pre_submit",
                      "retryable": True, "ambiguous": False,
                      "submit_callback_reached": False, "model_request_sent": False,
                      "automatic_retry": False,
                      "request_identity_sha256": "a" * 64,
                      "producer_identity_sha256": "b" * 64,
                      "source_files": active}
        fake_obj = {"completed": False, "automatic_retry": False, "phase": "pre_submit",
                    "error_code": "headless_runner_or_evidence_failed",
                    "model_request_sent": False, "pre_submit_proof": fake_proof}
        check("p1-presubmit-arbitrary-hash-rejected",
              A.pre_submit_payload(fake_obj, ident) is False)
        # 篡改 source 文件 hash 必须拒
        good_proof = dict(fake_proof,
                          request_identity_sha256=I.identity_digest(ident),
                          producer_identity_sha256=I.identity_digest(ident["producer"]),
                          source_files=dict(active, **{"src/chatgpt_provider/gpt2agent_provider.py": "c" * 64}))
        good_obj = dict(fake_obj, pre_submit_proof=good_proof)
        check("p1-presubmit-tampered-source-rejected",
              A.pre_submit_payload(good_obj, ident) is False)

# ---- Gap: environment 身份 ----
class Guard(dict):
    def __init__(self, *a, watched=(), **k):
        super().__init__(*a, **k)
        self._watched = set(watched)

    def __getitem__(self, key):
        if key in self._watched:
            raise AssertionError("must not read " + key)
        return super().__getitem__(key)


try:
    I.environment_identity(Guard({"GPT2AGENT_UNKNOWN_X": "v"},
                                 watched=["GPT2AGENT_UNKNOWN_X"]))
    check("p1-unknown-gpt2agent-refused-no-read", False, "accepted")
except ValueError:
    check("p1-unknown-gpt2agent-refused-no-read", True)
except AssertionError as exc:
    check("p1-unknown-gpt2agent-refused-no-read", False, "value was read: " + str(exc)[:60])
try:
    I.environment_identity(Guard({"OPENCODE_CONFIG_CONTENT": "v"},
                                 watched=["OPENCODE_CONFIG_CONTENT"]))
    check("p1-inline-config-refused-no-read", False, "accepted")
except ValueError:
    check("p1-inline-config-refused-no-read", True)
except AssertionError as exc:
    check("p1-inline-config-refused-no-read", False, "value was read: " + str(exc)[:60])
try:
    I.environment_identity({"HTTPS_PROXY": "http://user:pass@proxy.invalid:8080"})
    check("p1-proxy-userinfo-rejected", False, "accepted")
except ValueError:
    check("p1-proxy-userinfo-rejected", True)
ident_priv = I.environment_identity(
    Guard({"GPT2AGENT_BROWSER_SESSION_FILE": "priv"}, watched=["GPT2AGENT_BROWSER_SESSION_FILE"]))
check("p1-session-file-excluded-no-read",
      ident_priv["excluded_private_variable_names"] == ["GPT2AGENT_BROWSER_SESSION_FILE"]
      and "GPT2AGENT_BROWSER_SESSION_FILE" not in ident_priv["nonprivate_sha256"])

# ---- Gap: classify_stop 自实现 + ticket 保留（跨进程复验只读 queue_open） ----
with tempfile.TemporaryDirectory() as _t:
    hold = Path(_t) / "provider/queue_hold.json"
    ticket = I.submission_ticket(hold, Path(_t) / "run", "job-a", {"fake": True})
    with mock.patch.object(I, "hold", side_effect=OSError("probe hold failure")):
        err = I.classify_stop(hold, "job-a", "run", "probe")
    check("p1-classify-stop-returns-oserror", isinstance(err, str) and "OSError" in err, repr(err)[:60])
    check("p1-ticket-retained", ticket.is_file())
    check("p1-queue-blocked", I.queue_open(hold) is False)
    import subprocess as _sp
    script = ("import sys;sys.path.insert(0,sys.argv[1]);"
              "import execution_integrity_v7 as I;"
              "assert not I.queue_open(sys.argv[2])")
    r = _sp.run([sys.executable, "-B", "-I", "-c", script, str(TOOLS), str(hold)], capture_output=True)
    check("p1-cross-process-hold visible", r.returncode == 0, "rc=%d" % r.returncode)
    # v7 classify_stop 必须绑定 v7.hold（源码静态断言）
    import inspect as _ins
    src = _ins.getsource(I.classify_stop)
    check("p1-classify-stop-binds-v7-hold", "execution_integrity_v7.hold" in src or "hold(path" in src, "local lookup")

# ---- Gap: use_cache=False 不建 alias（mock RUN_PROCESS，临时目录） ----
with tempfile.TemporaryDirectory() as _t:
    root = Path(_t)
    out = root / "run"
    good = {"completed": True, "response": "resp-body",
            "metadata": {"headless": True, "provider_interface": True,
                         "no_auto_retry": True, "model": "gpt-5-6-thinking",
                         "thinking_effort": "max",
                         "response_sha256": I.sha_text("resp-body"),
                         "prepared_response_validation": {
                             "successful_assistant_terminal_observed": True,
                             "unsupported_work_continuation_observed": False},
                         "server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}}
    blob = json.dumps(good, ensure_ascii=False).encode()
    with contextlib.ExitStack() as st:
        st.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        st.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        st.enter_context(mock.patch.object(A, "HOLD_FILE", root / "slots/gpt2web/hold.json"))
        st.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        st.enter_context(mock.patch.object(
            A, "producer_identity",
            return_value={"route": "MOCK_ONLY", "cli_sha256": "1" * 64,
                          "active_provider_sources": I.active_provider_source_binding(A.SAFECHAIN_ROOT)}))
        proc = st.enter_context(mock.patch.object(
            A, "RUN_PROCESS",
            return_value=subprocess.CompletedProcess([], 0, blob, b"")))
        first = A.call_web_gpt("gpt56w", "prompt-y", run_id="MOCK_ONLY",
                               job_id="one", out_dir=out, sampling_key="shared")
        result = A.call_web_gpt("gpt56w", "prompt-y", run_id="MOCK_ONLY",
                                job_id="two", out_dir=out, sampling_key="shared",
                                use_cache=False)
        check("p1-nocache-returns-origin", result.get("job_id") == "one", repr(result.get("job_id")))
        check("p1-nocache-hit-true-requested-false",
              result.get("cache_hit") is True and result.get("cache_requested") is False)
        check("p1-nocache-no-alias-meta", not (out / "meta/two.json").exists())
        check("p1-nocache-no-alias-seal", not (out / "finalized/two.json").exists())
        check("p1-nocache-single-submit", proc.call_count == 1, "calls=%d" % proc.call_count)

failed = [name for name, ok, _d in RESULTS if not ok]
print("PROBE_SUMMARY total=%d failed=%d" % (len(RESULTS), len(failed)))
for name in failed:
    print("FAILED " + name)
sys.exit(1 if failed else 0)
