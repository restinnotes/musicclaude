"""Main-session offline verification; never invoke a provider or a model CLI."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def save(path: Path, value) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_inventory(path: Path) -> dict[str, str]:
    source = path.read_text(encoding="utf-8")
    return {node.name: ast.get_source_segment(source, node)
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")}


def protected_snapshot(root: Path) -> dict:
    relatives = [
        "runs/run139_e7_flash_diag/go.py", "runs/run141_thread_resume_r3/go.py",
        "runs/run142_e7_flash_diag_r4/go.py", "runs/run142_e7_flash_diag_r4/README.md",
        "runs/run142_e7_flash_diag_r4/manifest.json", "runs/run143_thread_resume_r4/go.py",
        "runs/run143_thread_resume_r4/README.md", "runs/run143_thread_resume_r4/manifest.json",
        "tools/tests/test_run139_e7_flash_diag_r3.py", "tools/tests/test_run141_thread_resume_r3.py",
        "tools/tests/test_run142_e7_flash_diag_r4.py", "tools/tests/test_run143_thread_resume_r4.py",
        "runs/run130_thread_e6/beads_clean.md", "runs/run130_thread_e6/steps.json",
        "runs/run124_render/surface__B__gpt56w__op60.md",
        "prompts/versions/WHY_GATE_v4.txt", "prompts/tooling/MECH_v1.txt",
        "prompts/tooling/MECH_AUDIT_v0.txt", "prompts/versions/E7_SURFACE_v0.txt",
        "prompts/tooling/E7_COMPARE_v0.txt", "prompts/versions/C7_STEP_v2.txt",
        "prompts/versions/C7_STEP_v3.txt", "prompts/versions/CENTER_v0.txt",
        "prompts/tooling/THREAD_IDENT_v0.txt", "prompts/tooling/THREAD_COMPARE_v0.txt",
        "reference/PRODUCT_CONSTITUTION_V2.md",
        "notes/chat_findings_20261005/music_pipeline_chat_findings_20261005/06_ACCEPTANCE_CRITERIA.md",
    ]
    snapshot = {}
    for relative in relatives:
        path = root / relative
        if path.is_file():
            raw = path.read_bytes()
            snapshot[relative] = {"bytes": len(raw), "sha256": digest(raw)}
        else:
            snapshot[relative] = {"missing": True}
    for run in ("run142_e7_flash_diag_r4", "run143_thread_resume_r4"):
        folder = root / "runs" / run
        snapshot["file_inventory:" + run] = sorted(
            path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_file())
    return snapshot


def challenges(root: Path) -> list[dict]:
    t142 = load(root / "tools/tests/test_run142_e7_flash_diag_r4.py", "main_r2_test142")
    g142 = t142.load_go("main_r2_go142")
    g143 = load(root / "runs/run143_thread_resume_r4/go.py", "main_r2_go143")
    rows = []
    with tempfile.TemporaryDirectory(prefix="main_r2_identity_") as temp:
        folder = Path(temp) / "mock"
        folder.mkdir()
        caller = t142.MockCaller()
        pipeline = g142.Pipeline(folder, caller)
        pipeline.data = g142._freeze_inputs(root)
        prompt = "MOCK_ONLY identity-binding fixture"
        key = ["run130:gpt56w", 2]
        first = pipeline.execute("why", key, "gflash", prompt, "WHY_GATE_v4", g142.parse_why)
        for label, model, version in (("changed_requested_model", "luna_noweb", "WHY_GATE_v4"),
                                      ("changed_prompt_version", "gflash", "different_version")):
            count_before = caller.submissions
            try:
                value = pipeline.execute("why", key, model, prompt, version, g142.parse_why)
                rows.append({"check": "run142_" + label, "accepted": True,
                             "resumed": value["resumed"], "prior_model": "gflash",
                             "requested_model_now": model, "requested_version_now": version,
                             "new_mock_submissions": caller.submissions - count_before,
                             "result_attempt": value["attempt"],
                             "finding": "current caller identity is not checked against the reused record"})
            except Exception as exc:
                rows.append({"check": "run142_" + label, "accepted": False,
                             "exception": type(exc).__name__, "error": str(exc)})
        rows.append({"check": "run142_transport_retry_executor_interface",
                     "parameters": list(inspect.signature(pipeline.execute).parameters),
                     "policy_function_present": callable(g142.transport_retry_allowed),
                     "policy_used_in_execute": "transport_retry_allowed" in inspect.getsource(g142.Pipeline.execute),
                     "scope": "static interface and integration check; not a real transport test"})

    with tempfile.TemporaryDirectory(prefix="main_r2_parsefail_") as temp:
        evidence = Path(temp) / "evidence"
        fingerprint = g143.build_fingerprint(root)
        slot = {"stage": "step", "chain_id": "v2_gpt56w", "version": "v2",
                "model_key": "gpt56w", "k": 1}
        task = {"slot": slot, "prompt": "MOCK_ONLY failed-output fixture",
                "template_sha256": fingerprint["templates"]["step_v2"],
                "source_sha256": "MOCK_ONLY source"}
        counts = {"mock_submissions": 0, "reused": 0}
        hashes, index, errors = {}, {}, []
        original = g143._mock_response
        try:
            g143._mock_response = lambda task: "MOCK_ONLY invalid completed JSON"
            for _ in range(2):
                try:
                    g143.execute_mock_task(evidence, task, fingerprint, hashes, counts, index)
                except Exception as exc:
                    errors.append({"exception": type(exc).__name__, "error": str(exc)})
        finally:
            g143._mock_response = original
        rows.append({"check": "run143_completed_parse_failure_rerun",
                     "mock_submissions_after_two_calls": counts["mock_submissions"],
                     "metadata_index_records": sum(len(values) for values in index.values()),
                     "saved_artifact_files": sorted(path.relative_to(evidence).as_posix()
                                                     for path in evidence.rglob("*") if path.is_file()),
                     "errors": errors,
                     "finding": "parse failure is raised before immutable output/meta are persisted; rerun resubmits the same slot"})
        rows.append({"check": "run143_explicit_new_sample_interface",
                     "parameters": list(inspect.signature(g143.execute_mock_task).parameters),
                     "has_explicit_resample_option": "allow_new_sample_on_parse_failure" in
                         inspect.signature(g143.execute_mock_task).parameters,
                     "scope": "interface check only; no new sample requested"})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    args.out_dir.mkdir(parents=False, exist_ok=False)
    before = protected_snapshot(root)
    save(args.out_dir / "protected_before.json", before)
    report = {"schema": "run142-143-main-offline-verification/2", "date": "2026-10-09",
              "commands": [], "music_acceptance": "NOT_PERFORMED", "production_ready": False,
              "real_gate": "not changed", "two_w_hold": "not changed",
              "real_model_submissions": 0, "model_cli_invocations": 0,
              "limits": ["Only Python offline suites and injected local mock fixtures run.",
                         "Hashes are local consistency evidence, not backend authentication.",
                         "Passing existing suites does not close uncovered requirements."]}
    commands = [
        ("run142_tests", ["tools/tests/test_run142_e7_flash_diag_r4.py"], 0),
        ("run143_tests", ["tools/tests/test_run143_thread_resume_r4.py"], 0),
        ("run142_real", ["runs/run142_e7_flash_diag_r4/go.py", "--real"], 3),
        ("run143_strict", ["runs/run143_thread_resume_r4/go.py", "--strict"], 0),
        ("run143_real", ["runs/run143_thread_resume_r4/go.py", "--real"], 3),
    ]
    for label, parts, expected_rc in commands:
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(root / parts[0]), *parts[1:]]
        start = time.monotonic()
        try:
            completed = subprocess.run(argv, cwd=root.parent.parent, capture_output=True, timeout=180)
            stdout, stderr, rc = completed.stdout, completed.stderr, completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, rc = exc.stdout or b"", exc.stderr or b"", None
            timed_out = True
        for stream_name, raw in (("stdout", stdout), ("stderr", stderr)):
            with (args.out_dir / (label + "." + stream_name + ".txt")).open("xb") as stream:
                stream.write(raw)
        report["commands"].append({"label": label, "argv": argv, "returncode": rc,
                                  "expected_returncode": expected_rc, "timed_out": timed_out,
                                  "elapsed_seconds": round(time.monotonic() - start, 3),
                                  "stdout_bytes": len(stdout), "stderr_bytes": len(stderr),
                                  "stdout_sha256": digest(stdout), "stderr_sha256": digest(stderr),
                                  "expected_exit_observed": rc == expected_rc})

    coverage = {}
    renames = {"test_muse_return_needs_real_transport_schema_and_exact_quotes":
               "test_muse_raw_return_is_unverified_and_actual_entry_needs_trusted_archive_receipt",
               "test_strict_preflight_is_pending_without_v4_and_writes_nothing":
               "test_strict_preflight_is_pending_without_v4_acceptance_and_writes_nothing"}
    for old, new in (("test_run139_e7_flash_diag_r3.py", "test_run142_e7_flash_diag_r4.py"),
                     ("test_run141_thread_resume_r3.py", "test_run143_thread_resume_r4.py")):
        old_tests, new_tests = test_inventory(root / "tools/tests" / old), test_inventory(root / "tools/tests" / new)
        matches = [{"old": name, "new": name if name in new_tests else renames.get(name),
                    "name_present": name in new_tests or renames.get(name) in new_tests}
                   for name in sorted(old_tests)]
        coverage[new] = {"old_count": len(old_tests), "new_count": len(new_tests), "matches": matches,
                         "scope": "AST name inventory only. Main also read original assertions; names alone are not proof."}
    report["test_inventory"] = coverage
    try:
        report["challenges"] = challenges(root)
    except Exception as exc:
        report["challenge_execution_error"] = {"type": type(exc).__name__, "error": str(exc)}
    after = protected_snapshot(root)
    save(args.out_dir / "protected_after.json", after)
    report["protected_files_unchanged"] = before == after
    report["changed_protected_paths"] = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
    report["main_disposition"] = "NOT_ACCEPTED_PENDING_INDEPENDENT_REVIEW_AND_UNCOVERED_REQUIREMENTS"
    save(args.out_dir / "report.json", report)
    print(json.dumps({"commands": [{"label": row["label"], "rc": row["returncode"]} for row in report["commands"]],
                      "protected_unchanged": report["protected_files_unchanged"],
                      "challenges": report.get("challenges", []),
                      "challenge_error": report.get("challenge_execution_error"),
                      "disposition": report["main_disposition"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
