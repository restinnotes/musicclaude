"""v4 新审查问题的主会话离线复现；临时 mock，不启动模型/网络。"""
import argparse
import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import execution_integrity_v4 as I
import gpt2_adapter_v4 as A
import experiment_calls_v4 as E

spec = importlib.util.spec_from_file_location("v4_fixture", TOOLS / "tests/test_execution_integrity_v4.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)


def check(run):
    rows = []
    for name, build in (
        ("codex_unknown_item_status", lambda: T.codex([{"type": "item.completed", "item": {
            "id": "other", "type": "reasoning", "status": "mystery_terminal"}}]).decode()),
        ("codex_conflicting_turn_status", lambda: T.codex().decode().replace('"usage": {}', '"usage": {}, "status": "failed"')),
        ("opencode_conflicting_finish_status", lambda: T.opencode().decode().replace('"reason": "stop"', '"reason": "stop", "status": "failed"'))):
        parser = I.parse_opencode if name.startswith("opencode") else I.parse_codex
        rows.append({"check": name, "reproduced": parser(build())[0] == "完整离线回答",
                     "scope": "synthetic local event, not observed real protocol"})
    with tempfile.TemporaryDirectory() as temp, contextlib.ExitStack() as stack:
        root = Path(temp)
        stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        stack.enter_context(mock.patch.object(I, "REAL_EXECUTION_APPROVED", True))
        stack.enter_context(mock.patch.object(A, "HOLD_FILE", root / "slots/gpt2web/hold.json"))
        stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **k: contextlib.nullcontext()))
        stack.enter_context(mock.patch.object(A, "producer_identity", return_value={"route": "MOCK_ONLY",
            "cli_sha256": "1" * 64, "cli_version": "fixture", "cli_source": {"missing": False}}))
        process = stack.enter_context(mock.patch.object(A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, T.payload(), b"")))
        out = root / "orphan"
        first = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="first", out_dir=out, sampling_key="shared")
        for folder in ("cache", "pending", "meta"):
            for path in (out / folder).glob("*.json"):
                path.unlink()
        second = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="second", out_dir=out, sampling_key="shared")
        rows.append({"check": "orphan_finalized_same_sample", "reproduced": first["status"] == second["status"] == "ok"
            and process.call_count == 2 and (out / "finalized/first.json").is_file(), "mock_process_calls": process.call_count,
            "scope": "temp ledger removal + retained completion seal; no real repeat"})
        process.return_value = subprocess.CompletedProcess([], 0, T.payload(metadata={"thinking_effort": "low"}), b"")
        low = A.call_web_gpt("gpt56w", "冻结输入", run_id="MOCK_ONLY", job_id="low", out_dir=root / "effort")
        rows.append({"check": "requested_max_returned_low", "reproduced": low["status"] == "ok", "scope": "local return metadata inconsistency, not proof of remote effort"})
    for key in ("HTTPS_PROXY", "GPT2AGENT_TURN_TIMEOUT_SECONDS", "GPT2AGENT_MAX_ACTIVE_TURNS"):
        before = {"PATH": "MOCK_ONLY", key: "1"}
        after = {"PATH": "MOCK_ONLY", key: "2"}
        rows.append({"check": "unbound_environment:" + key, "reproduced": I.environment_identity(before) == I.environment_identity(after),
                     "scope": "synthetic env; actual native worker source path separately inspected"})
    fixture = T.RunnerFixture()
    fixture.setUp()
    try:
        results = iter(((None, "complete body failed parse"), ({"parsed": True}, None)))
        parsed = E.call(fixture.root / "wrapper", "why", "MOCK_ONLY", "luna_noweb", "冻结输入",
                        lambda text: next(results), [2], "fixture", max_attempts=2)
        rows.append({"check": "wrapper_complete_then_parse_failure", "reproduced": fixture.process.call_count == 2,
                     "mock_process_calls": fixture.process.call_count, "parse_ok": parsed["parse_ok"],
                     "scope": "policy ambiguity: original engineering brief permits explicit new sample after complete parse failure; current wrapper does so automatically"})
    finally:
        fixture.doCleanups()
    return {"schema": "v4-r1-main-reproduction/1", "date": "2026-10-09", "real_model_submissions": 0,
            "rows": rows, "all_reproduced": all(row["reproduced"] for row in rows),
            "limits": "No real CLI/model/network. Reproduction is not music acceptance or route health. Gate and old hold untouched."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = check(args)
    with Path(args.output).open("x", encoding="utf-8", newline="") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
    if not result["all_reproduced"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
