"""Write source-bound manifests and audit reports after the final captured run."""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
FINAL_ATTEMPT = EVIDENCE / "attempt-008"


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def literal_constants(path: Path, names: tuple[str, ...]) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    wanted = set(names)
    found: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    found[target.id] = ast.literal_eval(node.value)
    if set(found) != wanted:
        raise RuntimeError("could not read fixed literal paths: " + repr(wanted - set(found)))
    return found


def file_hash_map(paths: list[str]) -> dict[str, str]:
    return {relative: digest_file(ROOT / relative) for relative in sorted(set(paths))}


def command_rows() -> list[dict]:
    metadata = json.loads((FINAL_ATTEMPT / "commands.json").read_text(encoding="utf-8"))
    expected = (0, 0, 3, 0, 3)
    rows = metadata["commands"]
    if len(rows) != 5 or tuple(row["returncode"] for row in rows) != expected or any(
            row["timed_out"] for row in rows):
        raise RuntimeError("final five-command evidence did not match expected status")
    if metadata.get("provider_or_model_cli_invocations") != 0:
        raise RuntimeError("unexpected CLI invocation in final evidence")
    return rows


def test_count(label: str) -> int:
    row = next(row for row in command_rows() if row["label"] == label)
    raw = (FINAL_ATTEMPT / row["stderr_file"]).read_bytes()
    match = re.search(rb"Ran (\d+) tests", raw)
    if not match:
        raise RuntimeError("test count missing from captured unittest output: " + label)
    return int(match.group(1))


def build_manifests() -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    specs = (
        ("run144_e7_flash_diag_r5", "run144_e7_flash_diag_r5", "test_run144_e7_flash_diag_r5.py",
         "run142_e7_flash_diag_r4", "run142_e7_flash_diag_r4/go.py", "run139",
         ("INPUT_PATHS", "TEMPLATE_PATHS"),
         {"fresh_full_run": 126, "fresh_full_run_breakdown": {
             "why": 22, "mechanical": 23, "audit": 46, "surface": 23, "compare": 12},
          "identical_second_run_new_submissions": 0,
          "real_model_submissions": 0, "real_cli_invocations": 0,
          "safe_pre_submit_retry_policy_test_invocations": 2}),
        ("run145_thread_resume_r5", "run145_thread_resume_r5", "test_run145_thread_resume_r5.py",
         "run143_thread_resume_r4", "run143_thread_resume_r4/go.py", "run141",
         ("SOURCE_PATHS", "TEMPLATE_PATHS"),
         {"fresh_full_run": 600, "fresh_full_run_breakdown": {
             "step": 92, "integrated_nlv_match": 4, "center": 4,
             "thread_identity_review": 480, "thread_compare_review": 20},
          "identical_second_run_reused": 600, "identical_second_run_new_submissions": 0,
          "match_artifacts_reverified_on_second_run": 4,
          "musepacks_test_only_mock_constructed": 100,
          "real_model_submissions": 0, "real_cli_invocations": 0}),
    )
    frozen_before = json.loads((EVIDENCE / "protected_before.json").read_text(encoding="utf-8"))
    for run_id, run_dir, test_name, parent_dir, parent_go, parent_run, const_names, mock_counts in specs:
        driver = ROOT / "runs" / run_dir / "go.py"
        constants = literal_constants(driver, const_names)
        frozen_paths = list(constants[const_names[0]].values()) + list(constants[const_names[1]].values())
        manifest = {
            "schema": "offline-implementation-manifest-v1",
            "revision": run_id,
            "based_on": {"run": parent_run, "source_revision": parent_dir,
                         "source_go_sha256": frozen_before["fixed_protected_files"]["runs/" + parent_go]["sha256"]},
            "artifacts": {
                "go_py_sha256": digest_file(driver),
                "readme_sha256": digest_file(ROOT / "runs" / run_dir / "README.md"),
                "test_py_sha256": digest_file(ROOT / "tools" / "tests" / test_name),
            },
            "frozen_input_sha256": file_hash_map(frozen_paths),
            "frozen_prompt_sha256": file_hash_map(list(constants[const_names[1]].values())),
            "mock_counts": mock_counts,
            "verification": {
                "final_attempt": 8,
                "test_count": test_count("run144_tests" if run_id.startswith("run144") else "run145_tests"),
                "command_attempt_directory": "attempt-008",
                "commands": [{"label": row["label"], "returncode": row["returncode"],
                              "timed_out": row["timed_out"], "stdout_bytes": row["stdout_bytes"],
                              "stderr_bytes": row["stderr_bytes"],
                              "stdout_sha256": row["stdout_sha256"],
                              "stderr_sha256": row["stderr_sha256"]}
                             for row in command_rows()],
            },
            "boundaries": {
                "network": "not used", "provider_or_model_cli_invocations": 0,
                "real_model_submissions": 0, "music_acceptance": "NOT_PERFORMED",
                "completion": "COMPLETION_PENDING", "production_ready": False,
                "independent_review": "required before any acceptance",
                "test_evidence_is_music_acceptance": False,
            },
        }
        path = ROOT / "runs" / run_dir / "manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
        manifests[run_id] = manifest
    return manifests


RUN139 = [
    ("test_import_has_no_environment_io_cli_or_source_import_effects",
     "Patched Path reads/writes/mkdir and subprocess calls to fail; asserted unchanged environment/run inventory and no imported legacy run modules.",
     "test_import_has_no_environment_io_cli_or_source_import_effects"),
    ("test_config_and_canonical_self_flags_are_frozen",
     "Asserted frozen generator/chooser/auditor/judge models and exact canonical self flags for gflash/gflash_web/luna.",
     "test_config_and_canonical_self_flags_are_frozen"),
    ("test_full_mock_rerun_adds_zero_submissions_and_stays_pending",
     "Ran full mock twice; asserted second run has zero new submissions, pending marker only, no DONE, zero real submissions and unknown/unverified legacy producer.",
     "test_full_mock_rerun_adds_zero_submissions_and_stays_pending"),
    ("test_full_collections_exact_identities_packs_and_reader_content",
     "Asserted WHY k2..23, MECH/SURFACE k1..23, full audit reviewer and blind compare identity sets, candidate rotation, six valid packs each, and actual expanded/recap text.",
     "test_full_collections_exact_identities_packs_and_reader_content"),
    ("test_parser_failure_retry_appends_attempt_without_overwrite",
     "Old implicit retry is explicitly replaced: default completed parse failure is persisted then STOPped; a separate test authorizes one bounded resample and proves attempt 0 raw bytes remain immutable.",
     "test_default_parse_failure_stops_and_rerun_submits_zero_new_samples; test_parser_failure_retry_appends_attempt_without_overwrite"),
    ("test_cache_only_claim_without_exact_artifacts_is_rejected",
     "Returned cache-only claim without exact files raises IntegrityError, records FAILED, and cannot be resumed as evidence.",
     "test_cache_only_claim_without_exact_artifacts_is_rejected"),
    ("test_queue_stop_blocks_every_following_submission_and_stage",
     "First mock queue_stop writes hold/failure evidence; no stage record is completed and next invocation is blocked with zero submissions.",
     "test_queue_stop_blocks_every_following_submission_and_stage"),
    ("test_exact_artifact_tamper_is_rejected_before_resume",
     "Mutated prompt and output bytes separately; resume raises before any new caller submission.",
     "test_exact_artifact_tamper_is_rejected_before_resume"),
    ("test_pack_missing_and_tamper_are_rejected_without_rebuilding",
     "Removed or changed a review pack; resume rejects with zero new submissions.",
     "test_pack_missing_and_tamper_are_rejected_without_rebuilding"),
    ("test_source_tamper_is_rejected_using_an_isolated_fixture_root",
     "Changed frozen history source in an isolated fixture after a full run; resume rejects before submission.",
     "test_source_tamper_is_rejected_using_an_isolated_fixture_root"),
    ("test_duplicate_reviewer_and_order_identity_sets_are_rejected",
     "Validated exact baseline×judge×order set then injected a duplicate, broken mapping, and missing audit reviewer; each is rejected.",
     "test_duplicate_reviewer_and_order_identity_sets_are_rejected"),
    ("test_pack_validator_rejects_placeholder_and_missing_task_id",
     "Injected an unfilled template token and removed a required task; exact pack validation rejects both.",
     "test_pack_validator_rejects_placeholder_and_missing_task_id"),
    ("test_muse_cannot_be_ingested_without_external_identity_verifier_and_twow_stays_held",
     "Raw fake results remain pending without a verifier; held two-w slot raises QueueStopped; separate TEST_ONLY receipt path and field-tamper tests exercise bound ingress.",
     "test_muse_cannot_be_ingested_without_external_identity_verifier_and_twow_stays_held; test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections"),
    ("test_missing_terminal_identity_is_rejected_and_producer_stays_unknown",
     "Omitted terminal artifact; execution rejects while historical producer remains unknown.",
     "test_missing_terminal_identity_is_rejected_and_producer_stays_unknown"),
    ("test_direct_real_path_blocks_before_creating_real_run_outputs",
     "Recorded run directory before direct real entry; call blocks with unchanged inventory and zero caller submissions.",
     "test_direct_real_path_blocks_before_creating_real_run_outputs; captured run144 --real returns 3"),
]

RUN141 = [
    ("test_import_has_no_environment_file_cli_or_write_side_effects",
     "Patched environment mutation, builtins/Path I/O and process APIs to fail during import; environment remains byte-for-byte equal.",
     "test_import_has_no_environment_file_cli_or_write_side_effects"),
    ("test_full_mock_chain_exact_disk_proof_and_second_run_zero_submit",
     "Asserted 4×23 chain, exact evidence-backed second-run reuse with zero new submissions, pending completion, held real plan, and no music acceptance.",
     "test_full_mock_chain_exact_disk_proof_and_second_run_zero_submit"),
    ("test_missing_artifact_is_not_reused",
     "A cache record without exact disk artifacts cannot be reused; verifier reports missing metadata.",
     "test_missing_artifact_is_not_reused; test_parse_failure_raw_is_durable_default_stop_and_explicit_sample_survives_restart"),
    ("test_tampered_output_sha_is_rejected",
     "Appended output bytes without matching proof; exact disk verifier rejects SHA mismatch.",
     "test_tampered_output_sha_is_rejected"),
    ("test_prompt_tamper_is_rejected",
     "Changed persisted prompt bytes; exact prompt hash/identity verification rejects.",
     "test_prompt_tamper_is_rejected"),
    ("test_full_identity_tamper_is_rejected",
     "Changed model identity in metadata; complete request identity verification rejects.",
     "test_full_identity_tamper_is_rejected; test_mode_request_and_full_mock_producer_tuple_are_bound_to_slot"),
    ("test_duplicate_success_in_same_slot_is_ambiguous",
     "Two successful records for one slot raise ambiguity rather than selecting either result.",
     "test_duplicate_success_in_same_slot_is_ambiguous"),
    ("test_ambiguous_success_sources_from_two_runs_are_rejected",
     "Two successful source-run candidates for the same slot raise ambiguity.",
     "test_ambiguous_success_sources_from_two_runs_are_rejected"),
    ("test_strict_sets_detect_missing_extra_and_duplicate_even_when_counts_match",
     "Same-size wrong identity set and duplicate identities both fail exact set comparison.",
     "test_strict_sets_detect_missing_extra_and_duplicate_even_when_counts_match"),
    ("test_musepack_tampering_and_file_read_reference_are_rejected",
     "Mutated mapping, added file-read path, changed seed, and changed template bytes; each invalidates exact frozen pack/hash binding.",
     "test_musepack_tampering_and_file_read_reference_are_rejected; test_muse_raw_return_is_unverified_and_sourcebound_entry_needs_exact_receipt"),
    ("test_muse_return_needs_real_transport_schema_and_exact_quotes",
     "Mock transport and unsupported quote are rejected; r5 never promotes raw result and separately tests complete sourcebound receipt binding.",
     "test_muse_raw_return_is_unverified_and_sourcebound_entry_needs_exact_receipt; test_thread_compare_uses_frozen_schema_and_candidate_specific_exact_quotes"),
    ("test_queue_stop_stops_current_remaining_jobs_and_all_later_stages",
     "After queue stop in match stage, center is never invoked and later stages are marked stopped before start.",
     "test_queue_stop_stops_current_remaining_jobs_and_all_later_stages"),
    ("test_no_longer_valid_without_match_evidence_blocks_history",
     "NLV history change without provenance-backed match evidence is rejected; full-chain positive and tamper/None cases exercise integrated retirement.",
     "test_no_longer_valid_without_match_evidence_blocks_history; test_integrated_match_evidence_binds_step_inventory_quote_and_none_does_not_delete"),
    ("test_legacy_unknown_producer_is_preserved_without_fabrication",
     "Legacy model label without exact producer proof remains recorded=false/value=None.",
     "test_legacy_unknown_producer_is_preserved_without_fabrication"),
    ("test_strict_preflight_is_pending_without_v4_and_writes_nothing",
     "Read-only preflight leaves run tree unchanged and reports blocked/pending with zero writes; absent and present-unverified cases are covered.",
     "test_strict_preflight_is_pending_without_v4_acceptance_and_writes_nothing; test_real_preflight_only_checks_presence_and_direct_real_entry_writes_nothing"),
]


def write_reports(manifests: dict[str, dict]) -> None:
    mappings = []
    for old_id, rows, current_id in (("run139_e7_flash_diag_r3", RUN139, "run144_e7_flash_diag_r5"),
                                     ("run141_thread_resume_r3", RUN141, "run145_thread_resume_r5")):
        for index, (test_name, behavior, new_test) in enumerate(rows, 1):
            mappings.append({"legacy_suite": old_id, "ordinal": index, "legacy_test": test_name,
                             "legacy_asserted_behavior": behavior, "mapped_revision": current_id,
                             "r5_test_assertions": new_test})
    (EVIDENCE / "historical_assertion_mapping.json").write_text(
        json.dumps(mappings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    before = json.loads((EVIDENCE / "protected_before.json").read_text(encoding="utf-8"))
    after = json.loads((EVIDENCE / "protected_after.json").read_text(encoding="utf-8"))
    protected_equal = all(before[key] == after[key] for key in
                          ("fixed_protected_files", "old_run_inventories", "presence_only_probes"))
    if not protected_equal:
        raise RuntimeError("protected before/after values differ")
    attempts = []
    for folder in sorted(EVIDENCE.glob("attempt-*")):
        command_path = folder / "commands.json"
        if not command_path.is_file():
            continue
        record = json.loads(command_path.read_text(encoding="utf-8"))
        attempts.append({"attempt": record["attempt"], "commands": [
            {"label": item["label"], "returncode": item["returncode"],
             "timed_out": item["timed_out"], "stdout_bytes": item["stdout_bytes"],
             "stderr_bytes": item["stderr_bytes"], "stdout_sha256": item["stdout_sha256"],
             "stderr_sha256": item["stderr_sha256"]} for item in record["commands"]]})
    run144 = manifests["run144_e7_flash_diag_r5"]
    run145 = manifests["run145_thread_resume_r5"]
    report = {
        "status": "IMPLEMENTATION_COMPLETE_PENDING_INDEPENDENT_REVIEW",
        "role_boundary": "offline engineering implementation only; no music candidate or verdict adjudicated",
        "new_artifacts": [
            "runs/run144_e7_flash_diag_r5/go.py", "runs/run144_e7_flash_diag_r5/README.md",
            "runs/run144_e7_flash_diag_r5/manifest.json", "runs/run145_thread_resume_r5/go.py",
            "runs/run145_thread_resume_r5/README.md", "runs/run145_thread_resume_r5/manifest.json",
            "tools/tests/test_run144_e7_flash_diag_r5.py", "tools/tests/test_run145_thread_resume_r5.py"],
        "historical_assertion_mapping": {"path": "historical_assertion_mapping.json", "rows": len(mappings),
                                         "run139_assertions": 15, "run141_assertions": 15,
                                         "mapping_is_behavioral_not_ast_name_only": True},
        "protected_snapshot": {"before": "protected_before.json", "after": "protected_after.json",
                                "fixed_files_hashed": 30,
                                "old_run_file_counts": {"runs/run141_thread_resume_r3": 2,
                                                        "runs/run142_e7_flash_diag_r4": 3,
                                                        "runs/run143_thread_resume_r4": 3},
                                "protected_values_equal": protected_equal,
                                "run140_archive_or_shared_v7_accessed": False,
                                "run140_archive_or_shared_v7_path_enumerated": False,
                                "credentials_cookies_tokens_read": False,
                                "old_CLAUDE_or_memory_written": False},
        "final_verification": {"attempt": 8, "commands": command_rows(),
                               "run144_test_count": run144["verification"]["test_count"],
                               "run145_test_count": run145["verification"]["test_count"],
                               "expected_return_codes": [0, 0, 3, 0, 3],
                               "all_expected_statuses": True,
                               "provider_or_model_cli_invocations": 0,
                               "network_used": False},
        "mock_counts": {"run144": run144["mock_counts"], "run145": run145["mock_counts"]},
        "attempt_history": attempts,
        "nineteen_protection_matrix": [
            {"item": 1, "status": "PASS", "evidence": "15+15 assertion-level historical mappings in historical_assertion_mapping.json; default parse retry was intentionally changed to STOP plus explicit bounded sample."},
            {"item": 2, "status": "PASS", "evidence": "Distinct run144/run145 IDs and paths; import probes preserve inventories; protected run141/run142/run143 inventories unchanged."},
            {"item": 3, "status": "PASS", "evidence": "Both --real commands return 3; preflight tests cover absent/present-unverified entries with 0 CLI, 0 submissions, 0 writes; no exec_module/sys.path import of shared entries."},
            {"item": 4, "status": "PASS", "evidence": "Unverified v4, partial v5 and v6 in-flight label remain non-adopted; r5 labels the v6 state in_flight_not_auto_adopted, a descriptive wording correction only."},
            {"item": 5, "status": "PASS", "evidence": "Both suites reject prefix/trailer/second JSON value, duplicate keys, nonfinite values, scalar/wrong type and bool-as-int at strict boundaries."},
            {"item": 6, "status": "PASS", "evidence": "Frozen parser schemas; quote validation binds to mapped candidate text; exact task and candidate mapping sets; source, template and driver locks rechecked."},
            {"item": 7, "status": "PASS", "evidence": "run144 full request identity binds slot, model/version, producer/source/template/driver and prompt bytes; run145 binds current mode, producer and exact slot."},
            {"item": 8, "status": "PASS", "evidence": "Canonical Muse alias maps only to claude-proxy/muse-spark-1.3-contributor-free over mcp. run144 exact 26-field receipt; run145 exact 27-field receipt; TEST_ONLY never counts real. No verifier means pending/raw_unverified."},
            {"item": 9, "status": "PASS", "evidence": "Thread frozen schemas enforce guess, fits, confidence strict integer, and candidate-specific exact citations; duplicate/unknown fields reject."},
            {"item": 10, "status": "PASS", "evidence": "Completed parse failure writes raw/prompt/meta/terminal before parse and survives restart; default STOP; only explicit True + strict budget <=2 + reason can create immutable sample."},
            {"item": 11, "status": "PASS", "evidence": "Injected sourcebound pre-submit proof is exercised through execute failure→success→reuse; bad/claimed/ambiguous/queue/exhausted proofs persist hold; same sampling identity retained."},
            {"item": 12, "status": "PASS", "evidence": "Full request/slot lineage hashes, exact disk bytes, terminal/meta bindings, duplicate success and tamper paths are rejected before reuse."},
            {"item": 13, "status": "PASS", "evidence": "Four 23-step chains complete mock validation; Center binds all 23 step outputs and required match lineage; second identical run has zero submissions."},
            {"item": 14, "status": "PASS", "evidence": "One k2 NLV per chain yields four exact source match tasks; full prompt/raw/meta/lineage validated through _stage_parse and exact source map; None does not delete; second run verifies four match artifacts."},
            {"item": 15, "status": "PASS", "evidence": "v2/v3 only Q3 single-line change positive; multiple-change, non-Q3, multiline and byte/hash mismatch negatives."},
            {"item": 16, "status": "PASS", "evidence": "Canonical self-review labels and anonymous rotations; run144 reader asserts actual expanded/recap text; run145 retirement uses exact source quote and lineage, not caller-supplied judgment."},
            {"item": 17, "status": "PASS", "evidence": "Mock status stays COMPLETION_PENDING, no DONE, real count zero, music_acceptance NOT_PERFORMED; no production/gate/hold or CENTER_v0 mutation."},
            {"item": 18, "status": "PASS", "evidence": "Import/strict/real side effects tested; first failures and every stdout/stderr/rc retained in attempt-001 through attempt-008."},
            {"item": 19, "status": "PENDING_EXTERNAL_REVIEW", "evidence": "This implementation does not accept itself. Prior independent Muse review remains NOT_ACCEPTED; a fresh independent review and main acceptance are still required."},
        ],
        "receipt_count_correction": {
            "prior_review_result": "NOT_ACCEPTED; retained as final prior independent review disposition",
            "run143_actual_schema": "21 required fields; 19 fixed-value expected bindings; terminal_id and reported_transport have separate checks. Do not repeat the prior review's 19-required/16-bound count.",
            "run145_r5_schema": "27 required fields; 25 fixed-value fields; attestation_class and terminal_id have separate strict checks.",
            "run144_r5_schema": "26 exact required fields; attestation_class plus all task/source/request/prompt/template/mapping/seed/raw/terminal/target/provider/model/transport bindings are validated.",
            "authentication_limit": "Only an injected trusted verifier can return a sourcebound archive receipt; this offline evidence exercises TEST_ONLY mocks and makes no real service/authentication claim."},
        "music_acceptance": "NOT_PERFORMED",
        "production_status": "NOT_AUTHORIZED_BY_MOCK; independent acceptance remains outstanding",
    }
    (EVIDENCE / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
    lines = ["# run144/run145 r5 离线实现报告", "",
             "## 交付状态", "",
             "r5 工程实现与本地 mock 回归完成；不包含音乐候选/裁决，不构成音乐验收或 production。上一轮 independent Muse review 的 NOT_ACCEPTED 结论继续有效；第 19 项需要新的独立 review 与主验收后才能关闭。", "",
             "新增源码、README、manifest 与两套 tests 均在 `report.json` 的 `new_artifacts` 中逐项列明。历史 30 项断言级映射见 [historical_assertion_mapping.json](historical_assertion_mapping.json)。", "",
             "## 最终亲跑证据", "",
             "attempt-008 捕获了五条最终命令的 argv、原始 stdout/stderr bytes、SHA、耗时、timeout 和 rc：run144 tests rc=0（%d tests），run145 tests rc=0（%d tests），run144 `--real` rc=3，run145 `--strict` rc=0，run145 `--real` rc=3。测试均仅用 Python `-X utf8 -I -B` 与本地 mock；provider/model CLI=0、network=未使用。" % (run144["verification"]["test_count"], run145["verification"]["test_count"]), "",
             "run144 fresh full mock 为 126 submissions（WHY 22、MECH 23、audit 46、surface 23、compare 12），同身份第二次新增 0。run145 fresh full mock 为 600（step 92、NLV match 4、Center 4、identity review 480、compare review 20），Muse TEST_ONLY packs 100；同身份第二次复用 600、提交 0，四条 match 证据均重新校验。数量有回归断言与 manifest 双重记录。", "",
             "run144 真实入口只做共享入口 presence check 后阻断；run145 strict 是只读 preflight。两条 `--real` 路径均无 model/CLI 调用、无 run 写入。三个作品的 `06_ACCEPTANCE_CRITERIA.md` 未逐条验收，音乐状态为 `NOT_PERFORMED`。", "",
             "## 失败证据与修复轨迹", "",
             "attempt-001 至 attempt-008 均独立保留；未删除或改名任何 firstfail。早期失败依次暴露 compare task 缩进、Muse 来源字段 schema、`c` 槽位到具体 baseline 名称映射、直接 receipt helper 的 transport 校验等问题；每次都追加新 attempt。每条命令的原始 stdout/stderr 与 rc 在各 attempt 目录的 `.bin` 和 `commands.json`。", "",
             "## Protected snapshot", "",
             "protected-before/after 比较通过：30 个固定历史文件哈希、run141=2/run142=3/run143=3 个旧 run 文件清单及 presence-only probes 全部相等。只 hash 非敏感文件。未枚举、读取或写入 run140 来源归档及共享 v7；未读取 credentials/cookies/tokens；旧 CLAUDE/memory 未写。", "",
             "## Muse schema 计数校正", "",
             "先前 Muse review 的 NOT_ACCEPTED 仍为最终状态。报告计数需按实际冻结代码纠正：旧 run143 schema 是 21 个 required、19 个固定等值 expected，另对 `terminal_id` 与 `reported_transport` 单独检查；不能沿用 19/16。run145 r5 是 27 个字段（25 固定值 + attestation class 与 terminal ID 单独检查）；run144 r5 是 26 个精确字段。canonical target 固定为 `claude-proxy/muse-spark-1.3-contributor-free`/`mcp`。测试 receipt 均是 `TEST_ONLY`，没有真实 Muse 服务认证。", "",
             "## 19 项保护矩阵", "",
             "| 项 | 状态 | 证据摘要 |", "|---:|---|---|"]
    for item in report["nineteen_protection_matrix"]:
        lines.append("| %d | %s | %s |" % (item["item"], item["status"], item["evidence"]))
    lines.extend(["", "完整数据、哈希与每轮测试状态见 [report.json](report.json)；源码/输入哈希和 mock boundaries 位于各自 revision `manifest.json`。", ""])
    (EVIDENCE / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = command_rows()
    if test_count("run144_tests") != 25 or test_count("run145_tests") != 24:
        raise RuntimeError("final suite test counts differ from audited expected counts")
    manifests = build_manifests()
    write_reports(manifests)
    print(json.dumps({"manifests": sorted(manifests), "final_attempt": 8,
                      "final_returncodes": [row["returncode"] for row in rows],
                      "report": str(EVIDENCE / "report.md"),
                      "mapping_rows": 30}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
