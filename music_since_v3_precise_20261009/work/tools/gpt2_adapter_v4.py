"""gpt2 v4 单提交；真实执行默认关闭，旧 hold 永不由此入口解除。"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import execution_integrity as old
import execution_integrity_v4 as I

ADAPTER_VERSION = "r4_20261009"
GPT2_CMD = os.environ.get("MUSIC_GPT2_CMD", r"D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd")
SAFECHAIN_ROOT = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", r"D:\musicclaude\gpt2agent-safechain"))
HOLD_FILE = I.SLOT_DIR / "gpt2web/queue_hold.json"
MODEL_ROUTES = {"gpt56w": "gpt-5-6-thinking", "gpt6w": "gpt-6-thinking"}
RUN_PROCESS, Slot = I.run_process, I.Slot


def producer_identity(gpt2_cmd=None):
    cmd = Path(gpt2_cmd or GPT2_CMD)
    files = {}
    for path in (cmd, SAFECHAIN_ROOT / ".venv-local/Scripts/python.exe", Path(sys.executable)):
        if path.is_file():
            files[str(path.resolve())] = I.sha_file(path)
    cp = subprocess.run(["git", "-C", str(SAFECHAIN_ROOT), "rev-parse", "HEAD"],
                        capture_output=True, timeout=30,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return {"schema": I.VERSION, "route": "gpt2", "adapter_version": ADAPTER_VERSION,
            "implementations": I.implementation_identity(), "cli": str(cmd.resolve()),
            "cli_sha256": I.sha_file(cmd) if cmd.is_file() else None,
            "cli_version": cp.stdout.decode("utf-8", "strict").strip() if cp.returncode == 0 else "unknown",
            "cli_source": old.source_fingerprint(SAFECHAIN_ROOT, ("bin", "src", "tools/chatgpt_web", "vendor/gpt2agent")),
            "runtime_files": files, "environment": I.environment_identity(os.environ),
            "execution_argv_template": _cmd_argv(cmd) + ["ask", "--file", "<exact-prompt-file>", "--model", "<requested-model>", "--json"],
            "coverage_limit": "fingerprinted source/known runtime only; private store, Docker image and external service not frozen; real gate closed"}


def request_identity(model_key, effort, prompt_text, *, producer=None, sampling_key="", request_context=None):
    value = {"schema": I.VERSION, "producer": producer or producer_identity(), "model_key": model_key,
             "requested_model": MODEL_ROUTES.get(model_key), "requested_effort": effort,
             "prompt_sha256": I.sha_text(prompt_text), "sampling_key": sampling_key}
    if request_context is not None:
        value["request_context"] = request_context
    return value


def _cmd_argv(cmd):
    return ["cmd.exe", "/c", str(cmd)] if sys.platform == "win32" and str(cmd).lower().endswith((".cmd", ".bat")) else [str(cmd)]


def terminal_payload(payload, requested):
    if (not isinstance(payload, dict) or payload.get("completed") is not True
            or not isinstance(payload.get("response"), str) or not payload["response"].strip()):
        raise ValueError("incomplete/unknown GPT2 terminal")
    meta = payload.get("metadata")
    if not isinstance(meta, dict):
        raise ValueError("missing headless provider metadata")
    validation = meta.get("prepared_response_validation")
    if (meta.get("headless") is not True or meta.get("provider_interface") is not True
            or meta.get("no_auto_retry") is not True or meta.get("model") != requested
            or meta.get("response_sha256") != I.sha_text(payload["response"])
            or not isinstance(validation, dict)
            or validation.get("successful_assistant_terminal_observed") is not True
            or validation.get("unsupported_work_continuation_observed") is not False):
        raise ValueError("missing/conflicting GPT2 provider terminal/binding/hash")
    return {"schema": "gpt2_headless_provider_v4", "terminal": "successful_assistant_terminal_observed",
            "unsupported_work_continuation_observed": False}


def pre_submit_payload(payload):
    # 两条源代码契约：gpt2_cli Docker 检查；headless_client ProviderError。
    return (isinstance(payload, dict) and payload.get("completed") is False
            and payload.get("automatic_retry") is False and payload.get("phase") == "pre_submit"
            and isinstance(payload.get("error_code"), str) and bool(payload["error_code"])
            and ("model_request_sent" not in payload or payload["model_request_sent"] is False))


def call_web_gpt(model_key, prompt_text, *, run_id, job_id, out_dir, effort="max", timeout=1800,
                 max_attempts=1, gpt2_cmd=None, sampling_key=None, use_cache=True, request_context=None,
                 expected_identity=None):
    old.check_policy(model_key)
    I.valid_id(job_id)
    I.assert_content_safe(prompt_text)
    if (model_key not in MODEL_ROUTES or effort != "max" or len(prompt_text) > 65536
            or type(max_attempts) is not int or max_attempts < 1):
        raise ValueError("invalid route/effort/input/attempts; input not truncated")
    if os.environ.get("MUSIC_WEB_ROUTE", "blocked") != "gpt2":
        raise I.PolicyBlocked("gpt2 route not explicitly selected; no fallback")
    directory, producer = Path(out_dir), producer_identity(gpt2_cmd)
    identity = request_identity(model_key, effort, prompt_text, producer=producer,
                                sampling_key=job_id if sampling_key is None else sampling_key,
                                request_context=request_context)
    if expected_identity is not None and identity != expected_identity:
        raise I.ArtifactConflict("producer/config changed before execution")
    previous = I.resume(directory, job_id, identity)
    if previous is not None:
        return previous
    prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
    stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
    t0 = time.monotonic()
    meta = {"schema": I.VERSION, "job_id": job_id, "run_id": run_id, "model_key": model_key,
            "route": "gpt2", "adapter_version": ADAPTER_VERSION, "request_identity": identity,
            "producer_identity": producer, "consumer_identity": producer, "prompt_file": prompt_rel,
            "prompt_sha256": I.sha_text(prompt_text), "output_file": output_rel, "stdout_file": stdout_rel,
            "stderr_file": stderr_rel, "requested_model": MODEL_ROUTES[model_key], "requested_effort": effort,
            "effort_is_request_not_backend_proof": True, "automatic_retry": False, "raw_redacted": True,
            "cache_hit": False, "terminal_verified": False, "attempts": 0,
            "queue_stop": False, "retry_safe": False, "tool_counts": {}, "started": datetime.now().isoformat()}

    def finish(status, text="", error=None, **fields):
        mp = directory / "meta" / (job_id + ".json")
        if mp.exists():
            raise I.ArtifactConflict("completion already written; retain ticket instead of overwriting")
        I.write_text(directory / output_rel, text)
        meta.update(status=status, error=I.safe_text(error) if error else None,
                    output_chars=len(text), response_sha256=I.sha_text(text) if status == "ok" else None,
                    ended=datetime.now().isoformat(), seconds=round(time.monotonic() - t0, 3), **fields)
        I.write_json(directory / "meta" / (job_id + ".json"), meta)
        if not meta.get("cache_hit"):
            I.sample_record(directory, job_id, identity, status, meta)
        I.finalize(directory, job_id, meta)
        return meta

    with Slot("gpt2web", 1, base=HOLD_FILE.parent.parent), Slot("all", int(os.environ.get("MUSIC_MAX_CALLS", "40")), base=HOLD_FILE.parent.parent):
        previous = I.resume(directory, job_id, identity)
        if previous is not None:
            return previous
        source = I.ref_cache(directory, identity)
        I.reserve(directory, job_id, identity)
        I.write_text(directory / prompt_rel, prompt_text)
        I.write_text(directory / stdout_rel, "")
        I.write_text(directory / stderr_rel, "")
        if source is not None:
            text = (directory / source["output_file"]).read_bytes().decode("utf-8")
            return finish("ok", text, terminal_verified=True, cache_hit=True,
                          cache_source_job=source["job_id"], terminal=source["terminal"],
                          model_evidence=source.get("model_evidence"), cli_metadata=source.get("cli_metadata"))
        if not I.queue_open(HOLD_FILE):
            return finish("failed", error="provider held/inflight; inspect evidence", queue_stop=True)
        if not I.REAL_EXECUTION_APPROVED:
            return finish("failed", error="v4 real execution not approved: protocol/independent review pending",
                          failure_phase="local_gate", queue_stop=True)
        if (not producer.get("cli_sha256") or producer.get("cli_version") == "unknown"
                or not producer.get("cli_source") or producer["cli_source"].get("missing")):
            return finish("failed", error="CLI producer evidence unavailable", retry_safe=True,
                          failure_phase="local_initialization")
        I.sample_record(directory, job_id, identity, "pending")
        cwd = directory / "_empty_cwd" / job_id
        cwd.mkdir(parents=True, exist_ok=False)
        argv = _cmd_argv(gpt2_cmd or GPT2_CMD) + ["ask", "--file", str((directory / prompt_rel).resolve()),
                                                 "--model", MODEL_ROUTES[model_key], "--json"]
        ticket = I.submission_ticket(HOLD_FILE, directory, job_id, identity)
        meta["attempts"] = 1
        out_s = err_s = ""
        try:
            cp = RUN_PROCESS(argv, input=None, capture_output=True, cwd=str(cwd), env=dict(os.environ), timeout=timeout,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out_s, err_s = cp.stdout.decode("utf-8", "strict"), cp.stderr.decode("utf-8", "strict")
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            payload = I.strict_json(out_s if cp.returncode == 0 else err_s)
            if old.PROTECT_RE.search(err_s if cp.returncode == 0 else err_s + "\n" + out_s):
                raise ValueError("protection signal; terminal not accepted")
            if cp.returncode != 0 and pre_submit_payload(payload):
                result = finish("failed", error="CLI proven pre_submit failure", returncode=cp.returncode,
                                retry_safe=True, failure_phase="pre_submit", pre_submit_contract="gpt2 source-bound ProviderError/Docker schema")
                I.release_ticket(ticket)
                return result
            if cp.returncode != 0:
                raise ValueError("nonzero/unknown submission phase")
            terminal = terminal_payload(payload, MODEL_ROUTES[model_key])
            evidence = I.model_evidence(payload["metadata"], MODEL_ROUTES[model_key])
            if evidence["verdict"] != "match":
                result = finish("failed", error="backend model unverified/mismatched", returncode=0,
                                terminal_verified=True, terminal=terminal, model_evidence=evidence)
            else:
                I.assert_content_safe(payload["response"])
                result = finish("ok", payload["response"], returncode=0, terminal_verified=True, terminal=terminal,
                                model_evidence=evidence, cli_metadata=I.safe_metadata(payload["metadata"]))
            I.release_ticket(ticket)
            return result
        except Exception as exc:
            hold_error = I.classify_stop(HOLD_FILE, job_id, run_id, type(exc).__name__ + ": " + str(exc))
            if isinstance(exc, subprocess.TimeoutExpired):
                out_s = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                err_s = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            return finish("failed", error=type(exc).__name__ + ": " + str(exc), queue_stop=True,
                          returncode=None, hold_write_error=hold_error, inflight_ticket_retained=True,
                          server_cancelled="unknown")
