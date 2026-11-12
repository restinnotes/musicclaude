"""Single-attempt runner using v8 identities, seals, and fail-closed holds."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import runner as legacy
import execution_integrity as old
import execution_integrity_v8 as I
import gpt2_adapter_v8 as A

RUN_PROCESS, Slot, SLOT_DIR = I.run_process, I.Slot, I.SLOT_DIR
ALLOWED = set(legacy.AGY_KEYS) | {"luna", "luna_noweb", "gpt56w", "gpt6w"}
fill = legacy.fill


def check_policy(model):
    old.check_policy(model)
    if model not in ALLOWED:
        raise I.PolicyBlocked("v8 supports only explicitly allowed routes")


def _config(model):
    if model in legacy.AGY_KEYS:
        config = json.loads(json.dumps(legacy.GEMINI_PROVIDER_CFG))
        if not model.endswith("_web"):
            config["permission"] = "deny"
        return config
    return None


def build_task(model):
    """Build the supported argv without legacy env-copy initialization.

    The legacy initializer copies the entire process environment, which would
    read credential values.  v8 uses only allowlisted path inputs and leaves
    the child environment inherited by the OS (env=None) while the gate stays
    closed.
    """
    if model in legacy.CODEX_KEYS:
        codex_js = os.path.join(os.environ.get("APPDATA", ""),
                                r"npm\node_modules\@openai\codex\bin\codex.js")
        offline = model.endswith("_noweb") or model in ("sol61_cx", "sol61_cxh")
        search = "disabled" if offline else "live"
        effort = legacy.CODEX_EFFORT.get(model, "high")
        argv = [legacy.NODE_EXE, codex_js, "exec", "--skip-git-repo-check", "--json",
                "-m", legacy.MODEL_NAMES[model], "-c", f'model_reasoning_effort="{effort}"',
                "-c", f'web_search="{search}"']
        if offline:
            for feature in ("shell_tool", "unified_exec", "apps", "plugins", "browser_use", "computer_use",
                            "in_app_browser", "multi_agent", "image_generation"):
                argv += ["--disable", feature]
            argv += ["-c", "mcp_servers.node_repl.enabled=false"]
        argv.append("-")
        return argv, "raw", legacy.MODEL_NAMES[model]
    if model in legacy.AGY_KEYS:
        opencode = shutil.which("opencode", path=os.environ.get("PATH") or os.environ.get("Path"))
        if not opencode:
            raise FileNotFoundError("opencode not found using the bound process PATH")
        model_name = legacy.MODEL_NAMES[model]
        return [opencode, "run", "--standalone", "--format", "json",
                "--model", "antigravity-tools/" + model_name], "raw", model_name
    raise I.PolicyBlocked("route has no v8 safe argv builder")


def execution_plan(job):
    model = job["model_key"]
    argv, mode, name = build_task(model)
    argv = list(argv)
    provider = "gemini" if model in legacy.AGY_KEYS else "codex"
    extra = job.get("extra") or {}
    if not isinstance(extra, dict):
        raise ValueError("execution extra must be an object")
    if extra.get("images") and provider == "codex":
        argv = argv[:-1] + [x for image in extra["images"] for x in ("-i", str(image))] + argv[-1:]
    if model == "luna":
        argv = argv[:-1] + ["-s", "workspace-write", "-c", "sandbox_workspace_write.network_access=true"] + argv[-1:]
    config = _config(model)
    # An inherited inline configuration is private/unfrozen and is rejected by
    # environment_identity without reading its value.  The generated config is
    # still identity-bound; no live CLI is permitted under this gate.
    if provider == "gemini" and "OPENCODE_CONFIG_CONTENT" in os.environ:
        raise I.PolicyBlocked("preexisting inline OpenCode configuration blocks v8 identity")
    files = {str(Path(arg).resolve()): I.sha_file(arg) for arg in argv if Path(arg).is_file()}
    for arg in argv:
        path = Path(arg)
        if path.name == "codex.js" and path.is_file():
            for binary in path.parent.parent.rglob("codex.exe"):
                files[str(binary.resolve())] = I.sha_file(binary)
    if not files:
        raise ValueError("CLI implementation fingerprint unavailable")
    for arg in argv:
        I.assert_content_safe(str(arg))
    if I.safe_metadata(extra) != extra:
        raise ValueError("private-looking execution extra rejected")
    producer = {
        "schema": I.VERSION, "route": provider, "model_name": name,
        "implementations": I.implementation_identity(), "argv": argv,
        "stdin_mode": mode, "cli_files_sha256": files,
        "inline_configuration_sha256": I.digest(config),
        "environment": I.environment_identity(os.environ),
        "coverage": {
            "final_argv_and_known_cli_files_bound": True,
            "inline_configuration_bound": config is not None,
            "inline_configuration_applied_to_child": False,
            "private_global_configuration_frozen": False,
            "external_service_frozen": False,
            "real_execution_approved": False,
        },
    }
    return argv, None, producer


def request_identity_for(job):
    check_policy(job["model_key"])
    I.valid_id(job["job_id"])
    I.assert_content_safe(job["prompt"])
    sampling_key = job.get("sampling_key", job["job_id"])
    if not isinstance(sampling_key, str) or not sampling_key:
        raise ValueError("sampling_key must be nonempty text")
    I.assert_content_safe(sampling_key)
    if job["model_key"] in A.MODEL_ROUTES:
        producer = A.producer_identity()
        context = old.job_identity(job, producer)
        return A.request_identity(job["model_key"], "max", job["prompt"], producer=producer,
                                  sampling_key=sampling_key, request_context=context)
    _, _, producer = execution_plan(job)
    identity = old.job_identity(job, producer)
    identity["schema"] = I.VERSION
    identity["sampling_key"] = sampling_key
    extra = job.get("extra") or {}
    if I.safe_metadata(extra) != extra:
        raise ValueError("private-looking execution extra rejected")
    identity["extra_sha256"] = I.digest(extra)
    return identity


def _artifact(directory, relative):
    return I._inside(directory, relative)


def run_job(run_dir, job, timeout=3600):
    model, job_id = job["model_key"], job["job_id"]
    check_policy(model)
    I.valid_id(job_id)
    I.assert_content_safe(job["prompt"])
    if type(job.get("max_attempts", 1)) is not int or job.get("max_attempts", 1) != 1:
        raise ValueError("runner executes one immutable attempt; retries belong to experiment_calls_v8")
    identity = request_identity_for(job)
    if model in A.MODEL_ROUTES:
        return A.call_web_gpt(
            model, job["prompt"], run_id=Path(run_dir).name, job_id=job_id,
            out_dir=run_dir, timeout=timeout, max_attempts=1,
            sampling_key=job.get("sampling_key", job_id),
            use_cache=job.get("use_cache", True),
            request_context=identity.get("request_context"), expected_identity=identity,
        )

    directory = Path(run_dir)
    previous = I.resume(directory, job_id, identity)
    if previous is not None:
        return dict(previous, cache_requested=job.get("use_cache", True), cache_hit=False)
    provider = "gemini" if model in legacy.AGY_KEYS else "codex"
    hold_file = SLOT_DIR / provider / "queue_hold.json"
    use_cache = job.get("use_cache", True)
    if type(use_cache) is not bool:
        raise ValueError("use_cache must be bool")
    with Slot(provider, 1, base=SLOT_DIR), Slot(
            "all", int(os.environ.get("MUSIC_MAX_CALLS", "40")), base=SLOT_DIR):
        previous = I.resume(directory, job_id, identity)
        if previous is not None:
            return dict(previous, cache_requested=use_cache, cache_hit=False)
        source = I.ref_cache(directory, identity)
        if source is not None and not use_cache:
            return dict(source, cache_hit=True, cache_requested=False, cache_bypassed=True,
                        consumer_job_id=job_id, consumer_identity=identity["producer"])

        I.reserve(directory, job_id, identity)
        prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
        stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
        I.write_text(_artifact(directory, prompt_rel), job["prompt"])
        I.write_text(_artifact(directory, stdout_rel), "")
        I.write_text(_artifact(directory, stderr_rel), "")
        started = time.monotonic()
        meta = {
            "schema": I.VERSION, "job_id": job_id, "run_id": directory.name,
            "model_key": model, "model_name": identity["producer"].get("model_name"),
            "request_identity": identity, "request_identity_sha256": I.identity_digest(identity),
            "producer_identity": identity["producer"], "consumer_identity": identity["producer"],
            "prompt_file": prompt_rel, "output_file": output_rel,
            "stdout_file": stdout_rel, "stderr_file": stderr_rel,
            "prompt_sha256": I.sha_text(job["prompt"]), "attempts": 0,
            "provider_submissions": 0, "branch": job.get("branch", ""),
            "prompt_version": job.get("prompt_version", ""),
            "prompt_template": job.get("prompt_template"), "work_key": job.get("work_key", ""),
            "sample": job.get("sample", 0), "raw_redacted": True,
            "automatic_retry": False, "terminal_verified": False,
            "queue_stop": False, "retry_safe": False, "cache_hit": False,
            "cache_requested": use_cache, "started_utc": datetime.now(timezone.utc).isoformat(),
            "tool_counts": {},
        }

        def finish(status, text="", error=None, *, write_cache=False, cache_state=None, **fields):
            if (directory / "meta" / (job_id + ".json")).exists():
                raise I.ArtifactConflict("completion already written; retain evidence instead of overwriting")
            if status == "ok":
                I.assert_content_safe(text)
            I.write_text(_artifact(directory, output_rel), text)
            meta.update(
                status=status, error=I.safe_text(error) if error else None,
                output_chars=len(text), response_sha256=I.sha_text(text) if status == "ok" else None,
                seconds=round(time.monotonic() - started, 3),
                ended_utc=datetime.now(timezone.utc).isoformat(), **fields,
            )
            I.write_json(_artifact(directory, "meta/%s.json" % job_id), meta)
            I.finalize(directory, job_id, meta)
            if write_cache:
                I.sample_record(directory, job_id, identity, cache_state or status, meta)
            return dict(meta)

        if source is not None:
            text = _artifact(directory, source["output_file"]).read_bytes().decode("utf-8")
            return finish(
                "ok", text, terminal_verified=True, cache_hit=True,
                cache_source_job=source["job_id"], exit_code=0,
                terminal=source["terminal"], cache_requested=True,
            )
        if not I.queue_open(hold_file):
            return finish("failed", error="provider held/inflight; inspect evidence", queue_stop=True,
                          failure_phase="queue_gate", submission_state="not_started")
        if not I.REAL_EXECUTION_APPROVED:
            return finish("failed", error="v8 real execution gate is closed", queue_stop=True,
                          failure_phase="local_gate", submission_state="not_started")

        argv, env, actual_producer = execution_plan(job)
        if actual_producer != identity["producer"]:
            return finish("failed", error="CLI/config/environment changed before submission", queue_stop=True,
                          failure_phase="local_identity", submission_state="not_started")
        cwd = directory / "_empty_cwd" / job_id
        cwd.mkdir(parents=True, exist_ok=False)
        ticket = I.submission_ticket(hold_file, directory, job_id, identity)
        meta["attempts"] = 1
        meta["provider_submissions"] = 1
        meta["submission_state"] = "unknown_after_ticket"
        out_s = err_s = ""
        try:
            cp = RUN_PROCESS(
                argv,
                input=job["prompt"].encode("utf-8") if identity["producer"].get("stdin_mode") == "raw" else None,
                capture_output=True, cwd=str(cwd), timeout=timeout,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            out_s, err_s = cp.stdout.decode("utf-8", "strict"), cp.stderr.decode("utf-8", "strict")
            I.write_text(_artifact(directory, stdout_rel), I.safe_records(out_s))
            I.write_text(_artifact(directory, stderr_rel), I.safe_records(err_s))
            if cp.returncode != 0 or old.PROTECT_RE.search(err_s):
                raise ValueError("nonzero exit/protection stderr; terminal unknown")
            text, counts, terminal = I.parse_opencode(out_s) if provider == "gemini" else I.parse_codex(out_s)
            used = [key for key in counts if key not in ("reasoning", "todo_list")]
            forbid = (bool(job.get("forbid_tools")) or model == "luna_noweb"
                      or (provider == "gemini" and not model.endswith("_web")))
            meta["provider_submissions"] = 1
            meta["submission_state"] = "terminal_observed"
            if forbid and used:
                result = finish(
                    "failed", error="forbidden tools used: " + ",".join(used),
                    terminal_verified=True, exit_code=0, tool_counts=counts, terminal=terminal,
                    write_cache=True, cache_state="failed_terminal",
                )
            else:
                I.assert_content_safe(text)
                result = finish(
                    "ok", text, terminal_verified=True, exit_code=0,
                    tool_counts=counts, terminal=terminal, write_cache=True, cache_state="ok",
                )
            I.release_ticket(ticket)
            return result
        except Exception as exc:
            hold_error = I.classify_stop(hold_file, job_id, directory.name,
                                         type(exc).__name__ + ": " + str(exc))
            if isinstance(exc, subprocess.TimeoutExpired):
                out_s = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                err_s = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            try:
                I.write_text(_artifact(directory, stdout_rel), I.safe_records(out_s))
                I.write_text(_artifact(directory, stderr_rel), I.safe_records(err_s))
            except OSError:
                pass
            meta_path = directory / "meta" / (job_id + ".json")
            if meta_path.exists():
                # The terminal evidence may already be immutable; report a
                # failed/held call to the caller without rewriting that record.
                return {
                    "schema": I.VERSION, "job_id": job_id, "status": "failed",
                    "error": I.safe_text(type(exc).__name__ + ": " + str(exc)),
                    "queue_stop": True, "attempts": 1, "provider_submissions": 1,
                    "inflight_ticket_retained": True, "hold_write_error": hold_error,
                    "server_cancelled": "unknown",
                }
            try:
                return finish(
                    "failed", error=type(exc).__name__ + ": " + str(exc), queue_stop=True,
                    exit_code=None, failure_phase="post_submit_ambiguous",
                    submission_state="unknown_after_ticket", inflight_ticket_retained=True,
                    server_cancelled="unknown", hold_write_error=hold_error,
                )
            except Exception as write_exc:
                return {
                    "schema": I.VERSION, "job_id": job_id, "status": "failed",
                    "error": I.safe_text(type(write_exc).__name__ + ": " + str(write_exc)),
                    "queue_stop": True, "attempts": 1, "provider_submissions": 1,
                    "inflight_ticket_retained": True, "hold_write_error": hold_error,
                    "server_cancelled": "unknown",
                }


def run_jobs(run_dir, jobs, max_workers=1, timeout=3600):
    if len({job["job_id"] for job in jobs}) != len(jobs):
        raise ValueError("duplicate job_id")
    for job in jobs:
        check_policy(job["model_key"])
    results, stopped = [], set()
    for job in jobs:
        provider = ("gpt2" if job["model_key"] in A.MODEL_ROUTES
                    else "gemini" if job["model_key"] in legacy.AGY_KEYS else "codex")
        if provider in stopped:
            results.append({"job_id": job["job_id"], "status": "skipped_queue_stop",
                            "attempts": 0, "provider_submissions": 0, "queue_stop": True})
            continue
        meta = run_job(run_dir, job, timeout)
        results.append(meta)
        if meta.get("queue_stop"):
            stopped.add(provider)
    return results
