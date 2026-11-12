"""Exact-identity GPT2 adapter.  Real execution stays disabled in v7."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import execution_integrity as old
import execution_integrity_v7 as I

ADAPTER_VERSION = "r7_20261009"
GPT2_CMD = os.environ.get("MUSIC_GPT2_CMD", r"D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd")
SAFECHAIN_ROOT = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", r"D:\musicclaude\gpt2agent-safechain"))
HOLD_FILE = I.SLOT_DIR / "gpt2web" / "queue_hold.json"
MODEL_ROUTES = {"gpt56w": "gpt-5-6-thinking", "gpt6w": "gpt-6-thinking"}
RUN_PROCESS, Slot = I.run_process, I.Slot


def producer_identity(gpt2_cmd=None):
    cmd = Path(gpt2_cmd or GPT2_CMD)
    root = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", str(SAFECHAIN_ROOT)))
    files = {}
    for path in (cmd, Path(sys.executable)):
        if path.is_file():
            files[str(path.resolve())] = I.sha_file(path)
    active_sources = I.active_provider_source_binding(root)
    argv_template = _cmd_argv(cmd) + [
        "ask", "--file", "<exact-prompt-file>", "--model", "<requested-model>", "--json"
    ]
    return {
        "schema": I.VERSION,
        "route": "gpt2",
        "adapter_version": ADAPTER_VERSION,
        "implementation_sha256": I.implementation_identity(),
        "cli_path": str(cmd.resolve()),
        "cli_sha256": I.sha_file(cmd) if cmd.is_file() else None,
        "cli_version": "file-and-source-fingerprint-only",
        "runtime_files_sha256": files,
        "safechain_root": str(root.resolve()),
        "active_provider_sources": active_sources,
        "environment": I.environment_identity(os.environ),
        "execution_argv_template": argv_template,
        "actual_argv_bound_in_sealed_completion_meta": True,
        "coverage": {
            "active_chain_sources_complete": active_sources["complete"],
            "remote_input_normalization_verified": False,
            "private_global_config_frozen": False,
            "container_image_and_external_service_frozen": False,
            "real_execution_approved": False,
        },
    }


def request_identity(model_key, effort, prompt_text, *, producer=None, sampling_key="", request_context=None):
    I.assert_content_safe(prompt_text)
    if not isinstance(sampling_key, str):
        raise ValueError("sampling_key must be text")
    I.assert_content_safe(sampling_key)
    identity = {
        "schema": I.VERSION,
        "producer": producer or producer_identity(),
        "model_key": model_key,
        "requested_model": MODEL_ROUTES.get(model_key),
        "requested_effort": effort,
        "prompt_sha256": I.sha_text(prompt_text),
        "sampling_key": sampling_key,
    }
    if request_context is not None:
        identity["request_context"] = request_context
    return identity


def _cmd_argv(cmd):
    cmd = str(cmd)
    if sys.platform == "win32" and cmd.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", cmd]
    return [cmd]


def terminal_payload(payload, requested, requested_effort="max"):
    if (not isinstance(payload, dict) or payload.get("completed") is not True
            or not isinstance(payload.get("response"), str) or not payload["response"].strip()):
        raise ValueError("incomplete/unknown GPT2 terminal")
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError("missing headless provider metadata")
    validation = metadata.get("prepared_response_validation")
    if (metadata.get("headless") is not True or metadata.get("provider_interface") is not True
            or metadata.get("no_auto_retry") is not True or metadata.get("model") != requested
            or metadata.get("thinking_effort") != requested_effort
            or not isinstance(metadata.get("thinking_effort"), str)
            or metadata.get("response_sha256") != I.sha_text(payload["response"])
            or not isinstance(validation, dict)
            or validation.get("successful_assistant_terminal_observed") is not True
            or validation.get("unsupported_work_continuation_observed") is not False):
        raise ValueError("missing/conflicting GPT2 provider terminal, model, effort, or response binding")
    return {
        "schema": "gpt2_headless_provider_v7",
        "terminal": "successful_assistant_terminal_observed",
        "unsupported_work_continuation_observed": False,
        "thinking_effort_binding": "returned metadata exactly matches requested effort; not remote attestation",
    }


def pre_submit_payload(payload, expected_identity=None):
    """Validate a structured no-submit error tied to exact source and request.

    A free-form digest is never accepted as proof.  Every named source file,
    contract field, request digest, and producer digest must match this run.
    """
    if (not isinstance(payload, dict) or payload.get("completed") is not False
            or payload.get("automatic_retry") is not False
            or payload.get("phase") != "pre_submit"
            or payload.get("error_code") != "headless_runner_or_evidence_failed"
            or ("model_request_sent" in payload and payload.get("model_request_sent") is not False)):
        return False
    proof = payload.get("pre_submit_proof")
    if not isinstance(proof, dict):
        return False
    identity = expected_identity
    if identity is None:
        try:
            active = I.active_provider_source_binding(SAFECHAIN_ROOT)
            if active.get("complete") is not True:
                return False
            # Without the caller identity this helper can only validate the
            # current source contract's structure, not authorize a retry.
            source_files = active["files"]
            return (
                proof.get("schema") == I.PRE_SUBMIT_PROOF_SCHEMA
                and proof.get("contract") == I.PRE_SUBMIT_CONTRACT
                and proof.get("provider_error_type") == "ProviderError"
                and proof.get("phase") == "pre_submit"
                and proof.get("retryable") is True
                and proof.get("ambiguous") is False
                and proof.get("submit_callback_reached") is False
                and proof.get("model_request_sent") is False
                and proof.get("automatic_retry") is False
                and proof.get("source_files") == source_files
                and I.SHA256_RE.fullmatch(str(proof.get("request_identity_sha256", ""))) is not None
                and I.SHA256_RE.fullmatch(str(proof.get("producer_identity_sha256", ""))) is not None
            )
        except (OSError, TypeError, ValueError):
            return False
    candidate = {
        "status": "failed", "failure_phase": "pre_submit", "retry_safe": True,
        "queue_stop": False, "terminal_verified": False,
        "submission_state": "proven_not_submitted", "pre_submit_proof": proof,
    }
    return I.verify_pre_submit_proof(candidate, identity)


def _safe_provider_result(meta, ticket=None, hold_error=None):
    result = dict(meta)
    if ticket is not None:
        result["inflight_ticket_retained"] = True
    if hold_error is not None:
        result["hold_write_error"] = hold_error
    return result


def call_web_gpt(model_key, prompt_text, *, run_id, job_id, out_dir, effort="max", timeout=1800,
                 max_attempts=1, gpt2_cmd=None, sampling_key=None, use_cache=True,
                 request_context=None, expected_identity=None):
    old.check_policy(model_key)
    I.valid_id(job_id)
    I.assert_content_safe(prompt_text)
    if (model_key not in MODEL_ROUTES or effort != "max" or len(prompt_text) > 65536
            or type(max_attempts) is not int or max_attempts < 1
            or type(use_cache) is not bool):
        raise ValueError("invalid route/effort/input/attempts/cache flag; input not truncated")
    if os.environ.get("MUSIC_WEB_ROUTE", "blocked") != "gpt2":
        raise I.PolicyBlocked("gpt2 route not explicitly selected; no fallback")
    directory = Path(out_dir)
    producer = producer_identity(gpt2_cmd)
    identity = request_identity(
        model_key, effort, prompt_text, producer=producer,
        sampling_key=job_id if sampling_key is None else sampling_key,
        request_context=request_context,
    )
    if expected_identity is not None and identity != expected_identity:
        raise I.ArtifactConflict("producer/config changed before execution")
    previous = I.resume(directory, job_id, identity)
    if previous is not None:
        return dict(previous, cache_requested=use_cache, cache_hit=False)

    prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
    stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
    started = time.monotonic()
    meta = {
        "schema": I.VERSION, "job_id": job_id, "run_id": I.safe_text(run_id),
        "model_key": model_key, "route": "gpt2", "adapter_version": ADAPTER_VERSION,
        "request_identity": identity, "request_identity_sha256": I.identity_digest(identity),
        "producer_identity": producer, "consumer_identity": producer,
        "prompt_file": prompt_rel, "prompt_sha256": I.sha_text(prompt_text),
        "output_file": output_rel, "stdout_file": stdout_rel, "stderr_file": stderr_rel,
        "requested_model": MODEL_ROUTES[model_key], "requested_effort": effort,
        "effort_is_request_and_return_binding_not_remote_attestation": True,
        "automatic_retry": False, "raw_redacted": True, "cache_hit": False,
        "cache_requested": use_cache, "terminal_verified": False,
        "attempts": 0, "provider_submissions": 0,
        "queue_stop": False, "retry_safe": False, "tool_counts": {},
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }

    def finish(status, text="", error=None, *, write_cache=False, cache_state=None, **fields):
        if (directory / "meta" / (job_id + ".json")).exists():
            raise I.ArtifactConflict("completion already written; retain evidence instead of overwriting")
        if status == "ok":
            I.assert_content_safe(text)
        I.write_text(I.run_artifact_path(directory, output_rel), text)
        meta.update(
            status=status, error=I.safe_text(error) if error else None,
            output_chars=len(text), response_sha256=I.sha_text(text) if status == "ok" else None,
            ended_utc=datetime.now(timezone.utc).isoformat(),
            seconds=round(time.monotonic() - started, 3), **fields,
        )
        I.write_json(I.run_artifact_path(directory, "meta/" + job_id + ".json"), meta)
        I.finalize(directory, job_id, meta)
        if write_cache:
            I.sample_record(directory, job_id, identity, cache_state or status, meta)
        return dict(meta)

    with Slot("gpt2web", 1, base=HOLD_FILE.parent.parent), Slot(
            "all", int(os.environ.get("MUSIC_MAX_CALLS", "40")), base=HOLD_FILE.parent.parent):
        previous = I.resume(directory, job_id, identity)
        if previous is not None:
            return dict(previous, cache_requested=use_cache, cache_hit=False)
        source = I.ref_cache(directory, identity)
        if source is not None and not use_cache:
            # Exact cache source is returned read-only.  No alias or redirected
            # cache entry is created when a caller requests cache bypass.
            return dict(source, cache_hit=True, cache_requested=False, cache_bypassed=True,
                        consumer_job_id=job_id, consumer_identity=producer)

        I.reserve(directory, job_id, identity)
        I.write_text(I.run_artifact_path(directory, prompt_rel), prompt_text)
        I.write_text(I.run_artifact_path(directory, stdout_rel), "")
        I.write_text(I.run_artifact_path(directory, stderr_rel), "")
        if source is not None:
            text = I._inside(directory, source["output_file"]).read_bytes().decode("utf-8")
            return finish(
                "ok", text, cache_hit=True, cache_source_job=source["job_id"],
                terminal_verified=True, terminal=source["terminal"],
                model_evidence=source.get("model_evidence"),
                cli_metadata=source.get("cli_metadata"), cache_requested=True,
            )
        if not I.queue_open(HOLD_FILE):
            return finish("failed", error="provider held/inflight; inspect evidence",
                          queue_stop=True, failure_phase="queue_gate", submission_state="not_started")
        if not I.REAL_EXECUTION_APPROVED:
            return finish("failed", error="v7 real execution gate is closed",
                          queue_stop=True, failure_phase="local_gate", submission_state="not_started")

        # Recompute immediately before crossing the boundary.  This binds the
        # invocation to the same CLI/source/environment identity as the request.
        current_producer = producer_identity(gpt2_cmd)
        if current_producer != producer:
            return finish("failed", error="producer/config changed before submission",
                          queue_stop=True, failure_phase="local_identity", submission_state="not_started")
        if (not producer.get("cli_sha256") or producer.get("cli_version") == "unknown"
                or producer.get("active_provider_sources", {}).get("complete") is not True):
            return finish("failed", error="active producer evidence unavailable/incomplete",
                          queue_stop=True, failure_phase="local_initialization", submission_state="not_started")

        cwd = directory / "_empty_cwd" / job_id
        cwd.mkdir(parents=True, exist_ok=False)
        argv = _cmd_argv(gpt2_cmd or GPT2_CMD) + [
            "ask", "--file", str((directory / prompt_rel).resolve()),
            "--model", MODEL_ROUTES[model_key], "--json",
        ]
        meta["execution_argv"] = argv
        meta["execution_argv_sha256"] = I.digest(argv)
        meta["execution_cwd"] = str(cwd.resolve())
        ticket = I.submission_ticket(HOLD_FILE, directory, job_id, identity)
        meta["attempts"] = 1
        meta["provider_submissions"] = 1
        meta["submission_state"] = "unknown_after_ticket"
        out_s = err_s = ""
        try:
            cp = RUN_PROCESS(
                argv, input=None, capture_output=True, cwd=str(cwd), timeout=timeout,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            out_s = cp.stdout.decode("utf-8", "strict")
            err_s = cp.stderr.decode("utf-8", "strict")
            I.write_text(I.run_artifact_path(directory, stdout_rel), I.safe_records(out_s))
            I.write_text(I.run_artifact_path(directory, stderr_rel), I.safe_records(err_s))
            if old.PROTECT_RE.search(err_s):
                raise ValueError("protection signal; terminal not accepted")
            response_stream = out_s if cp.returncode == 0 else err_s
            payload = I.strict_json(response_stream)
            if cp.returncode != 0 and pre_submit_payload(payload, identity):
                proof = payload["pre_submit_proof"]
                meta["provider_submissions"] = 0
                result = finish(
                    "failed", error="source-bound provider proof: no model submission",
                    retry_safe=True, failure_phase="pre_submit", pre_submit_proof=proof,
                    submission_state="proven_not_submitted", terminal_verified=False,
                    returncode=cp.returncode, retry_contract=I.PRE_SUBMIT_CONTRACT,
                )
                I.release_ticket(ticket)
                return result
            if cp.returncode != 0:
                raise ValueError("nonzero/unknown submission phase")
            terminal = terminal_payload(payload, MODEL_ROUTES[model_key], effort)
            evidence = I.model_evidence(payload["metadata"], MODEL_ROUTES[model_key])
            cli_metadata = I.safe_metadata(payload["metadata"])
            if evidence["verdict"] != "match":
                result = finish(
                    "failed", error="backend model unverified/mismatched", returncode=0,
                    terminal_verified=True, terminal=terminal, model_evidence=evidence,
                    cli_metadata=cli_metadata, submission_state="terminal_observed",
                    write_cache=True, cache_state="failed_terminal",
                )
            else:
                I.assert_content_safe(payload["response"])
                result = finish(
                    "ok", payload["response"], returncode=0, terminal_verified=True,
                    terminal=terminal, model_evidence=evidence, cli_metadata=cli_metadata,
                    submission_state="terminal_observed", write_cache=True, cache_state="ok",
                )
            I.release_ticket(ticket)
            return result
        except Exception as exc:
            hold_error = I.classify_stop(HOLD_FILE, job_id, run_id, type(exc).__name__ + ": " + str(exc))
            if isinstance(exc, subprocess.TimeoutExpired):
                out_s = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                err_s = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            try:
                I.write_text(I.run_artifact_path(directory, stdout_rel), I.safe_records(out_s))
                I.write_text(I.run_artifact_path(directory, stderr_rel), I.safe_records(err_s))
            except OSError:
                pass
            meta_path = directory / "meta" / (job_id + ".json")
            if meta_path.exists():
                prior = I._read_json_object(meta_path, "existing completion meta")
                if ticket.exists():
                    I.classify_stop(HOLD_FILE, job_id, run_id,
                                    "v7 ticket retained after completion write failure")
                if prior.get("status") == "ok" or prior.get("terminal_verified") is True:
                    raise I.ArtifactConflict(
                        "terminal evidence exists but post-terminal commit/release failed; ticket retained"
                    ) from exc
                result = _safe_provider_result(prior, ticket=ticket, hold_error=hold_error)
                result.update(queue_stop=True, server_cancelled="unknown")
                return result
            try:
                result = finish(
                    "failed", error=type(exc).__name__ + ": " + str(exc), queue_stop=True,
                    returncode=None, failure_phase="post_submit_ambiguous",
                    submission_state="unknown_after_ticket", inflight_ticket_retained=True,
                    server_cancelled="unknown", hold_write_error=hold_error,
                )
                return result
            except Exception as write_exc:
                # Ticket remains on disk; failure to write hold or final evidence
                # can never reopen the provider queue.
                return {
                    "schema": I.VERSION, "job_id": job_id, "status": "failed",
                    "error": I.safe_text(type(write_exc).__name__ + ": " + str(write_exc)),
                    "queue_stop": True, "attempts": 1, "provider_submissions": 1,
                    "inflight_ticket_retained": True, "hold_write_error": hold_error,
                    "server_cancelled": "unknown",
                }
