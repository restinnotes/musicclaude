"""Offline-first execution integrity primitives for v7.

The real execution gate is deliberately closed.  This module records immutable
request identities, validates exact on-disk evidence, and keeps ambiguous work
held.  Its seals are ordinary hashes, not authentication against a writer that
can rewrite the entire run directory.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import execution_integrity as old
import execution_integrity_v3 as v3

ArtifactConflict = old.ArtifactConflict
PolicyBlocked = old.PolicyBlocked
sha_text = old.sha_text
sha_file = old.sha_file
digest = old.digest
run_process = old.run_process
Slot = v3.Slot
SLOT_DIR = v3.SLOT_DIR
strict_json = v3.strict_json
valid_id = v3.valid_id

VERSION = "20261009.v7"
REAL_EXECUTION_APPROVED = False
INFLIGHT_DIR = "inflight_v7"
INFLIGHT_OLD = ("inflight_v4", "inflight_v5", "inflight_v6")
SEAL_LIMITATION = (
    "plain recomputable SHA-256 integrity marker; not a MAC, signature, or defense "
    "against a writer able to rebuild the whole run directory"
)

HANDLE_NAME = (
    r"(?:thread[_-]?id|session[_-]?(?:id|handle)|conversation[_-]?id|"
    r"message[_-]?id|parent[_-]?id)"
)
HANDLE_RE = re.compile(r"^" + HANDLE_NAME + r"$", re.I)
HANDLE_QUOTED = re.compile(r"([\"']?" + HANDLE_NAME + r"[\"']?\s*[=:]\s*)([\"'])(.*?)\2", re.I)
HANDLE_PLAIN = re.compile(r"([\"']?" + HANDLE_NAME + r"[\"']?\s*[=:]\s*)[^\s,;\"'&}]+", re.I)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")

# These are the active source files named in the handoff.  Hashing their source
# does not read runtime state, credentials, cookies, or private configuration.
ACTIVE_PROVIDER_SOURCE_RELATIVE = (
    "tools/chatgpt_web/linux_native_provider_runner.py",
    "tools/chatgpt_web/native_prepared_http_probe.py",
    "src/chatgpt_provider/gpt2agent_provider.py",
    "src/chatgpt_provider/headless_native_provider.py",
)

PRE_SUBMIT_PROOF_SCHEMA = "gpt2_pre_submit_proof_v7"
PRE_SUBMIT_CONTRACT = "gpt2agent_provider.ProviderError.PRE_SUBMIT.no-submit.v1"


def safe_text(text):
    text = old.safe_text(str(text))
    text = HANDLE_QUOTED.sub(lambda m: m[1] + m[2] + "<redacted>" + m[2], text)
    return HANDLE_PLAIN.sub(lambda m: m[1] + "<redacted>", text)


def safe_metadata(obj):
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            name = str(key)
            if HANDLE_RE.fullmatch(name) or old.PRIVATE_KEY_RE.search(name):
                out[name] = "<redacted>"
            else:
                out[name] = safe_metadata(value)
        return out
    if isinstance(obj, list):
        return [safe_metadata(value) for value in obj]
    if isinstance(obj, tuple):
        return [safe_metadata(value) for value in obj]
    if isinstance(obj, str):
        return safe_text(obj)
    return obj


def safe_records(text):
    text = str(text)
    try:
        return json.dumps(safe_metadata(strict_json(text)), ensure_ascii=False, allow_nan=False) + "\n"
    except (ValueError, TypeError):
        rows = []
        for line in text.splitlines():
            try:
                rows.append(json.dumps(safe_metadata(strict_json(line)), ensure_ascii=False, allow_nan=False))
            except (ValueError, TypeError):
                rows.append(safe_text(line))
        return "\n".join(rows) + ("\n" if rows else "")


def assert_content_safe(text):
    if not isinstance(text, str) or safe_text(text) != text:
        raise ValueError("sensitive-looking content rejected; body not persisted")


def _fsync_directory(directory):
    """Best-effort directory fsync where the platform supports opening dirs."""
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        fd = os.open(str(directory), flags)
    except OSError:
        return False
    try:
        os.fsync(fd)
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def _write_fsynced(path, text, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "x" if exclusive else "w"
    with path.open(mode, encoding="utf-8", newline="") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_directory(path.parent)
    return path


def write_text(path, text):
    if not isinstance(text, str):
        raise TypeError("text artifact must be a string")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        _write_fsynced(temp, text)
        os.replace(temp, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
    return path


def write_json(path, obj):
    text = json.dumps(safe_metadata(obj), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    return write_text(path, text)


def exclusive_json(path, obj):
    text = json.dumps(safe_metadata(obj), ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    return _write_fsynced(path, text, exclusive=True)


# Environment values are read only after their names have been allowlisted.
# Known credential/session-file variables are excluded by name without reading
# their values.  Unknown GPT2AGENT_* overrides fail closed based on key name.
_PROXY_PAIRS = (("HTTP_PROXY", "http_proxy"), ("HTTPS_PROXY", "https_proxy"),
                ("ALL_PROXY", "all_proxy"), ("NO_PROXY", "no_proxy"))
_GPT2_BEHAVIORAL = (
    "GPT2AGENT_MAX_ACTIVE_TURNS", "GPT2AGENT_TURN_TIMEOUT_SECONDS",
    "GPT2AGENT_SUSPECTED_FALLBACK_SECONDS", "GPT2AGENT_ARTIFACT_TIMEOUT_SECONDS",
    "GPT2AGENT_ARTIFACT_POLL_SECONDS", "GPT2AGENT_PROXY_CHECK_TIMEOUT_SECONDS",
    "GPT2AGENT_TEXT_ONLY", "GPT2AGENT_PARITY_REPORT",
    "GPT2AGENT_HTTP_PROFILE", "GPT2AGENT_IMPORTED_SHELL_HEADERS",
    "GPT2AGENT_PAYLOAD_PROFILE", "GPT2AGENT_PREPARE_ORDER",
    "GPT2AGENT_PREPARE_PROFILE", "GPT2AGENT_PREPARE_WAIT_SECONDS",
    "GPT2AGENT_REQUEST_AUDIT_FILE", "GPT2AGENT_RUNTIME_DIR",
    "GPT2AGENT_TURN_TRACE_HEADER",
)
_GPT2_PRIVATE_EXCLUDED = (
    "GPT2AGENT_BROWSER_SESSION_FILE",
)
_BASE_ENV_NAMES = (
    "PATH", "Path", "APPDATA", "LOCALAPPDATA", "USERPROFILE", "HOME",
    "NODE_OPTIONS", "PYTHONPATH", "PYTHONHOME", "CODEX_HOME",
    "OPENCODE_CONFIG", "MUSIC_WEB_ROUTE", "MUSIC_GPT2_CMD",
    "GPT2AGENT_SAFECHAIN_ROOT", "MUSIC_MAX_CALLS", "MUSIC_MAX_GEMINI_CALLS",
)


def _safe_env_value(name, value):
    if not isinstance(value, str):
        raise ValueError("non-string environment value refused: " + name)
    if safe_text(value) != value:
        raise ValueError("sensitive-shaped environment value refused: " + name)
    if name.upper().endswith("_PROXY") or name.upper() == "NO_PROXY":
        if "@" in value or "?" in value:
            raise ValueError("proxy userinfo/query refused: " + name)
    return value


def environment_identity(env):
    """Hash known nonprivate behavior values; never read credential values."""
    if not hasattr(env, "keys") or not hasattr(env, "__contains__"):
        raise ValueError("environment must be a mapping")
    keys = list(env.keys())
    known_gpt2 = {name.upper() for name in _GPT2_BEHAVIORAL}
    excluded_gpt2 = {name.upper() for name in _GPT2_PRIVATE_EXCLUDED}
    for key in keys:
        if not isinstance(key, str):
            continue
        normalized = key.upper()
        if normalized == "OPENCODE_CONFIG_CONTENT":
            raise ValueError("inline configuration value excluded; cannot freeze safely")
        if normalized.startswith("GPT2AGENT_") and normalized not in known_gpt2 | excluded_gpt2:
            raise ValueError("unknown GPT2AGENT override refused by variable name: " + key)
    allowed = {name.upper() for name in _BASE_ENV_NAMES}
    allowed.update(name.upper() for pair in _PROXY_PAIRS for name in pair)
    allowed.update(known_gpt2)
    bound = {}
    for key in keys:
        if isinstance(key, str) and key.upper() in allowed:
            bound[key] = sha_text(_safe_env_value(key, env[key]))
    excluded_present = sorted(key for key in keys
                              if isinstance(key, str) and key.upper() in excluded_gpt2)
    return {
        "nonprivate_sha256": bound,
        "bound_names": sorted(bound),
        "excluded_private_variable_names": excluded_present,
        "unknown_gpt2agent_policy": "refuse without reading values",
        "coverage": (
            "allowlisted behavioral values only; both proxy cases bound; proxy userinfo/query "
            "and sensitive-shaped values refused; credential/session variables excluded by name; "
            "private global config and external service are not frozen"
        ),
    }


def implementation_identity():
    tools_dir = Path(__file__).resolve().parent
    names = (
        "execution_integrity.py", "execution_integrity_v3.py", "execution_integrity_v4.py",
        "runner.py", "execution_integrity_v7.py", "gpt2_adapter_v7.py",
        "runner_v7.py", "experiment_calls_v7.py",
    )
    return {name: sha_file(tools_dir / name) for name in names if (tools_dir / name).is_file()}


def active_provider_source_binding(root):
    root = Path(root)
    files = {}
    missing = []
    for relative in ACTIVE_PROVIDER_SOURCE_RELATIVE:
        path = root / Path(relative)
        if path.is_file():
            files[relative] = sha_file(path)
        else:
            files[relative] = None
            missing.append(relative)
    return {"files": files, "complete": not missing, "missing": missing}


def _require_sha(value, where):
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ValueError("invalid SHA-256 binding at " + where)
    return value


def verify_pre_submit_proof(meta, identity):
    """Accept only the exact structured, source-bound no-submit proof contract."""
    if not isinstance(meta, dict) or not isinstance(identity, dict):
        return False
    proof = meta.get("pre_submit_proof")
    if not isinstance(proof, dict):
        return False
    producer = identity.get("producer")
    active = producer.get("active_provider_sources") if isinstance(producer, dict) else None
    if not isinstance(active, dict) or active.get("complete") is not True:
        return False
    source_files = active.get("files")
    if (not isinstance(source_files, dict) or set(source_files) != set(ACTIVE_PROVIDER_SOURCE_RELATIVE)
            or any(not isinstance(source_files.get(name), str)
                   or not SHA256_RE.fullmatch(source_files[name]) for name in ACTIVE_PROVIDER_SOURCE_RELATIVE)):
        return False
    required = {
        "schema": PRE_SUBMIT_PROOF_SCHEMA,
        "contract": PRE_SUBMIT_CONTRACT,
        "provider_error_type": "ProviderError",
        "phase": "pre_submit",
        "retryable": True,
        "ambiguous": False,
        "submit_callback_reached": False,
        "model_request_sent": False,
        "automatic_retry": False,
        "request_identity_sha256": digest(identity),
        "producer_identity_sha256": digest(producer),
        "source_files": source_files,
    }
    if any(proof.get(key) != value for key, value in required.items()):
        return False
    if (meta.get("status") != "failed" or meta.get("failure_phase") != "pre_submit"
            or meta.get("retry_safe") is not True or meta.get("queue_stop") is not False
            or meta.get("terminal_verified") is not False
            or meta.get("submission_state") != "proven_not_submitted"):
        return False
    try:
        _require_sha(proof.get("request_identity_sha256"), "pre_submit.request_identity_sha256")
        _require_sha(proof.get("producer_identity_sha256"), "pre_submit.producer_identity_sha256")
    except ValueError:
        return False
    return True


def identity_digest(identity):
    return digest(identity)


def _inside(directory, relative):
    if not isinstance(relative, str) or not relative:
        raise ArtifactConflict("missing artifact locator")
    root = Path(directory).resolve()
    path = (Path(directory) / relative).resolve()
    if not path.is_relative_to(root):
        raise ArtifactConflict("artifact locator outside run")
    return path


def run_artifact_path(directory, relative):
    """Resolve a new artifact under a run directory without following escapes."""
    root = Path(directory).resolve()
    candidate = Path(directory) / relative
    parent = candidate.parent.resolve()
    if not parent.is_relative_to(root):
        raise ArtifactConflict("artifact parent escapes run directory")
    if candidate.exists() and candidate.is_symlink():
        raise ArtifactConflict("symlink artifact path rejected")
    return parent / candidate.name


def _read_json_object(path, what):
    try:
        value = strict_json(Path(path).read_bytes().decode("utf-8"))
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        raise ArtifactConflict(what + " unreadable; no safe cache miss") from exc
    if not isinstance(value, dict):
        raise ArtifactConflict(what + " must be a JSON object")
    return value


def finalize(directory, job_id, meta):
    directory = Path(directory)
    valid_id(job_id)
    identity = meta.get("request_identity") if isinstance(meta, dict) else None
    if not isinstance(identity, dict) or meta.get("job_id") != job_id:
        raise ArtifactConflict("cannot seal without exact request identity and job id")
    prompt = _inside(directory, meta.get("prompt_file"))
    output = _inside(directory, meta.get("output_file"))
    if not prompt.is_file() or not output.is_file():
        raise ArtifactConflict("cannot seal missing prompt/output")
    marker = {
        "schema": VERSION,
        "job_id": job_id,
        "request_identity": identity,
        "identity_digest": identity_digest(identity),
        "meta_sha256": sha_file(directory / "meta" / (job_id + ".json")),
        "prompt_sha256": sha_file(prompt),
        "output_sha256": sha_file(output),
        "seal_limitation": SEAL_LIMITATION,
    }
    exclusive_json(run_artifact_path(directory, "finalized/" + job_id + ".json"), marker)


def verify_finalization(directory, job_id, meta):
    directory = Path(directory)
    try:
        marker = _read_json_object(directory / "finalized" / (job_id + ".json"), "finalization seal")
        identity = meta.get("request_identity") if isinstance(meta, dict) else None
        if (not isinstance(identity, dict) or meta.get("job_id") != job_id
                or marker.get("schema") != VERSION or marker.get("job_id") != job_id
                or marker.get("request_identity") != identity
                or marker.get("identity_digest") != identity_digest(identity)
                or marker.get("meta_sha256") != sha_file(directory / "meta" / (job_id + ".json"))):
            raise ArtifactConflict("missing/conflicting exact identity-bound v7 seal")
        for field, hash_field in (("prompt_file", "prompt_sha256"), ("output_file", "output_sha256")):
            artifact = _inside(directory, meta.get(field))
            if not artifact.is_file() or marker.get(hash_field) != sha_file(artifact):
                raise ArtifactConflict("finalized prompt/output missing, changed, or outside run")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ArtifactConflict("cannot verify exact v7 finalization seal") from exc
    return marker


def _validate_meta(directory, stem, meta, pending, marker):
    if (not isinstance(meta, dict) or meta.get("schema") != VERSION or meta.get("job_id") != stem
            or not isinstance(meta.get("request_identity"), dict)
            or meta.get("request_identity_sha256") != identity_digest(meta["request_identity"])
            or not isinstance(meta.get("producer_identity"), dict)
            or meta.get("producer_identity") != meta["request_identity"].get("producer")):
        raise ArtifactConflict("invalid/legacy meta ownership record: " + stem)
    identity = meta["request_identity"]
    if meta.get("prompt_sha256") != identity.get("prompt_sha256"):
        raise ArtifactConflict("meta prompt identity mismatch: " + stem)
    expected_pending = pending.get(stem)
    if (not isinstance(expected_pending, dict) or expected_pending.get("schema") != VERSION
            or expected_pending.get("job_id") != stem
            or expected_pending.get("request_identity") != identity
            or expected_pending.get("request_identity_sha256") != identity_digest(identity)):
        raise ArtifactConflict("missing/conflicting pending ownership record: " + stem)
    prompt = _inside(directory, meta.get("prompt_file"))
    output = _inside(directory, meta.get("output_file"))
    if meta.get("prompt_file") != "prompts/" + stem + ".txt" or meta.get("output_file") != "outputs/" + stem + ".md":
        raise ArtifactConflict("noncanonical prompt/output locator: " + stem)
    if not prompt.is_file() or sha_file(prompt) != identity.get("prompt_sha256"):
        raise ArtifactConflict("missing/conflicting frozen prompt: " + stem)
    if not output.is_file():
        raise ArtifactConflict("missing output artifact: " + stem)
    if marker is None:
        raise ArtifactConflict("meta exists without finalization seal: " + stem)
    verify_finalization(directory, stem, meta)
    status = meta.get("status")
    if status == "ok":
        if (meta.get("terminal_verified") is not True or meta.get("queue_stop") is not False
                or not isinstance(meta.get("terminal"), dict)
                or not isinstance(meta.get("response_sha256"), str)
                or meta.get("response_sha256") != sha_file(output)):
            raise ArtifactConflict("invalid success terminal/output binding: " + stem)
        body = output.read_bytes().decode("utf-8")
        if not body.strip():
            raise ArtifactConflict("empty successful output: " + stem)
        assert_content_safe(body)
    elif status == "failed":
        if meta.get("retry_safe") is True:
            if not verify_pre_submit_proof(meta, identity):
                raise ArtifactConflict("retry_safe claim lacks exact source-bound pre-submit proof: " + stem)
        elif meta.get("queue_stop") is not True and meta.get("terminal_verified") is not True:
            raise ArtifactConflict("failed record lacks terminal or persistent hold: " + stem)
    else:
        raise ArtifactConflict("unknown completion state: " + stem)
    return meta


def _read_inventory(directory):
    directory = Path(directory)
    inventory = {folder: {} for folder in ("pending", "meta", "finalized", "cache")}
    for folder in inventory:
        base = directory / folder
        if base.is_symlink():
            raise ArtifactConflict("ledger directory symlink rejected: " + folder)
        if not base.is_dir():
            continue
        if not base.resolve().is_relative_to(directory.resolve()):
            raise ArtifactConflict("ledger directory escapes run: " + folder)
        for path in sorted(base.glob("*.json")):
            record = _read_json_object(path, folder + " ledger " + path.name)
            inventory[folder][path.stem] = record
    return inventory


def _validate_inventory(directory, requested_identity):
    inventory = _read_inventory(directory)
    pending = inventory["pending"]
    metas = inventory["meta"]
    seals = inventory["finalized"]
    for folder in ("prompts", "outputs"):
        base = Path(directory) / folder
        if base.is_symlink() or (base.is_dir() and not base.resolve().is_relative_to(Path(directory).resolve())):
            raise ArtifactConflict("artifact directory symlink/escape rejected: " + folder)
    prompt_base = Path(directory) / "prompts"
    output_base = Path(directory) / "outputs"
    prompt_files = {p.stem: p for p in prompt_base.glob("*.txt")} if prompt_base.is_dir() else {}
    output_files = {p.stem: p for p in output_base.glob("*.md")} if output_base.is_dir() else {}
    stems = set(pending) | set(metas) | set(seals) | set(prompt_files) | set(output_files)
    validated = {}
    for stem in sorted(stems):
        if stem not in pending:
            raise ArtifactConflict("artifact/seal has no exact pending owner; inspect, do not resubmit: " + stem)
        record = pending[stem]
        if (record.get("schema") != VERSION or record.get("job_id") != stem
                or not isinstance(record.get("request_identity"), dict)
                or record.get("request_identity_sha256") != identity_digest(record["request_identity"])):
            raise ArtifactConflict("invalid/legacy pending ownership record: " + stem)
        if stem not in metas:
            # A pending-only record can have crossed the submission boundary.
            raise ArtifactConflict("incomplete pending record; submission state unknown: " + stem)
        if stem not in seals:
            raise ArtifactConflict("missing/legacy finalization seal: " + stem)
        validated[stem] = _validate_meta(directory, stem, metas[stem], pending, seals[stem])
    # Cache indexes are never authority by filename alone.  Every index must be
    # exact, and its named source must validate as an exact successful record.
    for stem, record in inventory["cache"].items():
        if (record.get("schema") != VERSION or not isinstance(record.get("request_identity"), dict)
                or record.get("identity_digest") != identity_digest(record["request_identity"])
                or stem != identity_digest(record["request_identity"])):
            raise ArtifactConflict("invalid/legacy cache ownership record: " + stem)
        source_id = record.get("source_job_id")
        if not isinstance(source_id, str) or source_id not in validated:
            raise ArtifactConflict("cache source missing exact ledger owner: " + stem)
        source = validated[source_id]
        if source.get("cache_hit") is True:
            raise ArtifactConflict("cache alias cannot replace the original sample source: " + stem)
        expected_status = ("ok" if record.get("state") == "ok"
                           else "failed" if record.get("state") == "failed_terminal" else None)
        if (source.get("request_identity") != record["request_identity"]
                or source.get("status") != expected_status
                or record.get("source_meta_sha256") != sha_file(Path(directory) / "meta" / (source_id + ".json"))
                or record.get("response_sha256") != source.get("response_sha256")):
            raise ArtifactConflict("cache source identity/state/digest mismatch: " + stem)
    return validated, inventory


def _has_exact_prior(validated, identity):
    return [(job_id, meta) for job_id, meta in validated.items()
            if meta.get("request_identity") == identity]


def _safe_pre_submit_only(rows):
    return bool(rows) and all(meta.get("status") == "failed"
                              and verify_pre_submit_proof(meta, meta.get("request_identity"))
                              for _, meta in rows)


def resume(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    path = directory / "meta" / (job_id + ".json")
    if not path.exists():
        return None
    try:
        data = _read_json_object(path, "completion meta")
        if (data.get("schema") != VERSION or data.get("job_id") != job_id
                or data.get("request_identity") != identity
                or data.get("producer_identity") != identity.get("producer")
                or data.get("status") != "ok" or data.get("terminal_verified") is not True
                or data.get("queue_stop") is not False or not isinstance(data.get("terminal"), dict)):
            raise ArtifactConflict("missing/conflicting exact v7 completion: " + job_id)
        _, inventory = _validate_inventory(directory, identity)
        cache = inventory["cache"].get(identity_digest(identity))
        if (not isinstance(cache, dict) or cache.get("request_identity") != identity
                or cache.get("state") != "ok"):
            raise ArtifactConflict("exact successful completion lacks an exact cache ownership index")
        output = _inside(directory, data.get("output_file"))
        body = output.read_bytes().decode("utf-8")
        assert_content_safe(body)
        return dict(data, resumed=True, consumer_identity=identity["producer"])
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        if isinstance(exc, ArtifactConflict):
            raise
        raise ArtifactConflict("invalid v7 completion evidence: " + job_id) from exc


def ref_cache(directory, identity):
    directory = Path(directory)
    validated, inventory = _validate_inventory(directory, identity)
    path = directory / "cache" / (identity_digest(identity) + ".json")
    matching = _has_exact_prior(validated, identity)
    if not path.exists():
        if matching and not _safe_pre_submit_only(matching):
            raise ArtifactConflict("same request has prior completion without exact cache; inspect, do not resubmit")
        return None
    try:
        obj = _read_json_object(path, "sample cache")
        if (obj.get("schema") != VERSION or obj.get("identity_digest") != identity_digest(identity)
                or obj.get("request_identity") != identity):
            raise ArtifactConflict("sample cache identity/schema conflict")
        state = obj.get("state")
        source_id = valid_id(obj.get("source_job_id"))
        source = validated.get(source_id)
        if source is None or source.get("request_identity") != identity:
            raise ArtifactConflict("cache source is not an exact owned sample")
        if source.get("cache_hit") is True:
            raise ArtifactConflict("cache alias cannot replace the original sample source")
        if state != "ok" or source.get("status") != "ok":
            raise ArtifactConflict("failed/unknown sample cache is not resumable")
        if obj.get("source_meta_sha256") != sha_file(directory / "meta" / (source_id + ".json")):
            raise ArtifactConflict("sample source meta changed")
        if obj.get("response_sha256") != source.get("response_sha256"):
            raise ArtifactConflict("sample source response changed")
        return dict(source, resumed=False)
    except (KeyError, ValueError, TypeError, OSError, UnicodeError) as exc:
        if isinstance(exc, ArtifactConflict):
            raise
        raise ArtifactConflict("sample cache cannot be recovered safely") from exc


def reserve(directory, job_id, identity):
    directory = Path(directory)
    valid_id(job_id)
    validated, _ = _validate_inventory(directory, identity)
    matching = _has_exact_prior(validated, identity)
    if matching and not _safe_pre_submit_only(matching):
        cache = (directory / "cache" / (identity_digest(identity) + ".json"))
        cache_record = _read_json_object(cache, "sample cache") if cache.exists() else None
        if not (cache_record and cache_record.get("state") == "ok"
                and cache_record.get("request_identity") == identity):
            raise ArtifactConflict("same request already has non-retryable owned evidence")
    for folder, suffix in (("prompts", ".txt"), ("outputs", ".md"), ("pending", ".json"),
                           ("meta", ".json"), ("finalized", ".json")):
        if (directory / folder / (job_id + suffix)).exists():
            raise ArtifactConflict("existing/incomplete job is read-only: " + job_id)
    exclusive_json(run_artifact_path(directory, "pending/" + job_id + ".json"), {
        "schema": VERSION, "job_id": job_id, "request_identity": identity,
        "request_identity_sha256": identity_digest(identity),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    })


def sample_record(directory, job_id, identity, state, meta=None):
    if state not in ("ok", "failed_terminal"):
        raise ValueError("only terminal outcomes may enter the sample cache index")
    if not isinstance(meta, dict) or meta.get("request_identity") != identity:
        raise ArtifactConflict("cache index requires exact completion metadata")
    path = run_artifact_path(directory, "cache/" + identity_digest(identity) + ".json")
    if path.exists():
        prior = _read_json_object(path, "sample cache")
        if prior.get("source_job_id") != job_id or prior.get("request_identity") != identity:
            raise ArtifactConflict("cannot redirect original sample source")
    write_json(path, {
        "schema": VERSION, "request_identity": identity,
        "identity_digest": identity_digest(identity), "source_job_id": job_id,
        "state": state, "source_meta_sha256": sha_file(Path(directory) / "meta" / (job_id + ".json")),
        "response_sha256": meta.get("response_sha256"),
    })


def queue_open(hold_file):
    hold_file = Path(hold_file)
    if hold_file.exists():
        return False
    for folder in (*INFLIGHT_OLD, INFLIGHT_DIR):
        base = hold_file.parent / folder
        if base.is_dir() and any(base.glob("*.json")):
            return False
    return True


def submission_ticket(hold_file, directory, job_id, identity):
    hold_file = Path(hold_file)
    if not queue_open(hold_file):
        raise PolicyBlocked("provider held or unclassified inflight submission; no replay")
    valid_id(job_id)
    ticket = hold_file.parent / INFLIGHT_DIR / (
        digest({"run": str(Path(directory).resolve()), "job": job_id}) + ".json"
    )
    exclusive_json(ticket, {
        "schema": VERSION, "run_directory": str(Path(directory).resolve()),
        "job_id": job_id, "request_identity_sha256": identity_digest(identity),
        "state": "may_submit_or_inflight", "server_cancelled": "unknown",
        "created_utc": datetime.now(timezone.utc).isoformat(),
    })
    return ticket


def hold(path, job_id, run_id, reason):
    path = Path(path)
    if path.exists():
        return
    write_json(path, {
        "schema": VERSION, "job_id": job_id, "run_id": run_id,
        "reason": safe_text(reason), "created_utc": datetime.now(timezone.utc).isoformat(),
        "server_cancelled": "unknown",
    })


def classify_stop(path, job_id, run_id, reason):
    # Local-module lookup is intentional: patching execution_integrity_v7.hold
    # must exercise the same failure path as production code.
    try:
        hold(path, job_id, run_id, reason)
        return None
    except OSError as exc:
        return safe_text(type(exc).__name__ + ": " + str(exc))


def release_ticket(ticket):
    ticket = Path(ticket)
    if ticket.parent.name != INFLIGHT_DIR:
        raise ArtifactConflict("refusing to release a non-v7 inflight ticket")
    ticket.unlink()
    _fsync_directory(ticket.parent)


def model_evidence(metadata, requested):
    metadata = metadata if isinstance(metadata, dict) else {}
    summary = metadata.get("server_metadata_summary")
    found = []
    if isinstance(summary, dict):
        slug = summary.get("model_slug")
        if isinstance(slug, str) and slug.strip():
            found.append(("server_metadata_summary.model_slug", slug))
        slugs = summary.get("resolved_model_slugs")
        if isinstance(slugs, list) and slugs and all(isinstance(x, str) and x.strip() for x in slugs):
            found.extend(("server_metadata_summary.resolved_model_slugs", x) for x in slugs)
    normalize = lambda value: value.strip().lower().replace(".", "-").replace("_", "-")
    values = sorted({value for _, value in found})
    verdict = "unverified" if not values else "match" if all(normalize(x) == normalize(requested) for x in values) else "mismatch"
    return {
        "verdict": verdict, "server_slugs": values,
        "fields": sorted({path for path, _ in found}),
        "contract": "only root server_metadata_summary fields count; client/request fields are not backend proof",
    }


def ndjson(stdout):
    if not isinstance(stdout, str):
        raise ValueError("event stream must be text")
    rows = []
    for line in stdout.splitlines():
        if not line.strip():
            continue
        item = strict_json(line)
        if not isinstance(item, dict):
            raise ValueError("non-object JSONL event")
        rows.append(item)
    if not rows:
        raise ValueError("empty JSONL stream")
    return rows


def _status(obj, allowed, where, *, missing_ok=True):
    if "status" not in obj:
        if missing_ok:
            return
        raise ValueError("missing status at " + where)
    if not isinstance(obj.get("status"), str) or obj.get("status") not in allowed:
        raise ValueError("unknown/conflicting/incomplete status at " + where)


CODEX_ITEM_STARTED_STATUSES = ("in_progress",)
CODEX_ITEM_COMPLETED_STATUSES = ("completed",)
CODEX_TURN_COMPLETED_STATUSES = ("completed",)
OPENCODE_PART_STATUSES = ("completed",)
OPENCODE_FINISH_STATUSES = ("completed",)


def parse_codex(stdout):
    rows = ndjson(stdout)
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
            if "status" in obj:
                raise ValueError("unexpected status at thread.started")
            if set(obj) != {"type", "thread_id"}:
                raise ValueError("unrecognized thread.started fixture shape")
            if thread_seen or active or not isinstance(obj.get("thread_id"), str) or not obj["thread_id"]:
                raise ValueError("invalid/duplicate thread start")
            thread_seen = True
        elif kind == "turn.started":
            if "status" in obj:
                raise ValueError("unexpected status at turn.started")
            if set(obj) != {"type"}:
                raise ValueError("unrecognized turn.started fixture shape")
            if not thread_seen or active:
                raise ValueError("invalid/duplicate turn start")
            active = True
        elif kind == "turn.completed":
            fixture_status_omission = "status" not in obj and set(obj) == {"type", "usage"}
            _status(obj, CODEX_TURN_COMPLETED_STATUSES, "turn.completed", missing_ok=fixture_status_omission)
            if not active or pending or not last_text.strip() or not isinstance(obj.get("usage"), dict):
                raise ValueError("incomplete turn/items/body")
            active, finished = False, True
        elif kind in ("item.started", "item.updated", "item.completed"):
            if "status" in obj:
                raise ValueError("unexpected top-level item event status")
            item = obj.get("item")
            if not active or not isinstance(item, dict):
                raise ValueError("item outside turn/bad shape")
            ident, itype = item.get("id"), item.get("type")
            if not isinstance(ident, str) or not ident or itype not in allowed_items or ident in completed:
                raise ValueError("unknown/error/duplicate item")
            if ident in pending and pending[ident] != itype:
                raise ValueError("item type changed")
            if kind == "item.completed":
                fixture_status_omission = ("status" not in item and itype == "agent_message"
                                           and set(item) == {"id", "type", "text"})
                _status(item, CODEX_ITEM_COMPLETED_STATUSES, "codex item.completed",
                        missing_ok=fixture_status_omission)
            else:
                _status(item, CODEX_ITEM_STARTED_STATUSES, "codex " + kind, missing_ok=False)
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
    return last_text, counts, {"schema": "codex_exec_jsonl_v7", "terminal": "turn.completed"}


def parse_opencode(stdout):
    rows = ndjson(stdout)
    session = message = None
    active = finished = False
    ids, texts, step_texts, counts = set(), [], [], {}
    expected = {"step_start": "step-start", "step_finish": "step-finish",
                "text": "text", "reasoning": "reasoning", "tool_use": "tool"}
    for obj in rows:
        if "status" in obj:
            raise ValueError("unexpected top-level OpenCode status")
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
            fixture_status_omission = "status" not in part and set(part) == {"type", "sessionID", "messageID", "id"}
            _status(part, OPENCODE_PART_STATUSES, "step_start part", missing_ok=fixture_status_omission)
            if active:
                raise ValueError("unfinished previous step")
            active, message, step_texts = True, mid, []
            continue
        if not active or message != mid:
            raise ValueError("part outside active step/message")
        if kind in ("text", "reasoning"):
            fixture_status_omission = ("status" not in part and set(part) ==
                                       {"type", "text", "time", "sessionID", "messageID", "id"})
            _status(part, OPENCODE_PART_STATUSES, kind + " part", missing_ok=fixture_status_omission)
            text, clock = part.get("text"), part.get("time")
            if (not isinstance(text, str) or not isinstance(clock, dict)
                    or type(clock.get("end")) not in (int, float) or clock["end"] <= 0):
                raise ValueError("text/reasoning part not completed")
            if kind == "text" and text.strip():
                texts.append(text)
                step_texts.append(text)
        elif kind == "tool_use":
            _status(part, OPENCODE_PART_STATUSES, "tool_use part", missing_ok=False)
            state, tool = part.get("state"), part.get("tool")
            if (not isinstance(state, dict) or state.get("status") != "completed"
                    or not isinstance(tool, str) or not tool):
                raise ValueError("failed/incomplete tool")
            counts["tool:" + tool] = counts.get("tool:" + tool, 0) + 1
        elif kind == "step_finish":
            fixture_status_omission = ("status" not in part and set(part) ==
                                       {"type", "reason", "sessionID", "messageID", "id"})
            _status(part, OPENCODE_FINISH_STATUSES, "step_finish part", missing_ok=fixture_status_omission)
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
    return "\n\n".join(texts), counts, {"schema": "opencode_run_jsonl_v7", "terminal": "step_finish:stop"}
