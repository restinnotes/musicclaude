"""run140 机械转写的调试前测试；不调用模型、不碰冻结源。"""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location("run140_under_test",
                                              TOOLS / "run140_mech_independent_review.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def toy_case(cid="R001", work="op52", station=1, ridx=1):
    return {"case_id": cid, "work": work, "station": station,
            "relation_index": ridx, "mm": "mm.1-2",
            "items": ["体验甲甲甲", "体验乙乙乙", "体验丙丙丙"],
            "relation": "待审关系文字", "explains": [1, 2],
            "new_understanding": "声称的新理解",
            "source": {"run": "run128_mech_calib", "job_id": "toy_job",
                       "generator_key": "gpt56w"}}


def toy_pack():
    packs, _ = R.build_packs([toy_case("R%03d" % (i + 1),
                                       "op52" if i < 32 else "op60",
                                       (i % 16) + 1 if i < 32 else (i - 32) % 14 + 1,
                                       1 if i % 2 == 0 else 2)
                              for i in range(60)])
    return packs[0]


def valid_review_text(pack):
    reviews = []
    for c in pack["cases"]:
        reviews.append({"blind_id": c["blind_id"], "verdict": "restatement",
                        "why": "只是合并换词，无新增理解。",
                        "quoted_items": [[n, c["items"][n - 1]] for n in c["explains"]],
                        "quoted_relation": c["relation"],
                        "loss_if_deleted": "NOCHANGE：原体验已说全，无损失。",
                        "retain_anchor": False, "anchor_reason": "无独立表达价值。",
                        "evidence_limit": "仅 input-level 支持，无乐谱证据。"})
    return json.dumps({"pack_id": pack["pack_id"], "reviews": reviews}, ensure_ascii=False)


class IndependentReviewTests(unittest.TestCase):
    def test_strict_case_rejects_set_nesting_first(self):
        with self.assertRaises(ValueError):
            R.strict_case({**toy_case(), "explains": {1, 2}})

    def test_explains_needs_two_distinct_strict_ints(self):
        R.strict_case(toy_case())
        for ex in ([1], [1, 1], [True, 2], [1, "2"], [0, 2], [1, 9], None, "12"):
            with self.subTest(ex=ex), self.assertRaises(ValueError):
                R.strict_case({**toy_case(), "explains": ex})

    def test_judge_text_hides_identity(self):
        packs, _ = R.build_packs([toy_case("R%03d" % (i + 1),
                                           "op52" if i < 32 else "op60",
                                           (i % 16) + 1 if i < 32 else (i - 32) % 14 + 1,
                                           1 if i % 2 == 0 else 2)
                                  for i in range(60)])
        for pack in packs:
            prompt = R.render_pack_prompt(pack)
            for token in ("R001", "MECH128", "run128", "run138", "gpt56w",
                          "producer_identity", "MECH_AUDIT"):
                self.assertNotIn(token, prompt, token)
            # 每包 12 case inline 原文都在，编号只 bind 当前 blindID。
            self.assertEqual(prompt.count("【案例 blindID="), 12)
            for entry in pack["cases"]:
                self.assertIn("blindID=%s" % entry["blind_id"], prompt)
                self.assertIn(entry["relation"], prompt)
                self.assertIn("MM（待审旧文字，非乐谱事实）", prompt)

    def test_seed_mapping_packs_complete_and_stable(self):
        mk = lambda: R.build_packs([toy_case("R%03d" % (i + 1),
                                             "op52" if i < 32 else "op60",
                                             (i % 16) + 1 if i < 32 else (i - 32) % 14 + 1,
                                             1 if i % 2 == 0 else 2)
                                    for i in range(60)])
        packs_a, map_a = mk()
        packs_b, map_b = mk()
        self.assertEqual([p["pack_id"] for p in packs_a],
                         ["pack%02d" % i for i in (1, 2, 3, 4, 5)])
        self.assertTrue(all(len(p["cases"]) == 12 for p in packs_a))
        blinds = [c["blind_id"] for p in packs_a for c in p["cases"]]
        self.assertEqual(len(set(blinds)), 60)
        # blindID 顺序与原顺序无关：映射覆盖全部 60 原 ID。
        self.assertEqual({m["original_case_id"] for m in map_a},
                         {"R%03d" % (i + 1) for i in range(60)})
        self.assertEqual(packs_a, packs_b)
        self.assertEqual(map_a, map_b)

    def test_pack_prompt_is_byte_stable(self):
        packs, _ = R.build_packs([toy_case("R%03d" % (i + 1),
                                           "op52" if i < 32 else "op60",
                                           (i % 16) + 1 if i < 32 else (i - 32) % 14 + 1,
                                           1 if i % 2 == 0 else 2)
                                  for i in range(60)])
        once = [R.render_pack_prompt(p) for p in packs]
        twice = [R.render_pack_prompt(p) for p in packs]
        self.assertEqual([R.sha_text(t) for t in once],
                         [R.sha_text(t) for t in twice])

    def test_parse_review_accepts_full_json_and_fenced_json(self):
        pack = toy_pack()
        text = valid_review_text(pack)
        parsed, err = R.parse_review(text, pack)
        self.assertIsNone(err)
        self.assertEqual(len(parsed["reviews"]), 12)
        fenced = "```json\n%s\n```" % text
        parsed2, err2 = R.parse_review(fenced, pack)
        self.assertIsNone(err2)
        self.assertEqual(parsed2, parsed)

    def test_parse_review_rejects_malformed_and_missing_quote(self):
        pack = toy_pack()
        base = json.loads(valid_review_text(pack))
        bad_missing = copy.deepcopy(base)
        bad_missing["reviews"][0]["quoted_items"] = [[n, "改过的引文"]
                                                     for n in pack["cases"][0]["explains"]]
        self.assertIsNone(R.parse_review(json.dumps(bad_missing, ensure_ascii=False), pack)[0])
        bad_dup = copy.deepcopy(base)
        bad_dup["reviews"][1]["blind_id"] = bad_dup["reviews"][0]["blind_id"]
        self.assertIsNone(R.parse_review(json.dumps(bad_dup, ensure_ascii=False), pack)[0])
        bad_schema = copy.deepcopy(base)
        bad_schema["reviews"][0]["extra"] = 1
        self.assertIsNone(R.parse_review(json.dumps(bad_schema, ensure_ascii=False), pack)[0])
        self.assertIsNone(R.parse_review('前言 ' + valid_review_text(pack), pack)[0])
        self.assertIsNone(R.parse_review('{"pack_id": "%s"}' % pack["pack_id"], pack)[0])
        # 重复键必须拒。
        dup_key = '{"pack_id": "%s", "reviews": [], "reviews": []}' % pack["pack_id"]
        self.assertIsNone(R.parse_review(dup_key, pack)[0])
        # verdict 为空必须拒。
        empty_verdict = copy.deepcopy(base)
        empty_verdict["reviews"][0]["verdict"] = ""
        self.assertIsNone(R.parse_review(json.dumps(empty_verdict, ensure_ascii=False), pack)[0])

    def test_source_and_prompt_tamper_freezes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases_p = root / "cases.json"
            plan_p = root / "plan.json"
            R.write_json(cases_p, [{"case_id": "R001"}])
            R.write_json(plan_p, {})
            with self.assertRaises(R.ArtifactConflict):
                R.load_and_validate(cases_p, plan_p)

    def test_prepare_is_immutable_and_policy_production_false(self):
        cases = R.load_and_validate()
        self.assertEqual(len(cases), 60)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            first = R.prepare(out)
            plan = json.loads((out / "plan.json").read_bytes().decode("utf-8"))
            mapping = json.loads((out / "case_mapping.json").read_bytes().decode("utf-8"))
            self.assertEqual(first["model_submissions"], 0)
            self.assertFalse(plan["production_ready"])
            self.assertEqual(plan["model_submissions"], 0)
            self.assertIn("canonical", plan["scope"])
            self.assertNotIn("production", plan["scope"].replace("不切 production", ""))
            self.assertEqual(len(mapping["entries"]), 60)
            # mapping 私存原文 SHA 与 genCanonical，不进 judge 全文。
            entry = mapping["entries"][0]
            self.assertIn("gen_canonical", entry)
            self.assertIn("relation_sha256", entry)
            hashes_before = {str(p.relative_to(out)): R.sha_file(p)
                             for p in sorted(out.rglob("*")) if p.is_file()}
            second = R.prepare(out)
            self.assertEqual(first, second)
            hashes_after = {str(p.relative_to(out)): R.sha_file(p)
                            for p in sorted(out.rglob("*")) if p.is_file()}
            self.assertEqual(hashes_before, hashes_after)
            # 冲突内容必须拒，不能覆盖。
            (out / "plan.json").write_bytes(b"tampered")
            with self.assertRaises(R.ArtifactConflict):
                R.prepare(out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
