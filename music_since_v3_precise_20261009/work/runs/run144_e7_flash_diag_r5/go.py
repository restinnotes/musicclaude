"""run144 E7 Flash diagnostic pipeline; offline-safe and never production."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run144_e7_flash_diag_r5"
RUN_DIR = ROOT / "runs" / RUN_ID

CFG = {
    "gen": "gflash",
    "chooser": "gflash",
    "auditors": ("gflash", "luna_noweb"),
    "judges": ("gflash", "luna_noweb"),
    "history": "run130:gpt56w",
}
WORK_KEY = "op60"
WORK_NAME = "肖邦《船歌》Op.60"
K_EXPECTED = 23
MAX_ATTEMPTS = 2
STRICT_JSON_FENCE_RE = re.compile(r"```(?:json)?[ \t]*\r?\n(.*?)\r?\n```", re.I | re.S)
SEED_COMPARE = 139060
POSITIONS = ("甲", "乙", "丙")
ACTIONS = ("保持", "补充", "更新", "沉默")
AUDIT_CLASSES = ("insight", "restatement", "manufactured", "imported")
AUDIT_DROP = ("manufactured", "imported")
MOCK_NAMESPACE = "MOCK:run144_e7_flash_diag_r5"
ARTIFACT_SCHEMA = "run144-exact-artifacts-v1"

INPUT_PATHS = {
    "beads": "runs/run130_thread_e6/beads_clean.md",
    "history": "runs/run130_thread_e6/steps.json",
    "run124_b": "runs/run124_render/surface__B__gpt56w__op60.md",
    "c_gpro_s3": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gpro_web__s3.md",
    "c_gpro_s3_meta": "runs/run132_v2a_gemini_baseline/meta/run132__op60__gpro_web__s3.json",
    "c_gflash_s1": "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gflash_web__s1.md",
    "c_gflash_s1_meta": "runs/run132_v2a_gemini_baseline/meta/run132__op60__gflash_web__s1.json",
}
TEMPLATE_PATHS = {
    "WHY_GATE_v4": "prompts/versions/WHY_GATE_v4.txt",
    "MECH_v1": "prompts/tooling/MECH_v1.txt",
    "MECH_AUDIT_v0": "prompts/tooling/MECH_AUDIT_v0.txt",
    "E7_SURFACE_v0": "prompts/versions/E7_SURFACE_v0.txt",
    "E7_COMPARE_v0": "prompts/tooling/E7_COMPARE_v0.txt",
}
BASELINE_MODELS = {"c_gpro_s3": "gpro_web", "c_gflash_s1": "gflash_web"}
MUSE_TARGET = "claude-proxy/muse-spark-1.3-contributor-free"
MUSE_TRANSPORT = "mcp"
IDENTITY_LEAK_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:gpt(?:[-_ ]?\w*)?|gemini|claude|luna(?:_noweb)?|"
    r"gpro(?:_web)?|gflash(?:_web)?|muse|sonnet|run\d{2,3}|v2a|E7_[A-Za-z0-9_]+|ATTN_[A-Za-z0-9_]+)(?![A-Za-z0-9_])"
)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
REL_HEAD_RE = re.compile(r"^###\s+(.*)$", re.M)


class Run144Error(RuntimeError):
    pass


class RealExecutionBlocked(Run144Error):
    pass


class IntegrityError(Run144Error):
    pass


class QueueStopped(Run144Error):
    pass


class StageFailed(Run144Error):
    pass


class TransportFailure(Run144Error):
    """Injected transport failure with exact proof bytes; callers cannot self-certify."""

    def __init__(self, message: str, *, phase: str, proof: Any = None, raw_error: bytes = b"") -> None:
        super().__init__(message)
        self.phase = phase
        self.proof = proof
        self.raw_error = bytes(raw_error)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(json_bytes(value))
    tmp.replace(path)


def read_json(path: Path) -> Any:
    return strict_json_loads(path.read_text(encoding="utf-8"))


def _reject_json_constant(value: str) -> None:
    raise ValueError("non-finite JSON constant: " + value)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key: " + key)
        result[key] = value
    return result


def strict_json_loads(text: str) -> Any:
    """Parse one complete JSON object/array or one complete JSON fence."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("empty JSON input")
    stripped = text.strip()
    fence = STRICT_JSON_FENCE_RE.fullmatch(stripped)
    payload = fence.group(1) if fence else stripped
    value = json.loads(payload, object_pairs_hook=_unique_object,
                       parse_constant=_reject_json_constant)
    if not isinstance(value, (dict, list)):
        raise ValueError("top-level JSON must be an object or array")
    return value


def transport_retry_allowed(*, phase: str, proof: Any,
                            verifier: Callable[[Any, Mapping[str, Any]], Any] | None,
                            expected_binding: Mapping[str, Any], retries_remaining: int) -> bool:
    """A retry requires a trusted source-bound receipt, not a caller safety claim or hash."""
    if (phase != "pre_submit" or not callable(verifier) or
            type(retries_remaining) is not int or not 1 <= retries_remaining <= MAX_ATTEMPTS):
        return False
    try:
        receipt = verifier(proof, dict(expected_binding))
    except Exception:
        return False
    return (isinstance(receipt, dict) and receipt.get("verified") is True and
            receipt.get("submission_state") == "not_submitted" and
            receipt.get("proof_scope") == "sourcebound_pre_submit_v1" and
            receipt.get("binding") == dict(expected_binding))


def fill_template(template: str, **values: Any) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", str(value))
    leftovers = PLACEHOLDER_RE.findall(out)
    if leftovers:
        raise IntegrityError("unfilled prompt placeholder(s): " + ", ".join(sorted(set(leftovers))))
    return out


def extract_json_object(text: str) -> tuple[bool, Any, str | None]:
    try:
        value = strict_json_loads(text)
    except Exception as exc:
        return False, None, "invalid complete JSON object: " + type(exc).__name__
    if not isinstance(value, dict):
        return False, None, "top level is not an object"
    return True, value, None


def extract_json_array(text: str) -> tuple[bool, Any, str | None]:
    try:
        value = strict_json_loads(text)
    except Exception as exc:
        return False, None, "invalid complete JSON array: " + type(exc).__name__
    if not isinstance(value, list):
        return False, None, "top level is not an array"
    return True, value, None


def mm_start_of(title: str) -> int | None:
    match = re.search(r"m{1,2}\.\s*(\d+)", title or "", re.I) or re.search(r"(\d+)", title or "")
    return int(match.group(1)) if match else None


def split_beads(text: str) -> list[dict[str, Any]]:
    matches = list(REL_HEAD_RE.finditer(text))
    beads: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chunk = text[match.start():end]
        title = match.group(1).strip()
        here = chunk.find("【此刻】")
        rel = chunk.find("【前后关系候选】", here + 1 if here >= 0 else 0)
        if here < 0 or rel < 0:
            raise IntegrityError("bead missing required section at k%d" % (index + 1))
        now_text = chunk[here + len("【此刻】"):rel]
        now_lines = [line.strip() for line in now_text.splitlines() if line.strip()]
        body = title + "\n【此刻】\n" + "\n".join(now_lines)
        beads.append({"k": index + 1, "title": title, "text": body,
                      "mm_start": mm_start_of(title), "now_lines": now_lines})
    expected = list(range(1, K_EXPECTED + 1))
    actual = [bead["k"] for bead in beads]
    if actual != expected:
        raise IntegrityError("bead k set/order mismatch: %s" % actual)
    return beads


def now_items(bead: Mapping[str, Any]) -> list[str]:
    items: list[str] = []
    for line in bead["now_lines"]:
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif items:
            items[-1] += " " + line
        else:
            items.append(line)
    return [item for item in items if item]


def time_of(title: str) -> str:
    match = re.match(r"^\s*(m{1,2}\.\s*\d+(?:\s*[–\-—]\s*\d+)?)", title, re.I)
    return match.group(1) if match else title.split(" ", 1)[0]


def _load_history(source_root: Path) -> tuple[dict[int, list[dict[str, Any]]], str]:
    data = read_json(source_root / INPUT_PATHS["history"])
    rows = [row for row in data.get("steps", [])
            if row.get("model") == "gpt56w" and row.get("work") == WORK_KEY]
    by_k: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        k = row.get("k")
        if not isinstance(k, int) or k in by_k:
            raise IntegrityError("run130 history has duplicate or invalid k")
        inventory = row.get("inventory_after") or []
        if not isinstance(inventory, list):
            raise IntegrityError("run130 history inventory is not a list at k%d" % k)
        safe_inventory = []
        for item in inventory:
            if not isinstance(item, dict) or not isinstance(item.get("change"), str) or not isinstance(item.get("from"), str):
                raise IntegrityError("run130 history item schema invalid at k%d" % k)
            safe_inventory.append({"change": item["change"], "from": item["from"]})
        by_k[k] = safe_inventory
    expected = list(range(1, K_EXPECTED + 1))
    if sorted(by_k) != expected:
        raise IntegrityError("run130:gpt56w history missing/duplicate k: %s" % sorted(by_k))
    producer = "unknown: run130 steps.json has no verified producer identity"
    return by_k, producer


def history_text(inventory: list[dict[str, Any]]) -> str:
    if not inventory:
        return "（还没有）"
    return "\n".join("- %s（来自：%s）" % (item["change"], item["from"]) for item in inventory)


def build_why_prompt(k: int, beads: list[dict[str, Any]], history: dict[int, list[dict[str, Any]]],
                     template: str = "") -> str:
    if not 2 <= k <= K_EXPECTED:
        raise ValueError("why k must be 2..23")
    # The only history supplied is inventory_after(k-1); later inventory is never consulted.
    prefix = "\n\n".join("第 %d 段：%s" % (bead["k"], bead["text"]) for bead in beads[:k])
    return fill_template(template, WORK=WORK_NAME, K=k, K_PREV=k - 1,
                         BEADS=prefix, HISTORY=history_text(history[k - 1]))


def parse_why(output: str) -> tuple[dict[str, Any] | None, str | None]:
    ok, obj, error = extract_json_object(output)
    if not ok or not isinstance(obj, dict):
        return None, error or "top level is not an object"
    if set(obj) != {"differs", "sentence"}:
        return None, "WHY_GATE_v4 fields must match the frozen schema exactly"
    differs = obj.get("differs")
    if not isinstance(differs, bool):
        return None, "differs must be boolean"
    sentence = obj.get("sentence")
    if not isinstance(sentence, str):
        return None, "sentence must be a string"
    if differs and (not sentence.strip() or sentence == "无"):
        return None, "differs=true requires an actual sentence"
    if not differs and sentence != "无":
        return None, "differs=false requires the exact frozen answer 无"
    return {"differs": differs, "sentence": sentence}, None


def build_mech_prompt(template: str, title: str, items: list[str]) -> str:
    numbered = "\n".join("%d. %s" % (i + 1, value) for i, value in enumerate(items))
    return fill_template(template, WORK=WORK_NAME, MM=title, ITEMS=numbered)


def parse_mech(output: str, n_items: int) -> tuple[list[dict[str, Any]] | None, str | None]:
    ok, values, error = extract_json_array(output)
    if not ok:
        return None, error
    if len(values) > 2:
        return None, "more than two relations"
    parsed: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        if not isinstance(value, dict) or set(value) != {"relation", "explains", "new_understanding"}:
            return None, "relation %d is not an object" % index
        relation = value.get("relation")
        understanding = value.get("new_understanding")
        explains = value.get("explains")
        if not isinstance(relation, str) or not relation.strip():
            return None, "relation %d has no text" % index
        if not isinstance(understanding, str) or not understanding.strip():
            return None, "relation %d has no new understanding" % index
        if not isinstance(explains, list):
            return None, "relation %d explains is not a list" % index
        nums: list[int] = []
        for value_no in explains:
            if type(value_no) is not int or not 1 <= value_no <= n_items:
                return None, "relation %d explains out-of-set item" % index
            if value_no in nums:
                return None, "relation %d explains contains a duplicate item" % index
            nums.append(value_no)
        if len(nums) < 2:
            return None, "relation %d must explain at least two distinct items" % index
        parsed.append({"relation": relation, "explains": nums,
                       "new_understanding": understanding})
    return parsed, None


def build_audit_prompt(template: str, title: str, items: list[str], relation: dict[str, Any]) -> str:
    item_lines = "\n".join("[%d] %s" % (i + 1, value) for i, value in enumerate(items))
    return fill_template(template, WORK=WORK_NAME, MM=title, ITEMS=item_lines,
                         RELATION=relation["relation"] + "——" + relation["new_understanding"],
                         EXPLAINS="、".join(str(v) for v in relation["explains"]))


def parse_audit(output: str) -> tuple[dict[str, Any] | None, str | None]:
    ok, obj, error = extract_json_object(output)
    if not ok or not isinstance(obj, dict):
        return None, error or "top level is not an object"
    if set(obj) != {"class", "why"}:
        return None, "audit fields must match the frozen schema exactly"
    verdict = obj.get("class")
    why = obj.get("why")
    if verdict not in AUDIT_CLASSES or not isinstance(why, str) or not why.strip():
        return None, "audit class/why schema invalid"
    return {"class": verdict, "why": why}, None


def build_candidates(beads: list[dict[str, Any]], why_records: list[dict[str, Any]],
                     mech_records: list[dict[str, Any]]) -> tuple[dict[int, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    why_by_k = {record["k"]: record for record in why_records}
    mech_by_k = {record["k"]: record for record in mech_records}
    candidates: dict[int, list[dict[str, Any]]] = {}
    registry: dict[str, dict[str, Any]] = {}
    for bead in beads:
        k = bead["k"]
        items = [{"uid": "k%02d_hd" % k, "kind": "认", "text": bead["title"], "meta": {}}]
        items.extend({"uid": "k%02d_now%02d" % (k, i), "kind": "此刻", "text": text,
                      "meta": {"item_no": i}} for i, text in enumerate(now_items(bead), 1))
        why = why_by_k.get(k)
        if why and why["differs"] and why["sentence"] != "无":
            items.append({"uid": "k%02d_why" % k, "kind": "因为前面", "text": why["sentence"], "meta": {}})
        mech = mech_by_k.get(k, {})
        for i, relation in enumerate(mech.get("relations", [])):
            if relation.get("survives"):
                items.append({"uid": "k%02d_mech%d" % (k, i), "kind": "更深",
                              "text": relation["relation"],
                              "meta": {"new_understanding": relation["new_understanding"],
                                       "explains": relation["explains"],
                                       "verdicts": relation["verdicts"],
                                       "audit_why": relation["audit_why"]}})
        for number, item in enumerate(items, 1):
            item["k"] = k
            item["id"] = number
            registry[item["uid"]] = item
        candidates[k] = items
    return candidates, registry


def tagged(item: Mapping[str, Any]) -> str:
    return "[%s] %s" % (item["kind"], item["text"])


def build_surface_prompt(template: str, title: str, screen_items: list[dict[str, Any]],
                         candidates: list[dict[str, Any]]) -> str:
    screen = "（空）" if not screen_items else "\n".join(
        "S%d. %s" % (i + 1, tagged(item)) for i, item in enumerate(screen_items))
    items = "\n".join("%d. %s" % (item["id"], tagged(item)) for item in candidates)
    return fill_template(template, WORK=WORK_NAME, MM=title, SCREEN=screen, ITEMS=items)


def _id_list(value: Any, max_value: int, screen_ids: bool = False) -> list[int]:
    if not isinstance(value, list):
        raise ValueError("id field is not a list")
    result: list[int] = []
    for raw in value:
        match = re.fullmatch(r"[Ss]\s*(\d+)" if screen_ids else r"(\d+)", str(raw).strip())
        if not match:
            raise ValueError("bad id %r" % raw)
        number = int(match.group(1))
        if not 1 <= number <= max_value:
            raise ValueError("id out of range")
        if number in result:
            raise ValueError("duplicate id")
        result.append(number)
    return result


def parse_surface(output: str, n_screen: int, n_items: int) -> tuple[dict[str, Any] | None, str | None]:
    ok, obj, error = extract_json_object(output)
    if not ok or not isinstance(obj, dict):
        return None, error or "top level is not an object"
    if set(obj) != {"action", "keep", "show", "expand", "recap", "why"}:
        return None, "surface fields must match the frozen schema exactly"
    action = obj.get("action")
    if action not in ACTIONS:
        return None, "unknown action"
    try:
        keep = _id_list(obj.get("keep"), n_screen, screen_ids=True)
        show = _id_list(obj.get("show"), n_items)
        expand = _id_list(obj.get("expand"), n_items)
        recap = _id_list(obj.get("recap"), n_items)
    except ValueError as exc:
        return None, "ids: " + str(exc)
    if set(show) & set(expand) or set(show) & set(recap) or set(expand) & set(recap):
        return None, "show/expand/recap must be disjoint"
    why = obj.get("why")
    if not isinstance(why, str) or not why.strip():
        return None, "surface why is empty"
    if action == "保持" and (keep != list(range(1, n_screen + 1)) or show):
        return None, "保持 must retain the full current screen and show nothing"
    if action == "补充" and (not show or keep != list(range(1, n_screen + 1))):
        return None, "补充 must add content and retain the current screen"
    if action == "更新" and not show:
        return None, "更新 must show new content"
    if action == "沉默" and (keep or show):
        return None, "沉默 must clear the screen"
    return {"action": action, "keep": keep, "show": show, "expand": expand,
            "recap": recap, "why": why}, None


def parse_compare(output: str, mapping: dict[str, str], candidate_texts: dict[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    ok, obj, error = extract_json_object(output)
    if not ok or not isinstance(obj, dict):
        return None, error or "top level is not an object"
    if set(obj) != {"ranking", "best_moments", "worst_moments", "hindsight", "only_here", "why"}:
        return None, "compare fields must match the frozen schema exactly"
    if (not isinstance(mapping, dict) or set(mapping) != set(POSITIONS) or
            any(not isinstance(value, str) for value in mapping.values()) or
            len(set(mapping.values())) != 3 or set(mapping.values()) != {"a", "b", "c"} or
            not isinstance(candidate_texts, dict) or set(candidate_texts) != {"a", "b", "c"} or
            any(not isinstance(text, str) for text in candidate_texts.values())):
        return None, "candidate mapping/text set must be an exact a/b/c bijection"
    ranking = obj.get("ranking")
    if (not isinstance(ranking, list) or len(ranking) != 3 or
            any(not isinstance(position, str) for position in ranking)):
        return None, "ranking must contain each of 甲乙丙 exactly once"
    if len(set(ranking)) != 3 or set(ranking) != set(POSITIONS):
        return None, "ranking has duplicates"
    normalized: dict[str, dict[str, Any]] = {}
    for field in ("best_moments", "worst_moments", "hindsight", "only_here"):
        value = obj.get(field)
        if not isinstance(value, dict) or set(value) != set(POSITIONS):
            return None, field + " must have exactly 甲乙丙 keys"
        normalized[field] = value
    for field in ("best_moments", "worst_moments"):
        for position in POSITIONS:
            value = normalized[field][position]
            if not isinstance(value, str) or not value.strip():
                return None, "%s[%s] is empty" % (field, position)
            quotes = re.findall(r"“([^”]+)”|\"([^\"]+)\"|「([^」]+)」|『([^』]+)』", value)
            snippets = [part for group in quotes for part in group if part]
            target = candidate_texts[mapping[position]]
            if not snippets or any(snippet not in target for snippet in snippets):
                return None, "%s[%s] quote missing or unsupported by its mapped candidate" % (field, position)
    for position in POSITIONS:
        only = normalized["only_here"][position]
        hindsight = normalized["hindsight"][position]
        if not isinstance(only, str) or not only.strip() or not isinstance(hindsight, list):
            return None, "only_here/hindsight schema invalid at " + position
        if any(not isinstance(value, str) for value in hindsight):
            return None, "hindsight entries must be strings"
        target = candidate_texts[mapping[position]]
        for quote in hindsight:
            if not quote.strip() or quote not in target:
                return None, "hindsight quote is empty or unsupported by its mapped candidate"
        only_quotes = re.findall(r"“([^”]+)”|\"([^\"]+)\"|「([^」]+)」|『([^』]+)』", only)
        only_snippets = [part for group in only_quotes for part in group if part]
        if not only_snippets or any(snippet not in target for snippet in only_snippets):
            return None, "only_here quote is missing or unsupported by its mapped candidate"
    why = obj.get("why")
    if not isinstance(why, str) or not why.strip():
        return None, "compare why is empty"
    why_quotes = [part for group in re.findall(
        r"“([^”]+)”|\"([^\"]+)\"|「([^」]+)」|『([^』]+)』", why) for part in group if part]
    if not why_quotes or any(not any(quote in candidate_texts[candidate] for candidate in ("a", "b", "c"))
                             for quote in why_quotes):
        return None, "compare why quote is missing or unsupported by every candidate"
    return {"ranking": ranking, "best_moments": normalized["best_moments"],
            "worst_moments": normalized["worst_moments"], "hindsight": normalized["hindsight"],
            "only_here": normalized["only_here"], "why": why}, None


def _read_bytes(root: Path, relative: str) -> bytes:
    path = root / relative
    if not path.is_file():
        raise IntegrityError("missing frozen input: " + relative)
    return path.read_bytes()


def _strip_recorded_heading(text: str, exact_heading: str | None) -> str:
    lines = text.splitlines()
    if exact_heading is not None and lines and lines[0] == exact_heading:
        return "\n".join(lines[1:]).strip()
    return text.strip()


def _reader_view(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    previous: list[str] = []
    view: list[dict[str, Any]] = []
    for step in steps:
        current = step["screen"]
        new = [text for text in current if text not in previous]
        gone = [text for text in previous if text not in current]
        status = "new" if new else ("unchanged" if not gone else ("removed_only" if current else "cleared"))
        view.append({"time": step["time"], "new": new, "status": status,
                     "n_screen": len(current), "screen_chars": sum(map(len, current))})
        previous = current
    return view


def _reader_timeline(view: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for step in view:
        lines.extend(["### " + step["time"], ""])
        if step["status"] == "new":
            lines.extend("- " + text for text in step["new"])
        elif step["status"] == "unchanged":
            lines.append("（屏幕不变）")
        elif step["status"] == "removed_only":
            lines.append("（无新内容；部分旧内容撤下）")
        else:
            lines.append("（屏幕为空）")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _extract_run124_screens(text: str) -> list[dict[str, Any]]:
    sections = list(re.finditer(r"^## 第\s*(\d+)\s*站\s*(.*)$", text, re.M))
    steps: list[dict[str, Any]] = []
    for index, match in enumerate(sections):
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        body = text[match.end():end]
        next_section = re.search(r"^## ", body, re.M)
        if next_section:
            body = body[:next_section.start()]
        screen: list[str] = []
        in_screen = False
        for line in body.splitlines():
            if line.startswith("- 屏幕"):
                in_screen = True
                continue
            if in_screen:
                if line.startswith("  - "):
                    # [kind] is a recorded structural tag in run124, not prose.
                    screen.append(re.sub(r"^\[[^\]\n]{1,8}\]\s*", "", line[4:].strip()))
                elif line.strip():
                    in_screen = False
        time_label = re.sub(r"^\d+\.\s*", "", match.group(2).strip())
        steps.append({"time": time_label, "screen": screen})
    if not steps or not any(step["screen"] for step in steps):
        raise IntegrityError("run124 B screen structure not found")
    return steps


def _assert_anonymous_payload(text: str, label: str) -> None:
    match = IDENTITY_LEAK_RE.search(text)
    if match:
        line_no = text[:match.start()].count("\n") + 1
        raise IntegrityError("identity marker in substantive blind payload %s at line %d; text was not stripped" %
                             (label, line_no))


def _freeze_inputs(source_root: Path) -> dict[str, Any]:
    raw_sources: dict[str, bytes] = {name: _read_bytes(source_root, path) for name, path in INPUT_PATHS.items()}
    raw_templates = {name: _read_bytes(source_root, path) for name, path in TEMPLATE_PATHS.items()}
    driver_bytes = (THIS_DIR / "go.py").read_bytes()
    beads = split_beads(raw_sources["beads"].decode("utf-8"))
    history_rows, history_producer = _load_history(source_root)
    baselines: dict[str, dict[str, Any]] = {}
    for set_name in sorted(BASELINE_MODELS):
        meta = strict_json_loads(raw_sources[set_name + "_meta"].decode("utf-8"))
        if not isinstance(meta, dict):
            raise IntegrityError("run132 baseline metadata must be a JSON object")
        expected_key = BASELINE_MODELS[set_name]
        if meta.get("model_key") != expected_key or meta.get("status") != "ok":
            raise IntegrityError("run132 baseline source meta mismatch for " + set_name)
        baselines[set_name] = {
            "text": raw_sources[set_name].decode("utf-8"),
            "source": INPUT_PATHS[set_name],
            "source_sha256": sha256_bytes(raw_sources[set_name]),
            "source_meta": INPUT_PATHS[set_name + "_meta"],
            "source_meta_sha256": sha256_bytes(raw_sources[set_name + "_meta"]),
            "generator_model_key": meta["model_key"],
            "generator_actual_identity": "unverified: run132 bundle has no terminal identity artifact",
            "source_job_id": meta.get("job_id"),
        }
    run124_text = raw_sources["run124_b"].decode("utf-8")
    b_steps = _extract_run124_screens(run124_text)
    b_view = _reader_view(b_steps)
    b_reading = "# 边听边读（run124 B 屏幕视图）\n\n" + _reader_timeline(b_view)
    # The source filename records the gpt56w lineage; no terminal identity is available in this render artifact.
    b_lineage = {
        "source": INPUT_PATHS["run124_b"],
        "source_sha256": sha256_bytes(raw_sources["run124_b"]),
        "generator_model_key": "gpt56w (recorded lineage label)",
        "generator_actual_identity": "unverified: reader render has no terminal identity artifact",
        "chooser_actual_identity": "unverified: reader render has no chooser terminal artifact",
    }
    source_lock = {INPUT_PATHS[key]: sha256_bytes(value) for key, value in raw_sources.items()}
    template_lock = {TEMPLATE_PATHS[key]: sha256_bytes(value) for key, value in raw_templates.items()}
    lock = {
        "run_id": RUN_ID,
        "schema": "run144-freeze-v1",
        "config": {key: list(value) if isinstance(value, tuple) else value for key, value in CFG.items()},
        "work_key": WORK_KEY,
        "bead_k": list(range(1, K_EXPECTED + 1)),
        "why_k": list(range(2, K_EXPECTED + 1)),
        "source_sha256": source_lock,
        "template_sha256": template_lock,
        "driver_sha256": sha256_bytes(driver_bytes),
        "history_producer": history_producer,
        "history_source": CFG["history"],
        "baseline_lineage": {name: {key: value for key, value in item.items() if key != "text"}
                             for name, item in baselines.items()},
        "run124_lineage": b_lineage,
        "scope": "diagnostic only; no production or fair-model claim",
    }
    return {"lock": lock, "beads": beads, "history": history_rows,
            "history_producer": history_producer, "templates": {
                name: value.decode("utf-8") for name, value in raw_templates.items()},
            "baselines": baselines, "run124_steps": b_steps, "run124_reading": b_reading,
            "run124_lineage": b_lineage}


def canonical_model(model: str) -> str:
    key = str(model or "").strip().lower()
    return {"gflash_web": "gflash", "gpro_web": "gpro"}.get(key, key)


def canonical_muse_identity(provider: str, model: str) -> dict[str, str]:
    """The only alias boundary for the historical generic Muse label."""
    provider_aliases = {"muse": "claude-proxy", "external muse": "claude-proxy",
                        "claude-proxy": "claude-proxy"}
    model_aliases = {"muse": "muse-spark-1.3-contributor-free",
                     "external muse": "muse-spark-1.3-contributor-free",
                     "muse-spark-1.3-contributor-free": "muse-spark-1.3-contributor-free"}
    canonical_provider = provider_aliases.get(str(provider).strip().lower())
    canonical_model_name = model_aliases.get(str(model).strip().lower())
    if canonical_provider is None or canonical_model_name is None:
        raise IntegrityError("Muse identity alias is unknown; expected canonical claude-proxy target")
    return {"provider": canonical_provider, "model": canonical_model_name,
            "transport": MUSE_TRANSPORT, "target": MUSE_TARGET}


def candidate_generators(set_name: str) -> dict[str, list[str]]:
    return {"a": [CFG["gen"], CFG["chooser"]], "b": ["gpt56w"],
            "c": [BASELINE_MODELS.get(set_name, "unknown")]}


def self_flag(set_name: str, judge: str) -> str:
    canonical_judge = canonical_model(judge)
    hits = [candidate for candidate, models in candidate_generators(set_name).items()
            if canonical_judge in {canonical_model(model) for model in models}]
    return ",".join(hits) if hits else "否"


def _expected_compare_mapping() -> dict[tuple[str, str, int], dict[str, str]]:
    result: dict[tuple[str, str, int], dict[str, str]] = {}
    for set_index, set_name in enumerate(sorted(BASELINE_MODELS)):
        seed = SEED_COMPARE + 100 * set_index
        base = ["a", "b", "c"]
        random.Random(seed).shuffle(base)
        for judge in CFG["judges"]:
            for order_index in range(3):
                order = base[order_index:] + base[:order_index]
                result[(set_name, judge, order_index)] = dict(zip(POSITIONS, order))
    return result


class Pipeline:
    """Sequential pipeline. Every model-facing submission is injected and artifact-verified."""

    def __init__(self, out_dir: Path, caller: Callable[[dict[str, Any]], Any],
                 source_root: Path = ROOT,
                 transport_proof_verifier: Callable[[Any, Mapping[str, Any]], Any] | None = None) -> None:
        self.out_dir = Path(out_dir).resolve()
        self.source_root = Path(source_root).resolve()
        self.caller = caller
        self.namespace = MOCK_NAMESPACE
        self.transport = "MOCK"
        self.data: dict[str, Any] | None = None
        self.calls: list[dict[str, Any]] = []
        self.transport_attempts: list[dict[str, Any]] = []
        self.transport_proof_verifier = transport_proof_verifier
        self.new_submissions = 0

    def _relative_output(self, path: Path) -> str:
        resolved = path.resolve()
        try:
            return resolved.relative_to(self.out_dir).as_posix()
        except ValueError as exc:
            raise IntegrityError("caller artifact escaped the output directory") from exc

    def _output_path(self, relative: str) -> Path:
        path = (self.out_dir / relative).resolve()
        try:
            path.relative_to(self.out_dir)
        except ValueError as exc:
            raise IntegrityError("output artifact path escaped the run directory") from exc
        return path

    def _all_files(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for path in sorted(self.out_dir.rglob("*")):
            if path.is_file():
                rel = path.relative_to(self.out_dir).as_posix()
                result[rel] = sha256_bytes(path.read_bytes())
        return result

    def _verify_output_lock(self) -> None:
        manifest_path = self.out_dir / "run_manifest.json"
        if not manifest_path.exists():
            return
        manifest = read_json(manifest_path)
        expected = manifest.get("outputs")
        if not isinstance(expected, dict):
            raise IntegrityError("existing run manifest has no output hash map")
        actual = self._all_files()
        actual.pop("run_manifest.json", None)
        if actual != expected:
            changed = sorted(set(actual) ^ set(expected))
            changed += sorted(key for key in set(actual) & set(expected) if actual[key] != expected[key])
            raise IntegrityError("existing output/pack/artifact tamper: " + ", ".join(changed[:12]))
        if any(path.name == "DONE" for path in self.out_dir.rglob("DONE")):
            raise IntegrityError("run144 never accepts a DONE marker")

    def _load_calls(self) -> None:
        path = self.out_dir / "call_index.json"
        if not path.exists():
            self.calls = []
            return
        data = read_json(path)
        records = data.get("records") if isinstance(data, dict) else None
        if not isinstance(records, list):
            raise IntegrityError("call_index records missing")
        seen: set[tuple[str, int]] = set()
        self.calls = []
        for record in records:
            pair = (record.get("logical_id"), record.get("attempt"))
            if not isinstance(pair[0], str) or type(pair[1]) is not int or pair in seen:
                raise IntegrityError("duplicate or malformed call identity")
            seen.add(pair)
            self._verify_artifact(record, expected_prompt=None)
            self.calls.append(record)
        transport_attempts = data.get("transport_attempts", [])
        if not isinstance(transport_attempts, list):
            raise IntegrityError("transport_attempts index must be a list")
        self.transport_attempts = []
        for attempt in transport_attempts:
            if not isinstance(attempt, dict) or not isinstance(attempt.get("logical_id"), str):
                raise IntegrityError("malformed immutable transport attempt index")
            paths = attempt.get("paths")
            if not isinstance(paths, dict) or set(paths) != {"request", "proof", "error", "raw_output", "terminal"}:
                raise IntegrityError("transport attempt artifact map is incomplete")
            for name, relative in paths.items():
                artifact_path = self._output_path(relative)
                if not artifact_path.is_file() or sha256_bytes(artifact_path.read_bytes()) != attempt["sha256"][name]:
                    raise IntegrityError("immutable transport attempt artifact changed: " + name)
            self.transport_attempts.append(attempt)

    def _save_calls(self) -> None:
        write_json(self.out_dir / "call_index.json", {
            "run_id": RUN_ID, "namespace": self.namespace,
            "records": self.calls,
            "transport_attempts": self.transport_attempts,
            "new_mock_submissions_this_invocation": self.new_submissions,
        })

    def _paths_for(self, logical_id: str, attempt: int) -> dict[str, str]:
        key_hash = sha256_text(logical_id)[:20]
        directory = self.out_dir / "evidence" / key_hash / ("attempt-%03d" % attempt)
        return {name: self._relative_output(directory / filename) for name, filename in {
            "meta": "meta.json", "prompt": "prompt.txt", "output": "output.txt", "terminal": "terminal.json"}.items()}

    def _verify_artifact(self, record: dict[str, Any], expected_prompt: str | None) -> tuple[dict[str, Any], str, dict[str, Any]]:
        identity = record.get("identity")
        paths = record.get("paths")
        if not isinstance(identity, dict) or not isinstance(paths, dict) or set(paths) != {"meta", "prompt", "output", "terminal"}:
            raise IntegrityError("call record lacks exact artifact identity/paths")
        if paths != self._paths_for(record.get("logical_id"), record.get("attempt")):
            raise IntegrityError("caller artifact path is not the exact immutable attempt path")
        if identity.get("run_id") != RUN_ID or identity.get("namespace") != self.namespace:
            raise IntegrityError("call namespace/run identity mismatch")
        request_identity = record.get("request_identity")
        if not isinstance(request_identity, dict):
            raise IntegrityError("indexed caller record omitted the complete request identity")
        expected_identity = {**request_identity, "attempt": record.get("attempt"),
                             "sampling_identity": record.get("sampling_identity"),
                             "actual_model": record.get("requested_model"), "transport": "MOCK"}
        if identity != expected_identity:
            raise IntegrityError("indexed caller identity fields are incomplete or inconsistent")
        meta_path, prompt_path = self._output_path(paths["meta"]), self._output_path(paths["prompt"])
        output_path, terminal_path = self._output_path(paths["output"]), self._output_path(paths["terminal"])
        if not all(path.is_file() for path in (meta_path, prompt_path, output_path, terminal_path)):
            raise IntegrityError("exact meta/prompt/output/terminal artifact missing")
        prompt_bytes, output_bytes = prompt_path.read_bytes(), output_path.read_bytes()
        meta, terminal = read_json(meta_path), read_json(terminal_path)
        if not isinstance(meta, dict) or not isinstance(terminal, dict):
            raise IntegrityError("meta/terminal artifact is not an object")
        expected_meta_keys = {"schema", "identity", "run_id", "namespace", "logical_id", "attempt",
                              "step", "key", "requested_model", "actual_model", "prompt_version",
                              "driver_sha256", "prompt_sha256", "output_sha256", "sampling_identity",
                              "new_sample_reason", "terminal_sha256", "transport", "request_identity"}
        expected_terminal_keys = {"schema", "identity", "run_id", "namespace", "actual_model",
                                  "transport", "terminal_id", "status", "exit_code", "identity_verified"}
        if set(meta) != expected_meta_keys or set(terminal) != expected_terminal_keys:
            raise IntegrityError("meta/terminal fields must match the exact artifact schema")
        prompt = prompt_bytes.decode("utf-8")
        output = output_bytes.decode("utf-8")
        if prompt != request_identity.get("prompt_utf8"):
            raise IntegrityError("exact stored prompt bytes differ from the complete indexed request identity")
        if expected_prompt is not None and prompt != expected_prompt:
            raise IntegrityError("exact prompt bytes differ from recomputed prompt")
        if meta.get("schema") != ARTIFACT_SCHEMA or terminal.get("schema") != ARTIFACT_SCHEMA:
            raise IntegrityError("unknown exact artifact schema")
        if meta.get("identity") != identity or terminal.get("identity") != identity:
            raise IntegrityError("meta/terminal identity does not match indexed identity")
        expected_fields = {"run_id": RUN_ID, "namespace": self.namespace,
                           "logical_id": record.get("logical_id"), "attempt": record.get("attempt"),
                           "step": record.get("step"), "key": record.get("key"),
                           "requested_model": record.get("requested_model"),
                           "actual_model": record.get("requested_model"),
                           "prompt_version": record.get("prompt_version"),
                           "driver_sha256": record.get("driver_sha256"),
                           "prompt_sha256": record.get("prompt_sha256"),
                           "sampling_identity": record.get("sampling_identity"),
                           "new_sample_reason": record.get("new_sample_reason"),
                           "transport": "MOCK", "request_identity": request_identity}
        for field, value in expected_fields.items():
            if meta.get(field) != value:
                raise IntegrityError("caller meta identity mismatch: " + field)
        if meta.get("output_sha256") != sha256_bytes(output_bytes):
            raise IntegrityError("output SHA mismatch")
        if meta.get("terminal_sha256") != sha256_bytes(terminal_path.read_bytes()):
            raise IntegrityError("terminal SHA mismatch")
        if meta.get("prompt_sha256") != sha256_bytes(prompt_bytes):
            raise IntegrityError("prompt SHA mismatch")
        if terminal.get("status") not in ("completed", "queue_stop"):
            raise IntegrityError("terminal status is missing/invalid")
        exit_code = terminal.get("exit_code")
        if (terminal.get("status") != "queue_stop" and
                not (exit_code is None or (type(exit_code) is int and exit_code == 0))):
            raise IntegrityError("terminal exit code indicates failed transport")
        if not isinstance(terminal.get("terminal_id"), str) or not terminal["terminal_id"]:
            raise IntegrityError("terminal identity is missing")
        if terminal.get("transport") != "MOCK" or terminal.get("actual_model") != record.get("requested_model"):
            raise IntegrityError("terminal actual model/transport identity mismatch")
        if terminal.get("namespace") != self.namespace or terminal.get("run_id") != RUN_ID:
            raise IntegrityError("terminal run/namespace mismatch")
        if terminal.get("identity_verified") is not True:
            raise IntegrityError("terminal identity was not verified")
        return meta, output, terminal

    def _request_identity(self, logical_id: str, step: str, key: list[Any], model: str,
                          prompt_version: str, prompt: str) -> dict[str, Any]:
        if self.data is None:
            raise IntegrityError("frozen input identity must be loaded before submission")
        lock = self.data["lock"]
        producer = {"history_producer": lock["history_producer"],
                    "source_sha256": lock["source_sha256"],
                    "template_sha256": lock["template_sha256"],
                    "driver_sha256": lock["driver_sha256"]}
        return {"run_id": RUN_ID, "namespace": self.namespace, "request_id": logical_id,
                "logical_id": logical_id, "step": step, "key": list(key),
                "requested_model": model, "current_model": model,
                "prompt_version": prompt_version, "driver_sha256": lock["driver_sha256"],
                "input_producer": producer, "prompt_utf8": prompt,
                "prompt_sha256": sha256_text(prompt)}

    def _make_record(self, *, request_identity: dict[str, Any], attempt: int,
                     new_sample_reason: str | None = None) -> dict[str, Any]:
        logical_id = request_identity["logical_id"]
        model = request_identity["requested_model"]
        sampling_identity = sha256_text(json.dumps(
            {"request_identity": request_identity, "sample_attempt": attempt},
            ensure_ascii=False, sort_keys=True, separators=(",", ":")))
        identity = {**request_identity, "attempt": attempt,
                    "actual_model": model, "transport": self.transport,
                    "sampling_identity": sampling_identity}
        return {"logical_id": logical_id, "step": request_identity["step"],
                "key": request_identity["key"], "requested_model": model,
                "prompt_version": request_identity["prompt_version"],
                "attempt": attempt, "identity": identity,
                "request_identity": request_identity,
                "sampling_identity": sampling_identity,
                "new_sample_reason": new_sample_reason,
                "new_sample_taken": attempt > 0,
                "driver_sha256": request_identity["driver_sha256"],
                "prompt_sha256": request_identity["prompt_sha256"],
                "parse_status": "not_parsed", "parse_error": None,
                "paths": self._paths_for(logical_id, attempt)}

    def _persist_transport_attempt(self, record: Mapping[str, Any], transport_index: int,
                                   exc: BaseException, phase: str, proof_receipt: Any,
                                   approved: bool) -> dict[str, Any]:
        logical_id = str(record["logical_id"])
        key_hash = sha256_text(logical_id)[:20]
        folder = self.out_dir / "evidence" / key_hash / ("transport-%03d" % transport_index)
        paths = {name: self._relative_output(folder / filename) for name, filename in {
            "request": "request.json", "proof": "proof.json", "error": "error.bin",
            "raw_output": "raw_output.bin", "terminal": "terminal.json"}.items()}
        proof = getattr(exc, "proof", None)
        try:
            proof_bytes = json_bytes(proof if proof is not None else {"status": "no_proof"})
        except (TypeError, ValueError):
            proof_bytes = repr(proof).encode("utf-8", errors="backslashreplace")
        error_bytes = getattr(exc, "raw_error", b"") or str(exc).encode("utf-8", errors="backslashreplace")
        raw_output = getattr(exc, "raw_output", b"")
        if isinstance(raw_output, str):
            raw_output = raw_output.encode("utf-8")
        raw_output = bytes(raw_output)
        terminal = {"schema": ARTIFACT_SCHEMA, "logical_id": logical_id,
                    "request_identity": record["request_identity"],
                    "sampling_identity": record["sampling_identity"],
                    "transport_attempt": transport_index, "phase": phase,
                    "status": "transport_failure", "terminal_observed": False,
                    "terminal_id": None, "exception_type": type(exc).__name__,
                    "proof_verified": approved}
        files = {"request": json_bytes({"request_identity": record["request_identity"],
                                        "sampling_identity": record["sampling_identity"],
                                        "sample_attempt": record["attempt"],
                                        "transport_attempt": transport_index}),
                 "proof": proof_bytes, "error": error_bytes,
                 "raw_output": raw_output, "terminal": json_bytes(terminal)}
        for name, raw in files.items():
            path = self._output_path(paths[name])
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(raw)
        entry = {"logical_id": logical_id, "sample_attempt": record["attempt"],
                 "transport_attempt": transport_index, "phase": phase,
                 "sampling_identity": record["sampling_identity"],
                 "request_identity": record["request_identity"], "proof_verified": approved,
                 "proof_receipt": proof_receipt if approved else None, "paths": paths,
                 "sha256": {name: sha256_bytes(raw) for name, raw in files.items()}}
        self.transport_attempts.append(entry)
        self._save_calls()
        return entry

    def execute(self, step: str, key: list[Any], model: str, prompt: str, prompt_version: str,
                parser: Callable[[str], tuple[Any, str | None]], *,
                allow_new_sample_on_parse_failure: bool = False,
                max_attempts: int | None = None,
                new_sample_reason: str | None = None,
                max_transport_retries: int = 0) -> dict[str, Any]:
        if not self.calls and (self.out_dir / "call_index.json").is_file():
            self._verify_output_lock()
            self._load_calls()
        if (self.out_dir / "queue_stop.json").exists() or (self.out_dir / "execution_hold.json").exists():
            raise QueueStopped("persisted queue/transport hold blocks every following job and stage")
        if PLACEHOLDER_RE.search(prompt):
            raise IntegrityError("unfilled placeholder in final prompt")
        if type(allow_new_sample_on_parse_failure) is not bool:
            raise IntegrityError("allow_new_sample_on_parse_failure must be a strict bool")
        if type(max_transport_retries) is not int or not 0 <= max_transport_retries <= MAX_ATTEMPTS:
            raise IntegrityError("transport retry budget must be a strict int from 0 to 2")
        if allow_new_sample_on_parse_failure:
            if type(max_attempts) is not int or not 1 <= max_attempts <= MAX_ATTEMPTS:
                raise IntegrityError("explicit parse resampling requires a strict bounded sample budget")
            if not isinstance(new_sample_reason, str) or not new_sample_reason.strip():
                raise IntegrityError("explicit parse resampling requires a nonempty new_sample_reason")
            attempt_limit = max_attempts
        else:
            if max_attempts is not None or new_sample_reason is not None:
                raise IntegrityError("parse resampling options require allow_new_sample_on_parse_failure=True")
            attempt_limit = 1
        logical_id = step + ":" + sha256_text(json.dumps(key, ensure_ascii=False, sort_keys=True))[:24]
        request_identity = self._request_identity(logical_id, step, key, model, prompt_version, prompt)
        prior = sorted((record for record in self.calls if record["logical_id"] == logical_id),
                       key=lambda record: record["attempt"])
        for record in prior:
            if record.get("request_identity") != request_identity:
                raise IntegrityError("current request identity conflicts with prior slot; no fallback sample is permitted")
        next_attempt = max((record["attempt"] for record in prior), default=-1) + 1
        for record in prior:
            _, output, terminal = self._verify_artifact(record, prompt)
            if terminal["status"] == "queue_stop":
                raise QueueStopped("terminal queue_stop blocks subsequent work")
            if terminal["status"] != "completed":
                raise IntegrityError("prior caller attempt has no completed terminal")
            parsed, error = parser(output)
            if error is None and parsed is not None:
                record["parse_status"], record["parse_error"] = "ok", None
                self._save_calls()
                return {"logical_id": logical_id, "attempt": record["attempt"], "parsed": parsed,
                        "output": output, "prompt_sha256": record["prompt_sha256"],
                        "paths": record["paths"], "resumed": True}
            record["parse_status"] = "failed"
            record["parse_error"] = error or "parser rejected completed output"
            self._save_calls()
            if not allow_new_sample_on_parse_failure:
                raise StageFailed("%s completed with a persisted parse failure; default policy stops: %s" %
                                  (logical_id, record["parse_error"]))
        if next_attempt >= attempt_limit:
            raise StageFailed("%s exhausted its explicit immutable sample budget" % logical_id)
        while next_attempt < attempt_limit:
            record = self._make_record(request_identity=request_identity, attempt=next_attempt,
                                       new_sample_reason=(new_sample_reason if next_attempt > 0 else None))
            matching_transport = [item for item in self.transport_attempts
                                  if item.get("logical_id") == logical_id and
                                  item.get("sample_attempt") == next_attempt]
            used_transport_retries = sum(1 for item in matching_transport if item.get("proof_verified") is True)
            transport_index = len(matching_transport)
            request = {"schema": ARTIFACT_SCHEMA, "mode": "MOCK_ONLY_OFFLINE_TEST",
                       "identity": record["identity"], "request_identity": request_identity,
                       "step": step, "key": key, "requested_model": model,
                       "prompt_version": prompt_version, "prompt": prompt,
                       "prompt_sha256": record["prompt_sha256"],
                       "sampling_identity": record["sampling_identity"],
                       "new_sample_reason": record["new_sample_reason"],
                       "driver_sha256": record["driver_sha256"],
                       "transport_attempt_index": transport_index,
                       "paths": {name: str(self._output_path(rel)) for name, rel in record["paths"].items()},
                       "required_artifacts": ["meta", "prompt", "output", "terminal"],
                       "must_not_use_cli_network_or_model": True}
            try:
                self.caller(request)
            except Exception as exc:
                failure_id = "%s|sample:%d|transport:%d" % (logical_id, next_attempt, transport_index)
                binding = {"request_identity": request_identity,
                           "sampling_identity": record["sampling_identity"],
                           "sample_attempt": next_attempt,
                           "transport_attempt": transport_index,
                           "failure_attempt_id": failure_id,
                           "phase": getattr(exc, "phase", "unknown_submitted")}
                phase = binding["phase"]
                receipt = None
                if (isinstance(exc, TransportFailure) and phase == "pre_submit" and
                        callable(self.transport_proof_verifier)):
                    try:
                        candidate_receipt = self.transport_proof_verifier(exc.proof, binding)
                        if (isinstance(candidate_receipt, dict) and
                                candidate_receipt.get("verified") is True and
                                candidate_receipt.get("submission_state") == "not_submitted" and
                                candidate_receipt.get("proof_scope") == "sourcebound_pre_submit_v1" and
                                candidate_receipt.get("binding") == binding):
                            receipt = candidate_receipt
                    except Exception:
                        receipt = None
                approved = (receipt is not None and
                            transport_retry_allowed(phase=phase, proof=exc.proof,
                                                    verifier=lambda _proof, _binding: receipt,
                                                    expected_binding=binding,
                                                    retries_remaining=max_transport_retries-used_transport_retries))
                self._persist_transport_attempt(record, transport_index, exc, phase, receipt, approved)
                if approved and used_transport_retries < max_transport_retries:
                    continue
                hold = {"run_id": RUN_ID, "logical_id": logical_id,
                        "phase": phase, "reason": "transport outcome is not retryable or retry budget is exhausted",
                        "request_identity": request_identity,
                        "transport_attempt": transport_index}
                write_json(self.out_dir / "execution_hold.json", hold)
                raise QueueStopped("transport failure is held; no later job/stage may proceed") from exc
            self.calls.append(record)
            self.new_submissions += 1
            self._save_calls()
            _, output, terminal = self._verify_artifact(record, prompt)
            if terminal["status"] == "queue_stop":
                write_json(self.out_dir / "queue_stop.json", {
                    "run_id": RUN_ID, "step": step, "logical_id": logical_id,
                    "attempt": next_attempt, "reason": "caller exact terminal status queue_stop"})
                raise QueueStopped("queue_stop at %s; subsequent job/stage submission prohibited" % logical_id)
            if terminal["status"] != "completed":
                raise IntegrityError("caller terminal is incomplete")
            parsed, error = parser(output)
            if error is None and parsed is not None:
                record["parse_status"], record["parse_error"] = "ok", None
                self._save_calls()
                return {"logical_id": logical_id, "attempt": next_attempt, "parsed": parsed,
                        "output": output, "prompt_sha256": record["prompt_sha256"],
                        "paths": record["paths"], "resumed": False}
            record["parse_status"] = "failed"
            record["parse_error"] = error or "parser rejected completed output"
            self._save_calls()
            if not allow_new_sample_on_parse_failure:
                raise StageFailed("%s completed with a persisted parse failure; default policy stops: %s" %
                                  (logical_id, record["parse_error"]))
            next_attempt += 1
        raise StageFailed("%s exhausted its explicit immutable sample budget" % logical_id)

    def _stage_why(self) -> list[dict[str, Any]]:
        data = self.data
        records = []
        template = data["templates"]["WHY_GATE_v4"]
        for k in range(2, K_EXPECTED + 1):
            prompt = build_why_prompt(k, data["beads"], data["history"], template)
            result = self.execute("why", [CFG["history"], k], CFG["gen"], prompt, "WHY_GATE_v4", parse_why)
            parsed = result["parsed"]
            records.append({"k": k, "title": data["beads"][k - 1]["title"], "model": CFG["gen"],
                            "actual_gen": CFG["gen"], "history_n": len(data["history"][k - 1]),
                            "history_prefix_k": k - 1, "differs": parsed["differs"],
                            "sentence": parsed["sentence"], "parse_ok": True,
                            "prompt_sha256": result["prompt_sha256"], "attempt": result["attempt"],
                            "evidence": result["paths"]})
        if [record["k"] for record in records] != list(range(2, K_EXPECTED + 1)):
            raise IntegrityError("why collection k2..23 mismatch")
        write_json(self.out_dir / "why.json", {"run_id": RUN_ID, "history_source": CFG["history"],
                                                "history_producer": data["history_producer"],
                                                "gen_model_key": CFG["gen"], "records": records})
        return records

    def _stage_mech(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        data = self.data
        generated: list[dict[str, Any]] = []
        for bead in data["beads"]:
            items = now_items(bead)
            prompt = build_mech_prompt(data["templates"]["MECH_v1"], bead["title"], items)
            parser = lambda output, n=len(items): parse_mech(output, n)
            result = self.execute("mech", [bead["k"]], CFG["gen"], prompt, "MECH_v1", parser)
            relations = [dict(relation=value["relation"], explains=value["explains"],
                              new_understanding=value["new_understanding"]) for value in result["parsed"]]
            generated.append({"k": bead["k"], "title": bead["title"], "n_items": len(items),
                              "actual_gen": CFG["gen"], "relations": relations,
                              "prompt_sha256": result["prompt_sha256"], "attempt": result["attempt"],
                              "evidence": result["paths"]})
        if [record["k"] for record in generated] != list(range(1, K_EXPECTED + 1)):
            raise IntegrityError("mech collection k1..23 mismatch")
        audit_tasks = [(record["k"], relation_index, reviewer, relation)
                       for record in generated
                       for relation_index, relation in enumerate(record["relations"])
                       for reviewer in CFG["auditors"]]
        audits: list[dict[str, Any]] = []
        for k, relation_index, reviewer, relation in audit_tasks:
            bead = data["beads"][k - 1]
            prompt = build_audit_prompt(data["templates"]["MECH_AUDIT_v0"], bead["title"],
                                        now_items(bead), relation)
            result = self.execute("audit", [k, relation_index, reviewer], reviewer, prompt,
                                  "MECH_AUDIT_v0", parse_audit)
            audits.append({"k": k, "relation_index": relation_index, "reviewer": reviewer,
                           "actual_reviewer": reviewer, "class": result["parsed"]["class"],
                           "why": result["parsed"]["why"], "prompt_sha256": result["prompt_sha256"],
                           "attempt": result["attempt"], "evidence": result["paths"]})
        expected_audits = {(record["k"], index, reviewer)
                           for record in generated for index, _ in enumerate(record["relations"])
                           for reviewer in CFG["auditors"]}
        actual_audits = [(audit["k"], audit["relation_index"], audit["reviewer"]) for audit in audits]
        if len(actual_audits) != len(set(actual_audits)) or set(actual_audits) != expected_audits:
            raise IntegrityError("audit relation×reviewer identity set mismatch")
        by_relation: dict[tuple[int, int], list[dict[str, Any]]] = {}
        for audit in audits:
            by_relation.setdefault((audit["k"], audit["relation_index"]), []).append(audit)
        for record in generated:
            for index, relation in enumerate(record["relations"]):
                rows = by_relation[(record["k"], index)]
                if {row["reviewer"] for row in rows} != set(CFG["auditors"]):
                    raise IntegrityError("missing reviewer for generated relation")
                relation["verdicts"] = {row["reviewer"]: row["class"] for row in rows}
                relation["audit_why"] = {row["reviewer"]: row["why"] for row in rows}
                relation["survives"] = not any(row["class"] in AUDIT_DROP for row in rows)
                relation["drop_reason"] = ("dropped by " + ",".join(row["reviewer"] for row in rows
                                             if row["class"] in AUDIT_DROP)) if not relation["survives"] else None
        write_json(self.out_dir / "mech.json", {"run_id": RUN_ID, "gen_model_key": CFG["gen"],
                                                 "auditors": list(CFG["auditors"]),
                                                 "records": generated, "audits": audits})
        return generated, audits

    def _stage_surface(self, why_records: list[dict[str, Any]], mech_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        data = self.data
        candidates, registry = build_candidates(data["beads"], why_records, mech_records)
        screen: list[str] = []
        records: list[dict[str, Any]] = []
        for bead in data["beads"]:
            k = bead["k"]
            previous_screen = list(screen)
            screen_items = [registry[uid] for uid in previous_screen]
            current = candidates[k]
            prompt = build_surface_prompt(data["templates"]["E7_SURFACE_v0"], bead["title"],
                                          screen_items, current)
            parser = lambda output, ns=len(screen_items), ni=len(current): parse_surface(output, ns, ni)
            result = self.execute("surface", [CFG["chooser"], k], CFG["chooser"], prompt,
                                  "E7_SURFACE_v0", parser)
            parsed = result["parsed"]
            keep = [previous_screen[index - 1] for index in parsed["keep"]]
            show = [current[index - 1]["uid"] for index in parsed["show"]]
            expand = [current[index - 1]["uid"] for index in parsed["expand"]]
            recap = [current[index - 1]["uid"] for index in parsed["recap"]]
            retired = [uid for uid in previous_screen if uid not in keep]
            screen = keep + [uid for uid in show if uid not in keep]
            records.append({"k": k, "title": bead["title"], "time": time_of(bead["title"]),
                            "chooser": CFG["chooser"], "actual_chooser": CFG["chooser"],
                            "screen_before": previous_screen,
                            "candidates": [item["uid"] for item in current],
                            "action": parsed["action"], "keep": keep, "show": show, "retired": retired,
                            "screen_after": list(screen), "expand": expand, "recap": recap,
                            "why": parsed["why"], "parse_ok": True,
                            "prompt_sha256": result["prompt_sha256"], "attempt": result["attempt"],
                            "evidence": result["paths"]})
        if [record["k"] for record in records] != list(range(1, K_EXPECTED + 1)):
            raise IntegrityError("surface collection k1..23 mismatch")
        write_json(self.out_dir / "surface.json", {"run_id": RUN_ID, "chooser_model_key": CFG["chooser"],
                                                    "items": registry, "records": records})
        return records

    def _stage_render(self, surface_records: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, str]]:
        registry = read_json(self.out_dir / "surface.json")["items"]
        internal: list[str] = ["# run144 内部决策稿（诊断用途；不进 production）", ""]
        for record in surface_records:
            internal.extend(["## 第 %d 段 %s" % (record["k"], record["title"]), "",
                             "- action：" + record["action"], "- 主 WHY：" + record["why"],
                             "- 屏幕："])
            internal.extend("  - %s%s" % ("【新】" if uid in record["show"] else "", tagged(registry[uid]))
                            for uid in record["screen_after"])
            if not record["screen_after"]:
                internal.append("  - （空）")
            internal.append("- 撤下：")
            internal.extend("  - %s（原上屏段 k%d）" % (tagged(registry[uid]), registry[uid]["k"])
                            for uid in record["retired"])
            if not record["retired"]:
                internal.append("  - （无）")
            internal.append("")
        (self.out_dir / "surface_internal.md").write_text(
            "\n".join(internal).rstrip() + "\n", encoding="utf-8")

        screen_steps = [{"time": record["time"],
                         "screen": [registry[uid]["text"] for uid in record["screen_after"]]}
                        for record in surface_records]
        view_a = _reader_view(screen_steps)
        reading_lines = ["# 边听边读（run144 本稿阅读视图）", "", "## 听中屏幕变化", "",
                         _reader_timeline(view_a).rstrip(), "", "## 展开可看（实际内容）", ""]
        for record in surface_records:
            if record["expand"]:
                reading_lines.extend(["### " + record["time"], ""])
                reading_lines.extend("- " + registry[uid]["text"] for uid in record["expand"])
                reading_lines.append("")
        if not any(record["expand"] for record in surface_records):
            reading_lines.append("（无）\n")
        reading_lines.extend(["", "## 曲终回顾（实际内容）", ""])
        recap_records = [(record, uid) for record in surface_records for uid in record["recap"]]
        for record, uid in recap_records:
            reading_lines.extend(["### " + record["time"], "", "- " + registry[uid]["text"], ""])
        if not recap_records:
            reading_lines.append("（无）\n")
        reading_a = "\n".join(reading_lines).rstrip() + "\n"
        (self.out_dir / "reading__gflash__op60.md").write_text(reading_a, encoding="utf-8")

        view_b = _reader_view(self.data["run124_steps"])
        reading_b = "# 边听边读（run124 B 阅读视图）\n\n" + _reader_timeline(view_b)
        (self.out_dir / "reading__run124B__op60.md").write_text(reading_b, encoding="utf-8")
        _assert_anonymous_payload(_strip_recorded_heading(
            reading_a, "# 边听边读（run144 本稿阅读视图）"), "a")
        _assert_anonymous_payload(_strip_recorded_heading(
            reading_b, "# 边听边读（run124 B 阅读视图）"), "b")
        actions = Counter(record["action"] for record in surface_records)
        stats = {"n_beads": len(surface_records),
                 "actions": {action: actions.get(action, 0) for action in ACTIONS},
                 "mean_screen_items": round(sum(len(record["screen_after"]) for record in surface_records) /
                                             len(surface_records), 2),
                 "shown_count": sum(len(record["show"]) for record in surface_records),
                 "retired_count": sum(len(record["retired"]) for record in surface_records),
                 "expanded_count": sum(len(record["expand"]) for record in surface_records),
                 "recap_count": sum(len(record["recap"]) for record in surface_records),
                 "reader_a_chars": len(reading_a), "reader_b_chars": len(reading_b),
                 "run124_steps": len(self.data["run124_steps"])}
        render = {"run_id": RUN_ID, "chooser_model_key": CFG["chooser"], "stats": stats,
                  "reading_a": "reading__gflash__op60.md", "reading_b": "reading__run124B__op60.md",
                  "view_a": view_a, "view_b": view_b}
        write_json(self.out_dir / "render.json", render)
        return render, {"a": reading_a, "b": reading_b}

    def _candidate_sets(self, readings: dict[str, str]) -> dict[str, dict[str, Any]]:
        a = _strip_recorded_heading(readings["a"], "# 边听边读（run144 本稿阅读视图）")
        b = _strip_recorded_heading(readings["b"], "# 边听边读（run124 B 阅读视图）")
        _assert_anonymous_payload(a, "a")
        _assert_anonymous_payload(b, "b")
        result: dict[str, dict[str, Any]] = {}
        for set_name, source in self.data["baselines"].items():
            # These source files have no declared title/header line; preserve every substantive byte.
            c = _strip_recorded_heading(source["text"], None)
            _assert_anonymous_payload(c, set_name + "/c")
            result[set_name] = {
                "texts": {"a": a, "b": b, "c": c},
                "sources": {
                    "a": {"source": "run144:reading__gflash__op60.md", "sha256": sha256_text(a),
                          "gen_model_key": CFG["gen"], "actual_gen": CFG["gen"],
                          "chooser_model_key": CFG["chooser"], "actual_chooser": CFG["chooser"]},
                    "b": dict(self.data["run124_lineage"]),
                    "c": {key: value for key, value in source.items() if key != "text"},
                },
            }
        return result

    def _make_compare_tasks(self, sets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
        tasks: list[dict[str, Any]] = []
        for set_index, set_name in enumerate(sorted(sets)):
            seed = SEED_COMPARE + 100 * set_index
            base = ["a", "b", "c"]
            random.Random(seed).shuffle(base)
            for order_index in range(3):
                order = base[order_index:] + base[:order_index]
                mapping = dict(zip(POSITIONS, order))
                candidate_texts = sets[set_name]["texts"]
                prompt = fill_template(self.data["templates"]["E7_COMPARE_v0"], WORK=WORK_NAME,
                                       A=candidate_texts[mapping["甲"]], B=candidate_texts[mapping["乙"]],
                                       C=candidate_texts[mapping["丙"]])
                if PLACEHOLDER_RE.search(prompt):
                    raise IntegrityError("comparison prompt placeholder remains")
                _assert_anonymous_payload(prompt, set_name + "/comparison prompt")
                tasks.append({"set": set_name, "order_index": order_index, "order": order,
                              "seed": seed, "mapping": mapping,
                              "task_id": "%s|order%d" % (set_name, order_index),
                              "logical_task_id": RUN_ID + ":" + set_name + "|order%d" % order_index,
                              "request_id": RUN_ID + ":muse:" + set_name + "|order%d" % order_index,
                              "prompt": prompt, "prompt_sha256": sha256_text(prompt),
                              "candidate_sha256": {key: sha256_text(value) for key, value in candidate_texts.items()},
                              "sources": sets[set_name]["sources"]})
        return tasks

    def _pack(self, slot: str, tasks: list[dict[str, Any]]) -> dict[str, Any]:
        status = ("PENDING - independent Muse review not dispatched" if slot == "muse_pending" else
                  "HELD - run135 post_submit_ambiguous global hold; no two-w submission")
        selected = []
        for task in tasks:
            selected.append({key: task[key] for key in (
                "set", "order_index", "order", "seed", "mapping", "task_id",
                "logical_task_id", "request_id",
                "prompt", "prompt_sha256", "candidate_sha256", "sources")})
        muse_identity = canonical_muse_identity("Muse", "external Muse")
        return {"schema": "run144-review-pack-v1", "run_id": RUN_ID, "slot": slot,
                "status": status, "template": "E7_COMPARE_v0",
                "review_target": MUSE_TARGET if slot == "muse_pending" else "two-w-held",
                "requested_identity": muse_identity if slot == "muse_pending" else None,
                "template_sha256": self.data["lock"]["template_sha256"][TEMPLATE_PATHS["E7_COMPARE_v0"]],
                "locks": {"source_sha256": self.data["lock"]["source_sha256"],
                          "template_sha256": self.data["lock"]["template_sha256"],
                          "driver_sha256": self.data["lock"]["driver_sha256"]},
                "positions": list(POSITIONS), "tasks": selected}

    def _stage_compare(self, readings: dict[str, str]) -> tuple[
            list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]], list[dict[str, Any]]]:
        sets = self._candidate_sets(readings)
        tasks = self._make_compare_tasks(sets)
        compare_records: list[dict[str, Any]] = []
        for set_name, group in sets.items():
            compare_dir = self.out_dir / "compare_inputs"
            compare_dir.mkdir(parents=True, exist_ok=True)
            for candidate, text in group["texts"].items():
                (compare_dir / (set_name + "__" + candidate + ".md")).write_text(
                    text + "\n", encoding="utf-8")
        for task in tasks:
            for judge in CFG["judges"]:
                candidate_texts = sets[task["set"]]["texts"]
                parser = lambda output, m=task["mapping"], c=candidate_texts: parse_compare(output, m, c)
                result = self.execute("compare", [task["set"], judge, task["order_index"]], judge,
                                      task["prompt"], "E7_COMPARE_v0", parser)
                parsed = result["parsed"]
                ranking_candidates = [task["mapping"][position] for position in parsed["ranking"]]
                compare_records.append({
                    "set": task["set"], "judge": judge, "actual_judge": judge,
                    "order_index": task["order_index"], "order": task["order"],
                    "seed": task["seed"], "mapping": task["mapping"],
                    "task_id": task["task_id"] + "|" + judge,
                    "prompt_sha256": result["prompt_sha256"], "attempt": result["attempt"],
                    "ranking_pos": parsed["ranking"], "ranking_candidates": ranking_candidates,
                    "best_moments": parsed["best_moments"], "worst_moments": parsed["worst_moments"],
                    "hindsight": parsed["hindsight"], "only_here": parsed["only_here"],
                    "why": parsed["why"], "self_flag": self_flag(task["set"], judge),
                    "evidence": result["paths"],
                })
        expected = {(set_name, judge, order) for set_name in sorted(BASELINE_MODELS)
                    for judge in CFG["judges"] for order in range(3)}
        actual = [(record["set"], record["judge"], record["order_index"]) for record in compare_records]
        if len(actual) != len(set(actual)) or set(actual) != expected:
            raise IntegrityError("compare baseline×judge×order identity set mismatch")
        mappings = _expected_compare_mapping()
        for set_name in sorted(BASELINE_MODELS):
            for judge in CFG["judges"]:
                group = [record for record in compare_records
                         if record["set"] == set_name and record["judge"] == judge]
                for record in group:
                    if record["mapping"] != mappings[(set_name, judge, record["order_index"])]:
                        raise IntegrityError("compare order/mapping mismatch")
                for candidate in ("a", "b", "c"):
                    positions = sorted(next(position for position, value in record["mapping"].items()
                                            if value == candidate) for record in group)
                    if positions != sorted(POSITIONS):
                        raise IntegrityError("candidate order rotation incomplete")
        aggregates: list[dict[str, Any]] = []
        for set_name in sorted(BASELINE_MODELS):
            for judge in CFG["judges"]:
                group = [record for record in compare_records
                         if record["set"] == set_name and record["judge"] == judge]
                aggregates.append({
                    "set": set_name, "judge": judge, "judge_is_generator_of": self_flag(set_name, judge),
                    "n": len(group),
                    "mean_rank_by_candidate": {
                        candidate: round(sum(record["ranking_candidates"].index(candidate) + 1
                                             for record in group) / len(group), 2)
                        for candidate in ("a", "b", "c")},
                    "first_by_candidate": dict(Counter(record["ranking_candidates"][0] for record in group)),
                })
        write_json(self.out_dir / "compare.json", {"run_id": RUN_ID, "judges": list(CFG["judges"]),
                                                    "aggregates": aggregates, "records": compare_records})
        muse_pack = self._pack("muse_pending", tasks)
        twow_pack = self._pack("twow_held", tasks)
        write_json(self.out_dir / "muse_review_pack.json", muse_pack)
        write_json(self.out_dir / "twow_review_pack.json", twow_pack)
        self._validate_pack(muse_pack, tasks, "muse_pending")
        self._validate_pack(twow_pack, tasks, "twow_held")
        return compare_records, aggregates, sets, tasks

    def _validate_pack(self, pack: dict[str, Any], tasks: list[dict[str, Any]], slot: str) -> None:
        if pack.get("schema") != "run144-review-pack-v1" or pack.get("slot") != slot:
            raise IntegrityError("review pack schema/slot mismatch")
        expected_status = ("PENDING - independent Muse review not dispatched" if slot == "muse_pending" else
                           "HELD - run135 post_submit_ambiguous global hold; no two-w submission")
        if pack.get("status") != expected_status or pack.get("positions") != list(POSITIONS):
            raise IntegrityError("review pack status/position lock mismatch")
        if pack.get("template") != "E7_COMPARE_v0" or pack.get("template_sha256") != \
                self.data["lock"]["template_sha256"][TEMPLATE_PATHS["E7_COMPARE_v0"]]:
            raise IntegrityError("review pack template identity mismatch")
        expected_tasks = {task["task_id"]: task for task in tasks}
        supplied = pack.get("tasks")
        if not isinstance(supplied, list):
            raise IntegrityError("review pack tasks missing")
        ids = [task.get("task_id") for task in supplied if isinstance(task, dict)]
        if len(ids) != len(supplied) or len(ids) != len(set(ids)) or set(ids) != set(expected_tasks):
            raise IntegrityError("review pack task ID set mismatch")
        locks = pack.get("locks", {})
        if locks.get("driver_sha256") != self.data["lock"]["driver_sha256"]:
            raise IntegrityError("review pack driver lock mismatch")
        if locks.get("source_sha256") != self.data["lock"]["source_sha256"]:
            raise IntegrityError("review pack source lock mismatch")
        if locks.get("template_sha256") != self.data["lock"]["template_sha256"]:
            raise IntegrityError("review pack template lock mismatch")
        for task in supplied:
            base = expected_tasks[task["task_id"]]
            for field in ("set", "order_index", "order", "seed", "mapping", "candidate_sha256", "sources"):
                if task.get(field) != base[field]:
                    raise IntegrityError("review pack task mismatch at %s/%s" % (task["task_id"], field))
            if task.get("prompt") != base["prompt"] or task.get("prompt_sha256") != sha256_text(task.get("prompt", "")):
                raise IntegrityError("review pack prompt bytes/SHA mismatch")
            if PLACEHOLDER_RE.search(task["prompt"]):
                raise IntegrityError("review pack has an unfilled placeholder")
            _assert_anonymous_payload(task["prompt"], slot + "/" + task["task_id"])
        for set_name in sorted(BASELINE_MODELS):
            group = [task for task in supplied if task["set"] == set_name]
            if len(group) != 3 or {task["order_index"] for task in group} != {0, 1, 2}:
                raise IntegrityError("review pack order task set incomplete")
            for candidate in ("a", "b", "c"):
                got = sorted(next(pos for pos, value in task["mapping"].items() if value == candidate)
                             for task in group)
                if got != sorted(POSITIONS):
                    raise IntegrityError("review pack candidate position rotation incomplete")

    def _report(self, why: list[dict[str, Any]], mech: list[dict[str, Any]],
                surface: list[dict[str, Any]], compare: list[dict[str, Any]],
                aggregates: list[dict[str, Any]], registry: dict[str, dict[str, Any]]) -> None:
        lines = ["# run144 E7 Flash 诊断报告（Op.60；永不进入 production）", "",
                 "- 固定阵容：gen=chooser=gflash；auditors=judges=gflash+luna_noweb。",
                 "- 历史：run130:gpt56w；producer 未验证，按 unknown 记录；why k 使用且仅使用 inventory_after(k-1)。",
                 "- 候选：a=本稿 reading；b=run124 生产稿 B；c=run132 V2A+Gemini 两组重建锚。Op.60 的 c 不是原始 V2A。",
                 "- run124 B 与 run132 c 的文件标签提供上游 model key；缺少可验证 terminal identity，报告明确标为 unverified。run144 每个 caller meta/output/terminal 都单独校验 actual_model。",
                 "- 此诊断不替代 GPT、不构成新模型公平赛、不进入 production；复用旧 E7/MECH 合同，无法证明单变量模型胜利。",
                 "- 新模型提交：0；本离线测试使用明确 MOCK namespace，不产生音乐候选。", "",
                 "## WHY：k2..23 全列", ""]
        for record in why:
            lines.append("- k%d（history prefix k%d，n=%d）：differs=%s；%s" %
                         (record["k"], record["history_prefix_k"], record["history_n"],
                          str(record["differs"]).lower(), record["sentence"]))
        lines.extend(["", "## MECH 与逐关系双审", ""])
        for record in mech:
            if not record["relations"]:
                lines.append("- k%d：没有候选关系。" % record["k"])
            for index, relation in enumerate(record["relations"]):
                lines.append("- k%d r%d：%s（解释条目 %s）；新理解：%s；审核=%s" %
                             (record["k"], index + 1, relation["relation"], relation["explains"],
                              relation["new_understanding"], json.dumps(relation["verdicts"], ensure_ascii=False)))
        lines.extend(["", "## 屏幕选择：KEEP / RETIRE / REPLACE / APPEND（逐条全文）", ""])
        for record in surface:
            shown = bool(record["show"])
            lines.extend(["### k%d %s" % (record["k"], record["time"]),
                          "", "主 WHY：%s" % record["why"], ""])
            for label in ("KEEP", "RETIRE", "REPLACE", "APPEND"):
                lines.append("**%s**" % label)
                if label == "KEEP":
                    uids = record["keep"]
                elif label == "APPEND":
                    uids = record["show"] if not record["retired"] else []
                elif label == "REPLACE":
                    uids = record["retired"] if shown else []
                else:
                    uids = record["retired"] if not shown else []
                if uids:
                    lines.extend("- %s — %s" % (uid, registry[uid]["text"]) for uid in uids)
                else:
                    lines.append("- （无）")
                if label == "APPEND" and shown and record["retired"]:
                    lines.extend("- %s — %s" % (uid, registry[uid]["text"]) for uid in record["show"])
            lines.append("")
        lines.extend(["## 三方盲比（每组×每评审×order 0/1/2）", "",
                      "自评 canonical 结果：Flash(gflash)=a；在 c_gflash_s1 组为 a,c；Luna 独立。",
                      "候选记录 gen：a=gflash，chooser=gflash；b=gpt56w（run124 标签，terminal identity 未验证）；",
                      "c_gpro_s3=gpro_web、c_gflash_s1=gflash_web（run132 meta model_key，terminal identity 未提供）。", ""])
        for aggregate in aggregates:
            lines.append("- %s / %s：n=%d；self=%s；mean-rank=%s；first=%s" %
                         (aggregate["set"], aggregate["judge"], aggregate["n"],
                          aggregate["judge_is_generator_of"], aggregate["mean_rank_by_candidate"],
                          aggregate["first_by_candidate"]))
        lines.append("")
        for record in compare:
            lines.append("- %s / %s / order%d seed=%d mapping=%s ranking=%s; quote schema validated" %
                         (record["set"], record["judge"], record["order_index"], record["seed"],
                          json.dumps(record["mapping"], ensure_ascii=False), record["ranking_candidates"]))
        lines.extend(["", "## 离线读者文件", "",
                      "- reading__gflash__op60.md 含实际展开可看与曲终回顾全文；选择没有生成新解释。",
                      "- reading__run124B__op60.md 为 run124 B 的屏幕视图。",
                      "- Muse pack 已机械生成但不是评审结果；two-w pack 已生成但仍处于 hold。",
                      "- 缺少真实 Muse 审核与两种 GPT 新鲜对照；不能宣告完成。", "",
                      "## 合同限制与状态", "",
                      "- WHY_GATE_v4、MECH_v1、MECH_AUDIT_v0、E7_SURFACE_v0、E7_COMPARE_v0 均为旧合同；该合同覆盖不足，不能把本诊断解释成模型单变量胜利。",
                      "- 审核结果只有在独立 transport/model、完整精确 artifact、全 schema/quotes、严格任务集合校验通过后才可归位。",
                      "- Completion: COMPLETION_PENDING（永不写 DONE / production-ready）。",
                      "- run135 post_submit_ambiguous 的全局 hold 阻止 two-w 提交；Muse 尚未派发。", ""])
        (self.out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")

    def _validate_collection(self, why: list[dict[str, Any]], mech: list[dict[str, Any]],
                             audits: list[dict[str, Any]], surface: list[dict[str, Any]],
                             compare: list[dict[str, Any]], tasks: list[dict[str, Any]]) -> None:
        if [record["k"] for record in why] != list(range(2, K_EXPECTED + 1)):
            raise IntegrityError("why full k2..23 set/order invalid")
        if [record["k"] for record in mech] != list(range(1, K_EXPECTED + 1)):
            raise IntegrityError("mech full k1..23 set/order invalid")
        if [record["k"] for record in surface] != list(range(1, K_EXPECTED + 1)):
            raise IntegrityError("surface full k1..23 set/order invalid")
        expected_audits = {(record["k"], idx, reviewer) for record in mech
                           for idx, _relation in enumerate(record["relations"]) for reviewer in CFG["auditors"]}
        actual_audits = [(record["k"], record["relation_index"], record["reviewer"]) for record in audits]
        if len(actual_audits) != len(set(actual_audits)) or set(actual_audits) != expected_audits:
            raise IntegrityError("audit reviewer exact set invalid")
        expected_compare = {(set_name, judge, order) for set_name in sorted(BASELINE_MODELS)
                            for judge in CFG["judges"] for order in range(3)}
        actual_compare = [(record["set"], record["judge"], record["order_index"]) for record in compare]
        if len(actual_compare) != len(set(actual_compare)) or set(actual_compare) != expected_compare:
            raise IntegrityError("compare exact set invalid")
        expected_mappings = _expected_compare_mapping()
        for set_name in sorted(BASELINE_MODELS):
            for judge in CFG["judges"]:
                group = [record for record in compare
                         if record["set"] == set_name and record["judge"] == judge]
                for record in group:
                    expected = expected_mappings[(set_name, judge, record["order_index"])]
                    if record.get("mapping") != expected:
                        raise IntegrityError("compare order mapping identity invalid")
                for candidate in ("a", "b", "c"):
                    positions = sorted(next(position for position, value in record["mapping"].items()
                                            if value == candidate) for record in group)
                    if positions != sorted(POSITIONS):
                        raise IntegrityError("compare candidate position ID set invalid")
        if len(tasks) != len(BASELINE_MODELS) * 3:
            raise IntegrityError("review pack task set invalid")

    def run(self) -> dict[str, Any]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._verify_output_lock()
            if ((self.out_dir / "queue_stop.json").exists() or
                    (self.out_dir / "execution_hold.json").exists()):
                raise QueueStopped("persisted queue/transport hold prevents any subsequent job/stage")
            self.data = _freeze_inputs(self.source_root)
            lock_path = self.out_dir / "freeze.json"
            if lock_path.exists() and read_json(lock_path) != self.data["lock"]:
                raise IntegrityError("frozen source/template/driver SHA changed")
            if not lock_path.exists():
                write_json(lock_path, self.data["lock"])
            self._load_calls()
            why = self._stage_why()
            mech, audits = self._stage_mech()
            surface = self._stage_surface(why, mech)
            registry = read_json(self.out_dir / "surface.json")["items"]
            _render, readings = self._stage_render(surface)
            compare, aggregates, sets, pack_tasks = self._stage_compare(readings)
            self._validate_collection(why, mech, audits, surface, compare, pack_tasks)
            self._report(why, mech, surface, compare, aggregates, registry)
            self._verify_final_artifacts(why, mech, audits, surface, compare, pack_tasks)
            failed = self.out_dir / "FAILED"
            if failed.exists():
                failed.unlink()
            (self.out_dir / "COMPLETION_PENDING").write_text(
                "status=COMPLETION_PENDING\nmissing=independent Muse review; fresh two-w reviews (held)\n"
                "real_model_submissions=0\n", encoding="utf-8")
            manifest = self._write_manifest()
            return {"ok": True, "completion": "COMPLETION_PENDING", "manifest": manifest,
                    "new_mock_submissions": self.new_submissions}
        except Exception as exc:
            try:
                pending = self.out_dir / "COMPLETION_PENDING"
                if pending.exists():
                    pending.unlink()
                (self.out_dir / "FAILED").write_text(
                    "status=FAILED\nreason=%s\n" % str(exc).replace("\n", " ")[:700], encoding="utf-8")
            except OSError:
                pass
            raise

    def _verify_final_artifacts(self, why: list[dict[str, Any]], mech: list[dict[str, Any]],
                                audits: list[dict[str, Any]], surface: list[dict[str, Any]],
                                compare: list[dict[str, Any]], pack_tasks: list[dict[str, Any]]) -> None:
        required = ("why.json", "mech.json", "surface.json", "render.json", "compare.json",
                    "report.md", "reading__gflash__op60.md", "reading__run124B__op60.md",
                    "muse_review_pack.json", "twow_review_pack.json")
        if not all((self.out_dir / name).is_file() for name in required):
            raise IntegrityError("required final artifact missing")
        for filename, slot in (("muse_review_pack.json", "muse_pending"),
                               ("twow_review_pack.json", "twow_held")):
            self._validate_pack(read_json(self.out_dir / filename), pack_tasks, slot)
        report = (self.out_dir / "report.md").read_text(encoding="utf-8")
        for required_text in ("KEEP", "RETIRE", "REPLACE", "APPEND", "主 WHY", "COMPLETION_PENDING",
                              "Op.60", "重建锚", "run135", "hold"):
            if required_text not in report:
                raise IntegrityError("report missing required declaration: " + required_text)
        reader = (self.out_dir / "reading__gflash__op60.md").read_text(encoding="utf-8")
        if "## 展开可看（实际内容）" not in reader or "## 曲终回顾（实际内容）" not in reader:
            raise IntegrityError("reader artifact lacks full expand/recap sections")
        for filename in ("why.json", "mech.json", "surface.json", "compare.json"):
            data = read_json(self.out_dir / filename)
            if not isinstance(data, dict) or data.get("run_id") != RUN_ID:
                raise IntegrityError("stage output identity mismatch: " + filename)
        for record in read_json(self.out_dir / "call_index.json")["records"]:
            self._verify_artifact(record, expected_prompt=None)

    def _write_manifest(self) -> dict[str, Any]:
        outputs = self._all_files()
        outputs.pop("run_manifest.json", None)
        manifest = {
            "run_id": RUN_ID, "mode": "MOCK_OFFLINE_TEST_ONLY",
            "config": {key: list(value) if isinstance(value, tuple) else value for key, value in CFG.items()},
            "real_model_submissions": 0, "mock_submissions_total": len(self.calls),
            "mock_submissions_this_invocation": self.new_submissions,
            "completed_parse_failures_preserved": sum(record.get("parse_status") == "failed"
                                                        for record in self.calls),
            "immutable_transport_attempts": len(self.transport_attempts),
            "transport_retry_verifier": "sourcebound verifier required; none implies persistent hold",
            "history_producer": self.data["history_producer"],
            "source_sha256": self.data["lock"]["source_sha256"],
            "template_sha256": self.data["lock"]["template_sha256"],
            "driver_sha256": self.data["lock"]["driver_sha256"],
            "candidate_generators_recorded": {name: candidate_generators(name) for name in sorted(BASELINE_MODELS)},
            "candidate_actual_identity_notes": {
                "a": "run144 caller evidence is MOCK; no model actual identity is claimed",
                "b": self.data["run124_lineage"],
                "c": {name: {key: value for key, value in source.items() if key != "text"}
                      for name, source in self.data["baselines"].items()},
            },
            "compare_design": {"sets": sorted(BASELINE_MODELS), "judges": list(CFG["judges"]),
                               "order_indices": [0, 1, 2], "positions": list(POSITIONS),
                               "seed_base": SEED_COMPARE},
            "completion": "COMPLETION_PENDING",
            "muse_identity_aliases": {"Muse/external Muse": canonical_muse_identity("Muse", "external Muse"),
                                      "canonical_target": MUSE_TARGET,
                                      "transport": MUSE_TRANSPORT},
            "limitations": [
                "Muse review is prepared, not returned or reviewed",
                "two-w pack is held by run135 post_submit_ambiguous",
                "old E7/MECH contracts do not establish a one-variable model win",
                "no actual CLI/model transport was invoked or independently accepted",
            ],
            "outputs": outputs,
        }
        write_json(self.out_dir / "run_manifest.json", manifest)
        return manifest


def _extract_prompt_payloads(prompt: str) -> dict[str, str]:
    payloads = {}
    for position, start_marker, end_marker in (
            ("甲", "【甲】", "【乙】"), ("乙", "【乙】", "【丙】"), ("丙", "【丙】", None)):
        if start_marker not in prompt:
            raise IntegrityError("packed comparison prompt is missing a candidate marker")
        section = prompt.split(start_marker, 1)[1]
        if end_marker:
            if end_marker not in section:
                raise IntegrityError("packed comparison prompt is missing a candidate boundary")
            section = section.split(end_marker, 1)[0]
        payloads[position] = section.strip()
    return payloads


def _validate_external_pack(pack: dict[str, Any]) -> dict[str, dict[str, Any]]:
    pack_fields = {"schema", "run_id", "slot", "status", "template", "review_target",
                   "requested_identity", "template_sha256", "locks", "positions", "tasks"}
    if not isinstance(pack, dict) or set(pack) != pack_fields or pack.get("run_id") != RUN_ID:
        raise IntegrityError("external Muse pack must match the frozen exact pack schema/run")
    if (pack.get("schema") != "run144-review-pack-v1" or pack.get("slot") != "muse_pending" or
            pack.get("status") != "PENDING - independent Muse review not dispatched" or
            pack.get("template") != "E7_COMPARE_v0" or pack.get("positions") != list(POSITIONS)):
        raise IntegrityError("external Muse pack identity/status mismatch")
    expected_muse_identity = canonical_muse_identity("Muse", "external Muse")
    if (pack.get("review_target") != MUSE_TARGET or
            pack.get("requested_identity") != expected_muse_identity):
        raise IntegrityError("external Muse review target/provider/model/transport mapping mismatch")
    locks = pack.get("locks")
    if not isinstance(locks, dict):
        raise IntegrityError("external Muse pack locks missing")
    expected_sources = set(INPUT_PATHS.values())
    expected_templates = set(TEMPLATE_PATHS.values())
    source_hashes = locks.get("source_sha256")
    template_hashes = locks.get("template_sha256")
    if (not isinstance(source_hashes, dict) or set(source_hashes) != expected_sources or
            not isinstance(template_hashes, dict) or set(template_hashes) != expected_templates or
            any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
                for value in source_hashes.values()) or
            any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
                for value in template_hashes.values()) or
            not re.fullmatch(r"[0-9a-f]{64}", str(locks.get("driver_sha256", "")))):
        raise IntegrityError("external Muse pack source/template/driver lock incomplete")
    frozen = _freeze_inputs(ROOT)["lock"]
    if (source_hashes != frozen["source_sha256"] or template_hashes != frozen["template_sha256"] or
            locks.get("driver_sha256") != frozen["driver_sha256"]):
        raise IntegrityError("external Muse pack source/template/driver lock differs from frozen inputs")
    if pack.get("template_sha256") != template_hashes.get(TEMPLATE_PATHS["E7_COMPARE_v0"]):
        raise IntegrityError("external Muse pack compare-template SHA mismatch")
    tasks = pack.get("tasks")
    if not isinstance(tasks, list):
        raise IntegrityError("external Muse pack tasks missing")
    by_id = {task.get("task_id"): task for task in tasks if isinstance(task, dict)}
    expected_ids = {set_name + "|order%d" % order for set_name in sorted(BASELINE_MODELS) for order in range(3)}
    if len(by_id) != len(tasks) or set(by_id) != expected_ids:
        raise IntegrityError("external Muse pack task-ID set is not exact")
    expected_mappings = _expected_compare_mapping()
    task_fields = {"set", "order_index", "order", "seed", "mapping", "task_id",
                   "logical_task_id", "request_id", "prompt", "prompt_sha256",
                   "candidate_sha256", "sources"}
    for set_index, set_name in enumerate(sorted(BASELINE_MODELS)):
        seed = SEED_COMPARE + 100 * set_index
        for order in range(3):
            task = by_id[set_name + "|order%d" % order]
            if set(task) != task_fields:
                raise IntegrityError("external Muse task must match the frozen exact task schema")
            if task.get("set") != set_name or task.get("order_index") != order or task.get("seed") != seed:
                raise IntegrityError("external Muse pack set/order/seed identity mismatch")
            if (task.get("logical_task_id") != RUN_ID + ":" + task["task_id"] or
                    task.get("request_id") != RUN_ID + ":muse:" + task["task_id"]):
                raise IntegrityError("external Muse logical task/request identity mismatch")
            if task.get("mapping") != expected_mappings[(set_name, CFG["judges"][0], order)]:
                raise IntegrityError("external Muse pack mapping identity mismatch")
            if task.get("order") != [task["mapping"][position] for position in POSITIONS]:
                raise IntegrityError("external Muse pack order/mapping mismatch")
            prompt = task.get("prompt")
            if not isinstance(prompt, str) or PLACEHOLDER_RE.search(prompt):
                raise IntegrityError("external Muse pack prompt missing or has a placeholder")
            if task.get("prompt_sha256") != sha256_text(prompt):
                raise IntegrityError("external Muse pack prompt SHA mismatch")
            _assert_anonymous_payload(prompt, "external Muse pack " + task["task_id"])
            embedded = _extract_prompt_payloads(prompt)
            mapping = task["mapping"]
            embedded_by_candidate = {mapping[position]: embedded[position] for position in POSITIONS}
            candidate_hashes = task.get("candidate_sha256")
            if (not isinstance(candidate_hashes, dict) or set(candidate_hashes) != {"a", "b", "c"} or
                    any(candidate_hashes[candidate] != sha256_text(embedded_by_candidate[candidate])
                        for candidate in ("a", "b", "c"))):
                raise IntegrityError("external Muse pack candidate text hash mismatch")
            sources = task.get("sources")
            if not isinstance(sources, dict) or set(sources) != {"a", "b", "c"}:
                raise IntegrityError("external Muse pack candidate lineage set mismatch")
            for candidate, source in sources.items():
                if not isinstance(source, dict):
                    raise IntegrityError("external Muse pack candidate source identity/hash incomplete")
                if candidate == "a":
                    exact = {"source", "sha256", "gen_model_key", "actual_gen",
                             "chooser_model_key", "actual_chooser"}
                    if (set(source) != exact or source.get("source") != "run144:reading__gflash__op60.md" or
                            source.get("sha256") != candidate_hashes["a"] or
                            source.get("gen_model_key") != CFG["gen"] or
                            source.get("actual_gen") != CFG["gen"] or
                            source.get("chooser_model_key") != CFG["chooser"] or
                            source.get("actual_chooser") != CFG["chooser"]):
                        raise IntegrityError("external Muse run144 candidate source identity/hash mismatch")
                elif candidate == "b":
                    exact = {"source", "source_sha256", "generator_model_key",
                             "generator_actual_identity", "chooser_actual_identity"}
                    if (set(source) != exact or source.get("source") != INPUT_PATHS["run124_b"] or
                            source.get("source_sha256") != source_hashes[INPUT_PATHS["run124_b"]] or
                            source.get("generator_model_key") != "gpt56w (recorded lineage label)" or
                            source.get("generator_actual_identity") !=
                            "unverified: reader render has no terminal identity artifact" or
                            source.get("chooser_actual_identity") !=
                            "unverified: reader render has no chooser terminal artifact"):
                        raise IntegrityError("external Muse run124 candidate source identity/hash mismatch")
                else:
                    source_path = INPUT_PATHS[set_name]
                    meta_path = INPUT_PATHS[set_name + "_meta"]
                    exact = {"source", "source_sha256", "source_meta", "source_meta_sha256",
                             "generator_model_key", "generator_actual_identity", "source_job_id"}
                    if (set(source) != exact or source.get("source") != source_path or
                            source.get("source_sha256") != source_hashes[source_path] or
                            source.get("source_meta") != meta_path or
                            source.get("source_meta_sha256") != source_hashes[meta_path] or
                            source.get("generator_model_key") != BASELINE_MODELS[set_name] or
                            source.get("generator_actual_identity") !=
                            "unverified: run132 bundle has no terminal identity artifact" or
                            (source.get("source_job_id") is not None and
                             not isinstance(source.get("source_job_id"), str))):
                        raise IntegrityError("external Muse run132 candidate source identity/hash mismatch")
    return by_id


def _external_source_bundle_sha256(pack: Mapping[str, Any], task: Mapping[str, Any]) -> str:
    """Hash candidate lineage together with every frozen source/template/driver lock."""
    locks = pack["locks"]
    bundle = {"candidate_sources": task["sources"],
              "source_sha256": locks["source_sha256"],
              "template_sha256": locks["template_sha256"],
              "driver_sha256": locks["driver_sha256"]}
    return sha256_text(json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _validate_external_muse_receipt(pack: Mapping[str, Any], task: Mapping[str, Any],
                                    result: Mapping[str, Any], raw_output: bytes,
                                    terminal: Mapping[str, Any], receipt: Any) -> dict[str, Any]:
    required = {"receipt_schema", "attestation_class", "verified", "source_bound", "task_id",
                "logical_task_id", "request_id", "prompt_sha256", "template_sha256",
                "source_bundle_sha256", "mapping_sha256", "seed", "raw_output_sha256",
                "raw_output_size", "terminal_status", "terminal_id", "review_target",
                "requested_provider", "requested_model", "requested_transport",
                "reported_provider", "reported_model", "reported_transport",
                "actual_provider", "actual_model", "actual_transport"}
    if not isinstance(receipt, dict) or set(receipt) != required:
        raise IntegrityError("trusted Muse sourcebound receipt must use the frozen exact field set")
    requested = canonical_muse_identity("Muse", "external Muse")
    reported = canonical_muse_identity(str(result.get("reported_provider", "")),
                                       str(result.get("reported_model", "")))
    if reported["target"] != MUSE_TARGET or str(result.get("reported_transport", "")).strip().lower() != MUSE_TRANSPORT:
        raise IntegrityError("reported Muse provider/model/transport does not map to the canonical target")
    expected = {"receipt_schema": "muse_sourcebound_receipt_v2",
                "verified": True, "source_bound": True,
                "task_id": task["task_id"], "logical_task_id": task["logical_task_id"],
                "request_id": task["request_id"], "prompt_sha256": task["prompt_sha256"],
                "template_sha256": pack["template_sha256"],
                "source_bundle_sha256": _external_source_bundle_sha256(pack, task),
                "mapping_sha256": sha256_text(json.dumps(
                    task["mapping"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
                "seed": task["seed"], "raw_output_sha256": sha256_bytes(raw_output),
                "raw_output_size": len(raw_output), "terminal_status": "completed",
                "terminal_id": terminal.get("terminal_id"), "review_target": MUSE_TARGET,
                "requested_provider": requested["provider"], "requested_model": requested["model"],
                "requested_transport": requested["transport"],
                "reported_provider": reported["provider"], "reported_model": reported["model"],
                "reported_transport": MUSE_TRANSPORT,
                "actual_provider": requested["provider"], "actual_model": requested["model"],
                "actual_transport": MUSE_TRANSPORT}
    for field, expected_value in expected.items():
        if receipt.get(field) != expected_value:
            raise IntegrityError("trusted Muse receipt is not source-bound for field " + field)
    if receipt.get("attestation_class") not in ("TEST_ONLY", "TRUSTED_SOURCEBOUND_ARCHIVE"):
        raise IntegrityError("Muse verifier attestation class is unknown")
    if (type(receipt.get("raw_output_size")) is not int or
            not isinstance(receipt.get("terminal_id"), str) or not receipt["terminal_id"].strip()):
        raise IntegrityError("Muse receipt requires exact byte size and nonempty terminal id")
    return receipt


def validate_external_review_results(pack: dict[str, Any], results: list[dict[str, Any]],
                                     expected_model: str,
                                     transport_verifier: Callable[[dict[str, Any], dict[str, Any],
                                                                    dict[str, Any], bytes], dict[str, Any]] | None = None
                                     ) -> list[dict[str, Any]]:
    """Validate exact artifacts and a sourcebound verifier receipt; caller claims are not attestation."""
    slot = pack.get("slot") if isinstance(pack, dict) else None
    if slot == "twow_held":
        raise QueueStopped("run135 post_submit_ambiguous hold prohibits accepting or submitting two-w results")
    expected_identity = canonical_muse_identity("Muse", expected_model)
    if slot != "muse_pending" or expected_identity["model"] != "muse-spark-1.3-contributor-free":
        raise IntegrityError("only the canonical pending Muse target may be ingested")
    if not isinstance(results, list):
        raise IntegrityError("external review pack/results schema missing")
    expected = _validate_external_pack(pack)
    ids = [result.get("task_id") for result in results if isinstance(result, dict)]
    if len(ids) != len(results) or len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise IntegrityError("external review task identity set mismatch")
    if not callable(transport_verifier):
        raise RealExecutionBlocked(
            "trusted sourcebound verifier unavailable; external Muse tasks remain pending")
    normalized = []
    result_fields = {"task_id", "logical_task_id", "request_id", "requested_identity",
                     "reported_provider", "reported_model", "reported_transport", "seed", "mapping",
                     "prompt_sha256", "raw_response", "artifacts", "candidate_texts"}
    for result in results:
        if not isinstance(result, dict) or set(result) != result_fields:
            raise IntegrityError("external Muse return must match the frozen result field set exactly")
        task = expected[result["task_id"]]
        if (result.get("logical_task_id") != task["logical_task_id"] or
                result.get("request_id") != task["request_id"] or
                result.get("requested_identity") != pack["requested_identity"] or
                result.get("mapping") != task["mapping"] or result.get("seed") != task["seed"] or
                result.get("prompt_sha256") != task["prompt_sha256"]):
            raise IntegrityError("external review task/request/mapping/seed/prompt identity mismatch")
        reported = canonical_muse_identity(str(result["reported_provider"]), str(result["reported_model"]))
        if reported["target"] != MUSE_TARGET or str(result["reported_transport"]).strip().lower() != MUSE_TRANSPORT:
            raise IntegrityError("reported Muse provider/model/transport does not map to the canonical target")
        artifact_files = result.get("artifacts")
        if not isinstance(artifact_files, dict) or set(artifact_files) != {"meta", "prompt", "output", "terminal"}:
            raise IntegrityError("external exact artifact set missing")
        paths = {name: Path(artifact_files[name]) for name in artifact_files}
        if not all(path.is_file() for path in paths.values()):
            raise IntegrityError("external exact artifact file missing")
        prompt_bytes, output_bytes = paths["prompt"].read_bytes(), paths["output"].read_bytes()
        terminal_bytes = paths["terminal"].read_bytes()
        prompt = prompt_bytes.decode("utf-8")
        if prompt_bytes != task["prompt"].encode("utf-8") or sha256_bytes(prompt_bytes) != task["prompt_sha256"]:
            raise IntegrityError("external prompt bytes differ from the frozen pack")
        if not isinstance(result["raw_response"], str) or output_bytes != result["raw_response"].encode("utf-8"):
            raise IntegrityError("external raw response is not byte-identical to the output artifact")
        meta, terminal = read_json(paths["meta"]), strict_json_loads(terminal_bytes.decode("utf-8"))
        if not isinstance(meta, dict) or not isinstance(terminal, dict):
            raise IntegrityError("external meta/terminal must be complete JSON objects")
        requested = pack["requested_identity"]
        receipt_binding = {"run_id": RUN_ID, "task_id": task["task_id"],
                           "logical_task_id": task["logical_task_id"], "request_id": task["request_id"],
                           "review_target": MUSE_TARGET, "requested_provider": requested["provider"],
                           "requested_model": requested["model"], "requested_transport": requested["transport"],
                           "reported_provider": reported["provider"], "reported_model": reported["model"],
                           "reported_transport": MUSE_TRANSPORT, "seed": task["seed"],
                           "mapping": task["mapping"], "mapping_sha256": sha256_text(json.dumps(
                               task["mapping"], ensure_ascii=False, sort_keys=True, separators=(",", ":"))),
                           "prompt_sha256": task["prompt_sha256"], "template_sha256": pack["template_sha256"],
                           "source_bundle_sha256": _external_source_bundle_sha256(pack, task)}
        if set(meta) != {"schema", "identity", "prompt_sha256", "output_sha256",
                         "terminal_sha256", "raw_output_size"}:
            raise IntegrityError("external Muse metadata must match the frozen exact schema")
        if meta.get("schema") != "run144-external-muse-meta-v1" or meta.get("identity") != receipt_binding:
            raise IntegrityError("external Muse metadata source/request identity mismatch")
        if (meta.get("prompt_sha256") != sha256_bytes(prompt_bytes) or
                meta.get("output_sha256") != sha256_bytes(output_bytes) or
                meta.get("terminal_sha256") != sha256_bytes(terminal_bytes) or
                meta.get("raw_output_size") != len(output_bytes)):
            raise IntegrityError("external Muse metadata bytes/hash/size mismatch")
        if set(terminal) != {"schema", "identity", "status", "terminal_id"}:
            raise IntegrityError("external Muse terminal must match the frozen exact schema")
        if (terminal.get("schema") != "run144-external-muse-terminal-v1" or
                terminal.get("identity") != receipt_binding or terminal.get("status") != "completed" or
                not isinstance(terminal.get("terminal_id"), str) or not terminal["terminal_id"].strip()):
            raise IntegrityError("external Muse terminal is incomplete or has a forbidden status")
        receipt = transport_verifier(result, meta, terminal, output_bytes)
        receipt = _validate_external_muse_receipt(pack, task, result, output_bytes, terminal, receipt)
        payloads = result.get("candidate_texts")
        if not isinstance(payloads, dict) or set(payloads) != {"a", "b", "c"}:
            raise IntegrityError("external result lacks all candidate payloads for quote validation")
        prompt_payloads = _extract_prompt_payloads(prompt)
        if any(prompt_payloads[position] != payloads[task["mapping"][position]] for position in POSITIONS):
            raise IntegrityError("external quote evidence candidate text differs from packed prompt")
        parsed, error = parse_compare(output_bytes.decode("utf-8"), task["mapping"], payloads)
        if error or parsed is None:
            raise IntegrityError("external result schema/quote validation failed: " + str(error))
        normalized.append({"task_id": task["task_id"], "logical_task_id": task["logical_task_id"],
                           "request_id": task["request_id"], "actual_provider": receipt["actual_provider"],
                           "actual_model": receipt["actual_model"], "transport": receipt["actual_transport"],
                           "parsed": parsed, "prompt_sha256": task["prompt_sha256"],
                           "verification_status": "TEST_ONLY_SOURCEBOUND" if receipt["attestation_class"] == "TEST_ONLY"
                           else "TRUSTED_SOURCEBOUND_ARCHIVE", "real_return_count": 0,
                           "music_acceptance": "NOT_PERFORMED"})
    return normalized


def real_preflight(root: Path = ROOT) -> dict[str, Any]:
    """Read only shared-entry presence; never import or initialize an unverified adapter."""
    tools_dir = Path(root) / "tools"
    v4_exists = (tools_dir / "experiment_calls_v4.py").is_file()
    v5_exists = (tools_dir / "experiment_calls_v5.py").is_file()
    return {
        "run_id": RUN_ID,
        "status": "blocked",
        "shared_v4": "present_unverified" if v4_exists else "absent",
        "shared_v5": "partial_unusable" if v5_exists else "absent",
        "shared_v6": "in_flight_not_auto_adopted",
        "dependencies": "not imported or verified",
        "real_model_submissions": 0,
        "cli_invocations": 0,
        "writes": 0,
        "reason": "no independently accepted shared exact-artifact entry and real CLI protocol",
    }


def _real_preflight_then_block(root: Path = ROOT) -> None:
    """Read-only preflight; the shared entry is never loaded."""
    status = real_preflight(root)
    raise RealExecutionBlocked(
        "BLOCKED: v4=%s; v5=%s; v6=%s; dependencies=%s; real submissions/CLI/writes=0. "
        "Independent shared-entry and real protocol acceptance is still required." %
        (status["shared_v4"], status["shared_v5"], status["shared_v6"], status["dependencies"])
    )


def run_all(out_dir: Path | None = None, caller: Callable[[dict[str, Any]], Any] | None = None,
            source_root: Path = ROOT) -> dict[str, Any]:
    if caller is None:
        _real_preflight_then_block()
    return Pipeline(Path(out_dir) if out_dir is not None else RUN_DIR, caller, source_root).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="run144 offline-safe E7 Flash diagnostic")
    parser.add_argument("--real", action="store_true", help="always blocked pending shared-entry acceptance")
    args = parser.parse_args(argv)
    try:
        if not args.real:
            raise RealExecutionBlocked(
                "BLOCKED: direct execution requires an injected offline caller; real submissions are disabled")
        _real_preflight_then_block()
    except RealExecutionBlocked as exc:
        print(str(exc))
        return 3
    return 3


if __name__ == "__main__":
    sys.exit(main())
