"""v3 允许路由的单次提交入口；旧 builder 仅作已测 argv 复用，不改旧全局。"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import runner as legacy
import execution_integrity as old
import execution_integrity_v3 as I
import gpt2_adapter_v3 as A

RUN_PROCESS = I.run_process
Slot = I.Slot
SLOT_DIR = I.SLOT_DIR
ALLOWED = set(legacy.AGY_KEYS) | {"luna", "luna_noweb", "gpt56w", "gpt6w"}
fill = legacy.fill


def check_policy(model):
    old.check_policy(model)
    if model not in ALLOWED:
        raise old.PolicyBlocked("v3 supports only explicitly allowed routes")


def _config(model):
    if model in legacy.AGY_KEYS:
        cfg = json.loads(json.dumps(legacy.GEMINI_PROVIDER_CFG))
        if not model.endswith("_web"):
            cfg["permission"] = "deny"
        return cfg
    return None


def request_identity_for(job):
    check_policy(job["model_key"])
    I.valid_id(job["job_id"])
    if job["model_key"] in A.MODEL_ROUTES:
        producer = A.producer_identity()
        context = old.job_identity(job, producer)
        return A.request_identity(job["model_key"], "max", job["prompt"], producer=producer,
                                  sampling_key=job.get("sampling_key", job["job_id"]), request_context=context)
    producer = {"schema": I.VERSION, "implementations": I.implementation_identity()}
    try:
        argv, mode, name = legacy._build_task(job["model_key"])
        files = {str(Path(arg).resolve()): I.sha_file(arg) for arg in argv if Path(arg).is_file()}
        for arg in argv:
            path = Path(arg)
            if path.name == "codex.js" and path.is_file():
                for binary in path.parent.parent.rglob("codex.exe"):
                    files[str(binary.resolve())] = I.sha_file(binary)
        producer.update(route=mode, model_name=name, argv=legacy._sanitize_argv(argv),
                        cli_files=files, configuration_sha256=I.digest(_config(job["model_key"])))
        if not files:
            raise ValueError("CLI implementation fingerprint unavailable")
    except Exception as exc:
        producer.update(initialization_error=I.safe_text(type(exc).__name__ + ": " + str(exc)))
    ident = old.job_identity(job, producer)
    ident["schema"] = I.VERSION
    return ident


def run_job(run_dir, job, timeout=3600):
    model, job_id = job["model_key"], job["job_id"]
    check_policy(model)
    I.valid_id(job_id)
    I.assert_content_safe(job["prompt"])
    if type(job.get("max_attempts", 1)) is not int or job.get("max_attempts", 1) < 1:
        raise ValueError("max_attempts must be positive int")
    if model in A.MODEL_ROUTES:
        # 不对已恢复的 meta 再 write_json；source/consumer 明确分列。
        producer = A.producer_identity()
        return A.call_web_gpt(model, job["prompt"], run_id=Path(run_dir).name, job_id=job_id,
                              out_dir=run_dir, timeout=timeout, max_attempts=1,
                              sampling_key=job.get("sampling_key", job_id), use_cache=job.get("use_cache", True),
                              request_context=old.job_identity(job, producer))
    directory, identity = Path(run_dir), request_identity_for(job)
    previous = I.resume(directory, job_id, identity)
    if previous is not None:
        return previous
    provider = "gemini" if model in legacy.AGY_KEYS else "codex"
    hold_file = SLOT_DIR / provider / "queue_hold.json"
    # 安全修订阶段同 provider 串行：结果分类/hold 建立先于下一次提交。
    with Slot(provider, 1, base=SLOT_DIR), Slot("all", int(os.environ.get("MUSIC_MAX_CALLS", "40")), base=SLOT_DIR):
        previous = I.resume(directory, job_id, identity)
        if previous is not None:
            return previous
        source = I.ref_cache(directory, identity)
        I.reserve(directory, job_id, identity)
        prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
        stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
        I.write_text(directory / prompt_rel, job["prompt"])
        I.write_text(directory / stdout_rel, "")
        I.write_text(directory / stderr_rel, "")
        t0 = time.monotonic()
        meta = {"schema": I.VERSION, "job_id": job_id, "run_id": directory.name, "model_key": model,
                "model_name": identity["producer"].get("model_name"), "request_identity": identity,
                "producer_identity": identity["producer"], "consumer_identity": identity["producer"],
                "prompt_file": prompt_rel, "output_file": output_rel, "stdout_file": stdout_rel,
                "stderr_file": stderr_rel, "prompt_sha256": I.sha_text(job["prompt"]), "attempts": 0,
                "branch": job.get("branch", ""), "prompt_version": job.get("prompt_version", ""),
                "prompt_template": job.get("prompt_template"), "work_key": job.get("work_key", ""),
                "sample": job.get("sample", 0), "raw_redacted": True, "automatic_retry": False,
                "terminal_verified": False, "queue_stop": False, "retry_safe": False, "cache_hit": False,
                "started": datetime.now().isoformat(), "tool_counts": {}}

        def finish(status, text="", error=None, **fields):
            I.write_text(directory / output_rel, text)
            meta.update(status=status, error=I.safe_text(error) if error else None, output_chars=len(text),
                        response_sha256=I.sha_text(text) if status == "ok" else None,
                        seconds=round(time.monotonic() - t0, 3), ended=datetime.now().isoformat(), **fields)
            I.write_json(directory / "meta" / (job_id + ".json"), meta)
            if not meta.get("cache_hit"):
                I.sample_record(directory, job_id, identity, status, meta)
            return meta

        if source is not None:
            text = (directory / source["output_file"]).read_bytes().decode("utf-8")
            I.write_text(directory / stdout_rel, "cache reference; source raw remains read-only\n")
            return finish("ok", text, terminal_verified=True, cache_hit=True,
                          cache_source_job=source["job_id"], exit_code=0, terminal=source.get("terminal"))
        if hold_file.exists():
            return finish("failed", error="provider queue held; inspect existing hold", queue_stop=True)
        if identity["producer"].get("initialization_error"):
            return finish("failed", error=identity["producer"]["initialization_error"],
                          retry_safe=True, failure_phase="local_initialization")
        argv, mode, name = legacy._build_task(model)
        if job.get("extra", {}).get("images") and provider == "codex":
            argv = argv[:-1] + [x for image in job["extra"]["images"] for x in ("-i", str(image))] + argv[-1:]
        if model == "luna":
            # 已测网络 sandbox，不使用 danger-full-access。
            argv = argv[:-1] + ["-s", "workspace-write", "-c", "sandbox_workspace_write.network_access=true"] + argv[-1:]
        legacy._ensure_init()
        env = dict(legacy._STATE["env"])
        if provider == "gemini":
            env["OPENCODE_CONFIG_CONTENT"] = json.dumps(_config(model))
        cwd = directory / "_empty_cwd" / job_id
        cwd.mkdir(parents=True, exist_ok=False)
        I.sample_record(directory, job_id, identity, "pending")
        meta["attempts"] = 1
        out_s = err_s = ""
        try:
            cp = RUN_PROCESS(argv, input=job["prompt"].encode("utf-8"), capture_output=True,
                             cwd=str(cwd), env=env, timeout=timeout,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out_s, err_s = cp.stdout.decode("utf-8", "strict"), cp.stderr.decode("utf-8", "strict")
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            if cp.returncode != 0 or old.PROTECT_RE.search(err_s):
                raise ValueError("nonzero exit/protection stderr; terminal unknown")
            text, counts, terminal = I.parse_opencode(out_s) if provider == "gemini" else I.parse_codex(out_s)
            used = [key for key in counts if key not in ("reasoning", "todo_list")]
            forbid = bool(job.get("forbid_tools")) or model == "luna_noweb" or (provider == "gemini" and not model.endswith("_web"))
            if forbid and used:
                return finish("failed", error="forbidden tools used: " + ",".join(used),
                              terminal_verified=True, exit_code=0, tool_counts=counts, terminal=terminal)
            I.assert_content_safe(text)
            return finish("ok", text, terminal_verified=True, exit_code=0, tool_counts=counts, terminal=terminal)
        except Exception as exc:
            I.hold(hold_file, job_id, directory.name, type(exc).__name__ + ": " + str(exc))
            if isinstance(exc, subprocess.TimeoutExpired):
                out_s = exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout or ""
                err_s = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
            I.write_text(directory / stdout_rel, I.safe_records(out_s))
            I.write_text(directory / stderr_rel, I.safe_records(err_s))
            return finish("failed", error=type(exc).__name__ + ": " + str(exc), queue_stop=True,
                          exit_code=None, server_cancelled="unknown")


def run_jobs(run_dir, jobs, max_workers=1, timeout=3600):
    if len({job["job_id"] for job in jobs}) != len(jobs):
        raise ValueError("duplicate job_id")
    for job in jobs:
        check_policy(job["model_key"])
    results, stopped = [], set()
    for job in jobs:
        provider = "gpt2" if job["model_key"] in A.MODEL_ROUTES else "gemini" if job["model_key"] in legacy.AGY_KEYS else "codex"
        if provider in stopped:
            results.append({"job_id": job["job_id"], "status": "skipped_queue_stop", "attempts": 0, "queue_stop": True})
            continue
        meta = run_job(run_dir, job, timeout)
        results.append(meta)
        if meta.get("queue_stop"):
            stopped.add(provider)
    return results
