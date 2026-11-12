"""Inspect run132 local-tool provenance only; never execute archive or tool payloads."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "runs/run132_v2a_gemini_baseline"
LOCAL_TOOLS = {"read", "glob", "execute", "bash", "shell"}
ALLOWED_CONTEXTS = {"reference/PRODUCT_CONSTITUTION_V2.md",
                    "reference/THREAD_USER_PROMPTS_FROM_OP52_20260924.md"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(text):
    def pairs(values):
        obj = {}
        for key, value in values:
            if key in obj:
                raise ValueError("duplicate key")
            obj[key] = value
        return obj

    def bad_constant(value):
        raise ValueError("nonfinite constant")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant)


def safe_path(value):
    if not isinstance(value, str):
        return "[nonstring-path-not-exported]"
    normalized = value.replace("\\", "/")
    prefix = ROOT.as_posix() + "/"
    if normalized.casefold().startswith(prefix.casefold()):
        normalized = normalized[len(prefix):]
    elif PureWindowsPath(value).is_absolute() or normalized.startswith("/"):
        return "[external-path-not-exported]"
    if any(term in normalized.casefold() for term in
           ("cookie", "token", "credential", "session", "secret", "auth")):
        return "[sensitive-path-not-exported]"
    return normalized


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    destination = Path(args.out_dir)
    destination.mkdir(parents=True, exist_ok=False)
    jobs = []
    context_returns = []
    for path in sorted((RUN / "outputs/raw").glob("*.stdout.txt")):
        raw = path.read_bytes()
        events = []
        counts = {}
        for line in raw.decode("utf-8", "strict").splitlines():
            if not line.strip():
                continue
            event = strict_json(line)
            part = event.get("part", {})
            if event.get("type") != "tool_use" or not isinstance(part, dict):
                continue
            tool = part.get("tool")
            counts[tool] = counts.get(tool, 0) + 1
            if tool not in LOCAL_TOOLS:
                continue
            state = part.get("state", {})
            inputs = state.get("input", {})
            output = state.get("output", "")
            if not isinstance(output, str):
                raise ValueError("nonstring tool output")
            target = inputs.get("path") or inputs.get("filePath") or inputs.get("pattern")
            target = safe_path(target) if tool in {"read", "glob"} else "[command-not-exported]"
            row = {"tool": tool, "status": state.get("status"), "target": target,
                   "offset": inputs.get("offset"), "limit": inputs.get("limit"),
                   "returned_chars": len(output), "returned_sha256": sha(output.encode("utf-8"))}
            events.append(row)
            if target in ALLOWED_CONTEXTS and state.get("status") == "completed":
                # These two named public project texts are the only returned bodies inspected/exported.
                if any(term in output.casefold() for term in
                       ("sessionid", "messageid", "bearer ", "api_key", "cookie", "credential")):
                    raise ValueError("context output failed safety check; do not export")
                context_returns.append({"job_id": path.name.removesuffix(".stdout.txt"),
                                        "target": target, "returned_text": output,
                                        "returned_sha256": row["returned_sha256"]})
        jobs.append({"job_id": path.name.removesuffix(".stdout.txt"),
                     "raw_sha256": sha(raw), "raw_bytes": len(raw),
                     "tool_event_counts": counts, "local_tool_events": events})
    report = {"schema": "run132-local-tool-provenance/1", "date": "2026-10-09",
              "jobs": jobs, "named_project_context_returns": context_returns,
              "network_calls": 0, "new_model_submissions": 0,
              "original_files_modified": False, "music_acceptance": "NOT_PERFORMED",
              "production_ready": False,
              "limits": ["Local event records are not remote backend attestation.",
                         "Non-listed tool outputs/commands are not exported or executed.",
                         "Observed extra inputs do not prove their causal effect on the music text."]}
    with (destination / "report.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps({"report": str(destination / "report.json"), "jobs": len(jobs),
                      "jobs_with_local_tools": [row["job_id"] for row in jobs if row["local_tool_events"]],
                      "named_context_returns": len(context_returns),
                      "new_model_submissions": 0}, ensure_ascii=False))


if __name__ == "__main__":
    main()
