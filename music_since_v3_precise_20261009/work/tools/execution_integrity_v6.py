"""v6：修 v5 实跑复现的五项实质问题；旧 v4/v5/历史实现只读，不补写。

相对 v5 的变更（对应主会话 integrity_v5_partial_main_verify_20261009_r1 实跑证据）：
1. status 阶段 allowlist 收紧：item.completed 出现 status 必须是 completed；
   in_progress 只允许出现在 item.started/item.updated（缺省仍按已知 fixture 接受）。
   turn.completed 出现 status 必须是 completed。OpenCode 各 part 出现 status 必须
   是 completed；step_finish reason 限定 stop/tool-calls；tool_use state.status 必须
   completed。未知/矛盾/不完整终态一律拒收。allowlist 依据仅为合成 fixture，
   真实 CLI 契约仍未验证，不宣称兼容。
2. 实验包装层见 experiment_calls_v6（显式重采样不再被无条件 break 挡住；
   新样本以新 sampling_key 为身份，不强制改 prompt；pre_submit retry 动态声明）。
3. pre_submit retry 见 experiment_calls_v6（未提交且 retry_safe 可 budget 内新
   immutable attempt，相同冻结 prompt；post_submit_ambiguous/queue_stop 绝不可）。
4. seal/cache miss fail-closed 加强：finalized 中凡无有效 v6 身份绑定的 seal
   （legacy 无身份/坏 schema/jobid 不匹配/缺 identity/损坏）一律阻断，不编造身份；
   有效 v6 seal 但身份无关且账本可验才放行；reserve 查 finalized（沿用 v5）。
5. use_cache=False 见 gpt2_adapter_v6/runner_v6（有可复用来源时返回 exact 来源，
   标 cache_hit=True + cache_bypassed，不 redirect source，不产生未 finalized alias）。

mock-seam 修正：hold/classify_stop 由本模块自己实现（不别名 v4 函数），
classify_stop 只经本模块 globals 查 hold；测试 patch 本模块 origin 即生效。
跨进程复验用本模块（execution_integrity_v6）。

证据边界（重申，不放宽）：seal 是普通可重算 hash 的完整性标记，不是带密钥的
认证或 signature；目录整体可写者能重建整套证据，本模块不防御该威胁模型，只防
意外损坏与单写者纪律。远端输入规范化（native 侧 BOM/CRLF/rstrip 等）仍未验证，
不得伪造“已 source-bound exact 远端 input”，gate 保持关闭。
REAL_EXECUTION_APPROVED=False；无真实模型/CLI/网络调用；测试全临时目录 mock。
"""
from __future__ import annotations

from pathlib import Path

import execution_integrity as old
import execution_integrity_v3 as v3
import execution_integrity_v4 as v4

ArtifactConflict, PolicyBlocked = old.ArtifactConflict, old.PolicyBlocked
sha_text, sha_file, digest = old.sha_text, old.sha_file, old.digest
run_process = old.run_process
strict_json, valid_id = v3.strict_json, v3.valid_id
Slot = v3.Slot
SLOT_DIR = v3.SLOT_DIR
safe_text, safe_metadata, safe_records = v4.safe_text, v4.safe_metadata, v4.safe_records
assert_content_safe = v4.assert_content_safe
write_text, write_json, exclusive_json = v4.write_text, v4.write_json, v4.exclusive_json
release_ticket = v4.release_ticket
model_evidence = v4.model_evidence
# 真实 CLI 事件契约与独立复核证据到位前，真实路径保持关闭；测试只能局部 mock 此值。
REAL_EXECUTION_APPROVED = False
VERSION = "20261009.v6"
INFLIGHT_V4 = "inflight_v4"
INFLIGHT_V5 = "inflight_v5"
INFLIGHT_V6 = "inflight_v6"


# ------------------------------------------------- hold（v6 自己实现）
# 不别名 v4.hold：classify_stop 经本模块 globals 查 hold，测试 patch 本模块
# origin 即生效，避免 v5 的 mock-seam 误绑定（patch v5.hold 不影响 v4.hold）。
def hold(path, job_id, run_id, reason):
    path = Path(path)
    if not path.exists():
        write_json(path, {"schema": VERSION, "job_id": job_id, "run_id": run_id,
                          "reason": safe_text(reason), "created": __import__("datetime").datetime.now().isoformat(),
                          "server_cancelled": "unknown"})


def classify_stop(path, job_id, run_id, reason):
    try:
        hold(path, job_id, run_id, reason)
        return None
    except OSError as exc:
        # 不吞保护失败；返回审计字段。票据绝不清除，不把 OS 释放锁当放行。
        return safe_text(type(exc).__name__ + ": " + str(exc))


def _ndjson(stdout):
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


# ------------------------------------------------------------- 环境身份（v6）
# 只收录源代码可查的键名；此处枚举的是“名字”，真实值只在调用方进程 env 里出现，
# 本模块从不读取 cookie/session-state/secret/private-config 文件或真实凭证值。
_PROXY_PAIRS = (("HTTP_PROXY", "http_proxy"), ("HTTPS_PROXY", "https_proxy"),
                ("ALL_PROXY", "all_proxy"), ("NO_PROXY", "no_proxy"))
# gpt2agent_provider 源代码中实际读取的行为开关（键名来自只读源码检查）。
_GPT2_BEHAVIORAL = ("GPT2AGENT_MAX_ACTIVE_TURNS", "GPT2AGENT_TURN_TIMEOUT_SECONDS",
                    "GPT2AGENT_SUSPECTED_FALLBACK_SECONDS", "GPT2AGENT_ARTIFACT_TIMEOUT_SECONDS",
                    "GPT2AGENT_ARTIFACT_POLL_SECONDS", "GPT2AGENT_PROXY_CHECK_TIMEOUT_SECONDS",
                    "GPT2AGENT_TEXT_ONLY", "GPT2AGENT_PARITY_REPORT")
# 已知指向凭证文件的变量：明确不读取、不 hash，只在 coverage 声明排除。
_GPT2_KNOWN_PRIVATE_EXCLUDED = ("GPT2AGENT_BROWSER_SESSION_FILE",)
_BASE_NAMES = ("PATH", "Path", "APPDATA", "LOCALAPPDATA", "USERPROFILE", "HOME", "NODE_OPTIONS",
               "PYTHONPATH", "PYTHONHOME", "CODEX_HOME", "OPENCODE_CONFIG", "OPENCODE_CONFIG_CONTENT",
               "MUSIC_WEB_ROUTE", "MUSIC_GPT2_CMD", "GPT2AGENT_SAFECHAIN_ROOT", "MUSIC_MAX_CALLS")


def _refuse_sensitive_shape(name, value):
    if not isinstance(value, str):
        raise ValueError("non-string environment value refused: " + name)
    if safe_text(value) != value:
        # 敏感形态：拒请求，不静默跳过（跳过会让不同请求折叠成同一身份）。
        raise ValueError("sensitive-looking environment value refused: " + name)
    upper = name.upper()
    if upper.endswith("_PROXY") or upper == "NO_PROXY":
        if "@" in value or "?" in value:
            # userinfo（user:pass@）或 token-query 会把凭证带进身份与产物；fail-closed。
            raise ValueError("proxy value with userinfo/query refused: " + name)
    return value


def environment_identity(env):
    """绑定已知非私密行为环境；未知 GPT2AGENT_* 保守拒收；凭证永不 hash/落盘。"""
    bound = {}
    try:
        keys = list(env.keys())
    except AttributeError as exc:
        raise ValueError("environment must be a mapping") from exc
    for key in keys:
        if isinstance(key, str) and key.startswith("GPT2AGENT_") and key not in _GPT2_BEHAVIORAL \
                and key not in _GPT2_KNOWN_PRIVATE_EXCLUDED:
            raise ValueError("unknown GPT2AGENT override with unproven effect refused: " + key)
    present_excluded = sorted({key for key in keys if key in _GPT2_KNOWN_PRIVATE_EXCLUDED})
    names = list(_BASE_NAMES) + [name for pair in _PROXY_PAIRS for name in pair] + list(_GPT2_BEHAVIORAL)
    for key in names:
        if key in env:
            bound[key] = sha_text(_refuse_sensitive_shape(key, env[key]))
    return {"nonprivate_sha256": bound, "bound_names": sorted(bound),
            "excluded_private": present_excluded,
            "unknown_gpt2agent_policy": "refuse",
            "coverage": ("allowlisted behavioral values only; proxy userinfo/query refused, "
                         "sensitive-shaped values refused, credentials never read/hashed/persisted; "
                         "private global config and external service not frozen")}


def implementation_identity():
    names = ("execution_integrity.py", "runner.py", "execution_integrity_v3.py",
             "execution_integrity_v4.py", "execution_integrity_v5.py", "execution_integrity_v6.py",
             "runner_v6.py", "gpt2_adapter_v6.py", "experiment_calls_v6.py")
    return {name: sha_file(Path(__file__).with_name(name)) for name in names}


# ------------------------------------------------------- strict 状态合同（v6）
# 缺省 status 按已知合成 fixture 接受；凡出现 status，必须落在该事件/阶段/part 的
# 允许值内。允许值依据仅为离线 fixture，真实 CLI 契约仍未验证，不宣称兼容。
# v5 缺口修正：item.completed 不再接受 in_progress（v5 共用 allowlist 把未完成
# 的 reasoning 当已完成）。in_progress 只属于 item.started/item.updated 阶段。
CODEX_ITEM_STARTED_OK_STATUSES = ("in_progress",)
CODEX_ITEM_COMPLETED_OK_STATUSES = ("completed",)
CODEX_TURN_COMPLETED_OK_STATUSES = ("completed",)
OPENCODE_PART_OK_STATUSES = ("completed",)
OPENCODE_FINISH_OK_STATUSES = ("completed",)


def _require_absent_status(obj, where):
    if isinstance(obj, dict) and "status" in obj:
        raise ValueError("unexpected status on " + where)


def _require_status_in(obj, allowed, where, *, missing_ok=True):
    if not isinstance(obj, dict):
        raise ValueError("bad shape at " + where)
    if "status" not in obj:
        if missing_ok:
            return
        raise ValueError("missing status at " + where)
    if obj.get("status") not in allowed:
        raise ValueError("unknown/conflicting status at " + where + ": " + repr(obj.get("status")))


def parse_codex(stdout):
    rows = _ndjson(stdout)
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
            _require_absent_status(obj, "thread.started")
            if thread_seen or active or not isinstance(obj.get("thread_id"), str) or not obj["thread_id"]:
                raise ValueError("invalid/duplicate thread start")
            thread_seen = True
        elif kind == "turn.started":
            _require_absent_status(obj, "turn.started")
            if not thread_seen or active:
                raise ValueError("invalid/duplicate turn start")
            active = True
        elif kind == "turn.completed":
            _require_status_in(obj, CODEX_TURN_COMPLETED_OK_STATUSES, "turn.completed")
            if not active or pending or not last_text.strip() or not isinstance(obj.get("usage"), dict):
                raise ValueError("incomplete turn/items/body")
            active, finished = False, True
        elif kind in ("item.started", "item.updated", "item.completed"):
            _require_absent_status(obj, kind + " top-level")
            item = obj.get("item")
            if not active or not isinstance(item, dict):
                raise ValueError("item outside turn/bad shape")
            ident, itype = item.get("id"), item.get("type")
            if not isinstance(ident, str) or not ident or itype not in allowed_items or ident in completed:
                raise ValueError("unknown/error/duplicate item")
            if ident in pending and pending[ident] != itype:
                raise ValueError("item type changed")
            # 阶段 allowlist：completed 阶段只收 completed；started/updated 只收 in_progress。
            # 缺省按已知合成 fixture 接受；出现即必须落在阶段允许值内。
            if kind == "item.completed":
                _require_status_in(item, CODEX_ITEM_COMPLETED_OK_STATUSES, "codex item.completed")
            else:
                _require_status_in(item, CODEX_ITEM_STARTED_OK_STATUSES, "codex " + kind)
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
    return last_text, counts, {"schema": "codex_exec_jsonl_v6", "terminal": "turn.completed"}


def parse_opencode(stdout):
    rows = _ndjson(stdout)
    session = message = None
    active = finished = False
    ids, texts, step_texts, counts = set(), [], [], {}
    expected = {"step_start": "step-start", "step_finish": "step-finish",
                "text": "text", "reasoning": "reasoning", "tool_use": "tool"}
    for obj in rows:
        _require_absent_status(obj, "opencode event top-level")
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
            _require_status_in(part, OPENCODE_PART_OK_STATUSES, "step_start part")
            if active:
                raise ValueError("unfinished previous step")
            active, message, step_texts = True, mid, []
            continue
        if not active or message != mid:
            raise ValueError("part outside active step/message")
        if kind in ("text", "reasoning"):
            _require_status_in(part, OPENCODE_PART_OK_STATUSES, kind + " part")
            text, clock = part.get("text"), part.get("time")
            if (not isinstance(text, str) or not isinstance(clock, dict)
                    or type(clock.get("end")) not in (int, float) or clock["end"] <= 0):
                raise ValueError("text/reasoning part not completed")
            if kind == "text" and text.strip():
                texts.append(text)
                step_texts.append(text)
        elif kind == "tool_use":
            _require_status_in(part, OPENCODE_PART_OK_STATUSES, "tool_use part")
            state, tool = part.get("state"), part.get("tool")
            if (not isinstance(state, dict) or state.get("status") != "completed"
                    or not isinstance(tool, str) or not tool):
                raise ValueError("failed/incomplete tool")
            counts["tool:" + tool] = counts.get("tool:" + tool, 0) + 1
        elif kind == "step_finish":
            _require_status_in(part, OPENCODE_FINISH_OK_STATUSES, "step_finish part")
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
    return "\n\n".join(texts), counts, {"schema": "opencode_run_jsonl_v6", "terminal": "step_finish:stop"}


# ------------------------------------------------- seal 绑定与账本扫描（v6）
def identity_digest(identity):
    return digest(identity)


def finalize(directory, job_id, meta):
    directory = Path(directory)
    try:
        request_identity = meta["request_identity"]
    except (KeyError, TypeError) as exc:
        raise ArtifactConflict("cannot seal completion without exact request identity") from exc
    exclusive_json(directory / "finalized" / (job_id + ".json"),
                   {"schema": VERSION, "job_id": job_id,
                    "identity_digest": identity_digest(request_identity),
                    "request_identity": request_identity,
                    "meta_sha256": sha_file(directory / "meta" / (job_id + ".json")),
                    "prompt_sha256": sha_file(directory / meta["prompt_file"]),
                    "output_sha256": sha_file(directory / meta["output_file"]),
                    "seal_note": ("plain recomputable hash integrity marker, not cryptographic "
                                  "authentication or signature; a full-directory writer can rebuild "
                                  "the whole set; guards accidental damage and single-writer discipline only")})


def verify_finalization(directory, job_id, meta):
    directory = Path(directory)
    try:
        marker = strict_json((directory / "finalized" / (job_id + ".json")).read_bytes().decode("utf-8"))
        if (not isinstance(marker, dict) or marker.get("schema") != VERSION or marker.get("job_id") != job_id
                or marker.get("meta_sha256") != sha_file(directory / "meta" / (job_id + ".json"))):
            raise ArtifactConflict("missing/conflicting finalization seal")
        # seal 必须绑定 exact 身份：无绑定（legacy 残留）的 seal 不具归属证明力。
        request_identity = meta.get("request_identity")
        if (marker.get("request_identity") != request_identity
                or marker.get("identity_digest") != identity_digest(request_identity)):
            raise ArtifactConflict("finalization seal not bound to exact request identity")
        for field, hash_field in (("prompt_file", "prompt_sha256"), ("output_file", "output_sha256")):
            rel = meta.get(field)
            path = (directory / rel).resolve() if isinstance(rel, str) else None
            if (path is None or not path.is_relative_to(directory.resolve()) or not path.is_file()
                    or marker.get(hash_field) != sha_file(path)):
                raise ArtifactConflict("finalized artifact missing/tampered/outside run")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ArtifactConflict("cannot verify finalization seal") from exc


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
            raise ArtifactConflict("missing/conflicting exact v6 completion: " + job_id)
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
        raise ArtifactConflict("invalid v6 completion evidence: " + job_id) from exc


def _readable_ledger(directory, folder):
    records = {}
    base = Path(directory) / folder
    if base.is_dir():
        for candidate in sorted(base.glob("*.json")):
            try:
                record = strict_json(candidate.read_bytes().decode("utf-8"))
                if not isinstance(record, dict):
                    raise ValueError("non-object ledger")
            except (ValueError, TypeError, OSError) as exc:
                raise ArtifactConflict("run ledger unreadable; no safe cache miss: " + candidate.name) from exc
            records[candidate.stem] = record
    return records


def _is_valid_bound_seal(marker, stem):
    """有效 v6 身份绑定 seal：schema 本版、job_id 自洽、有 request_identity 且 digest 自洽。
    legacy 无身份 seal、坏 schema、jobid 不匹配、缺 identity 一律返回 False（不可验证）。"""
    return (isinstance(marker, dict) and marker.get("schema") == VERSION
            and marker.get("job_id") == stem
            and isinstance(marker.get("request_identity"), dict)
            and marker.get("identity_digest") == digest(marker["request_identity"]))


def _fail_closed_on_orphan_residue(directory, identity, owned_stems):
    # 凡无法归属有效账本、又与本次采样内容相撞（或根本无账本可对）的残留，一律拒收。
    prompt_sha = identity.get("prompt_sha256")
    for prompt_file in sorted((directory / "prompts").glob("*.txt")):
        if prompt_file.stem in owned_stems:
            continue
        try:
            content_sha = sha_file(prompt_file)
        except OSError as exc:
            raise ArtifactConflict("orphan prompt unreadable; no safe cache miss") from exc
        if content_sha == prompt_sha:
            raise ArtifactConflict("orphan prompt with same sample content; no owning ledger: " + prompt_file.name)
    for output_file in sorted((directory / "outputs").glob("*.md")):
        if output_file.stem in owned_stems:
            continue
        # 无任何账本可对的输出残留：不能证明它与本次提交无关，fail-closed。
        raise ArtifactConflict("orphan output without owning ledger; inspect, do not resubmit: " + output_file.name)


def reserve(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    for folder, suffix in (("prompts", ".txt"), ("outputs", ".md"), ("pending", ".json"),
                           ("meta", ".json"), ("finalized", ".json")):
        if (directory / folder / (job_id + suffix)).exists():
            raise ArtifactConflict("existing/incomplete job is read-only: " + job_id)
    exclusive_json(directory / "pending" / (job_id + ".json"),
                   {"schema": VERSION, "request_identity": identity, "job_id": job_id,
                    "created": __import__("datetime").datetime.now().isoformat()})


def ref_cache(directory, identity):
    directory = Path(directory)
    path = directory / "cache" / (digest(identity) + ".json")
    if not path.exists():
        # 索引丢失不等于未提交。pending/meta/finalized 三来源缺一不可；
        # 无法归属的残留一律 fail-closed，不能为同一采样另取 job 偷跑。
        # v6 加强：finalized 中无有效本版身份绑定的 seal（legacy/坏/缺身份）
        # 不能编造身份，一律保守阻断；只有“有效 v6 seal 且身份明确无关”
        # 才放行（正常 unrelated 完整样本不误封）。
        pending = _readable_ledger(directory, "pending")
        meta = _readable_ledger(directory, "meta")
        finalized = _readable_ledger(directory, "finalized")
        for stem, record in list(pending.items()) + list(meta.items()):
            if record.get("request_identity") == identity:
                raise ArtifactConflict("sample ledger exists but cache index missing; inspect, do not resubmit")
        for stem, marker in finalized.items():
            if marker.get("request_identity") == identity or marker.get("identity_digest") == digest(identity):
                raise ArtifactConflict("completion seal exists for sample but cache index missing; inspect, do not resubmit")
        for stem, marker in sorted(finalized.items()):
            if _is_valid_bound_seal(marker, stem):
                continue
            raise ArtifactConflict("unverifiable completion seal without exact v6 identity binding; "
                                   "inspect, do not resubmit: " + stem)
        _fail_closed_on_orphan_residue(directory, identity, set(pending) | set(meta) | set(finalized))
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
    # 旧 v4/v5 inflight 与新 v6 ticket 同等阻断；即便 hold 写盘失败，已 fsync 的票据仍在。
    # 旧 hold/ticket 永不由此迁移或删除（只读尊重）。
    if hold_file.exists():
        return False
    for folder in (INFLIGHT_V4, INFLIGHT_V5, INFLIGHT_V6):
        if any((hold_file.parent / folder).glob("*.json")):
            return False
    return True


def submission_ticket(hold_file, directory, job_id, identity):
    hold_file = Path(hold_file)
    if not queue_open(hold_file):
        raise PolicyBlocked("provider held or unclassified inflight submission; no replay")
    ticket = hold_file.parent / INFLIGHT_V6 / (digest({"run": str(Path(directory).resolve()), "job": job_id}) + ".json")
    exclusive_json(ticket, {"schema": VERSION, "run_directory": str(Path(directory).resolve()),
                            "job_id": job_id, "request_identity_sha256": digest(identity),
                            "identity_digest": digest(identity),
                            "state": "may_submit_or_inflight", "server_cancelled": "unknown"})
    return ticket
