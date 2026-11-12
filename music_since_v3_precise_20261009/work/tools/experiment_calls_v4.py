"""v4 实验合同：只凭 exact 落盘终态恢复；解析失败不能变成成功缓存。"""
import threading
from pathlib import Path

import runner_v4 as runner
import execution_integrity_v4 as I

LOCK = threading.Lock()


def call(run_dir, step, core, model, prompt, parse_fn, key, prompt_version,
         prompt_template=None, extra=None, work_key="op60", work_name="", max_attempts=3):
    directory = Path(run_dir)
    runner.check_policy(model)
    I.valid_id(core)
    I.valid_id(step)
    if type(max_attempts) is not int or max_attempts < 1:
        raise ValueError("max_attempts must be positive int")
    record = {"key": key, "core": core, "model": model, "prompt_sha256": I.sha_text(prompt),
              "prompt_sha": I.sha_text(prompt), "prompt_version": prompt_version,
              "prompt_template": prompt_template, "attempts": [], "parse_ok": False,
              "parsed": None, "output": None, "output_file": None, "cached": False,
              "queue_stop": False, "new_model_submissions": 0, "resume_validations": 0}
    for attempt in range(max_attempts):
        job = {"job_id": core + "__h" + record["prompt_sha256"][:12] + "__attempt%d" % attempt,
               "branch": step, "model_key": model, "prompt": prompt, "prompt_version": prompt_version,
               "prompt_template": prompt_template, "work_key": work_key, "work_name": work_name,
               "sample": 1, "max_attempts": 1,
               "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
               "extra": dict(extra or {}, attempt=attempt)}
        identity = runner.request_identity_for(job)
        mp = directory / "meta" / (job["job_id"] + ".json")
        if mp.exists():
            previous = I.strict_json(mp.read_bytes().decode("utf-8"))
            if not isinstance(previous, dict) or previous.get("request_identity") != identity:
                raise I.ArtifactConflict("existing experiment producer/input changed")
            if previous.get("status") != "ok":
                I.verify_finalization(directory, job["job_id"], previous)
                record["attempts"].append({"job_id": job["job_id"], "status": "failed", "parse_ok": False,
                                           "parse_error": previous.get("error"), "resumed": True})
                if previous.get("retry_safe") is not True or previous.get("queue_stop"):
                    record.update(parse_error=previous.get("error"), queue_stop=bool(previous.get("queue_stop")))
                    break
                continue
        meta = runner.run_job(directory, job, timeout=1800 if model in ("gpt56w", "gpt6w") else 3600)
        if meta.get("status") == "ok":
            verified = I.resume(directory, job["job_id"], identity)
            if verified is None:
                raise I.ArtifactConflict("runner success lacks exact disk evidence")
            text = (directory / verified["output_file"]).read_bytes().decode("utf-8")
            try:
                parsed, error = parse_fn(text)
                if error is not None:
                    parsed = None
            except Exception as exc:
                parsed, error = None, "parser " + type(exc).__name__ + ": " + str(exc)
        else:
            text, parsed, error = "", None, meta.get("error")
        resumed = bool(meta.get("resumed") or meta.get("cache_hit"))
        record["resume_validations" if resumed else "new_model_submissions"] += 1 if resumed else meta.get("attempts", 0)
        record["attempts"].append({"job_id": job["job_id"], "status": meta["status"], "parse_ok": parsed is not None,
                                   "parse_error": error, "meta_error": meta.get("error"), "output_chars": len(text),
                                   "output_file": meta.get("output_file"), "resumed": resumed,
                                   "queue_stop": meta.get("queue_stop"), "producer_identity": meta.get("producer_identity")})
        if parsed is not None:
            record.update(parsed=parsed, output=text, parse_ok=True, output_file=meta["output_file"],
                          cached=resumed, producer_identity=meta["producer_identity"], request_identity=identity,
                          response_sha256=meta["response_sha256"], parse_error=None)
            break
        record["parse_error"] = error
        if meta.get("queue_stop") or (meta["status"] != "ok" and meta.get("retry_safe") is not True):
            record["queue_stop"] = bool(meta.get("queue_stop"))
            break
    with LOCK:
        path = directory / ("cache_%s_exact.json" % step)
        log = I.strict_json(path.read_bytes().decode("utf-8")) if path.exists() else {"records": []}
        if not isinstance(log, dict) or not isinstance(log.get("records"), list):
            raise I.ArtifactConflict("invalid audit-only log")
        log["records"].append(record)
        I.write_json(path, log)
    return record
