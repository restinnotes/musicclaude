"""gpt2 v3：严格终态、锁内 hold、引用缓存；不触碰旧实现/旧证据。"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import execution_integrity as old
import execution_integrity_v3 as I

ADAPTER_VERSION = "r3_20261009"
GPT2_CMD = os.environ.get("MUSIC_GPT2_CMD", r"D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd")
SAFECHAIN_ROOT = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", r"D:\musicclaude\gpt2agent-safechain"))
HOLD_FILE = I.SLOT_DIR / "gpt2web/queue_hold.json"
MODEL_ROUTES = {"gpt56w": "gpt-5-6-thinking", "gpt6w": "gpt-6-thinking"}
RUN_PROCESS = I.run_process
Slot = I.Slot


def producer_identity(gpt2_cmd=None):
    cmd = Path(gpt2_cmd or GPT2_CMD)
    cp = subprocess.run(["git", "-C", str(SAFECHAIN_ROOT), "rev-parse", "HEAD"],
                        capture_output=True, timeout=30,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return {"schema": I.VERSION, "route": "gpt2", "adapter_version": ADAPTER_VERSION,
            "implementations": I.implementation_identity(), "cli": str(cmd.resolve()),
            "cli_sha256": I.sha_file(cmd) if cmd.is_file() else None,
            "cli_version": cp.stdout.decode("utf-8", "strict").strip() if cp.returncode == 0 else "unknown",
            "cli_source": old.source_fingerprint(SAFECHAIN_ROOT, ("bin", "src", "tools/chatgpt_web", "vendor/gpt2agent"))}


def request_identity(model_key, effort, prompt_text, *, producer=None, sampling_key="", request_context=None):
    value = {"schema": I.VERSION, "producer": producer or producer_identity(), "model_key": model_key,
             "requested_model": MODEL_ROUTES.get(model_key), "requested_effort": effort,
             "prompt_sha256": I.sha_text(prompt_text), "sampling_key": sampling_key}
    if request_context is not None:
        value["request_context"] = request_context
    return value


def _cmd_argv(cmd):
    return ["cmd.exe", "/c", str(cmd)] if sys.platform == "win32" and str(cmd).lower().endswith((".cmd", ".bat")) else [str(cmd)]


def call_web_gpt(model_key, prompt_text, *, run_id, job_id, out_dir, effort="max", timeout=1800,
                 max_attempts=1, gpt2_cmd=None, sampling_key=None, use_cache=True, request_context=None):
    old.check_policy(model_key)
    I.valid_id(job_id)
    I.assert_content_safe(prompt_text)
    if model_key not in MODEL_ROUTES or effort != "max" or len(prompt_text) > 65536 or max_attempts < 1:
        raise ValueError("invalid route/effort/input/attempts; input not truncated")
    # 直接 adapter 也必须显式选择，不允许绕过 route/hold。
    if os.environ.get("MUSIC_WEB_ROUTE", "blocked") != "gpt2":
        raise old.PolicyBlocked("gpt2 route not explicitly selected; no fallback")
    directory, producer = Path(out_dir), producer_identity(gpt2_cmd)
    identity = request_identity(model_key, effort, prompt_text, producer=producer,
                                sampling_key=job_id if sampling_key is None else sampling_key,
                                request_context=request_context)
    previous = I.resume(directory, job_id, identity)
    if previous is not None:
        return previous
    t0 = time.monotonic()
    prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
    stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
    meta = {"schema": I.VERSION, "job_id": job_id, "run_id": run_id, "model_key": model_key,
            "route": "gpt2", "adapter_version": ADAPTER_VERSION, "request_identity": identity,
            "producer_identity": producer, "consumer_identity": producer, "prompt_file": prompt_rel,
            "prompt_sha256": I.sha_text(prompt_text), "output_file": output_rel, "stdout_file": stdout_rel,
            "stderr_file": stderr_rel, "requested_model": MODEL_ROUTES[model_key], "requested_effort": effort,
            "effort_is_request_not_backend_proof": True, "automatic_retry": False, "raw_redacted": True,
            "cache_key": I.digest(identity), "cache_hit": False, "terminal_verified": False,
            "attempts": 0, "queue_stop": False, "retry_safe": False, "tool_counts": {},
            "started": datetime.now().isoformat()}

    def finish(status, text="", error=None, **fields):
        I.write_text(directory / output_rel, text)
        meta.update(status=status, error=I.safe_text(error) if error else None,
                    output_chars=len(text), response_sha256=I.sha_text(text) if status == "ok" else None,
                    ended=datetime.now().isoformat(), seconds=round(time.monotonic() - t0, 3), **fields)
        I.write_json(directory / "meta" / (job_id + ".json"), meta)
        # 无论 use_cache，仍保留采样提交账本；该参数不能让同一采样再次提交。
        if not meta.get("cache_hit"):
            I.sample_record(directory, job_id, identity, status, meta)
        return meta

    with Slot("gpt2web", 1), Slot("all", int(os.environ.get("MUSIC_MAX_CALLS", "40"))):
        previous = I.resume(directory, job_id, identity)
        if previous is not None:
            return previous
        source = I.ref_cache(directory, identity)
        if source is not None:
            I.reserve(directory, job_id, identity)
            I.write_text(directory / prompt_rel, prompt_text)
            I.write_text(directory / stdout_rel, "cache reference; source raw remains read-only\n")
            I.write_text(directory / stderr_rel, "")
            text = (directory / source["output_file"]).read_bytes().decode("utf-8")
            return finish("ok", text, terminal_verified=True, cache_hit=True, attempts=0,
                          returncode=0, cache_source_job=source["job_id"],
                          model_evidence=source.get("model_evidence"), cli_metadata=source.get("cli_metadata"))
        I.reserve(directory, job_id, identity)
        I.write_text(directory / prompt_rel, prompt_text)
        I.write_text(directory / stdout_rel, "")
        I.write_text(directory / stderr_rel, "")
        if HOLD_FILE.exists():
            return finish("failed", error="provider queue held; inspect existing hold", queue_stop=True)
        if (not producer.get("cli_sha256") or producer.get("cli_version") == "unknown"
                or not producer.get("cli_source") or producer["cli_source"].get("missing")):
            return finish("failed", error="CLI producer evidence unavailable", retry_safe=True,
                          failure_phase="local_initialization")
        I.sample_record(directory, job_id, identity, "pending")
        cwd = directory / "_empty_cwd" / job_id
        cwd.mkdir(parents=True, exist_ok=False)
        argv = _cmd_argv(gpt2_cmd or GPT2_CMD) + ["ask", "--file", str((directory / prompt_rel).resolve()),
                                                 "--model", MODEL_ROUTES[model_key], "--json"]
        meta["attempts"] = 1
        out_s = err_s = ""
        try:
            cp = RUN_PROCESS(argv, input=None, capture_output=True, cwd=str(cwd), timeout=timeout,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out_s, err_s = cp.stdout.decode("utf-8", "strict"), cp.stderr.decode("utf-8", "strict")
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            payload = I.strict_json(out_s if cp.returncode == 0 else err_s)
            if not isinstance(payload, dict):
                raise ValueError("non-object GPT2 result")
            phase = payload.get("phase")
            protect = old.PROTECT_RE.search(err_s if cp.returncode == 0 else err_s + "\n" + out_s)
            valid = (cp.returncode == 0 and payload.get("completed") is True
                     and isinstance(payload.get("response"), str) and bool(payload["response"].strip()))
            if protect:
                I.hold(HOLD_FILE, job_id, run_id, "protection signal")
                return finish("failed", error="protection signal", queue_stop=True, returncode=cp.returncode)
            if cp.returncode != 0 and phase == "pre_submit":
                return finish("failed", error="CLI pre_submit failure", returncode=cp.returncode,
                              retry_safe=True, failure_phase=phase)
            if not valid:
                raise ValueError("incomplete/unknown GPT2 terminal")
            evidence = I.model_evidence(payload.get("metadata"), MODEL_ROUTES[model_key])
            if evidence["verdict"] != "match":
                return finish("failed", error="backend model unverified/mismatched", returncode=cp.returncode,
                              terminal_verified=True, model_evidence=evidence)
            I.assert_content_safe(payload["response"])
            return finish("ok", payload["response"], returncode=cp.returncode, terminal_verified=True,
                          model_evidence=evidence, cli_metadata=I.safe_metadata(payload.get("metadata")))
        except Exception as exc:
            # 普通异常与 timeout 同样可能已提交；先持久 hold 再释放槽位。
            I.hold(HOLD_FILE, job_id, run_id, type(exc).__name__ + ": " + str(exc))
            if isinstance(exc, subprocess.TimeoutExpired):
                out_s = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                err_s = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            return finish("failed", error=type(exc).__name__ + ": " + str(exc), queue_stop=True,
                          returncode=None, server_cancelled="unknown")
