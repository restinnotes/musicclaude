"""无真实模型调用的身份/历史保护/缓存/进程树回归。"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_integrity as E
import gpt2_adapter as A
import runner as R


class IntegrityTests(unittest.TestCase):
    def test_experience_is_not_model_slug(self):
        md = {"model": "wrong-request-label", "server_metadata_summary": {
            "model_slug": "gpt-5-6-thinking", "requested_model_experience": "thinking"}}
        ev = E.model_evidence(md, "gpt-5-6-thinking")
        self.assertEqual(ev["verdict"], "match")
        self.assertEqual(ev["server_slugs"], ["gpt-5-6-thinking"])

    def test_client_requested_model_not_evidence(self):
        self.assertEqual(E.model_evidence({"model": "gpt-6-thinking"}, "gpt-6-thinking")["verdict"], "unverified")

    def test_resolved_mismatch(self):
        self.assertEqual(E.model_evidence({"resolved_model_slugs": ["gpt-5-6-thinking"]}, "gpt-6-thinking")["verdict"], "mismatch")

    def test_policy_blocks_opus_sol_and_old_muse(self):
        for model in ("opus", "opus_hi", "opus_web", "sol61_cx", "muse", "muse_web"):
            with self.assertRaises(E.PolicyBlocked):
                E.check_policy(model)
        E.check_policy("gflash")

    def test_secret_redaction(self):
        md = E.safe_metadata({"session_handle": "not-public", "nested": {"access_token": "private"},
                              "detail": "secret=abc bearer xyz password=def"})
        text = json.dumps(md)
        for value in ("not-public", "private", "abc", "xyz", "def"):
            self.assertNotIn(value, text)

    def test_alias_self_identification(self):
        self.assertEqual(E.canonical_model("gpro_web"), E.canonical_model("gpro"))
        self.assertEqual(E.canonical_model("gflash_web"), E.canonical_model("gflash"))

    def test_checked_resume_rejects_legacy_meta(self):
        d = Path(tempfile.mkdtemp())
        E.write_json(d / "meta/j.json", {"status": "ok", "job_id": "j"})
        with self.assertRaises(E.ArtifactConflict):
            E.checked_resume(d, "j", {"prompt_sha256": "a", "producer": {}})

    def test_cli_content_changes_identity(self):
        d = Path(tempfile.mkdtemp())
        p = d / "gpt2.cmd"
        p.write_text("a")
        with mock.patch.object(A, "SAFECHAIN_ROOT", d), mock.patch.object(A, "_cli_version", return_value="same"):
            x = A.producer_identity(str(p))
            p.write_text("b")
            y = A.producer_identity(str(p))
        self.assertNotEqual(x, y)

    def test_image_content_changes_identity_at_same_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "score.png"
            image.write_bytes(b"first-image")
            job = {"job_id": "j", "model_key": "luna_noweb", "prompt": "inspect",
                   "extra": {"images": [str(image)]}}
            first = E.job_identity(job, {"cli": "stub"})
            image.write_bytes(b"second-image")
            second = E.job_identity(job, {"cli": "stub"})
            self.assertNotEqual(first, second)
            self.assertEqual(second["image_sha256"][str(image)], E.sha_file(image))

    def test_missing_image_fails_before_identity_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            job = {"job_id": "j", "model_key": "luna_noweb", "prompt": "inspect",
                   "extra": {"images": [str(Path(tmp) / "missing.png")]}}
            with self.assertRaises(FileNotFoundError):
                E.job_identity(job, {"cli": "stub"})

    def test_sampling_changes_key(self):
        prod = {"cli_version": "x"}
        self.assertNotEqual(A.cache_key("gpt56w", "max", "same", producer=prod, sampling_key="s1"),
                            A.cache_key("gpt56w", "max", "same", producer=prod, sampling_key="s2"))

    def test_adapter_resume_preserves_raw_and_metadata(self):
        d = Path(tempfile.mkdtemp())
        payload = json.dumps({"completed": True, "response": "中文回答", "metadata": {
            "model": "gpt-6-thinking", "session_handle": "private-handle",
            "server_metadata_summary": {"model_slug": "gpt-6-thinking", "requested_model_experience": "thinking"}}}).encode()
        prod = {"route": "gpt2", "cli": "stub", "cli_version": "1", "adapter_version": A.ADAPTER_VERSION}
        with mock.patch.object(A, "producer_identity", return_value=prod), \
             mock.patch.object(A, "HOLD_FILE", d / "hold"), \
             mock.patch.object(A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload, b"")) as call:
            m = A.call_web_gpt("gpt6w", "问题", run_id="t", job_id="j", out_dir=d)
            raw = (d / m["stdout_file"]).read_bytes()
            disk = (d / "meta/j.json").read_bytes()
            m2 = A.call_web_gpt("gpt6w", "问题", run_id="t", job_id="j", out_dir=d)
            self.assertTrue(m2["resumed"])
            self.assertEqual(call.call_count, 1)
            self.assertEqual(raw, (d / m["stdout_file"]).read_bytes())
            self.assertEqual(disk, (d / "meta/j.json").read_bytes())
            self.assertNotIn(b"private-handle", raw + disk)
            with self.assertRaises(E.ArtifactConflict):
                A.call_web_gpt("gpt6w", "改变问题", run_id="t", job_id="j", out_dir=d)

    def test_runner_gpt2_fields_persisted(self):
        d = Path(tempfile.mkdtemp())
        job = {"job_id": "j", "model_key": "gpt56w", "branch": "test", "prompt": "问题",
               "prompt_version": "v", "prompt_template": "t", "work_key": "op60", "sample": 2}
        prod = {"route": "gpt2", "cli": "stub", "cli_version": "1"}
        payload = json.dumps({"completed": True, "response": "回答", "metadata": {
            "server_metadata_summary": {"model_slug": "gpt-5-6-thinking"}}}).encode()
        with mock.patch.object(R, "GPT2_KEYS", ("gpt56w", "gpt6w")), \
             mock.patch.object(A, "producer_identity", return_value=prod), \
             mock.patch.object(A, "HOLD_FILE", d / "hold"), \
             mock.patch.object(A, "RUN_PROCESS", return_value=subprocess.CompletedProcess([], 0, payload, b"")) as call:
            R.run_job(d, job)
            disk = json.loads((d / "meta/j.json").read_text(encoding="utf-8"))
            self.assertEqual(disk["branch"], "test")
            self.assertEqual(disk["sample"], 2)
            R.run_jobs(d, [job])
            self.assertEqual(call.call_count, 1)
            with self.assertRaises(E.ArtifactConflict):
                R.run_jobs(d, [dict(job, prompt="different")])

    def test_timeout_reclaims_child_tree(self):
        d = Path(tempfile.mkdtemp())
        marker, pidfile = d / "escaped.txt", d / "child.pid"
        child = "import time,pathlib;time.sleep(3);pathlib.Path(%r).write_text('escaped')" % str(marker)
        parent = "import subprocess,sys,pathlib,time;p=subprocess.Popen([sys.executable,'-I','-c',%r]);pathlib.Path(%r).write_text(str(p.pid));time.sleep(20)" % (child, str(pidfile))
        with self.assertRaises(subprocess.TimeoutExpired):
            E.run_process([sys.executable, "-I", "-c", parent], timeout=1)
        self.assertTrue(pidfile.exists())
        # 被回收的子进程不应在父超时之后产生文件。
        import time
        time.sleep(3.2)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
