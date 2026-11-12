"""Offline integrity tests for run143 Thread resume r4. No provider is called."""

from __future__ import annotations

import argparse
import builtins
import difflib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
GO_PATH = ROOT / "runs" / "run143_thread_resume_r4" / "go.py"


def load_go():
    # Compile the already-read source instead of importing the legacy drivers or
    # writing a pyc into the workspace.
    source = GO_PATH.read_text(encoding="utf-8")
    namespace = {"__file__": str(GO_PATH), "__name__": "_run143_thread_resume_r4_test"}
    exec(compile(source, str(GO_PATH), "exec"), namespace)
    return namespace


GO = load_go()


class ImportSideEffectsTests(unittest.TestCase):
    def test_import_has_no_environment_file_cli_or_write_side_effects(self):
        source = GO_PATH.read_bytes()
        before_env = dict(os.environ)
        preloaded = (argparse, difflib, hashlib, json, re, sys, Path)
        self.assertTrue(preloaded)

        class ReadOnlyEnv(dict):
            def __setitem__(self, key, value):
                raise AssertionError("environment mutation during import")

            def __delitem__(self, key):
                raise AssertionError("environment mutation during import")

            def update(self, *args, **kwargs):
                raise AssertionError("environment mutation during import")

        namespace = {"__file__": str(GO_PATH), "__name__": "_run143_import_probe"}
        with patch.object(os, "environ", ReadOnlyEnv(before_env)), \
                patch.object(builtins, "open", side_effect=AssertionError("file I/O during import")), \
                patch.object(Path, "read_text", side_effect=AssertionError("file I/O during import")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("file I/O during import")), \
                patch.object(Path, "write_text", side_effect=AssertionError("write during import")), \
                patch.object(Path, "write_bytes", side_effect=AssertionError("write during import")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("CLI during import")), \
                patch.object(subprocess, "run", side_effect=AssertionError("CLI during import")), \
                patch.object(os, "system", side_effect=AssertionError("CLI during import")):
            exec(compile(source, str(GO_PATH), "exec"), namespace)
        self.assertEqual(dict(os.environ), before_env)


class Run143ThreadResumeTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT

    def test_full_mock_chain_exact_disk_proof_and_second_run_zero_submit(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_thread_resume_r4_") as temp:
            report = GO["run_mock"](self.root, Path(temp) / "mock-evidence")
            self.assertEqual(report["completion"], "COMPLETION_PENDING")
            self.assertEqual(report["mock_chain_validation"], "PASS")
            self.assertTrue(report["exactdiskproof"])
            self.assertTrue(report["secondrun0newsubmit"])
            self.assertEqual(report["second_run_new_submissions"], 0)
            self.assertEqual(report["chain_count"], 4)
            self.assertEqual(report["steps_per_chain"], 23)
            self.assertTrue(report["ident_set_exact"])
            self.assertTrue(report["compare_set_exact"])
            self.assertEqual(report["muse_real_return_count"], 0)
            self.assertEqual(report["real_model_submissions"], 0)
            self.assertEqual(report["generation_plan"]["status"], "HELD_NO_REAL_SUBMISSIONS")
            self.assertEqual(report["review_plan"]["reviewers"], ["gpt56w", "gpt6w", "gflash", "luna_noweb", "muse_external"])
            self.assertEqual(report["music_acceptance"], "NOT_PERFORMED")

    def _mock_artifact(self, folder: Path):
        beads, _, _ = GO["load_frozen_inputs"](self.root)
        fingerprint = GO["build_fingerprint"](self.root)
        template = (self.root / GO["TEMPLATE_PATHS"]["step_v2"]).read_text(encoding="utf-8")
        prompt = GO["build_step_prompt"](template, 1, [], beads)
        slot = {"stage": "step", "chain_id": "v2_gpt56w", "version": "v2",
                "model_key": "gpt56w", "k": 1}
        task = {"slot": slot, "prompt": prompt, "template_sha256": fingerprint["templates"]["step_v2"],
                "source_sha256": "frozen-source-test"}
        raw = GO["_mock_response"](task)
        proof = GO["_create_mock_artifact"](folder, task, fingerprint, raw)
        return slot, prompt, fingerprint, proof

    def test_missing_artifact_is_not_reused(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_missing_") as temp:
            Path(temp, "cache_step.json").write_text('{"records":[{"status":"ok"}]}', encoding="utf-8")
            beads, _, _ = GO["load_frozen_inputs"](self.root)
            fingerprint = GO["build_fingerprint"](self.root)
            template = (self.root / GO["TEMPLATE_PATHS"]["step_v2"]).read_text(encoding="utf-8")
            prompt = GO["build_step_prompt"](template, 1, [], beads)
            slot = {"stage": "step", "chain_id": "v2_gpt56w", "version": "v2",
                    "model_key": "gpt56w", "k": 1}
            with self.assertRaisesRegex(GO["IntegrityError"], "missing metadata"):
                GO["verify_disk_evidence"](Path(temp), slot, prompt, fingerprint)

    def test_tampered_output_sha_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_tamper_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            output = folder / "outputs" / (GO["_slot_id"](slot) + ".txt")
            output.write_text(output.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(GO["IntegrityError"], "output SHA256 mismatch"):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_prompt_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_prompt_tamper_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            path = folder / "prompts" / (GO["_slot_id"](slot) + ".txt")
            path.write_text(path.read_text(encoding="utf-8") + "tamper", encoding="utf-8")
            with self.assertRaisesRegex(GO["IntegrityError"], "prompt bytes/SHA256 mismatch"):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_full_identity_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_identity_tamper_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            path = folder / "meta" / (GO["_slot_id"](slot) + ".json")
            meta = json.loads(path.read_text(encoding="utf-8"))
            meta["identity"]["model_key"] = "gpt6w"
            path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(GO["IntegrityError"], "identity does not match"):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_duplicate_success_in_same_slot_is_ambiguous(self):
        slot = {"stage": "step", "chain_id": "v2_gpt56w", "version": "v2",
                "model_key": "gpt56w", "k": 1}
        records = [{"slot": slot, "status": "ok", "source_run": "r1"},
                   {"slot": slot, "status": "ok", "source_run": "r1-retry"}]
        with self.assertRaisesRegex(GO["IntegrityError"], "multiple successful"):
            GO["matching_successes"](records, slot)

    def test_ambiguous_success_sources_from_two_runs_are_rejected(self):
        slot = {"stage": "step", "chain_id": "v3_gpt6w", "version": "v3",
                "model_key": "gpt6w", "k": 9}
        sources = [{"slot": slot, "status": "ok", "source_run": "run133"},
                   {"slot": slot, "status": "ok", "source_run": "run136"}]
        with self.assertRaisesRegex(GO["IntegrityError"], "ambiguous source"):
            GO["matching_successes"](sources, slot)

    def test_strict_sets_detect_missing_extra_and_duplicate_even_when_counts_match(self):
        expected = [("gpt56w", 0, "gflash"), ("gpt56w", 1, "gflash")]
        GO["assert_exact_set"](expected, list(expected), "compare")
        with self.assertRaisesRegex(GO["IntegrityError"], "identity set"):
            GO["assert_exact_set"](expected, [("gpt56w", 0, "gflash"), ("gpt6w", 1, "gflash")], "compare")
        with self.assertRaisesRegex(GO["IntegrityError"], "duplicated"):
            GO["assert_exact_set"](expected, [expected[0], expected[0]], "compare")

    def test_musepack_tampering_and_file_read_reference_are_rejected(self):
        template = (self.root / GO["TEMPLATE_PATHS"]["ident"]).read_text(encoding="utf-8")
        template_sha = GO["sha256_bytes"]((self.root / GO["TEMPLATE_PATHS"]["ident"]).read_bytes())
        pack = GO["build_ident_musepack"](template, "MOCK_ONLY statement", 42,
                                         "ident:fixture", template_sha)
        GO["validate_musepack"](pack)
        altered = json.loads(json.dumps(pack, ensure_ascii=False))
        altered["mapping"]["STATEMENT"] = "tampered"
        with self.assertRaisesRegex(GO["IntegrityError"], "mapping"):
            GO["validate_musepack"](altered)
        altered = json.loads(json.dumps(pack, ensure_ascii=False))
        altered["source_path"] = "secret.txt"
        with self.assertRaisesRegex(GO["IntegrityError"], "read files"):
            GO["validate_musepack"](altered)
        altered = json.loads(json.dumps(pack, ensure_ascii=False))
        altered["seed"] += 1
        with self.assertRaisesRegex(GO["IntegrityError"], "candidate mapping|binding SHA256"):
            GO["validate_musepack"](altered)
        altered = json.loads(json.dumps(pack, ensure_ascii=False))
        altered["template"]["text"] += "tamper"
        with self.assertRaisesRegex(GO["IntegrityError"], "template/source SHA256"):
            GO["validate_musepack"](altered)

    def test_muse_raw_return_is_unverified_and_actual_entry_needs_trusted_archive_receipt(self):
        template = (self.root / GO["TEMPLATE_PATHS"]["ident"]).read_text(encoding="utf-8")
        template_sha = GO["sha256_bytes"]((self.root / GO["TEMPLATE_PATHS"]["ident"]).read_bytes())
        pack = GO["build_ident_musepack"](template, "MOCK_ONLY statement", 19,
                                         "ident:result", template_sha)
        result = {"transport": "mcp", "provider": "Muse", "model": "external Muse",
                  "schema": {"schema_id": "caller-selected", "required_keys": []},
                  "raw_response": json.dumps({"guess": "说不准", "confidence": 50,
                                               "also_fits": [GO["CANDIDATES"][0]],
                                               "why": "“MOCK_ONLY statement” supports uncertainty."}, ensure_ascii=False),
                  "evidence_quotes": ["MOCK_ONLY statement"], "canonicalization": "raw_unverified"}
        with self.assertRaises(GO["CompletionPending"]):
            GO["validate_muse_return"](pack, result)
        raw_only = GO["validate_muse_raw_unverified"](pack, result)
        self.assertEqual(raw_only["status"], "raw_unverified")
        self.assertEqual(raw_only["schema_id"], "THREAD_IDENT_v0")
        self.assertEqual(raw_only["real_return_count"], 0)
        self.assertEqual(raw_only["music_acceptance"], "NOT_PERFORMED")

        malformed = dict(result, raw_response="{}")
        with self.assertRaisesRegex(GO["IntegrityError"], "THREAD_IDENT_v0"):
            GO["validate_muse_raw_unverified"](pack, malformed)
        wrong_guess = dict(result, raw_response=json.dumps({"guess": "made up", "confidence": 20,
                                                            "also_fits": [], "why": "unsupported"}))
        with self.assertRaisesRegex(GO["IntegrityError"], "guess"):
            GO["validate_muse_raw_unverified"](pack, wrong_guess)
        bool_confidence = dict(result, raw_response=json.dumps({"guess": "说不准", "confidence": True,
                                                               "also_fits": [], "why": "not exact int"}, ensure_ascii=False))
        with self.assertRaisesRegex(GO["IntegrityError"], "confidence"):
            GO["validate_muse_raw_unverified"](pack, bool_confidence)
        duplicate_fits = dict(result, raw_response=json.dumps({"guess": "说不准", "confidence": 50,
                                                              "also_fits": [GO["CANDIDATES"][0], GO["CANDIDATES"][0]],
                                                              "why": "duplicate"}, ensure_ascii=False))
        with self.assertRaisesRegex(GO["IntegrityError"], "also_fits"):
            GO["validate_muse_raw_unverified"](pack, duplicate_fits)

        raw_bytes = result["raw_response"].encode("utf-8")
        def mock_archive_verifier(actual_pack, actual_bytes):
            self.assertEqual(actual_pack["task_id"], pack["task_id"])
            self.assertEqual(actual_bytes, raw_bytes)
            return {"receipt_schema": "muse_archive_receipt_v1", "verified": True,
                    "bytes_verified": True, "task_id": pack["task_id"],
                    "logical_task_id": pack["task_id"], "request_id": pack["task_id"],
                    "source_sha256": pack["source"]["sha256"],
                    "template_sha256": pack["template"]["sha256"],
                    "mapping_sha256": GO["sha256_text"](GO["canonical_json"](pack["mapping"])),
                    "seed": pack["seed"], "prompt_sha256": pack["prompt_sha256"],
                    "raw_response_sha256": GO["sha256_bytes"](actual_bytes),
                    "raw_response_size": len(actual_bytes), "terminal_status": "completed",
                    "terminal_id": "TEST_ONLY_mock_terminal", "requested_provider": pack["provider"],
                    "requested_model": pack["model"], "requested_transport": pack["transport"],
                    "reported_provider": pack["provider"], "reported_model": pack["model"],
                    "reported_transport": "mcp"}
        attested = GO["validate_muse_return"](pack, result, mock_archive_verifier)
        self.assertEqual(attested["status"], "external_return_identity_attested")
        self.assertEqual(attested["real_return_count"], 0)
        self.assertEqual(attested["music_acceptance"], "NOT_PERFORMED")

        def bad_archive_verifier(actual_pack, actual_bytes):
            receipt = mock_archive_verifier(actual_pack, actual_bytes)
            receipt["raw_response_sha256"] = "0" * 64
            return receipt
        with self.assertRaisesRegex(GO["IntegrityError"], "raw_response_sha256"):
            GO["validate_muse_return"](pack, result, bad_archive_verifier)

    def test_thread_compare_uses_frozen_schema_and_candidate_specific_exact_quotes(self):
        template = (self.root / GO["TEMPLATE_PATHS"]["compare"]).read_text(encoding="utf-8")
        template_sha = GO["sha256_bytes"]((self.root / GO["TEMPLATE_PATHS"]["compare"]).read_bytes())
        a = "A_unique_phrase occurs only in candidate A."
        b = "B_unique_phrase occurs only in candidate B."
        mapping = {"WORK": GO["WORK_NAME"], "BEADS": "MOCK_ONLY bead text", "A": a, "B": b}
        pack = GO["build_compare_musepack"](template, GO["WORK_NAME"], "MOCK_ONLY bead text",
                                            a, b, mapping, 7, "compare:fixture", template_sha)
        good = {"better": "A",
                "specificity": {"A": "“A_unique_phrase” is specific.", "B": "“B_unique_phrase” is specific."},
                "grounding": {"A": "“A_unique_phrase” has a concrete basis.", "B": "“B_unique_phrase” has a concrete basis."},
                "flattened": {"A": ["“A_unique_phrase” is flattened here."], "B": []},
                "openness": {"A": "“A_unique_phrase” leaves room.", "B": "“B_unique_phrase” leaves room."},
                "why": "A cites “A_unique_phrase”; B cites “B_unique_phrase”."}
        raw = json.dumps(good, ensure_ascii=False)
        result = {"raw_response": raw, "schema": {"schema_id": "attacker", "required_keys": []},
                  "provider": "claimed Muse", "transport": "claimed mcp"}
        parsed = GO["validate_muse_raw_unverified"](pack, result)
        self.assertEqual(parsed["status"], "raw_unverified")
        self.assertEqual(parsed["parsed"], good)
        self.assertEqual(parsed["real_return_count"], 0)

        invalid_object = dict(good)
        invalid_object["specificity"] = {"A": "A has no quote", "B": "“B_unique_phrase” is specific."}
        with self.assertRaisesRegex(GO["IntegrityError"], "citation"):
            GO["validate_muse_raw_unverified"](pack, dict(result, raw_response=json.dumps(invalid_object, ensure_ascii=False)))
        wrong_candidate = dict(good)
        wrong_candidate["grounding"] = {"A": "“B_unique_phrase” appears here.",
                                         "B": "“B_unique_phrase” has a basis."}
        with self.assertRaisesRegex(GO["IntegrityError"], "candidate A"):
            GO["validate_muse_raw_unverified"](pack, dict(result, raw_response=json.dumps(wrong_candidate, ensure_ascii=False)))
        mixed_quote = dict(good)
        mixed_quote["openness"] = {"A": "“A_unique_phrase” and “invented phrase”.",
                                   "B": "“B_unique_phrase” leaves room."}
        with self.assertRaisesRegex(GO["IntegrityError"], "candidate A"):
            GO["validate_muse_raw_unverified"](pack, dict(result, raw_response=json.dumps(mixed_quote, ensure_ascii=False)))
        bad_flattened = dict(good)
        bad_flattened["flattened"] = {"A": "not a list", "B": []}
        with self.assertRaisesRegex(GO["IntegrityError"], "lists"):
            GO["validate_muse_raw_unverified"](pack, dict(result, raw_response=json.dumps(bad_flattened, ensure_ascii=False)))

    def test_response_and_metadata_parsing_reject_prefix_trailer_duplicates_and_nonfinite(self):
        good_object = '{"x":1}'
        good_array = '[{"x":1}]'
        self.assertEqual(GO["extract_json"]("  " + good_object + "  "), {"x": 1})
        self.assertEqual(GO["extract_json"]("```json\n" + good_array + "\n```"), [{"x": 1}])
        for raw in ("prefix " + good_object, good_object + " trailing", good_object + good_object,
                    '{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}', '"scalar"'):
            with self.subTest(raw=raw):
                with self.assertRaises(GO["IntegrityError"]):
                    GO["extract_json"](raw)
        with tempfile.TemporaryDirectory(prefix="test_run143_strict_meta_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            path = folder / "meta" / (GO["_slot_id"](slot) + ".json")
            path.write_text('{"status":"ok","status":"ok"}', encoding="utf-8")
            with self.assertRaises((ValueError, GO["IntegrityError"])):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_mode_request_and_full_mock_producer_tuple_are_bound_to_slot(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_mode_binding_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, proof = self._mock_artifact(folder)
            base = proof["meta"]
            missing_mode = dict(base)
            missing_mode.pop("execution_mode")
            with self.assertRaisesRegex(GO["IntegrityError"], "exact value mock_only"):
                GO["_validate_identity"](missing_mode, slot, fingerprint)
            unknown_mode = dict(base, execution_mode="MOCK")
            with self.assertRaisesRegex(GO["IntegrityError"], "exact value mock_only"):
                GO["_validate_identity"](unknown_mode, slot, fingerprint)
            real_mode = dict(base, execution_mode="real")
            with self.assertRaises(GO["CompletionPending"]):
                GO["_validate_identity"](real_mode, slot, fingerprint)

            wrong_request = json.loads(json.dumps(base))
            wrong_request["identity"]["request_id"] = "mock:wrong-slot"
            with self.assertRaisesRegex(GO["IntegrityError"], "identity does not match"):
                GO["_validate_identity"](wrong_request, slot, fingerprint)
            for field in ("model", "kind", "adapter", "producer_revision", "transport", "provider", "slot_sha256"):
                with self.subTest(field=field):
                    altered = json.loads(json.dumps(base))
                    altered["producer_identity"][field] = "MOCK_ONLY forged label"
                    with self.assertRaisesRegex(GO["IntegrityError"], "producer tuple"):
                        GO["_validate_identity"](altered, slot, fingerprint)

    def test_real_preflight_only_checks_presence_and_direct_real_entry_writes_nothing(self):
        with tempfile.TemporaryDirectory(prefix="test_run143_real_preflight_") as temp:
            root = Path(temp)
            tools_dir = root / "tools"
            tools_dir.mkdir()
            absent = GO["check_v4_transport"](root)
            self.assertEqual(absent["v4"], "absent")
            malicious = tools_dir / "experiment_calls_v4.py"
            malicious.write_text("from pathlib import Path\nPath('EXECUTED').write_text('yes')\n", encoding="utf-8")
            (tools_dir / "experiment_calls_v5.py").write_text("# partial", encoding="utf-8")
            (tools_dir / "experiment_calls_v6.py").write_text("# in flight", encoding="utf-8")
            before = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in root.rglob("*") if path.is_file()}
            present = GO["check_v4_transport"](root)
            self.assertEqual(present["v4"], "present_unverified")
            self.assertEqual(present["v5"], "partial_unusable")
            self.assertEqual(present["v6"], "in_flight_not_auto_adopted")
            self.assertEqual(present["dependencies"], "not imported or verified")
            after = {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertFalse((root / "EXECUTED").exists())

        run_dir = ROOT / GO["RUN_DIR_REL"]
        before_run = {str(path.relative_to(run_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
                      for path in run_dir.rglob("*") if path.is_file()}
        output = io.StringIO()
        with redirect_stdout(output):
            rc = GO["main"](["--real"])
        report = json.loads(output.getvalue())
        self.assertEqual(rc, 3)
        self.assertEqual(report["completion"], "COMPLETION_PENDING")
        self.assertEqual(report["real_model_submissions"], 0)
        self.assertEqual(report["writes_to_run_directory"], 0)
        self.assertEqual(report["transport"]["status"], "blocked")
        after_run = {str(path.relative_to(run_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in run_dir.rglob("*") if path.is_file()}
        self.assertEqual(after_run, before_run)

    def test_queue_stop_stops_current_remaining_jobs_and_all_later_stages(self):
        called = []

        def generation():
            called.append("generation")
            return {"status": "ok", "jobs": ["g1", "g2"]}

        def match():
            called.append("match")
            return {"status": "failed", "queue_stop": True, "jobs": ["m1"], "failed_job": "m1"}

        def center():
            called.append("center")
            return {"status": "ok", "jobs": ["c1"]}

        report = GO["run_stages"](["generation", "match", "center"],
                                  {"generation": generation, "match": match, "center": center})
        self.assertEqual(called, ["generation", "match"])
        self.assertTrue(report["queue_stop"])
        self.assertEqual(report["stages"][1]["remaining_jobs"], "stopped")
        self.assertEqual(report["stages"][2]["status"], "stopped_before_start")

    def test_no_longer_valid_without_match_evidence_blocks_history(self):
        parsed = {"new_changes": [], "no_longer_valid": ["old statement"], "thread": "MOCK_ONLY"}
        with self.assertRaisesRegex(GO["IntegrityError"], "provenance-backed"):
            GO["update_inventory"]([], parsed, 2, None)

    def test_no_longer_valid_requires_an_exact_source_match(self):
        inventory = [{"change": "old statement", "from": "k1", "added_step": 1},
                     {"change": "another statement", "from": "k2", "added_step": 2}]
        parsed = {"new_changes": [], "no_longer_valid": ["old statement"], "thread": "MOCK_ONLY"}
        with self.assertRaisesRegex(GO["IntegrityError"], "exactly match"):
            GO["update_inventory"](inventory, parsed, 3, [{"quote": "old statement ", "match": 1}])
        after = GO["update_inventory"](inventory, parsed, 3,
                                       [{"quote": "old statement", "match": 1}])
        self.assertEqual(after, [inventory[1]])

    def test_legacy_unknown_producer_is_preserved_without_fabrication(self):
        evidence = GO["preserve_legacy_producer"]({"model_key": "gpt56w", "status": "ok"})
        self.assertEqual(evidence, {"recorded": False, "value": None})

    def test_strict_preflight_is_pending_without_v4_acceptance_and_writes_nothing(self):
        run_dir = ROOT / GO["RUN_DIR_REL"]
        before = sorted(str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file())
        report = GO["strict_preflight"](self.root)
        after = sorted(str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file())
        self.assertEqual(report["completion"], "COMPLETION_PENDING")
        self.assertEqual(report["transport"]["status"], "blocked")
        self.assertIn("present_unverified", report["transport"]["v4"])
        self.assertIn("partial_unusable", report["transport"]["v5"])
        self.assertIn("in_flight_not_auto_adopted", report["transport"]["v6"])
        self.assertEqual(before, after)
        self.assertEqual(report["writes_to_run_directory"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
