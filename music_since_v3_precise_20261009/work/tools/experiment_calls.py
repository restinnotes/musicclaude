"""新实验共享调用存储；精确身份/完整输出/解析三者同时成立才复用。"""
import json
import threading
from pathlib import Path

import runner
from execution_integrity import (ArtifactConflict, check_policy, digest, sha_text, write_json)

LOCK = threading.Lock()


def call(run_dir, step, core, model, prompt, parse_fn, key, prompt_version,
         prompt_template=None, extra=None, work_key="op60", work_name="", max_attempts=3):
    run_dir = Path(run_dir)
    check_policy(model)
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    base = {"branch": step, "model_key": model, "prompt": prompt,
            "prompt_version": prompt_version, "prompt_template": prompt_template,
            "work_key": work_key, "work_name": work_name, "sample": 1,
            "forbid_tools": ["websearch", "webfetch", "bash", "read", "glob", "grep", "write", "edit"],
            "max_attempts": 1, "extra": extra or {}}
    rec = {"key": key, "core": core, "model": model, "prompt_sha": sha_text(prompt),
           "prompt_sha256": sha_text(prompt), "prompt_version": prompt_version,
           "prompt_template": prompt_template, "attempts": [], "cached": False,
           "parse_ok": False, "parsed": None, "output": None, "output_file": None}
    for att in range(max_attempts):
        # 新记录每一次尝试身份包含 actual attempt；已失败尝试不重提交。
        job = dict(base, job_id=core + "__h" + rec["prompt_sha256"][:12] + "__attempt%d" % att,
                   extra=dict(extra or {}, attempt=att))
        identity = runner.request_identity_for(job)
        mp = run_dir / "meta" / (job["job_id"] + ".json")
        if mp.exists():
            old = json.loads(mp.read_text(encoding="utf-8"))
            if old.get("request_identity") != identity:
                raise ArtifactConflict("实验旧身份不匹配；另取新run而非重写：" + job["job_id"])
            if old.get("status") != "ok":
                rec["attempts"].append({"job_id": job["job_id"], "status": "failed",
                                        "parse_ok": False, "parse_error": old.get("error")})
                if old.get("retry_safe") is not True or old.get("queue_stop"):
                    rec["parse_error"] = old.get("error")
                    rec["queue_stop"] = old.get("queue_stop", False)
                    break
                continue
        meta = runner.run_job(run_dir, job, timeout=1800 if model in ("gpt56w", "gpt6w") else 3600)
        path = run_dir / meta["output_file"]
        text = path.read_bytes().decode("utf-8") if path.is_file() else ""
        try:
            parsed, err = parse_fn(text) if meta["status"] == "ok" else (None, meta.get("error"))
        except Exception as e:
            parsed, err = None, "parser %s: %s" % (type(e).__name__, e)
        if any(x in text for x in ("temporarily frozen", "Temporary Chat activation control was not found", "incomplete_response")):
            parsed, err = None, "frozen/activation/incomplete marker"
        entry = {"job_id": job["job_id"], "status": meta["status"], "parse_ok": parsed is not None,
                 "parse_error": err, "meta_error": meta.get("error"), "output_chars": len(text),
                 "output_file": meta.get("output_file"), "resumed": meta.get("resumed", False),
                 "producer_identity": meta.get("producer_identity"),
                 "model_evidence": meta.get("model_evidence")}
        rec["attempts"].append(entry)
        print("[%s %s] attempt=%d parse_ok=%s %s" % (step, core, att, parsed is not None, err or ""), flush=True)
        if parsed is not None:
            rec.update(parsed=parsed, output=text, parse_ok=True, output_file=meta["output_file"],
                       cached=bool(meta.get("resumed") or meta.get("cache_hit")),
                       producer_identity=meta.get("producer_identity"), request_identity=meta.get("request_identity"),
                       response_sha256=meta.get("response_sha256"), parse_error=None)
            break
        rec["parse_error"] = err
        if meta["status"] != "ok" and (meta.get("retry_safe") is not True or meta.get("queue_stop")):
            rec["queue_stop"] = meta.get("queue_stop", False)
            break
    with LOCK:
        file = run_dir / ("cache_%s_exact.json" % step)
        data = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {"records": []}
        # 缓存为可审计日志；复用走磁盘 meta/input/output 校验，不仅依赖 parse_ok。
        data["records"].append(rec)
        write_json(file, data)
    return rec
