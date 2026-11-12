"""六项旧 v3 缺口的只读离线复现；临时目录，mock 外部进程，未提交模型。"""
import argparse
import contextlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_integrity_v3 as I
import gpt2_adapter_v3 as A


def run():
    rows = []
    events = [{"type": "thread.started", "thread_id": "FAKE_THREAD"}, {"type": "turn.started"},
              {"type": "turn.cancelled"},
              {"type": "item.completed", "item": {"id": "fake_item", "type": "agent_message", "text": "离线回答"}},
              {"type": "turn.completed", "usage": {}}]
    accepted = I.parse_codex("\n".join(json.dumps(event) for event in events))[0] == "离线回答"
    rows.append({"gap": "unknown_codex_event", "reproduced": accepted, "scope": "synthetic event accepted despite cancellation"})
    fake = "FICTIONAL_HANDLE_20261009"
    rows.append({"gap": "raw_handle_string", "reproduced": fake in I.safe_records(json.dumps({"text": "sessionID=" + fake}))
                 and fake in I.safe_records("thread_id=" + fake), "scope": "fictional handles only"})
    rows.append({"gap": "untrusted_model_evidence_path", "reproduced": I.model_evidence(
        {"debug": {"resolved_model_slugs": ["gpt-5-6-thinking"]}}, "gpt-5-6-thinking")["verdict"] == "match",
        "scope": "local metadata spoof accepted, not evidence of real service mismatch"})
    with tempfile.TemporaryDirectory() as temp, contextlib.ExitStack() as stack:
        root = Path(temp)
        stack.enter_context(mock.patch.dict(os.environ, {"MUSIC_WEB_ROUTE": "gpt2"}))
        stack.enter_context(mock.patch.object(A, "Slot", side_effect=lambda *a, **kw: contextlib.nullcontext()))
        stack.enter_context(mock.patch.object(A, "producer_identity", return_value={"route": "MOCK_ONLY", "cli_version": "test",
            "cli_sha256": "1" * 64, "cli_source": {"missing": False}}))
        process = stack.enter_context(mock.patch.object(A, "RUN_PROCESS"))
        body = json.dumps({"completed": True, "response": "离线回答", "metadata": {
            "server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}, "sessionID": fake, "thread_id": fake}}).encode()
        process.return_value = subprocess.CompletedProcess([], 0, body, b"")
        def call(out, job, **kw):
            return A.call_web_gpt("gpt56w", "离线冻结输入", run_id="MOCK_ONLY", job_id=job, out_dir=out, **kw)
        with mock.patch.object(A, "HOLD_FILE", root / "cache_provider/hold.json"):
            first = call(root / "cache_run", "a", sampling_key="shared")
            rows.append({"gap": "cli_metadata_handle", "reproduced": fake in json.dumps(first.get("cli_metadata")),
                         "scope": "fictional CLI metadata persisted"})
            next((root / "cache_run/cache").glob("*.json")).unlink()
            before = process.call_count
            second = call(root / "cache_run", "b", sampling_key="shared")
            rows.append({"gap": "missing_cache_duplicate_submission", "reproduced": process.call_count == before + 1
                         and second["status"] == "ok", "scope": "mock resubmit for identical sample, no real CLI"})
        hold_file = root / "hold_provider/hold.json"
        process.side_effect = OSError("fictional process failure")
        with mock.patch.object(A, "HOLD_FILE", hold_file), mock.patch.object(I, "write_json", side_effect=OSError("fictional disk failure")):
            try:
                call(root / "hold_run", "a")
            except OSError:
                pass
        # 前一 mock 在 sample_record 写盘前即失败不构成已提交；另单独只让 hold 写失败。
        process.side_effect = OSError("fictional process failure")
        with mock.patch.object(A, "HOLD_FILE", hold_file), mock.patch.object(I, "hold", side_effect=OSError("fictional hold disk failure")):
            try:
                call(root / "hold_run2", "a")
            except OSError:
                pass
        first_count = process.call_count
        process.side_effect = None
        process.return_value = subprocess.CompletedProcess([], 0, body, b"")
        with mock.patch.object(A, "HOLD_FILE", hold_file):
            call(root / "hold_run3", "b")
        rows.append({"gap": "hold_write_failure_allows_next", "reproduced": not hold_file.exists()
                     and process.call_count == first_count + 1, "scope": "mock hold OSError, distinct job proceeded"})
    return {"schema": "v3_gaps.1", "date": "2026-10-09", "real_model_submissions": 0,
            "rows": rows, "all_reproduced": all(row["reproduced"] for row in rows),
            "limits": "synthetic local protocol; no claim of real CLI compatibility, service state or music quality"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run()
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
    if not result["all_reproduced"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
