"""Run a JSON-described Thread pipeline; see schemes/README_pipe.md."""
import argparse
import json
import os
import re
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, as_completed, wait
from pathlib import Path

import covjudge
import evo
import v6fix as V
import work_meta

HERE = Path(__file__).resolve().parent
SCHEMES = HERE / "schemes"
BUILTINS = {"WORK_INFO", "SEGMENTS", "CENTER", "BEADS_TEXT"}


def token(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", value):
        raise ValueError(f"{label}: expected letters, digits, underscores or hyphens")
    return value


def prompt_path(name):
    if not isinstance(name, str):
        raise ValueError("prompt_file must be a path relative to schemes/")
    path = (SCHEMES / name).resolve()
    if not path.is_relative_to(SCHEMES.resolve()) or path.suffix.lower() != ".txt":
        raise ValueError(f"prompt_file must be a .txt inside schemes/: {name!r}")
    return path


def source_refs(source):
    """Validate a source and return its step dependencies."""
    if isinstance(source, str):
        return {source[5:]} if source.startswith("step:") else set()
    if isinstance(source, dict) and set(source) == {"text"} and isinstance(source["text"], str):
        return set()
    if isinstance(source, list):
        return set().union(*(source_refs(part) for part in source))
    raise ValueError(f"invalid source (use a string, {{\"text\": ...}}, or a list): {source!r}")


def resolve(source, builtins, outputs):
    if isinstance(source, list):
        return "".join(resolve(part, builtins, outputs) for part in source)
    if isinstance(source, dict):
        return source["text"]
    if source in BUILTINS:
        return builtins[source]
    if source.startswith("step:"):
        return json.dumps(outputs[source[5:]], ensure_ascii=False, indent=1)
    return source


def load_spec(filename):
    path = Path(filename)
    spec = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(spec, dict) or set(spec) - {"name", "note", "steps", "edits", "final"}:
        raise ValueError("pipeline must be an object with name/note/steps/edits/final")
    spec.setdefault("name", path.stem)
    spec.setdefault("note", spec["name"])
    if not isinstance(spec["name"], str) or not isinstance(spec["note"], str):
        raise ValueError("name and note must be strings")
    steps = spec.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("steps must be a nonempty array")
    by_id, texts = {}, {}
    for step in steps:
        required = {"id", "prompt_file", "replace", "model"}
        if (not isinstance(step, dict) or not required <= set(step)
                or set(step) - required - {"append", "after"}):
            raise ValueError("each step needs id/prompt_file/replace/model; optional append/after")
        sid = token(step["id"], "step id")
        if sid in by_id:
            raise ValueError(f"duplicate step id: {sid}")
        by_id[sid] = step
        if step["model"] not in ("g6", "g56"):
            raise ValueError(f"{sid}: model must be g6 or g56")
        if not isinstance(step["replace"], dict):
            raise ValueError(f"{sid}: replace must be an object")
        for placeholder, source in step["replace"].items():
            if not placeholder:
                raise ValueError(f"{sid}: empty placeholder")
            source_refs(source)
        if not isinstance(step.get("append", ""), str):
            raise ValueError(f"{sid}: append must be a string")
        after = step.get("after", [])
        if isinstance(after, str):
            after = [after]
        if not isinstance(after, list) or not all(isinstance(dep, str) for dep in after):
            raise ValueError(f"{sid}: after must be a step id or an array of ids")
        step["after"] = after
        texts[step["prompt_file"]] = prompt_path(step["prompt_file"]).read_text(encoding="utf-8")

    edits = spec.get("edits", [])
    if not isinstance(edits, list):
        raise ValueError("edits must be an array")
    # Apply edits in order to a preview, so stale fragments fail before any model calls.
    preview = dict(texts)
    for edit in edits:
        if not isinstance(edit, dict) or set(edit) != {"prompt_file", "old", "new"}:
            raise ValueError("each edit needs exactly prompt_file/old/new")
        name = edit["prompt_file"]
        if name not in texts:
            raise ValueError(f"edit refers to an unused prompt_file: {name!r}")
        if not isinstance(edit["old"], str) or not edit["old"]:
            raise ValueError("edit.old must be nonempty text")
        source_refs(edit["new"])
        if edit["old"] not in preview[name]:
            raise ValueError(f"edit.old fragment not found in {name}")
        # Only literal edits can introduce fragments targeted by later edits.
        new = edit["new"]
        literal = isinstance(new, str) and new not in BUILTINS and not new.startswith("step:")
        replacement = new if literal else (new["text"] if isinstance(new, dict) else "")
        preview[name] = preview[name].replace(edit["old"], replacement)

    deps = {}
    for sid, step in by_id.items():
        refs = set(step["after"])
        for source in step["replace"].values():
            refs |= source_refs(source)
        for edit in edits:
            if edit["prompt_file"] == step["prompt_file"]:
                refs |= source_refs(edit["new"])
        unknown = refs - by_id.keys()
        if unknown:
            raise ValueError(f"{sid}: unknown dependencies {sorted(unknown)}")
        deps[sid] = refs
    final = spec.get("final")
    if not isinstance(final, str) or final not in by_id:
        raise ValueError("final must name an existing step")
    complete = set()
    while len(complete) < len(by_id):
        ready = {sid for sid in by_id if sid not in complete and deps[sid] <= complete}
        if not ready:
            raise ValueError(f"dependency cycle: {sorted(by_id.keys() - complete)}")
        complete |= ready
    spec["_steps"], spec["_texts"], spec["_deps"] = by_id, texts, deps
    return spec


def render_step(spec, sid, builtins, outputs):
    """Keep str.replace order, whitespace and JSON formatting identical to schemes.py."""
    step = spec["_steps"][sid]
    text = spec["_texts"][step["prompt_file"]]
    for edit in spec.get("edits", []):
        if edit["prompt_file"] == step["prompt_file"]:
            if edit["old"] not in text:
                raise ValueError(f"{sid}: edit.old fragment no longer present")
            text = text.replace(edit["old"], resolve(edit["new"], builtins, outputs))
    text += step.get("append", "")
    for placeholder, source in step["replace"].items():
        text = text.replace(placeholder, resolve(source, builtins, outputs))
    return text


def work_context(w, ref):
    graph = V.graph_of(w, ref)
    metadata = work_meta.load(w)
    composer = metadata['composer']
    if metadata.get('composer_en'):
        composer += f"（{metadata['composer_en']}）"
    builtins = {
        "WORK_INFO": f"作曲家：{composer}\n作品：{metadata['title_zh']}{metadata['opus']}",
        "SEGMENTS": "\n".join(f"{s['sec']}：第 {s['bars']} 小节" for s in graph["segments"]),
        "CENTER": graph["center"],
        "BEADS_TEXT": covjudge.bead_text(w),
    }
    return builtins, graph


def call(rid, message, model, name):
    if not evo.done(rid):
        evo.call(rid, message, model=V.JUDGES[model], meta={"stage": f"scheme-{name}"})
    result = V.parse(rid)
    if result is None:      # 11-02: a model may answer with a bare JSON array (scqb_op60_A1); keep it as {"items": [...]}
        import re as _re
        # 11-02: the web route sometimes returns markdown-escaped text (a backslash at each line end, &#x20; for spaces); undo that first
        raw = _re.sub(r"\\(\r?\n)", r"\1", (evo.output(rid) or "").replace("&#x20;", " "))
        raw = _re.sub(r"\\([\[\]_*`~])", r"\1", raw)
        try:
            obj = json.loads(raw.strip().rstrip("\\").strip())
            result = obj if isinstance(obj, dict) else {"items": obj}
        except Exception:
            pass
        m = _re.search(r"\[.*\]", raw, _re.S) if result is None else None
        if m:
            try:
                result = {"items": json.loads(m.group(0))}
            except Exception:
                pass
    if not result:
        raise RuntimeError(f"{rid}: no usable json")
    return result


def save(w, g_ref, result, note, tag, ref):
    """The same graph conversion and output layout as schemes.save()."""
    bars = {s["sec"]: s["bars"] for s in g_ref["segments"]}
    got = {s.get("sec"): s for s in result.get("segments") or []}
    missing = [sec for sec in bars if not (got.get(sec) or {}).get("items")]
    if missing:
        raise RuntimeError(f"{w} {tag}: segments missing {missing}")
    graph = {"center": g_ref["center"], "segments": []}
    seen = set()
    original_ids = {}
    for sec in bars:
        segment = got[sec]
        items = []
        for k, it in enumerate(segment["items"], 1):
            item_id = f"{sec}-{k}"
            # IDs are presentation-normalized; references must follow the same
            # mapping, including a reference to an earlier item in this segment.
            cites = [original_ids.get(c, c) for c in it.get("cite") or [] if isinstance(c, str)]
            items.append({"id": item_id, "text": it["text"], "key": it["text"][:8],
                          "follows": bool(it.get("after")), "explains": [],
                          "cite": [c for c in cites if c in seen]})
            seen.add(item_id)
            if isinstance(it.get("id"), str):
                original_ids[it["id"]] = item_id
        links = [{"from": c, "to": it["id"], "rel": "引用"} for it in items for c in it["cite"]]
        graph["segments"].append({"sec": sec, "bars": bars[sec], "relation": segment.get("relation"),
                                  "items": items, "because": links})
    V.tidy(graph)
    rows = json.loads((V.OUT / f"{w}_{ref}.json").read_text(encoding="utf-8"))["rows"]
    with (V.OUT / f"{w}_{tag}.json").open("w", encoding="utf-8") as handle:
        json.dump({"graph": graph, "rows": rows, "base": note}, handle, ensure_ascii=False, indent=1)
    (V.OUT / f"{w}_{tag}.md").write_text(
        f"# {'Op.60' if w == 'op60' else 'Op.61'}｜线（{tag}）\n\n" + V.view(graph), encoding="utf-8")
    print(w, tag, "字数", sum(len(i["text"]) for s in graph["segments"] for i in s["items"]),
          "条目", sum(len(s["items"]) for s in graph["segments"]),
          "关系", [s["relation"] for s in graph["segments"]], flush=True)


def run_work(spec, w, tag, sample=None, ref="m6w", context=None):
    token(tag, "TAG")
    if sample is not None and (not isinstance(sample, str) or not re.fullmatch(r"[0-9]+", sample)):
        raise ValueError("SAMPLE must be a nonnegative integer")
    builtins, graph = context if context is not None else work_context(w, ref)
    outputs, pending, running = {}, set(spec["_steps"]), {}
    suffix = f"_s{sample}" if sample is not None else ""
    output_tag = tag + (f"s{sample}" if sample is not None else "")
    with ThreadPoolExecutor(max_workers=len(pending)) as executor:
        while pending or running:
            for sid in spec["_steps"]:
                if sid in pending and spec["_deps"][sid] <= outputs.keys():
                    message = render_step(spec, sid, builtins, outputs)
                    rid = f"sc{tag}_{w}_{sid}{suffix}"
                    future = executor.submit(call, rid, message, spec["_steps"][sid]["model"], spec["name"])
                    running[future] = sid
                    pending.remove(sid)
            if not running:
                raise RuntimeError(f"{w}: no runnable steps")
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            try:
                for future in finished:
                    outputs[running.pop(future)] = future.result()
            except Exception:
                for future in running:
                    future.cancel()
                raise
    save(w, graph, outputs[spec["final"]], spec["note"], output_tag, ref)
    return outputs


def run(spec, tag, sample=None, ref="m6w"):
    token(tag, "TAG")
    if sample is not None and not re.fullmatch(r"[0-9]+", sample):
        raise ValueError("SAMPLE must be a nonnegative integer")
    # Read both works before submitting anything; no scheduling or transport overrides.
    contexts = {w: work_context(w, ref) for w in ("op60", "op61")}
    errors, results = [], {}
    with ThreadPoolExecutor(max_workers=2) as executor:
        jobs = {executor.submit(run_work, spec, w, tag, sample, ref, ctx): w for w, ctx in contexts.items()}
        for future in as_completed(jobs):
            w = jobs[future]
            try:
                results[w] = future.result()
            except Exception as exc:
                errors.append(f"{w}: {exc}")
    if errors:
        raise RuntimeError("; ".join(errors))
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("run", help="run op60 and op61 concurrently")
    command.add_argument("spec", help="JSON description path, relative to current directory or absolute")
    command.add_argument("tag", help="output version tag")
    args = parser.parse_args(argv)
    try:
        run(load_spec(args.spec), args.tag, os.environ.get("SAMPLE"), os.environ.get("REF", "m6w"))
    except Exception as exc:
        parser.exit(1, f"pipe: {exc}\n")


if __name__ == "__main__":
    main()
