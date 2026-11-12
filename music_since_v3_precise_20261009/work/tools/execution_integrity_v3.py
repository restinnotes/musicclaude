"""v3 新调用边界；旧实现只读，不给历史补写证明。"""
from __future__ import annotations

import contextlib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import execution_integrity as old

ArtifactConflict = old.ArtifactConflict
PolicyBlocked = old.PolicyBlocked
sha_text, sha_file, digest = old.sha_text, old.sha_file, old.digest
write_text, write_json = old.write_text, old.write_json
safe_text, safe_metadata = old.safe_text, old.safe_metadata
run_process, model_evidence = old.run_process, old.model_evidence
ROOT = Path(__file__).resolve().parents[1]
SLOT_DIR = ROOT / "runs/_call_slots"
VERSION = "20261009.v3"
ID_RE = re.compile(r"[A-Za-z0-9_.-]+\Z")
HANDLE_RE = re.compile(r"^(thread_id|sessionID|session_id|conversation_id|messageID|parentID)$", re.I)


def valid_id(value):
    if not isinstance(value, str) or not ID_RE.fullmatch(value) or value in (".", ".."):
        raise ValueError("unsafe job_id")
    return value


def strict_json(text):
    def pairs(rows):
        out = {}
        for key, value in rows:
            if key in out:
                raise ValueError("duplicate JSON key")
            out[key] = value
        return out
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))


def safe_records(text):
    def scrub(obj):
        if isinstance(obj, dict):
            return {key: "<redacted>" if HANDLE_RE.fullmatch(key) else scrub(value)
                    for key, value in obj.items()}
        if isinstance(obj, list):
            return [scrub(value) for value in obj]
        return obj
    rows = []
    for line in str(text).splitlines():
        try:
            rows.append(json.dumps(safe_metadata(scrub(strict_json(line))), ensure_ascii=False))
        except (ValueError, TypeError):
            rows.append(safe_text(line))
    return "\n".join(rows) + ("\n" if rows else "")


def assert_content_safe(text):
    # 不能分辨正文中的示例赋值和真正凭证时，拒收，不静默改写正文/哈希。
    if safe_text(text) != text:
        raise ValueError("sensitive-looking content rejected; body not persisted")


class Slot:
    def __init__(self, pool, cap=1, *, base=None):
        if type(cap) is not int or cap < 1:
            raise ValueError("slot cap must be positive")
        self.base, self.pool, self.cap = Path(base or SLOT_DIR), pool, cap

    def __enter__(self):
        directory = self.base / self.pool
        directory.mkdir(parents=True, exist_ok=True)
        while True:
            for index in range(self.cap):
                fd = os.open(str(directory / ("slot%03d" % index)), os.O_RDWR | os.O_CREAT)
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    if sys.platform == "win32":
                        import msvcrt
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    os.close(fd)
                    continue
                self.fd = fd
                return self
            time.sleep(.05)

    def __exit__(self, *exc):
        try:
            os.lseek(self.fd, 0, os.SEEK_SET)
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_UN)
        finally:
            os.close(self.fd)
        return False


def implementation_identity():
    names = ("execution_integrity.py", "runner.py", "execution_integrity_v3.py",
             "runner_v3.py", "gpt2_adapter_v3.py", "experiment_calls_v3.py")
    return {name: sha_file(Path(__file__).with_name(name)) for name in names}


def resume(directory, job_id, identity):
    valid_id(job_id)
    try:
        data = old.checked_resume(directory, job_id, identity)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        raise ArtifactConflict("invalid completion evidence: " + job_id) from exc
    if data is None:
        return None
    if (data.get("terminal_verified") is not True or data.get("queue_stop") is not False
            or data.get("producer_identity") != identity["producer"]
            or data.get("prompt_sha256") != identity["prompt_sha256"]):
        raise ArtifactConflict("missing v3 terminal/producer evidence: " + job_id)
    assert_content_safe((Path(directory) / data["output_file"]).read_bytes().decode("utf-8"))
    return data


def reserve(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    for folder, extension in (("prompts", ".txt"), ("outputs", ".md"), ("pending", ".json")):
        if (directory / folder / (job_id + extension)).exists():
            raise ArtifactConflict("existing/incomplete job is read-only: " + job_id)
    assert_content_safe(identity.get("_prompt_for_validation", ""))
    path = directory / "pending" / (job_id + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    # 崩溃后保留 pending，不把缺 meta 解释成可以再次提交。
    with path.open("x", encoding="utf-8", newline="") as handle:
        json.dump({"schema": VERSION, "request_identity": identity, "job_id": job_id,
                   "created": datetime.now().isoformat()}, handle, ensure_ascii=False)


def hold(path, job_id, run_id, reason):
    path = Path(path)
    if path.exists():
        return
    # 必须在 provider/global slot 的 with 内调用；不能吞写盘失败。
    write_json(path, {"schema": VERSION, "job_id": job_id, "run_id": run_id,
                      "reason": safe_text(reason), "created": datetime.now().isoformat(),
                      "server_cancelled": "unknown"})


def ref_cache(directory, identity):
    path = Path(directory) / "cache" / (digest(identity) + ".json")
    if not path.exists():
        return None
    try:
        obj = strict_json(path.read_bytes().decode("utf-8"))
        if (not isinstance(obj, dict) or obj.get("schema") != VERSION
                or obj.get("request_identity") != identity or obj.get("state") != "ok"):
            raise ArtifactConflict("sample cache is incomplete/failed/conflicting")
        job_id = valid_id(obj["source_job_id"])
        meta_path = Path(directory) / "meta" / (job_id + ".json")
        if sha_file(meta_path) != obj["source_meta_sha256"]:
            raise ArtifactConflict("sample source meta changed")
        data = resume(directory, job_id, identity)
        if data is None or data["response_sha256"] != obj["response_sha256"]:
            raise ArtifactConflict("sample source missing/conflicting")
        return data
    except (KeyError, ValueError, TypeError, OSError) as exc:
        raise ArtifactConflict("sample cache cannot be safely recovered") from exc


def sample_record(directory, job_id, identity, state, meta=None):
    record = {"schema": VERSION, "request_identity": identity, "source_job_id": job_id, "state": state}
    if meta is not None:
        record.update(source_meta_sha256=sha_file(Path(directory) / "meta" / (job_id + ".json")),
                      response_sha256=meta.get("response_sha256"))
    write_json(Path(directory) / "cache" / (digest(identity) + ".json"), record)


def ndjson(stdout):
    rows = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        obj = strict_json(line)
        if not isinstance(obj, dict):
            raise ValueError("non-object JSONL event")
        rows.append(obj)
    if not rows:
        raise ValueError("empty JSONL stream")
    return rows


def parse_codex(stdout):
    rows = ndjson(stdout)
    active = finished = False
    thread_seen = False
    pending, completed, counts = {}, set(), {}
    last_text = ""
    allowed_items = {"agent_message", "reasoning", "todo_list", "command_execution", "file_change",
                     "mcp_tool_call", "web_search", "image_generation"}
    for obj in rows:
        kind = obj.get("type")
        if finished:
            raise ValueError("event after completed turn")
        if kind in ("error", "turn.failed"):
            raise ValueError("Codex error/failed turn")
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
            if item.get("status") in ("failed", "error"):
                raise ValueError("failed item")
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
    if not finished:
        raise ValueError("no complete Codex turn")
    return last_text, counts, {"schema": "codex_exec_jsonl_v3", "terminal": "turn.completed"}


def parse_opencode(stdout):
    rows = ndjson(stdout)
    session = message = None
    active = finished = False
    ids, texts, step_texts, counts = set(), [], [], {}
    expected = {"step_start": "step-start", "step_finish": "step-finish",
                "text": "text", "reasoning": "reasoning", "tool_use": "tool"}
    for obj in rows:
        kind, part = obj.get("type"), obj.get("part")
        if finished:
            raise ValueError("event after successful final step")
        if kind not in expected or not isinstance(part, dict) or part.get("type") != expected[kind]:
            raise ValueError("unknown/error OpenCode event/shape")
        sid, mid, pid = obj.get("sessionID"), part.get("messageID"), part.get("id")
        if (not all(isinstance(value, str) and value for value in (sid, mid, pid))
                or part.get("sessionID") != sid or pid in ids):
            raise ValueError("invalid IDs/duplicate part")
        ids.add(pid)
        if session is None:
            session = sid
        if session != sid:
            raise ValueError("mixed sessions")
        if kind == "step_start":
            if active:
                raise ValueError("unfinished previous step")
            active, message, step_texts = True, mid, []
            continue
        if not active or message != mid:
            raise ValueError("part outside active step/message")
        if kind in ("text", "reasoning"):
            text, clock = part.get("text"), part.get("time")
            if (not isinstance(text, str) or not isinstance(clock, dict)
                    or type(clock.get("end")) not in (int, float) or clock["end"] <= 0):
                raise ValueError("text/reasoning part not completed")
            if kind == "text" and text.strip():
                texts.append(text)
                step_texts.append(text)
        elif kind == "tool_use":
            state, tool = part.get("state"), part.get("tool")
            if (not isinstance(state, dict) or state.get("status") != "completed"
                    or not isinstance(tool, str) or not tool):
                raise ValueError("failed/incomplete tool")
            counts["tool:" + tool] = counts.get("tool:" + tool, 0) + 1
        elif kind == "step_finish":
            reason = part.get("reason")
            if reason not in ("stop", "tool-calls"):
                raise ValueError("unknown/length/filter/error finish")
            active = False
            if reason == "stop":
                if not step_texts:
                    raise ValueError("no answer in final step")
                finished = True
    if not finished or active:
        raise ValueError("no successful final OpenCode step")
    return "\n\n".join(texts), counts, {"schema": "opencode_run_jsonl_v3", "terminal": "step_finish:stop"}
