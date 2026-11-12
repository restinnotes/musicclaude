"""网页 GPT 的 gpt2 适配层；r2 使用精确身份、独立采样键与只读续跑。

实测 CLI：gpt2 ask --file <UTF-8> --model <slug> --json。
effort 请求固定 max，不能据此声称服务端真实推理深度。输入超限失败，不截断。
旧调用只读；新 job_id 不覆盖旧证据。raw 是脱敏 CLI 记录，不保存会话凭据。
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from execution_integrity import (ArtifactConflict, GlobalSlot, PROTECT_RE, checked_resume,
    digest, model_evidence, run_process, safe_metadata, safe_records, safe_text, sha_file, sha_text,
    source_fingerprint, write_json, write_text)

ADAPTER_VERSION = "r2_20261009"
ADAPTER_ROUTE = "gpt2"
GPT2_CMD = os.environ.get("MUSIC_GPT2_CMD", r"D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd")
SAFECHAIN_ROOT = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", r"D:\musicclaude\gpt2agent-safechain"))
MODEL_ROUTES = {"gpt56w": {"slug": "gpt-5-6-thinking", "effort": "max"},
                "gpt6w": {"slug": "gpt-6-thinking", "effort": "max"}}
MAX_PROMPT_CHARS = 65536
STDERR_TAIL_CHARS = 2000
RUN_PROCESS = run_process
HOLD_FILE = Path(__file__).resolve().parents[1] / "runs/_call_slots/gpt2web/queue_hold.json"


def _cli_version():
    try:
        cp = subprocess.run(["git", "-C", str(SAFECHAIN_ROOT), "rev-parse", "HEAD"],
                            capture_output=True, timeout=30,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if cp.returncode == 0:
            return cp.stdout.decode("utf-8", "replace").strip()
    except Exception:
        pass
    return "unknown"


def producer_identity(gpt2_cmd=None):
    cmd = Path(gpt2_cmd or GPT2_CMD)
    return {"route": ADAPTER_ROUTE, "adapter_version": ADAPTER_VERSION,
            "adapter_sha256": sha_file(__file__),
            "integrity_sha256": sha_file(Path(__file__).with_name("execution_integrity.py")),
            "cli": str(cmd.resolve()), "cli_sha256": sha_file(cmd) if cmd.is_file() else None,
            "cli_version": _cli_version(),
            # HEAD 不能识别未提交/未跟踪的当前 CLI 实现。
            "cli_source": source_fingerprint(SAFECHAIN_ROOT, ("bin", "src", "tools/chatgpt_web", "vendor/gpt2agent"))}


def request_identity(model_key, effort, prompt_text, *, producer=None, sampling_key=""):
    route = MODEL_ROUTES.get(model_key) or {}
    return {"producer": producer or producer_identity(), "model_key": model_key,
            "requested_model": route.get("slug"), "requested_effort": effort,
            "prompt_sha256": sha_text(prompt_text), "sampling_key": sampling_key}


def cache_key(model_key, effort, prompt_text, *, producer=None, sampling_key=""):
    return digest(request_identity(model_key, effort, prompt_text,
                                  producer=producer, sampling_key=sampling_key))


def _write_text(path, text):
    write_text(path, text)


def _cmd_argv(cmd):
    if sys.platform == "win32" and str(cmd).lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", cmd]
    return [cmd]


def _reported_model(metadata, requested):
    ev = model_evidence(metadata, requested)
    return ev["server_slugs"][0] if ev["verdict"] == "match" else None


def _safe_stdout(text):
    return safe_records(text)


def call_web_gpt(model_key, prompt_text, *, run_id, job_id, out_dir, effort="max",
                 timeout=1800, max_attempts=1, gpt2_cmd=None, sampling_key=None,
                 use_cache=True, request_context=None):
    """最多提交一次；timeout/post-submit/保护信号停队列，失败不缓存为成功。

    默认 sampling_key=job_id，换 job 是新样本。显式共享键才可跨 job 复用。
    producer 身份原样保留，consumer 身份单列；相同 job 只读恢复，不清空 raw。
    """
    out_dir = Path(out_dir)
    producer = producer_identity(gpt2_cmd)
    identity = request_identity(model_key, effort, prompt_text, producer=producer,
                                sampling_key=job_id if sampling_key is None else sampling_key)
    if request_context is not None:
        identity["request_context"] = request_context
    old = checked_resume(out_dir, job_id, identity)
    if old is not None:
        return old
    artifacts = [out_dir / d / (job_id + ext) for d, ext in (("prompts", ".txt"), ("outputs", ".md"))]
    if any(p.exists() for p in artifacts):
        raise ArtifactConflict("存在未完成/旧产物，不覆盖；请用新 job_id：" + job_id)
    t0 = time.monotonic()
    prompt_rel, output_rel = "prompts/%s.txt" % job_id, "outputs/%s.md" % job_id
    stdout_rel, stderr_rel = "outputs/raw/%s.stdout.txt" % job_id, "outputs/raw/%s.stderr.txt" % job_id
    write_text(out_dir / prompt_rel, prompt_text)
    meta = {"job_id": job_id, "run_id": run_id, "route": ADAPTER_ROUTE,
            "adapter_version": ADAPTER_VERSION, "model_key": model_key,
            "requested_effort": effort, "effort_is_request_not_backend_proof": True,
            "prompt_file": prompt_rel, "prompt_chars": len(prompt_text),
            "prompt_sha256": sha_text(prompt_text), "output_file": output_rel,
            "stdout_file": stdout_rel, "stderr_file": stderr_rel,
            "started": datetime.now().isoformat(timespec="seconds"),
            "cli": producer["cli"], "cli_version": producer["cli_version"],
            "producer_identity": producer, "consumer_identity": producer,
            "request_identity": identity, "cache_key": digest(identity), "cache_hit": False,
            "raw_redacted": True, "automatic_retry": False, "tool_counts": {}}

    def finish(status, **kw):
        meta.update(status=status, ended=datetime.now().isoformat(timespec="seconds"),
                    seconds=round(time.monotonic() - t0, 1), **kw)
        write_json(out_dir / "meta" / (job_id + ".json"), meta)
        return meta

    def fail(error, **kw):
        write_text(out_dir / output_rel, "")
        for rel in (stdout_rel, stderr_rel):
            if not (out_dir / rel).exists():
                write_text(out_dir / rel, "")
        return finish("failed", error=safe_text(error), response_sha256=None,
                      output_chars=0, **kw)

    route = MODEL_ROUTES.get(model_key)
    if route is None:
        return fail("unknown model_key for gpt2 route: " + model_key, attempts=0, returncode=None)
    meta["requested_model"] = route["slug"]
    if effort != route["effort"]:
        return fail("effort mismatch: fixed max, requested " + effort, attempts=0, returncode=None)
    if len(prompt_text) > MAX_PROMPT_CHARS:
        return fail("prompt too long: %d > %d; not truncated" % (len(prompt_text), MAX_PROMPT_CHARS),
                    attempts=0, returncode=None)
    cache_path = out_dir / "cache" / (meta["cache_key"] + ".json")
    if use_cache and cache_path.exists():
        try:
            hit = json.loads(cache_path.read_text(encoding="utf-8"))
            text = hit.get("response")
            if (hit.get("request_identity") == identity and isinstance(text, str) and text.strip()
                    and sha_text(text) == hit.get("response_sha256")):
                write_text(out_dir / output_rel, text)
                meta["producer_identity"] = hit["producer_identity"]
                meta["cache_source_job"] = hit.get("producer_job_id")
                # 命中是复用，不伪造一次 CLI stdout，也不抹去源 job 的 raw。
                write_text(out_dir / stdout_rel, json.dumps({"cache_reference": meta["cache_key"],
                           "producer_job_id": hit.get("producer_job_id")}, ensure_ascii=False))
                write_text(out_dir / stderr_rel, "")
                return finish("ok", response_sha256=hit["response_sha256"], cache_hit=True,
                              output_chars=len(text), replacement_chars=text.count("\ufffd"),
                              attempts=0, returncode=0, cli_metadata=hit.get("cli_metadata"),
                              model_evidence=hit.get("model_evidence"), reported_model=hit.get("reported_model"))
        except (ValueError, KeyError, OSError):
            pass
    argv = _cmd_argv(gpt2_cmd or GPT2_CMD) + ["ask", "--file", str((out_dir / prompt_rel).resolve()),
                                               "--model", route["slug"], "--json"]
    with GlobalSlot("gpt2web", 1):
        if HOLD_FILE.exists():
            return fail("gpt2 queue held: inspect " + str(HOLD_FILE), attempts=0, returncode=None,
                        queue_stop=True, retry_safe=False)
        try:
            cp = RUN_PROCESS(argv, input=None, capture_output=True, cwd=str(out_dir), timeout=timeout,
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            out_s, err_s = cp.stdout.decode("utf-8", "replace"), cp.stderr.decode("utf-8", "replace")
            returncode = cp.returncode
        except subprocess.TimeoutExpired as e:
            out_s = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else e.stdout or ""
            err_s = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else e.stderr or ""
            write_text(out_dir / stdout_rel, _safe_stdout(out_s))
            write_text(out_dir / stderr_rel, safe_text(err_s))
            write_json(HOLD_FILE, {"job_id": job_id, "run_id": run_id, "reason": "timeout; server turn unknown",
                                  "created": datetime.now().isoformat()})
            return fail("timeout after %ss; local process tree reclaimed, server state unknown" % timeout,
                        attempts=1, returncode=None, queue_stop=True, retry_safe=False)
        except Exception as e:
            return fail("%s: %s" % (type(e).__name__, e), attempts=1, returncode=None, retry_safe=False)
        write_text(out_dir / stdout_rel, _safe_stdout(out_s))
        write_text(out_dir / stderr_rel, safe_text(err_s))
        try:
            payload = json.loads(out_s if returncode == 0 else err_s)
        except (ValueError, TypeError):
            payload = {}
        protect = PROTECT_RE.search(err_s) if returncode != 0 else None  # 10-09: only a failed call's stderr
        phase = payload.get("phase") if isinstance(payload, dict) else None
        # 只有明确 pre_submit 可以判未提交。坏 JSON/未知终态不能再次盲提。
        valid_terminal = (returncode == 0 and isinstance(payload, dict)
                          and payload.get("completed") and isinstance(payload.get("response"), str))
        ambiguous = phase in ("post_submit", "post_submit_ambiguous") or (not valid_terminal and phase != "pre_submit")
        if protect:  # 10-09: ambiguous single call fails only that job; only protection signals stop the gpt2 queue
            write_json(HOLD_FILE, {"job_id": job_id, "run_id": run_id,
                                  "reason": "protection_signal" if protect else phase or "unknown_terminal_state",
                                  "created": datetime.now().isoformat()})
        if returncode != 0:
            return fail("exit %s: %s" % (returncode, safe_text(err_s[-500:])), attempts=1,
                        returncode=returncode, failure_phase=phase,
                        queue_stop=bool(protect), retry_safe=not protect)
        if not valid_terminal:
            return fail("cli reported incomplete or bad json stdout", attempts=1, returncode=returncode,
                        queue_stop=bool(protect), retry_safe=False)
        text, md = payload["response"], payload.get("metadata")
        if not text.strip():
            return fail("empty response", attempts=1, returncode=returncode, retry_safe=False)
        ev = model_evidence(md, route["slug"])
        if ev["verdict"] == "mismatch":
            return fail("server model_slug mismatch", attempts=1, returncode=returncode,
                        model_evidence=ev, retry_safe=False)
        if protect:
            return fail("protection signal in CLI stderr; queue stopped", attempts=1, returncode=returncode,
                        queue_stop=True, retry_safe=False)
        md = safe_metadata(md)
        resp_sha = sha_text(text)
        write_text(out_dir / output_rel, text)
        reported = ev["server_slugs"][0] if ev["verdict"] == "match" else None
        if use_cache:
            write_json(cache_path, {"request_identity": identity, "response": text, "response_sha256": resp_sha,
                                   "producer_identity": producer, "producer_job_id": job_id,
                                   "cli_metadata": md, "model_evidence": ev, "reported_model": reported})
        return finish("ok", response_sha256=resp_sha, returncode=returncode, attempts=1,
                      output_chars=len(text), replacement_chars=text.count("\ufffd"), cli_metadata=md,
                      reported_model=reported, model_evidence=ev, stderr_tail=safe_text(err_s[-STDERR_TAIL_CHARS:]))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-key", required=True, choices=sorted(MODEL_ROUTES))
    ap.add_argument("--prompt-file", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--job-id", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--effort", default="max")
    ap.add_argument("--timeout", type=float, default=1800)
    a = ap.parse_args()
    m = call_web_gpt(a.model_key, a.prompt_file.read_text(encoding="utf-8-sig"), run_id=a.run_id,
                     job_id=a.job_id, out_dir=a.out_dir, effort=a.effort, timeout=a.timeout)
    print(json.dumps(m, ensure_ascii=False, indent=2))
    sys.exit(0 if m["status"] == "ok" else 1)
