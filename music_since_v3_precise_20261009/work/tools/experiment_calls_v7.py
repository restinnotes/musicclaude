"""Experiment wrapper with explicit sample changes and proven pre-submit retry."""
from __future__ import annotations

import json
import threading
from pathlib import Path

import runner_v7 as runner
import execution_integrity_v7 as I

LOCK = threading.Lock()


def _safe_parse_result(parsed, error):
    if error is not None or parsed is None:
        return None, error
    try:
        encoded = json.dumps(parsed, ensure_ascii=False, allow_nan=False)
        safe = I.safe_metadata(parsed)
        if safe != parsed:
            return None, "parser result rejected as sensitive-shaped"
        json.loads(encoded)
    except (TypeError, ValueError) as exc:
        return None, "parser result is not finite JSON: " + type(exc).__name__
    return parsed, None


def _verify_prior(directory, job_id, identity, prior):
    if not isinstance(prior, dict) or prior.get("request_identity") != identity:
        raise I.ArtifactConflict("existing experiment producer/input changed")
    I.verify_finalization(directory, job_id, prior)
    if prior.get("status") == "ok":
        verified = I.resume(directory, job_id, identity)
        if verified is None:
            raise I.ArtifactConflict("exact successful disk evidence missing")
        return verified
    if I.verify_pre_submit_proof(prior, identity):
        return prior
    return prior


def _verify_pre_submit_disk(directory, job_id, identity, returned):
    path = Path(directory) / "meta" / (job_id + ".json")
    if not path.is_file():
        return False
    try:
        disk = I._read_json_object(path, "pre-submit retry meta")
        if (disk.get("request_identity") != identity
                or disk.get("pre_submit_proof") != returned.get("pre_submit_proof")):
            return False
        I.verify_finalization(directory, job_id, disk)
        return I.verify_pre_submit_proof(disk, identity)
    except (I.ArtifactConflict, OSError, ValueError, TypeError):
        return False


def call(run_dir, step, core, model, prompt, parse_fn, key, prompt_version,
         prompt_template=None, extra=None, work_key="op60", work_name="", max_attempts=3,
         allow_new_sample_on_parse_failure=False, new_sample_reason=None,
         new_sample_prompt=None, new_sampling_key=None):
    directory = Path(run_dir)
    runner.check_policy(model)
    I.valid_id(core)
    I.valid_id(step)
    I.assert_content_safe(prompt)
    if type(max_attempts) is not int or max_attempts < 1:
        raise ValueError("max_attempts must be positive int")
    if type(allow_new_sample_on_parse_failure) is not bool:
        raise ValueError("allow_new_sample_on_parse_failure must be bool")
    if allow_new_sample_on_parse_failure:
        if (max_attempts < 2 or not isinstance(new_sample_reason, str) or not new_sample_reason.strip()
                or not isinstance(new_sampling_key, str) or not new_sampling_key.strip()):
            raise ValueError("explicit new sample requires budget >= 2, nonempty reason, and new sampling_key")
        I.assert_content_safe(new_sample_reason)
        I.assert_content_safe(new_sampling_key)
        if new_sample_prompt is not None:
            if not isinstance(new_sample_prompt, str) or not new_sample_prompt.strip():
                raise ValueError("explicit new_sample_prompt must be nonempty text")
            I.assert_content_safe(new_sample_prompt)
    elif any(value is not None for value in (new_sample_reason, new_sample_prompt, new_sampling_key)):
        raise ValueError("new-sample fields require explicit allow_new_sample_on_parse_failure=True")

    original_prompt_sha = I.sha_text(prompt)
    original_sampling_key = "sample-" + I.digest({"step": step, "core": core, "key": key,
                                                   "prompt_sha256": original_prompt_sha})[:24]
    if allow_new_sample_on_parse_failure and new_sampling_key == original_sampling_key:
        raise ValueError("new sample requires a distinct sampling_key")
    declared_new_prompt = prompt if new_sample_prompt is None else new_sample_prompt
    declared_new_prompt_sha = I.sha_text(declared_new_prompt)

    record = {
        "key": key, "core": core, "model": model,
        "prompt_sha256": original_prompt_sha, "prompt_sha": original_prompt_sha,
        "prompt_version": prompt_version, "prompt_template": prompt_template,
        "attempts": [], "parse_ok": False, "parsed": None, "output": None,
        "output_file": None, "cached": False, "queue_stop": False,
        "new_process_invocations": 0, "new_model_submissions": 0,
        "resume_validations": 0,
        "new_sample_policy": ("explicit-new-sample-after-complete-parse-failure"
                               if allow_new_sample_on_parse_failure else "stop-on-first-complete-parse-failure"),
        "new_sample_taken": False, "new_sample_reason": None,
    }

    current_sample = 0
    transport_attempt = 0
    total_attempts = 0
    used_new_sample = False
    base_extra = dict(extra or {})
    while total_attempts < max_attempts:
        attempt_prompt = prompt if current_sample == 0 else declared_new_prompt
        sample_key = original_sampling_key if current_sample == 0 else new_sampling_key
        prompt_sha = I.sha_text(attempt_prompt)
        job_id = core + "__h" + prompt_sha[:12] + "__s%d_t%d" % (current_sample, transport_attempt)
        I.valid_id(job_id)
        job_extra = dict(base_extra)
        job_extra["sample_index"] = current_sample
        job = {
            "job_id": job_id, "branch": step, "model_key": model,
            "prompt": attempt_prompt, "prompt_version": prompt_version,
            "prompt_template": prompt_template, "work_key": work_key,
            "work_name": work_name, "sample": current_sample + 1,
            "max_attempts": 1, "sampling_key": sample_key,
            "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
            "extra": job_extra,
        }
        identity = runner.request_identity_for(job)
        meta_path = directory / "meta" / (job_id + ".json")
        loaded_existing = False
        if meta_path.exists():
            prior = I.strict_json(meta_path.read_bytes().decode("utf-8"))
            meta = _verify_prior(directory, job_id, identity, prior)
            resumed = meta.get("status") == "ok"
            loaded_existing = True
            if meta.get("status") != "ok" and not I.verify_pre_submit_proof(meta, identity):
                total_attempts += 1
                record["attempts"].append({
                    "job_id": job_id, "status": "failed", "parse_ok": False,
                    "parse_error": meta.get("error"), "resumed": True,
                    "queue_stop": meta.get("queue_stop"),
                    "submission_state": meta.get("submission_state", "unknown"),
                })
                record.update(parse_error=I.safe_text(meta.get("error", "prior failed attempt")),
                              queue_stop=bool(meta.get("queue_stop")))
                break
        else:
            meta = runner.run_job(directory, job, timeout=1800 if model in ("gpt56w", "gpt6w") else 3600)
            resumed = bool(meta.get("resumed") or meta.get("cache_hit"))

        total_attempts += 1
        if loaded_existing:
            record["resume_validations"] += 1
        elif not resumed:
            record["new_process_invocations"] += int(meta.get("attempts", 0))
            # Ambiguous post-ticket failures count as a possible submission.
            # Proven pre-submit failures count as zero.
            if I.verify_pre_submit_proof(meta, identity):
                pass
            else:
                record["new_model_submissions"] += int(meta.get("provider_submissions", 0))
        elif not loaded_existing:
            record["resume_validations"] += 1

        if current_sample == 1 and not used_new_sample:
            used_new_sample = True
            record.update(new_sample_taken=True, new_sample_reason=new_sample_reason,
                          new_sample_prompt_sha256=declared_new_prompt_sha,
                          new_sample_sampling_key_sha256=I.sha_text(new_sampling_key),
                          new_sample_identity_sha256=I.identity_digest(identity))

        if meta.get("status") == "ok":
            verified = I.resume(directory, job_id, identity)
            if verified is None:
                raise I.ArtifactConflict("runner success lacks exact finalized disk evidence")
            text = I._inside(directory, verified["output_file"]).read_bytes().decode("utf-8")
            try:
                parsed, error = parse_fn(text)
                parsed, error = _safe_parse_result(parsed, error)
            except Exception as exc:
                parsed, error = None, "parser " + type(exc).__name__ + ": " + I.safe_text(str(exc))
            parsed_ok = parsed is not None and error is None
            attempt_record = {
                "job_id": job_id, "attempt_kind": "new_sample" if current_sample else (
                    "transport_retry" if transport_attempt else "initial"),
                "status": "ok", "parse_ok": parsed_ok,
                "parse_error": None if parsed_ok else I.safe_text(error or "parser returned no value"),
                "output_chars": len(text), "output_file": verified["output_file"],
                "response_sha256": verified.get("response_sha256"),
                "resumed": resumed, "cache_hit": bool(meta.get("cache_hit")),
                "queue_stop": False, "request_identity_sha256": I.identity_digest(identity),
            }
            record["attempts"].append(attempt_record)
            if parsed_ok:
                record.update(
                    parsed=parsed, output=text, parse_ok=True,
                    output_file=verified["output_file"], cached=resumed or bool(meta.get("cache_hit")),
                    producer_identity=meta.get("producer_identity"),
                    request_identity=identity, response_sha256=verified.get("response_sha256"),
                    parse_error=None,
                )
                break
            record["parse_error"] = I.safe_text(error or "parser returned no value")
            if (allow_new_sample_on_parse_failure and current_sample == 0
                    and not used_new_sample and total_attempts < max_attempts):
                current_sample = 1
                transport_attempt = 0
                continue
            record["stop_reason"] = "complete terminal parse failed; no undeclared sample will be submitted"
            break

        # A transport retry is permitted only after the exact source-bound
        # proof has been finalized and the v7 ticket has been released.
        pre_submit_valid = I.verify_pre_submit_proof(meta, identity)
        if pre_submit_valid and not loaded_existing:
            pre_submit_valid = _verify_pre_submit_disk(directory, job_id, identity, meta)
            if not pre_submit_valid:
                raise I.ArtifactConflict("retry_safe return lacks exact finalized source-bound pre-submit evidence")
        if (pre_submit_valid and meta.get("queue_stop") is not True and total_attempts < max_attempts):
            record["attempts"].append({
                "job_id": job_id, "attempt_kind": "proven_pre_submit_transport_failure",
                "status": "failed", "parse_ok": False,
                "parse_error": I.safe_text(meta.get("error", "pre-submit failure")),
                "resumed": resumed, "queue_stop": False,
                "submission_state": "proven_not_submitted",
                "request_identity_sha256": I.identity_digest(identity),
            })
            transport_attempt += 1
            continue

        record["attempts"].append({
            "job_id": job_id, "attempt_kind": "new_sample" if current_sample else (
                "transport_retry" if transport_attempt else "initial"),
            "status": meta.get("status", "failed"), "parse_ok": False,
            "parse_error": I.safe_text(meta.get("error", "execution did not produce an exact terminal")),
            "meta_error": I.safe_text(meta.get("error", "")),
            "output_file": meta.get("output_file"), "resumed": resumed,
            "queue_stop": bool(meta.get("queue_stop")),
            "submission_state": meta.get("submission_state", "unknown"),
            "request_identity_sha256": I.identity_digest(identity),
        })
        record["parse_error"] = I.safe_text(meta.get("error", "execution did not produce an exact terminal"))
        record["queue_stop"] = bool(meta.get("queue_stop"))
        break

    with LOCK:
        path = directory / ("cache_%s_exact.json" % step)
        log = I.strict_json(path.read_bytes().decode("utf-8")) if path.exists() else {"records": []}
        if not isinstance(log, dict) or not isinstance(log.get("records"), list):
            raise I.ArtifactConflict("invalid audit-only experiment log")
        log["records"].append(record)
        I.write_json(path, log)
    return record
