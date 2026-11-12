"""Fail-closed Thread v2/v3 resume harness.

Importing this module is inert.  The only executable workflow is an explicitly
mocked full-chain exercise in a temporary directory or a read-only strict
preflight.  This module never calls a model, CLI, network, or delegate.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


RUN_ID = "run145_thread_resume_r5"
RUN_DIR_REL = "runs/run145_thread_resume_r5"
STRICT_JSON_FENCE_RE = re.compile(r"```(?:json)?[ \t]*\r?\n(.*?)\r?\n```", re.I | re.S)
K_EXPECTED = 23
WORK_KEY = "op60"
WORK_NAME = "肖邦《船歌》Op.60"
VERSIONS = ("v2", "v3")
GENERATION_MODELS = ("gpt56w", "gpt6w")
REVIEWERS = ("gpt56w", "gpt6w", "gflash", "luna_noweb", "muse_external")
FORBIDDEN_MODELS = ("opus", "sol")
LEGACY_CONTROL = {
    "source_run": "run133_thread_spec",
    "source_model": "gpt56w",
    "status": "not_loaded_no_exact_disk_proof",
    "use_if_later_verified": "frozen_control_only",
    "eligible_for_new_fair_comparison": False,
}
SOURCE_PATHS = {
    "beads_markdown": "runs/run130_thread_e6/beads_clean.md",
    "bead_index": "runs/run130_thread_e6/steps.json",
}
TEMPLATE_PATHS = {
    "step_v2": "prompts/versions/C7_STEP_v2.txt",
    "step_v3": "prompts/versions/C7_STEP_v3.txt",
    "center": "prompts/versions/CENTER_v0.txt",
    "ident": "prompts/tooling/THREAD_IDENT_v0.txt",
    "compare": "prompts/tooling/THREAD_COMPARE_v0.txt",
}
CANDIDATES = (
    "肖邦《第一叙事曲》Op.23",
    "肖邦《第二叙事曲》Op.38",
    "肖邦《第三叙事曲》Op.47",
    "肖邦《第四叙事曲》Op.52",
    "肖邦《船歌》Op.60",
    "肖邦《幻想波兰舞曲》Op.61",
    "舒伯特《降B大调钢琴奏鸣曲》D.960",
    "舒曼《C大调幻想曲》Op.17",
)
MUSE_TARGET = "claude-proxy/muse-spark-1.3-contributor-free"
MUSE_TRANSPORT = "mcp"


class IntegrityError(RuntimeError):
    """Raised when provenance or chain integrity is incomplete or ambiguous."""


class CompletionPending(RuntimeError):
    """Raised when true transport or independently accepted protocol is absent."""


def canonical_muse_identity(provider: str, model: str) -> dict[str, str]:
    """Normalize historical generic Muse aliases at one boundary only."""
    providers = {"muse": "claude-proxy", "external muse": "claude-proxy",
                 "claude-proxy": "claude-proxy"}
    models = {"muse": "muse-spark-1.3-contributor-free",
              "external muse": "muse-spark-1.3-contributor-free",
              "muse-spark-1.3-contributor-free": "muse-spark-1.3-contributor-free"}
    canonical_provider = providers.get(str(provider).strip().lower())
    canonical_model_name = models.get(str(model).strip().lower())
    if canonical_provider is None or canonical_model_name is None:
        raise IntegrityError("Muse alias is unknown; expected the canonical claude-proxy target")
    return {"provider": canonical_provider, "model": canonical_model_name,
            "transport": MUSE_TRANSPORT, "target": MUSE_TARGET}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _reject_json_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant: " + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key: " + key)
        result[key] = value
    return result


def strict_json_loads(raw: str) -> Any:
    """Parse exactly one complete object/array or one complete JSON fence."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("empty response")
    stripped = raw.strip()
    fence = STRICT_JSON_FENCE_RE.fullmatch(stripped)
    payload = fence.group(1) if fence else stripped
    value = json.loads(payload, object_pairs_hook=_unique_object,
                       parse_constant=_reject_json_constant)
    if not isinstance(value, (dict, list)):
        raise ValueError("top-level JSON must be an object or array")
    return value


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _safe_child(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    base = root.resolve()
    if path != base and base not in path.parents:
        raise IntegrityError("artifact path escapes its evidence directory")
    return path


def fill_template(template: str, mapping: Mapping[str, Any]) -> str:
    names = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", template))
    if names != set(mapping):
        raise IntegrityError("template placeholder/mapping key set differs")
    rendered = template
    for name in sorted(names):
        value = mapping[name]
        if not isinstance(value, str):
            raise IntegrityError("template values must be strings")
        rendered = rendered.replace("{{" + name + "}}", value)
    if re.search(r"\{\{[A-Z0-9_]+\}\}", rendered):
        raise IntegrityError("unfilled template placeholder")
    return rendered


def validate_prompt_pair(v2: str, v3: str) -> dict[str, Any]:
    """Require one contiguous, single-line change inside question 3 only."""
    changes = [op for op in difflib.SequenceMatcher(a=v2, b=v3, autojunk=False).get_opcodes()
               if op[0] != "equal"]
    if len(changes) != 1:
        raise IntegrityError("v2/v3 must have exactly one prompt diff")
    tag, a0, a1, b0, b1 = changes[0]
    if tag not in ("replace", "insert"):
        raise IntegrityError("v2/v3 prompt diff must be one replacement or insertion")
    before, after = v2[a0:a1], v3[b0:b1]
    if not before and not after:
        raise IntegrityError("empty prompt diff")
    if "\n" in before or "\n" in after or "。" in before or "。" in after:
        raise IntegrityError("prompt diff must be one sentence fragment, not a wider paragraph edit")
    line_no = v2.count("\n", 0, a0)
    lines2 = v2.splitlines()
    lines3 = v3.splitlines()
    if line_no >= len(lines2) or line_no >= len(lines3):
        raise IntegrityError("prompt diff location is outside the prompt")
    if not lines2[line_no].lstrip().startswith("3."):
        raise IntegrityError("the sole prompt diff must be in question 3")
    if len(lines2) != len(lines3):
        raise IntegrityError("v2/v3 line structure differs beyond the single question-3 sentence")
    return {"changed_line": line_no + 1, "old_text": before, "new_text": after,
            "diff_count": 1, "question": 3}


def split_beads(markdown: str) -> list[dict[str, Any]]:
    """Pure copy of run133's canonical title + 此刻-only bead splitter."""
    headers = list(re.finditer(r"^###\s+(.*)$", markdown, re.M))
    beads: list[dict[str, Any]] = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(markdown)
        chunk = markdown[header.start():end]
        title = header.group(1).strip()
        marker = "【此刻】"
        start = chunk.find(marker)
        relation = chunk.find("【前后关系候选】", start + 1 if start >= 0 else 0)
        if start < 0:
            raise IntegrityError("bead source is missing 此刻 block")
        now = chunk[start + len(marker): relation if relation >= 0 else len(chunk)]
        lines = [line.strip() for line in now.split("\n") if line.strip()]
        beads.append({"k": index + 1, "title": title,
                      "text": title + "\n【此刻】\n" + "\n".join(lines)})
    return beads


def load_frozen_inputs(root: Path) -> tuple[list[dict[str, Any]], dict[str, str], dict[str, str]]:
    sources: dict[str, str] = {}
    for name, relative in SOURCE_PATHS.items():
        path = _safe_child(root, relative)
        if not path.is_file():
            raise IntegrityError("missing frozen source: " + relative)
        sources[name] = sha256_file(path)

    beads_path = _safe_child(root, SOURCE_PATHS["beads_markdown"])
    index_path = _safe_child(root, SOURCE_PATHS["bead_index"])
    markdown = beads_path.read_text(encoding="utf-8")
    parsed_beads = split_beads(markdown)
    index = strict_json_loads(index_path.read_text(encoding="utf-8"))
    if not isinstance(index, dict):
        raise IntegrityError("frozen bead index must be a JSON object")
    indexed = index.get("beads", {}).get(WORK_KEY)
    if not isinstance(indexed, list) or len(indexed) != K_EXPECTED:
        raise IntegrityError("frozen bead index must contain exactly 23 beads")
    if len(parsed_beads) != K_EXPECTED:
        raise IntegrityError("canonical bead source must contain exactly 23 beads")
    for expected_k, (actual, stored) in enumerate(zip(parsed_beads, indexed), 1):
        if actual["k"] != expected_k or stored.get("k") != expected_k:
            raise IntegrityError("bead prefix has a missing or duplicate step")
        if actual["title"] != stored.get("title") or actual["text"] != stored.get("text"):
            raise IntegrityError("beads_clean.md and frozen bead index disagree")

    templates: dict[str, str] = {}
    template_shas: dict[str, str] = {}
    for name, relative in TEMPLATE_PATHS.items():
        path = _safe_child(root, relative)
        if not path.is_file():
            raise IntegrityError("missing frozen template: " + relative)
        raw = path.read_bytes()
        templates[name] = raw.decode("utf-8")
        template_shas[name] = sha256_bytes(raw)
    validate_prompt_pair(templates["step_v2"], templates["step_v3"])
    return parsed_beads, sources, {**template_shas, "templates_payload": canonical_json(templates)}


def build_fingerprint(root: Path) -> dict[str, Any]:
    _, sources, template_info = load_frozen_inputs(root)
    template_shas = {key: value for key, value in template_info.items() if key != "templates_payload"}
    config = {
        "run_id": RUN_ID, "algorithm": "thread-resume-r5.0", "work_key": WORK_KEY,
        "work_name": WORK_NAME, "steps": K_EXPECTED, "versions": list(VERSIONS),
        "generation_models": list(GENERATION_MODELS), "reviewers": list(REVIEWERS),
        "forbidden_models": list(FORBIDDEN_MODELS), "legacy_control": LEGACY_CONTROL,
        "source_paths": SOURCE_PATHS, "template_paths": TEMPLATE_PATHS,
        "mock_only_for_local_validation": True,
    }
    driver = _safe_child(root, RUN_DIR_REL + "/go.py")
    driver_sha = sha256_file(driver)
    config_sha = sha256_text(canonical_json(config))
    frozen = {"sources": sources, "templates": template_shas,
              "driver_sha256": driver_sha, "config_sha256": config_sha,
              "config": config}
    frozen["fingerprint_sha256"] = sha256_text(canonical_json(frozen))
    return frozen


def render_history(inventory: Sequence[Mapping[str, Any]]) -> str:
    if not inventory:
        return "（还没有）"
    return "\n".join("- %s（来自：%s）" % (item["change"], item["from"]) for item in inventory)


def build_step_prompt(template: str, k: int, inventory: Sequence[Mapping[str, Any]],
                      beads: Sequence[Mapping[str, Any]]) -> str:
    bead_text = "\n\n".join("第 %d 段：%s" % (bead["k"], bead["text"]) for bead in beads[:k])
    return fill_template(template, {"WORK": WORK_NAME, "K": str(k), "K_PREV": str(k - 1),
                                    "HISTORY": render_history(inventory), "BEADS": bead_text})


def extract_json(raw: str) -> Any:
    try:
        return strict_json_loads(raw)
    except Exception as exc:
        raise IntegrityError("response is not one complete strict JSON object/array: " + type(exc).__name__) from exc


def normalize_step(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"new_changes", "no_longer_valid", "thread"}:
        raise IntegrityError("step response fields must match the frozen C7_STEP_v2/v3 schema")
    new_changes = value["new_changes"]
    no_longer_valid = value["no_longer_valid"]
    if not isinstance(new_changes, list) or not isinstance(no_longer_valid, list):
        raise IntegrityError("step lists have invalid schema")
    normalized: list[dict[str, str]] = []
    for item in new_changes:
        if not isinstance(item, dict) or set(item) != {"change", "from"}:
            raise IntegrityError("new_changes item must match the frozen change/from schema")
        change, origin = item["change"], item["from"]
        if (not isinstance(change, str) or not change.strip() or
                not isinstance(origin, str) or not origin.strip()):
            raise IntegrityError("new_changes item has invalid fields")
        normalized.append({"change": change, "from": origin})
    removed = []
    for item in no_longer_valid:
        if not isinstance(item, str) or not item.strip():
            raise IntegrityError("no_longer_valid items must be nonempty strings")
        removed.append(item)
    thread = value["thread"]
    if not isinstance(thread, str) or not thread.strip():
        raise IntegrityError("thread must be a nonempty string")
    return {"new_changes": normalized, "no_longer_valid": removed, "thread": thread}


def normalize_center(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"centers", "no_single_center"}:
        raise IntegrityError("center fields must match the frozen CENTER_v0 schema")
    centers = value["centers"]
    no_single = value["no_single_center"]
    if not isinstance(centers, list) or not 1 <= len(centers) <= 3 or not isinstance(no_single, bool):
        raise IntegrityError("center response has invalid top-level schema")
    result = []
    for center in centers:
        if (not isinstance(center, dict) or set(center) != {"center", "covers", "strains", "note"} or
                not isinstance(center.get("center"), str) or not center["center"].strip() or
                not isinstance(center.get("note"), str) or not center["note"].strip()):
            raise IntegrityError("center item is invalid")
        covers, strains = center["covers"], center["strains"]
        if not isinstance(covers, list) or not isinstance(strains, list):
            raise IntegrityError("center covers/strains must be lists")
        if (any(type(k) is not int or not 1 <= k <= K_EXPECTED for k in covers + strains) or
                len(set(covers)) != len(covers) or len(set(strains)) != len(strains)):
            raise IntegrityError("center covers/strains must contain unique in-range integers")
        result.append({"center": center["center"], "covers": covers, "strains": strains,
                       "note": center["note"]})
    return {"centers": result, "no_single_center": no_single}


def update_inventory(inventory: Sequence[Mapping[str, Any]], parsed: Mapping[str, Any], k: int,
                     match_judgments: Sequence[Mapping[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Apply v2's durable-change list; removal judgments must be explicit and exact."""
    added = [dict(change=item["change"], **{"from": item["from"]}, added_step=k)
             for item in parsed["new_changes"]]
    current = [dict(item) for item in inventory] + added
    nlv = list(parsed["no_longer_valid"])
    if not nlv:
        return current
    if match_judgments is None or len(match_judgments) != len(nlv):
        raise IntegrityError("History needs one provenance-backed match judgment per no_longer_valid entry")
    removed_indices: set[int] = set()
    for quote, judgment in zip(nlv, match_judgments):
        if judgment.get("quote") != quote:
            raise IntegrityError("match judgment quote does not exactly match source statement")
        index = judgment.get("match")
        if index is None:
            continue
        if type(index) is not int or index < 1 or index > len(current):
            raise IntegrityError("match judgment points outside current History inventory")
        removed_indices.add(index - 1)
    return [item for index, item in enumerate(current) if index not in removed_indices]


def _slot_id(slot: Mapping[str, Any]) -> str:
    return sha256_text(canonical_json(slot))[:24]


def _artifact_id(slot: Mapping[str, Any], sample_attempt: int = 0) -> str:
    if type(sample_attempt) is not int or sample_attempt < 0:
        raise IntegrityError("sample_attempt must be a nonnegative strict int")
    return _slot_id(slot) if sample_attempt == 0 else _slot_id(slot) + "__sample-%03d" % sample_attempt


def _stage_parse(stage: str, raw: str, task: Mapping[str, Any] | None = None) -> Any:
    value = extract_json(raw)
    if stage == "step":
        return normalize_step(value)
    if stage == "center":
        return normalize_center(value)
    if stage == "match":
        if not isinstance(value, list):
            raise IntegrityError("match response must be a JSON array")
        parsed = []
        for index, item in enumerate(value):
            if not isinstance(item, dict) or set(item) != {"quote", "match", "note"}:
                raise IntegrityError("match row must match the frozen quote/match/note schema")
            quote, match, note = item["quote"], item["match"], item["note"]
            if not isinstance(quote, str) or not quote.strip() or not isinstance(note, str) or not note.strip():
                raise IntegrityError("match row quote/note must be nonempty strings")
            if match is not None and (type(match) is not int or match < 1):
                raise IntegrityError("match index must be null or a strict positive integer")
            parsed.append({"quote": quote, "match": match, "note": note})
        binding = task.get("match_binding") if isinstance(task, Mapping) else None
        if isinstance(binding, Mapping):
            expected_quotes = binding.get("quotes")
            if not isinstance(expected_quotes, list) or [row["quote"] for row in parsed] != expected_quotes:
                raise IntegrityError("match quote list differs from the exact step output source")
        return parsed
    return value


def matching_successes(records: Iterable[Mapping[str, Any]], slot: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    matched = [record for record in records if record.get("slot") == dict(slot) and record.get("status") == "ok"]
    if len(matched) > 1:
        raise IntegrityError("ambiguous source: multiple successful records occupy the same slot")
    return matched


def scan_metadata_index(evidence_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """Read a source directory once and retain every success for ambiguity checks."""
    index: dict[str, list[dict[str, Any]]] = {}
    meta_dir = evidence_dir / "meta"
    if not meta_dir.exists():
        return index
    for path in meta_dir.glob("*.json"):
        value = strict_json_loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise IntegrityError("metadata index entry must be a JSON object")
        if isinstance(value.get("slot"), dict):
            index.setdefault(canonical_json(value["slot"]), []).append(value)
    return index


def preserve_legacy_producer(meta: Mapping[str, Any]) -> dict[str, Any]:
    """Keep the observed legacy producer value; never infer a missing identity."""
    if "producer_identity" in meta:
        return {"recorded": True, "value": meta.get("producer_identity")}
    if "producer_code_hash_at_generation" in meta:
        return {"recorded": True, "value": meta.get("producer_code_hash_at_generation")}
    return {"recorded": False, "value": None}


def _expected_mock_producer(slot: Mapping[str, Any], fingerprint: Mapping[str, Any]) -> dict[str, Any]:
    model_key = str(slot.get("model_key", slot.get("reviewer", "mock")))
    return {"kind": "mock_only", "adapter": RUN_ID + ".mock",
            "adapter_sha256": fingerprint.get("driver_sha256"),
            "producer_revision": "mock-only/1", "transport": "mock", "provider": "mock",
            "model": "MOCK_ONLY", "slot_model_key": model_key,
            "slot_sha256": sha256_text(canonical_json(dict(slot)))}


def _validate_identity(meta: Mapping[str, Any], slot: Mapping[str, Any], fingerprint: Mapping[str, Any]) -> None:
    mode = meta.get("execution_mode")
    if mode != "mock_only":
        if mode in ("real", "real_model", "production", "external"):
            raise CompletionPending("real execution metadata is unsupported until a trusted archive verifier is installed")
        raise IntegrityError("execution_mode must equal the exact value mock_only")
    identity = meta.get("identity")
    producer = meta.get("producer_identity")
    if not isinstance(identity, dict) or identity.get("slot") != dict(slot):
        raise IntegrityError("full job identity is missing or differs from requested slot")
    expected_model = slot.get("model_key", slot.get("reviewer"))
    expected_identity = {"run_id": RUN_ID, "slot": dict(slot), "work_key": WORK_KEY,
                         "model_key": expected_model, "model_name": "MOCK_ONLY",
                         "request_id": "mock:" + _slot_id(slot),
                         "canonicalization": "mock_unverified"}
    if identity != expected_identity:
        raise IntegrityError("full job identity does not match its run/work/model/request slot")
    if not isinstance(producer, dict):
        raise IntegrityError("producer identity is unrecorded; no exact reuse")
    if producer != _expected_mock_producer(slot, fingerprint):
        raise IntegrityError("mock producer tuple/request binding differs from the exact slot")
    if meta.get("queue_stop") is not False:
        raise IntegrityError("queue_stop metadata prevents reuse")
    if meta.get("fingerprint_sha256") != fingerprint.get("fingerprint_sha256"):
        raise IntegrityError("frozen source/template/driver/config fingerprint changed")
    request_identity = meta.get("request_identity")
    prompt_text = request_identity.get("prompt_utf8") if isinstance(request_identity, dict) else None
    expected_request = {"run_id": RUN_ID, "slot": dict(slot), "work_key": WORK_KEY,
                        "model_key": expected_model, "model_name": "MOCK_ONLY",
                        "request_id": "mock:" + _slot_id(slot),
                        "execution_mode": "mock_only", "prompt_sha256": meta.get("prompt_sha256"),
                        "prompt_utf8": prompt_text,
                        "template_sha256": meta.get("template_sha256"),
                        "source_sha256": meta.get("source_sha256"),
                        "lineage": meta.get("lineage")}
    if request_identity != expected_request:
        raise IntegrityError("complete request identity does not match current slot/template/source/lineage")


def _load_attempt_files(evidence_dir: Path, slot: Mapping[str, Any], sample_attempt: int) -> tuple[Path, bytes, dict[str, Any], bytes, bytes]:
    meta_path = _safe_child(evidence_dir, "meta/" + _artifact_id(slot, sample_attempt) + ".json")
    if not meta_path.is_file():
        raise IntegrityError("missing metadata; cache-only evidence is not reusable")
    meta_raw = meta_path.read_bytes()
    meta = strict_json_loads(meta_raw.decode("utf-8"))
    if not isinstance(meta, dict):
        raise IntegrityError("metadata must be a complete JSON object")
    if meta.get("prompt_file") != "prompts/" + _artifact_id(slot, sample_attempt) + ".txt" or \
            meta.get("output_file") != "outputs/" + _artifact_id(slot, sample_attempt) + ".txt":
        raise IntegrityError("sample artifact paths differ from immutable attempt identity")
    prompt_path = _safe_child(evidence_dir, meta["prompt_file"])
    output_path = _safe_child(evidence_dir, meta["output_file"])
    if not prompt_path.is_file() or not output_path.is_file():
        raise IntegrityError("missing prompt/output file; cache-only evidence is not reusable")
    return meta_path, meta_raw, meta, prompt_path.read_bytes(), output_path.read_bytes()


def _expected_local_meta_keys() -> set[str]:
    return {"run_id", "slot", "status", "execution_mode", "prompt_file", "output_file",
            "prompt_sha256", "output_sha256", "parsed", "parse_error", "parse_status",
            "sample_attempt", "sampling_identity", "sample_reason", "new_sample_taken",
            "identity", "request_identity", "producer_identity", "fingerprint_sha256",
            "template_sha256", "source_sha256", "lineage", "canonicalization", "queue_stop"}


def verify_failed_disk_evidence(evidence_dir: Path, slot: Mapping[str, Any], prompt: str,
                                fingerprint: Mapping[str, Any], sample_attempt: int,
                                expected_meta_sha256: str | None = None,
                                expected_template_sha256: str | None = None,
                                expected_source_sha256: str | None = None,
                                expected_lineage: Mapping[str, Any] | None = None) -> dict[str, Any]:
    meta_path, meta_raw, meta, prompt_raw, output_raw = _load_attempt_files(evidence_dir, slot, sample_attempt)
    if set(meta) != _expected_local_meta_keys() or meta.get("status") != "parse_failed":
        raise IntegrityError("failed sample metadata schema/status mismatch")
    if (meta.get("sample_attempt") != sample_attempt or meta.get("new_sample_taken") is not (sample_attempt > 0) or
            (sample_attempt == 0 and meta.get("sample_reason") is not None) or
            (sample_attempt > 0 and (not isinstance(meta.get("sample_reason"), str) or
                                     not meta["sample_reason"].strip()))):
        raise IntegrityError("failed sample identity/reason mismatch")
    if expected_meta_sha256 and sha256_bytes(meta_raw) != expected_meta_sha256:
        raise IntegrityError("metadata SHA256 changed")
    if meta.get("slot") != dict(slot) or meta.get("parse_status") != "failed":
        raise IntegrityError("failed sample slot/parse status mismatch")
    _validate_identity(meta, slot, fingerprint)
    if expected_template_sha256 is not None and meta.get("template_sha256") != expected_template_sha256:
        raise IntegrityError("metadata template SHA256 mismatch")
    if expected_source_sha256 is not None and meta.get("source_sha256") != expected_source_sha256:
        raise IntegrityError("metadata source SHA256 mismatch")
    if expected_lineage is not None and meta.get("lineage") != dict(expected_lineage):
        raise IntegrityError("metadata chain lineage mismatch")
    if prompt_raw != prompt.encode("utf-8") or sha256_bytes(prompt_raw) != meta.get("prompt_sha256"):
        raise IntegrityError("prompt bytes/SHA256 mismatch")
    if sha256_bytes(output_raw) != meta.get("output_sha256"):
        raise IntegrityError("output SHA256 mismatch")
    expected_sampling = sha256_text(canonical_json({
        "run_id": RUN_ID, "slot": dict(slot), "prompt_sha256": meta["prompt_sha256"],
        "source_sha256": meta.get("source_sha256"),
        "template_sha256": meta.get("template_sha256"), "sample_attempt": sample_attempt}))
    if meta.get("sampling_identity") != expected_sampling:
        raise IntegrityError("failed sample sampling identity changed")
    try:
        parse_task = {"match_binding": (meta.get("lineage") or {}).get("match_binding")}
        _stage_parse(str(slot["stage"]), output_raw.decode("utf-8"), parse_task)
    except Exception as exc:
        actual_error = type(exc).__name__ + ": " + str(exc)
        if meta.get("parse_error") != actual_error:
            raise IntegrityError("persisted parse error differs from exact failed raw bytes") from exc
    else:
        raise IntegrityError("recorded parse-failed sample parses successfully on disk")
    return {"slot": dict(slot), "status": "parse_failed", "output": output_raw.decode("utf-8"),
            "meta_sha256": sha256_bytes(meta_raw), "prompt_sha256": sha256_bytes(prompt_raw),
            "output_sha256": sha256_bytes(output_raw), "sampling_identity": meta["sampling_identity"],
            "request_identity": meta["request_identity"], "meta": meta}


def verify_disk_evidence(evidence_dir: Path, slot: Mapping[str, Any], prompt: str,
                         fingerprint: Mapping[str, Any], expected_meta_sha256: str | None = None,
                         expected_template_sha256: str | None = None,
                         expected_source_sha256: str | None = None,
                         expected_lineage: Mapping[str, Any] | None = None,
                         sample_attempt: int = 0) -> dict[str, Any]:
    """Verify exact successful prompt/output/meta bytes and the full request identity."""
    meta_path, meta_raw, meta, prompt_raw, output_raw = _load_attempt_files(evidence_dir, slot, sample_attempt)
    if set(meta) != _expected_local_meta_keys() or meta.get("status") != "ok":
        raise IntegrityError("metadata fields/status must match the exact successful evidence schema")
    if meta.get("sample_attempt") != sample_attempt or meta.get("parse_status") != "ok":
        raise IntegrityError("successful sample attempt/parse identity mismatch")
    if (meta.get("new_sample_taken") is not (sample_attempt > 0) or
            (sample_attempt == 0 and meta.get("sample_reason") is not None) or
            (sample_attempt > 0 and (not isinstance(meta.get("sample_reason"), str) or
                                     not meta["sample_reason"].strip()))):
        raise IntegrityError("successful sample reason/identity mismatch")
    if expected_meta_sha256 and sha256_bytes(meta_raw) != expected_meta_sha256:
        raise IntegrityError("metadata SHA256 changed")
    if meta.get("slot") != dict(slot):
        raise IntegrityError("metadata slot mismatch")
    _validate_identity(meta, slot, fingerprint)
    if expected_template_sha256 is not None and meta.get("template_sha256") != expected_template_sha256:
        raise IntegrityError("metadata template SHA256 mismatch")
    if expected_source_sha256 is not None and meta.get("source_sha256") != expected_source_sha256:
        raise IntegrityError("metadata source SHA256 mismatch")
    if expected_lineage is not None and meta.get("lineage") != dict(expected_lineage):
        raise IntegrityError("metadata chain lineage mismatch")
    if prompt_raw != prompt.encode("utf-8") or sha256_bytes(prompt_raw) != meta.get("prompt_sha256"):
        raise IntegrityError("prompt bytes/SHA256 mismatch")
    if sha256_bytes(output_raw) != meta.get("output_sha256"):
        raise IntegrityError("output SHA256 mismatch")
    expected_sampling = sha256_text(canonical_json({
        "run_id": RUN_ID, "slot": dict(slot), "prompt_sha256": meta["prompt_sha256"],
        "source_sha256": meta.get("source_sha256"),
        "template_sha256": meta.get("template_sha256"), "sample_attempt": sample_attempt}))
    if meta.get("sampling_identity") != expected_sampling:
        raise IntegrityError("sampling identity changed")
    parse_task = {"match_binding": (meta.get("lineage") or {}).get("match_binding")}
    parsed = _stage_parse(str(slot["stage"]), output_raw.decode("utf-8"), parse_task)
    if parsed != meta.get("parsed"):
        raise IntegrityError("parsed response differs from parsing the exact output bytes")
    return {"slot": dict(slot), "parsed": parsed, "output": output_raw.decode("utf-8"),
            "meta_sha256": sha256_bytes(meta_raw), "prompt_sha256": sha256_bytes(prompt_raw),
            "output_sha256": sha256_bytes(output_raw), "producer_identity": meta["producer_identity"],
            "identity": meta["identity"], "request_identity": meta["request_identity"],
            "sampling_identity": meta["sampling_identity"], "sample_attempt": sample_attempt, "meta": meta}


def _mock_response(task: Mapping[str, Any]) -> str:
    slot = task["slot"]
    stage = slot["stage"]
    if stage == "step":
        k = slot["k"]
        payload = {"new_changes": ([{"change": "MOCK_ONLY durable change", "from": "MOCK_ONLY k1"}]
                                    if k == 1 else []),
                   "no_longer_valid": (["MOCK_ONLY durable change"] if k == 2 else []),
                   "thread": "MOCK_ONLY %s %s k%d" %
                   (slot["version"], slot["model_key"], k)}
    elif stage == "center":
        payload = {"centers": [{"center": "MOCK_ONLY synthetic center", "covers": list(range(1, K_EXPECTED + 1)),
                                "strains": [], "note": "MOCK_ONLY"}], "no_single_center": False}
    elif stage == "match":
        binding = task.get("match_binding")
        if isinstance(binding, Mapping):
            inventory = binding["inventory_before"]
            payload = []
            for quote in binding["quotes"]:
                matches = [index for index, item in enumerate(inventory, 1) if item["change"] == quote]
                payload.append({"quote": quote, "match": matches[0] if len(matches) == 1 else None,
                                "note": "MOCK_ONLY exact source search"})
        else:
            payload = [{"quote": quote, "match": None, "note": "MOCK_ONLY"} for quote in task["quotes"]]
    else:
        payload = {"mock_only": True, "stage": stage, "reviewer": slot.get("reviewer"),
                   "canonicalization": "mock_unverified"}
    return canonical_json(payload)


def _create_mock_artifact(evidence_dir: Path, task: Mapping[str, Any], fingerprint: Mapping[str, Any],
                          raw_output: str, *, sample_attempt: int = 0,
                          sample_reason: str | None = None) -> dict[str, Any]:
    slot = dict(task["slot"])
    if type(sample_attempt) is not int or not 0 <= sample_attempt <= 1:
        raise IntegrityError("mock sample attempt must be a strict int within the bounded two-sample limit")
    if (sample_attempt == 0 and sample_reason is not None) or (sample_attempt > 0 and
            (not isinstance(sample_reason, str) or not sample_reason.strip())):
        raise IntegrityError("new immutable sample requires an explicit nonempty reason")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    artifact_id = _artifact_id(slot, sample_attempt)
    prompt_rel = "prompts/" + artifact_id + ".txt"
    output_rel = "outputs/" + artifact_id + ".txt"
    meta_rel = "meta/" + artifact_id + ".json"
    for relative in (prompt_rel, output_rel, meta_rel):
        path = _safe_child(evidence_dir, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise IntegrityError("refusing to overwrite existing immutable sample/artifact")

    prompt_bytes = task["prompt"].encode("utf-8")
    output_bytes = raw_output.encode("utf-8")
    prompt_sha = sha256_bytes(prompt_bytes)
    sampling_identity = sha256_text(canonical_json({
        "run_id": RUN_ID, "slot": slot, "prompt_sha256": prompt_sha,
        "source_sha256": task.get("source_sha256"),
        "template_sha256": task.get("template_sha256"), "sample_attempt": sample_attempt}))
    parse_error = None
    try:
        parsed = _stage_parse(str(slot["stage"]), raw_output, task)
        status, parse_status = "ok", "ok"
    except Exception as exc:
        parsed = None
        parse_error = type(exc).__name__ + ": " + str(exc)
        status, parse_status = "parse_failed", "failed"
    driver_sha = fingerprint["driver_sha256"]
    producer = _expected_mock_producer(slot, fingerprint)
    model_key = str(slot.get("model_key", slot.get("reviewer", "mock")))
    identity = {"run_id": RUN_ID, "slot": slot, "work_key": WORK_KEY,
                "model_key": model_key, "model_name": "MOCK_ONLY",
                "request_id": "mock:" + _slot_id(slot), "canonicalization": "mock_unverified"}
    request_identity = {"run_id": RUN_ID, "slot": slot, "work_key": WORK_KEY,
                        "model_key": model_key, "model_name": "MOCK_ONLY",
                        "request_id": "mock:" + _slot_id(slot), "execution_mode": "mock_only",
                        "prompt_utf8": task["prompt"], "prompt_sha256": prompt_sha,
                        "template_sha256": task.get("template_sha256"),
                        "source_sha256": task.get("source_sha256"), "lineage": task.get("lineage")}
    meta = {"run_id": RUN_ID, "slot": slot, "status": status, "execution_mode": "mock_only",
            "prompt_file": prompt_rel, "output_file": output_rel,
            "prompt_sha256": prompt_sha, "output_sha256": sha256_bytes(output_bytes),
            "parsed": parsed, "parse_error": parse_error, "parse_status": parse_status,
            "sample_attempt": sample_attempt, "sampling_identity": sampling_identity,
            "sample_reason": sample_reason, "new_sample_taken": sample_attempt > 0,
            "identity": identity, "request_identity": request_identity,
            "producer_identity": producer,
            "fingerprint_sha256": fingerprint["fingerprint_sha256"],
            "template_sha256": task.get("template_sha256"),
            "source_sha256": task.get("source_sha256"),
            "lineage": task.get("lineage"),
            "canonicalization": "mock_unverified", "queue_stop": False}
    # Persist all immutable bytes, including failed raw output, before propagating parse status.
    for relative, raw in ((prompt_rel, prompt_bytes), (output_rel, output_bytes),
                          (meta_rel, (canonical_json(meta) + "\n").encode("utf-8"))):
        with _safe_child(evidence_dir, relative).open("xb") as stream:
            stream.write(raw)
    if status == "parse_failed":
        return {"slot": slot, "status": status, "output": raw_output,
                "meta_sha256": sha256_bytes((canonical_json(meta) + "\n").encode("utf-8")),
                "prompt_sha256": prompt_sha, "output_sha256": sha256_bytes(output_bytes),
                "sampling_identity": sampling_identity, "request_identity": request_identity,
                "sample_attempt": sample_attempt, "meta": meta}
    return verify_disk_evidence(evidence_dir, slot, task["prompt"], fingerprint,
                                expected_template_sha256=task.get("template_sha256"),
                                expected_source_sha256=task.get("source_sha256"),
                                expected_lineage=task.get("lineage"), sample_attempt=sample_attempt)


def execute_mock_task(evidence_dir: Path, task: Mapping[str, Any], fingerprint: Mapping[str, Any],
                      expected_meta_hashes: dict[str, str], counters: dict[str, int],
                      metadata_index: dict[str, list[dict[str, Any]]], *,
                      allow_new_sample_on_parse_failure: bool = False,
                      max_new_samples: int | None = None,
                      new_sample_reason: str | None = None,
                      response_factory: Callable[[Mapping[str, Any], int], str] | None = None) -> dict[str, Any]:
    slot = dict(task["slot"])
    if type(allow_new_sample_on_parse_failure) is not bool:
        raise IntegrityError("allow_new_sample_on_parse_failure must be a strict bool")
    if allow_new_sample_on_parse_failure:
        if type(max_new_samples) is not int or not 1 <= max_new_samples <= 2:
            raise IntegrityError("explicit new sample budget must be a strict int from 1 to 2")
        if not isinstance(new_sample_reason, str) or not new_sample_reason.strip():
            raise IntegrityError("explicit new sample requires a nonempty reason")
    elif max_new_samples is not None or new_sample_reason is not None:
        raise IntegrityError("sample budget/reason requires explicit parse-failure authorization")
    slot_key = canonical_json(slot)
    matches = metadata_index.get(slot_key, [])
    success = matching_successes(matches, slot)
    if success:
        failed_records = [record for record in matches if record.get("status") == "parse_failed"]
        if len(failed_records) + len(success) != len(matches):
            raise IntegrityError("slot index contains an unknown artifact status")
        for failed_record in failed_records:
            failed_attempt = failed_record.get("sample_attempt")
            if type(failed_attempt) is not int:
                raise IntegrityError("persisted failed sample has no strict attempt identity")
            verify_failed_disk_evidence(evidence_dir, slot, task["prompt"], fingerprint, failed_attempt,
                                        expected_template_sha256=task.get("template_sha256"),
                                        expected_source_sha256=task.get("source_sha256"),
                                        expected_lineage=task.get("lineage"))
        record = success[0]
        sample_attempt = record.get("sample_attempt", 0)
        expected_meta = expected_meta_hashes.get(slot_key)
        proof = verify_disk_evidence(evidence_dir, slot, task["prompt"], fingerprint, expected_meta,
                                     task.get("template_sha256"), task.get("source_sha256"),
                                     task.get("lineage"), sample_attempt=sample_attempt)
        counters["reused"] += 1
        if slot.get("stage") == "match":
            counters["match_reused"] = counters.get("match_reused", 0) + 1
        return proof
    attempts = sorted((record for record in matches if record.get("status") == "parse_failed"),
                      key=lambda record: record.get("sample_attempt", -1))
    if len(attempts) != len(matches):
        raise IntegrityError("failed slot metadata has an unknown status; no new sample is allowed")
    for record in attempts:
        sample_attempt = record.get("sample_attempt")
        if type(sample_attempt) is not int:
            raise IntegrityError("persisted failed sample has no strict attempt identity")
        verify_failed_disk_evidence(evidence_dir, slot, task["prompt"], fingerprint, sample_attempt,
                                    expected_template_sha256=task.get("template_sha256"),
                                    expected_source_sha256=task.get("source_sha256"),
                                    expected_lineage=task.get("lineage"))
    if attempts and not allow_new_sample_on_parse_failure:
        raise IntegrityError("persisted completed parse failure blocks this slot by default")
    if attempts and len(attempts) >= int(max_new_samples or 0):
        raise IntegrityError("explicit new sample budget is exhausted; failed raw evidence remains indexed")
    next_attempt = max((record.get("sample_attempt", -1) for record in matches), default=-1) + 1
    if next_attempt > 1:
        raise IntegrityError("new sample budget exceeds the two immutable sample hard limit")
    while True:
        raw = (response_factory(task, next_attempt) if callable(response_factory) else
               _mock_response({**dict(task), "sample_attempt": next_attempt}))
        counters["mock_submissions"] += 1
        if slot.get("stage") == "match":
            counters["match_submissions"] = counters.get("match_submissions", 0) + 1
        proof = _create_mock_artifact(evidence_dir, task, fingerprint, raw,
                                      sample_attempt=next_attempt,
                                      sample_reason=(new_sample_reason if next_attempt > 0 else None))
        expected_meta_hashes[slot_key] = proof["meta_sha256"]
        metadata_index.setdefault(slot_key, []).append(proof["meta"])
        if proof.get("status") != "parse_failed":
            return proof
        if not allow_new_sample_on_parse_failure or next_attempt + 1 >= int(max_new_samples or 0):
            raise IntegrityError("completed parse failure was persisted immutably; default STOP remains in force")
        next_attempt += 1


def _apply_match_output(inventory: Sequence[Mapping[str, Any]], nlv: Sequence[str],
                        judgments: Sequence[Mapping[str, Any]], k: int,
                        new_changes: Sequence[Mapping[str, str]], *,
                        step_output_sha256: str, step_slot: Mapping[str, Any]) -> list[dict[str, Any]]:
    if not nlv:
        if judgments:
            raise IntegrityError("match judgments supplied although this step has no no_longer_valid quote")
        return update_inventory(inventory, {"new_changes": list(new_changes), "no_longer_valid": []}, k, None)
    if len(judgments) != len(nlv):
        raise IntegrityError("match evidence count must exactly equal the step's no_longer_valid quote count")
    inventory_sha = sha256_text(canonical_json([dict(item) for item in inventory]))
    checked: list[dict[str, Any]] = []
    for quote_index, (quote, judgment) in enumerate(zip(nlv, judgments), 1):
        if not isinstance(judgment, Mapping) or set(judgment) != {"quote", "match", "note", "evidence"}:
            raise IntegrityError("NLV retirement requires a complete disk-backed match judgment")
        evidence = judgment.get("evidence")
        if not isinstance(evidence, Mapping) or set(evidence) != {
                "slot", "target_slot", "match_binding", "prompt_sha256", "output_sha256",
                "meta_sha256", "source_sha256", "lineage", "output", "parsed"}:
            raise IntegrityError("match evidence is missing exact disk/source/lineage proof fields")
        binding = evidence["match_binding"]
        if (judgment.get("quote") != quote or not isinstance(binding, Mapping) or
                binding.get("k") != k or binding.get("quote_index") != quote_index or
                binding.get("quote") != quote or binding.get("step_output_sha256") != step_output_sha256 or
                binding.get("inventory_sha256") != inventory_sha or
                binding.get("target_slot") != dict(step_slot) or
                evidence.get("target_slot") != dict(step_slot) or
                evidence.get("slot") != dict(binding.get("slot", {}))):
            raise IntegrityError("exact NLV quote/output/inventory/task binding mismatch")
        if (evidence.get("lineage") != {"match_binding": dict(binding)} or
                sha256_text(evidence.get("output", "")) != evidence.get("output_sha256") or
                not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("meta_sha256", ""))) or
                not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("source_sha256", ""))) or
                not re.fullmatch(r"[0-9a-f]{64}", str(evidence.get("prompt_sha256", "")))):
            raise IntegrityError("match disk evidence hashes/lineage are incomplete")
        match_task = {"match_binding": dict(binding)}
        reparsed = _stage_parse("match", evidence["output"], match_task)
        if reparsed != evidence.get("parsed") or len(reparsed) != 1 or reparsed[0] != {
                "quote": judgment["quote"], "match": judgment["match"], "note": judgment["note"]}:
            raise IntegrityError("match output does not parse to the recorded exact quote judgment")
        index = judgment["match"]
        if index is not None:
            if type(index) is not int or not 1 <= index <= len(inventory):
                raise IntegrityError("match judgment points outside its bound inventory snapshot")
            if inventory[index - 1]["change"] != quote:
                raise IntegrityError("match index does not identify the exact source statement")
        checked.append({"quote": quote, "match": index, "note": judgment["note"]})
    parsed = {"new_changes": list(new_changes), "no_longer_valid": list(nlv)}
    return update_inventory(inventory, parsed, k, checked)


def build_match_prompt(k: int, quote: str, inventory: Sequence[Mapping[str, Any]],
                       step_output_sha256: str) -> str:
    rows = "\n".join("%d. %s" % (index, item["change"])
                     for index, item in enumerate(inventory, 1)) or "(empty inventory)"
    return ("MOCK_ONLY independent exact-source match task\n"
            "step=%d\nstep_output_sha256=%s\nquote=%s\ninventory:\n%s\n"
            "Return one JSON row with exact quote and 1-based match index, or null.\n" %
            (k, step_output_sha256, quote, rows))


def build_center_history(beads: Sequence[Mapping[str, Any]], records: Sequence[Mapping[str, Any]]) -> str:
    by_k = {record["k"]: record for record in records}
    lines = []
    for bead in beads:
        record = by_k.get(bead["k"])
        if record is None:
            raise IntegrityError("Center cannot omit a Thread step")
        parsed = record["parsed"]
        changes = "；".join(item["change"] for item in parsed["new_changes"]) or "（无）"
        lines.append("第%d段（%s）：新记下的变化：%s；线：%s" %
                     (bead["k"], bead["title"], changes, parsed["thread"] or "（空）"))
    final = records[-1]["inventory_after"]
    inventory_text = "（空）" if not final else "\n".join(
        "%d. %s（来自：%s）[第%d步加入]" % (i + 1, item["change"], item["from"], item["added_step"])
        for i, item in enumerate(final))
    lines.append("最终清单：\n" + inventory_text)
    return "\n".join(lines)


def build_center_beads(beads: Sequence[Mapping[str, Any]]) -> str:
    return "\n\n".join("第%d段（%s）：%s" % (b["k"], b["title"], b["text"]) for b in beads)


def validate_chain(records: Sequence[Mapping[str, Any]], version: str, model: str,
                   beads: Sequence[Mapping[str, Any]], step_template: str) -> None:
    if len(records) != K_EXPECTED or [r.get("k") for r in records] != list(range(1, K_EXPECTED + 1)):
        raise IntegrityError("chain must contain every History prefix k1..23 in order")
    inventory: list[dict[str, Any]] = []
    previous_sha: str | None = None
    for k, record in enumerate(records, 1):
        if record.get("version") != version or record.get("model_key") != model:
            raise IntegrityError("chain identity changed within a prefix")
        if record.get("previous_output_sha256") != previous_sha:
            raise IntegrityError("History prefix does not point to the immediately previous step")
        if record.get("inventory_before") != inventory:
            raise IntegrityError("History prefix differs from preceding parsed outputs")
        expected_prompt = build_step_prompt(step_template, k, inventory, beads)
        if record.get("prompt") != expected_prompt or record.get("prompt_sha256") != sha256_text(expected_prompt):
            raise IntegrityError("step prompt does not reconstruct from frozen input + exact History prefix")
        bead_sha = sha256_text(canonical_json([b["text"] for b in beads[:k]]))
        history_sha = sha256_text(render_history(inventory))
        if record.get("bead_prefix_sha256") != bead_sha:
            raise IntegrityError("step prompt used a different or non-prefix bead input")
        if record.get("history_prefix_sha256") != history_sha:
            raise IntegrityError("stored History prefix hash differs from preceding parsed outputs")
        expected_lineage = {"previous_output_sha256": previous_sha,
                            "history_prefix_sha256": history_sha,
                            "bead_prefix_sha256": bead_sha}
        if record.get("lineage") != expected_lineage:
            raise IntegrityError("step lineage is not linked to the preceding prefix")
        parsed = normalize_step(extract_json(record["output"]))
        if parsed != record.get("parsed") or sha256_text(record["output"]) != record.get("output_sha256"):
            raise IntegrityError("parsed step and exact output bytes disagree")
        match = record.get("match_judgments")
        inventory = _apply_match_output(inventory, parsed["no_longer_valid"], match or [], k,
                                        parsed["new_changes"],
                                        step_output_sha256=record["output_sha256"],
                                        step_slot=record["slot"])
        if inventory != record.get("inventory_after"):
            raise IntegrityError("History inventory transition differs from parsed step/match evidence")
        if len(record.get("match_lineage", [])) != len(parsed["no_longer_valid"]):
            raise IntegrityError("step lineage omits a required independent NLV match task")
        for judgment, lineage in zip(match or [], record.get("match_lineage", [])):
            proof = judgment["evidence"]
            if (lineage != {"slot": proof["slot"], "output_sha256": proof["output_sha256"],
                            "meta_sha256": proof["meta_sha256"], "prompt_sha256": proof["prompt_sha256"]}):
                raise IntegrityError("match lineage differs from the exact disk proof hashes")
        previous_sha = record["output_sha256"]


def validate_center_link(center_record: Mapping[str, Any], chain_id: str,
                         records: Sequence[Mapping[str, Any]], beads: Sequence[Mapping[str, Any]],
                         template: str) -> None:
    source_shas = [record["output_sha256"] for record in records]
    source_matches = [match for record in records for match in record.get("match_lineage", [])]
    prompt = fill_template(template, {"WORK": WORK_NAME, "HISTORY": build_center_history(beads, records),
                                      "BEADS": build_center_beads(beads)})
    if (center_record.get("chain_id") != chain_id or center_record.get("source_step_sha256s") != source_shas or
            center_record.get("source_match_lineage") != source_matches):
        raise IntegrityError("Center is not associated with this exact complete 23-step chain")
    expected_lineage = {"chain_id": chain_id, "source_step_sha256s": source_shas,
                        "source_step_slots": [record["slot"] for record in records],
                        "source_match_lineage": source_matches}
    if center_record.get("lineage") != expected_lineage:
        raise IntegrityError("Center disk lineage does not cite every source step slot")
    if center_record.get("prompt") != prompt or center_record.get("prompt_sha256") != sha256_text(prompt):
        raise IntegrityError("Center prompt differs from the associated complete chain")
    if normalize_center(extract_json(center_record["output"])) != center_record.get("parsed"):
        raise IntegrityError("Center parsed value differs from exact output")


def _slot(stage: str, **fields: Any) -> dict[str, Any]:
    return {"stage": stage, **fields}


def _task(stage: str, slot: Mapping[str, Any], prompt: str, template_sha: str,
          source_sha: str, **more: Any) -> dict[str, Any]:
    return {"slot": dict(slot), "prompt": prompt, "template_sha256": template_sha,
            "source_sha256": source_sha, **more}


def _build_mock_chain(root: Path, evidence_dir: Path, fingerprint: Mapping[str, Any],
                      beads: Sequence[Mapping[str, Any]], templates: Mapping[str, str], version: str,
                      model: str, counters: dict[str, int], hashes: dict[str, str],
                      metadata_index: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    chain_id = version + "_" + model
    records: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    previous_sha = None
    source_sha = sha256_text(canonical_json(fingerprint["sources"]))
    template_sha = fingerprint["templates"]["step_" + version]
    for k in range(1, K_EXPECTED + 1):
        prompt = build_step_prompt(templates["step_" + version], k, inventory, beads)
        slot = _slot("step", chain_id=chain_id, version=version, model_key=model, k=k)
        bead_prefix_sha = sha256_text(canonical_json([b["text"] for b in beads[:k]]))
        lineage = {"previous_output_sha256": previous_sha,
                   "history_prefix_sha256": sha256_text(render_history(inventory)),
                   "bead_prefix_sha256": bead_prefix_sha}
        task = _task("step", slot, prompt, template_sha, source_sha, lineage=lineage)
        proof = execute_mock_task(evidence_dir, task, fingerprint, hashes, counters, metadata_index)
        parsed = proof["parsed"]
        match_judgments: list[dict[str, Any]] = []
        match_lineage: list[dict[str, Any]] = []
        for quote_index, quote in enumerate(parsed["no_longer_valid"], 1):
            match_slot = _slot("match", chain_id=chain_id, version=version,
                               model_key=model, k=k, quote_index=quote_index)
            binding = {"k": k, "quote_index": quote_index, "quote": quote, "quotes": [quote],
                       "inventory_before": [dict(item) for item in inventory],
                       "step_output_sha256": proof["output_sha256"],
                       "inventory_sha256": sha256_text(canonical_json(inventory)),
                       "target_slot": slot, "slot": match_slot}
            match_prompt = build_match_prompt(k, quote, inventory, proof["output_sha256"])
            match_task = _task("match", match_slot, match_prompt,
                               sha256_text("run145-exact-source-match-v1"), source_sha,
                               match_binding=binding, lineage={"match_binding": binding})
            match_proof = execute_mock_task(evidence_dir, match_task, fingerprint, hashes,
                                            counters, metadata_index)
            if len(match_proof["parsed"]) != 1:
                raise IntegrityError("independent match task returned wrong judgment count")
            parsed_judgment = match_proof["parsed"][0]
            evidence = {"slot": match_slot, "target_slot": slot, "match_binding": binding,
                        "prompt_sha256": match_proof["prompt_sha256"],
                        "output_sha256": match_proof["output_sha256"],
                        "meta_sha256": match_proof["meta_sha256"], "source_sha256": source_sha,
                        "lineage": {"match_binding": binding}, "output": match_proof["output"],
                        "parsed": match_proof["parsed"]}
            match_judgments.append({**parsed_judgment, "evidence": evidence})
            match_lineage.append({"slot": match_slot, "output_sha256": match_proof["output_sha256"],
                                  "meta_sha256": match_proof["meta_sha256"],
                                  "prompt_sha256": match_proof["prompt_sha256"]})
        after = _apply_match_output(inventory, parsed["no_longer_valid"], match_judgments, k,
                                    parsed["new_changes"], step_output_sha256=proof["output_sha256"],
                                    step_slot=slot)
        record = {"k": k, "version": version, "model_key": model, "chain_id": chain_id,
                  "slot": slot, "prompt": prompt, "prompt_sha256": proof["prompt_sha256"],
                  "output": proof["output"], "output_sha256": proof["output_sha256"],
                  "parsed": parsed, "inventory_before": [dict(item) for item in inventory],
                  "inventory_after": [dict(item) for item in after],
                  "match_judgments": match_judgments, "match_lineage": match_lineage,
                  "previous_output_sha256": previous_sha,
                  "bead_prefix_sha256": bead_prefix_sha,
                  "history_prefix_sha256": lineage["history_prefix_sha256"],
                  "lineage": lineage,
                  "meta_sha256": proof["meta_sha256"], "producer_identity": proof["producer_identity"],
                  "execution_mode": "mock_only"}
        records.append(record)
        inventory = after
        previous_sha = record["output_sha256"]
    validate_chain(records, version, model, beads, templates["step_" + version])

    center_prompt = fill_template(templates["center"], {
        "WORK": WORK_NAME, "HISTORY": build_center_history(beads, records),
        "BEADS": build_center_beads(beads)})
    center_slot = _slot("center", chain_id=chain_id, version=version, model_key=model)
    center_lineage = {"chain_id": chain_id,
                      "source_step_sha256s": [record["output_sha256"] for record in records],
                      "source_step_slots": [record["slot"] for record in records],
                      "source_match_lineage": [match for record in records
                                                for match in record["match_lineage"]]}
    center_task = _task("center", center_slot, center_prompt, fingerprint["templates"]["center"], source_sha,
                        source_step_sha256s=center_lineage["source_step_sha256s"],
                        lineage=center_lineage)
    center_proof = execute_mock_task(evidence_dir, center_task, fingerprint, hashes, counters, metadata_index)
    center_record = {"chain_id": chain_id, "slot": center_slot, "prompt": center_prompt,
                     "prompt_sha256": center_proof["prompt_sha256"], "output": center_proof["output"],
                     "output_sha256": center_proof["output_sha256"], "parsed": center_proof["parsed"],
                     "source_step_sha256s": center_task["source_step_sha256s"],
                     "source_match_lineage": center_lineage["source_match_lineage"],
                     "lineage": center_lineage,
                     "meta_sha256": center_proof["meta_sha256"], "execution_mode": "mock_only"}
    validate_center_link(center_record, chain_id, records, beads, templates["center"])
    return records, center_record


def _statement_rows(chain_id: str, records: Sequence[Mapping[str, Any]], center: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        text = record["parsed"]["thread"].strip()
        if not text or text == "还看不出" or text in seen:
            continue
        seen.add(text)
        rows.append({"chain_id": chain_id, "kind": "step", "k": record["k"], "text": text})
    for index, item in enumerate(center["parsed"]["centers"]):
        rows.append({"chain_id": chain_id, "kind": "center", "center_idx": index, "text": item["center"]})
    for row in rows:
        row["statement_id"] = sha256_text(canonical_json(row))[:20]
    return rows


def deterministic_seed(*values: Any) -> int:
    return int(sha256_text(canonical_json(list(values)))[:8], 16)


def build_ident_musepack(template: str, statement: str, seed: int, task_id: str,
                         template_sha: str) -> dict[str, Any]:
    # Candidate shuffle is deterministic and the mapping is carried with the inline prompt.
    candidates = list(CANDIDATES)
    candidates.sort(key=lambda item: sha256_text(str(seed) + "|" + item))
    mapping = {"CANDIDATES": "\n".join("- " + item for item in candidates), "STATEMENT": statement}
    prompt = fill_template(template, mapping)
    source_text = statement + "\n\n" + mapping["CANDIDATES"]
    identity = canonical_muse_identity("Muse", "external Muse")
    pack = {"schema_version": "thread-musepack/2", "task_id": task_id,
            "logical_task_id": RUN_ID + ":" + task_id,
            "request_id": RUN_ID + ":muse:" + task_id,
            "target": MUSE_TARGET,
            "transport": identity["transport"], "provider": identity["provider"], "model": identity["model"],
            "requested_identity": identity,
            "template": {"id": "THREAD_IDENT_v0", "text": template, "sha256": template_sha},
            "source": {"id": "statement:" + task_id, "text": source_text,
                       "sha256": sha256_text(source_text)},
            "mapping": mapping, "seed": seed, "inline_prompt": prompt,
            "prompt_sha256": sha256_text(prompt), "no_file_reads": True,
            "canonicalization": "raw_unverified_until_independent_normalization"}
    pack["binding_sha256"] = musepack_binding(pack)
    return pack


def build_compare_musepack(template: str, work: str, beads_text: str, a_text: str, b_text: str,
                           mapping: Mapping[str, str], seed: int, task_id: str,
                           template_sha: str) -> dict[str, Any]:
    expected_mapping = {"WORK": work, "BEADS": beads_text, "A": a_text, "B": b_text}
    if dict(mapping) != expected_mapping:
        raise IntegrityError("compare A/B mapping is not the recorded blind assignment")
    prompt = fill_template(template, expected_mapping)
    source_text = canonical_json(expected_mapping)
    identity = canonical_muse_identity("Muse", "external Muse")
    pack = {"schema_version": "thread-musepack/2", "task_id": task_id,
            "logical_task_id": RUN_ID + ":" + task_id,
            "request_id": RUN_ID + ":muse:" + task_id,
            "target": MUSE_TARGET,
            "transport": identity["transport"], "provider": identity["provider"], "model": identity["model"],
            "requested_identity": identity,
            "template": {"id": "THREAD_COMPARE_v0", "text": template, "sha256": template_sha},
            "source": {"id": "compare-source:" + task_id, "text": source_text,
                       "sha256": sha256_text(source_text)},
            "mapping": expected_mapping, "seed": seed, "inline_prompt": prompt,
            "prompt_sha256": sha256_text(prompt), "no_file_reads": True,
            "canonicalization": "raw_unverified_until_independent_normalization"}
    pack["binding_sha256"] = musepack_binding(pack)
    return pack


def musepack_binding(pack: Mapping[str, Any]) -> str:
    bound = {key: pack.get(key) for key in (
        "schema_version", "task_id", "logical_task_id", "request_id", "target",
        "requested_identity", "transport", "provider", "model", "template",
        "source", "mapping", "seed", "inline_prompt", "prompt_sha256", "no_file_reads",
        "canonicalization")}
    return sha256_text(canonical_json(bound))


def validate_musepack(pack: Mapping[str, Any]) -> None:
    if any(key in pack for key in ("source_path", "template_path", "attachment_path", "read_file")):
        raise IntegrityError("Musepack must not make a content judge read files")
    expected_pack_keys = {"schema_version", "task_id", "logical_task_id", "request_id", "target",
                          "requested_identity", "transport", "provider", "model", "template", "source",
                          "mapping", "seed", "inline_prompt", "prompt_sha256", "no_file_reads",
                          "canonicalization", "binding_sha256"}
    if set(pack) != expected_pack_keys or pack.get("schema_version") != "thread-musepack/2" or \
            pack.get("no_file_reads") is not True:
        raise IntegrityError("Musepack schema/no-file-read policy invalid")
    if (not isinstance(pack.get("task_id"), str) or not pack["task_id"].strip() or
            pack.get("logical_task_id") != RUN_ID + ":" + pack["task_id"] or
            pack.get("request_id") != RUN_ID + ":muse:" + pack["task_id"]):
        raise IntegrityError("Muse task/logical-task/request identity binding is incomplete")
    identity = canonical_muse_identity("Muse", "external Muse")
    if (pack.get("target") != MUSE_TARGET or pack.get("requested_identity") != identity or
            pack.get("provider") != identity["provider"] or pack.get("model") != identity["model"] or
            pack.get("transport") != identity["transport"]):
        raise IntegrityError("Muse target/provider/model/transport identity differs from canonical mapping")
    template, source, mapping = pack.get("template"), pack.get("source"), pack.get("mapping")
    if not isinstance(template, dict) or set(template) != {"id", "text", "sha256"} or \
            not isinstance(source, dict) or set(source) != {"id", "text", "sha256"} or \
            not isinstance(mapping, dict):
        raise IntegrityError("Musepack must inline template, source and mapping")
    template_text, source_text = template.get("text"), source.get("text")
    if not isinstance(template_text, str) or not isinstance(source_text, str):
        raise IntegrityError("Musepack omitted full template/source text")
    if sha256_text(template_text) != template.get("sha256") or sha256_text(source_text) != source.get("sha256"):
        raise IntegrityError("Musepack template/source SHA256 mismatch")
    template_name = template.get("id")
    template_key = {"THREAD_IDENT_v0": "ident", "THREAD_COMPARE_v0": "compare"}.get(template_name)
    if template_key is None:
        raise IntegrityError("Musepack template identity is unknown")
    frozen_template_path = _safe_child(_repo_root(), TEMPLATE_PATHS[template_key])
    frozen_template_bytes = frozen_template_path.read_bytes()
    if (template_text.encode("utf-8") != frozen_template_bytes or
            template.get("sha256") != sha256_bytes(frozen_template_bytes)):
        raise IntegrityError("Musepack template differs from the frozen prompt bytes")
    if template_name == "THREAD_IDENT_v0":
        if set(mapping) != {"CANDIDATES", "STATEMENT"} or \
                any(not isinstance(value, str) for value in mapping.values()):
            raise IntegrityError("ident mapping must match THREAD_IDENT_v0 placeholders exactly")
        expected_candidates = sorted(CANDIDATES, key=lambda item: sha256_text(str(pack.get("seed")) + "|" + item))
        expected_candidate_text = "\n".join("- " + item for item in expected_candidates)
        if mapping["CANDIDATES"] != expected_candidate_text:
            raise IntegrityError("ident candidate mapping differs from the seeded frozen candidate set")
        expected_source = mapping.get("STATEMENT", "") + "\n\n" + mapping.get("CANDIDATES", "")
    else:
        if set(mapping) != {"WORK", "BEADS", "A", "B"} or \
                any(not isinstance(value, str) for value in mapping.values()) or mapping.get("WORK") != WORK_NAME:
            raise IntegrityError("compare mapping must match THREAD_COMPARE_v0 placeholders exactly")
        expected_source = canonical_json(mapping)
    if source_text != expected_source:
        raise IntegrityError("Musepack source text does not match its mapping")
    prompt = fill_template(template_text, mapping)
    if prompt != pack.get("inline_prompt") or sha256_text(prompt) != pack.get("prompt_sha256"):
        raise IntegrityError("Musepack full inline prompt/mapping/seed binding failed")
    if type(pack.get("seed")) is not int or not pack.get("task_id"):
        raise IntegrityError("Musepack seed/task identity missing")
    if any(key in pack for key in ("source_path", "template_path", "attachment_path", "read_file")):
        raise IntegrityError("Musepack must not make a content judge read files")
    if pack.get("binding_sha256") != musepack_binding(pack):
        raise IntegrityError("Musepack task/source/template/prompt/mapping/seed binding SHA256 mismatch")


_QUOTE_RE = re.compile(r"“([^”]+)”|\"([^\"]+)\"|「([^」]+)」|『([^』]+)』|‘([^’]+)’")


def _quoted_snippets(text: str) -> list[str]:
    return [part for group in _QUOTE_RE.findall(text) for part in group if part]


def _fixed_muse_schema(pack: Mapping[str, Any], parsed: Any) -> dict[str, Any]:
    template_id = pack["template"]["id"]
    if not isinstance(parsed, dict):
        raise IntegrityError("Muse raw response must be a JSON object")
    if template_id == "THREAD_IDENT_v0":
        required = {"guess", "confidence", "also_fits", "why"}
        mapping = pack["mapping"]
        if set(parsed) != required:
            raise IntegrityError("THREAD_IDENT_v0 fields must match the frozen schema exactly")
        guess, confidence = parsed["guess"], parsed["confidence"]
        fits, why = parsed["also_fits"], parsed["why"]
        if not isinstance(guess, str) or (guess != "说不准" and guess not in CANDIDATES):
            raise IntegrityError("ident guess must be one frozen candidate or 说不准")
        if type(confidence) is not int or not 0 <= confidence <= 100:
            raise IntegrityError("ident confidence must be an exact integer from 0 to 100")
        if (not isinstance(fits, list) or any(not isinstance(item, str) or item not in CANDIDATES for item in fits) or
                len(set(fits)) != len(fits) or (guess in CANDIDATES and guess in fits)):
            raise IntegrityError("ident also_fits must contain unique legal candidates other than guess")
        if not isinstance(why, str) or not why.strip():
            raise IntegrityError("ident why must be nonempty")
        if any(quote not in mapping["STATEMENT"] for quote in _quoted_snippets(why)):
            raise IntegrityError("ident why contains a quote unsupported by its statement")
        return parsed

    if template_id != "THREAD_COMPARE_v0":
        raise IntegrityError("no fixed response schema exists for this Muse template")
    required = {"better", "specificity", "grounding", "flattened", "openness", "why"}
    if set(parsed) != required or parsed["better"] not in ("A", "B", "不可判"):
        raise IntegrityError("THREAD_COMPARE_v0 top-level schema is invalid")
    mapping = pack["mapping"]
    for field in ("specificity", "grounding", "openness"):
        value = parsed[field]
        if not isinstance(value, dict) or set(value) != {"A", "B"}:
            raise IntegrityError(field + " must contain exactly A and B")
        for candidate in ("A", "B"):
            text = value[candidate]
            if not isinstance(text, str) or not text.strip():
                raise IntegrityError(field + " entries must be nonempty strings")
            quotes = _quoted_snippets(text)
            if not quotes or any(quote not in mapping[candidate] for quote in quotes):
                raise IntegrityError(field + " citation is missing or unsupported by candidate " + candidate)
    flattened = parsed["flattened"]
    if not isinstance(flattened, dict) or set(flattened) != {"A", "B"}:
        raise IntegrityError("flattened must contain exactly A and B lists")
    for candidate in ("A", "B"):
        entries = flattened[candidate]
        if not isinstance(entries, list) or any(not isinstance(item, str) or not item.strip() for item in entries):
            raise IntegrityError("flattened entries must be lists of nonempty strings")
        for item in entries:
            quotes = _quoted_snippets(item)
            if not quotes or any(quote not in mapping[candidate] for quote in quotes):
                raise IntegrityError("flattened citation is missing or unsupported by candidate " + candidate)
    why = parsed["why"]
    if not isinstance(why, str) or not why.strip():
        raise IntegrityError("compare why must be nonempty")
    why_quotes = _quoted_snippets(why)
    if (not any(quote in mapping["A"] for quote in why_quotes) or
            not any(quote in mapping["B"] for quote in why_quotes) or
            any(quote not in mapping["A"] and quote not in mapping["B"] for quote in why_quotes)):
        raise IntegrityError("compare why must cite exact supported text from both candidates")
    return parsed


def validate_muse_raw_unverified(pack: Mapping[str, Any], result: Mapping[str, Any]) -> dict[str, Any]:
    """Inspect structure only. This never authenticates a provider or counts a real return."""
    validate_musepack(pack)
    raw_response = result.get("raw_response")
    if not isinstance(raw_response, str):
        raise IntegrityError("raw_unverified result must preserve the original response text")
    parsed = _fixed_muse_schema(pack, extract_json(raw_response))
    raw_bytes = raw_response.encode("utf-8")
    return {"status": "raw_unverified", "canonicalization": "raw_unverified",
            "schema_id": pack["template"]["id"], "parsed": parsed,
            "raw_response": raw_response, "raw_response_sha256": sha256_bytes(raw_bytes),
            "real_return_count": 0, "music_acceptance": "NOT_PERFORMED"}


def _validate_trusted_muse_receipt(pack: Mapping[str, Any], raw_bytes: bytes,
                                   receipt: Any) -> dict[str, Any]:
    required = {"receipt_schema", "attestation_class", "verified", "bytes_verified", "source_bound", "task_id",
                "logical_task_id", "request_id", "target", "source_sha256", "template_sha256",
                "mapping_sha256", "seed", "prompt_sha256", "raw_response_sha256",
                "raw_response_size", "terminal_status", "terminal_id", "requested_provider",
                "requested_model", "requested_transport", "reported_provider", "reported_model",
                "reported_transport", "actual_provider", "actual_model", "actual_transport"}
    if not isinstance(receipt, dict) or set(receipt) != required:
        raise IntegrityError("trusted archive receipt exact field set is incomplete or unexpected")
    identity = canonical_muse_identity("Muse", "external Muse")
    expected = {"receipt_schema": "muse_archive_receipt_v1", "verified": True, "bytes_verified": True,
                "source_bound": True,
                "task_id": pack["task_id"], "logical_task_id": pack["logical_task_id"],
                "request_id": pack["request_id"], "target": MUSE_TARGET,
                "source_sha256": pack["source"]["sha256"],
                "template_sha256": pack["template"]["sha256"],
                "mapping_sha256": sha256_text(canonical_json(pack["mapping"])),
                "seed": pack["seed"], "prompt_sha256": pack["prompt_sha256"],
                "raw_response_sha256": sha256_bytes(raw_bytes), "raw_response_size": len(raw_bytes),
                "terminal_status": "completed", "requested_provider": identity["provider"],
                "requested_model": identity["model"], "requested_transport": identity["transport"],
                "reported_provider": identity["provider"], "reported_model": identity["model"],
                "reported_transport": identity["transport"],
                "actual_provider": identity["provider"], "actual_model": identity["model"],
                "actual_transport": identity["transport"]}
    for key, value in expected.items():
        if receipt.get(key) != value:
            raise IntegrityError("trusted archive receipt is not bound to exact task bytes/identity: " + key)
    if (receipt.get("attestation_class") not in ("TEST_ONLY", "TRUSTED_SOURCEBOUND_ARCHIVE") or
            not isinstance(receipt.get("terminal_id"), str) or not receipt["terminal_id"].strip() or
            type(receipt.get("raw_response_size")) is not int or
            receipt.get("reported_transport") in ("", "mock", "file", "unknown") or
            receipt.get("actual_transport") != MUSE_TRANSPORT):
        raise IntegrityError("trusted archive receipt lacks completed terminal or reported transport")
    return receipt


def validate_muse_return(pack: Mapping[str, Any], result: Mapping[str, Any],
                         trusted_identity_verifier: Callable[[Mapping[str, Any], bytes], Mapping[str, Any]] | None = None
                         ) -> dict[str, Any]:
    """Authenticate a returned Muse task only through a trusted archive verifier."""
    validate_musepack(pack)
    if not callable(trusted_identity_verifier):
        raise CompletionPending("trusted Muse identity/archive verifier unavailable; return remains raw_unverified")
    if set(result) != {"task_id", "logical_task_id", "request_id", "provider", "model", "transport",
                       "raw_response"}:
        raise IntegrityError("Muse return task/request/result fields must match the frozen exact schema")
    if (result.get("task_id") != pack["task_id"] or
            result.get("logical_task_id") != pack["logical_task_id"] or
            result.get("request_id") != pack["request_id"]):
        raise IntegrityError("Muse return task/logical-task/request identity differs from the frozen pack")
    reported_identity = canonical_muse_identity(str(result.get("provider", "")),
                                                str(result.get("model", "")))
    if (reported_identity != pack["requested_identity"] or
            str(result.get("transport", "")).strip().lower() != MUSE_TRANSPORT):
        raise IntegrityError("reported Muse identity/transport differs from canonical requested target")
    raw_response = result.get("raw_response")
    if not isinstance(raw_response, str):
        raise IntegrityError("Muse return must preserve exact raw_response text")
    raw_bytes = raw_response.encode("utf-8")
    receipt = _validate_trusted_muse_receipt(pack, raw_bytes, trusted_identity_verifier(pack, raw_bytes))
    structural = validate_muse_raw_unverified(pack, result)
    return {**structural,
            "status": "test_only_sourcebound_receipt" if receipt["attestation_class"] == "TEST_ONLY"
            else "trusted_sourcebound_archive_receipt",
            "trusted_receipt_sha256": sha256_text(canonical_json(receipt)),
            "trusted_terminal_id": receipt["terminal_id"],
            "target": receipt["target"],
            "requested_provider": receipt["requested_provider"],
            "requested_model": receipt["requested_model"],
            "reported_provider": receipt["actual_provider"],
            "reported_model": receipt["actual_model"],
            "reported_transport": receipt["reported_transport"],
            "attestation_class": receipt["attestation_class"],
            "real_return_count": 0 if receipt["attestation_class"] == "TEST_ONLY" else 1,
            "music_acceptance": "NOT_PERFORMED"}


def assert_exact_set(expected: Iterable[tuple[Any, ...]], actual: Iterable[tuple[Any, ...]], label: str) -> None:
    expected_list, actual_list = list(expected), list(actual)
    if len(expected_list) != len(set(expected_list)):
        raise IntegrityError(label + " expected set itself has duplicates")
    if len(actual_list) != len(set(actual_list)) or set(expected_list) != set(actual_list):
        raise IntegrityError(label + " actual identity set is missing, extra or duplicated")


def build_chain_record_text(beads: Sequence[Mapping[str, Any]], records: Sequence[Mapping[str, Any]],
                            center: Mapping[str, Any]) -> str:
    lines = ["逐段看出的线："]
    for record in records:
        lines.append("第%d段：%s" % (record["k"], record["parsed"]["thread"] or "（空）"))
    lines.append("最后的线：%s" % records[-1]["parsed"]["thread"])
    lines.append("全曲核心关系候选：%s" % canonical_json(center["parsed"]["centers"]))
    return "\n".join(lines)


def _run_review_jobs(root: Path, evidence_dir: Path, fingerprint: Mapping[str, Any],
                     templates: Mapping[str, str], beads: Sequence[Mapping[str, Any]],
                     chains: Mapping[str, Sequence[Mapping[str, Any]]], centers: Mapping[str, Mapping[str, Any]],
                     counters: dict[str, int], hashes: dict[str, str],
                     metadata_index: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    ident_expected: list[tuple[Any, ...]] = []
    ident_actual: list[tuple[Any, ...]] = []
    musepacks: list[dict[str, Any]] = []
    ident_rows: list[dict[str, Any]] = []
    for chain_id, records in sorted(chains.items()):
        rows = _statement_rows(chain_id, records, centers[chain_id])
        for row in rows:
            candidates = list(CANDIDATES)
            seed = deterministic_seed(chain_id, row["statement_id"], "THREAD_IDENT_v0")
            candidates.sort(key=lambda item: sha256_text(str(seed) + "|" + item))
            mapping = {"CANDIDATES": "\n".join("- " + item for item in candidates),
                       "STATEMENT": row["text"]}
            prompt = fill_template(templates["ident"], mapping)
            for reviewer in REVIEWERS:
                task_id = "ident:" + chain_id + ":" + row["statement_id"] + ":" + reviewer
                slot = _slot("ident", chain_id=chain_id, statement_id=row["statement_id"], reviewer=reviewer)
                task = _task("ident", slot, prompt, fingerprint["templates"]["ident"],
                             sha256_text(canonical_json(row)), self_review=(reviewer == chain_id.rsplit("_", 1)[-1]),
                             canonicalization="mock_unverified")
                proof = execute_mock_task(evidence_dir, task, fingerprint, hashes, counters, metadata_index)
                ident_expected.append((chain_id, row["statement_id"], reviewer))
                actual_slot = proof["meta"]["slot"]
                ident_actual.append((actual_slot["chain_id"], actual_slot["statement_id"], actual_slot["reviewer"]))
                ident_rows.append({**row, "reviewer": reviewer,
                                   "self_review": task["self_review"],
                                   "canonicalization": "mock_unverified",
                                   "result_status": "mock_only"})
                if reviewer == "muse_external":
                    musepacks.append(build_ident_musepack(templates["ident"], row["text"], seed,
                                                          task_id, fingerprint["templates"]["ident"]))
                    validate_musepack(musepacks[-1])
    assert_exact_set(ident_expected, ident_actual, "ident statement × reviewer")

    compare_expected: list[tuple[Any, ...]] = []
    compare_actual: list[tuple[Any, ...]] = []
    compare_rows: list[dict[str, Any]] = []
    bead_text = build_center_beads(beads)
    for model in GENERATION_MODELS:
        v2_id, v3_id = "v2_" + model, "v3_" + model
        text_v2 = build_chain_record_text(beads, chains[v2_id], centers[v2_id])
        text_v3 = build_chain_record_text(beads, chains[v3_id], centers[v3_id])
        for order in (0, 1):
            a_text, b_text = (text_v2, text_v3) if order == 0 else (text_v3, text_v2)
            assignment = {"A": "v2" if order == 0 else "v3", "B": "v3" if order == 0 else "v2"}
            mapping = {"WORK": WORK_NAME, "BEADS": bead_text, "A": a_text, "B": b_text}
            prompt = fill_template(templates["compare"], mapping)
            for reviewer in REVIEWERS:
                task_id = "compare:%s:o%d:%s" % (model, order, reviewer)
                slot = _slot("compare", model_key=model, order=order, reviewer=reviewer)
                task = _task("compare", slot, prompt, fingerprint["templates"]["compare"],
                             sha256_text(canonical_json(mapping)), blind_mapping=assignment,
                             seed=deterministic_seed(model, order, reviewer), canonicalization="mock_unverified")
                proof = execute_mock_task(evidence_dir, task, fingerprint, hashes, counters, metadata_index)
                compare_expected.append((model, order, reviewer))
                actual_slot = proof["meta"]["slot"]
                compare_actual.append((actual_slot["model_key"], actual_slot["order"], actual_slot["reviewer"]))
                compare_rows.append({"model_key": model, "order": order, "reviewer": reviewer,
                                     "mapping": assignment, "self_review": reviewer == model,
                                     "canonicalization": "mock_unverified", "result_status": "mock_only"})
                if reviewer == "muse_external":
                    pack = build_compare_musepack(templates["compare"], WORK_NAME, bead_text,
                                                  a_text, b_text, mapping,
                                                  deterministic_seed(model, order, reviewer), task_id,
                                                  fingerprint["templates"]["compare"])
                    validate_musepack(pack)
                    musepacks.append(pack)
    assert_exact_set(compare_expected, compare_actual, "compare order 0/1 × reviewer")
    return {"ident_expected": ident_expected, "ident_actual": ident_actual,
            "compare_expected": compare_expected, "compare_actual": compare_actual,
            "ident_records": ident_rows, "compare_records": compare_rows,
            "musepack_count": len(musepacks), "musepacks_validated": True,
            "muse_real_return_count": 0}


def run_mock(root: Path, evidence_dir: Path) -> dict[str, Any]:
    beads, _, _ = load_frozen_inputs(root)
    templates = {name: _safe_child(root, relative).read_text(encoding="utf-8")
                 for name, relative in TEMPLATE_PATHS.items()}
    pair = validate_prompt_pair(templates["step_v2"], templates["step_v3"])
    fingerprint = build_fingerprint(root)
    first_counters = {"mock_submissions": 0, "reused": 0}
    expected_hashes: dict[str, str] = {}
    first_index = scan_metadata_index(evidence_dir)
    chains: dict[str, list[dict[str, Any]]] = {}
    centers: dict[str, dict[str, Any]] = {}
    for model in GENERATION_MODELS:
        for version in VERSIONS:
            chain_id = version + "_" + model
            chains[chain_id], centers[chain_id] = _build_mock_chain(
                root, evidence_dir, fingerprint, beads, templates, version, model,
                first_counters, expected_hashes, first_index)
    review = _run_review_jobs(root, evidence_dir, fingerprint, templates, beads, chains, centers,
                              first_counters, expected_hashes, first_index)

    # Re-run the identical full plan from disk.  Every slot must validate against
    # its actual metadata/prompt/output bytes and no new mock submission is allowed.
    second = {"mock_submissions": 0, "reused": 0}
    second_index = scan_metadata_index(evidence_dir)
    for model in GENERATION_MODELS:
        for version in VERSIONS:
            _build_mock_chain(root, evidence_dir, fingerprint, beads, templates, version, model,
                              second, expected_hashes, second_index)
    review2 = _run_review_jobs(root, evidence_dir, fingerprint, templates, beads, chains, centers,
                               second, expected_hashes, second_index)
    if build_fingerprint(root)["fingerprint_sha256"] != fingerprint["fingerprint_sha256"]:
        raise IntegrityError("source/template/driver/config changed during mock run; start a new run")
    exact_disk_proof = (first_counters["mock_submissions"] > 0 and
                        second["reused"] == first_counters["mock_submissions"] and
                        second["mock_submissions"] == 0)
    if not exact_disk_proof:
        raise IntegrityError("second run did not prove exact disk reuse with zero new submissions")
    if review2["ident_expected"] != review["ident_expected"] or review2["compare_expected"] != review["compare_expected"]:
        raise IntegrityError("review identity sets changed on second run")
    nlv_rows = [{"chain_id": chain_id, "step_k": record["k"],
                 "quotes": record["parsed"]["no_longer_valid"],
                 "judgments": record["match_judgments"],
                 "inventory_after": record["inventory_after"],
                 "next_inventory_before": chains[chain_id][record["k"]]["inventory_before"]}
                for chain_id, records in sorted(chains.items()) for record in records
                if record["parsed"]["no_longer_valid"]]
    if len(nlv_rows) != len(chains) or any(
            row["inventory_after"] != row["next_inventory_before"] or
            row["inventory_after"] or len(row["judgments"]) != 1 or
            row["judgments"][0]["match"] != 1 for row in nlv_rows):
        raise IntegrityError("NLV exact-match retirement/next-prefix lineage did not validate")
    return {
        "run_id": RUN_ID, "mode": "mock_only", "completion": "COMPLETION_PENDING",
        "generation_plan": {"models": list(GENERATION_MODELS), "versions": list(VERSIONS),
                            "real_submissions": 0, "status": "HELD_NO_REAL_SUBMISSIONS"},
        "review_plan": {"reviewers": list(REVIEWERS), "self_review_marked": True,
                        "external_muse_real_returns": 0},
        "mock_chain_validation": "PASS", "prompt_diff": pair,
        "chain_count": len(chains), "steps_per_chain": K_EXPECTED,
        "center_count": len(centers), "first_run_mock_submissions": first_counters["mock_submissions"],
        "second_run_reused": second["reused"], "second_run_new_submissions": second["mock_submissions"],
        "exactdiskproof": exact_disk_proof, "secondrun0newsubmit": second["mock_submissions"] == 0,
        "ident_pair_count": len(review["ident_expected"]),
        "compare_pair_count": len(review["compare_expected"]),
        "ident_set_exact": True, "compare_set_exact": True,
        "musepack_count": review["musepack_count"], "musepack_inline_validation": True,
        "muse_real_return_count": 0, "real_model_submissions": 0,
        "nlv_integrated_retirement_count": len(nlv_rows),
        "nlv_match_tasks_first_run": first_counters.get("match_submissions", 0),
        "nlv_match_tasks_reverified_second_run": second.get("match_reused", 0),
        "nlv_exact_source_retirement_validated": True,
        "center_match_lineage_count": sum(len(center.get("source_match_lineage", []))
                                           for center in centers.values()),
        "legacy_control_policy": LEGACY_CONTROL,
        "new_opus_or_sol": False,
        "music_acceptance": "NOT_PERFORMED",
        "evidence_dir_is_temporary_only": True,
        "frozen_hashes": {"sources": fingerprint["sources"], "templates": fingerprint["templates"],
                          "driver_sha256": fingerprint["driver_sha256"],
                          "config_sha256": fingerprint["config_sha256"]},
    }


def check_v4_transport(root: Path) -> dict[str, Any]:
    """Read-only presence check; v4, partial v5 and in-flight v6 are never imported."""
    tools_dir = Path(root) / "tools"
    v4_exists = (tools_dir / "experiment_calls_v4.py").is_file()
    v5_exists = (tools_dir / "experiment_calls_v5.py").is_file()
    return {"status": "blocked",
            "v4": "present_unverified" if v4_exists else "absent",
            "v5": "partial_unusable" if v5_exists else "absent",
            "v6": "in_flight_not_auto_adopted",
            "dependencies": "not imported or verified",
            "real_submissions": 0,
            "reason": "shared entry and real protocol lack independent acceptance"}


def strict_preflight(root: Path) -> dict[str, Any]:
    try:
        pair = validate_prompt_pair(
            _safe_child(root, TEMPLATE_PATHS["step_v2"]).read_text(encoding="utf-8"),
            _safe_child(root, TEMPLATE_PATHS["step_v3"]).read_text(encoding="utf-8"))
        fingerprint = build_fingerprint(root)
    except Exception as exc:
        return {"run_id": RUN_ID, "completion": "FAILED", "reason": str(exc),
                "real_model_submissions": 0, "writes_to_run_directory": 0}
    transport = check_v4_transport(root)
    return {"run_id": RUN_ID, "completion": "COMPLETION_PENDING", "prompt_diff": pair,
            "generation_plan": {"models": list(GENERATION_MODELS), "versions": list(VERSIONS),
                                "real_submissions": 0, "status": "HELD_NO_REAL_SUBMISSIONS"},
            "review_plan": {"reviewers": list(REVIEWERS), "self_review_marked": True,
                            "external_muse_real_returns": 0},
            "fingerprint_sha256": fingerprint["fingerprint_sha256"],
            "frozen_hashes": {"sources": fingerprint["sources"], "templates": fingerprint["templates"],
                              "driver_sha256": fingerprint["driver_sha256"],
                              "config_sha256": fingerprint["config_sha256"]},
            "transport": transport, "real_model_submissions": 0,
            "external_muse_returns": 0, "chain_outputs_verified": 0,
            "reason": "real route is blocked: v4 is unverified, v5 partial is unusable, and v6 is never auto-selected",
            "legacy_gpt56w_prefix_policy": LEGACY_CONTROL,
            "new_opus_or_sol": False, "writes_to_run_directory": 0,
            "completion_artifact": "not created; mock output cannot mark DONE"}


def run_stages(stage_names: Sequence[str], stage_funcs: Mapping[str, Callable[[], Mapping[str, Any]]]) -> dict[str, Any]:
    """Stop the current and every later job/stage after a failed or queue-stop result."""
    report: dict[str, Any] = {"queue_stop": False, "stages": []}
    for index, name in enumerate(stage_names):
        if report["queue_stop"]:
            report["stages"].append({"stage": name, "status": "stopped_before_start", "jobs": []})
            continue
        result = dict(stage_funcs[name]())
        report["stages"].append({"stage": name, **result})
        if result.get("status") != "ok" or result.get("queue_stop") is True:
            report["queue_stop"] = True
            report["stages"][-1]["remaining_jobs"] = "stopped"
            for later in stage_names[index + 1:]:
                report["stages"].append({"stage": later, "status": "stopped_before_start", "jobs": []})
            break
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--mock", action="store_true", help="run the full mocked chain in a temporary directory")
    modes.add_argument("--strict", action="store_true", help="read-only production preflight; never submits")
    modes.add_argument("--real", action="store_true", help="read-only preflight, then remain blocked")
    args = parser.parse_args(argv)
    root = _repo_root()
    if args.mock:
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(prefix="run145_thread_resume_r5_") as temp:
            result = run_mock(root, Path(temp) / "evidence")
    else:
        result = strict_preflight(root)
        if args.real:
            result["reason"] = "BLOCKED before real work: " + result["reason"]
            result["real_model_submissions"] = 0
            result["writes_to_run_directory"] = 0
    # Keep command output ASCII-safe across Windows console code pages.
    print(json.dumps(result, ensure_ascii=True, indent=2))
    if args.real:
        return 3
    return 0 if result.get("mock_chain_validation") == "PASS" or result.get("completion") == "COMPLETION_PENDING" else 1


if __name__ == "__main__":
    raise SystemExit(main())
