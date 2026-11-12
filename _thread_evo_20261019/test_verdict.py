"""Prevent incomplete measurements or ties from being promoted as experimental wins."""
import contextlib
import io
import unittest
from unittest.mock import patch

import verdict


class VerdictTests(unittest.TestCase):
    def rows(self):
        return [{"w": w, "j": j, "better": "新版", "new_regress": "否",
                 "cnt": {k: {"new": 2, "base": 0, "平": 0} for k in ("alone", "lean", "plain", "cover")}}
                for w in verdict.WORKS for j in verdict.J2]

    def report(self, rows):
        output = io.StringIO()
        with patch.object(verdict, "floor", return_value=[]), patch.object(verdict, "rows", return_value=rows), \
             patch.object(verdict.V, "graph_of", return_value={"segments": [{"sec": "S01"}, {"sec": "S02"}]}), \
             contextlib.redirect_stdout(output):
            verdict.main("new", "base")
        return output.getvalue()

    def test_three_of_three_cannot_pass_four_review_screen(self):
        self.assertIn("不判通过", self.report(self.rows()[:3]))

    def test_tie_is_not_a_new_version_win(self):
        rows = self.rows()
        rows[2]["better"] = rows[3]["better"] = "差不多"
        report = self.report(rows)
        self.assertIn("2/4 选新版", report)
        self.assertIn("快筛： 不过", report)

    def test_missing_regression_answer_is_not_non_regression(self):
        rows = self.rows() * 2
        rows[0] = {**rows[0], "new_regress": None}
        self.assertIn("不判通过", self.report(rows))

    def test_missing_alone_review_is_unknown_not_zero_drop(self):
        with patch.object(verdict.V, "graph_of", return_value={"segments": [{"sec": "S01"}]}), \
             patch.object(verdict.V, "parse", return_value=None):
            self.assertIsNone(verdict.alone_count("op60", "g6", "new"))

    def test_duplicate_bead_does_not_replace_missing_bead(self):
        review = {"beads": [{"sec": "S01", "bead": "B1", "status": "说清"}] * 2}
        with patch.object(verdict, "bead_keys", return_value={("S01", "B1"), ("S01", "B2")}), \
             patch.object(verdict.V, "parse", return_value=review):
            self.assertIsNone(verdict.cov_secs("op60", "g6", "new"))

    def test_complete_four_and_eight_review_sets_still_pass(self):
        self.assertIn("快筛： 过", self.report(self.rows()))
        self.assertIn("验收： 过", self.report(self.rows() * 2))


if __name__ == "__main__":
    unittest.main()
