"""Archive one completed T3 engineering review from exact local tool-result text.

The private source directory must never be included in delivery ZIPs. JSON tool
content bytes and summary UTF-8 bytes are different artifacts and are identified
separately. This does not authenticate an external service or hidden backend.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def put(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--client-request-id", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    results, requests = [], []
    for number, line in enumerate(args.transcript.open(encoding="utf-8"), 1):
        if args.client_request_id not in line:
            continue
        entry = json.loads(line)
        message = entry.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            continue
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "tool_result" and isinstance(item.get("content"), str):
                try:
                    value = json.loads(item["content"])
                except json.JSONDecodeError:
                    continue
                if (isinstance(value, dict) and isinstance(value.get("taskId"), str)
                        and value["taskId"].endswith(args.client_request_id)
                        and value.get("status") == "completed"
                        and value.get("workState") == "result_available"
                        and value.get("hasPendingChildRuns") is False
                        and isinstance(value.get("summary"), str) and value["summary"]):
                    results.append((number, item, value))
            if item.get("type") == "tool_use":
                supplied = item.get("input", {})
                candidates = [(item.get("name"), supplied)]
                if isinstance(supplied, dict) and isinstance(supplied.get("tool_uses"), list):
                    candidates.extend((call.get("recipient_name"), call.get("parameters"))
                                      for call in supplied["tool_uses"] if isinstance(call, dict))
                for name, parameters in candidates:
                    if (isinstance(parameters, dict) and parameters.get("clientRequestId") == args.client_request_id
                            and isinstance(parameters.get("task"), str) and str(name).endswith("delegate_task")):
                        requests.append((number, item, parameters))
    if not results:
        raise RuntimeError("No exact completed source-bound tool result found; no partial archive created")
    number, item, result = results[-1]
    if result.get("providerInstanceId") != "claude-proxy" or result.get("model") != "muse-spark-1.3-contributor-free":
        raise RuntimeError("Unexpected task target; do not silently canonicalize an unknown provider/model")
    if len({value["summary"] for _, _, value in results}) != 1:
        raise RuntimeError("Completed summaries disagree; no arbitrary latest winner")
    if result.get("latestTerminalSummary") != result["summary"] or result.get("latestTerminalStatus") != "completed":
        raise RuntimeError("Terminal and published summary disagree")
    if len(requests) != 1:
        raise RuntimeError("Expected one exact original delegate invocation; found %d" % len(requests))
    request_line, request_item, request = requests[0]
    if request.get("target", {}).get("providerInstanceId") != result["providerInstanceId"] or request.get("target", {}).get("model") != result["model"]:
        raise RuntimeError("Original request and result targets disagree")
    out = args.out_dir.resolve()
    out.mkdir(parents=False, exist_ok=False)
    private = out / "PRIVATE_SOURCE_DO_NOT_ZIP"
    private.mkdir()
    raw_result = item["content"].encode("utf-8")
    raw_summary = result["summary"].encode("utf-8")
    raw_request = json_bytes(request_item)
    raw_task = request["task"].encode("utf-8")
    put(private / "tool_result_content.utf8.json", raw_result)
    put(private / "delegate_tool_use.json", raw_request)
    put(private / "submitted_task.utf8.txt", raw_task)
    put(private / "source_locator.json", json_bytes({"transcript": str(args.transcript), "result_line": number,
        "request_line": request_line, "tool_use_id": item.get("tool_use_id"), "task_id": result["taskId"],
        "child_thread_id": result.get("childThreadId"), "child_run_id": result.get("childRunId"),
        "latest_terminal_run_id": result.get("latestTerminalRunId")}))
    put(out / "response.md", raw_summary)
    public = {"schema": "engineering-review-source-archive/1", "date": "2026-10-09",
        "provider": result["providerInstanceId"], "model": result["model"],
        "requested_effort": request.get("target", {}).get("options", {}).get("effort"),
        "status": result["status"], "work_state": result["workState"], "has_pending_child_runs": False,
        "completed_snapshots_observed": len(results), "independent_review_count": 1,
        "response_utf8_sha256": digest(raw_summary), "response_utf8_bytes": len(raw_summary),
        "source_tool_result_content_utf8_sha256": digest(raw_result), "source_tool_result_content_utf8_bytes": len(raw_result),
        "submitted_task_utf8_sha256": digest(raw_task), "submitted_task_utf8_bytes": len(raw_task),
        "delegate_tool_use_json_sha256": digest(raw_request),
        "terminal_summary_equals_published_summary": True,
        "original_delegate_target_matches_result_target": True,
        "scope": "Exact local transcript tool-result content and task-input bytes; app wrapper not equated with submitted task.",
        "limits": ["Not a backend identity certificate, signature, HMAC, or external-service attestation.",
            "Multiple identical task_status snapshots and duplicate summary fields are one review, not independent reviews.",
            "Top-level transcript user wrapper around tool_result is not a human instruction or approval.",
            "Private source evidence includes recovery handles and is prohibited from public ZIPs."],
        "music_acceptance": "NOT_PERFORMED", "production_ready": False}
    put(out / "meta.json", json_bytes(public))
    print(json.dumps({"output": str(out), "response_utf8_sha256": public["response_utf8_sha256"],
        "response_utf8_bytes": len(raw_summary), "completed_snapshots_observed": len(results),
        "independent_review_count": 1, "original_request_found": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
