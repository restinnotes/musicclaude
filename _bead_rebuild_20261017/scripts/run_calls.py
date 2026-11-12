#!/usr/bin/env python3
"""Isolated single-attempt model calls. Default is offline validation; --execute submits."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time

SCRIPT_DIR = Path(__file__).resolve().parent
EXPERIMENT = SCRIPT_DIR.parent
PROJECT = EXPERIMENT.parent
GPT_ROOT = PROJECT / "gpt2agent-safechain"
GPT_PYTHON = GPT_ROOT / ".venv-local/Scripts/python.exe"
GPT_CLI = GPT_ROOT / "tools/chatgpt_web/gpt2_cli.py"
OPENCODE = Path(r"C:\Users\zuoyi\AppData\Local\Programs\@openchamberelectron\resources\opencode-cli\opencode.exe")
OPENCODE_CONFIG = Path.home() / ".config/opencode/opencode.json"
GPT_MODELS = {"gpt-6-thinking", "gpt-5-6-thinking"}
FLASH = "antigravity-tools/gemini-3.8-flash-high"
MUSE = "opencode2api/muse-spark-1.3-contributor-free#xhigh"
JOB_KEYS = {"job_id", "channel", "model", "prompt_file", "prompt_sha256", "attachments",
            "timeout_seconds", "min_response_chars", "enabled", "labels"}
PRINT_LOCK = threading.Lock()
STOP = threading.Event()
SECRET_KEY = re.compile(r"authorization|cookie|password|secret|api[_-]?key|access[_-]?token|refresh[_-]?token|session_handle", re.I)


class Invalid(ValueError):
    pass


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def safe(value):
    """Redact credential fields in derived metadata; raw child files stay byte exact."""
    if isinstance(value, dict):
        return {k: "[REDACTED]" if SECRET_KEY.search(k) else safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [safe(v) for v in value]
    return value


def write_json(path, data):
    with Path(path).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(safe(data), f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def write_bytes(path, data):
    with Path(path).open("xb") as f:
        f.write(data)


def emit(data):
    with PRINT_LOCK:
        print(json.dumps(data, ensure_ascii=False), flush=True)


def resolve_input(base, value):
    if not isinstance(value, str) or not value:
        raise Invalid("input_path_required")
    p = (base / value).resolve(strict=True)
    if not p.is_file():
        raise Invalid("input_not_a_file")
    return p


def validate_job(job, base):
    if not isinstance(job, dict) or set(job) - JOB_KEYS:
        raise Invalid("unknown_job_fields_or_non_object")
    jid = job.get("job_id", "")
    if not isinstance(jid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", jid):
        raise Invalid("invalid_job_id")
    if jid.endswith(".") or jid.split(".")[0].upper() in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1,10)], *[f"LPT{i}" for i in range(1,10)]}:
        raise Invalid("reserved_job_id")
    channel, model = job.get("channel"), job.get("model")
    if not ((channel == "gpt2" and model in GPT_MODELS) or
            (channel == "opencode" and model in (FLASH, MUSE))):
        raise Invalid("unsupported_explicit_channel_or_model")
    timeout = job.get("timeout_seconds", 7200)
    minimum = job.get("min_response_chars", 1)
    if type(timeout) not in (int, float) or not 1 <= timeout <= 86400:
        raise Invalid("timeout_seconds_must_be_1_to_86400")
    if type(minimum) is not int or minimum < 1:
        raise Invalid("min_response_chars_must_be_positive_integer")
    if "enabled" in job and type(job["enabled"]) is not bool:
        raise Invalid("enabled_must_be_boolean")
    source = resolve_input(base, job.get("prompt_file"))
    raw = source.read_bytes()
    text = raw.decode("utf-8-sig")
    if not text.strip() or "\x00" in text:
        raise Invalid("empty_or_NUL_prompt")
    digest = sha(raw)
    if job.get("prompt_sha256") is not None and job["prompt_sha256"] != digest:
        raise Invalid("prompt_sha256_mismatch")
    # Exact normalization performed by the existing safechain provider; keep both hashes.
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip()
    native_limit = 1048576 if os.environ.get("MUSIC_RESEARCH_LARGE_NATIVE_BODY") == "1" else 65536
    if channel == "gpt2":
        if len(normalized) > 65536:
            raise Invalid("gpt2_prompt_exceeds_65536_characters_use_explicit_attachment_job")
        # A lower bound only: the actual request adds metadata and must pass its own byte guard.
        if len(json.dumps(normalized, ensure_ascii=False).encode("utf-8")) >= native_limit:
            raise Invalid("gpt2_prompt_alone_exceeds_native_JSON_byte_limit")
    attachments = job.get("attachments", [])
    if not isinstance(attachments, list) or len(attachments) > 10:
        raise Invalid("attachments_must_be_list_max_10")
    if channel == "opencode" and attachments:
        raise Invalid("opencode_requires_frozen_complete_inline_prompt_no_implicit_attachment_conversion")
    files, names = [], set()
    for item in attachments:
        if isinstance(item, str):
            spec = {"path": item}
        elif isinstance(item, dict) and set(item) <= {"path", "sha256"}:
            spec = item
        else:
            raise Invalid("attachment_requires_path_and_optional_sha256")
        p = resolve_input(base, spec.get("path"))
        size = p.stat().st_size
        if not 0 < size <= 100 * 1024 * 1024 or p.name.casefold() in names:
            raise Invalid("attachment_size_or_duplicate_basename")
        names.add(p.name.casefold())
        h = file_sha(p)
        if spec.get("sha256") is not None and spec["sha256"] != h:
            raise Invalid("attachment_sha256_mismatch")
        files.append({"source": str(p), "name": p.name, "size": size, "sha256": h})
    if sum(x["size"] for x in files) > 200 * 1024 * 1024:
        raise Invalid("attachment_total_exceeds_200_MiB")
    return {"job": job, "source": source, "raw": raw, "attachments": files,
            "prompt_sha256": digest, "prompt_bytes": len(raw), "prompt_characters": len(text),
            "normalized_prompt_sha256": sha(normalized.encode("utf-8")),
            "normalized_prompt_bytes": len(normalized.encode("utf-8")),
            "normalized_prompt_characters": len(normalized), "native_body_limit_bytes": native_limit}


def build_command(prepared, directory):
    job = prepared["job"]
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    policy = {"automatic_retry": False, "automatic_fallback": False, "new_session": True}
    if job["channel"] == "gpt2":
        if not GPT_PYTHON.is_file() or not GPT_CLI.is_file():
            raise Invalid("gpt2_interpreter_or_cli_missing")
        # Same executable and entry point as bin/gpt2.cmd, without cmd.exe interpolation.
        argv = [str(GPT_PYTHON), str(GPT_CLI), "ask", "--file", str(directory / "prompt.txt"),
                "--model", job["model"], "--initializer-pss-limit-mib", "1536", "--json"]
        for item in prepared["attachments"]:
            argv += ["--attach", str(directory / "attachments" / item["name"])]
        policy.update(thinking_effort="max", temporary=True, unpersonalized=True,
                      initializer_pss_limit_mib=1536, native_body_limit_bytes=prepared["native_body_limit_bytes"],
                      prompt_normalization="single_leading_BOM_removed_CRLF_or_CR_to_LF_and_trim_end",
                      cli_sha256=file_sha(GPT_CLI))
        return argv, env, policy
    if not OPENCODE.is_file() or not OPENCODE_CONFIG.is_file():
        raise Invalid("opencode_executable_or_existing_configuration_missing")
    provider, model = job["model"].split("/", 1)
    current = json.loads(OPENCODE_CONFIG.read_text(encoding="utf-8-sig"))
    if provider not in current.get("provider", {}):
        raise Invalid("opencode_required_provider_missing")
    # Per-process overlay only. Inherit provider auth through the existing client; never copy secrets.
    overlay = {"permission": "deny", "provider": {provider: {"options": {"timeout": False}}}}
    if job["model"] == FLASH:
        overlay["provider"][provider]["models"] = {"gemini-3.8-flash-high": {}}
    env["OPENCODE_CONFIG_CONTENT"] = json.dumps(overlay)
    policy.update(tools="deny", standalone=True, provider_timeout=False,
                  effort="high" if job["model"] == FLASH else "xhigh",
                  provider_configuration_sha256=file_sha(OPENCODE_CONFIG),
                  process_config=overlay, upstream_safety_settings="inherited_not_independently_verified",
                  provider_internal_retry_behavior="not_verified_runner_never_retries")
    return [str(OPENCODE), "run", "--standalone", "--format", "json", "--model", job["model"]], env, policy


def parse_gpt2(raw, prepared):
    data = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(data, dict):
        raise Invalid("gpt2_stdout_not_object")
    body = data.get("response", "")
    if not isinstance(body, str):
        body = ""
    meta = data.get("metadata")
    errors = []
    if data.get("completed") is not True:
        errors.append("gpt2_completed_not_true")
    if not isinstance(meta, dict):
        meta = {}
        errors.append("gpt2_metadata_missing")
    if meta.get("model") != prepared["job"]["model"] or meta.get("thinking_effort") != "max":
        errors.append("gpt2_model_or_effort_mismatch")
    stream = meta.get("stream_completion") or {}
    if stream.get("sse_done") is not True or stream.get("message_completed") is not True or stream.get("continuation_expected") is True:
        errors.append("gpt2_stream_not_complete")
    if (meta.get("prepared_response_validation") or {}).get("successful_assistant_terminal_observed") is not True:
        errors.append("gpt2_successful_terminal_not_observed")
    expected = [{k: x[k] for k in ("name", "size", "sha256")} for x in prepared["attachments"]]
    if meta.get("attachments") != expected:
        errors.append("gpt2_attachment_manifest_mismatch")
    if meta.get("response_sha256") != sha(body.encode("utf-8")):
        errors.append("gpt2_response_sha256_mismatch")
    slugs = set()
    def visit(obj):
        if isinstance(obj, dict):
            if isinstance(obj.get("model_slug"), str):
                slugs.add(obj["model_slug"])
            for value in obj.values():
                visit(value)
        elif isinstance(obj, list):
            for value in obj:
                visit(value)
    visit(meta.get("server_metadata_summary", {}))
    if any(slug != prepared["job"]["model"] for slug in slugs):
        errors.append("gpt2_server_model_slug_mismatch")
    return body, {"provider_metadata": meta, "server_model_slugs": sorted(slugs),
                  "completion_basis": "SSE_DONE_and_assistant_terminal_and_response_hash",
                  "attachment_upload_verified": bool(expected) and not any("attachment" in e for e in errors)}, errors


def parse_opencode(raw):
    records = []
    for line in raw.decode("utf-8-sig").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise Invalid("opencode_event_not_object")
            records.append(value)
    errors, text_parts, metadata, closed, tools = [], [], [], [], []
    terminals = []
    for event in records:
        part = event.get("part") or {}
        kind = event.get("type")
        if kind in ("error", "session.error") or event.get("error"):
            errors.append("opencode_error_event")
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            text_parts.append(part["text"])
            closed.append(isinstance((part.get("time") or {}).get("end"), (int, float)))
        if part.get("type") == "tool":
            status = (part.get("state") or {}).get("status")
            tools.append({"name": part.get("tool"), "status": status})
            # Failed tools can have side effects; any tool event invalidates this tool-free sample.
            errors.append("opencode_tool_event_in_tool_free_job")
        if kind == "step_finish" or part.get("type") == "step-finish":
            terminals.append(part.get("reason"))
        copy = dict(event)
        if "part" in copy:
            copy["part"] = {k: v for k, v in part.items() if k not in ("text", "state")}
        metadata.append(copy)
    if not text_parts:
        errors.append("opencode_no_text")
    if terminals and terminals[-1] not in ("stop", "end_turn", "completed"):
        errors.append("opencode_terminal_not_successful")
    if not terminals and (not closed or not all(closed)):
        errors.append("opencode_text_not_closed")
    # The installed CLI historically exposes only step_start + text(time.end), no usage/finish_reason.
    return "\n\n".join(text_parts), {"events": metadata, "tool_events": tools,
        "completion_basis": "explicit_terminal" if terminals else "CLI_exit_0_and_text_time_end",
        "server_completion_verified": bool(terminals), "actual_server_model_verified": False}, errors


def stop_owned_process(process):
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=20, check=False)
    else:
        import signal
        os.killpg(process.pid, signal.SIGKILL)
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=10)


def run_job(prepared, output, manifest_sha):
    job = prepared["job"]
    jid = job["job_id"]
    directory = output / jid
    try:
        directory.mkdir()  # Atomic reservation: even incomplete/failed prior jobs are never reused.
    except FileExistsError:
        return {"job_id": jid, "status": "exists_not_overwritten", "directory": str(directory)}
    began = time.monotonic()
    meta = {"job_id": jid, "status": "failed", "started": utc(), "channel": job["channel"],
            "requested_model": job["model"], "manifest_sha256": manifest_sha, "runner_sha256": file_sha(__file__),
            "prompt_source": str(prepared["source"]), "attachments": prepared["attachments"],
            "automatic_retry": False, "automatic_fallback": False, "exit_code": None,
            "submission_state": "not_started", "errors": [], "labels": job.get("labels", {})}
    for key in ("prompt_sha256", "prompt_bytes", "prompt_characters", "normalized_prompt_sha256",
                "normalized_prompt_bytes", "normalized_prompt_characters", "native_body_limit_bytes"):
        meta[key] = prepared[key]
    process = None
    try:
        write_bytes(directory / "prompt.txt", prepared["raw"])
        write_json(directory / "job.json", job)
        if prepared["attachments"]:
            (directory / "attachments").mkdir()
        for item in prepared["attachments"]:
            dest = directory / "attachments" / item["name"]
            with open(item["source"], "rb") as src, dest.open("xb") as dst:
                shutil.copyfileobj(src, dst)
            if dest.stat().st_size != item["size"] or file_sha(dest) != item["sha256"]:
                raise Invalid("attachment_changed_after_validation")
        argv, env, policy = build_command(prepared, directory)
        meta["policy"] = policy
        write_json(directory / "command.json", {"argv": argv, "policy": policy,
                   "stdin": "prompt.txt" if job["channel"] == "opencode" else "DEVNULL"})
        cwd = directory / "cwd"
        cwd.mkdir()
        if STOP.is_set():
            raise Invalid("cancelled_before_launch")
        write_json(directory / "started.json", meta)
        flags = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
        with (directory / "prompt.txt").open("rb") as stdin, (directory / "stdout.raw").open("xb") as stdout, (directory / "stderr.raw").open("xb") as stderr:
            process = subprocess.Popen(argv, cwd=cwd, env=env, shell=False,
                stdin=stdin if job["channel"] == "opencode" else subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, **flags)
            meta["submission_state"] = "child_started_remote_acceptance_unknown"
            deadline = time.monotonic() + job.get("timeout_seconds", 7200)
            while process.poll() is None:
                if STOP.is_set() or time.monotonic() >= deadline:
                    meta["errors"].append("interrupted" if STOP.is_set() else "timeout")
                    meta["submission_state"] = "unknown_do_not_automatically_replay"
                    stop_owned_process(process)
                    break
                time.sleep(0.2)
            meta["exit_code"] = process.returncode
        if process.returncode != 0:
            meta["errors"].append("child_nonzero_exit")
        raw = (directory / "stdout.raw").read_bytes()
        try:
            body, observed, errors = parse_gpt2(raw, prepared) if job["channel"] == "gpt2" else parse_opencode(raw)
            meta["observed"] = observed
            meta["errors"].extend(errors)
            write_bytes(directory / "response.txt", body.encode("utf-8"))
            meta["response_chars"] = len(body)
            meta["response_sha256"] = sha(body.encode("utf-8"))
            if len(body.strip()) < job.get("min_response_chars", 1):
                meta["errors"].append("response_empty_or_below_explicit_minimum")
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            meta["errors"].append("response_parse_failed_" + type(error).__name__)
        if not meta["errors"]:
            meta["status"] = "ok"
            meta["submission_state"] = "completed_by_recorded_evidence"
        else:
            meta["status"] = "timeout" if "timeout" in meta["errors"] else "failed"
    except Exception as error:
        if process is not None and process.poll() is None:
            stop_owned_process(process)
        meta["errors"].append(str(error) if isinstance(error, Invalid) else "local_" + type(error).__name__)
    finally:
        for name in ("stdout.raw", "stderr.raw"):
            path = directory / name
            if not path.exists():
                write_bytes(path, b"")
            meta[name + "_sha256"] = file_sha(path)
            meta[name + "_bytes"] = path.stat().st_size
        meta["ended"] = utc()
        meta["seconds"] = round(time.monotonic() - began, 3)
        write_json(directory / "metadata.json", meta)
    return {"job_id": jid, "status": meta["status"], "exit_code": meta["exit_code"],
            "errors": meta["errors"], "directory": str(directory)}


def save_preflight_failure(result, job, output, base, manifest_sha):
    jid = result["job_id"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,119}", jid):
        return
    directory = output / jid
    try:
        directory.mkdir()
    except (OSError, ValueError):
        return
    meta = {**result, "status": "failed_preflight", "started": utc(), "ended": utc(),
            "model_request_sent": False, "automatic_retry": False, "automatic_fallback": False,
            "manifest_sha256": manifest_sha}
    write_json(directory / "job.json", job)
    for name in ("stdout.raw", "stderr.raw"):
        write_bytes(directory / name, b"")
    try:
        source = resolve_input(base, job.get("prompt_file"))
        raw = source.read_bytes()
        write_bytes(directory / "prompt.txt", raw)
        meta.update(prompt_source=str(source), prompt_sha256=sha(raw), prompt_bytes=len(raw))
    except (OSError, ValueError):
        meta["prompt_snapshot_available"] = False
    write_json(directory / "metadata.json", meta)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=Path, default=EXPERIMENT / "jobs.json")
    parser.add_argument("--job-id", "--jobid", action="append", default=[], help="Exact job ID; repeat for a selection")
    parser.add_argument("--max-workers", type=int, choices=(1, 2))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--execute", action="store_true", help="Submit actual calls; default only validates offline")
    mode.add_argument("--dry-run", action="store_true", help="Validate and print hashes without subprocesses or writes")
    args = parser.parse_args(argv)
    try:
        manifest = args.jobs.resolve(strict=True)
        raw_manifest = manifest.read_bytes()
        spec = json.loads(raw_manifest.decode("utf-8-sig"))
        if not isinstance(spec, dict) or set(spec) - {"schema_version", "max_workers", "output_dir", "jobs"} or spec.get("schema_version") != 1:
            raise Invalid("invalid_manifest_schema")
        workers = args.max_workers if args.max_workers is not None else spec.get("max_workers", 1)
        if type(workers) is not int or workers not in (1, 2):
            raise Invalid("max_workers_must_be_1_or_2")
        output = (manifest.parent / spec.get("output_dir", "scripts/call_results")).resolve()
        if output == SCRIPT_DIR or not output.is_relative_to(SCRIPT_DIR):
            raise Invalid("output_dir_must_be_strictly_inside_experiment_scripts")
        jobs = spec.get("jobs")
        if not isinstance(jobs, list) or not jobs:
            raise Invalid("jobs_must_be_nonempty_list")
        ids = [j.get("job_id") if isinstance(j, dict) else None for j in jobs]
        if any(not isinstance(jid, str) for jid in ids) or len({x.casefold() for x in ids}) != len(ids):
            raise Invalid("job_ids_missing_or_duplicate_case_insensitive")
        if set(args.job_id) - set(ids):
            raise Invalid("requested_job_id_not_found")
        selected = [j for j in jobs if not args.job_id or j["job_id"] in args.job_id]
    except (OSError, ValueError, TypeError) as error:
        emit({"status": "invalid_manifest", "error": str(error) if isinstance(error, Invalid) else type(error).__name__})
        return 2
    prepared_jobs, results = [], []
    for job in selected:
        jid = job["job_id"]
        if job.get("enabled") is False:
            emit({"job_id": jid, "status": "disabled"})
            continue
        try:
            prepared = validate_job(job, manifest.parent)
            # Offline command construction validates executable/provider availability without invoking either.
            build_command(prepared, output / jid)
            prepared_jobs.append(prepared)
            if not args.execute:
                emit({"job_id": jid, "status": "validated_no_call", "model": job["model"],
                      "prompt_sha256": prepared["prompt_sha256"], "prompt_bytes": prepared["prompt_bytes"],
                      "prompt_characters": prepared["prompt_characters"], "attachments": prepared["attachments"],
                      "native_body_limit_bytes": prepared["native_body_limit_bytes"] if job["channel"] == "gpt2" else None,
                      "existing_output": (output / jid).exists()})
        except (OSError, ValueError, TypeError) as error:
            result = {"job_id": jid, "status": "invalid_job", "error": str(error) if isinstance(error, Invalid) else type(error).__name__}
            results.append(result)
            emit(result)
    if not args.execute:
        return 2 if results else 0
    # One batch owner across all output roots. Does not count independently launched legacy processes.
    lock = SCRIPT_DIR / ".run_calls.lock"
    try:
        with lock.open("x", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "started": utc()}, f)
    except FileExistsError:
        emit({"status": "runner_locked", "lock": str(lock), "automatic_stale_lock_removal": False})
        return 2
    try:
        output.mkdir(parents=True, exist_ok=True)
        # Record invalid jobs as failures without modifying any previously reserved directory.
        for result in results:
            job = next(j for j in selected if j["job_id"] == result["job_id"])
            save_preflight_failure(result, job, output, manifest.parent, sha(raw_manifest))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(run_job, p, output, sha(raw_manifest)) for p in prepared_jobs]
            try:
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    emit(result)
            except KeyboardInterrupt:
                STOP.set()
                emit({"status": "interrupted", "automatic_retry": False})
                return 130
    finally:
        lock.unlink()
    return 1 if any(r["status"] != "ok" for r in results) else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
