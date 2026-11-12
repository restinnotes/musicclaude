"""独立 attempt、只读恢复、解析失败与保护停队列；无真实模型调用。"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import experiment_calls as X
import execution_integrity as E


def ident(job):
    return E.job_identity(job, {"route": "stub", "version": "1"})


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        self.submissions = []
        p = mock.patch.object(X.runner, "request_identity_for", side_effect=ident)
        p.start()
        self.addCleanup(p.stop)

    def runner(self, outputs):
        def run(d, job, timeout):
            i = ident(job)
            hit = E.checked_resume(d, job["job_id"], i)
            if hit:
                return hit
            self.submissions.append(job["job_id"])
            result = outputs[len(self.submissions) - 1]
            if isinstance(result, str):
                result = {"status": "ok", "text": result}
            text = result.get("text", "")
            pf, op = "prompts/" + job["job_id"] + ".txt", "outputs/" + job["job_id"] + ".md"
            E.write_text(d / pf, job["prompt"])
            E.write_text(d / op, text)
            m = dict(result, prompt_file=pf, output_file=op, request_identity=i,
                     producer_identity=i["producer"], response_sha256=E.sha_text(text))
            E.write_json(d / "meta" / (job["job_id"] + ".json"), m)
            return m
        p = mock.patch.object(X.runner, "run_job", side_effect=run)
        p.start()
        self.addCleanup(p.stop)

    def call(self, parser=None, **kw):
        parser = parser or (lambda s: (s if s == "valid" else None, None if s == "valid" else "bad"))
        return X.call(self.d, "step", "core", "gflash", "中文\n输入\r\n", parser,
                      [1], "v0", **kw)

    def test_parser_resampling_uses_new_id_then_resume_zero_new_submissions(self):
        self.runner(["bad", "valid"])
        r = self.call()
        self.assertTrue(r["parse_ok"])
        self.assertEqual(len(self.submissions), 2)
        self.assertNotEqual(*self.submissions)
        meta_before = {p.name: p.read_bytes() for p in (self.d / "meta").iterdir()}
        r2 = self.call()
        self.assertTrue(r2["cached"])
        self.assertEqual(len(self.submissions), 2)
        self.assertEqual(meta_before, {p.name: p.read_bytes() for p in (self.d / "meta").iterdir()})

    def test_safe_presubmit_failure_remains_readonly(self):
        self.runner([{"status": "failed", "error": "presubmit", "retry_safe": True}, "valid"])
        self.assertTrue(self.call()["parse_ok"])
        before = (self.d / "meta" / (self.submissions[0] + ".json")).read_bytes()
        self.assertTrue(self.call()["parse_ok"])
        self.assertEqual(len(self.submissions), 2)
        self.assertEqual(before, (self.d / "meta" / (self.submissions[0] + ".json")).read_bytes())

    def test_queue_stop_never_retries(self):
        self.runner([{"status": "failed", "error": "ambiguous", "retry_safe": True, "queue_stop": True}])
        for _ in range(2):
            r = self.call()
            self.assertFalse(r["parse_ok"])
            self.assertTrue(r["queue_stop"])
        self.assertEqual(len(self.submissions), 1)

    def test_unknown_failure_not_resubmitted(self):
        self.runner([{"status": "failed", "error": "unknown"}])
        self.call()
        self.call()
        self.assertEqual(len(self.submissions), 1)

    def test_legacy_identity_never_overwritten(self):
        job = "core__h" + E.sha_text("中文\n输入\r\n")[:12] + "__attempt0"
        p = self.d / "meta" / (job + ".json")
        E.write_json(p, {"status": "ok"})
        raw = p.read_bytes()
        self.runner([])
        with self.assertRaises(E.ArtifactConflict):
            self.call()
        self.assertEqual(raw, p.read_bytes())
        self.assertFalse(self.submissions)

    def test_tampered_output_not_reused(self):
        self.runner(["valid"])
        r = self.call()
        E.write_text(self.d / r["output_file"], "tampered")
        with self.assertRaises(E.ArtifactConflict):
            self.call()
        self.assertEqual(len(self.submissions), 1)

    def test_parser_exception_recorded_then_new_attempt(self):
        self.runner(["throws", "valid"])
        def parse(s):
            if s == "throws":
                raise ValueError("bad schema")
            return s, None
        r = self.call(parse)
        self.assertIn("parser ValueError", r["attempts"][0]["parse_error"])
        self.assertTrue(r["parse_ok"])

    def test_invalid_attempt_budget_rejected_before_submission(self):
        self.runner([])
        with self.assertRaises(ValueError):
            self.call(max_attempts=0)
        self.assertFalse(self.submissions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
