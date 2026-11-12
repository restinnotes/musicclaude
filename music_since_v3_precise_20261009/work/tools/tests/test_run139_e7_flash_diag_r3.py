"""Offline-only run139 regression suite. Run with: python -I -B tools/tests/test_run139_e7_flash_diag_r3.py"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
GO_PATH = ROOT / "runs" / "run139_e7_flash_diag" / "go.py"
RUN_DIR = ROOT / "runs" / "run139_e7_flash_diag"
sys.dont_write_bytecode = True


def load_go(name: str = "run139_under_test"):
    spec = importlib.util.spec_from_file_location(name, GO_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MockCaller:
    """Writes all four exact artifacts. It never invokes a model, CLI, or network."""

    def __init__(self, *, stop_on: int | None = None, invalid_first: bool = False,
                 omit_terminal: bool = False, cache_only: bool = False):
        self.submissions = 0
        self.stop_on = stop_on
        self.invalid_first = invalid_first
        self.omit_terminal = omit_terminal
        self.cache_only = cache_only

    @staticmethod
    def _candidate_payloads(prompt: str) -> dict[str, str]:
        markers = (("a", "【甲】", "【乙】"), ("b", "【乙】", "【丙】"), ("c", "【丙】", None))
        result = {}
        for key, start, end in markers:
            piece = prompt.split(start, 1)[1]
            if end:
                piece = piece.split(end, 1)[0]
            result[key] = piece.strip()
        return result

    def _output(self, request: dict) -> str:
        go = load_go()
        step = request["step"]
        key = request["key"]
        if self.invalid_first and self.submissions == 1:
            return "not a JSON response"
        if step == "why":
            k = int(key[-1])
            if k % 4 == 0:
                value = {"differs": False, "sentence": "无"}
            else:
                value = {"differs": True, "sentence": "此前的低音在这里以更短的呼吸回来。"}
            return json.dumps(value, ensure_ascii=False)
        if step == "mech":
            return json.dumps([{
                "relation": "mock relation",
                "explains": [1, 2],
                "new_understanding": "mock new understanding",
            }], ensure_ascii=False)
        if step == "audit":
            return json.dumps({"class": "insight", "why": "mock audit evidence"}, ensure_ascii=False)
        if step == "surface":
            k = int(key[-1])
            prompt = request["prompt"]
            before = prompt.split("【上一段结束时屏幕上的内容】", 1)[1].split(
                "【这一段可以给读者的内容】", 1)[0]
            items = prompt.split("【这一段可以给读者的内容】", 1)[1]
            n_screen = len(re.findall(r"(?m)^S\d+\.", before))
            n_items = len(re.findall(r"(?m)^\d+\. \[", items))
            show_id = 2 if n_items >= 2 else 1
            extra_ids = [number for number in (3, 4) if number <= n_items]
            action_slot = k % 5
            if action_slot == 1:
                value = {"action": "更新", "keep": [], "show": [show_id],
                         "expand": extra_ids[:1], "recap": extra_ids[1:2], "why": "mock update"}
            elif action_slot == 2 and n_screen:
                value = {"action": "保持", "keep": ["S%d" % i for i in range(1, n_screen + 1)],
                         "show": [], "expand": [], "recap": [], "why": "mock keep"}
            elif action_slot == 3 and n_screen:
                value = {"action": "补充", "keep": ["S%d" % i for i in range(1, n_screen + 1)],
                         "show": [show_id], "expand": extra_ids[:1], "recap": extra_ids[1:2],
                         "why": "mock append"}
            elif action_slot == 0:
                value = {"action": "沉默", "keep": [], "show": [],
                         "expand": [], "recap": [], "why": "mock silence"}
            else:
                value = {"action": "更新", "keep": [], "show": [show_id],
                         "expand": extra_ids[:1], "recap": extra_ids[1:2], "why": "mock replace"}
            return json.dumps(value, ensure_ascii=False)
        if step == "compare":
            payloads = self._candidate_payloads(request["prompt"])
            values = {}
            for label, position in zip(("甲", "乙", "丙"), ("甲", "乙", "丙")):
                content = payloads[{"甲": "a", "乙": "b", "丙": "c"}[position]]
                line = next((line.strip() for line in content.splitlines() if line.strip()), "candidate")
                quote = line[:min(10, len(line))]
                values[label] = "“%s” 可见一个具体时刻。" % quote
            value = {
                "ranking": ["甲", "乙", "丙"],
                "best_moments": values,
                "worst_moments": values,
                "hindsight": {label: [] for label in ("甲", "乙", "丙")},
                "only_here": {label: "不可判" for label in ("甲", "乙", "丙")},
                "why": "mock compare output with source-grounded quotes.",
            }
            return json.dumps(value, ensure_ascii=False)
        raise AssertionError("unexpected mock step " + step)

    def __call__(self, request: dict):
        self.submissions += 1
        if self.cache_only:
            return {"parse_ok": True, "cached": True, "output": '{"differs":true}'}
        paths = {key: Path(value) for key, value in request["paths"].items()}
        for path in paths.values():
            path.parent.mkdir(parents=True, exist_ok=True)
        prompt_bytes = request["prompt"].encode("utf-8")
        prompt_sha = digest(prompt_bytes)
        output = self._output(request)
        output_bytes = output.encode("utf-8")
        paths["prompt"].write_bytes(prompt_bytes)
        paths["output"].write_bytes(output_bytes)
        status = "queue_stop" if self.stop_on == self.submissions else "completed"
        terminal = {
            "schema": request["schema"], "identity": request["identity"],
            "run_id": request["identity"]["run_id"], "namespace": request["identity"]["namespace"],
            "actual_model": request["requested_model"], "transport": "MOCK",
            "terminal_id": "mock-terminal-%06d" % self.submissions,
            "status": status, "exit_code": 0, "identity_verified": True,
        }
        terminal_bytes = (json.dumps(terminal, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if not self.omit_terminal:
            paths["terminal"].write_bytes(terminal_bytes)
        meta = {
            "schema": request["schema"], "identity": request["identity"],
            "run_id": request["identity"]["run_id"], "namespace": request["identity"]["namespace"],
            "logical_id": request["identity"]["logical_id"], "attempt": request["identity"]["attempt"],
            "step": request["step"], "key": request["key"],
            "requested_model": request["requested_model"], "actual_model": request["requested_model"],
            "prompt_version": request["prompt_version"], "driver_sha256": request["driver_sha256"],
            "prompt_sha256": prompt_sha, "output_sha256": digest(output_bytes),
            "terminal_sha256": digest(terminal_bytes) if not self.omit_terminal else "",
            "transport": "MOCK",
        }
        paths["meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")


class Run139Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="run139_e7_r3_")
        cls.out_dir = Path(cls.temp.name) / "mock-run"
        cls.caller = MockCaller()
        cls.go = load_go("run139_main_test")
        cls.first_result = cls.go.run_all(cls.out_dir, caller=cls.caller)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def clone_output(self, name: str) -> Path:
        target = Path(self.temp.name) / name
        shutil.copytree(self.out_dir, target)
        return target

    def test_import_has_no_environment_io_cli_or_source_import_effects(self):
        before_entries = sorted(path.name for path in RUN_DIR.iterdir())
        env_before = dict(os.environ)
        with mock.patch.dict(os.environ, {"RUN139_IMPORT_SENTINEL": "stable"}), \
                mock.patch("subprocess.run") as run, mock.patch("subprocess.Popen") as pop, \
                mock.patch.object(Path, "read_text", side_effect=AssertionError("import read a file")), \
                mock.patch.object(Path, "read_bytes", side_effect=AssertionError("import read bytes")), \
                mock.patch.object(Path, "write_text", side_effect=AssertionError("import wrote text")), \
                mock.patch.object(Path, "write_bytes", side_effect=AssertionError("import wrote bytes")), \
                mock.patch.object(Path, "mkdir", side_effect=AssertionError("import created a directory")):
            imported = load_go("run139_import_probe_r3")
            self.assertEqual(imported.CFG["gen"], "gflash")
            self.assertEqual(os.environ["RUN139_IMPORT_SENTINEL"], "stable")
            run.assert_not_called()
            pop.assert_not_called()
        self.assertEqual(dict(os.environ), env_before)
        self.assertEqual(sorted(path.name for path in RUN_DIR.iterdir()), before_entries)
        self.assertNotIn("run134_go", sys.modules)
        self.assertNotIn("run137_go", sys.modules)

    def test_config_and_canonical_self_flags_are_frozen(self):
        self.assertEqual(self.go.CFG["gen"], "gflash")
        self.assertEqual(self.go.CFG["chooser"], "gflash")
        self.assertEqual(self.go.CFG["auditors"], ("gflash", "luna_noweb"))
        self.assertEqual(self.go.CFG["judges"], ("gflash", "luna_noweb"))
        self.assertEqual(self.go.self_flag("c_gflash_s1", "gflash"), "a,c")
        self.assertEqual(self.go.self_flag("c_gflash_s1", "gflash_web"), "a,c")
        self.assertEqual(self.go.self_flag("c_gpro_s3", "gflash"), "a")
        self.assertEqual(self.go.self_flag("c_gflash_s1", "luna_noweb"), "否")

    def test_full_mock_rerun_adds_zero_submissions_and_stays_pending(self):
        first_count = self.caller.submissions
        second_caller = MockCaller()
        result = self.go.run_all(self.out_dir, caller=second_caller)
        self.assertEqual(second_caller.submissions, 0)
        self.assertEqual(result["new_mock_submissions"], 0)
        self.assertEqual(result["completion"], "COMPLETION_PENDING")
        self.assertGreater(first_count, 0)
        self.assertFalse((self.out_dir / "DONE").exists())
        self.assertTrue((self.out_dir / "COMPLETION_PENDING").exists())
        manifest = self.go.read_json(self.out_dir / "run_manifest.json")
        self.assertEqual(manifest["real_model_submissions"], 0)
        self.assertEqual(manifest["history_producer"].split(":", 1)[0], "unknown")
        self.assertEqual(manifest["config"]["gen"], "gflash")
        self.assertEqual(manifest["candidate_actual_identity_notes"]["b"]["generator_actual_identity"].split(":", 1)[0],
                         "unverified")

    def test_full_collections_exact_identities_packs_and_reader_content(self):
        why = self.go.read_json(self.out_dir / "why.json")["records"]
        mech_file = self.go.read_json(self.out_dir / "mech.json")
        mech = mech_file["records"]
        audits = mech_file["audits"]
        surface = self.go.read_json(self.out_dir / "surface.json")
        compares = self.go.read_json(self.out_dir / "compare.json")["records"]
        self.assertEqual([row["k"] for row in why], list(range(2, 24)))
        self.assertEqual([row["k"] for row in mech], list(range(1, 24)))
        self.assertEqual([row["k"] for row in surface["records"]], list(range(1, 24)))
        expected_audits = {(row["k"], idx, reviewer) for row in mech for idx, _ in enumerate(row["relations"])
                           for reviewer in self.go.CFG["auditors"]}
        self.assertEqual({(row["k"], row["relation_index"], row["reviewer"]) for row in audits}, expected_audits)
        expected_compares = {(set_name, judge, order) for set_name in self.go.BASELINE_MODELS
                             for judge in self.go.CFG["judges"] for order in range(3)}
        self.assertEqual({(row["set"], row["judge"], row["order_index"]) for row in compares}, expected_compares)
        for set_name in self.go.BASELINE_MODELS:
            for judge in self.go.CFG["judges"]:
                group = [row for row in compares if row["set"] == set_name and row["judge"] == judge]
                self.assertEqual(len(group), 3)
                for candidate in ("a", "b", "c"):
                    positions = [next(pos for pos, value in row["mapping"].items() if value == candidate)
                                 for row in group]
                    self.assertEqual(set(positions), set(self.go.POSITIONS))
        for filename, slot in (("muse_review_pack.json", "muse_pending"),
                               ("twow_review_pack.json", "twow_held")):
            pack = self.go.read_json(self.out_dir / filename)
            self.assertEqual(pack["slot"], slot)
            self.assertEqual(len(pack["tasks"]), 6)
            self.assertTrue(all(task["prompt"] and task["prompt_sha256"] and task["seed"] and
                                task["order"] and task["mapping"] for task in pack["tasks"]))
            self.assertTrue(all(self.go.PLACEHOLDER_RE.search(task["prompt"]) is None for task in pack["tasks"]))
        reader = (self.out_dir / "reading__gflash__op60.md").read_text(encoding="utf-8")
        registry = surface["items"]
        self.assertIn("## 展开可看（实际内容）", reader)
        self.assertIn("## 曲终回顾（实际内容）", reader)
        expanded = next(uid for row in surface["records"] for uid in row["expand"])
        recap = next(uid for row in surface["records"] for uid in row["recap"])
        self.assertIn(registry[expanded]["text"], reader)
        self.assertIn(registry[recap]["text"], reader)
        report = (self.out_dir / "report.md").read_text(encoding="utf-8")
        self.assertEqual(report.count("differs="), 22)
        for label in ("KEEP", "RETIRE", "REPLACE", "APPEND", "主 WHY", "重建锚", "COMPLETION_PENDING"):
            self.assertIn(label, report)

    def test_parser_failure_retry_appends_attempt_without_overwrite(self):
        out = Path(self.temp.name) / "retry-run"
        caller = MockCaller(invalid_first=True)
        pipeline = self.go.Pipeline(out, caller)
        pipeline.data = self.go._freeze_inputs(ROOT)
        out.mkdir()
        self.go.write_json(out / "freeze.json", pipeline.data["lock"])
        result = pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                                  '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why)
        self.assertEqual(result["attempt"], 1)
        self.assertEqual(caller.submissions, 2)
        calls = self.go.read_json(out / "call_index.json")["records"]
        self.assertEqual([record["attempt"] for record in calls], [0, 1])
        first_output = out / calls[0]["paths"]["output"]
        self.assertEqual(first_output.read_text(encoding="utf-8"), "not a JSON response")
        self.assertTrue((out / calls[1]["paths"]["output"]).is_file())

    def test_cache_only_claim_without_exact_artifacts_is_rejected(self):
        out = Path(self.temp.name) / "cache-only"
        caller = MockCaller(cache_only=True)
        with self.assertRaises(self.go.IntegrityError):
            self.go.run_all(out, caller=caller)
        self.assertEqual(caller.submissions, 1)
        self.assertTrue((out / "FAILED").exists())

    def test_queue_stop_blocks_every_following_submission_and_stage(self):
        out = Path(self.temp.name) / "queue-stop"
        caller = MockCaller(stop_on=1)
        with self.assertRaises(self.go.QueueStopped):
            self.go.run_all(out, caller=caller)
        self.assertEqual(caller.submissions, 1)
        self.assertTrue((out / "queue_stop.json").exists())
        self.assertTrue((out / "FAILED").exists())
        self.assertFalse((out / "why.json").exists())
        second = MockCaller()
        with self.assertRaises(self.go.QueueStopped):
            self.go.run_all(out, caller=second)
        self.assertEqual(second.submissions, 0)

    def test_exact_artifact_tamper_is_rejected_before_resume(self):
        for name, file_key, replacement in (
                ("prompt", "prompt", b"tampered prompt"),
                ("output", "output", b'{"parse_ok":true}')):
            with self.subTest(name=name):
                out = self.clone_output("tamper-" + name)
                index = self.go.read_json(out / "call_index.json")
                path = out / index["records"][0]["paths"][file_key]
                path.write_bytes(replacement)
                caller = MockCaller()
                with self.assertRaises(self.go.IntegrityError):
                    self.go.run_all(out, caller=caller)
                self.assertEqual(caller.submissions, 0)
                self.assertTrue((out / "FAILED").exists())

    def test_pack_missing_and_tamper_are_rejected_without_rebuilding(self):
        for mode in ("missing", "tamper"):
            with self.subTest(mode=mode):
                out = self.clone_output("pack-" + mode)
                pack_path = out / "muse_review_pack.json"
                if mode == "missing":
                    pack_path.unlink()
                else:
                    pack_path.write_text(pack_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
                caller = MockCaller()
                with self.assertRaises(self.go.IntegrityError):
                    self.go.run_all(out, caller=caller)
                self.assertEqual(caller.submissions, 0)

    def test_source_tamper_is_rejected_using_an_isolated_fixture_root(self):
        fixture = Path(self.temp.name) / "fixture-source"
        for relative in list(self.go.INPUT_PATHS.values()) + list(self.go.TEMPLATE_PATHS.values()):
            source = ROOT / relative
            target = fixture / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        out = Path(self.temp.name) / "source-tamper-run"
        caller = MockCaller()
        self.go.run_all(out, caller=caller, source_root=fixture)
        original_count = caller.submissions
        history = fixture / self.go.INPUT_PATHS["history"]
        history.write_bytes(history.read_bytes() + b"\n")
        next_caller = MockCaller()
        with self.assertRaises(self.go.IntegrityError):
            self.go.run_all(out, caller=next_caller, source_root=fixture)
        self.assertEqual(next_caller.submissions, 0)
        self.assertGreater(original_count, 0)

    def test_duplicate_reviewer_and_order_identity_sets_are_rejected(self):
        pipeline = self.go.Pipeline(Path(self.temp.name) / "collection-check", MockCaller())
        why = [{"k": k} for k in range(2, 24)]
        mech = [{"k": k, "relations": []} for k in range(1, 24)]
        surface = [{"k": k} for k in range(1, 24)]
        mappings = self.go._expected_compare_mapping()
        compares = []
        for set_name in sorted(self.go.BASELINE_MODELS):
            for judge in self.go.CFG["judges"]:
                for order in range(3):
                    compares.append({"set": set_name, "judge": judge, "order_index": order,
                                     "mapping": mappings[(set_name, judge, order)]})
        pipeline._validate_collection(why, mech, [], surface, compares, [{}] * 6)
        with self.assertRaises(self.go.IntegrityError):
            pipeline._validate_collection(why, mech, [], surface, compares + [compares[0]], [{}] * 6)
        broken = [dict(row) for row in compares]
        broken[0]["mapping"] = {"甲": "a", "乙": "a", "丙": "c"}
        with self.assertRaises(self.go.IntegrityError):
            pipeline._validate_collection(why, mech, [], surface, broken, [{}] * 6)
        mech_with_rel = [dict(row) for row in mech]
        mech_with_rel[0] = {"k": 1, "relations": [{"relation": "r"}]}
        one_reviewer = [{"k": 1, "relation_index": 0, "reviewer": "gflash"}]
        with self.assertRaises(self.go.IntegrityError):
            pipeline._validate_collection(why, mech_with_rel, one_reviewer, surface, compares, [{}] * 6)

    def test_pack_validator_rejects_placeholder_and_missing_task_id(self):
        pipeline = self.go.Pipeline(Path(self.temp.name) / "pack-check", MockCaller())
        pipeline.data = self.go._freeze_inputs(ROOT)
        readings = {
            "a": (self.out_dir / "reading__gflash__op60.md").read_text(encoding="utf-8"),
            "b": (self.out_dir / "reading__run124B__op60.md").read_text(encoding="utf-8"),
        }
        sets = pipeline._candidate_sets(readings)
        tasks = pipeline._make_compare_tasks(sets)
        pack = pipeline._pack("muse_pending", tasks)
        pipeline._validate_pack(pack, tasks, "muse_pending")
        broken = json.loads(json.dumps(pack, ensure_ascii=False))
        broken["tasks"][0]["prompt"] += "\n{{REVIEWER}}"
        broken["tasks"][0]["prompt_sha256"] = self.go.sha256_text(broken["tasks"][0]["prompt"])
        expected_with_placeholder = list(tasks)
        expected_with_placeholder[0] = dict(tasks[0])
        expected_with_placeholder[0]["prompt"] = broken["tasks"][0]["prompt"]
        expected_with_placeholder[0]["prompt_sha256"] = broken["tasks"][0]["prompt_sha256"]
        with self.assertRaises(self.go.IntegrityError):
            pipeline._validate_pack(broken, expected_with_placeholder, "muse_pending")
        missing = json.loads(json.dumps(pack, ensure_ascii=False))
        missing["tasks"].pop()
        with self.assertRaises(self.go.IntegrityError):
            pipeline._validate_pack(missing, tasks, "muse_pending")

    def test_muse_cannot_be_ingested_without_external_identity_verifier_and_twow_stays_held(self):
        muse_pack = self.go.read_json(self.out_dir / "muse_review_pack.json")
        fake_results = [{"task_id": task["task_id"]} for task in muse_pack["tasks"]]
        with self.assertRaises(self.go.RealExecutionBlocked):
            self.go.validate_external_review_results(muse_pack, fake_results, "muse")
        twow_pack = self.go.read_json(self.out_dir / "twow_review_pack.json")
        with self.assertRaises(self.go.QueueStopped):
            self.go.validate_external_review_results(twow_pack, [], "gpt56w")

    def test_missing_terminal_identity_is_rejected_and_producer_stays_unknown(self):
        frozen = self.go._freeze_inputs(ROOT)
        self.assertTrue(frozen["history_producer"].startswith("unknown"))
        out = Path(self.temp.name) / "missing-terminal"
        caller = MockCaller(omit_terminal=True)
        pipeline = self.go.Pipeline(out, caller)
        pipeline.data = frozen
        out.mkdir()
        self.go.write_json(out / "freeze.json", frozen["lock"])
        with self.assertRaises(self.go.IntegrityError):
            pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                             '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why)
        self.assertEqual(caller.submissions, 1)

    def test_direct_real_path_blocks_before_creating_real_run_outputs(self):
        before = sorted(path.name for path in RUN_DIR.iterdir())
        caller = MockCaller()
        with self.assertRaises(self.go.RealExecutionBlocked):
            self.go.run_all(caller=None)
        self.assertEqual(caller.submissions, 0)
        self.assertEqual(sorted(path.name for path in RUN_DIR.iterdir()), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
