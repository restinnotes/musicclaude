"""run139 E7 Flash diagnostic pipeline; offline-safe and never production."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

THIS_DIR = Path(__file__).resolve().parent
ROOT = THIS_DIR.parents[1]
RUN_ID = "run139_e7_flash_diag"
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
SEED_COMPARE = 139060
POSITIONS = ("甲", "乙", "丙")
ACTIONS = ("保持", "补充", "更新", "沉默")
AUDIT_CLASSES = ("insight", "restatement", "manufactured", "imported")
AUDIT_DROP = ("manufactured", "imported")
MOCK_NAMESPACE = "MOCK:run139_e7_flash_diag"
ARTIFACT_SCHEMA = "run139-exact-artifacts-v1"

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
IDENTITY_LEAK_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_])(?:gpt(?:[-_ ]?\w*)?|gemini|claude|luna(?:_noweb)?|"
    r"gpro(?:_web)?|gflash(?:_web)?|muse|sonnet|run\d{2,3}|v2a|E7_[A-Za-z0-9_]+|ATTN_[A-Za-z0-9_]+)(?![A-Za-z0-9_])"
)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
REL_HEAD_RE = re.compile(r"^###\s+(.*)$", re.M)


class Run139Error(RuntimeError):
    pass


class RealExecutionBlocked(Run139Error):
    pass


class IntegrityError(Run139Error):
    pass


class QueueStopped(Run139Error):
    pass


class StageFailed(Run139Error):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(json_bytes(value))
    tmp.replace(path)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fill_template(template: str, **values: Any) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", str(value))
    leftovers = PLACEHOLDER_RE.findall(out)
    if leftovers:
        raise IntegrityError("unfilled prompt placeholder(s): " + ", ".join(sorted(set(leftovers))))
    return out


def extract_json_object(text: str) -> tuple[bool, Any, str | None]:
    if not isinstance(text, str) or not text.strip():
        return False, None, "empty output"
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return False, None, "no JSON object bounds"
    try:
        value = json.loads(text[start:end + 1])
    except Exception as exc:
        return False, None, "invalid JSON object: " + type(exc).__name__
    return True, value, None


def extract_json_array(text: str) -> tuple[bool, Any, str | None]:
    if not isinstance(text, str) or not text.strip():
        return False, None, "empty output"
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        return False, None, "no JSON array bounds"
    try:
        value = json.loads(text[start:end + 1])
    except Exception as exc:
        return False, None, "invalid JSON array: " + type(exc).__name__
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
    differs = obj.get("differs")
    if isinstance(differs, str) and differs.strip().lower() in ("true", "false"):
        differs = differs.strip().lower() == "true"
    if not isinstance(differs, bool):
        return None, "differs must be boolean"
    sentence = obj.get("sentence", "")
    sentence = sentence.strip() if isinstance(sentence, str) else ""
    if differs and (not sentence or sentence == "无"):
        return None, "differs=true requires an actual sentence"
    return {"differs": differs, "sentence": sentence or "无"}, None


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
        if not isinstance(value, dict):
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
            if value_no not in nums:
                nums.append(value_no)
        if len(nums) < 2:
            return None, "relation %d must explain at least two distinct items" % index
        parsed.append({"relation": relation.strip(), "explains": sorted(nums),
                       "new_understanding": understanding.strip()})
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
    verdict = obj.get("class")
    why = obj.get("why")
    if verdict not in AUDIT_CLASSES or not isinstance(why, str) or not why.strip():
        return None, "audit class/why schema invalid"
    return {"class": verdict, "why": why.strip()}, None


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
            "recap": recap, "why": why.strip()}, None


def parse_compare(output: str, mapping: dict[str, str], candidate_texts: dict[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    ok, obj, error = extract_json_object(output)
    if not ok or not isinstance(obj, dict):
        return None, error or "top level is not an object"
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
            if not snippets or not any(snippet in target for snippet in snippets):
                return None, "%s[%s] has no quote found in its candidate" % (field, position)
    for position in POSITIONS:
        only = normalized["only_here"][position]
        hindsight = normalized["hindsight"][position]
        if not isinstance(only, str) or not only.strip() or not isinstance(hindsight, list):
            return None, "only_here/hindsight schema invalid at " + position
        if any(not isinstance(value, str) for value in hindsight):
            return None, "hindsight entries must be strings"
    why = obj.get("why")
    if not isinstance(why, str) or not why.strip():
        return None, "compare why is empty"
    return {"ranking": ranking, "best_moments": normalized["best_moments"],
            "worst_moments": normalized["worst_moments"], "hindsight": normalized["hindsight"],
            "only_here": normalized["only_here"], "why": why.strip()}, None


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
        meta = json.loads(raw_sources[set_name + "_meta"].decode("utf-8"))
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
        "schema": "run139-freeze-v1",
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
                 source_root: Path = ROOT) -> None:
        self.out_dir = Path(out_dir).resolve()
        self.source_root = Path(source_root).resolve()
        self.caller = caller
        self.namespace = MOCK_NAMESPACE
        self.transport = "MOCK"
        self.data: dict[str, Any] | None = None
        self.calls: list[dict[str, Any]] = []
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
            raise IntegrityError("run139 never accepts a DONE marker")

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

    def _save_calls(self) -> None:
        write_json(self.out_dir / "call_index.json", {
            "run_id": RUN_ID, "namespace": self.namespace,
            "records": self.calls,
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
        expected_identity = {
            "run_id": RUN_ID, "namespace": self.namespace,
            "logical_id": record.get("logical_id"), "attempt": record.get("attempt"),
            "requested_model": record.get("requested_model"), "actual_model": record.get("requested_model"),
            "transport": "MOCK",
        }
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
        prompt = prompt_bytes.decode("utf-8")
        output = output_bytes.decode("utf-8")
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
                           "transport": "MOCK"}
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
        if terminal.get("exit_code") not in (0, None) and terminal.get("status") != "queue_stop":
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

    def _make_record(self, *, logical_id: str, step: str, key: list[Any], model: str,
                     prompt_version: str, prompt: str, attempt: int) -> dict[str, Any]:
        lock = self.data["lock"]
        identity = {"run_id": RUN_ID, "namespace": self.namespace, "logical_id": logical_id,
                    "attempt": attempt, "requested_model": model, "actual_model": model,
                    "transport": self.transport}
        return {"logical_id": logical_id, "step": step, "key": key,
                "requested_model": model, "prompt_version": prompt_version,
                "attempt": attempt, "identity": identity,
                "driver_sha256": lock["driver_sha256"], "prompt_sha256": sha256_text(prompt),
                "paths": self._paths_for(logical_id, attempt)}

    def execute(self, step: str, key: list[Any], model: str, prompt: str, prompt_version: str,
                parser: Callable[[str], tuple[Any, str | None]]) -> dict[str, Any]:
        if (self.out_dir / "queue_stop.json").exists():
            raise QueueStopped("persisted queue_stop blocks every following job/stage")
        if PLACEHOLDER_RE.search(prompt):
            raise IntegrityError("unfilled placeholder in final prompt")
        logical_id = step + ":" + sha256_text(json.dumps(key, ensure_ascii=False, sort_keys=True))[:24]
        prior = sorted((record for record in self.calls if record["logical_id"] == logical_id),
                       key=lambda record: record["attempt"])
        next_attempt = max((record["attempt"] for record in prior), default=-1) + 1
        for record in prior:
            _, output, terminal = self._verify_artifact(record, prompt)
            if terminal["status"] == "queue_stop":
                raise QueueStopped("terminal queue_stop blocks subsequent work")
            if terminal["status"] != "completed":
                raise IntegrityError("prior caller attempt has no completed terminal")
            parsed, error = parser(output)
            if error is None and parsed is not None:
                return {"logical_id": logical_id, "attempt": record["attempt"], "parsed": parsed,
                        "output": output, "prompt_sha256": record["prompt_sha256"],
                        "paths": record["paths"], "resumed": True}
        errors: list[str] = []
        while next_attempt < MAX_ATTEMPTS:
            record = self._make_record(logical_id=logical_id, step=step, key=key, model=model,
                                       prompt_version=prompt_version, prompt=prompt, attempt=next_attempt)
            paths_abs = {name: str(self._output_path(rel)) for name, rel in record["paths"].items()}
            request = {"schema": ARTIFACT_SCHEMA, "mode": "MOCK_ONLY_OFFLINE_TEST",
                       "identity": record["identity"], "step": step, "key": key,
                       "requested_model": model, "prompt_version": prompt_version,
                       "prompt": prompt, "prompt_sha256": record["prompt_sha256"],
                       "driver_sha256": record["driver_sha256"], "paths": paths_abs,
                       "required_artifacts": ["meta", "prompt", "output", "terminal"],
                       "must_not_use_cli_network_or_model": True}
            self.new_submissions += 1
            try:
                self.caller(request)
            except Exception:
                self.calls.append(record)
                self._save_calls()
                raise
            self.calls.append(record)
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
                return {"logical_id": logical_id, "attempt": next_attempt, "parsed": parsed,
                        "output": output, "prompt_sha256": record["prompt_sha256"],
                        "paths": record["paths"], "resumed": False}
            errors.append(error or "parser rejected completed output")
            next_attempt += 1
        raise StageFailed("%s failed after %d immutable completed attempt(s): %s" %
                          (logical_id, MAX_ATTEMPTS, "; ".join(errors)))

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
        internal: list[str] = ["# run139 内部决策稿（诊断用途；不进 production）", ""]
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
        reading_lines = ["# 边听边读（run139 本稿阅读视图）", "", "## 听中屏幕变化", "",
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
            reading_a, "# 边听边读（run139 本稿阅读视图）"), "a")
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
        a = _strip_recorded_heading(readings["a"], "# 边听边读（run139 本稿阅读视图）")
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
                    "a": {"source": "run139:reading__gflash__op60.md", "sha256": sha256_text(a),
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
                "prompt", "prompt_sha256", "candidate_sha256", "sources")})
        return {"schema": "run139-review-pack-v1", "run_id": RUN_ID, "slot": slot,
                "status": status, "template": "E7_COMPARE_v0",
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
        if pack.get("schema") != "run139-review-pack-v1" or pack.get("slot") != slot:
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
        lines = ["# run139 E7 Flash 诊断报告（Op.60；永不进入 production）", "",
                 "- 固定阵容：gen=chooser=gflash；auditors=judges=gflash+luna_noweb。",
                 "- 历史：run130:gpt56w；producer 未验证，按 unknown 记录；why k 使用且仅使用 inventory_after(k-1)。",
                 "- 候选：a=本稿 reading；b=run124 生产稿 B；c=run132 V2A+Gemini 两组重建锚。Op.60 的 c 不是原始 V2A。",
                 "- run124 B 与 run132 c 的文件标签提供上游 model key；缺少可验证 terminal identity，报告明确标为 unverified。run139 每个 caller meta/output/terminal 都单独校验 actual_model。",
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
            if (self.out_dir / "queue_stop.json").exists():
                raise QueueStopped("persisted queue_stop prevents any subsequent job/stage")
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
            "history_producer": self.data["history_producer"],
            "source_sha256": self.data["lock"]["source_sha256"],
            "template_sha256": self.data["lock"]["template_sha256"],
            "driver_sha256": self.data["lock"]["driver_sha256"],
            "candidate_generators_recorded": {name: candidate_generators(name) for name in sorted(BASELINE_MODELS)},
            "candidate_actual_identity_notes": {
                "a": "run139 caller evidence is MOCK; no model actual identity is claimed",
                "b": self.data["run124_lineage"],
                "c": {name: {key: value for key, value in source.items() if key != "text"}
                      for name, source in self.data["baselines"].items()},
            },
            "compare_design": {"sets": sorted(BASELINE_MODELS), "judges": list(CFG["judges"]),
                               "order_indices": [0, 1, 2], "positions": list(POSITIONS),
                               "seed_base": SEED_COMPARE},
            "completion": "COMPLETION_PENDING",
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
    if (pack.get("schema") != "run139-review-pack-v1" or pack.get("slot") != "muse_pending" or
            pack.get("status") != "PENDING - independent Muse review not dispatched" or
            pack.get("template") != "E7_COMPARE_v0" or pack.get("positions") != list(POSITIONS)):
        raise IntegrityError("external Muse pack identity/status mismatch")
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
    for set_index, set_name in enumerate(sorted(BASELINE_MODELS)):
        seed = SEED_COMPARE + 100 * set_index
        for order in range(3):
            task = by_id[set_name + "|order%d" % order]
            if task.get("set") != set_name or task.get("order_index") != order or task.get("seed") != seed:
                raise IntegrityError("external Muse pack set/order/seed identity mismatch")
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
    return by_id


def validate_external_review_results(pack: dict[str, Any], results: list[dict[str, Any]],
                                     expected_model: str,
                                     transport_verifier: Callable[[dict[str, Any], dict[str, Any],
                                                                    dict[str, Any]], dict[str, Any]] | None = None
                                     ) -> list[dict[str, Any]]:
    """Validate a later Muse/two-w return; this function never dispatches or imports a reviewer."""
    slot = pack.get("slot") if isinstance(pack, dict) else None
    if slot == "twow_held":
        raise QueueStopped("run135 post_submit_ambiguous hold prohibits accepting or submitting two-w results")
    if slot != "muse_pending" or expected_model != "muse":
        raise IntegrityError("only the pending Muse review pack may be ingested here")
    if not isinstance(results, list):
        raise IntegrityError("external review pack/results schema missing")
    expected = _validate_external_pack(pack)
    ids = [result.get("task_id") for result in results if isinstance(result, dict)]
    if len(ids) != len(results) or len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise IntegrityError("external review task identity set mismatch")
    if not callable(transport_verifier):
        raise RealExecutionBlocked(
            "independent transport/model verifier unavailable; packed tasks remain pending and cannot be ingested")
    normalized = []
    for result in results:
        task = expected[result["task_id"]]
        if (result.get("mapping") != task.get("mapping") or result.get("seed") != task.get("seed") or
                result.get("prompt_sha256") != task.get("prompt_sha256")):
            raise IntegrityError("external review mapping/seed/prompt identity mismatch")
        if result.get("actual_model") != expected_model or result.get("transport") in (None, "", "MOCK"):
            raise IntegrityError("external reviewer actual model/transport is not independently identified")
        if result.get("terminal_identity_verified") is not True:
            raise IntegrityError("external terminal identity missing")
        artifact_files = result.get("artifacts")
        if not isinstance(artifact_files, dict) or set(artifact_files) != {"meta", "prompt", "output", "terminal"}:
            raise IntegrityError("external exact artifact set missing")
        paths = {name: Path(artifact_files[name]) for name in artifact_files}
        if not all(path.is_file() for path in paths.values()):
            raise IntegrityError("external exact artifact file missing")
        prompt_bytes, output_bytes = paths["prompt"].read_bytes(), paths["output"].read_bytes()
        terminal_bytes = paths["terminal"].read_bytes()
        prompt = prompt_bytes.decode("utf-8")
        if prompt != task.get("prompt") or sha256_text(prompt) != task.get("prompt_sha256"):
            raise IntegrityError("external prompt bytes differ from the frozen pack")
        meta, terminal = read_json(paths["meta"]), json.loads(terminal_bytes.decode("utf-8"))
        expected_identity = {
            "task_id": task["task_id"], "actual_model": expected_model,
            "transport": result["transport"], "seed": task["seed"],
            "mapping": task["mapping"], "prompt_sha256": task["prompt_sha256"],
        }
        if meta.get("task_id") != task["task_id"] or terminal.get("task_id") != task["task_id"]:
            raise IntegrityError("external meta/terminal task identity mismatch")
        if meta.get("identity") != expected_identity or terminal.get("identity") != expected_identity:
            raise IntegrityError("external meta/terminal identity fields are incomplete")
        if (meta.get("actual_model") != expected_model or terminal.get("actual_model") != expected_model or
                meta.get("transport") != result.get("transport") or
                terminal.get("transport") != result.get("transport")):
            raise IntegrityError("external meta/terminal model or transport mismatch")
        if (meta.get("prompt_sha256") != sha256_bytes(prompt_bytes) or
                meta.get("output_sha256") != sha256_bytes(output_bytes) or
                meta.get("terminal_sha256") != sha256_bytes(terminal_bytes)):
            raise IntegrityError("external meta artifact hashes do not match exact disk bytes")
        if (terminal.get("status") != "completed" or terminal.get("identity_verified") is not True or
                terminal.get("transport_identity_verified") is not True or
                not isinstance(terminal.get("terminal_id"), str) or not terminal.get("terminal_id")):
            raise IntegrityError("external terminal not completed with verified identity")
        attestation = transport_verifier(result, meta, terminal)
        if (not isinstance(attestation, dict) or attestation.get("verified") is not True or
                attestation.get("task_id") != task["task_id"] or
                attestation.get("actual_model") != expected_model or
                attestation.get("transport") != result.get("transport") or
                attestation.get("terminal_id") != terminal.get("terminal_id")):
            raise IntegrityError("independent transport verifier did not attest the exact Muse terminal identity")
        output = output_bytes.decode("utf-8")
        payloads = result.get("candidate_texts")
        if not isinstance(payloads, dict) or set(payloads) != {"a", "b", "c"}:
            raise IntegrityError("external result lacks all candidate payloads for quote validation")
        prompt_payloads = _extract_prompt_payloads(prompt)
        if any(prompt_payloads[position] != payloads[task["mapping"][position]] for position in POSITIONS):
            raise IntegrityError("external quote evidence candidate text differs from packed prompt")
        parsed, error = parse_compare(output, task["mapping"], payloads)
        if error or parsed is None:
            raise IntegrityError("external result schema/quote validation failed: " + str(error))
        normalized.append({"task_id": result["task_id"], "actual_model": expected_model,
                           "transport": result["transport"], "parsed": parsed,
                           "prompt_sha256": task["prompt_sha256"]})
    return normalized


def _load_v4_lazily_then_block() -> None:
    """Load the optional shared entry only when a real run is explicitly attempted."""
    path = ROOT / "tools" / "experiment_calls_v4.py"
    if not path.is_file():
        raise RealExecutionBlocked(
            "BLOCKED: tools/experiment_calls_v4.py is absent; real CLI/model path is disabled. "
            "Complete independent acceptance of the shared exact-artifact entry and real CLI protocol first."
        )
    spec = importlib.util.spec_from_file_location("run139_experiment_calls_v4", path)
    if spec is None or spec.loader is None:
        raise RealExecutionBlocked("BLOCKED: unable to inspect the shared v4 entry")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    raise RealExecutionBlocked(
        "BLOCKED: shared v4 entry exists but independent exact-artifact acceptance and real CLI protocol "
        "verification are still required; this diagnostic does not enable real submissions."
    )


def run_all(out_dir: Path | None = None, caller: Callable[[dict[str, Any]], Any] | None = None,
            source_root: Path = ROOT) -> dict[str, Any]:
    if caller is None:
        _load_v4_lazily_then_block()
    return Pipeline(Path(out_dir) if out_dir is not None else RUN_DIR, caller, source_root).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="run139 offline-safe E7 Flash diagnostic")
    parser.add_argument("--real", action="store_true", help="always blocked pending shared-entry acceptance")
    args = parser.parse_args(argv)
    try:
        if not args.real:
            raise RealExecutionBlocked(
                "BLOCKED: direct execution requires an injected offline caller; real submissions are disabled")
        _load_v4_lazily_then_block()
    except RealExecutionBlocked as exc:
        print(str(exc))
        return 3
    return 3


if __name__ == "__main__":
    sys.exit(main())
