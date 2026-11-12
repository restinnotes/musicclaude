"""Offline integrity tests for run141 Thread resume r3. No provider is called."""

from __future__ import annotations

import argparse
import builtins
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
GO_PATH = ROOT / "runs" / "run141_thread_resume_r3" / "go.py"


def load_go():
    # Compile the already-read source instead of importing the legacy drivers or
    # writing a pyc into the workspace.
    source = GO_PATH.read_text(encoding="utf-8")
    namespace = {"__file__": str(GO_PATH), "__name__": "_run141_thread_resume_r3_test"}
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

        namespace = {"__file__": str(GO_PATH), "__name__": "_run141_import_probe"}
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


class Run141ThreadResumeTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT

    def test_full_mock_chain_exact_disk_proof_and_second_run_zero_submit(self):
        with tempfile.TemporaryDirectory(prefix="test_run141_thread_resume_r3_") as temp:
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
        with tempfile.TemporaryDirectory(prefix="test_run141_missing_") as temp:
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
        with tempfile.TemporaryDirectory(prefix="test_run141_tamper_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            output = folder / "outputs" / (GO["_slot_id"](slot) + ".txt")
            output.write_text(output.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(GO["IntegrityError"], "output SHA256 mismatch"):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_prompt_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="test_run141_prompt_tamper_") as temp:
            folder = Path(temp) / "evidence"
            slot, prompt, fingerprint, _ = self._mock_artifact(folder)
            path = folder / "prompts" / (GO["_slot_id"](slot) + ".txt")
            path.write_text(path.read_text(encoding="utf-8") + "tamper", encoding="utf-8")
            with self.assertRaisesRegex(GO["IntegrityError"], "prompt bytes/SHA256 mismatch"):
                GO["verify_disk_evidence"](folder, slot, prompt, fingerprint)

    def test_full_identity_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="test_run141_identity_tamper_") as temp:
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
        with self.assertRaisesRegex(GO["IntegrityError"], "binding SHA256"):
            GO["validate_musepack"](altered)
        altered = json.loads(json.dumps(pack, ensure_ascii=False))
        altered["template"]["text"] += "tamper"
        with self.assertRaisesRegex(GO["IntegrityError"], "template/source SHA256"):
            GO["validate_musepack"](altered)

    def test_muse_return_needs_real_transport_schema_and_exact_quotes(self):
        template = (self.root / GO["TEMPLATE_PATHS"]["ident"]).read_text(encoding="utf-8")
        template_sha = GO["sha256_bytes"]((self.root / GO["TEMPLATE_PATHS"]["ident"]).read_bytes())
        pack = GO["build_ident_musepack"](template, "MOCK_ONLY statement", 19,
                                         "ident:result", template_sha)
        result = {"transport": "mock", "provider": "Muse", "model": "external Muse",
                  "schema": {"schema_id": "ident/v1", "required_keys": ["guess"]},
                  "raw_response": '{"guess":"x"}',
                  "evidence_quotes": ["MOCK_ONLY statement"], "canonicalization": "raw_unverified"}
        with self.assertRaisesRegex(GO["IntegrityError"], "real transport"):
            GO["validate_muse_return"](pack, result)
        result["transport"] = "mcp"
        result["evidence_quotes"] = ["not an original quote"]
        with self.assertRaisesRegex(GO["IntegrityError"], "exact original"):
            GO["validate_muse_return"](pack, result)
        result["provider"] = "Muse fixture"
        result["model"] = "external Muse fixture"
        result["evidence_quotes"] = ["MOCK_ONLY statement"]
        validated = GO["validate_muse_return"](pack, result)
        self.assertEqual(validated["canonicalization"], "raw_unverified")

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

    def test_legacy_unknown_producer_is_preserved_without_fabrication(self):
        evidence = GO["preserve_legacy_producer"]({"model_key": "gpt56w", "status": "ok"})
        self.assertEqual(evidence, {"recorded": False, "value": None})

    def test_strict_preflight_is_pending_without_v4_and_writes_nothing(self):
        run_dir = ROOT / GO["RUN_DIR_REL"]
        before = sorted(str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file())
        report = GO["strict_preflight"](self.root)
        after = sorted(str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file())
        self.assertEqual(report["completion"], "COMPLETION_PENDING")
        self.assertEqual(report["transport"]["status"], "blocked")
        self.assertEqual(before, after)
        self.assertEqual(report["writes_to_run_directory"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
