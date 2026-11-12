"""Offline-only run146 regression suite. Run with: python -I -B tools/tests/test_run146_e7_flash_diag_r6.py"""
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
GO_PATH = ROOT / "runs" / "run146_e7_flash_diag_r6" / "go.py"
RUN_DIR = ROOT / "runs" / "run146_e7_flash_diag_r6"
sys.dont_write_bytecode = True


def load_go(name: str = "run146_under_test"):
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
            source_quotes = {}
            for label, position in zip(("甲", "乙", "丙"), ("甲", "乙", "丙")):
                content = payloads[{"甲": "a", "乙": "b", "丙": "c"}[position]]
                line = next((line.strip() for line in content.splitlines() if line.strip()), "candidate")
                quote = line[:min(10, len(line))]
                source_quotes[label] = quote
                values[label] = "“%s” 可见一个具体时刻。" % quote
            value = {
                "ranking": ["甲", "乙", "丙"],
                "best_moments": values,
                "worst_moments": values,
                "hindsight": {label: [] for label in ("甲", "乙", "丙")},
                "only_here": {label: "“%s” 是此处独有的具体表达。" % source_quotes[label]
                              for label in ("甲", "乙", "丙")},
                "why": "甲写到“%s”，乙写到“%s”，丙写到“%s”。" %
                       (source_quotes["甲"], source_quotes["乙"], source_quotes["丙"]),
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
            "sampling_identity": request["sampling_identity"],
            "new_sample_reason": request["new_sample_reason"],
            "terminal_sha256": digest(terminal_bytes) if not self.omit_terminal else "",
            "transport": "MOCK", "request_identity": request["request_identity"],
        }
        paths["meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                 encoding="utf-8")


class Run146Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="run146_e7_r5_")
        cls.out_dir = Path(cls.temp.name) / "mock-run"
        cls.caller = MockCaller()
        cls.go = load_go("run146_main_test")
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
            imported = load_go("run146_import_probe_r5")
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
        self.assertEqual(first_count, 126)
        self.assertEqual(self.first_result["new_mock_submissions"], 126)
        second_caller = MockCaller()
        result = self.go.run_all(self.out_dir, caller=second_caller)
        self.assertEqual(second_caller.submissions, 0)
        self.assertEqual(result["new_mock_submissions"], 0)
        self.assertEqual(result["completion"], "COMPLETION_PENDING")
        self.assertGreater(first_count, 0)
        self.assertFalse((self.out_dir / "DONE").exists())

    def test_current_model_version_prompt_and_input_producer_conflicts_stop_before_write(self):
        caller = MockCaller()
        pipeline = self.go.Pipeline(self.out_dir, caller)
        pipeline.data = self.go._freeze_inputs(ROOT)
        pipeline._load_calls()
        record = next(row for row in pipeline.calls if row["step"] == "why")
        output = self.out_dir / record["paths"]["output"]
        before_output = output.read_bytes()
        before_index = (self.out_dir / "call_index.json").read_bytes()
        base = ("why", record["key"], record["requested_model"], '{"immutable prompt"}',
                record["prompt_version"], self.go.parse_why)
        variants = [base[:2] + ("luna_noweb",) + base[3:],
                    base[:4] + ("changed_version",) + base[5:],
                    base[:3] + ('{"changed prompt bytes"}',) + base[4:]]
        for args in variants:
            with self.subTest(model=args[2], version=args[4], prompt=args[3]):
                with self.assertRaisesRegex(self.go.IntegrityError, "current request identity conflicts"):
                    pipeline.execute(*args)
        pipeline.data["lock"]["source_sha256"] = {"changed": "0" * 64}
        with self.assertRaisesRegex(self.go.IntegrityError, "current request identity conflicts"):
            pipeline.execute(*base)
        self.assertEqual(caller.submissions, 0)
        self.assertEqual(output.read_bytes(), before_output)
        self.assertEqual((self.out_dir / "call_index.json").read_bytes(), before_index)
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
                                  '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why,
                                  allow_new_sample_on_parse_failure=True, max_attempts=2,
                                  new_sample_reason="completed output failed the frozen JSON schema")
        self.assertEqual(result["attempt"], 1)
        self.assertEqual(caller.submissions, 2)
        calls = self.go.read_json(out / "call_index.json")["records"]
        self.assertEqual([record["attempt"] for record in calls], [0, 1])
        self.assertNotEqual(calls[0]["sampling_identity"], calls[1]["sampling_identity"])
        self.assertIsNone(calls[0]["new_sample_reason"])
        self.assertEqual(calls[1]["new_sample_reason"], "completed output failed the frozen JSON schema")
        first_output = out / calls[0]["paths"]["output"]
        self.assertEqual(first_output.read_text(encoding="utf-8"), "not a JSON response")
        self.assertTrue((out / calls[1]["paths"]["output"]).is_file())
        second_output = (out / calls[1]["paths"]["output"]).read_bytes()
        pipeline._load_calls()
        no_new = MockCaller()
        pipeline.caller = no_new
        rerun = pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                                 '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why,
                                 allow_new_sample_on_parse_failure=True, max_attempts=2,
                                 new_sample_reason="completed output failed the frozen JSON schema")
        self.assertTrue(rerun["resumed"])
        self.assertEqual(rerun["attempt"], 1)
        self.assertEqual(no_new.submissions, 0)
        self.assertEqual(first_output.read_bytes(), b"not a JSON response")
        self.assertEqual((out / calls[1]["paths"]["output"]).read_bytes(), second_output)

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

    def test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections(self):
        pipeline = self.go.Pipeline(Path(self.temp.name) / "external-muse-pack", MockCaller())
        pipeline.data = self.go._freeze_inputs(ROOT)
        readings = {"a": (self.out_dir / "reading__gflash__op60.md").read_text(encoding="utf-8"),
                    "b": (self.out_dir / "reading__run124B__op60.md").read_text(encoding="utf-8")}
        tasks = pipeline._make_compare_tasks(pipeline._candidate_sets(readings))
        pack = pipeline._pack("muse_pending", tasks)
        expected = self.go._validate_external_pack(pack)
        for candidate, field, value in (("a", "sha256", "0" * 64),
                                        ("b", "source_sha256", "1" * 64),
                                        ("c", "source_meta_sha256", "2" * 64)):
            broken_source = json.loads(json.dumps(pack, ensure_ascii=False))
            broken_source["tasks"][0]["sources"][candidate][field] = value
            with self.subTest(candidate_source_binding=(candidate, field)):
                with self.assertRaises(self.go.IntegrityError):
                    self.go._validate_external_pack(broken_source)
        broken_lock = json.loads(json.dumps(pack, ensure_ascii=False))
        lock_path = self.go.INPUT_PATHS["beads"]
        broken_lock["locks"]["source_sha256"][lock_path] = "f" * 64
        with self.assertRaisesRegex(self.go.IntegrityError, "lock differs from frozen inputs"):
            self.go._validate_external_pack(broken_lock)
        temp = Path(self.temp.name) / "external-muse-artifacts"
        temp.mkdir()
        results = []
        bindings = {}
        receipts = {}
        for index, task in enumerate(tasks):
            output = MockCaller()._output({"step": "compare", "key": [], "prompt": task["prompt"]})
            output_bytes = output.encode("utf-8")
            prompt_bytes = task["prompt"].encode("utf-8")
            positions = self.go._extract_prompt_payloads(task["prompt"])
            candidate_texts = {candidate: positions[position]
                               for position, candidate in task["mapping"].items()}
            identity = pack["requested_identity"]
            reported = self.go.canonical_muse_identity("Muse", "external Muse")
            binding = {"run_id": self.go.RUN_ID, "task_id": task["task_id"],
                       "logical_task_id": task["logical_task_id"], "request_id": task["request_id"],
                       "review_target": self.go.MUSE_TARGET,
                       "requested_provider": identity["provider"], "requested_model": identity["model"],
                       "requested_transport": identity["transport"],
                       "reported_provider": reported["provider"], "reported_model": reported["model"],
                       "reported_transport": self.go.MUSE_TRANSPORT, "seed": task["seed"],
                       "mapping": task["mapping"],
                       "mapping_sha256": self.go.sha256_text(json.dumps(task["mapping"], ensure_ascii=False,
                           sort_keys=True, separators=(",", ":"))),
                       "prompt_sha256": task["prompt_sha256"], "template_sha256": pack["template_sha256"],
                       "source_bundle_sha256": self.go._external_source_bundle_sha256(pack, task)}
            terminal = {"schema": "run146-external-muse-terminal-v1", "identity": binding,
                        "status": "completed", "terminal_id": "TEST_ONLY-terminal-%d" % index}
            terminal_bytes = self.go.json_bytes(terminal)
            meta = {"schema": "run146-external-muse-meta-v1", "identity": binding,
                    "prompt_sha256": self.go.sha256_bytes(prompt_bytes),
                    "output_sha256": self.go.sha256_bytes(output_bytes),
                    "terminal_sha256": self.go.sha256_bytes(terminal_bytes),
                    "raw_output_size": len(output_bytes)}
            folder = temp / ("task-%d" % index)
            folder.mkdir()
            files = {"meta": folder / "meta.json", "prompt": folder / "prompt.txt",
                     "output": folder / "output.txt", "terminal": folder / "terminal.json"}
            files["meta"].write_bytes(self.go.json_bytes(meta))
            files["prompt"].write_bytes(prompt_bytes)
            files["output"].write_bytes(output_bytes)
            files["terminal"].write_bytes(terminal_bytes)
            results.append({"task_id": task["task_id"], "logical_task_id": task["logical_task_id"],
                            "request_id": task["request_id"], "requested_identity": pack["requested_identity"],
                            "reported_provider": "Muse", "reported_model": "external Muse",
                            "reported_transport": "mcp", "seed": task["seed"],
                            "mapping": task["mapping"], "prompt_sha256": task["prompt_sha256"],
                            "raw_response": output, "artifacts": {key: str(path) for key, path in files.items()},
                            "candidate_texts": candidate_texts})
            bindings[task["task_id"]] = (binding, terminal, output_bytes)

        def verifier(result, meta, terminal, raw_output):
            task = expected[result["task_id"]]
            binding, expected_terminal, expected_bytes = bindings[result["task_id"]]
            self.assertEqual(meta["identity"], binding)
            self.assertEqual(terminal["identity"], binding)
            self.assertEqual(raw_output, expected_bytes)
            identity = pack["requested_identity"]
            return {"receipt_schema": "muse_sourcebound_receipt_v2", "attestation_class": "TEST_ONLY",
                    "verified": True, "source_bound": True, "task_id": task["task_id"],
                    "logical_task_id": task["logical_task_id"], "request_id": task["request_id"],
                    "prompt_sha256": task["prompt_sha256"], "template_sha256": pack["template_sha256"],
                    "source_bundle_sha256": self.go._external_source_bundle_sha256(pack, task),
                    "mapping_sha256": self.go.sha256_text(json.dumps(task["mapping"], ensure_ascii=False,
                        sort_keys=True, separators=(",", ":"))), "seed": task["seed"],
                    "raw_output_sha256": self.go.sha256_bytes(raw_output), "raw_output_size": len(raw_output),
                    "terminal_status": "completed", "terminal_id": expected_terminal["terminal_id"],
                    "review_target": self.go.MUSE_TARGET,
                    "requested_provider": identity["provider"], "requested_model": identity["model"],
                    "requested_transport": identity["transport"],
                    "reported_provider": identity["provider"], "reported_model": identity["model"],
                    "reported_transport": self.go.MUSE_TRANSPORT,
                    "actual_provider": identity["provider"], "actual_model": identity["model"],
                    "actual_transport": identity["transport"]}
        normalized = self.go.validate_external_review_results(pack, results, "muse", verifier)
        self.assertEqual(len(normalized), 6)
        self.assertTrue(all(row["verification_status"] == "TEST_ONLY_SOURCEBOUND" and
                            row["real_return_count"] == 0 and
                            row["music_acceptance"] == "NOT_PERFORMED" for row in normalized))
        first = expected[tasks[0]["task_id"]]
        binding, terminal, raw_bytes = bindings[tasks[0]["task_id"]]
        receipt = verifier(results[0], {"identity": binding}, terminal, raw_bytes)
        for field in ("verified", "source_bound", "seed", "raw_output_size"):
            for malformed in ((1, 1.0, False, "true", None) if field in ("verified", "source_bound")
                              else (True, float(receipt[field]))):
                changed = dict(receipt, **{field: malformed})
                with self.subTest(exact_receipt_type_field=field, malformed=malformed):
                    with self.assertRaises(self.go.IntegrityError):
                        self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes, terminal, changed)
                    def malformed_verifier(result, meta, terminal, raw_output):
                        row = verifier(result, meta, terminal, raw_output)
                        row[field] = malformed
                        return row
                    with self.assertRaises(self.go.IntegrityError):
                        self.go.validate_external_review_results(pack, results, "muse", malformed_verifier)
        required = set(receipt)
        self.assertEqual(len(required), 26)
        for field in sorted(required):
            broken = dict(receipt)
            broken.pop(field)
            with self.subTest(missing_external_receipt_field=field):
                with self.assertRaises(self.go.IntegrityError):
                    self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes,
                                                           terminal, broken)
        with self.assertRaisesRegex(self.go.IntegrityError, "exact field set"):
            self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes, terminal,
                                                    dict(receipt, extra="no"))
        binding_fields = ("task_id", "logical_task_id", "request_id", "prompt_sha256", "template_sha256",
                          "source_bundle_sha256", "mapping_sha256", "seed", "raw_output_sha256",
                          "raw_output_size", "terminal_status", "review_target", "requested_provider",
                          "requested_model", "requested_transport", "reported_provider", "reported_model",
                          "reported_transport", "actual_provider", "actual_model", "actual_transport")
        for field in binding_fields:
            broken = dict(receipt)
            broken[field] = "tampered"
            with self.subTest(external_receipt_binding=field):
                with self.assertRaises(self.go.IntegrityError):
                    self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes,
                                                           terminal, broken)
        with self.assertRaises(self.go.IntegrityError):
            self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes,
                                                    dict(terminal, terminal_id=""), receipt)
        for forbidden in ("", "mock", "file", "unknown"):
            with self.assertRaises(self.go.IntegrityError):
                self.go._validate_external_muse_receipt(
                    pack, first, dict(results[0], reported_transport=forbidden), raw_bytes, terminal, receipt)
        wrong_target = json.loads(json.dumps(pack, ensure_ascii=False))
        wrong_target["review_target"] = "Muse/external Muse"
        with self.assertRaisesRegex(self.go.IntegrityError, "target/provider/model/transport"):
            self.go._validate_external_pack(wrong_target)
        wrong_request = json.loads(json.dumps(results, ensure_ascii=False))
        wrong_request[0]["request_id"] = "other-task"
        with self.assertRaisesRegex(self.go.IntegrityError, "task/request/mapping"):
            self.go.validate_external_review_results(pack, wrong_request, "muse", verifier)
        wrong_mapping = json.loads(json.dumps(results, ensure_ascii=False))
        wrong_mapping[0]["mapping"][self.go.POSITIONS[0]] = \
            wrong_mapping[0]["mapping"][self.go.POSITIONS[1]]
        with self.assertRaisesRegex(self.go.IntegrityError, "task/request/mapping"):
            self.go.validate_external_review_results(pack, wrong_mapping, "muse", verifier)
        bad_quote_results = json.loads(json.dumps(results, ensure_ascii=False))
        bad_payload = json.loads(bad_quote_results[0]["raw_response"])
        bad_payload["best_moments"][self.go.POSITIONS[0]] = "A claim cites \"invented exact quote\"."
        bad_output = json.dumps(bad_payload, ensure_ascii=False).encode("utf-8")
        bad_quote_results[0]["raw_response"] = bad_output.decode("utf-8")
        output_path = Path(bad_quote_results[0]["artifacts"]["output"])
        output_path.write_bytes(bad_output)
        meta_path = Path(bad_quote_results[0]["artifacts"]["meta"])
        bad_meta = self.go.read_json(meta_path)
        bad_meta["output_sha256"] = self.go.sha256_bytes(bad_output)
        bad_meta["raw_output_size"] = len(bad_output)
        meta_path.write_bytes(self.go.json_bytes(bad_meta))
        task_id = bad_quote_results[0]["task_id"]
        bindings[task_id] = (bindings[task_id][0], bindings[task_id][1], bad_output)
        with self.assertRaisesRegex(self.go.IntegrityError, "quote validation"):
            self.go.validate_external_review_results(pack, bad_quote_results, "muse", verifier)

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
        before = {str(path.relative_to(RUN_DIR)): digest(path.read_bytes())
                  for path in RUN_DIR.rglob("*") if path.is_file()}
        caller = MockCaller()
        with mock.patch.object(importlib.util, "spec_from_file_location",
                               side_effect=AssertionError("shared entry must never be imported")):
            with self.assertRaises(self.go.RealExecutionBlocked):
                self.go.run_all(caller=None)
        self.assertEqual(caller.submissions, 0)
        after = {str(path.relative_to(RUN_DIR)): digest(path.read_bytes())
                 for path in RUN_DIR.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_v4_preflight_is_read_only_for_absent_and_present_unverified_entries(self):
        with tempfile.TemporaryDirectory(prefix="run146_real_preflight_") as temp:
            root = Path(temp)
            (root / "tools").mkdir()
            absent = self.go.real_preflight(root)
            self.assertEqual(absent["shared_v4"], "absent")
            self.assertEqual(absent["writes"], 0)
            (root / "tools" / "experiment_calls_v4.py").write_text(
                "from pathlib import Path\nPath('SHOULD_NOT_EXIST').write_text('executed')\n", encoding="utf-8")
            (root / "tools" / "experiment_calls_v5.py").write_text("# partial\n", encoding="utf-8")
            (root / "tools" / "experiment_calls_v6.py").write_text("# in flight\n", encoding="utf-8")
            before = {str(path.relative_to(root)): digest(path.read_bytes())
                      for path in root.rglob("*") if path.is_file()}
            present = self.go.real_preflight(root)
            self.assertEqual(present["shared_v4"], "present_unverified")
            self.assertEqual(present["shared_v5"], "partial_unusable")
            self.assertEqual(present["shared_v6"], "in_flight_not_auto_adopted")
            self.assertEqual(present["dependencies"], "not imported or verified")
            with mock.patch.object(importlib.util, "spec_from_file_location",
                                   side_effect=AssertionError("shared entry must never be imported")):
                with self.assertRaises(self.go.RealExecutionBlocked):
                    self.go._real_preflight_then_block(root)
            after = {str(path.relative_to(root)): digest(path.read_bytes())
                     for path in root.rglob("*") if path.is_file()}
            self.assertEqual(after, before)
            self.assertFalse((root / "SHOULD_NOT_EXIST").exists())

    def test_raw_response_and_metadata_json_require_complete_strict_boundaries(self):
        valid_object = '{"differs":false,"sentence":"无"}'
        valid_array = '[{"relation":"r"}]'
        self.assertTrue(self.go.extract_json_object("  " + valid_object + "  ")[0])
        self.assertTrue(self.go.extract_json_object("```json\n" + valid_object + "\n```")[0])
        self.assertTrue(self.go.extract_json_array(valid_array)[0])
        self.assertTrue(self.go.extract_json_array("```json\n" + valid_array + "\n```")[0])
        invalid = (
            'prefix ' + valid_object, valid_object + ' trailer', valid_object + '{"second":1}',
            '{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}', 'true'
        )
        for raw in invalid:
            with self.subTest(raw=raw):
                self.assertFalse(self.go.extract_json_object(raw)[0])
                with self.assertRaises((ValueError, TypeError)):
                    self.go.strict_json_loads(raw)
        self.assertFalse(self.go.extract_json_object(valid_array)[0])
        self.assertFalse(self.go.extract_json_array(valid_object)[0])
        raw_bytes = b' {"differs":false, "sentence":"\xe6\x97\xa0"} '
        raw_text = raw_bytes.decode("utf-8")
        self.assertTrue(self.go.parse_why(raw_text)[0])
        self.assertEqual(raw_bytes, raw_text.encode("utf-8"))
        with tempfile.TemporaryDirectory(prefix="run146_meta_strict_") as temp:
            path = Path(temp) / "meta.json"
            path.write_text('{"identity":{},"identity":{}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                self.go.read_json(path)

    def test_mech_explains_is_strict_int_set_and_rejects_bool_nested_duplicate_and_range(self):
        valid = [{"relation": "MOCK_ONLY relation", "explains": [1, 2],
                  "new_understanding": "MOCK_ONLY new understanding"}]
        parsed, error = self.go.parse_mech(json.dumps(valid), 2)
        self.assertIsNone(error)
        self.assertEqual(parsed[0]["explains"], [1, 2])
        for values in ([True, 2], [False, 1], [1.0, 2], ["1", 2], [[1], 2],
                       [0, 1], [1, 3], [1, 1]):
            with self.subTest(explains=values):
                parsed, error = self.go.parse_mech(json.dumps([{**valid[0], "explains": values}]), 2)
                self.assertIsNone(parsed)
                self.assertIsNotNone(error)

    def test_compare_checks_every_quote_mapping_and_required_citation(self):
        candidates = {"a": "Unique alpha phrase appears here.",
                      "b": "Unique beta phrase appears here.",
                      "c": "Unique gamma phrase appears here."}
        mapping = dict(zip(self.go.POSITIONS, ("a", "b", "c")))

        def response():
            moments = {position: "“%s” supports this moment." % candidates[candidate].split(" appears")[0]
                       for position, candidate in mapping.items()}
            only_here = {position: "“%s” is unique here." % candidates[candidate].split(" appears")[0]
                         for position, candidate in mapping.items()}
            why = "甲写到“%s”，乙写到“%s”，丙写到“%s”。" % tuple(
                candidates[mapping[position]].split(" appears")[0] for position in self.go.POSITIONS)
            return {"ranking": list(self.go.POSITIONS), "best_moments": dict(moments),
                    "worst_moments": dict(moments),
                    "hindsight": {position: [] for position in self.go.POSITIONS},
                    "only_here": only_here, "why": why}

        value = response()
        raw = json.dumps(value, ensure_ascii=False)
        parsed, error = self.go.parse_compare(raw, mapping, candidates)
        self.assertIsNone(error)
        self.assertIsNotNone(parsed)
        mixed = response()
        mixed["best_moments"]["甲"] += " “nonexistent quotation”"
        self.assertIsNone(self.go.parse_compare(json.dumps(mixed, ensure_ascii=False), mapping, candidates)[0])
        missing = response()
        missing["worst_moments"]["乙"] = "A claim without a source quote."
        self.assertIsNone(self.go.parse_compare(json.dumps(missing, ensure_ascii=False), mapping, candidates)[0])
        missing_only = response()
        missing_only["only_here"]["甲"] = "A claim without a source quote."
        self.assertIsNone(self.go.parse_compare(json.dumps(missing_only, ensure_ascii=False), mapping, candidates)[0])
        missing_why = response()
        missing_why["why"] = "A summary without a source quote."
        self.assertIsNone(self.go.parse_compare(json.dumps(missing_why, ensure_ascii=False), mapping, candidates)[0])
        wrong_map = dict(mapping)
        wrong_map["甲"], wrong_map["乙"] = wrong_map["乙"], wrong_map["甲"]
        self.assertIsNone(self.go.parse_compare(raw, wrong_map, candidates)[0])
        duplicate_map = {"甲": "a", "乙": "a", "丙": "c"}
        self.assertIsNone(self.go.parse_compare(raw, duplicate_map, candidates)[0])
        bad_hindsight = response()
        bad_hindsight["hindsight"]["甲"] = ["nonexistent"]
        self.assertIsNone(self.go.parse_compare(json.dumps(bad_hindsight, ensure_ascii=False), mapping, candidates)[0])

    def test_default_parse_failure_stops_and_rerun_submits_zero_new_samples(self):
        out = Path(self.temp.name) / "default-stop"
        caller = MockCaller(invalid_first=True)
        pipeline = self.go.Pipeline(out, caller)
        pipeline.data = self.go._freeze_inputs(ROOT)
        out.mkdir()
        self.go.write_json(out / "freeze.json", pipeline.data["lock"])
        args = ("why", ["run130:gpt56w", 2], "gflash", '{"immutable prompt"}',
                "WHY_GATE_v4", self.go.parse_why)
        with self.assertRaises(self.go.StageFailed):
            pipeline.execute(*args)
        self.assertEqual(caller.submissions, 1)
        index = self.go.read_json(out / "call_index.json")
        self.assertEqual([record["attempt"] for record in index["records"]], [0])
        first_record = index["records"][0]
        first_output = out / first_record["paths"]["output"]
        original = first_output.read_bytes()
        self.assertEqual(original, b"not a JSON response")
        pipeline._load_calls()
        no_new = MockCaller()
        pipeline.caller = no_new
        with self.assertRaises(self.go.StageFailed):
            pipeline.execute(*args)
        self.assertEqual(no_new.submissions, 0)
        self.assertEqual(first_output.read_bytes(), original)
        self.assertEqual(len(self.go.read_json(out / "call_index.json")["records"]), 1)

    def test_transport_policy_needs_sourcebound_receipt_and_strict_budget(self):
        binding = {"logical_id": "why:fixture", "request_id": "req-1", "model": "gflash",
                   "prompt_version": "WHY_GATE_v4", "prompt_sha256": "a" * 64,
                   "producer_sha256": "b" * 64, "attempt": 0}
        proof = {"failure_attempt_id": "attempt-0", "state": "never_submitted"}
        verifier = lambda received, expected: {
            "verified": received == proof, "submission_state": "not_submitted",
            "proof_scope": "sourcebound_pre_submit_v1", "binding": dict(expected)}
        self.assertTrue(self.go.transport_retry_allowed(phase="pre_submit", proof=proof,
                                                        verifier=verifier, expected_binding=binding,
                                                        retries_remaining=1))
        self.assertFalse(self.go.transport_retry_allowed(phase="pre_submit", proof=proof,
                                                         verifier=verifier, expected_binding=binding,
                                                         retries_remaining=0))
        self.assertFalse(self.go.transport_retry_allowed(phase="post_submit_ambiguous", proof=proof,
                                                         verifier=verifier, expected_binding=binding,
                                                         retries_remaining=1))
        self.assertFalse(self.go.transport_retry_allowed(phase="queue_stop", proof=proof,
                                                         verifier=verifier, expected_binding=binding,
                                                         retries_remaining=1))
        self.assertFalse(self.go.transport_retry_allowed(phase="pre_submit", proof={"retry_safe": True},
                                                         verifier=None, expected_binding=binding,
                                                         retries_remaining=1))
        self.assertFalse(self.go.transport_retry_allowed(phase="pre_submit", proof=proof,
                                                         verifier=verifier, expected_binding=binding,
                                                         retries_remaining=True))

    def test_execute_retries_one_proven_pre_submit_failure_then_reuses_same_sample(self):
        go_module = self.go
        class FailOnce:
            def __init__(self):
                self.calls = 0
                self.writer = MockCaller()

            def __call__(self, request):
                self.calls += 1
                if self.calls == 1:
                    binding = {"request_identity": request["request_identity"],
                               "sampling_identity": request["sampling_identity"],
                               "sample_attempt": 0, "transport_attempt": 0,
                               "failure_attempt_id": request["identity"]["logical_id"] +
                                   "|sample:0|transport:0", "phase": "pre_submit"}
                    raise go_module.TransportFailure("offline mock pre-submit failure", phase="pre_submit",
                                                     proof={"sourcebound": binding},
                                                     raw_error=b"first failure")
                return self.writer(request)

        caller = FailOnce()
        def verifier(proof, binding):
            return {"verified": proof.get("sourcebound") == binding,
                    "submission_state": "not_submitted", "proof_scope": "sourcebound_pre_submit_v1",
                    "binding": dict(binding)}
        out = Path(self.temp.name) / "transport-safe"
        pipeline = self.go.Pipeline(out, caller, transport_proof_verifier=verifier)
        pipeline.data = self.go._freeze_inputs(ROOT)
        out.mkdir()
        result = pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                                  '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why,
                                  max_transport_retries=1)
        self.assertEqual(caller.calls, 2)
        self.assertEqual(result["attempt"], 0)
        index = self.go.read_json(out / "call_index.json")
        self.assertEqual(len(index["records"]), 1)
        self.assertEqual(len(index["transport_attempts"]), 1)
        self.assertTrue(index["transport_attempts"][0]["proof_verified"])
        self.assertEqual(index["records"][0]["sampling_identity"],
                         index["transport_attempts"][0]["sampling_identity"])
        pipeline._load_calls()
        again = pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                                 '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why,
                                 max_transport_retries=1)
        self.assertTrue(again["resumed"])
        self.assertEqual(caller.calls, 2)

    def test_unproven_ambiguous_and_exhausted_transport_failures_hold_persistently(self):
        scenarios = (("claimed", None, "pre_submit", {"retry_safe": True}),
                     ("wrong-proof", lambda proof, binding: {"verified": True,
                      "submission_state": "not_submitted", "proof_scope": "sourcebound_pre_submit_v1",
                      "binding": {"request_identity": "wrong"}}, "pre_submit", {"claim": "safe"}),
                     ("ambiguous", None, "post_submit_ambiguous", {"ticket": "unknown"}),
                     ("queue", None, "queue_stop", {"stopped": True}))
        for name, verifier, phase, proof in scenarios:
            with self.subTest(name=name):
                out = Path(self.temp.name) / ("transport-hold-" + name)
                def fail(_request, _phase=phase, _proof=proof):
                    raise self.go.TransportFailure("transport did not complete", phase=_phase,
                                                   proof=_proof, raw_error=b"immutable raw failure")
                pipeline = self.go.Pipeline(out, fail, transport_proof_verifier=verifier)
                pipeline.data = self.go._freeze_inputs(ROOT)
                out.mkdir()
                with self.assertRaises(self.go.QueueStopped):
                    pipeline.execute("why", ["run130:gpt56w", 2], "gflash",
                                     '{"immutable prompt"}', "WHY_GATE_v4", self.go.parse_why,
                                     max_transport_retries=1)
                self.assertTrue((out / "execution_hold.json").is_file())
                self.assertEqual(len(self.go.read_json(out / "call_index.json")["transport_attempts"]), 1)
                for file_key in ("request", "proof", "error", "raw_output", "terminal"):
                    path = out / self.go.read_json(out / "call_index.json")["transport_attempts"][0]["paths"][file_key]
                    self.assertTrue(path.is_file())
                blocked = self.go.Pipeline(out, fail, transport_proof_verifier=verifier)
                blocked.data = pipeline.data
                with self.assertRaises(self.go.QueueStopped):
                    blocked.execute("another", ["stage", 3], "gflash", '{"prompt"}',
                                    "WHY_GATE_v4", self.go.parse_why)


if __name__ == "__main__":
    unittest.main(verbosity=2)
