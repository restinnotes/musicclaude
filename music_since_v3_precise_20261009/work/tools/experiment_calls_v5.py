"""v5 实验合同：只凭 exact 落盘终态恢复；默认 complete+parse-failure 即 STOP。

相对 v4 的变更（对应原 run139 brief 裁决）：
- 原行为：max_attempts 循环 + 每次换 job_id/sampling 身份，parse 失败自动新提交。
- v5 默认：一次成功终态（status ok）后解析失败，记 STOP，不再取新 attempt；
  max_attempts 只覆盖“明确未提交可安全重试”的 pre_submit/retry_safe 路径，
  不被暗许为“完整提交失败后换样本”的预算。
- 显式 allow_new_sample_on_parse_failure=True 时，才允许取新 job/sample 身份
  继续（需 max_attempts 仍有预算），并记录 new_sample_reason；旧产物原样保留；
  同 sample 身份永不重提（sampling_key 与 prompt 都绑定到新 ask 时必须变化，
  否则拒收）。
- pre_submit 明确 retry_safe 的失败可在预算内 new attempt（新 job_id）；
  post_submit_ambiguous（queue_stop）不可。
- audit log 只记事实：parse_ok False 的记录永不写 parsed/成功语义。
"""
import threading
from pathlib import Path

import runner_v5 as runner
import execution_integrity_v5 as I

LOCK = threading.Lock()


def call(run_dir, step, core, model, prompt, parse_fn, key, prompt_version,
         prompt_template=None, extra=None, work_key="op60", work_name="", max_attempts=3,
         allow_new_sample_on_parse_failure=False, new_sample_reason=None,
         new_sample_prompt=None, new_sampling_key=None):
    directory = Path(run_dir)
    runner.check_policy(model)
    I.valid_id(core)
    I.valid_id(step)
    if type(max_attempts) is not int or max_attempts < 1:
        raise ValueError("max_attempts must be positive int")
    if type(allow_new_sample_on_parse_failure) is not bool:
        raise ValueError("allow_new_sample_on_parse_failure must be bool")
    if allow_new_sample_on_parse_failure and (new_sample_reason is None or new_sample_prompt is None
                                              or new_sampling_key is None):
        raise ValueError("explicit new sample requires reason+prompt+sampling_key")
    if not allow_new_sample_on_parse_failure and (new_sample_reason is not None or new_sample_prompt is not None
                                                  or new_sampling_key is not None):
        raise ValueError("new-sample fields require explicit allow_new_sample_on_parse_failure=True")
    record = {"key": key, "core": core, "model": model, "prompt_sha256": I.sha_text(prompt),
              "prompt_sha": I.sha_text(prompt), "prompt_version": prompt_version,
              "prompt_template": prompt_template, "attempts": [], "parse_ok": False,
              "parsed": None, "output": None, "output_file": None, "cached": False,
              "queue_stop": False, "new_model_submissions": 0, "resume_validations": 0,
              "new_sample_policy": ("explicit-new-sample-only"
                                    if allow_new_sample_on_parse_failure else "stop-on-first-complete-parse-failure"),
              "new_sample_taken": False, "new_sample_reason": None}
    attempt_prompts = {0: (prompt, None)}
    if allow_new_sample_on_parse_failure:
        attempt_prompts[1] = (new_sample_prompt, new_sampling_key)
    for attempt in range(max_attempts):
        if attempt in attempt_prompts:
            attempt_prompt, attempt_sampling = attempt_prompts[attempt]
        else:
            # 预算内也只允许已声明的样本；未声明的新样本一律 STOP，不自动编造。
            record.update(stop_reason="no declared new sample for attempt %d; max_attempts does not imply retry" % attempt)
            break
        if attempt > 0 and I.sha_text(attempt_prompt) == I.sha_text(prompt):
            raise I.ArtifactConflict("new sample must differ from failed sample; same sample never resubmitted")
        job = {"job_id": core + "__h" + I.sha_text(attempt_prompt)[:12] + "__attempt%d" % attempt,
               "branch": step, "model_key": model, "prompt": attempt_prompt, "prompt_version": prompt_version,
               "prompt_template": prompt_template, "work_key": work_key, "work_name": work_name,
               "sample": 1 if attempt == 0 else 2, "max_attempts": 1,
               "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
               "extra": dict(extra or {}, attempt=attempt)}
        if attempt_sampling is not None:
            job["sampling_key"] = attempt_sampling
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
            if attempt > 0:
                record.update(new_sample_taken=True, new_sample_reason=new_sample_reason,
                              new_sample_prompt_sha256=I.sha_text(attempt_prompt),
                              new_sample_sampling_key=attempt_sampling)
            record.update(parsed=parsed, output=text, parse_ok=True, output_file=meta["output_file"],
                          cached=resumed, producer_identity=meta["producer_identity"], request_identity=identity,
                          response_sha256=meta["response_sha256"], parse_error=None)
            break
        record["parse_error"] = error
        if meta.get("queue_stop") or meta.get("status") != "ok":
            # 未提交（pre_submit retry_safe）可在预算内继续；post_submit_ambiguous 停。
            if meta.get("status") != "ok" and meta.get("retry_safe") is True and not meta.get("queue_stop"):
                continue
            record["queue_stop"] = bool(meta.get("queue_stop"))
            break
        # 成功终态但解析失败：默认 STOP；只有显式声明的新样本才继续。
        record.update(stop_reason="complete terminal but parse failed; STOP (no silent new-sample retry)")
        break
    with LOCK:
        path = directory / ("cache_%s_exact.json" % step)
        log = I.strict_json(path.read_bytes().decode("utf-8")) if path.exists() else {"records": []}
        if not isinstance(log, dict) or not isinstance(log.get("records"), list):
            raise I.ArtifactConflict("invalid audit-only log")
        log["records"].append(record)
        I.write_json(path, log)
    return record
