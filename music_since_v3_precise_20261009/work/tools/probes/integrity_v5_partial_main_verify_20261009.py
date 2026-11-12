"""Verify the partial v5 handoff locally; synthetic fixtures only, no real CLI."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))
import execution_integrity_v5 as I
import gpt2_adapter_v5 as A
import runner_v5 as R
import experiment_calls_v5 as E


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fixture_module():
    original = (TOOLS / "tests/test_execution_integrity_v4.py").read_bytes()
    text = original.decode("utf-8")
    for name in ("execution_integrity", "gpt2_adapter", "runner", "experiment_calls"):
        text = text.replace(name + "_v4", name + "_v5")
    text = text.replace('"inflight_v4"', '"inflight_v5"')
    text = text.replace('"model": "gpt-5-6-thinking", "response_sha256":',
                        '"model": "gpt-5-6-thinking", "thinking_effort": "max", "response_sha256":')
    module = types.ModuleType("v5_inherited_mock_fixture")
    module.__file__ = str(TOOLS / "tests/test_execution_integrity_v4.py")
    exec(compile(text, module.__file__, "exec"), module.__dict__)
    return module, original, text.encode("utf-8")


def record_probe(name, callback, **scope):
    try:
        details = callback()
        return {"check": name, "observed": details, **scope}
    except Exception as exc:
        return {"check": name, "error_type": type(exc).__name__,
                "error": I.safe_text(str(exc)), **scope}


def adapter_probe(T, kind):
    fixture = T.AdapterTests()
    fixture.setUp()
    try:
        first = fixture.call(sampling_key="shared")
        original_meta = (fixture.out / "meta/one.json").read_bytes()
        if kind == "legacy_seal":
            for folder in ("cache", "pending", "meta"):
                for path in (fixture.out / folder).glob("*.json"):
                    path.unlink()
            # A legacy-shaped seal is not a valid ownership record for v5.
            legacy = {"schema": "20261009.v4", "job_id": "one",
                      "meta_sha256": sha(original_meta),
                      "prompt_sha256": I.sha_file(fixture.out / "prompts/one.txt"),
                      "output_sha256": I.sha_file(fixture.out / "outputs/one.md")}
            (fixture.out / "finalized/one.json").write_text(json.dumps(legacy), encoding="utf-8")
        error = None
        second = None
        try:
            second = fixture.call("two", sampling_key="shared", use_cache=(kind != "cache_false"))
        except Exception as exc:
            error = {"type": type(exc).__name__, "message": I.safe_text(str(exc))}
        cache = [I.strict_json(path.read_bytes().decode("utf-8"))
                 for path in (fixture.out / "cache").glob("*.json")]
        return {"first_status": first["status"], "second_status": (second or {}).get("status"),
                "error": error, "mock_process_calls": fixture.process.call_count,
                "cache_sources": [row.get("source_job_id") for row in cache],
                "second_meta_written": (fixture.out / "meta/two.json").exists(),
                "second_seal_written": (fixture.out / "finalized/two.json").exists()}
    finally:
        fixture.doCleanups()


def wrapper_probe(T, kind):
    fixture = T.RunnerFixture()
    fixture.setUp()
    try:
        kwargs = {"max_attempts": 2}
        parser_calls = 0

        def parser(text):
            nonlocal parser_calls
            parser_calls += 1
            return (None, "synthetic complete-response parse failure") if parser_calls == 1 else ({"value": text}, None)

        if kind == "explicit_new_sample":
            kwargs.update(allow_new_sample_on_parse_failure=True,
                          new_sample_reason="explicit synthetic resampling authorization",
                          new_sample_prompt="另一个冻结输入", new_sampling_key="declared-sample-two")
        original = R.run_job
        runner_calls = 0

        def scripted(directory, job, timeout=3600):
            nonlocal runner_calls
            runner_calls += 1
            if kind == "pre_submit" and runner_calls == 1:
                return {"status": "failed", "error": "synthetic proven pre_submit failure",
                        "retry_safe": True, "queue_stop": False, "attempts": 1}
            return original(directory, job, timeout)

        with mock.patch.object(R, "run_job", side_effect=scripted):
            result = E.call(fixture.root / kind, "why", "MOCK_ONLY", "luna_noweb", "冻结输入",
                            parser, [2], "v5-partial-probe", **kwargs)
        return {"parse_ok": result["parse_ok"], "new_sample_taken": result["new_sample_taken"],
                "stop_reason": result.get("stop_reason"), "runner_calls": runner_calls,
                "mock_process_calls": fixture.process.call_count, "parser_calls": parser_calls}
    finally:
        fixture.doCleanups()


def status_probe(T):
    events = [{"type": "item.completed", "item": {"id": "reasoning-extra", "type": "reasoning",
                                                   "status": "in_progress"}}]
    try:
        I.parse_codex(T.codex(events).decode("utf-8"))
        return {"accepted_incomplete_terminal_item": True}
    except ValueError:
        return {"accepted_incomplete_terminal_item": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    destination = Path(args.out_dir)
    destination.mkdir(parents=True, exist_ok=False)
    protected = [TOOLS / (name + ".py") for name in
                 ("execution_integrity_v4", "gpt2_adapter_v4", "runner_v4", "experiment_calls_v4",
                  "execution_integrity_v5", "gpt2_adapter_v5", "runner_v5", "experiment_calls_v5")]
    protected.append(TOOLS / "tests/test_execution_integrity_v4.py")
    before = {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in protected}
    T, fixture_raw, transformed_raw = fixture_module()
    stdout, stderr = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        suite = unittest.defaultTestLoader.loadTestsFromModule(T)
        result = unittest.TextTestRunner(stream=stderr, verbosity=2).run(suite)
        rows = [record_probe("codex_completed_item_in_progress", lambda: status_probe(T)),
                record_probe("explicit_new_sample", lambda: wrapper_probe(T, "explicit_new_sample")),
                record_probe("safe_pre_submit_retry", lambda: wrapper_probe(T, "pre_submit")),
                record_probe("legacy_seal_ownership", lambda: adapter_probe(T, "legacy_seal")),
                record_probe("use_cache_false_source_preserved", lambda: adapter_probe(T, "cache_false"))]
    after = {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in protected}
    for filename, text in (("inherited_tests.stdout.txt", stdout.getvalue()),
                           ("inherited_tests.stderr.txt", stderr.getvalue())):
        with (destination / filename).open("x", encoding="utf-8", newline="") as stream:
            stream.write(text)
    report = {"schema": "partial-v5-main-offline-verification/1", "date": "2026-10-09",
              "source_hashes_before": before, "source_hashes_after": after,
              "source_bytes_unchanged": before == after,
              "inherited_fixture": {"original_sha256": sha(fixture_raw),
                                    "in_memory_transformed_sha256": sha(transformed_raw),
                                    "changes": ["v4 module imports and child-process module to v5",
                                                "inflight_v4 ticket expectation to inflight_v5",
                                                "synthetic GPT2 payload includes thinking_effort=max"],
                                    "disk_test_modified": False},
              "inherited_tests": {"run": result.testsRun, "failures": len(result.failures),
                                  "errors": len(result.errors), "skipped": len(result.skipped),
                                  "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)},
              "probes": rows, "real_model_submissions": 0, "network_calls": 0,
              "music_acceptance": "NOT_PERFORMED", "production_ready": False,
              "limits": "Synthetic fixtures/temp-only. No real CLI/backend attestation. Old holds/gates/production untouched."}
    with (destination / "report.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps({"report": str(destination / "report.json"),
                      "inherited_tests": report["inherited_tests"], "probes": rows,
                      "source_bytes_unchanged": before == after, "real_model_submissions": 0},
                     ensure_ascii=False, allow_nan=False))
    if before != after:
        raise SystemExit("source changed during offline verification")


if __name__ == "__main__":
    main()
