"""只用隔离桩复现终态门、正文保护误判与缓存重提；不运行真实模型。"""
import contextlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import gpt2_adapter as A
import runner as R


def ndjson(*rows):
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode("utf-8")


def runner_case(root, name, model, stdout, stderr=b"", error=None):
    directory = root / name
    job = {"job_id": "probe", "model_key": model, "prompt": "冻结离线输入", "max_attempts": 1}
    patches = [mock.patch.object(R, "_SLOT_DIR", root / (name + "_slots")),
               mock.patch.object(R, "_GlobalSlot", side_effect=lambda *a, **kw: contextlib.nullcontext()),
               mock.patch.object(R, "_ensure_init"),
               mock.patch.dict(R._STATE, {"env": {}, "init": True}),
               mock.patch.object(R, "_build_task", return_value=(["offline_stub"], "raw", "offline_stub"))]
    with contextlib.ExitStack() as stack:
        for patch in patches:
            stack.enter_context(patch)
        process = stack.enter_context(mock.patch.object(R, "run_process", side_effect=error) if error
                    else mock.patch.object(R, "run_process", return_value=subprocess.CompletedProcess([], 0, stdout, stderr)))
        meta = R.run_job(directory, job)
        return {"status": meta["status"], "queue_stop": meta.get("queue_stop"),
                "error": meta.get("error"), "stub_submissions": process.call_count,
                "output_chars": meta["output_chars"]}


def main():
    with tempfile.TemporaryDirectory(prefix="music_terminal_probe_") as tmp:
        root = Path(tmp)
        results = {}
        results["codex_without_turn_completed"] = runner_case(root, "codex", "luna_noweb", ndjson(
            {"type": "item.completed", "item": {"type": "agent_message", "text": "尚未有终态的片段"}}))
        results["opencode_without_terminal"] = runner_case(root, "opencode", "gflash", ndjson(
            {"type": "text", "part": {"type": "text", "text": "尚未有终态的片段"}}))
        results["successful_body_mentions_challenge"] = runner_case(root, "body", "gflash", ndjson(
            {"type": "text", "part": {"type": "text", "text": "文中的 challenge 只是一个普通英文词。"}},
            {"type": "step_finish", "part": {"type": "step-finish", "reason": "stop"}}))
        results["process_exception_without_hold"] = runner_case(root, "exception", "gflash", b"",
                                                                                error=OSError("offline process exception"))
        identity = {"route": "stub", "adapter_version": "probe", "cli": "offline_stub", "cli_version": "probe"}
        answer = "这是离线虚构的赋值示例 secret=NOT_A_REAL_SECRET。"
        payload = json.dumps({"completed": True, "response": answer,
            "metadata": {"server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}}, ensure_ascii=False).encode()
        out = root / "adapter"
        with mock.patch.object(A, "producer_identity", return_value=identity), \
             mock.patch.object(A, "HOLD_FILE", root / "adapter_hold.json"), \
             mock.patch.object(A, "GlobalSlot", side_effect=lambda *a, **kw: contextlib.nullcontext()), \
             mock.patch.object(A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload, b"")) as process:
            first = A.call_web_gpt("gpt56w", "固定输入", run_id="probe", job_id="one", out_dir=out, sampling_key="shared")
            cache = json.loads((out / "cache" / (first["cache_key"] + ".json")).read_bytes())
            second = A.call_web_gpt("gpt56w", "固定输入", run_id="probe", job_id="two", out_dir=out, sampling_key="shared")
            results["redacted_cache_resubmits_same_sample"] = {
                "first_status": first["status"], "second_status": second["status"],
                "cache_body_changed": cache["response"] != answer, "second_cache_hit": second["cache_hit"],
                "stub_submissions": process.call_count}
        assert results["codex_without_turn_completed"]["status"] == "ok"
        assert results["opencode_without_terminal"]["status"] == "ok"
        assert results["successful_body_mentions_challenge"]["queue_stop"] is True
        assert results["process_exception_without_hold"]["queue_stop"] is False
        assert results["redacted_cache_resubmits_same_sample"]["stub_submissions"] == 2
        print(json.dumps({"scope": "offline_only", "real_model_submissions": 0, "results": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
