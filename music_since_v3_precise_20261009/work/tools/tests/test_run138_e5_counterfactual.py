"""run138 新审核入口的冻结输入、单变量、解析与完整性；不调用模型。"""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("run138_under_test", TOOLS / "run138_e5_counterfactual.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class CounterfactualTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def sample_case(self):
        return {"case_id": "R001", "work": "op60", "station": 1, "relation_index": 1,
                "mm": "mm.1–4", "items": ["体验甲", "体验乙", "体验丙"],
                "relation": "关系", "explains": [1, 2], "new_understanding": "增量",
                "source": {"generator_key": "gpt56w"}}

    def test_frozen_template_diff_is_exactly_one_sentence(self):
        templates = R.verify_templates()
        self.assertEqual(templates["v1"].replace(R.ADDITION + "\n", ""), templates["v0"])
        case = self.sample_case()
        p0, p1 = (R.audit_prompt(case, templates[v]) for v in ("v0", "v1"))
        self.assertEqual(p1.replace(R.ADDITION + "\n", ""), p0)
        self.assertIn("戏剧化、笃定、单一故事线本身不扣分", p0)
        self.assertNotIn("gpt56w", p0)
        self.assertNotIn("R001", p0)

    def test_relation_requires_two_distinct_valid_integer_explanations(self):
        valid = {"relation": "关系", "explains": [1, 2], "new_understanding": "新理解"}
        self.assertEqual(R.strict_relations([valid], 3), [valid])
        for ex in ([1], [1, 1], [True, 2], [1, "2"], [0, 2], [1, 4], None):
            with self.subTest(ex=ex), self.assertRaises(ValueError):
                R.strict_relations([{**valid, "explains": ex}], 3)
        with self.assertRaises(ValueError):
            R.strict_relations([{**valid, "new_understanding": ""}], 3)
        self.assertEqual(R.strict_relations([], 3), [])

    def test_audit_parser_rejects_partial_or_missing_reason(self):
        self.assertIsNotNone(R.parse_audit('{"class":"insight","why":"具体损失"}')[0])
        self.assertIsNotNone(R.parse_audit('{"class":"undetermined","why":"缺少本处依据"}')[0])
        for text in ('{"class":"insight"}', '{"class":"insight","why":""}',
                     '{"class":"other","why":"说明"}', '前言 {"class":"insight","why":"理由"}',
                     '{"class":"insight","why":"理由","score":5}', '{"class":"insight"'):
            self.assertIsNone(R.parse_audit(text)[0], text)

    def test_frozen_files_are_readonly_and_different_content_fails(self):
        path = self.root / "frozen.txt"
        R.immutable_text(path, "甲\n乙\r\n丙")
        original = path.read_bytes()
        R.immutable_text(path, "甲\n乙\r\n丙")
        self.assertEqual(path.read_bytes(), original)
        with self.assertRaises(R.ArtifactConflict):
            R.immutable_text(path, "改动")
        self.assertEqual(path.read_bytes(), original)
        jp = self.root / "frozen.json"
        R.immutable_json(jp, {"seed": 1})
        original_json = jp.read_bytes()
        with self.assertRaises(R.ArtifactConflict):
            R.immutable_json(jp, {"seed": 2})
        self.assertEqual(jp.read_bytes(), original_json)

    def fixture(self):
        source = self.root / "source"
        source.mkdir()
        gen_template = self.root / "MECH_v1.txt"
        gen_template.write_bytes(R.GEN_TEMPLATE.read_bytes())
        prompt = R.legacy_text(gen_template).replace("{{WORK}}", R.WORKS["op60"]).replace(
            "{{MM}}", "mm.1–4").replace("{{ITEMS}}", "1. 体验甲\n2. 体验乙\n3. 体验丙")
        output = [{"relation": "关系", "explains": [1, 2], "new_understanding": "新理解"}]
        jid = "legacy_job"
        R.write_text(source / "prompts/legacy_job.txt", prompt.replace("\n", "\r\n"))
        R.write_json(source / "outputs/legacy_job.md", output)
        R.write_json(source / "meta/legacy_job.json", {
            "job_id": jid, "status": "ok", "model_key": "gpt56w", "work_key": "op60",
            "prompt_version": "MECH_v1", "model_name": "old recorded alias",
            "prompt_file": "prompts/legacy_job.txt", "output_file": "outputs/legacy_job.md",
            "extra": {"station": 1, "version": "v1", "gen": "gpt56w"}})
        record = {"key": ["gen", "op60", 1, "v1", "gpt56w"], "model": "gpt56w",
                  "prompt_version": "MECH_v1", "parse_ok": True, "parsed": output,
                  "prompt_sha": R.sha_text(prompt)[:10], "output_job_id": jid}
        R.write_json(source / "cache_gen.json", {"records": [record]})
        return source, gen_template, record

    def fixture_context(self, gen_template):
        return mock.patch.multiple(R, ROOT=self.root, GEN_TEMPLATE=gen_template, EXPECTED={"op60": 1})

    def test_legacy_input_requires_artifacts_and_records_actual_identity_as_unknown(self):
        source, tpl, _ = self.fixture()
        before = {str(p): p.read_bytes() for p in source.rglob("*") if p.is_file()}
        with self.fixture_context(tpl):
            cases, files = R.load_cases(source)
        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["source"]["actual_backend_model"], "unknown_in_legacy_record")
        self.assertIsNone(cases[0]["source"]["producer_identity"])
        self.assertEqual(len(files), 4)
        self.assertEqual(before, {str(p): p.read_bytes() for p in source.rglob("*") if p.is_file()})
        (source / "outputs/legacy_job.md").unlink()
        with self.fixture_context(tpl), self.assertRaises(R.ArtifactConflict):
            R.load_cases(source)

    def test_cache_only_and_duplicate_success_cannot_count_as_valid_source(self):
        source, tpl, record = self.fixture()
        R.write_json(source / "cache_gen.json", {"records": [record, copy.deepcopy(record)]})
        with self.fixture_context(tpl), self.assertRaises(R.ArtifactConflict):
            R.load_cases(source)
        R.write_json(source / "cache_gen.json", {"records": []})
        with self.fixture_context(tpl), self.assertRaises(R.ArtifactConflict):
            R.load_cases(source)

    def test_cache_parsed_must_match_reparsed_output(self):
        source, tpl, record = self.fixture()
        record["parsed"][0]["new_understanding"] = "被篡改"
        R.write_json(source / "cache_gen.json", {"records": [record]})
        with self.fixture_context(tpl), self.assertRaises(R.ArtifactConflict):
            R.load_cases(source)

    def test_report_does_not_mark_missing_jobs_complete(self):
        case = self.sample_case()
        jobs = [{"case_id": "R001", "version": v} for v in ("v0", "v1")]
        result = {"case_id": "R001", "version": "v0", "record": {
            "parse_ok": True, "parsed": {"class": "insight", "why": "理解增量"}}}
        self.assertFalse(R.report(self.root, [case], jobs, [result]))
        saved = json.loads((self.root / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["completed_jobs"], 1)
        self.assertFalse(saved["production_ready"])
        with self.assertRaises(R.ArtifactConflict):
            R.report(self.root, [case], jobs, [result, result])

    def test_execute_checks_frozen_prompt_before_call(self):
        path = self.root / "audit_prompts/task.txt"
        R.write_text(path, "原文")
        task = {"prompt_file": "audit_prompts/task.txt", "prompt_sha256": R.sha_text("原文")}
        R.write_text(path, "改变")
        with mock.patch.object(R.calls, "call") as call, self.assertRaises(R.ArtifactConflict):
            R.execute_one(self.root, task)
        call.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
