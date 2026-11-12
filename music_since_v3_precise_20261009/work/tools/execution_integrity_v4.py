"""v4：先持久化提交票据，再启动进程；旧实现及失败证据只读。"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path

import execution_integrity as old
import execution_integrity_v3 as v3

ArtifactConflict, PolicyBlocked = old.ArtifactConflict, old.PolicyBlocked
sha_text, sha_file, digest = old.sha_text, old.sha_file, old.digest
run_process = old.run_process
Slot = v3.Slot
SLOT_DIR = v3.SLOT_DIR
# 未取得真实 CLI 事件契约与独立复核证据前，真实路径保持关闭；测试只能局部 mock 此值。
REAL_EXECUTION_APPROVED = False
VERSION = "20261009.v4"
HANDLE_NAME = r"(?:thread[_-]?id|session[_-]?(?:id|handle)|conversation[_-]?id|message[_-]?id|parent[_-]?id)"
HANDLE_RE = re.compile(r"^" + HANDLE_NAME + r"$", re.I)
HANDLE_QUOTED = re.compile(r"([\"']?" + HANDLE_NAME + r"[\"']?\s*[=:]\s*)([\"'])(.*?)\2", re.I)
HANDLE_PLAIN = re.compile(r"([\"']?" + HANDLE_NAME + r"[\"']?\s*[=:]\s*)[^\s,;\"'&}]+", re.I)
strict_json, valid_id = v3.strict_json, v3.valid_id
parse_opencode = v3.parse_opencode


def safe_text(text):
    text = old.safe_text(text)
    text = HANDLE_QUOTED.sub(lambda m: m[1] + m[2] + "<redacted>" + m[2], text)
    return HANDLE_PLAIN.sub(lambda m: m[1] + "<redacted>", text)


def safe_metadata(obj):
    if isinstance(obj, dict):
        return {str(key): "<redacted>" if HANDLE_RE.fullmatch(str(key)) or old.PRIVATE_KEY_RE.search(str(key))
                else safe_metadata(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [safe_metadata(value) for value in obj]
    if isinstance(obj, str):
        return safe_text(obj)
    return obj


def safe_records(text):
    text = str(text)
    try:
        return json.dumps(safe_metadata(strict_json(text)), ensure_ascii=False) + "\n"
    except (ValueError, TypeError):
        rows = []
        for line in text.splitlines():
            try:
                rows.append(json.dumps(safe_metadata(strict_json(line)), ensure_ascii=False))
            except (ValueError, TypeError):
                rows.append(safe_text(line))
        return "\n".join(rows) + ("\n" if rows else "")


def assert_content_safe(text):
    if not isinstance(text, str) or safe_text(text) != text:
        raise ValueError("sensitive-looking content rejected; body not persisted")


def write_text(path, text):
    old.write_text(path, text)


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(safe_metadata(obj), ensure_ascii=False, indent=2))
        handle.flush()
        os.fsync(handle.fileno())
    temp.replace(path)


def exclusive_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        handle.write(json.dumps(safe_metadata(obj), ensure_ascii=False, indent=2))
        handle.flush()
        os.fsync(handle.fileno())


def environment_identity(env):
    # 不落凭证或凭证 hash。只冻结已知非敏感、会影响 CLI 解析/选路的环境值。
    names = ("PATH", "Path", "APPDATA", "LOCALAPPDATA", "USERPROFILE", "HOME", "NODE_OPTIONS",
             "PYTHONPATH", "PYTHONHOME", "CODEX_HOME", "OPENCODE_CONFIG", "OPENCODE_CONFIG_CONTENT",
             "MUSIC_WEB_ROUTE", "MUSIC_GPT2_CMD", "GPT2AGENT_SAFECHAIN_ROOT")
    fields = {key: sha_text(str(env[key])) for key in names if key in env and safe_text(str(env[key])) == str(env[key])}
    return {"nonprivate_sha256": fields, "coverage": "allowlisted behavioral values only; credentials and other environment not frozen"}


def implementation_identity():
    names = ("execution_integrity.py", "runner.py", "execution_integrity_v3.py",
             "execution_integrity_v4.py", "runner_v4.py", "gpt2_adapter_v4.py", "experiment_calls_v4.py")
    return {name: sha_file(Path(__file__).with_name(name)) for name in names}


def resume(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    path = directory / "meta" / (job_id + ".json")
    if not path.exists():
        return None
    try:
        data = strict_json(path.read_bytes().decode("utf-8"))
        if (not isinstance(data, dict) or data.get("schema") != VERSION
                or data.get("job_id") != job_id or data.get("request_identity") != identity
                or data.get("producer_identity") != identity["producer"]
                or data.get("status") != "ok" or data.get("terminal_verified") is not True
                or data.get("queue_stop") is not False or not isinstance(data.get("terminal"), dict)):
            raise ArtifactConflict("missing/conflicting exact v4 completion: " + job_id)
        verify_finalization(directory, job_id, data)
        if data.get("prompt_sha256") != identity["prompt_sha256"]:
            raise ArtifactConflict("meta prompt SHA conflicts with request")
        for field, expected in (("prompt_file", identity["prompt_sha256"]),
                                ("output_file", data.get("response_sha256"))):
            rel = data.get(field)
            if not isinstance(rel, str):
                raise ArtifactConflict("missing artifact locator")
            artifact = (directory / rel).resolve()
            if (not artifact.is_relative_to(directory.resolve()) or not artifact.is_file()
                    or sha_file(artifact) != expected):
                raise ArtifactConflict("artifact missing/tampered/outside run")
        text = (directory / data["output_file"]).read_bytes().decode("utf-8")
        if not text.strip():
            raise ArtifactConflict("empty completed body")
        assert_content_safe(text)
        return dict(data, resumed=True, consumer_identity=identity["producer"])
    except (ValueError, TypeError, KeyError, OSError) as exc:
        raise ArtifactConflict("invalid v4 completion evidence: " + job_id) from exc


def finalize(directory, job_id, meta):
    directory = Path(directory)
    exclusive_json(directory / "finalized" / (job_id + ".json"),
                   {"schema": VERSION, "job_id": job_id,
                    "meta_sha256": sha_file(directory / "meta" / (job_id + ".json")),
                    "prompt_sha256": sha_file(directory / meta["prompt_file"]),
                    "output_sha256": sha_file(directory / meta["output_file"])})


def verify_finalization(directory, job_id, meta):
    directory = Path(directory)
    try:
        marker = strict_json((directory / "finalized" / (job_id + ".json")).read_bytes().decode("utf-8"))
        if (not isinstance(marker, dict) or marker.get("schema") != VERSION or marker.get("job_id") != job_id
                or marker.get("meta_sha256") != sha_file(directory / "meta" / (job_id + ".json"))):
            raise ArtifactConflict("missing/conflicting finalization seal")
        for field, hash_field in (("prompt_file", "prompt_sha256"), ("output_file", "output_sha256")):
            rel = meta.get(field)
            path = (directory / rel).resolve() if isinstance(rel, str) else None
            if (path is None or not path.is_relative_to(directory.resolve()) or not path.is_file()
                    or marker.get(hash_field) != sha_file(path)):
                raise ArtifactConflict("finalized artifact missing/tampered/outside run")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ArtifactConflict("cannot verify finalization seal") from exc


def reserve(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    for folder, suffix in (("prompts", ".txt"), ("outputs", ".md"), ("pending", ".json"), ("meta", ".json")):
        if (directory / folder / (job_id + suffix)).exists():
            raise ArtifactConflict("existing/incomplete job is read-only: " + job_id)
    exclusive_json(directory / "pending" / (job_id + ".json"),
                   {"schema": VERSION, "request_identity": identity, "job_id": job_id,
                    "created": datetime.now().isoformat()})


def ref_cache(directory, identity):
    directory = Path(directory)
    path = directory / "cache" / (digest(identity) + ".json")
    if not path.exists():
        # 索引丢失不等于未提交。保留 pending/meta 双来源；不能为同一采样另取 job 偷跑。
        for folder in ("pending", "meta"):
            for candidate in sorted((directory / folder).glob("*.json")):
                try:
                    record = strict_json(candidate.read_bytes().decode("utf-8"))
                    if not isinstance(record, dict):
                        raise ValueError("non-object ledger")
                except (ValueError, TypeError, OSError) as exc:
                    raise ArtifactConflict("run ledger unreadable; no safe cache miss") from exc
                if record.get("request_identity") == identity:
                    raise ArtifactConflict("sample ledger exists but cache index missing; inspect, do not resubmit")
        return None
    try:
        obj = strict_json(path.read_bytes().decode("utf-8"))
        if (not isinstance(obj, dict) or obj.get("schema") != VERSION
                or obj.get("request_identity") != identity or obj.get("state") != "ok"):
            raise ArtifactConflict("sample cache incomplete/failed/conflicting")
        source_id = valid_id(obj["source_job_id"])
        if sha_file(directory / "meta" / (source_id + ".json")) != obj["source_meta_sha256"]:
            raise ArtifactConflict("sample source meta changed")
        data = resume(directory, source_id, identity)
        if data is None or data["response_sha256"] != obj["response_sha256"]:
            raise ArtifactConflict("sample source missing/conflicting")
        return data
    except (KeyError, ValueError, TypeError, OSError) as exc:
        raise ArtifactConflict("sample cache cannot be recovered safely") from exc


def sample_record(directory, job_id, identity, state, meta=None):
    record = {"schema": VERSION, "request_identity": identity, "source_job_id": job_id, "state": state}
    if meta is not None:
        record.update(source_meta_sha256=sha_file(Path(directory) / "meta" / (job_id + ".json")),
                      response_sha256=meta.get("response_sha256"))
    path = Path(directory) / "cache" / (digest(identity) + ".json")
    if path.exists():
        prior = strict_json(path.read_bytes().decode("utf-8"))
        if prior.get("source_job_id") != job_id or prior.get("request_identity") != identity:
            raise ArtifactConflict("cannot redirect original sample source")
    write_json(path, record)


def queue_open(hold_file):
    hold_file = Path(hold_file)
    # 即便 hold 写盘失败，已 fsync 的 inflight 票据仍在跨进程阻断后继请求。
    return not hold_file.exists() and not any((hold_file.parent / "inflight_v4").glob("*.json"))


def submission_ticket(hold_file, directory, job_id, identity):
    hold_file = Path(hold_file)
    if not queue_open(hold_file):
        raise PolicyBlocked("provider held or unclassified inflight submission; no replay")
    ticket = hold_file.parent / "inflight_v4" / (digest({"run": str(Path(directory).resolve()), "job": job_id}) + ".json")
    exclusive_json(ticket, {"schema": VERSION, "run_directory": str(Path(directory).resolve()),
                           "job_id": job_id, "request_identity_sha256": digest(identity),
                           "state": "may_submit_or_inflight", "server_cancelled": "unknown"})
    return ticket


def hold(path, job_id, run_id, reason):
    path = Path(path)
    if not path.exists():
        write_json(path, {"schema": VERSION, "job_id": job_id, "run_id": run_id,
                          "reason": safe_text(reason), "created": datetime.now().isoformat(),
                          "server_cancelled": "unknown"})


def classify_stop(path, job_id, run_id, reason):
    try:
        hold(path, job_id, run_id, reason)
        return None
    except OSError as exc:
        # 不吞保护失败；返回审计字段。票据绝不清除，不把 OS 释放锁当放行。
        return safe_text(type(exc).__name__ + ": " + str(exc))


def release_ticket(ticket):
    # 只在成功终态/明确未提交 + 全部正文/meta/cache 已落盘后调用；失败保持阻断。
    Path(ticket).unlink()


def model_evidence(metadata, requested):
    metadata = metadata if isinstance(metadata, dict) else {}
    summary = metadata.get("server_metadata_summary")
    found = []
    # 当前 source-bound native provider 只输出 STE summary 根字段；debug/嵌套自述无型号证明权。
    if isinstance(summary, dict):
        slug = summary.get("model_slug")
        if isinstance(slug, str) and slug.strip():
            found.append(("server_metadata_summary.model_slug", slug))
        slugs = summary.get("resolved_model_slugs")
        if isinstance(slugs, list) and slugs and all(isinstance(item, str) and item.strip() for item in slugs):
            found.extend(("server_metadata_summary.resolved_model_slugs", item) for item in slugs)
    normalize = lambda value: value.strip().lower().replace(".", "-").replace("_", "-")
    slugs = sorted({value for _, value in found})
    verdict = "unverified" if not slugs else "match" if all(normalize(value) == normalize(requested) for value in slugs) else "mismatch"
    return {"verdict": verdict, "server_slugs": slugs, "fields": sorted({path for path, _ in found}),
            "contract": "gpt2 headless provider exposes server_metadata_summary; other paths ignored"}


def parse_codex(stdout):
    rows = v3.ndjson(stdout)
    active = finished = thread_seen = False
    pending, completed, counts = {}, set(), {}
    last_text = ""
    allowed_items = {"agent_message", "reasoning", "todo_list", "command_execution", "file_change",
                     "mcp_tool_call", "web_search", "image_generation"}
    for obj in rows:
        kind = obj.get("type")
        if finished:
            raise ValueError("event after completed turn")
        if kind == "thread.started":
            if thread_seen or active or not isinstance(obj.get("thread_id"), str) or not obj["thread_id"]:
                raise ValueError("invalid/duplicate thread start")
            thread_seen = True
        elif kind == "turn.started":
            if not thread_seen or active:
                raise ValueError("invalid/duplicate turn start")
            active = True
        elif kind == "turn.completed":
            if not active or pending or not last_text.strip() or not isinstance(obj.get("usage"), dict):
                raise ValueError("incomplete turn/items/body")
            active, finished = False, True
        elif kind in ("item.started", "item.updated", "item.completed"):
            item = obj.get("item")
            if not active or not isinstance(item, dict):
                raise ValueError("item outside turn/bad shape")
            ident, itype = item.get("id"), item.get("type")
            if not isinstance(ident, str) or not ident or itype not in allowed_items or ident in completed:
                raise ValueError("unknown/error/duplicate item")
            if ident in pending and pending[ident] != itype:
                raise ValueError("item type changed")
            if item.get("status") in ("failed", "error", "cancelled", "canceled"):
                raise ValueError("failed/cancelled item")
            if kind != "item.completed":
                pending[ident] = itype
                continue
            pending.pop(ident, None)
            completed.add(ident)
            if itype == "agent_message":
                if not isinstance(item.get("text"), str) or not item["text"].strip():
                    raise ValueError("invalid agent message")
                last_text = item["text"]
            else:
                counts[itype] = counts.get(itype, 0) + 1
        else:
            raise ValueError("unknown/error/cancelled Codex event")
    if not finished:
        raise ValueError("no complete Codex turn")
    return last_text, counts, {"schema": "codex_exec_jsonl_v4", "terminal": "turn.completed"}
