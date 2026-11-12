"""run137_e7_flash_diag 纯 mock 回归：import 不能调用 CLI；mock 不与真实目录冲突。

只用标准库 + unittest.mock。允许工程测试，不得启动真实 runner。
跑法（cwd 为仓库根）：python -I tools/tests/test_run137_e7_flash_diag.py
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
RUN137_DIR = ROOT / "runs" / "run137_e7_flash_diag"
RUN134_GO = ROOT / "runs" / "run134_e7_diag" / "go.py"
RUN137_GO = RUN137_DIR / "go.py"
BEFORE134 = RUN134_GO.read_bytes()


def load137(name="run137_go"):
    spec = importlib.util.spec_from_file_location(name, RUN137_GO)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class ImportSafetyTests(unittest.TestCase):
    def test_import_has_no_cli_side_effect(self):
        with mock.patch("subprocess.run") as sr, mock.patch("subprocess.Popen") as pop:
            mod = load137("run137_import_probe")
            self.assertEqual(mod.RUN_ID, "run137_e7_flash_diag")
            sr.assert_not_called()
            pop.assert_not_called()

    def test_import_does_not_touch_real_run_dir(self):
        before = {p.name for p in RUN137_DIR.iterdir()} if RUN137_DIR.exists() else set()
        load137("run137_import_probe2")
        after = {p.name for p in RUN137_DIR.iterdir()} if RUN137_DIR.exists() else set()
        self.assertEqual(before, after)

    def test_run134_source_untouched(self):
        load137("run137_import_probe3")
        self.assertEqual(RUN134_GO.read_bytes(), BEFORE134)

    def test_frozen_config(self):
        mod = load137("run137_import_probe4")
        self.assertEqual(mod.CFG137["gen"], "gflash")
        self.assertEqual(mod.CFG137["chooser"], "gflash")
        self.assertEqual(tuple(mod.CFG137["auditors"]), ("gflash", "luna_noweb"))
        self.assertEqual(tuple(mod.CFG137["judges"]), ("gflash", "luna_noweb"))
        self.assertEqual(mod.CFG137["history"], "run130:gpt56w")

    def test_no_done_write_path(self):
        text = RUN137_GO.read_text(encoding="utf-8")
        # 允许 unlink 旧 DONE（清理），但绝不允许写 DONE
        self.assertNotIn('("DONE").write_text', text)
        self.assertNotIn("('DONE').write_text", text)
        self.assertIn("COMPLETION_PENDING", text)


class MockFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load137("run137_mock_flow")

    def test_full_mock_flow(self):
        mod = self.mod
        tmp = Path(tempfile.mkdtemp(prefix="run137_test_"))
        import runner as _runner
        count = {"n": 0}
        fake = mod.r134.fake_run_job

        def counting_fake(run_dir, job, timeout=3600):
            count["n"] += 1
            return fake(run_dir, job, timeout=timeout)

        real_out = mod.OUT_DIR
        try:
            with mock.patch.object(_runner, "run_job", counting_fake):
                ok, problems = mod.run_all(tmp, mod.STAGES, 4)
            self.assertTrue(ok, problems)
            first = count["n"]
            self.assertGreater(first, 0)
            # 旧 Store 缓存（cache_<step>.json）不得出现；新层只写 cache_<step>_exact.json
            old_caches = list(tmp.glob("cache_*.json"))
            self.assertTrue(old_caches)
            for p in old_caches:
                self.assertIn("_exact", p.name, p.name)
            # surface k3 解析失败重试被演练
            import json as _json
            S = _json.loads((tmp / "surface.json").read_text(encoding="utf-8"))
            self.assertEqual(len(S["records"][2]["attempts"]), 2)
            # 缺项落 completion：PENDING 在，DONE 永不在
            self.assertTrue((tmp / "COMPLETION_PENDING").exists())
            self.assertFalse((tmp / "DONE").exists())
            pending = (tmp / "COMPLETION_PENDING").read_text(encoding="utf-8")
            for needle in ("two-w", "Muse", "run135", "hold"):
                self.assertIn(needle, pending)
            # 重建锚声明
            man = _json.loads((tmp / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertIn("重建锚", man["extra"]["reconstruction_note"])
            self.assertTrue(man["extra"]["history_producer"].startswith("unknown"))
            self.assertIn("stop_reasons", man["extra"])
            for slot_file in ("muse_review_pack.json", "twow_review_pack.json"):
                pack = _json.loads((tmp / slot_file).read_text(encoding="utf-8"))
                self.assertEqual(len(pack["tasks"]), 2 * 3)
                self.assertTrue(all("prompt_sha256" in t and "mapping" in t for t in pack["tasks"]))
            muse_pack = _json.loads((tmp / "muse_review_pack.json").read_text(encoding="utf-8"))
            self.assertIn("T3", muse_pack["status"])
            # lifecycle 章节
            report = (tmp / "report.md").read_text(encoding="utf-8")
            for life in ("KEEP", "RETIRE", "REPLACE", "APPEND"):
                self.assertIn(life, report)
            # 断点续跑零新调用
            with mock.patch.object(_runner, "run_job", counting_fake):
                ok2, problems2 = mod.run_all(tmp, mod.STAGES, 4)
            self.assertTrue(ok2, problems2)
            self.assertEqual(count["n"], first)
        finally:
            mod.OUT_DIR = real_out
            mod.r134.OUT_DIR, mod.r134.RUN_ID = real_out, "run137_e7_flash_diag"
            import shutil as _sh
            _sh.rmtree(tmp, ignore_errors=True)

    def test_mock_never_touches_real_dir(self):
        mod = self.mod
        run_dir = ROOT / "runs" / "run137_e7_flash_diag"
        before = {p.name for p in run_dir.iterdir()}
        self.assertTrue(mod.run_mock137(2))
        after = {p.name for p in run_dir.iterdir()}
        self.assertEqual(before, after)
        self.assertEqual(RUN134_GO.read_bytes(), BEFORE134)

    def test_canonical_self_flag(self):
        mod = self.mod
        self.assertEqual(mod.self_flag137("c_gflash_s1", "gflash"), "a,c")
        self.assertEqual(mod.self_flag137("c_gflash_s1", "luna_noweb"), "否")
        # _web 后缀归一：gflash_web 若参评同样标 a,c（run134 旧逻辑会漏标）
        self.assertEqual(mod.self_flag137("c_gflash_s1", "gflash_web"), "a,c")

    def test_verify_rejects_incomplete(self):
        mod = self.mod
        tmp = Path(tempfile.mkdtemp(prefix="run137_verify_"))
        real_out = mod.OUT_DIR
        try:
            mod.OUT_DIR = tmp
            (tmp / "why.json").write_text('{"records": []}', encoding="utf-8")
            (tmp / "mech.json").write_text('{"records": []}', encoding="utf-8")
            (tmp / "surface.json").write_text('{"records": []}', encoding="utf-8")
            ok, problems = mod.verify137()
            self.assertFalse(ok)
            self.assertTrue(problems)
        finally:
            mod.OUT_DIR = real_out
            import shutil as _sh
            _sh.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
