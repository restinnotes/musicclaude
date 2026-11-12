"""run149_e7_diag 离线回归（stdlib；不调任何真实 CLI）。

跑法（cwd 为仓库根）：python -X utf8 -I tools/tests/test_run149_e7_diag.py
"""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
GO = ROOT / "runs" / "run149_e7_diag" / "go.py"


def load(name="run149_go"):
    spec = importlib.util.spec_from_file_location(name, GO)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


g = load()


def _bead(k, n_now):
    lines = ["- 第%d段条目%d" % (k, i) for i in range(1, n_now + 1)]
    return {"k": k, "title": "m.%d 标题%d" % (k, k), "text": "", "now_lines": lines}


class ImportSafety(unittest.TestCase):
    def test_import_no_subprocess(self):
        with mock.patch("subprocess.run") as sr, mock.patch("subprocess.Popen") as pop:
            m = load("run149_probe")
            sr.assert_not_called()
            pop.assert_not_called()
        self.assertEqual(m.RUN_ID, "run149_e7_diag")

    def test_opus_policy_scoped(self):
        self.assertIsNot(g.runner.check_policy, g._policy149)  # import 不改 runner
        g._policy149("opus")  # 不抛
        with self.assertRaises(Exception):
            g._policy149("sol")
        with self.assertRaises(Exception):
            g._policy149("muse")


class Items(unittest.TestCase):
    def test_now_items_keep_tags_and_merge(self):
        b = {"now_lines": ["- 甲【另一种理解】乙", "续行", "- 【先后】丙"]}
        self.assertEqual(g.now_items(b), ["甲【另一种理解】乙 续行", "【先后】丙"])

    def test_candidate_numbering(self):
        beads = [_bead(1, 2), _bead(2, 3)]
        why = [{"k": 2, "parse_ok": True, "differs": True, "sentence": "因为前面X"}]
        mech = [{"k": 2, "relations": [{"relation": "R0", "survives": False}, {"relation": "R1", "survives": True}]}]
        C = g.build_candidates(beads, why, mech)
        self.assertEqual([(it["id"], it["kind"]) for it in C[1]], [(1, "认"), (2, "此刻"), (3, "此刻")])
        self.assertEqual([(it["id"], it["kind"]) for it in C[2]],
                         [(1, "认"), (2, "此刻"), (3, "此刻"), (4, "此刻"), (5, "因为前面"), (6, "更深")])
        self.assertEqual(C[2][5]["uid"], "k02_mech1")
        p = g.build_surface_prompt("t", [C[1][1]], C[2])
        self.assertIn("S1. [此刻] 第1段条目1", p)
        self.assertIn("5. [因为前面] 因为前面X", p)

    def test_judge_relation(self):
        au = ("luna_noweb", "gflash_web")
        self.assertEqual(g.judge_relation({"luna_noweb": "insight", "gflash_web": "restatement"}, au), (True, None))
        self.assertFalse(g.judge_relation({"luna_noweb": "insight", "gflash_web": "imported"}, au)[0])
        s, why = g.judge_relation({"luna_noweb": "audit_failed", "gflash_web": "insight"}, au)
        self.assertTrue(s)
        self.assertIn("audit_incomplete", why)
        self.assertFalse(g.judge_relation({"luna_noweb": "audit_failed", "gflash_web": "audit_failed"}, au)[0])
        self.assertFalse(g.judge_relation({"luna_noweb": "audit_failed", "gflash_web": "manufactured"}, au)[0])


class Surface(unittest.TestCase):
    def setUp(self):
        self.C = [{"uid": "k03_hd"}, {"uid": "k03_now01"}, {"uid": "k03_now02"}, {"uid": "k03_why"}]

    def test_retire_and_keep(self):
        screen = ["k01_now01", "k02_now01", "k02_why"]
        p = {"action": "补充", "keep": [2], "show": [2, 4], "expand": [1], "recap": []}
        r = g.apply_surface(screen, p, self.C)
        self.assertEqual(r["screen_after"], ["k02_now01", "k03_now01", "k03_why"])
        self.assertEqual(r["retired"], ["k01_now01", "k02_why"])
        self.assertFalse(r["action_mismatch"])
        self.assertEqual(r["expand"], ["k03_hd"])

    def test_hold_and_mismatch(self):
        screen = ["a", "b"]
        r = g.apply_surface(screen, {"action": "保持", "keep": [1, 2], "show": [], "expand": [], "recap": []}, self.C)
        self.assertEqual((r["screen_after"], r["retired"], r["action_mismatch"]), (["a", "b"], [], False))
        r = g.apply_surface(screen, {"action": "保持", "keep": [1], "show": [], "expand": [], "recap": []}, self.C)
        self.assertTrue(r["action_mismatch"])
        r = g.apply_surface(screen, {"action": "沉默", "keep": [], "show": [], "expand": [], "recap": []}, self.C)
        self.assertEqual((r["screen_after"], r["retired"], r["action_mismatch"]), ([], ["a", "b"], False))

    def test_parse_surface_ranges(self):
        fn = g.parse_surface_fn(2, 4)
        ok, _ = fn('{"action":"更新","keep":["S2"],"show":[1,3],"why":"x"}')
        self.assertEqual((ok["keep"], ok["show"]), ([2], [1, 3]))
        self.assertIsNone(fn('{"action":"更新","keep":["S3"],"show":[1]}')[0])
        self.assertIsNone(fn('{"action":"换掉","keep":[],"show":[1]}')[0])


class ReaderFormat(unittest.TestCase):
    def test_run124_conversion(self):
        steps = g.convert_run124()
        self.assertGreater(len(steps), 5)
        self.assertEqual(len(steps[0]["screen"]), 2)
        md = g.reader_md(g.reader_view_from_screens(steps))
        for bad in ("run122", "action", "why", "gpt56w", "[此刻]", "[更深]", "规则", "宏观段", "展开可看"):
            self.assertNotIn(bad, md)
        self.assertIn("【听】", md)

    def test_unchanged_marker(self):
        v = g.reader_view_from_screens([{"time": "t1", "screen": ["x"]}, {"time": "t2", "screen": ["x"]},
                                        {"time": "t3", "screen": []}])
        md = g.reader_md(v)
        self.assertIn("（屏幕不变）", md)
        self.assertIn("（屏幕清空）", md)
        self.assertEqual([s["status"] for s in v], ["new", "unchanged", "cleared"])


class Rotation(unittest.TestCase):
    def test_each_candidate_each_position(self):
        sets = {"c_gpro_s3": {"texts": {"a": "A", "b": "B", "c": "C"}, "c_source": "x"},
                "c_gflash_s1": {"texts": {"a": "A", "b": "B", "c": "C"}, "c_source": "y"}}
        tasks = g.compare_tasks(sets, ("gpt56w", "luna_noweb"))
        self.assertEqual(len(tasks), 2 * 2 * 3)
        for s in sets:
            for j in ("gpt56w", "luna_noweb"):
                rs = [t for t in tasks if t["set"] == s and t["judge"] == j]
                self.assertEqual(len({t["seed"] for t in rs}), 1)
                for c in "abc":
                    self.assertEqual(sorted(next(p for p, v in t["mapping"].items() if v == c) for t in rs),
                                     sorted(g.POS))
                for t in rs:  # 提示词按映射放置候选
                    pa = t["prompt"].index("【甲】")
                    self.assertEqual(t["prompt"][pa + 4:].strip()[0], t["mapping"]["甲"].upper())
        self.assertEqual(g.rotations(5), g.rotations(5))

    def test_parse_compare(self):
        p, _ = g.parse_compare('{"ranking":["乙","甲 ","丙"],"why":"w"}')
        self.assertEqual(p["ranking"], ["乙", "甲", "丙"])
        self.assertIsNone(g.parse_compare('{"ranking":["乙","乙","丙"]}')[0])


class Aggregation(unittest.TestCase):
    def _rec(self, s, j, run, rk_true, ok=True):
        mapping = dict(zip(g.POS, ["a", "b", "c"]))
        inv = {v: k for k, v in mapping.items()}
        return {"set": s, "judge": j, "run": run, "mapping": mapping, "parse_ok": ok,
                "ranking_true": list(rk_true) if ok else None,
                "ranking_pos": [inv[x] for x in rk_true] if ok else None, "parse_error": None if ok else "boom"}

    def test_aggregate_and_missing(self):
        recs = [self._rec("c_gpro_s3", "luna_noweb", r, rk) for r, rk in enumerate(("abc", "acb", "bac"))]
        recs += [self._rec("c_gpro_s3", "gpt56w", r, "abc", ok=False) for r in range(3)]
        rows = {(r["set"], r["judge"]): r for r in g.aggregate(recs, ("gpt56w", "luna_noweb"))}
        lu = rows[("c_gpro_s3", "luna_noweb")]
        self.assertEqual((lu["n_ok"], lu["first_a"], lu["first_b"], lu["mean_rank_a"]), (3, 2, 1, 1.33))
        self.assertEqual(lu["first_consistency"], "2/3（a）")
        self.assertEqual(lu["rankings"], ["abc", "acb", "bac"])
        self.assertEqual(lu["self_judge"], "否")
        self.assertEqual(rows[("c_gpro_s3", "gpt56w")]["self_judge"], "a,b")
        self.assertEqual(rows[("c_gpro_s3", "ALL")]["n_ok"], 3)
        self.assertEqual(rows[("c_gpro_s3", "ALL-非自评")]["n"], 3)
        miss = g.missing_judges(recs, ("gpt56w", "luna_noweb"))
        self.assertIn({"set": "c_gpro_s3", "judge": "gpt56w", "n_ok": 0, "n": 3, "errors": ["boom"]}, miss)
        self.assertTrue(any(m["set"] == "c_gflash_s1" and m["judge"] == "luna_noweb" for m in miss))

    def test_canonical_self_flag(self):
        self.assertEqual(g.self_flag("c_gflash_s1", "gflash_web"), "c")
        self.assertEqual(g.self_flag("c_gpro_s3", "gflash_web"), "否")


class FullMock(unittest.TestCase):
    def test_full_mock_pipeline(self):
        real = sorted(p.name for p in (ROOT / "runs" / "run149_e7_diag").iterdir())
        ok, info = g.run_mock(4)
        self.assertTrue(ok)
        self.assertEqual(info["calls_rerun"], 6)
        self.assertLess(info["max_prompt_chars"]["why"], 65536)
        self.assertEqual(real, sorted(p.name for p in (ROOT / "runs" / "run149_e7_diag").iterdir()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
