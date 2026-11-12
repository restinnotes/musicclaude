#!/usr/bin/env python3
"""独立交付验收验证器（只读，不调用任何模型，不修改原证据）。

用途：对冻结基线实验目录做交付前独立验证，区分传输完整性与内容模式：
  - transport_valid：CLI 元数据/路由/effort/会话/SHA 链/文件三元组是否自洽。
  - schema_parse_ok：响应 txt 在语义上是否可解析为 JSON（仅可解析程度，不等于质量判断）。
  - source_valid：可解析 payload 相对冻结 source 输入的结构一致性（A/B/C 按原规则）。

关键工程细节（避免误判）：
  - response txt 由原 runner 以 Path.write_text 默认文本模式落盘，Windows 下为 CRLF；
    而 response_sha256_observed 是对原 response UTF-8（LF）哈希。因此磁盘 txt 的
    archive_byte_sha 单独记录，逻辑校验用 CRLF->LF 归一化后比较；绝不把 CRLF 落盘
    等同模型/证据篡改。
  - prompt 严格 read_bytes 对 manifest input_sha256（逐字节）。
  - review prompt 由 build_repeat_judges 以 newline='\\n' 落盘，磁盘字节必须与哈希相符。
  - 不使用运行日志里的 PRESERVED 行、不以 txt 含 stderr 文本误计成功。
  - 原始失败（confirmed_pre_submit_failure / failure_or_ambiguous）永不算成功。
  - session_handle 全局唯一性检查；pilot 导入（imported_from_pilot）的 r01 例外另记。
  - 外部只读恢复任务若找回完整终态，只能记 supplemental RECOVERED_FROM_OWNED_EVIDENCE，
    原 CLI exit1 保留，不伪造 exit0；本验证器仅独立记录 recovered_verified 与可证明范围。
  - 本脚本不产生任何子进程（无 powershell/cmd/python 内层进程），无网络，不调用模型，
    不写 data-root。

用法（必须 -I，从可信目录调用，不从下载解压目录运行）：
  python -I validate_delivery.py --data-root D:/musicclaude/_dl_latest_zip_work --report-dir D:/musicclaude/_baseline_delivery_control_20261010
  python -I validate_delivery.py --data-root <dir> --stdout-summary   # 只打印，不产生文件
  python -I validate_delivery.py --data-root <dir> --report-dir <dir> --recovered-json <path>  # 附带恢复证据独立记录
"""
import argparse
import collections
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

MODEL_FULL = {"gpt6w": "gpt-6-thinking", "gpt56w": "gpt-5-6-thinking"}
ALLOWED_A = {"insight", "restatement", "manufactured", "imported", "undetermined"}
ALLOWED_B = {"valuable_new_link", "restatement", "unsupported_causality", "premature_lock", "not_enough_evidence"}
ALLOWED_C = {"KEEP", "RETIRE", "REPLACE", "APPEND", "SILENCE"}
BASE_ROUNDS = list(range(1, 6))
ALL_ROUNDS = list(range(1, 13))
FINAL_RE = re.compile(r"^r(\d{2})\.meta\.json$")
ATTEMPT_RE = re.compile(r"^r(\d{2})\.attempt(\d+)\.(meta\.json|raw\.json|stderr\.txt)$")


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


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
    # 1) 路由与 effort
    if meta.get("model_requested") != exp_full:
        reasons.append(f"model_requested {meta.get('model_requested')!r} != {exp_full}")
    if meta.get("model_reported") != exp_full:
        reasons.append(f"model_reported {meta.get('model_reported')!r} != {exp_full}")
    if meta.get("thinking_effort") != "max":
        reasons.append(f"thinking_effort {meta.get('thinking_effort')!r} != max")
    # 2) prompt 哈希（meta 记录 vs manifest vs 磁盘 prompt 字节）
    if meta.get("prompt_sha256") != job["input_sha256"]:
        reasons.append("meta.prompt_sha256 != manifest input_sha256")
    if not prompt_ok:
        reasons.append("frozen prompt bytes != manifest input_sha256")
    # 3) raw wrapper
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
    # 4) 成功三元组
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
    # 5) 终态分类（原始失败永不算成功）
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
    # 6) schema/source（可解析程度 != 质量判断）
    schema_parse_ok = None
    schema_note = None
    source_valid = None
    source_failures = []
    if txt_p.exists() and txt_p.stat().st_size > 0 and final_class in ("transport_valid_success", "success_claimed_transport_invalid"):
        try:
            text = txt_p.read_text(encoding="utf-8")  # universal newlines
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


def check_review_slot(data_root: Path, row: dict):
    model = row["judge_model"]
    jid = row["job_id"]
    kind = row.get("kind")
    exp_full = MODEL_FULL[model]
    prompt_p = data_root / row["prompt_file"]
    prompt_ok = False
    prompt_note = None
    if prompt_p.exists():
        prompt_ok = sha_bytes(prompt_p.read_bytes()) == row.get("prompt_sha256")
        if not prompt_ok:
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
           "prompt_ok": prompt_ok, "prompt_note": prompt_note}
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
    schema_parse_ok = None
    schema_note = None
    if txt_p.exists() and txt_p.stat().st_size > 0 and final_class in ("transport_valid_success", "success_claimed_transport_invalid"):
        try:
            text = txt_p.read_text(encoding="utf-8")
            obj = json.loads(text)
            schema_parse_ok = True
            if not isinstance(obj, dict) or obj.get("task") != kind:
                schema_parse_ok = False
                schema_note = f"task field {obj.get('task') if isinstance(obj, dict) else type(obj).__name__!r} != {kind}"
            elif "winner" in obj and obj["winner"] not in ("A", "B"):
                schema_parse_ok = False
                schema_note = f"winner {obj.get('winner')!r} not in A/B"
        except Exception as e:  # noqa: BLE001
            schema_parse_ok = False
            schema_note = f"{type(e).__name__}: {str(e)[:160]}"
    rec.update({"meta_status": status, "transport_valid": transport_valid, "transport_reasons": reasons,
                "final_class": final_class, "session_handle": session_handle,
                "utc_start": meta.get("utc_start"), "elapsed_seconds": meta.get("elapsed_seconds"),
                "response_sha256_observed": obs, "schema_parse_ok": schema_parse_ok, "schema_note": schema_note,
                "txt": txt_info, "station_k": row.get("station_k")})
    return rec, session_handle


def main():
    ap = argparse.ArgumentParser(description="独立交付验收验证（只读，不调用模型）")
    ap.add_argument("--data-root", required=True, help="实验数据目录（冻结包解压后的数据根）")
    ap.add_argument("--report-dir", default=None, help="报告输出目录（默认=本脚本所在可信目录）")
    ap.add_argument("--stdout-summary", action="store_true", help="只打印小 summary，不产生任何文件")
    ap.add_argument("--recovered-json", default=None, help="可选：只读恢复任务产出的补充证据清单（仅记录，不改原状态）")
    a = ap.parse_args()
    data_root = Path(a.data_root)
    trusted = Path(__file__).resolve().parent
    report_dir = Path(a.report_dir) if a.report_dir else trusted
    if not data_root.is_dir():
        print(f"ERROR: --data-root 不存在: {data_root}", file=sys.stderr)
        return 2
    try:
        manifest = json.loads((data_root / "jobs/manifest.json").read_text(encoding="utf-8"))
        plan = json.loads((data_root / "jobs/repetition_plan.json").read_text(encoding="utf-8"))
        reviews = json.loads((data_root / "jobs/reviews/review_manifest.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: 冻结 manifest 读取失败: {type(e).__name__} {e}", file=sys.stderr)
        return 2
    # prompt 冻结哈希（严格 read_bytes）
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
        rec, _ = check_review_slot(data_root, row)
        review_details.append(rec)
    # session 唯一性（pilot 例外另记）
    handle_map = collections.defaultdict(list)
    pilot_handles = []
    for rec in trial_details + review_details:
        h = rec.get("session_handle")
        if not h:
            continue
        label = f"{rec['area']}:{rec['job']}:{rec.get('model')}:r{rec.get('round', '-')}"
        if rec.get("pilot_imported"):
            pilot_handles.append({"handle": h, "slot": label})
        else:
            handle_map[h].append(label)
    reuse = {h: v for h, v in handle_map.items() if len(v) > 1}
    # BASE 计数（r01-r05：16*2*5=160 格）
    base = [r for r in trial_details if r.get("round") in BASE_ROUNDS]
    def cnt(pred):
        return sum(1 for r in base if pred(r))
    base_counts = {
        "slots": len(base),
        "transport_valid_success": cnt(lambda r: r["final_class"] == "transport_valid_success"),
        "success_claimed_transport_invalid": cnt(lambda r: r["final_class"] == "success_claimed_transport_invalid"),
        "confirmed_pre_submit_failure": cnt(lambda r: r["final_class"] == "confirmed_pre_submit_failure"),
        "ambiguous_failure": cnt(lambda r: r["final_class"] == "ambiguous_failure"),
        "missing": cnt(lambda r: r["final_class"] == "missing"),
        "other": cnt(lambda r: r["final_class"] not in ("transport_valid_success", "success_claimed_transport_invalid",
                                                        "confirmed_pre_submit_failure", "ambiguous_failure", "missing")),
    }
    valid_recs = [r for r in base if r["final_class"] == "transport_valid_success"]
    base_counts["schema_parse_ok_among_valid"] = sum(1 for r in valid_recs if r.get("schema_parse_ok") is True)
    base_counts["schema_parse_fail_among_valid"] = sum(1 for r in valid_recs if r.get("schema_parse_ok") is False)
    base_counts["source_valid_among_valid"] = sum(1 for r in valid_recs if r.get("source_valid") is True)
    base_counts["source_invalid_among_valid"] = sum(1 for r in valid_recs if r.get("source_valid") is False)
    # r06+ 配对缺口
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
    # 评审计数（review_manifest 按实际长度动态读，不写死 88）
    rc = collections.Counter(r["final_class"] for r in review_details)
    rk = collections.Counter(r.get("kind") for r in review_details)
    review_counts = {"total_manifest": len(reviews["jobs"]), "by_kind": dict(rk), "by_class": dict(rc),
                     "transport_valid_success": sum(1 for r in review_details if r["final_class"] == "transport_valid_success")}
    # ambiguous 建议（只建议 ownedjob 只读核查，不重提交）
    suggestions = []
    for r in trial_details + review_details:
        if r["final_class"] == "ambiguous_failure":
            area = r["area"]
            stem = f"r{r['round']:02d}" if area == "trial" else r["job"]
            suggestions.append({"suggest_ownedjob_review": f"{area}:{r['job']}:{r.get('model')}:{stem}",
                                "action": "read-only audit only; no resubmit, no overwrite",
                                "stderr": f"results/{'trials' if area=='trial' else 'reviews'}/{r.get('model')}/" +
                                          (f"{r['job']}/{stem}.stderr.txt" if area == "trial" else f"{r['job']}.stderr.txt")})
    # 实际并发峰值（来自 utc_start+elapsed，非假定）
    events = []
    for r in trial_details + review_details:
        t0 = parse_iso(r.get("utc_start"))
        el = r.get("elapsed_seconds")
        if t0 is None or not isinstance(el, (int, float)):
            continue
        t1 = t0 + datetime.timedelta(seconds=float(el))
        events.append((t0, 1))
        events.append((t1, -1))
    events.sort(key=lambda e: (e[0], -e[1]))
    cur = peak = 0
    peak_at = None
    for t, dlt in events:
        cur += dlt
        if cur > peak:
            peak = cur
            peak_at = t.isoformat()
    # 恢复补充证据（仅记录）
    recovered = {"provided": bool(a.recovered_json), "items": [], "note": "absent: no supplemental recovery list supplied"}
    if a.recovered_json:
        try:
            lst = json.loads(Path(a.recovered_json).read_text(encoding="utf-8"))
            recovered["note"] = "supplemental only; original exit/status preserved, no exit0 forgery"
            for it in lst if isinstance(lst, list) else []:
                ev = Path(str(it.get("evidence_path", "")))
                ok = ev.exists() and ev.stat().st_size > 0
                actual = sha_bytes(ev.read_bytes()) if ok else None
                match = (actual == it.get("response_sha256")) if (ok and it.get("response_sha256")) else None
                recovered["items"].append({"ref": it.get("ref"), "job": it.get("job_id"),
                                            "evidence_exists": ok, "sha_match": match,
                                            "recovered_verified": bool(ok and match),
                                            "provable_scope": "sha+session+binding only; original CLI exit1 retained",
                                            "original_status_preserved": it.get("original_status")})
        except Exception as e:  # noqa: BLE001
            recovered["note"] = f"recovered list unreadable: {type(e).__name__} {str(e)[:160]}"
    detail = {"tool": "validate_delivery.py", "data_root": str(data_root),
              "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "frozen_models": ["gpt-6-thinking", "gpt-5-6-thinking"],
              "prompt_freeze": prompt_state,
              "prompt_freeze_ok": all(v["ok"] for v in prompt_state.values()),
              "base_counts_r01_r05": base_counts,
              "pairing_gaps_r06plus": gaps,
              "review_counts": review_counts,
              "session_reuse_non_pilot": [{"handle": h, "slots": v} for h, v in reuse.items()],
              "pilot_session_exceptions": pilot_handles,
              "ambiguous_ownedjob_suggestions": suggestions,
              "concurrency_observed": {"peak": peak, "peak_at": peak_at,
                                       "basis": "utc_start+elapsed_seconds from final metas; observed, not assumed"},
              "recovered_supplemental": recovered,
              "trial_details": trial_details, "review_details": review_details}
    lines = []
    lines.append(f"data_root={data_root}")
    lines.append(f"prompt_freeze_ok={detail['prompt_freeze_ok']} (16 jobs byte-identical pairing)")
    lines.append(f"BASE r01-r05 slots={base_counts['slots']} transport_valid_success={base_counts['transport_valid_success']} "
                 f"claimed_invalid={base_counts['success_claimed_transport_invalid']} "
                 f"confirmed_pre_submit={base_counts['confirmed_pre_submit_failure']} "
                 f"ambiguous={base_counts['ambiguous_failure']} missing={base_counts['missing']} other={base_counts['other']}")
    lines.append(f"valid中 schema_parse_ok={base_counts['schema_parse_ok_among_valid']} fail={base_counts['schema_parse_fail_among_valid']} "
                 f"source_valid={base_counts['source_valid_among_valid']} invalid={base_counts['source_invalid_among_valid']}")
    lines.append(f"reviews manifest={review_counts['total_manifest']} transport_valid_success={review_counts['transport_valid_success']} by_class={dict(rc)}")
    lines.append(f"r06+ pairing_gaps={len(gaps)} session_reuse={len(reuse)} pilot_exceptions={len(pilot_handles)}")
    lines.append(f"concurrency_peak_observed={peak} at={peak_at}")
    lines.append(f"recovered_items={len(recovered['items'])} (supplemental only)")
    summary = "\n".join(lines) + "\n"
    print(summary, end="")
    if a.stdout_summary:
        return 0
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "delivery_validation.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (report_dir / "delivery_validation_summary.txt").write_text(summary, encoding="utf-8")
    print(f"wrote {report_dir / 'delivery_validation.json'}")
    print(f"wrote {report_dir / 'delivery_validation_summary.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
