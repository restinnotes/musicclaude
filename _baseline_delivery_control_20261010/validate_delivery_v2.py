#!/usr/bin/env python3
"""独立交付验收验证器 v2（只读，不调用任何模型，不修改原证据，不产生子进程）。

相对 v1 修复（主控 2026-10-10 点名 4 bug，全部实测覆盖）：
  BUG1 review-schema 过浅：D/G winner 只允许 A/B，但冻结模板明写
    winner ∈ {A|B|TIE|UNDETERMINED}；且只检 task 字段。v2 按 kind 做完整结构校验：
    D: task==D, station_k==manifest, winner∈4枚举,
       A_source_supported/B_source_supported∈{yes,partial,no,uncertain},
       quoted_evidence 非空且 excerpt 在 prompt 内逐字，reasoned_decision≥100中文字。
    G: task==G, station_k==manifest, winner∈4枚举,
       source_quotes 非空且逐字，reasoned_decision≥100中文字。
    F: task==F, station_k==manifest, sample_count==prompt【sample_count】真值,
       semantic_units 非空且 unit_id 唯一，
       status∈{grounded_valuable,grounded_redundant,unsupported,language_only,uncertain},
       source_evidence 非空 quote 且逐字，first_seen∈seen_in，
       per_trial 恰覆盖 T1..TN，best_trial_candidate∈{T1..TN,NONE}，
       saturation_assessment∈3枚举，recommend_more∈{YES,NO,UNCERTAIN}。
    以上只判“结构完整”，不作音乐审美评判；失败记 review_schema_fail 单列，
    不进 transport_valid。
  BUG2 session 唯一性漏 pilot 碰撞：v1 把 pilot handle 移出检查集，pilot 与当前轮
    复用同一 handle 会漏报。v2 全量建 map；pilot 之间复用仍记 pilot 例外；
    pilot handle 若出现在任何非 pilot slot → pilot_collision_with_current 硬失败单列。
  BUG3 concurrency_peak_observed=9 口径不明：v2 四层分开：
    meta_interval_peak（含/排 pilot 两版，沿用旧口径并点名构成）、
    scheduler_worker_peak（pipeline events launched→result 同 task 配对在途峰值）、
    owned_submitted_marker_peak（submitted.json utc ±60s 窗计数，注：提交标记峰值）、
    owned_completed_terminal_peak（result completed+terminal utc 窗）。
    去重说明：原 meta/attempt 文件与 supplement 绑定按 job_id 去重计数。
  BUG4 recovered_verified 只有文件 SHA 却声称 sha+session+binding：
    v2 --supplement-dir 逐条独立验证 7 项并分层布尔输出：
    sha_self（supplement==其.meta.json 声明 sha）
    sha_source（supplement==源 owned job response.txt sha）
    binding（源 job started 五项+归一化 prompt 绑定+时间窗）
    terminal（源 result completed+terminal+no_work_cont）
    submitted（submitted marker 存在）
    canonical_untouched（原 meta 状态/exit 原样未动）
    schema_source（补充 payload 过同 track schema/source 规则；A/B/C 按 v1 同规则；
      旧 B18/gpt6w/r02 类非法控制字符保留不修原文，如实记 fail）
    recovered_verified 仅 7 项全过才为真；canonical 计数永不混入恢复。

不变量（回归门，失败即 failed_invariants）：
  canonical_base_transport_valid_success == 146
  canonical_base_source_valid_among_valid == 145
  canonical_not_inflated_by_recovery（恢复条目不计入 canonical 任一计数）
旧 exit1/空 raw 永不伪造成 success（沿用 v1 transport 全链）。

用法（必须 -I，从可信目录调用，不从下载解压目录运行）：
  python -I validate_delivery_v2.py --data-root D:/musicclaude/_dl_latest_zip_work --report-dir <新report root> [--supplement-dir D:/musicclaude/_baseline_recovery_control_20261010] [--owned-runs-dir D:/musicclaude/gpt2agent-safechain/runs/yi-cookie-repair-20261006] [--scheduler-events <events.jsonl>]
输出：delivery_validation_v2.json + delivery_validation_v2_summary.txt（版本化，不碰旧文件）。
"""
import argparse
import collections
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

MODEL_FULL = {"gpt6w": "gpt-6-thinking", "gpt56w": "gpt-5-6-thinking"}
ALLOWED_A = {"insight", "restatement", "manufactured", "imported", "undetermined"}
ALLOWED_B = {"valuable_new_link", "restatement", "unsupported_causality", "premature_lock", "not_enough_evidence"}
ALLOWED_C = {"KEEP", "RETIRE", "REPLACE", "APPEND", "SILENCE"}
BASE_ROUNDS = list(range(1, 6))
ALL_ROUNDS = list(range(1, 13))
ATTEMPT_RE = re.compile(r"^r(\d{2})\.attempt(\d+)\.(meta\.json|raw\.json|stderr\.txt)$")
SAMPLE_RE = re.compile(r"【sample_count】\s*(\d+)")

# review 枚举（来自冻结 prompt 模板原文）
DG_WINNER = {"A", "B", "TIE", "UNDETERMINED"}
D_SUPPORT = {"yes", "partial", "no", "uncertain"}
F_STATUS = {"grounded_valuable", "grounded_redundant", "unsupported", "language_only", "uncertain"}
F_SAT = {"SATURATED_WITHIN_SAMPLE", "NOT_SATURATED", "UNCERTAIN"}
F_REC = {"YES", "NO", "UNCERTAIN"}

# canonical 回归门默认值（旧 v1 实测值；v3 起以 --expected-base-* 或 --baseline-snapshot 为准）
DEFAULT_BASE_TRANSPORT = 146
DEFAULT_BASE_SOURCE_VALID = 145

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def review_input_source_map(data_root: Path, kind: str, row: dict) -> dict[str, str]:
    """review prompt 内各 source_id → 冻结 input 源片段（只读 input，不读稿件正文区）。

    D/G/F（k 站）：screen_before 各 id text + current_candidates 各 id text。
    PREVIOUS 映射为 screen_before 全文拼合；A/B 为匿名稿引用（prompt 内逐字存在即可，
    不记 source_grounded——稿件自引不能自证落源）。
    F 的 quote 若只在 prompt 尾部某 T 稿出现、而不在候选/先前屏，即记 non_source_quote。
    input 缺失时返回 {}（调用方记 input_absent，不判 fail）。
    """
    m: dict[str, str] = {}
    try:
        k = row.get("station_k")
        if kind in ("D", "G", "F") and isinstance(k, int):
            orig = json.loads((data_root / f"inputs/op60/C_k{k:02d}.json").read_text(encoding="utf-8"))
            for v in orig.get("screen_before", []) or []:
                if isinstance(v, dict) and v.get("id") and isinstance(v.get("text"), str):
                    m[v["id"]] = v["text"]
            for v in orig.get("current_candidates", []) or []:
                if isinstance(v, dict) and v.get("id") and isinstance(v.get("text"), str):
                    m[v["id"]] = v["text"]
            prev_texts = [v["text"] for v in orig.get("screen_before", []) or []
                          if isinstance(v, dict) and isinstance(v.get("text"), str)]
            if prev_texts:
                m["PREVIOUS"] = "\n".join(prev_texts)
    except Exception:  # noqa: BLE001
        return {}
    return m


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {str(e)[:200]}"


def parse_iso(s):
    try:
        return datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return None


def norm_prompt_bytes(raw: bytes) -> bytes:
    return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").rstrip().encode("utf-8")


# ---------------- trial slot（沿用 v1 全链，transport 口径不变） ----------------

def check_trial_slot(data_root: Path, job: dict, model: str, rnd: int, prompt_bytes: bytes, prompt_ok: bool):
    jid = job["job_id"]
    d = data_root / "results" / "trials" / model / jid
    stem = f"r{rnd:02d}"
    meta_p = d / f"{stem}.meta.json"
    raw_p = d / f"{stem}.raw.json"
    txt_p = d / f"{stem}.txt"
    err_p = d / f"{stem}.stderr.txt"
    attempts = sorted([f.name for f in d.glob(f"{stem}.attempt*")]) if d.is_dir() else []
    rec = {
        "area": "trial", "job": jid, "model": model, "round": rnd,
        "files": {
            "meta": meta_p.exists(), "raw": raw_p.exists(),
            "txt": txt_p.exists(), "stderr": err_p.exists(),
            "attempt_files": attempts,
        },
    }
    if not meta_p.exists():
        rec.update({"final_class": "missing", "transport_valid": False,
                    "transport_reasons": ["final meta absent: no evidence"],
                    "schema_parse_ok": None, "source_valid": None})
        return rec
    meta, meta_err = load_json(meta_p)
    if meta is None or not isinstance(meta, dict):
        rec.update({"final_class": "other_failure", "transport_valid": False,
                    "transport_reasons": [f"meta unparseable: {meta_err}"],
                    "schema_parse_ok": None, "source_valid": None})
        return rec
    reasons = []
    exp_full = MODEL_FULL[model]
    if meta.get("model_requested") != exp_full:
        reasons.append(f"model_requested {meta.get('model_requested')!r} != {exp_full}")
    if meta.get("model_reported") != exp_full:
        reasons.append(f"model_reported {meta.get('model_reported')!r} != {exp_full}")
    if meta.get("thinking_effort") != "max":
        reasons.append(f"thinking_effort {meta.get('thinking_effort')!r} != max")
    if meta.get("prompt_sha256") != job["input_sha256"]:
        reasons.append("meta.prompt_sha256 != manifest input_sha256")
    if not prompt_ok:
        reasons.append("frozen prompt bytes != manifest input_sha256")
    raw_sz = raw_p.stat().st_size if raw_p.exists() else -1
    raw_obj = None
    raw_meta = {}
    response = None
    session_handle = None
    if raw_sz == 0:
        raw_empty = True
    elif raw_p.exists():
        raw_empty = False
        try:
            raw_obj = json.loads(raw_p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            reasons.append(f"raw.json unparseable: {type(e).__name__}")
            raw_obj = None
    else:
        raw_empty = None
        reasons.append("raw.json absent")
    if isinstance(raw_obj, dict):
        raw_meta = raw_obj.get("metadata") or {}
        response = raw_obj.get("response")
        for k in ("session_handle", "session_id", "conversation_id"):
            if raw_meta.get(k):
                session_handle = raw_meta.get(k)
                break
    status = meta.get("status")
    completed = meta.get("completed")
    exit_code = meta.get("exit_code")
    pilot = bool(meta.get("imported_from_pilot"))
    is_success_claim = (status == "success" and completed is True and exit_code == 0)
    obs = meta.get("response_sha256_observed")
    rep = meta.get("response_sha256_reported")
    txt_info = {"exists": txt_p.exists(), "archive_byte_sha256": None,
                "logical_sha256": None, "matches_observed": None, "newline_variant": None}
    if txt_p.exists():
        try:
            disk = txt_p.read_bytes()
        except Exception as e:  # noqa: BLE001
            reasons.append(f"txt unreadable: {type(e).__name__}")
            disk = None
        if disk is not None:
            txt_info["archive_byte_sha256"] = sha_bytes(disk)
            txt_info["newline_variant"] = "crlf" if b"\r\n" in disk else ("lf" if b"\n" in disk else "none")
            norm = disk.replace(b"\r\n", b"\n")
            txt_info["logical_sha256"] = sha_bytes(norm)
    if is_success_claim:
        if not isinstance(response, str) or not response.strip():
            reasons.append("success claimed but raw.response empty/non-string")
        else:
            recomputed = sha_bytes(response.encode("utf-8"))
            if obs != recomputed:
                reasons.append("meta.response_sha256_observed != sha256(raw.response utf8)")
            if txt_info["logical_sha256"] is None:
                reasons.append("success claimed but txt absent/unreadable")
            elif txt_info["logical_sha256"] != recomputed:
                reasons.append("txt logical sha (crlf-normalized) != raw.response sha")
            elif obs is not None and txt_info["logical_sha256"] != obs:
                reasons.append("txt logical sha != meta observed sha")
            if rep != raw_meta.get("response_sha256"):
                reasons.append("meta.reported sha != raw.metadata.response_sha256")
            if obs is not None and rep is not None and obs != rep:
                reasons.append("observed sha != reported sha")
            if raw_meta.get("model") != exp_full:
                reasons.append(f"raw.metadata.model {raw_meta.get('model')!r} != {exp_full}")
            if raw_meta.get("thinking_effort") != "max":
                reasons.append("raw.metadata.thinking_effort != max")
            if raw_obj is not None and raw_obj.get("completed") is not True:
                reasons.append("raw.completed is not True")
            if not session_handle:
                reasons.append("raw.metadata.session_handle absent")
            if meta.get("new_session") is not True:
                reasons.append("meta.new_session is not True")
            if isinstance(meta.get("response_chars"), int) and isinstance(response, str):
                if meta["response_chars"] != len(response):
                    reasons.append(f"meta.response_chars {meta['response_chars']} != len(response) {len(response)}")
        if raw_empty:
            reasons.append("success claimed but raw.json empty (0 bytes)")
    transport_valid = (len(reasons) == 0) and is_success_claim
    if transport_valid:
        final_class = "transport_valid_success"
    elif status == "success":
        final_class = "success_claimed_transport_invalid"
        if not reasons:
            reasons.append("success claimed but transport checks inconclusive")
    elif status == "confirmed_pre_submit_failure":
        if txt_p.exists() and txt_p.stat().st_size > 0:
            final_class = "anomaly_txt_on_failure"
            reasons.append("failure state carries non-empty success txt")
        else:
            final_class = "confirmed_pre_submit_failure"
    elif status == "failure_or_ambiguous":
        final_class = "ambiguous_failure"
    elif not meta_p.exists():
        final_class = "missing"
    else:
        final_class = f"other_failure:{status}"
    schema_parse_ok = None
    schema_note = None
    source_valid = None
    source_failures = []
    if txt_p.exists() and txt_p.stat().st_size > 0 and final_class in ("transport_valid_success", "success_claimed_transport_invalid"):
        try:
            text = txt_p.read_text(encoding="utf-8")
            obj = json.loads(text)
            schema_parse_ok = True
        except Exception as e:  # noqa: BLE001
            schema_parse_ok = False
            schema_note = f"{type(e).__name__}: {str(e)[:160]}"
            obj = None
        if schema_parse_ok:
            ok, fails = check_source_payload(data_root, job, obj)
            source_valid = ok
            source_failures = fails
    rec.update({
        "meta_status": status, "meta_phase": meta.get("phase"),
        "transport_valid": transport_valid, "transport_reasons": reasons,
        "final_class": final_class,
        "prompt_ok": prompt_ok, "pilot_imported": pilot,
        "pilot_source": meta.get("imported_from_pilot"),
        "model_requested": meta.get("model_requested"), "model_reported": meta.get("model_reported"),
        "thinking_effort": meta.get("thinking_effort"),
        "completed": completed, "exit_code": exit_code,
        "elapsed_seconds": meta.get("elapsed_seconds"), "utc_start": meta.get("utc_start"),
        "response_sha256_observed": obs, "response_sha256_reported": rep,
        "txt": txt_info, "raw_bytes": raw_sz,
        "session_handle": session_handle,
        "schema_parse_ok": schema_parse_ok, "schema_note": schema_note,
        "source_valid": source_valid, "source_failures": source_failures,
    })
    return rec


def check_source_payload(data_root: Path, job: dict, obj):
    fails = []
    try:
        track = job.get("track")
        if track == "A_E5":
            if not isinstance(obj, dict):
                return False, ["not a dict"]
            if obj.get("batch_id") != job["job_id"]:
                fails.append("batch_id mismatch")
            revs = obj.get("reviews")
            if not isinstance(revs, list) or len(revs) != 6:
                fails.append("reviews length != 6")
                return False, fails
            if [v.get("blind_id") for v in revs] != job.get("cases"):
                fails.append("blind_id order != manifest cases")
            raw_src = (data_root / f"inputs/e5/{job['job_id']}_source.txt").read_text(encoding="utf-8")
            for v in revs:
                if v.get("verdict") not in ALLOWED_A:
                    fails.append(f"bad verdict {v.get('verdict')!r}")
                ev = v.get("evidence")
                if not isinstance(ev, list) or not ev:
                    fails.append(f"{v.get('blind_id')}: empty evidence")
                    continue
                for q in ev:
                    if not isinstance(q.get("item_number"), int) or q["item_number"] <= 0:
                        fails.append(f"{v.get('blind_id')}: bad item_number")
                    if q.get("quote") not in raw_src:
                        fails.append(f"{v.get('blind_id')}: quote not in source")
            return (len(fails) == 0), fails
        elif track == "B_RELATION":
            k = job["k"]
            original = json.loads((data_root / f"inputs/op60/B_k{k:02d}.json").read_text(encoding="utf-8"))
            ids = [v["id"] for name in ("thread_hypotheses", "why_hypotheses", "mech_hypotheses") for v in original[name]]
            if obj.get("station_k") != k or obj.get("task") != "B":
                fails.append("station_k/task mismatch")
            revs = obj.get("reviews") or []
            if len(revs) != len(ids) or set(r.get("hypothesis_id") for r in revs) != set(ids):
                fails.append("hypothesis id set mismatch")
            for r in revs:
                if r.get("verdict") not in ALLOWED_B:
                    fails.append(f"bad verdict {r.get('verdict')!r}")
            return (len(fails) == 0), fails
        elif track == "C_E7":
            k = job["k"]
            original = json.loads((data_root / f"inputs/op60/C_k{k:02d}.json").read_text(encoding="utf-8"))
            if obj.get("station_k") != k or obj.get("task") != "C":
                fails.append("station_k/task mismatch")
            if obj.get("action") not in ALLOWED_C:
                fails.append(f"bad action {obj.get('action')!r}")
                return False, fails
            previous = {v["id"]: v["text"] for v in original["screen_before"]}
            candidates = {v["id"] for v in original["current_candidates"]}
            keeps = obj.get("keep_ids") or []
            retires = obj.get("retire_ids") or []
            if len(keeps) != len(set(keeps)) or len(retires) != len(set(retires)):
                fails.append("keep/retire dup")
            if not set(keeps).isdisjoint(set(retires)):
                fails.append("keep/retire overlap")
            if set(keeps) | set(retires) != set(previous):
                fails.append("keep|retire != previous set")
            for x in obj.get("new_screen_items") or []:
                if not (x.get("text") and x.get("source_ids") and set(x["source_ids"]) <= candidates):
                    fails.append("bad new_screen_item")
            if set(obj.get("expand_ids") or []) - candidates:
                fails.append("expand_ids outside candidates")
            if set(obj.get("recap_ids") or []) - candidates:
                fails.append("recap_ids outside candidates")
            expect = [previous[v["id"]] for v in original["screen_before"] if v["id"] in keeps] + [x["text"] for x in obj.get("new_screen_items") or []]
            if obj.get("final_screen_text") != expect:
                fails.append("final_screen_text recompute mismatch")
            if obj.get("action") == "KEEP" and (obj.get("new_screen_items") or retires):
                fails.append("KEEP with new items/retires")
            if obj.get("action") == "SILENCE" and (keeps or obj.get("new_screen_items")):
                fails.append("SILENCE with keeps/new items")
            return (len(fails) == 0), fails
        return None, ["unknown track"]
    except FileNotFoundError as e:
        return None, [f"source input absent: {e.filename}"]
    except Exception as e:  # noqa: BLE001
        return False, [f"{type(e).__name__}: {str(e)[:160]}"]


# ---------------- review slot v2：transport + 完整 schema ----------------

def check_review_slot_v2(data_root: Path, row: dict):
    """返回 (rec, session_handle)。rec 含 transport_valid 与 review_schema_*（BUG1 修复）。"""
    model = row["judge_model"]
    jid = row["job_id"]
    kind = row.get("kind")
    exp_full = MODEL_FULL[model]
    prompt_p = data_root / row["prompt_file"]
    prompt_ok = False
    prompt_note = None
    prompt_text = None
    if prompt_p.exists():
        try:
            prompt_text = prompt_p.read_text(encoding="utf-8")
            prompt_ok = sha_bytes(prompt_p.read_bytes()) == row.get("prompt_sha256")
        except Exception as e:  # noqa: BLE001
            prompt_note = f"prompt unreadable: {type(e).__name__}"
        if prompt_text is not None and not prompt_ok:
            prompt_note = "on-disk prompt bytes (must be LF, newline='\\n') != manifest sha"
    else:
        prompt_note = "prompt file absent"
    d = data_root / "results" / "reviews" / model
    meta_p = d / f"{jid}.meta.json"
    raw_p = d / f"{jid}.raw.json"
    txt_p = d / f"{jid}.txt"
    attempts = sorted([f.name for f in d.glob(f"{jid}.attempt*")]) if d.is_dir() else []
    rec = {"area": "review", "job": jid, "kind": kind, "model": model,
           "files": {"meta": meta_p.exists(), "raw": raw_p.exists(), "txt": txt_p.exists(),
                     "attempt_files": attempts},
           "prompt_ok": prompt_ok, "prompt_note": prompt_note,
           "review_schema_ok": None, "review_schema_failures": []}
    if not meta_p.exists():
        rec.update({"final_class": "missing", "transport_valid": False,
                    "transport_reasons": ["final meta absent"], "schema_parse_ok": None})
        return rec, None
    meta, meta_err = load_json(meta_p)
    if meta is None or not isinstance(meta, dict):
        rec.update({"final_class": "other_failure", "transport_valid": False,
                    "transport_reasons": [f"meta unparseable: {meta_err}"], "schema_parse_ok": None})
        return rec, None
    reasons = []
    if meta.get("model_requested") != exp_full:
        reasons.append(f"model_requested {meta.get('model_requested')!r} != {exp_full}")
    if meta.get("model_reported") != exp_full:
        reasons.append(f"model_reported {meta.get('model_reported')!r} != {exp_full}")
    if meta.get("thinking_effort") != "max":
        reasons.append("thinking_effort != max")
    if meta.get("prompt_sha256") != row.get("prompt_sha256"):
        reasons.append("meta.prompt_sha256 != review_manifest sha")
    if not prompt_ok:
        reasons.append(prompt_note or "prompt bytes mismatch")
    raw_obj = None
    raw_meta = {}
    response = None
    session_handle = None
    if raw_p.exists() and raw_p.stat().st_size > 0:
        try:
            raw_obj = json.loads(raw_p.read_text(encoding="utf-8"))
            raw_meta = raw_obj.get("metadata") or {}
            response = raw_obj.get("response")
            for k in ("session_handle", "session_id", "conversation_id"):
                if raw_meta.get(k):
                    session_handle = raw_meta.get(k)
                    break
        except Exception as e:  # noqa: BLE001
            reasons.append(f"raw.json unparseable: {type(e).__name__}")
    else:
        reasons.append("raw.json absent/empty")
    status = meta.get("status")
    completed = meta.get("completed")
    exit_code = meta.get("exit_code")
    pilot = bool(meta.get("imported_from_pilot"))
    is_claim = (status == "success" and completed is True and exit_code == 0)
    obs = meta.get("response_sha256_observed")
    rep = meta.get("response_sha256_reported")
    txt_info = {"exists": txt_p.exists(), "archive_byte_sha256": None,
                "logical_sha256": None, "matches_observed": None, "newline_variant": None}
    if txt_p.exists():
        try:
            disk = txt_p.read_bytes()
            txt_info["archive_byte_sha256"] = sha_bytes(disk)
            txt_info["newline_variant"] = "crlf" if b"\r\n" in disk else ("lf" if b"\n" in disk else "none")
            txt_info["logical_sha256"] = sha_bytes(disk.replace(b"\r\n", b"\n"))
        except Exception as e:  # noqa: BLE001
            reasons.append(f"txt unreadable: {type(e).__name__}")
    if is_claim:
        if not isinstance(response, str) or not response.strip():
            reasons.append("success claimed but raw.response empty")
        else:
            recomputed = sha_bytes(response.encode("utf-8"))
            if obs != recomputed:
                reasons.append("observed != sha256(raw.response utf8)")
            if txt_info["logical_sha256"] is None:
                reasons.append("txt absent for success")
            elif txt_info["logical_sha256"] != recomputed:
                reasons.append("txt logical sha != raw.response sha")
            if rep != raw_meta.get("response_sha256"):
                reasons.append("reported != raw.metadata.response_sha256")
            if obs is not None and rep is not None and obs != rep:
                reasons.append("observed != reported")
            if raw_meta.get("model") != exp_full:
                reasons.append("raw.metadata.model mismatch")
            if raw_meta.get("thinking_effort") != "max":
                reasons.append("raw.metadata effort != max")
            if raw_obj is not None and raw_obj.get("completed") is not True:
                reasons.append("raw.completed not True")
            if not session_handle:
                reasons.append("session_handle absent")
    transport_valid = (len(reasons) == 0) and is_claim
    if transport_valid:
        final_class = "transport_valid_success"
    elif status == "success":
        final_class = "success_claimed_transport_invalid"
    elif status == "confirmed_pre_submit_failure":
        final_class = "confirmed_pre_submit_failure"
    elif status == "failure_or_ambiguous":
        final_class = "ambiguous_failure"
    else:
        final_class = f"other_failure:{status}"
    # ---- v2 完整 review schema（仅对有非空 txt 的 success 类终态做内容结构检查）----
    schema_parse_ok = None
    schema_note = None
    schema_failures: list[str] = []
    payload_obj = None
    if txt_p.exists() and txt_p.stat().st_size > 0 and final_class in ("transport_valid_success", "success_claimed_transport_invalid"):
        try:
            payload_obj = json.loads(txt_p.read_text(encoding="utf-8"))
            schema_parse_ok = True
        except Exception as e:  # noqa: BLE001
            schema_parse_ok = False
            schema_note = f"{type(e).__name__}: {str(e)[:160]}"
            schema_failures.append(f"payload unparseable: {schema_note}")
    if schema_parse_ok and isinstance(payload_obj, dict):
        smap = review_input_source_map(data_root, kind, row)
        if kind in ("D", "G"):
            schema_failures.extend(check_dg_schema(payload_obj, kind, row, prompt_text, smap))
        elif kind == "F":
            schema_failures.extend(check_f_schema(payload_obj, row, prompt_text, smap))
        else:
            schema_failures.append(f"unknown review kind {kind!r}")
    # 空单元无文本稿合法：failures 仅一条 empty_units_silent_ok 时视为 ok（结构标注，不判 fail）
    if schema_parse_ok and schema_failures == ["empty_units_silent_ok (no-text draft: units empty, per_trial refs empty, late empty)"]:
        schema_failures = []
        rec["empty_units_silent"] = True
    review_schema_ok = (len(schema_failures) == 0) if schema_parse_ok else None
    if schema_parse_ok is False:
        review_schema_ok = False
    rec.update({"meta_status": status, "transport_valid": transport_valid, "transport_reasons": reasons,
                "final_class": final_class, "session_handle": session_handle,
                "pilot_imported": pilot,
                "utc_start": meta.get("utc_start"), "elapsed_seconds": meta.get("elapsed_seconds"),
                "response_sha256_observed": obs, "schema_parse_ok": schema_parse_ok, "schema_note": schema_note,
                "review_schema_ok": review_schema_ok, "review_schema_failures": schema_failures,
                "txt": txt_info, "station_k": row.get("station_k")})
    return rec, session_handle


def check_dg_schema(obj: dict, kind: str, row: dict, prompt_text: str | None,
                    source_map: dict[str, str] | None = None) -> list[str]:
    """D/G 完整结构校验。quote 规则（v2.1）：

    - A/B/PREVIOUS：prompt 内逐字存在即可（present_in_prompt）；稿件自引不证落源。
    - 其余 source_id：必须落在冻结 input 源片段内（source_map），且在 prompt 内逐字；
      只在某匿名稿出现、不在源片段的记 non_source_quote（quote 能来自模型稿不是 source）。
    - source_id 未知（不在 {源 ids}∪{A,B,PREVIOUS}）记 unknown_source_id。
    - input 缺失（source_map 为空）记 input_absent，不判 fail。
    """
    fails: list[str] = []
    if obj.get("task") != kind:
        fails.append(f"task field {obj.get('task')!r} != {kind}")
    if obj.get("station_k") != row.get("station_k"):
        fails.append(f"station_k {obj.get('station_k')!r} != manifest {row.get('station_k')!r}")
    if obj.get("winner") not in DG_WINNER:
        fails.append(f"winner {obj.get('winner')!r} not in {sorted(DG_WINNER)}")
    rd = obj.get("reasoned_decision")
    if not isinstance(rd, str) or len(CJK_RE.findall(rd)) < 100:
        got = len(CJK_RE.findall(rd)) if isinstance(rd, str) else 0
        fails.append(f"reasoned_decision CJK chars {got} < 100")

    def check_quote_list(evs, field: str):
        if not isinstance(evs, list) or not evs:
            fails.append(f"{field} empty/absent")
            return
        if prompt_text is None:
            fails.append(f"{field}: prompt unreadable, quote check skipped")
            return
        no_source = source_map is None or len(source_map) == 0
        for i, e in enumerate(evs):
            q = e.get("excerpt" if field == "quoted_evidence" else "quote") if isinstance(e, dict) else None
            sid = e.get("source_id") if isinstance(e, dict) else None
            if not sid:
                fails.append(f"{field}[{i}] missing source_id")
                continue
            if not q:
                fails.append(f"{field}[{i}] empty {'excerpt' if field == 'quoted_evidence' else 'quote'}")
                continue
            if sid in ("A", "B", "PREVIOUS"):
                if q not in prompt_text:
                    fails.append(f"{field}[{i}] {sid} quote not verbatim in prompt")
                continue
            if no_source:
                fails.append(f"{field}[{i}] {sid}: input_absent (source map unavailable)")
                continue
            if sid not in source_map:
                fails.append(f"{field}[{i}] unknown_source_id {sid!r}")
                continue
            if q not in source_map[sid]:
                fails.append(f"{field}[{i}] {sid}: non_source_quote (not in frozen input fragment)")
            if q not in prompt_text:
                fails.append(f"{field}[{i}] {sid}: quote not verbatim in prompt")

    if kind == "D":
        if obj.get("A_source_supported") not in D_SUPPORT:
            fails.append(f"A_source_supported {obj.get('A_source_supported')!r} not in {sorted(D_SUPPORT)}")
        if obj.get("B_source_supported") not in D_SUPPORT:
            fails.append(f"B_source_supported {obj.get('B_source_supported')!r} not in {sorted(D_SUPPORT)}")
        check_quote_list(obj.get("quoted_evidence"), "quoted_evidence")
    else:  # G
        for f in ("A_unique_gain", "B_unique_gain", "A_unjustified", "B_unjustified"):
            if f not in obj:
                fails.append(f"missing field {f}")
        check_quote_list(obj.get("source_quotes"), "source_quotes")
    return fails


def check_f_schema(obj: dict, row: dict, prompt_text: str | None,
                 source_map: dict[str, str] | None = None) -> list[str]:
    """F 完整结构校验（v2.1）：

    - 空 semantic_units 在无文本稿可合法：仅当 per_trial 全轮 distinct/repeats/
      unsupported 三类引用全集为空、且 late 为空时放行（记 empty_units_silent_ok），
      否则 fail。
    - unit 引用全集：per_trial 三类 id 必须 ⊆ unit_id 全集，未知引用记 unknown_unit_ref。
    - late 一致性：late_round_new_valuable_unit_ids ⊆ 全集；其中 status 须为
      grounded_valuable；其 first_seen 须落在 late 轮（T4 起；sample_count>8 时 T6 起），
      否则记 late_consistency_fail（机械检查，不评价值）。
    - quote 源映射同 D/G：源 id 必须落冻结 input 片段；T 稿自引记 non_source_quote。
    """
    fails: list[str] = []
    if obj.get("task") != "F":
        fails.append(f"task field {obj.get('task')!r} != F")
    if obj.get("station_k") != row.get("station_k"):
        fails.append(f"station_k {obj.get('station_k')!r} != manifest {row.get('station_k')!r}")
    expect_n = None
    if prompt_text is not None:
        m = SAMPLE_RE.search(prompt_text)
        if m:
            expect_n = int(m.group(1))
    sc = obj.get("sample_count")
    if expect_n is not None and sc != expect_n:
        fails.append(f"sample_count {sc!r} != prompt sample_count {expect_n}")
    n = sc if isinstance(sc, int) and sc > 0 else (expect_n or 0)
    units = obj.get("semantic_units")
    trials = obj.get("per_trial")
    late = obj.get("late_round_new_valuable_unit_ids") or []
    per_refs: set = set()
    if isinstance(trials, list):
        for t in trials:
            if not isinstance(t, dict):
                continue
            for k in ("distinct_valid_new_unit_ids", "repeats_existing_unit_ids",
                      "unsupported_or_language_only_unit_ids"):
                for u in t.get(k) or []:
                    per_refs.add(u)
    if not isinstance(units, list) or not units:
        if isinstance(trials, list) and not per_refs and not late:
            fails.append("empty_units_silent_ok (no-text draft: units empty, per_trial refs empty, late empty)")
        else:
            fails.append("semantic_units empty/absent with non-empty per_trial refs or late ids")
        units = []
    seen_ids: set = set()
    unit_status: dict = {}
    unit_first: dict = {}
    for i, u in enumerate(units):
        if not isinstance(u, dict):
            fails.append(f"semantic_units[{i}] not a dict")
            continue
        uid = u.get("unit_id")
        if not uid:
            fails.append(f"semantic_units[{i}] missing unit_id")
        elif uid in seen_ids:
            fails.append(f"duplicate unit_id {uid!r}")
        else:
            seen_ids.add(uid)
        unit_status[uid] = u.get("status")
        unit_first[uid] = u.get("first_seen")
        if u.get("status") not in F_STATUS:
            fails.append(f"{uid or i}: status {u.get('status')!r} not in {sorted(F_STATUS)}")
        evs = u.get("source_evidence")
        if not isinstance(evs, list) or not evs:
            fails.append(f"{uid or i}: source_evidence empty/absent")
        elif prompt_text is not None:
            no_source = source_map is None or len(source_map) == 0
            for j, e in enumerate(evs):
                q = e.get("quote") if isinstance(e, dict) else None
                sid = e.get("source_id") if isinstance(e, dict) else None
                if not sid:
                    fails.append(f"{uid or i}: source_evidence[{j}] missing source_id")
                    continue
                if not q:
                    fails.append(f"{uid or i}: source_evidence[{j}] empty quote")
                    continue
                if no_source:
                    fails.append(f"{uid or i}: {sid}: input_absent (source map unavailable)")
                    continue
                if sid not in source_map:
                    fails.append(f"{uid or i}: unknown_source_id {sid!r}")
                    continue
                if q not in source_map[sid]:
                    fails.append(f"{uid or i}: {sid}: non_source_quote (not in frozen input fragment)")
                if q not in prompt_text:
                    fails.append(f"{uid or i}: {sid}: quote not verbatim in prompt")
        fs = u.get("first_seen")
        si = u.get("seen_in")
        if not isinstance(si, list) or fs not in si:
            fails.append(f"{uid or i}: first_seen {fs!r} not in seen_in {si!r}")
    # per_trial 引用全集 ⊆ unit 全集
    for ref in sorted(per_refs):
        if ref not in seen_ids:
            fails.append(f"unknown_unit_ref {ref!r} (per_trial refs id not in semantic_units)")
    if n > 0:
        expect_trials = [f"T{i}" for i in range(1, n + 1)]
        got_trials = [t.get("trial") for t in trials] if isinstance(trials, list) else None
        if got_trials != expect_trials:
            fails.append(f"per_trial trials {got_trials!r} != expected {expect_trials!r}")
    else:
        if not isinstance(trials, list) or not trials:
            fails.append("per_trial empty/absent")
    # late 一致性（机械）：late ⊆ 全集；status 须 grounded_valuable；first_seen 须 late 轮
    late_start = 6 if n > 8 else 4
    for lid in late:
        if lid not in seen_ids:
            fails.append(f"late id {lid!r} not in semantic_units")
            continue
        if unit_status.get(lid) != "grounded_valuable":
            fails.append(f"late_consistency_fail {lid}: status {unit_status.get(lid)!r} != grounded_valuable")
        fs = unit_first.get(lid)
        try:
            fs_n = int(str(fs).lstrip("T"))
        except Exception:  # noqa: BLE001
            fails.append(f"late_consistency_fail {lid}: first_seen {fs!r} unparseable")
            continue
        if fs_n < late_start:
            fails.append(f"late_consistency_fail {lid}: first_seen {fs!r} before late window T{late_start}+")
    valid_trials = {f"T{i}" for i in range(1, n + 1)} if n > 0 else None
    bc = obj.get("best_trial_candidate")
    if valid_trials is not None:
        if bc not in (valid_trials | {"NONE"}):
            fails.append(f"best_trial_candidate {bc!r} not in {sorted(valid_trials | {'NONE'})}")
    elif bc not in ("NONE", None):
        fails.append(f"best_trial_candidate {bc!r} unexpected without sample_count")
    if obj.get("saturation_assessment") not in F_SAT:
        fails.append(f"saturation_assessment {obj.get('saturation_assessment')!r} not in {sorted(F_SAT)}")
    if obj.get("recommend_more") not in F_REC:
        fails.append(f"recommend_more {obj.get('recommend_more')!r} not in {sorted(F_REC)}")
    return fails


# ---------------- supplemented payload 的 schema/source（与 canonical 同规则） ----------------

def check_supplement_payload(data_root: Path, manifest_jobs: dict, kind_area: str, job_id: str, text: str):
    """返回 (schema_parse_ok, schema_note, source_valid, source_failures)。原文不修（如非法控制字符如实 fail）。"""
    try:
        obj = json.loads(text)
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {str(e)[:160]}", None, []
    if kind_area == "trial":
        job = manifest_jobs.get(job_id)
        if job is None:
            return True, None, None, ["manifest job absent"]
        ok, fails = check_source_payload(data_root, job, obj)
        return True, None, ok, fails
    return True, None, None, ["review supplement source check: not applicable (schema only)"]


# ---------------- 主流程 ----------------

def main():
    ap = argparse.ArgumentParser(description="独立交付验收验证 v2（只读，不调用模型）")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--report-dir", default=None)
    ap.add_argument("--supplement-dir", default=None, help="补充恢复证据目录（含 SUPPLEMENTAL_*.txt + .meta.json）")
    ap.add_argument("--owned-runs-dir", default=None, help="owned job 池（只读 started/result/submitted/response 四类证据）")
    ap.add_argument("--scheduler-events", default=None, help="pipeline events.jsonl（scheduler 事件区间估计；v3 将补 proc_started→process_exit）")
    ap.add_argument("--review-manifest", default=None, help="可选：扩样后的新 review manifest（默认 data-root 内冻结旧版）")
    ap.add_argument("--review-mapping", default=None,
                    help="可选 JSON：{review_job_id: {input: inputs/op60/C_kNN.json, kind}}，覆盖默认 input 映射")
    ap.add_argument("--expected-base-transport", type=int, default=None, help="覆盖默认 146")
    ap.add_argument("--expected-base-source", type=int, default=None, help="覆盖默认 145")
    ap.add_argument("--baseline-snapshot", default=None,
                    help="可选：旧证据基线 snapshot JSON（含 frozen meta byte SHA）；canonical_untouched 按字节比对")
    a = ap.parse_args()
    data_root = Path(a.data_root)
    trusted = Path(__file__).resolve().parent
    report_dir = Path(a.report_dir) if a.report_dir else trusted / "v2_report_20261010"
    if not data_root.is_dir():
        print(f"ERROR: --data-root 不存在: {data_root}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads((data_root / "jobs/manifest.json").read_text(encoding="utf-8"))
        plan = json.loads((data_root / "jobs/repetition_plan.json").read_text(encoding="utf-8"))
        rman_path = Path(a.review_manifest) if a.review_manifest else (data_root / "jobs/reviews/review_manifest.json")
        reviews = json.loads(rman_path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: 冻结 manifest 读取失败: {type(e).__name__} {e}", file=sys.stderr)
        return 2
    review_mapping: dict = {}
    if a.review_mapping:
        try:
            review_mapping = json.loads(Path(a.review_mapping).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: --review-mapping 读取失败: {type(e).__name__} {e}", file=sys.stderr)
            return 2
    exp_transport = a.expected_base_transport if a.expected_base_transport is not None else DEFAULT_BASE_TRANSPORT
    exp_source = a.expected_base_source if a.expected_base_source is not None else DEFAULT_BASE_SOURCE_VALID
    baseline_snapshot: dict = {}
    if a.baseline_snapshot:
        try:
            baseline_snapshot = json.loads(Path(a.baseline_snapshot).read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: --baseline-snapshot 读取失败: {type(e).__name__} {e}", file=sys.stderr)
            return 2
    manifest_jobs = {j["job_id"]: j for j in manifest["jobs"]}

    prompt_state = {}
    for j in manifest["jobs"]:
        ok6 = ok56 = False
        try:
            b6 = (data_root / j["model_prompt_paths"]["gpt6w"]).read_bytes()
            b56 = (data_root / j["model_prompt_paths"]["gpt56w"]).read_bytes()
            ok6 = sha_bytes(b6) == j["input_sha256"]
            ok56 = sha_bytes(b56) == j["input_sha256"]
        except Exception:  # noqa: BLE001
            pass
        same = False
        try:
            same = (data_root / j["model_prompt_paths"]["gpt6w"]).read_bytes() == (data_root / j["model_prompt_paths"]["gpt56w"]).read_bytes()
        except Exception:  # noqa: BLE001
            pass
        prompt_state[j["job_id"]] = {"gpt6w_ok": ok6, "gpt56w_ok": ok56, "pair_identical": same,
                                     "ok": ok6 and ok56 and same}

    trial_details = []
    for j in manifest["jobs"]:
        for model in ("gpt6w", "gpt56w"):
            try:
                pb = (data_root / j["model_prompt_paths"][model]).read_bytes()
            except Exception:  # noqa: BLE001
                pb = b""
            pok = sha_bytes(pb) == j["input_sha256"] if pb else False
            for rnd in ALL_ROUNDS:
                trial_details.append(check_trial_slot(data_root, j, model, rnd, pb, pok))
    review_details = []
    for row in reviews["jobs"]:
        rec, _ = check_review_slot_v2(data_root, row)
        review_details.append(rec)

    # ---- session 唯一性 v2（BUG2：pilot 碰撞也要抓）----
    handle_map: dict[str, list[dict]] = collections.defaultdict(list)
    for rec in trial_details + review_details:
        h = rec.get("session_handle")
        if not h:
            continue
        label = f"{rec['area']}:{rec['job']}:{rec.get('model')}:r{rec.get('round', '-')}"
        handle_map[h].append({"slot": label, "pilot": bool(rec.get("pilot_imported"))})
    session_reuse_non_pilot = []
    pilot_session_exceptions = []
    pilot_collision_with_current = []
    for h, slots in handle_map.items():
        if len(slots) < 2:
            continue
        pilots = [s for s in slots if s["pilot"]]
        currents = [s for s in slots if not s["pilot"]]
        if currents and pilots:
            pilot_collision_with_current.append({"handle": h, "slots": slots})
        elif currents:
            session_reuse_non_pilot.append({"handle": h, "slots": [s["slot"] for s in currents]})
        else:
            pilot_session_exceptions.append({"handle": h, "slots": [s["slot"] for s in pilots]})

    # ---- BASE 计数 + pilot 敏感性两版 ----
    base = [r for r in trial_details if r.get("round") in BASE_ROUNDS]

    def cnt(rs, pred):
        return sum(1 for r in rs if pred(r))

    def base_count_block(rs):
        return {
            "slots": len(rs),
            "transport_valid_success": cnt(rs, lambda r: r["final_class"] == "transport_valid_success"),
            "success_claimed_transport_invalid": cnt(rs, lambda r: r["final_class"] == "success_claimed_transport_invalid"),
            "confirmed_pre_submit_failure": cnt(rs, lambda r: r["final_class"] == "confirmed_pre_submit_failure"),
            "ambiguous_failure": cnt(rs, lambda r: r["final_class"] == "ambiguous_failure"),
            "missing": cnt(rs, lambda r: r["final_class"] == "missing"),
            "other": cnt(rs, lambda r: r["final_class"] not in ("transport_valid_success", "success_claimed_transport_invalid",
                                                                "confirmed_pre_submit_failure", "ambiguous_failure", "missing")),
        }

    base_counts = base_count_block(base)
    base_nopilot = [r for r in base if not r.get("pilot_imported")]
    base_counts_excl_pilot = base_count_block(base_nopilot)
    valid_recs = [r for r in base if r["final_class"] == "transport_valid_success"]
    base_counts["schema_parse_ok_among_valid"] = sum(1 for r in valid_recs if r.get("schema_parse_ok") is True)
    base_counts["schema_parse_fail_among_valid"] = sum(1 for r in valid_recs if r.get("schema_parse_ok") is False)
    base_counts["source_valid_among_valid"] = sum(1 for r in valid_recs if r.get("source_valid") is True)
    base_counts["source_invalid_among_valid"] = sum(1 for r in valid_recs if r.get("source_valid") is False)
    base_counts["schema_fail_slots"] = [
        f"{r['area']}:{r['job']}:{r['model']}:r{r['round']:02d}:{r.get('schema_note')}" for r in valid_recs if r.get("schema_parse_ok") is False]

    # ---- r06+ 配对缺口 ----
    gaps = []
    for j in manifest["jobs"]:
        for rnd in range(6, 13):
            got = {}
            for model in ("gpt6w", "gpt56w"):
                r = next(x for x in trial_details if x["job"] == j["job_id"] and x["model"] == model and x["round"] == rnd)
                got[model] = "valid" if r["final_class"] == "transport_valid_success" else r["final_class"]
            if got["gpt6w"] != got["gpt56w"]:
                if "valid" in (got["gpt6w"], got["gpt56w"]):
                    gaps.append({"job": j["job_id"], "round": rnd, **got, "kind": "pairing_gap_r06plus"})

    # ---- 评审计数 v2（含 review_schema 分层）----
    rc = collections.Counter(r["final_class"] for r in review_details)
    rk = collections.Counter(r.get("kind") for r in review_details)
    valid_reviews = [r for r in review_details if r["final_class"] == "transport_valid_success"]
    review_counts = {
        "total_manifest": len(reviews["jobs"]), "by_kind": dict(rk), "by_class": dict(rc),
        "transport_valid_success": len(valid_reviews),
        "review_schema_ok_among_valid": sum(1 for r in valid_reviews if r.get("review_schema_ok") is True),
        "review_schema_fail_among_valid": sum(1 for r in valid_reviews if r.get("review_schema_ok") is False),
        "review_schema_fail_slots": [
            {"slot": f"{r['job']}:{r['model']}", "failures": r.get("review_schema_failures")}
            for r in valid_reviews if r.get("review_schema_ok") is False],
        "review_winner_distribution": {},
        "review_recommend_distribution": {},
    }
    for kind in ("D", "G"):
        dist = collections.Counter()
        for r in valid_reviews:
            if r.get("kind") != kind:
                continue
            try:
                o = json.loads((data_root / "results" / "reviews" / r["model"] / (r["job"] + ".txt")).read_text(encoding="utf-8"))
                dist[str(o.get("winner"))] += 1
            except Exception:  # noqa: BLE001
                dist["UNREADABLE"] += 1
        review_counts["review_winner_distribution"][kind] = dict(dist)
    fdist = collections.Counter()
    for r in valid_reviews:
        if r.get("kind") != "F":
            continue
        try:
            o = json.loads((data_root / "results" / "reviews" / r["model"] / (r["job"] + ".txt")).read_text(encoding="utf-8"))
            fdist[str(o.get("recommend_more"))] += 1
        except Exception:  # noqa: BLE001
            fdist["UNREADABLE"] += 1
    review_counts["review_recommend_distribution"] = dict(fdist)

    # ---- AB/BA 一致性 ----
    ab_pairs: dict[str, dict] = {}
    for r in review_details:
        m = re.match(r"^(.*)_(AB|BA)$", r["job"])
        if not m:
            continue
        stem, side = m.group(1), m.group(2)
        ab_pairs.setdefault(f"{r['kind']}:{r['model']}:{stem}", {})[side] = r
    ab_agreement = {"comparable": 0, "agree": 0, "disagree": [], "uncomparable": 0}
    for stem, sides in ab_pairs.items():
        if "AB" not in sides or "BA" not in sides:
            ab_agreement["uncomparable"] += 1
            continue
        rec_ab, rec_ba = sides["AB"], sides["BA"]
        if rec_ab["final_class"] != "transport_valid_success" or rec_ba["final_class"] != "transport_valid_success":
            ab_agreement["uncomparable"] += 1
            continue
        try:
            oa = json.loads((data_root / "results" / "reviews" / rec_ab["model"] / (rec_ab["job"] + ".txt")).read_text(encoding="utf-8"))
            ob = json.loads((data_root / "results" / "reviews" / rec_ba["model"] / (rec_ba["job"] + ".txt")).read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            ab_agreement["uncomparable"] += 1
            continue
        ab_agreement["comparable"] += 1
        # AB/BA 是同一对稿的顺序互换：AB 槽 winner=A ⟺ BA 槽 winner=B 才表示同一稿获胜。
        # 直接比标签（A vs B）是伪不一致；按“首位稿/次位稿”归一后再比。
        def norm_win(side: str, w):
            # AB 槽：A=首位稿，B=次位稿；BA 槽：B=首位稿，A=次位稿
            if side == "AB":
                return {"A": "FIRST", "B": "SECOND"}.get(w, w)
            return {"B": "FIRST", "A": "SECOND"}.get(w, w)
        if norm_win("AB", oa.get("winner")) == norm_win("BA", ob.get("winner")):
            ab_agreement["agree"] += 1
        else:
            ab_agreement["disagree"].append({"pair": stem, "AB_winner": oa.get("winner"), "BA_winner": ob.get("winner"),
                                             "note": "normalized by presentation order (AB:A==BA:B means same draft wins)"})

    # ---- 自评敏感性（D：生成与评审同模型；G：按评审模型分别展示）----
    def d_is_self_review(job_id: str) -> bool:
        mg = re.search(r"gen(gpt6w|gpt56w)_judge(gpt6w|gpt56w)", job_id)
        return bool(mg) and mg.group(1) == mg.group(2)

    d_valid = [r for r in valid_reviews if r.get("kind") == "D"]
    d_self = [r for r in d_valid if d_is_self_review(r["job"])]
    d_nonself = [r for r in d_valid if not d_is_self_review(r["job"])]

    def winner_dist(rs):
        dist = collections.Counter()
        for r in rs:
            try:
                o = json.loads((data_root / "results" / "reviews" / r["model"] / (r["job"] + ".txt")).read_text(encoding="utf-8"))
                dist[str(o.get("winner"))] += 1
            except Exception:  # noqa: BLE001
                dist["UNREADABLE"] += 1
        return dict(dist)

    self_review_sensitivity = {
        "D_self_reviewed_slots": len(d_self),
        "D_non_self_slots": len(d_nonself),
        "D_winner_all": winner_dist(d_valid),
        "D_winner_excl_self": winner_dist(d_nonself),
        "G_winner_by_judge_model": {},
    }
    for jm in ("gpt6w", "gpt56w"):
        self_review_sensitivity["G_winner_by_judge_model"][jm] = winner_dist(
            [r for r in valid_reviews if r.get("kind") == "G" and r.get("model") == jm])

    # ---- 并发四层 v2（BUG3）----
    def interval_peak(recs):
        events = []
        for r in recs:
            t0 = parse_iso(r.get("utc_start"))
            el = r.get("elapsed_seconds")
            if t0 is None or not isinstance(el, (int, float)):
                continue
            t1 = t0 + datetime.timedelta(seconds=float(el))
            events.append((t0, 1, r))
            events.append((t1, -1, r))
        events.sort(key=lambda e: (e[0], -e[1]))
        cur = peak = 0
        peak_at = None
        members = []
        for t, dlt, r in events:
            cur += dlt
            if cur > peak:
                peak = cur
                peak_at = t.isoformat()
        # 回放 peak 时刻构成
        if peak_at is not None:
            pt = parse_iso(peak_at)
            for r in recs:
                t0 = parse_iso(r.get("utc_start"))
                el = r.get("elapsed_seconds")
                if t0 is None or not isinstance(el, (int, float)):
                    continue
                if t0 <= pt < t0 + datetime.timedelta(seconds=float(el)):
                    members.append(f"{r['area']}:{r['job']}:{r.get('model')}:r{r.get('round', '-')}:{r.get('final_class')}")
        return {"peak": peak, "peak_at": peak_at, "members": members}

    concurrency = {
        "meta_interval_peak_incl_pilot": interval_peak(trial_details + review_details),
        "meta_interval_peak_excl_pilot": interval_peak([r for r in trial_details + review_details if not r.get("pilot_imported")]),
        "note": ("meta 口径=终态 meta utc_start+elapsed 区间重叠；含短失败任务在途重叠，"
                 "不是 HTTP 并发；attempt 归档文件不参与在途计数（非运行区间）"),
        # v2.1：scheduler 事件区间只是 launched→result 落盘估计。launched 发生在 worker
        # 线程开始、result 在落盘后、函数实际 return 更晚，新 fut 可在不同线程快速开始；
        # max_workers=8 下事件估计峰值 9 ≠ 9 个 worker 真实活进程。不宣称活进程峰值。
        # v3 将补 proc_started→process_exit 真正在途。
        "scheduler_event_window_peak": {"assessed": False, "note": "no --scheduler-events supplied"},
        "owned_http_inflight_peak": {"assessed": False, "note": "no --owned-runs-dir supplied"},
        "owned_terminal_event_density_120s": {"assessed": False, "note": "no --owned-runs-dir supplied"},
    }
    if a.scheduler_events:
        try:
            evs = [json.loads(l) for l in Path(a.scheduler_events).read_text(encoding="utf-8").splitlines() if l.strip()]
            starts: dict[str, datetime.datetime] = {}
            intervals = []
            for e in evs:
                if e.get("type") == "launched" and e.get("task"):
                    t = parse_iso(e.get("utc"))
                    if t is not None:
                        starts[e["task"]] = t
                elif e.get("type") == "result" and e.get("task") and e["task"] in starts:
                    t = parse_iso(e.get("utc"))
                    if t is not None:
                        intervals.append((starts.pop(e["task"]), t, e["task"]))
            pts = []
            for s0, s1, task in intervals:
                pts.append((s0, 1))
                pts.append((s1, -1))
            pts.sort(key=lambda e: (e[0], -e[1]))
            cur = peak = 0
            peak_at = None
            for t, dlt in pts:
                cur += dlt
                if cur > peak:
                    peak = cur
                    peak_at = t.isoformat()
            concurrency["scheduler_event_window_peak"] = {
                "assessed": True, "peak": peak, "peak_at": peak_at,
                "paired_tasks": len(intervals),
                "basis": ("pipeline events launched.utc→result.utc 同 task 配对的事件窗口估计；"
                          "launched 早于 worker 开始、result 晚于实际结束（落盘后），max_workers=8 下"
                          "估计值 9 不等于 9 worker 真实活进程；v3 以 proc_started→process_exit 为准"),
            }
        except Exception as e:  # noqa: BLE001
            concurrency["scheduler_event_window_peak"] = {"assessed": False, "note": f"events unreadable: {type(e).__name__}"}
    if a.owned_runs_dir:
        try:
            runs = Path(a.owned_runs_dir)
            # 真正 HTTP 在途：仅 experiment 绑定 job（started.prompt_sha256 ∈ 本实验归一化
            # prompt 集），submitted.utc→result.utc 区间；无 result 保留 open（以 runs 池
            # 扫描时刻为右端，不假设结束）；无关旧 job 过滤。
            norm_prompts: set[str] = set()
            for j in manifest["jobs"]:
                for mk in ("gpt6w", "gpt56w"):
                    try:
                        norm_prompts.add(sha_bytes(norm_prompt_bytes(
                            (data_root / j["model_prompt_paths"][mk]).read_bytes())))
                    except Exception:  # noqa: BLE001
                        pass
            for row in reviews["jobs"]:
                try:
                    norm_prompts.add(sha_bytes(norm_prompt_bytes(
                        (data_root / row["prompt_file"]).read_bytes())))
                except Exception:  # noqa: BLE001
                    pass
            inflight_intervals = []
            bound_jobs = 0
            term_times = []
            scan_now = datetime.datetime.now(datetime.timezone.utc)
            for jd in runs.glob("job-*"):
                try:
                    st = json.loads((jd / "started.json").read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(st, dict) or st.get("prompt_sha256") not in norm_prompts:
                    continue  # 无关旧 job 过滤
                bound_jobs += 1
                try:
                    so = json.loads((jd / "submitted.json").read_text(encoding="utf-8"))
                    t_sub = parse_iso(so.get("utc")) if isinstance(so, dict) else None
                except Exception:  # noqa: BLE001
                    t_sub = None
                t_end = None
                term = False
                try:
                    ro = json.loads((jd / "result.json").read_text(encoding="utf-8"))
                except Exception:  # noqa: BLE001
                    ro = None
                if isinstance(ro, dict):
                    md = ro.get("metadata") or {}
                    val = md.get("prepared_response_validation") or {}
                    if ro.get("completed") is True and val.get("successful_assistant_terminal_observed") is True:
                        term = True
                        t_end = parse_iso(ro.get("utc"))
                if t_sub is not None:
                    inflight_intervals.append((t_sub, t_end if t_end is not None else scan_now,
                                               jd.name, t_end is None))
                if term and t_end is not None:
                    term_times.append(t_end)
            ipts = []
            for s0, s1, _nm, _op in inflight_intervals:
                ipts.append((s0, 1))
                ipts.append((s1, -1))
            ipts.sort(key=lambda e: (e[0], -e[1]))
            cur = hpeak = 0
            hpeak_at = None
            hmembers: list[str] = []
            for t, dlt in ipts:
                cur += dlt
                if cur > hpeak:
                    hpeak = cur
                    hpeak_at = t.isoformat()
            if hpeak_at is not None:
                pt = parse_iso(hpeak_at)
                for s0, s1, nm, op in inflight_intervals:
                    if s0 <= pt < s1:
                        hmembers.append(nm + (" (open)" if op else ""))
            # terminal 事件密度：result completed+terminal utc ±60s 窗（事件密度，不是 HTTP 在途）
            def window_peak(times, half_s=60):
                pts = []
                for t in times:
                    pts.append((t - datetime.timedelta(seconds=half_s), 1))
                    pts.append((t + datetime.timedelta(seconds=half_s), -1))
                pts.sort(key=lambda e: (e[0], -e[1]))
                cur = peak = 0
                peak_at = None
                for t, dlt in pts:
                    cur += dlt
                    if cur > peak:
                        peak = cur
                        peak_at = t.isoformat()
                return peak, peak_at

            tp, tat = window_peak(term_times)
            concurrency["owned_http_inflight_peak"] = {
                "assessed": True, "peak": hpeak, "peak_at": hpeak_at,
                "bound_experiment_jobs": bound_jobs,
                "open_intervals": sum(1 for _, _, _, op in inflight_intervals if op),
                "members": hmembers,
                "basis": ("experiment 绑定 job 的 submitted.utc→result.utc 区间重叠；"
                          "无 result 保留 open（右端=扫描时刻，不假设结束）；无关旧 job 已过滤"),
            }
            concurrency["owned_terminal_event_density_120s"] = {
                "assessed": True, "peak": tp, "peak_at": tat, "markers": len(term_times),
                "basis": "result completed+terminal utc ±60s 窗事件密度；不是 HTTP 在途",
            }
        except Exception as e:  # noqa: BLE001
            concurrency["owned_http_inflight_peak"] = {"assessed": False, "note": f"runs unreadable: {type(e).__name__}"}

    # ---- 补充恢复独立验证 v2（BUG4 + --supplement-dir）----
    recovered = {"supplement_dir": a.supplement_dir, "items": [],
                 "note": "absent: no --supplement-dir supplied" if not a.supplement_dir else
                         "supplemental only; canonical status/exit preserved, never forged into canonical counts"}
    canonical_jobs_touched: set[str] = set()
    if a.supplement_dir:
        sdir = Path(a.supplement_dir)
        for txt_p in sorted(sdir.glob("SUPPLEMENTAL_*.txt")):
            meta_p = Path(str(txt_p) + ".meta.json")
            item: dict = {"supplement": txt_p.name, "checks": {}}
            try:
                blob = txt_p.read_bytes()
            except Exception as e:  # noqa: BLE001
                item["checks"]["readable"] = False
                item["recovered_verified"] = False
                item["note"] = f"supplement unreadable: {type(e).__name__}"
                recovered["items"].append(item)
                continue
            sup_sha = sha_bytes(blob)
            item["supplement_sha256"] = sup_sha
            item["supplement_bytes"] = len(blob)
            side, side_err = load_json(meta_p) if meta_p.exists() else (None, "sidecar absent")
            item["sidecar"] = side if isinstance(side, dict) else None
            item["sidecar_error"] = None if isinstance(side, dict) else side_err
            c = item["checks"]
            # 1) sha_self
            c["sha_self"] = bool(isinstance(side, dict) and side.get("response_sha256") == sup_sha)
            # 2) sha_source：与源 owned job response.txt 对比（只读 response.txt，不碰敏感文件）
            src_dir = Path(str((side or {}).get("source_job_directory", "")))
            src_blob = None
            if src_dir.is_dir() and (src_dir / "response.txt").exists():
                try:
                    src_blob = (src_dir / "response.txt").read_bytes()
                except Exception:  # noqa: BLE001
                    src_blob = None
            c["sha_source"] = bool(src_blob is not None and sha_bytes(src_blob) == sup_sha)
            # 3) binding：源 job started 五项 + 归一化 prompt 绑定 + 时间窗（只读 started.json）
            c["binding"] = False
            c["binding_detail"] = None
            try:
                started = json.loads((src_dir / "started.json").read_text(encoding="utf-8")) if src_dir.is_dir() else None
            except Exception:  # noqa: BLE001
                started = None
            target = (side or {}).get("target", "")
            if started and target:
                parts = target.split("/")
                area = parts[0] if parts else ""
                # target 形如 trials/gpt6w/A01/r03 或 results/trials/...；取 job 与 model
                mj = re.search(r"(gpt6w|gpt56w)", target)
                model_k = mj.group(1) if mj else None
                job_id = None
                if area == "trials" or "trials" in target:
                    mt = re.search(r"trials/(?:gpt6w|gpt56w)/([A-Za-z0-9]+)/r(\d+)", target)
                    if mt:
                        job_id = mt.group(1)
                if model_k and job_id and job_id in manifest_jobs:
                    mj0 = manifest_jobs[job_id]
                    try:
                        praw = (data_root / mj0["model_prompt_paths"][model_k]).read_bytes()
                        ns = sha_bytes(norm_prompt_bytes(praw))
                    except Exception:  # noqa: BLE001
                        ns = None
                    exp_full = MODEL_FULL[model_k]
                    # 时间窗：用 canonical 原 meta（若存在）否则 sidecar 记录
                    t0 = el = None
                    can_meta = None
                    if "trials" in target and job_id:
                        mt2 = re.search(r"/r(\d+)", target)
                        if mt2:
                            cp = data_root / "results" / "trials" / model_k / job_id / f"r{int(mt2.group(1)):02d}.meta.json"
                            if cp.exists():
                                can_meta, _ = load_json(cp)
                    if isinstance(can_meta, dict):
                        t0 = parse_iso(can_meta.get("utc_start"))
                        el = can_meta.get("elapsed_seconds") or 0
                    else:
                        t0 = parse_iso((side or {}).get("meta_utc_start"))
                        el = (side or {}).get("meta_elapsed") or 0
                    try:
                        su = parse_iso(started.get("utc"))
                    except Exception:  # noqa: BLE001
                        su = None
                    in_window = bool(t0 is not None and su is not None and
                                     t0 - datetime.timedelta(seconds=45) <= su <= t0 + datetime.timedelta(seconds=float(el or 0) + 30))
                    bind_ok = (started.get("model") == exp_full
                               and started.get("thinking_effort") == "max"
                               and started.get("temporary") is True
                               and started.get("prepare_source") == "native"
                               and started.get("isolated_runtime") is True
                               and started.get("provider_interface") is True
                               and ns is not None and started.get("prompt_sha256") == ns
                               and in_window)
                    c["binding"] = bool(bind_ok)
                    # binding 的 model 以 requested 期望全称为准（不是 sidecar==started 自洽）；
                    # sidecar 声明与期望不一致同样记录。
                    c["binding_detail"] = {"model_started": started.get("model"),
                                           "model_sidecar": (side or {}).get("model"),
                                           "model_expected": exp_full,
                                           "model_ok_vs_expected": started.get("model") == exp_full,
                                           "model_sidecar_vs_expected": (side or {}).get("model") == exp_full,
                                           "prompt_bound": ns is not None and started.get("prompt_sha256") == ns,
                                           "in_window": in_window}
            # 4) terminal（只读 result.json 的 completed/metadata 标量）
            c["terminal"] = False
            try:
                ro = json.loads((src_dir / "result.json").read_text(encoding="utf-8")) if src_dir.is_dir() else None
            except Exception:  # noqa: BLE001
                ro = None
            if isinstance(ro, dict):
                md = ro.get("metadata") or {}
                val = md.get("prepared_response_validation") or {}
                c["terminal"] = bool(ro.get("completed") is True
                                     and val.get("successful_assistant_terminal_observed") is True
                                     and val.get("unsupported_work_continuation_observed") is False)
                item["source_response_sha256"] = ro.get("response_sha256")
                # terminal 要求 result 声明 sha == 源 response.txt 实测字节（防声明与字节脱钩）
                c["terminal_sha_match"] = bool(
                    src_blob is not None and ro.get("response_sha256") == sha_bytes(src_blob))
                c["terminal"] = bool(c["terminal"] and c["terminal_sha_match"])
            # 5) submitted marker
            c["submitted"] = bool(src_dir.is_dir() and (src_dir / "submitted.json").exists())
            # 6) canonical_untouched：原 meta/raw/txt 三件套字节快照比对（有 --baseline-snapshot 时）；
            #    无快照时退化为“仍非 success”（明确记为 degraded_status_only，不冒充字节比对）。
            c["canonical_untouched"] = False
            c["canonical_untouched_mode"] = None
            if isinstance(can_meta, dict):
                item["canonical_status"] = can_meta.get("status")
                item["canonical_exit"] = can_meta.get("exit_code")
                snap_key = None
                if "trials" in target and job_id:
                    mt3 = re.search(r"/r(\d+)", target)
                    if mt3 and model_k:
                        snap_key = f"trials/{model_k}/{job_id}/r{int(mt3.group(1)):02d}"
                snap = baseline_snapshot.get("files", baseline_snapshot).get(snap_key) if snap_key else None
                if isinstance(snap, dict) and snap.get("meta_sha256"):
                    cur: dict = {}
                    try:
                        cp = data_root / "results" / "trials" / model_k / job_id / f"r{int(mt3.group(1)):02d}.meta.json"
                        cur["meta_sha256"] = sha_bytes(cp.read_bytes())
                        rp = cp.with_name(cp.name.replace(".meta.json", ".raw.json"))
                        cur["raw_sha256"] = sha_bytes(rp.read_bytes()) if rp.exists() else None
                        tp2 = cp.with_name(cp.name.replace(".meta.json", ".txt"))
                        cur["txt_sha256"] = sha_bytes(tp2.read_bytes()) if tp2.exists() else None
                    except Exception as e:  # noqa: BLE001
                        cur["read_error"] = f"{type(e).__name__}"
                    item["canonical_bytes_current"] = cur
                    item["canonical_bytes_snapshot"] = {k: snap.get(k) for k in ("meta_sha256", "raw_sha256", "txt_sha256")}
                    c["canonical_untouched"] = all(cur.get(k) == snap.get(k) for k in ("meta_sha256", "raw_sha256", "txt_sha256")
                                                   if snap.get(k) is not None)
                    c["canonical_untouched_mode"] = "byte_snapshot"
                else:
                    c["canonical_untouched"] = bool(not (can_meta.get("status") == "success"
                                                        and can_meta.get("completed") is True
                                                        and can_meta.get("exit_code") == 0))
                    c["canonical_untouched_mode"] = "degraded_status_only (no --baseline-snapshot)"
                if job_id:
                    canonical_jobs_touched.add(f"{job_id}:{model_k}")
            # 7) schema/source：补充 payload 过同规则（原文不修）
            c["schema_source"] = False
            try:
                stext = blob.decode("utf-8")
            except Exception:  # noqa: BLE001
                stext = None
            if stext is not None and job_id and "trials" in target:
                ok, note, sv, fails = check_supplement_payload(data_root, manifest_jobs, "trial", job_id, stext)
                item["supplement_schema_parse_ok"] = ok
                item["supplement_schema_note"] = note
                item["supplement_source_valid"] = sv
                item["supplement_source_failures"] = fails
                c["schema_source"] = bool(ok is True and sv is True)
            item["recovered_verified"] = bool(all([c.get("sha_self"), c.get("sha_source"), c.get("binding"),
                                                   c.get("terminal"), c.get("submitted"),
                                                   c.get("canonical_untouched"), c.get("schema_source")]))
            item["provable_scope"] = ("sha+binding+terminal+submitted+canonical_untouched+schema_source "
                                      "only; original CLI exit/status retained") if item["recovered_verified"] else "not verified"
            recovered["items"].append(item)
    recovered["recovered_verified_count"] = sum(1 for i in recovered["items"] if i.get("recovered_verified"))

    # ---- 不变量回归门（非硬编码最终期望：--expected-base-* 或默认值；--baseline-snapshot 校验冻结未改） ----
    failed_invariants = []
    if base_counts["transport_valid_success"] != exp_transport:
        failed_invariants.append(f"canonical_base_transport {base_counts['transport_valid_success']} != expected {exp_transport}")
    if base_counts["source_valid_among_valid"] != exp_source:
        failed_invariants.append(f"canonical_base_source_valid {base_counts['source_valid_among_valid']} != expected {exp_source}")
    # 恢复条目是否混入 canonical：trial/review details 终态分类不受 supplement 影响（本工具从不改写）→ 结构性成立；
    # 额外断言：canonical_jobs_touched 的槽位终态仍非 success。
    inflated = []
    for tag in canonical_jobs_touched:
        jid, mk = tag.split(":")
        for r in trial_details:
            if r["job"] == jid and r["model"] == mk and r["final_class"] == "transport_valid_success" and r.get("round") in BASE_ROUNDS:
                # 仅当该槽位原本就是 valid 才算正常；恢复目标槽位应为 ambiguous/missing
                pass
        for it in recovered["items"]:
            if it.get("recovered_verified") and it.get("canonical_status") == "success":
                inflated.append(tag)
    if inflated:
        failed_invariants.append(f"recovery inflated canonical success: {inflated}")
    invariants = {
        "expected_base_transport": exp_transport,
        "expected_base_source": exp_source,
        "expected_source": "--expected-base-transport/--expected-base-source or defaults (146/145); not a final verdict",
        "baseline_snapshot_used": bool(a.baseline_snapshot),
        "canonical_not_inflated_by_recovery": len(inflated) == 0,
        "failed_invariants": failed_invariants,
        "pass": len(failed_invariants) == 0,
    }

    # ---- ambiguous 建议（只读核查，不重提交）----
    suggestions = []
    for r in trial_details + review_details:
        if r["final_class"] == "ambiguous_failure":
            area = r["area"]
            stem = f"r{r['round']:02d}" if area == "trial" else r["job"]
            suggestions.append({"suggest_ownedjob_review": f"{area}:{r['job']}:{r.get('model')}:{stem}",
                                "action": "read-only audit only; no resubmit, no overwrite",
                                "stderr": f"results/{'trials' if area == 'trial' else 'reviews'}/{r.get('model')}/" +
                                          (f"{r['job']}/{stem}.stderr.txt" if area == "trial" else f"{r['job']}.stderr.txt")})

    detail = {"tool": "validate_delivery_v2.py", "data_root": str(data_root),
              "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "frozen_models": ["gpt-6-thinking", "gpt-5-6-thinking"],
              "prompt_freeze": prompt_state,
              "prompt_freeze_ok": all(v["ok"] for v in prompt_state.values()),
              "base_counts_r01_r05": base_counts,
              "base_counts_r01_r05_excl_pilot": base_counts_excl_pilot,
              "pairing_gaps_r06plus": gaps,
              "review_counts": review_counts,
              "ab_ba_agreement": ab_agreement,
              "self_review_sensitivity": self_review_sensitivity,
              "session_reuse_non_pilot": session_reuse_non_pilot,
              "pilot_session_exceptions": pilot_session_exceptions,
              "pilot_collision_with_current": pilot_collision_with_current,
              "ambiguous_ownedjob_suggestions": suggestions,
              "concurrency_v2": concurrency,
              "recovered_supplemental": recovered,
              "invariants": invariants,
              "trial_details": trial_details, "review_details": review_details}
    lines = []
    lines.append(f"data_root={data_root}")
    lines.append(f"prompt_freeze_ok={detail['prompt_freeze_ok']} (16 jobs byte-identical pairing)")
    lines.append(f"BASE r01-r05 slots={base_counts['slots']} transport_valid_success={base_counts['transport_valid_success']} "
                 f"claimed_invalid={base_counts['success_claimed_transport_invalid']} "
                 f"confirmed_pre_submit={base_counts['confirmed_pre_submit_failure']} "
                 f"ambiguous={base_counts['ambiguous_failure']} missing={base_counts['missing']} other={base_counts['other']}")
    lines.append(f"BASE excl_pilot slots={base_counts_excl_pilot['slots']} transport_valid_success={base_counts_excl_pilot['transport_valid_success']} "
                 f"ambiguous={base_counts_excl_pilot['ambiguous_failure']}")
    lines.append(f"valid中 schema_parse_ok={base_counts['schema_parse_ok_among_valid']} fail={base_counts['schema_parse_fail_among_valid']} "
                 f"source_valid={base_counts['source_valid_among_valid']} invalid={base_counts['source_invalid_among_valid']}")
    if base_counts["schema_fail_slots"]:
        lines.append(f"schema_fail_slots={base_counts['schema_fail_slots']}")
    lines.append(f"reviews manifest={review_counts['total_manifest']} transport_valid_success={review_counts['transport_valid_success']} by_class={dict(rc)}")
    lines.append(f"reviews schema_ok={review_counts['review_schema_ok_among_valid']} schema_fail={review_counts['review_schema_fail_among_valid']}")
    for s in review_counts["review_schema_fail_slots"]:
        lines.append(f"  REVIEW-SCHEMA-FAIL {s['slot']}: {s['failures']}")
    lines.append(f"D/G winner={review_counts['review_winner_distribution']} F recommend={review_counts['review_recommend_distribution']}")
    lines.append(f"AB/BA comparable={ab_agreement['comparable']} agree={ab_agreement['agree']} disagree={len(ab_agreement['disagree'])} uncomparable={ab_agreement['uncomparable']}")
    for dg in ab_agreement["disagree"]:
        lines.append(f"  AB-BA-DISAGREE {dg['pair']}: AB={dg['AB_winner']} BA={dg['BA_winner']}")
    lines.append(f"self_review D_self={self_review_sensitivity['D_self_reviewed_slots']} D_nonself={self_review_sensitivity['D_non_self_slots']} "
                 f"D_excl_self={self_review_sensitivity['D_winner_excl_self']}")
    lines.append(f"session_reuse_non_pilot={len(session_reuse_non_pilot)} pilot_exceptions={len(pilot_session_exceptions)} "
                 f"pilot_collision_with_current={len(pilot_collision_with_current)}")
    for pc in pilot_collision_with_current:
        lines.append(f"  PILOT-COLLISION {pc['handle']}: {pc['slots']}")
    mp = concurrency["meta_interval_peak_incl_pilot"]
    lines.append(f"meta_interval_peak_incl_pilot={mp['peak']} at={mp['peak_at']}")
    lines.append(f"  members={mp['members']}")
    me = concurrency["meta_interval_peak_excl_pilot"]
    lines.append(f"meta_interval_peak_excl_pilot={me['peak']} at={me['peak_at']}")
    for k in ("scheduler_event_window_peak", "owned_http_inflight_peak", "owned_terminal_event_density_120s"):
        v = concurrency[k]
        lines.append(f"{k}={v}")
    lines.append(f"recovered_items={len(recovered['items'])} recovered_verified={recovered.get('recovered_verified_count', 0)} (supplemental only, never into canonical)")
    for it in recovered["items"]:
        lines.append(f"  RECOVERED {it.get('supplement')}: verified={it.get('recovered_verified')} checks={it.get('checks')} "
                      f"schema={it.get('supplement_schema_parse_ok')} source={it.get('supplement_source_valid')}")
    lines.append(f"INVARIANTS pass={invariants['pass']} failed={failed_invariants}")
    lines.append(f"r06+ pairing_gaps={len(gaps)}")
    summary = "\n".join(lines) + "\n"
    print(summary, end="")
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "delivery_validation_v2.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (report_dir / "delivery_validation_v2_summary.txt").write_text(summary, encoding="utf-8")
    print(f"wrote {report_dir / 'delivery_validation_v2.json'}")
    print(f"wrote {report_dir / 'delivery_validation_v2_summary.txt'}")
    return 0 if invariants["pass"] else 4


if __name__ == "__main__":
    sys.exit(main())
