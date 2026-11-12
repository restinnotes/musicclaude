"""Read-only mapping and targeted residual verification, not a repeat suite."""
import argparse
import ast
import difflib
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def functions(path, tests):
    text = path.read_text(encoding="utf-8")
    rows = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and not tests:
            rows[node.name] = ast.get_source_segment(text, node)
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_") == tests:
                    rows[node.name + "." + item.name] = ast.get_source_segment(text, item)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out_dir.resolve()
    if out.exists():
        raise RuntimeError("Refuse existing output directory")
    before = {path.relative_to(root).as_posix(): sha(path.read_bytes()) for path in [
        root / "tools/tests/test_execution_integrity_v4.py", root / "tools/tests/test_execution_integrity_v7.py",
        root / "tools/tests/test_execution_integrity_v8.py", root / "tools/execution_integrity_v8.py",
        root / "notes/research/integrity_v8_main_verify_20261009_r1/report.json"]}
    def audit(event, values):
        if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "socket.connect", "socket.getaddrinfo", "socket.bind"):
            raise RuntimeError("Residual probe blocks processes and network")
        if event == "open":
            path, mode, flags = values
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            if writing and not isinstance(path, int) and not Path(path).resolve().is_relative_to(out):
                raise RuntimeError("Residual probe blocks historical writes")
    sys.addaudithook(audit)
    report = json.loads((root / "notes/research/integrity_v8_main_verify_20261009_r1/report.json").read_bytes())
    mapping = report["assertion_mapping"]
    mapping_checks = []
    for group in mapping["mappings"]:
        mapping_checks.append({"source": group["source"], "mapped_methods": len(group["mapping"]),
            "missing_assertions": sum(len(row["old_assertions_not_retained"]) for row in group["mapping"]),
            "changed_test_bodies": [row["test"] for row in group["mapping"] if not row["body_same_after_namespace"]]})
    diffs = []
    for tests in (True, False):
        new = functions(root / "tools/tests/test_execution_integrity_v8.py", tests)
        for version in ("v4", "v7"):
            old = functions(root / ("tools/tests/test_execution_integrity_" + version + ".py"), tests)
            for name, original in old.items():
                normalized = original.replace("execution_integrity_" + version, "execution_integrity_v8").replace("inflight_" + version, "inflight_v8")
                current = new.get(name)
                if current is None or ast.dump(ast.parse(normalized), include_attributes=False) != ast.dump(ast.parse(current), include_attributes=False):
                    diffs.append({"kind": "test" if tests else "helper", "source": version, "name": name,
                        "missing": current is None, "diff": "\n".join(difflib.unified_diff(normalized.splitlines(), (current or "").splitlines(), lineterm=""))})
    sys.path.insert(0, str(root / "tools"))
    import execution_integrity_v8 as integrity
    prefix = [{"type": "thread.started", "thread_id": "MOCK_ONLY"}, {"type": "turn.started"}]
    started = {"type": "item.started", "item": {"id": "r", "type": "reasoning", "status": "in_progress"}}
    end = [{"type": "item.completed", "item": {"id": "r", "type": "reasoning", "status": "completed"}},
        {"type": "item.completed", "item": {"id": "a", "type": "agent_message", "text": "MOCK_ONLY terminal body", "status": "completed"}},
        {"type": "turn.completed", "status": "completed", "usage": {}}]
    rows = []
    for name, events in (("duplicate_started_complete_terminal", prefix + [started, started] + end),
        ("duplicate_started_incomplete_reasoning", prefix + [started, started] + end[1:]),
        ("duplicate_started_no_turn_terminal", prefix + [started, started] + end[:-1])):
        payload = ("\n".join(json.dumps(row, ensure_ascii=False) for row in events) + "\n").encode("utf-8")
        try:
            parsed = integrity.parse_codex(payload)
            rows.append({"case": name, "accepted": True, "parsed": parsed, "events_sha256": sha(payload)})
        except ValueError as exc:
            rows.append({"case": name, "accepted": False, "exception": str(exc), "events_sha256": sha(payload)})
    proxy = "http://proxy.invalid:8080/%40token"
    parts = urlsplit(proxy)
    first = integrity.environment_identity({"HTTP_PROXY": proxy})
    second = integrity.environment_identity({"HTTP_PROXY": "http://proxy.invalid:8080/%40different"})
    after = {path: sha((root / path).read_bytes()) for path in before}
    result = {"schema": "v8-targeted-main-disposition/1", "date": "2026-10-09", "probe_sha256": sha(Path(__file__).read_bytes()),
        "assertion_mapping": mapping_checks, "semantic_diffs": diffs, "duplicate_started": rows,
        "duplicate_started_disposition": "Duplicate start is accepted with a genuine completed item/body/turn; missing pending completion or turn terminal stays rejected. Low-risk tightening residual, not fabricated successful terminal.",
        "proxy_example": {"url": proxy, "username": parts.username, "password": parts.password, "path": parts.path,
            "query": parts.query, "is_userinfo_example": parts.username is not None,
            "value_changed_identity": first != second,
            "disposition": "The review example encodes @ in URL path, not userinfo. Do not infer a userinfo credential bypass from it. Broader URI/private config behavior remains unverified."},
        "protected_unchanged": before == after, "real_model_submissions": 0, "model_cli_invocations": 0,
        "music_acceptance": "NOT_PERFORMED", "production_ready": False,
        "limit": "Local finite parser/mapping checks only, no real protocol/service/backend validation."}
    out.mkdir()
    with (out / "report.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"output": str(out), "mapping": mapping_checks, "diff_count": len(diffs),
        "duplicate_started": [{"case": row["case"], "accepted": row["accepted"]} for row in rows],
        "proxy_is_userinfo": parts.username is not None, "protected_unchanged": before == after}, ensure_ascii=False))


if __name__ == "__main__":
    main()
