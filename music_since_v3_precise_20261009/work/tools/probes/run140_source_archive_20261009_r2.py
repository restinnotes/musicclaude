"""Verify run140 dispatcher sources and recover the missing pack02 Muse archive.

This is a one-shot, offline archive repair. It reads historical files and a
sanitized T3-source bundle from stdin, imports the frozen mechanical parser,
and writes only under notes/research/run140_source_archive_20261009_r2/.
It refuses to run outside Python -I -B and refuses any existing output path.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if not sys.flags.isolated or not sys.dont_write_bytecode:
    raise SystemExit("Run only as: python -I -B tools/probes/run140_source_archive_20261009_r2.py")

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
PROBES = TOOLS / "probes"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(PROBES))

import run140_mech_independent_review as driver  # noqa: E402
import run140_dispatch_archive_20261009 as old_archive  # noqa: E402

RUN140 = ROOT / "runs" / "run140_mech_independent_review"
REVIEWS = RUN140 / "reviews"
ARCHIVE_ROOT = ROOT / "notes" / "research" / "run140_source_archive_20261009_r2"
TEMP_BUNDLE = ARCHIVE_ROOT / ".source_bundle.tmp.json"
PROMPT_SHA = old_archive.FROZEN_PROMPT_SHA
VERDICT_ORDER = ["insight", "restatement", "manufactured", "imported", "undetermined"]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_new(path: Path, raw: bytes) -> None:
    if path.exists():
        raise FileExistsError("refusing to overwrite: " + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError("refusing to overwrite: " + str(path))
    path.write_bytes(raw)


def write_json_new(path: Path, obj: dict) -> None:
    raw = (json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    write_new(path, raw)


def load_source_bundle() -> dict:
    if TEMP_BUNDLE.is_file():
        raw = TEMP_BUNDLE.read_bytes()
        TEMP_BUNDLE.unlink()
        obj = json.loads(raw.decode("utf-8"))
        if not isinstance(obj, dict) or not isinstance(obj.get("sources"), dict):
            raise ValueError("invalid temporary source bundle")
        return obj
    line = sys.stdin.readline()
    if not line:
        raise ValueError("missing source bundle on stdin")
    obj = json.loads(line)
    if not isinstance(obj, dict) or not isinstance(obj.get("sources"), dict):
        raise ValueError("invalid source bundle")
    return obj


def strict_parse(response_text: str, pack: dict) -> tuple[dict | None, str | None]:
    try:
        outer = old_archive.strict_outer_load(response_text)
        parsed, error = driver.parse_review(response_text, pack)
        if parsed is None:
            return None, error
        if parsed != outer:
            return None, "strict outer JSON and frozen driver parse differ"
        return parsed, None
    except (ValueError, TypeError, AttributeError) as exc:
        return None, str(exc)


def json_file(path: Path) -> tuple[dict | None, str | None]:
    try:
        return json.loads(path.read_bytes().decode("utf-8")), None
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        return None, type(exc).__name__ + ": " + str(exc)


def source_row(source: dict, pack: dict, prompt_bytes: bytes, render_bytes: bytes) -> dict:
    task_bytes = source["inputTask"].encode("utf-8")
    response_bytes = source["responseText"].encode("utf-8")
    parsed, parse_error = strict_parse(source["responseText"], pack)
    return {
        "pack": source["pack"],
        "reviewer": source["reviewer"],
        "client_request_id": source["requestId"],
        "submission_event_position": source["submissionEventPosition"],
        "submission_event_status": source["submissionEventStatus"],
        "terminal_status": source["terminalStatus"],
        "terminal_item_position": source["terminalItemPosition"],
        "request_time": source.get("requestTime"),
        "completed_at": source.get("completedAt"),
        "requested_target": source["requestedTarget"],
        "t3_reported_provider": source["providerAppReported"],
        "t3_reported_model": source["modelAppReported"],
        "task_bytes": task_bytes,
        "response_bytes": response_bytes,
        "task_sha256": sha(task_bytes),
        "response_sha256": sha(response_bytes),
        "task_matches_frozen_prompt": task_bytes == prompt_bytes,
        "prompt_matches_driver_render": prompt_bytes == render_bytes,
        "prompt_sha256": sha(prompt_bytes),
        "parsed": parsed,
        "parse_error": parse_error,
        "schema_pass": parsed is not None,
        "wrapper_preview_check": source.get("wrapperPreviewCheck"),
    }


def compare_existing_archive(source: dict, row: dict) -> dict:
    dirname = "%s_%s_r1" % (source["pack"], source["reviewer"])
    folder = REVIEWS / dirname
    names = ["task.txt", "response.txt", "meta.json", "parse_report.json"]
    present = {name: (folder / name).is_file() for name in names}
    result = {
        "directory": "runs/run140_mech_independent_review/reviews/" + dirname,
        "all_four_files_present": all(present.values()),
        "files_present": present,
        "actual_delegate_payload_equals_frozen_prompt": row["task_matches_frozen_prompt"],
        "archive_task_equals_frozen_prompt": False,
        "archive_task_equals_delegate_payload": False,
        "archive_response_equals_terminal_message": False,
        "meta_checks": {},
        "parse_report_checks": {},
        "recomputed_schema_pass_from_terminal_message": row["schema_pass"],
        "recomputed_parse_error": row["parse_error"],
    }
    if not all(present.values()):
        return result

    task_raw = (folder / "task.txt").read_bytes()
    response_raw = (folder / "response.txt").read_bytes()
    result["archive_task_sha256"] = sha(task_raw)
    result["archive_response_sha256"] = sha(response_raw)
    prompt_path = RUN140 / "review_prompts" / (source["pack"] + ".txt")
    result["archive_task_equals_frozen_prompt"] = task_raw == prompt_path.read_bytes()
    result["archive_task_equals_delegate_payload"] = task_raw == row["task_bytes"]
    result["archive_response_equals_terminal_message"] = response_raw == row["response_bytes"]

    meta, meta_error = json_file(folder / "meta.json")
    parse_report, parse_error = json_file(folder / "parse_report.json")
    result["meta_json_error"] = meta_error
    result["parse_report_json_error"] = parse_error
    if meta is not None:
        expected = {
            "client_request_id": source["requestId"],
            "task_sha256": row["task_sha256"],
            "response_sha256": row["response_sha256"],
            "task_utf8_bytes": len(row["task_bytes"]),
            "response_utf8_bytes": len(row["response_bytes"]),
            "status": source["terminalStatus"],
            "requested_target": source["requestedTarget"],
            "observed_t3_provider": source["providerAppReported"],
            "observed_t3_model": source["modelAppReported"],
        }
        result["meta_checks"] = {
            key: {"matches": meta.get(key) == value, "reported": meta.get(key)}
            for key, value in expected.items()
        }
    if parse_report is not None:
        expected_parsed = row["parsed"]
        result["parse_report_checks"] = {
            "response_sha256_matches_terminal": parse_report.get("response_sha256") == row["response_sha256"],
            "actual_task_sha256_matches_delegate_payload": parse_report.get("actual_task_sha256") == row["task_sha256"],
            "actual_task_equals_frozen": parse_report.get("actual_task_equals_frozen") is row["task_matches_frozen_prompt"],
            "schema_pass_matches_recomputed": parse_report.get("schema_pass") is row["schema_pass"],
            "parsed_object_matches_recomputed": parse_report.get("parsed") == expected_parsed,
            "quoted_items_exact_matches_recomputed": parse_report.get("quoted_items_exact") is row["schema_pass"],
            "quoted_relation_exact_matches_recomputed": parse_report.get("quoted_relation_exact") is row["schema_pass"],
        }
    return result


def main() -> None:
    if ARCHIVE_ROOT.exists():
        children = list(ARCHIVE_ROOT.iterdir())
        if len(children) != 1 or children[0] != TEMP_BUNDLE or not TEMP_BUNDLE.is_file():
            raise SystemExit("archive already exists; refusing to write or overwrite: " + str(ARCHIVE_ROOT))

    bundle = load_source_bundle()
    frozen = old_archive.check_frozen()
    if not frozen.get("all_ok"):
        raise SystemExit("frozen inputs do not match; refusing repair: " + json.dumps(frozen, ensure_ascii=False))

    cases = driver.load_and_validate()
    packs, _mapping = driver.build_packs(cases)
    pack_by_id = {p["pack_id"]: p for p in packs}
    prompts: dict[str, bytes] = {}
    renders: dict[str, bytes] = {}
    for pack_id in ("pack01", "pack02", "pack03", "pack04", "pack05"):
        prompts[pack_id] = (RUN140 / "review_prompts" / (pack_id + ".txt")).read_bytes()
        renders[pack_id] = driver.render_pack_prompt(pack_by_id[pack_id]).encode("utf-8")
        if sha(prompts[pack_id]) != PROMPT_SHA[pack_id] or prompts[pack_id] != renders[pack_id]:
            raise SystemExit("frozen prompt mismatch; refusing repair: " + pack_id)

    sources = bundle["sources"]
    required = {"pack01_muse", "pack01_luna", "pack02_luna", "pack02_muse"}
    if set(sources) != required:
        raise ValueError("source bundle must contain exactly the four observed review submissions")

    rows = {}
    for key, source in sources.items():
        if source["terminalStatus"] != "completed":
            raise ValueError("terminal response is not completed for " + key)
        pid = source["pack"]
        rows[key] = source_row(source, pack_by_id[pid], prompts[pid], renders[pid])

    existing = {
        key: compare_existing_archive(sources[key], rows[key])
        for key in ("pack01_muse", "pack01_luna", "pack02_luna")
    }
    fully_verified_existing = {}
    for key, check in existing.items():
        fully_verified_existing[key] = bool(
            check["all_four_files_present"]
            and check["actual_delegate_payload_equals_frozen_prompt"]
            and check["archive_task_equals_frozen_prompt"]
            and check["archive_task_equals_delegate_payload"]
            and check["archive_response_equals_terminal_message"]
            and check.get("meta_checks")
            and all(v["matches"] for v in check["meta_checks"].values())
            and check.get("parse_report_checks")
            and all(check["parse_report_checks"].values())
        )

    muse = rows["pack02_muse"]
    muse_source = sources["pack02_muse"]
    parsed, parse_error = muse["parsed"], muse["parse_error"]
    schema_pass = muse["schema_pass"]
    counts = {}
    if parsed is not None:
        for item in parsed["reviews"]:
            counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1

    source_receipt = {
        "schema": "run140-source-receipt/1",
        "client_request_id": muse_source["requestId"],
        "pack_id": "pack02",
        "reviewer_route": "muse",
        "role": muse_source["role"],
        "mode": muse_source["mode"],
        "requested_at": muse_source.get("requestTime"),
        "completed_at": muse_source.get("completedAt"),
        "requested_target": muse_source["requestedTarget"],
        "t3_reported_provider": muse_source["providerAppReported"],
        "t3_reported_model": muse_source["modelAppReported"],
        "actual_backend_identity": "unattested",
        "task_source": {
            "kind": "successful delegate_task tool input",
            "dispatcher_activity_position": muse_source["submissionEventPosition"],
            "field": "input.task",
            "sha256": muse["task_sha256"],
            "utf8_bytes": len(muse["task_bytes"]),
            "equals_frozen_prompt_bytes": muse["task_matches_frozen_prompt"],
            "prompt_sha256": muse["prompt_sha256"],
        },
        "terminal_source": {
            "kind": "completed child terminal assistant_message",
            "item_position": muse_source["terminalItemPosition"],
            "item_updated_at": muse_source.get("terminalItemUpdatedAt"),
            "status": muse_source["terminalStatus"],
            "sha256": muse["response_sha256"],
            "utf8_bytes": len(muse["response_bytes"]),
            "written_without_trimming": True,
        },
        "task_status_tool_evidence": {
            "dispatcher_activity_positions": [115, 146, 200],
            "position_200_reassembled": bundle["task_status_evidence"]["pack02_muse_position_200_reassembled"],
            "final_status": "completed",
            "has_pending_child_runs": False,
        },
        "wrapper_secondary_check": muse_source.get("wrapperPreviewCheck"),
        "identity_limits": {
            "t3_provider_and_model_are_app_reported": True,
            "independent_remote_attestation": False,
            "legacy_producer_identity": "unknown_in_legacy_record",
            "canonical_model_labels_do_not_establish_self_review": True,
        },
        "scope_limits": {
            "music_judgment_performed": False,
            "production_ready": False,
            "schema_pass_is_not_quality_or_acceptance": True,
        },
    }

    parse_report = {
        "schema": "run140-return-parse/1",
        "date": "2026-10-09",
        "pack_id": "pack02",
        "reviewer": "muse",
        "client_request_id": muse_source["requestId"],
        "schema_pass": schema_pass,
        "error": parse_error,
        "response_sha256": muse["response_sha256"],
        "response_utf8_bytes": len(muse["response_bytes"]),
        "actual_task_sha256": muse["task_sha256"],
        "actual_task_equals_frozen": muse["task_matches_frozen_prompt"],
        "requested_target": muse_source["requestedTarget"],
        "observed_t3_provider": muse_source["providerAppReported"],
        "observed_t3_model": muse_source["modelAppReported"],
        "observed_status": muse_source["terminalStatus"],
        "production_ready": False,
        "music_verdict": "not adjudicated by parser",
        "limits": "Strict JSON/schema/quote checks only; T3 identity is not remote attestation; historical backend unknown.",
        "identity_limit": "legacy producer identity remains unknown_in_legacy_record; no exact-producer or self-review claim",
        "quoted_items_exact": bool(schema_pass),
        "quoted_relation_exact": bool(schema_pass),
        "parsed": parsed,
    }
    if schema_pass:
        parse_report["verdict_counts_raw_reviewer_only"] = {
            key: counts[key] for key in VERDICT_ORDER if key in counts
        }

    submitted = {}
    for key, source in sources.items():
        row = rows[key]
        submitted[key] = {
            "client_request_id": source["requestId"],
            "model": source["modelAppReported"],
            "provider_app_reported": source["providerAppReported"],
            "task_terminal_status": source["terminalStatus"],
            "delegate_task_event_position": source["submissionEventPosition"],
            "task_equals_frozen_prompt": row["task_matches_frozen_prompt"],
            "task_sha256": row["task_sha256"],
            "terminal_response_sha256": row["response_sha256"],
            "terminal_item_position": source["terminalItemPosition"],
        }

    planned = []
    for n in range(1, 6):
        pack_id = "pack%02d" % n
        for reviewer in ("luna", "muse"):
            if reviewer == "muse" and n == 1:
                continue
            key = pack_id + "_" + reviewer
            if key in sources:
                status = "terminal_completed"
                if key in existing:
                    archive_status = "verified_existing" if fully_verified_existing[key] else "existing_with_mismatch"
                else:
                    archive_status = "recovered_new"
            else:
                status = "not_submitted"
                archive_status = "none"
            planned.append({
                "pack": pack_id,
                "reviewer": reviewer,
                "client_request_id": "music-20261009-run140-%s-%s-r1" % (pack_id, reviewer),
                "submission_status": status,
                "archive_status": archive_status,
            })
    planned.append({
        "pack": "pack01",
        "reviewer": "muse",
        "client_request_id": "music-20261009-run140-pack01-muse-r1",
        "submission_status": "terminal_completed_preexisting",
        "archive_status": "verified_existing" if fully_verified_existing["pack01_muse"] else "existing_with_mismatch",
    })
    planned.sort(key=lambda x: (x["pack"], x["reviewer"]))

    report = {
        "schema": "run140-source-archive-report/1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": {
            "historical_sources_read_only": True,
            "runtime": "python -I -B",
            "frozen_driver_sha256": frozen["driver"],
            "frozen_cases_sha256": frozen["cases"],
            "all_five_frozen_prompts_match_render_and_allowlisted_sha": frozen["all_ok"],
            "strict_parser": "tools/probes/run140_dispatch_archive_20261009.py strict_outer_load + tools/run140_mech_independent_review.py parse_review",
            "new_model_or_workflow_submissions": 0,
            "new_review_or_candidate_content_authored": False,
        },
        "dispatcher": {
            "client_request_id": bundle["dispatcher"]["client_request_id"],
            "source_activity_position": bundle["dispatcher"]["activity_position"],
            "brief_requested_additional_child_tasks": 9,
            "prior_completed_task": "pack01_muse",
            "requested_additional_routes": "pack01-pack05 Luna and pack02-pack05 Muse",
            "parent_activity_reported_item_count": bundle["coverage"]["parent_activity_item_count"],
            "parent_activity_last_position_read": bundle["coverage"]["parent_activity_last_position"],
            "parent_delegate_task_call_count": bundle["coverage"]["parent_delegate_task_call_count"],
            "dispatcher_activity_item_count": bundle["coverage"]["dispatcher_activity_item_count"],
            "dispatcher_status": bundle["coverage"]["dispatcher_status"],
            "dispatcher_run_count": bundle["coverage"]["dispatcher_run_count"],
            "successful_content_child_submissions": 3,
            "failed_delegate_invocations_without_task_id": bundle["failed_delegate_invocations"],
        },
        "counts": {
            "planned_content_review_slots_including_preexisting_pack01_muse": 10,
            "submitted_content_reviews": 4,
            "terminal_content_reviews": 4,
            "archive_directories_present_after_repair": 4,
            "preexisting_archives_fully_matching_source_metadata_and_parse": sum(fully_verified_existing.values()),
            "exact_task_and_response_source_pairs_after_repair": sum(
                bool(check["archive_task_equals_delegate_payload"] and check["archive_response_equals_terminal_message"])
                for check in existing.values()
            ) + 1,
            "not_submitted_slots": 6,
            "additional_tasks_requested": 9,
            "additional_tasks_submitted": 3,
        },
        "submission_matrix": planned,
        "submitted_sources": submitted,
        "task_status_evidence": bundle["task_status_evidence"],
        "existing_archive_checks": {key: existing[key] for key in sorted(existing)},
        "new_archive": {
            "directory": "notes/research/run140_source_archive_20261009_r2/pack02_muse_r1",
            "task_equals_frozen_prompt": muse["task_matches_frozen_prompt"],
            "task_sha256": muse["task_sha256"],
            "response_sha256": muse["response_sha256"],
            "response_utf8_bytes": len(muse["response_bytes"]),
            "terminal_status": muse_source["terminalStatus"],
            "strict_schema_pass": schema_pass,
            "parse_error": parse_error,
        },
        "limitations": [
            "T3 provider/model are app-reported labels; actual backend identity is unattested.",
            "Nested child user text is not exposed in messages view. For nested submissions, the exact known wrapper was removed only from the 72-character subagent title preview; the remaining visible prefix matched the delegate input prefix. This is auxiliary and not proof of the full prompt.",
            "The delegate_task input.task is the primary task-payload source; receipt hashes do not authenticate a remote backend.",
            "Schema and exact-quote parsing does not judge musical quality, resolve the reviews, complete any work, or establish production readiness.",
        ],
    }

    readme = (
        "# run140 source archive r2\n\n"
        "This directory records a read-only source audit and the recovered pack02 Muse archive.\n\n"
        "- pack02_muse_r1/task.txt is the exact successful delegate_task input.task string encoded as UTF-8.\n"
        "- response.txt is the complete terminal assistant message encoded as UTF-8, written without trimming.\n"
        "- source_receipt.json records the request ID, app-reported target and terminal status, timestamps, and source hashes. Actual backend identity remains unattested.\n"
        "- parse_report.json applies the frozen strict JSON and quote/schema checks. Passing is not a musical or production verdict.\n"
        "- report.json compares the three pre-existing archives byte-for-byte with their frozen prompt, actual delegate input, terminal message, metadata, and parse report.\n"
        "- Source review slots: 4 of 10 planned tasks were submitted, terminal, and archived after this repair; pack03–05 Luna/Muse were not submitted. No new review task was dispatched.\n"
        "- Producer identity remains unknown in the legacy record; app-reported model labels do not establish backend identity or self-review.\n"
    ).encode("utf-8")

    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=False, exist_ok=False)
    pack_dir = ARCHIVE_ROOT / "pack02_muse_r1"
    pack_dir.mkdir(parents=False, exist_ok=False)
    write_new(pack_dir / "task.txt", muse["task_bytes"])
    write_new(pack_dir / "response.txt", muse["response_bytes"])
    write_json_new(pack_dir / "source_receipt.json", source_receipt)
    write_json_new(pack_dir / "parse_report.json", parse_report)
    write_json_new(ARCHIVE_ROOT / "report.json", report)
    write_new(ARCHIVE_ROOT / "README.md", readme)

    print(json.dumps({
        "archive_written": True,
        "archive_root": str(ARCHIVE_ROOT),
        "pack02_muse": {
            "task_sha256": muse["task_sha256"],
            "response_sha256": muse["response_sha256"],
            "schema_pass": schema_pass,
            "response_utf8_bytes": len(muse["response_bytes"]),
        },
        "existing_archives": {
            key: {
                "task_matches_delegate_input": existing[key]["archive_task_equals_delegate_payload"],
                "response_matches_terminal": existing[key]["archive_response_equals_terminal_message"],
                "all_four_files_present": existing[key]["all_four_files_present"],
            }
            for key in sorted(existing)
        },
        "submitted_terminal_count": 4,
        "preexisting_archives_fully_verified": sum(fully_verified_existing.values()),
        "not_submitted_count": 6,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
