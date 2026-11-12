"""gpt2_adapter 的 mock 单元测试（不调用真实模型）。只用标准库 unittest。"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gpt2_adapter as A


def _ok_payload(text="回答正文", model="gpt-5-6-thinking"):
    return json.dumps({"completed": True, "response": text,
                       "metadata": {"model": model, "session_handle": "h",
                                    "elapsed_seconds": 12.5,
                                    "job_directory": "D:\\x\\job-1",
                                    "server_metadata_summary": {"model_slug": model,
                                                                "requested_model_experience": "thinking"}}})


class _Gpt2Mock:
    """只拦截 gpt2 CLI 调用（argv 含 gpt2 入口）；git 等内部调用 passthrough。

    Windows 上真实 argv 是 [cmd.exe, /c, <...gpt2.cmd>, ask, ...]，
    判别看任意元素而非 argv[0]。"""

    def __init__(self, patcher, payload_fn=None, returncode=0, stderr=b"",
                 side_effect=None):
        self.patcher = patcher
        self.payload_fn = payload_fn
        self.returncode = returncode
        self.stderr = stderr
        self.side_effect = side_effect
        self.gpt2_calls = []
        self.real_run = A.RUN_PROCESS

    def __call__(self, argv, **kw):
        # 只认 `ask` 调用；`git -C ...gpt2agent-safechain rev-parse`（取 CLI 版本）不算。
        if (isinstance(argv, list) and "ask" in argv
                and any("gpt2" in str(a).lower() for a in argv)):
            self.gpt2_calls.append(argv)
            if self.side_effect is not None:
                raise self.side_effect
            text = self.payload_fn(argv) if self.payload_fn else _ok_payload()
            out = text.encode("utf-8") if isinstance(text, str) else text
            return subprocess.CompletedProcess(
                args=argv, returncode=self.returncode,
                stdout=out, stderr=self.stderr)
        return self.real_run(argv, **kw)


def _patch(testcase, **kw):
    p = mock.patch.object(A, "RUN_PROCESS")
    m = p.start()
    testcase.addCleanup(p.stop)
    fake = _Gpt2Mock(p, **kw)
    m.side_effect = fake
    return m, fake


def _run_call(prompt, **kw):
    tmp = tempfile.mkdtemp()
    return A.call_web_gpt(kw.pop("model_key", "gpt56w"), prompt,
                          run_id="t", job_id=kw.pop("job_id", "j1"),
                          out_dir=tmp, **kw), Path(tmp)


class CacheKeyTests(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(A, "HOLD_FILE", Path(tempfile.mkdtemp()) / "hold.json")
        p.start()
        self.addCleanup(p.stop)

    def test_key_distinguishes_prompt(self):
        self.assertNotEqual(A.cache_key("gpt56w", "max", "prompt A"),
                            A.cache_key("gpt56w", "max", "prompt B"))

    def test_key_distinguishes_model(self):
        self.assertNotEqual(A.cache_key("gpt56w", "max", "same"),
                            A.cache_key("gpt6w", "max", "same"))

    def test_key_distinguishes_effort(self):
        self.assertNotEqual(A.cache_key("gpt56w", "max", "same"),
                            A.cache_key("gpt56w", "high", "same"))

    def test_key_stable(self):
        self.assertEqual(A.cache_key("gpt56w", "max", "x"),
                         A.cache_key("gpt56w", "max", "x"))


class CallTests(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(A, "HOLD_FILE", Path(tempfile.mkdtemp()) / "hold.json")
        p.start()
        self.addCleanup(p.stop)

    def test_ok_basics(self):
        _, fake = _patch(self, payload_fn=lambda argv: _ok_payload("第一次回答"))
        meta, d = _run_call("你好", job_id="j1")
        self.assertEqual(meta["status"], "ok")
        self.assertEqual((d / "outputs/j1.md").read_text(encoding="utf-8"),
                         "第一次回答")
        self.assertFalse(meta["cache_hit"])
        self.assertEqual(meta["reported_model"], "gpt-5-6-thinking")
        self.assertEqual(len(fake.gpt2_calls), 1)

    def test_cache_hit_same_out_dir(self):
        tmp = tempfile.mkdtemp()
        _, fake = _patch(self, payload_fn=lambda argv: _ok_payload("缓存答案"))
        m1 = A.call_web_gpt("gpt56w", "同一问题", run_id="t",
                            job_id="a", out_dir=tmp, sampling_key="shared")
        self.assertFalse(m1["cache_hit"])
        m2 = A.call_web_gpt("gpt56w", "同一问题", run_id="t",
                            job_id="b", out_dir=tmp, sampling_key="shared")
        self.assertTrue(m2["cache_hit"])
        self.assertEqual(m2["attempts"], 0)
        self.assertEqual((Path(tmp) / "outputs/b.md").read_text(encoding="utf-8"),
                         "缓存答案")
        self.assertEqual(len(fake.gpt2_calls), 1)

    def test_cache_not_reused_across_models(self):
        tmp = tempfile.mkdtemp()

        def payload(argv):
            slug = argv[argv.index("--model") + 1]
            return _ok_payload("答:" + slug, slug)

        _, fake = _patch(self, payload_fn=payload)
        m1 = A.call_web_gpt("gpt56w", "同一问题", run_id="t",
                            job_id="a", out_dir=tmp)
        m2 = A.call_web_gpt("gpt6w", "同一问题", run_id="t",
                            job_id="b", out_dir=tmp)
        self.assertFalse(m1["cache_hit"])
        self.assertFalse(m2["cache_hit"])
        self.assertEqual(len(fake.gpt2_calls), 2)

    def test_long_input_argv_uses_file(self):
        long_prompt = "字" * 20000
        _, fake = _patch(self, payload_fn=lambda argv: _ok_payload("长输入OK"))
        meta, d = _run_call(long_prompt, job_id="long")
        argv = fake.gpt2_calls[0]
        self.assertIn("--file", argv)
        self.assertLess(len(" ".join(argv)), 32000)  # 远小于 Windows 32k 上限
        self.assertEqual(meta["status"], "ok")
        self.assertEqual(meta["prompt_chars"], 20000)
        self.assertEqual((d / "prompts/long.txt").read_text(encoding="utf-8"),
                         long_prompt)

    def test_over_limit_rejected(self):
        _, fake = _patch(self)
        meta, _ = _run_call("x" * (A.MAX_PROMPT_CHARS + 1))
        self.assertEqual(meta["status"], "failed")
        self.assertIn("too long", meta["error"])
        self.assertEqual(len(fake.gpt2_calls), 0)

    def test_garbled_stdout_replacement_counted(self):
        raw = b'{"completed": true, "response": "\xff\xfe\xe4\xb8\xad\xe6\x96\x87", "metadata": {}}'
        _, _fake = _patch(self, payload_fn=lambda argv: raw)
        meta, _ = _run_call("乱码测试")
        self.assertEqual(meta["status"], "ok")
        self.assertGreater(meta.get("replacement_chars", 0), 0)

    def test_nonzero_exit(self):
        _, fake = _patch(self, returncode=1, stderr=b"boom happened")
        meta, d = _run_call("失败测试")
        self.assertEqual(meta["status"], "failed")
        self.assertIn("exit 1", meta["error"])
        self.assertEqual((d / "outputs/j1.md").read_text(encoding="utf-8"), "")
        self.assertIn("attempts", meta)
        self.assertEqual(len(fake.gpt2_calls), 1)

    def test_incomplete_payload_is_failure(self):
        bad = json.dumps({"completed": False, "error_code": "x"})
        _, _fake = _patch(self, payload_fn=lambda argv: bad)
        meta, _ = _run_call("未完成测试")
        self.assertEqual(meta["status"], "failed")
        self.assertIn("incomplete", meta["error"])

    def test_bad_json_stdout(self):
        _, _fake = _patch(self, payload_fn=lambda argv: "不是json")
        meta, _ = _run_call("坏json")
        self.assertEqual(meta["status"], "failed")

    def test_timeout(self):
        _, fake = _patch(
            self, side_effect=subprocess.TimeoutExpired(cmd="gpt2", timeout=5))
        meta, _ = _run_call("超时测试", timeout=5)
        self.assertEqual(meta["status"], "failed")
        self.assertIn("timeout", meta["error"])
        self.assertIsNone(meta["returncode"])
        self.assertEqual(len(fake.gpt2_calls), 1)

    def test_ambiguous_holds_queue_and_second_job_not_submitted(self):
        error = json.dumps({"completed": False, "phase": "post_submit_ambiguous"}).encode()
        _, fake = _patch(self, returncode=1, stderr=error)
        tmp = Path(tempfile.mkdtemp())
        first = A.call_web_gpt("gpt6w", "p", run_id="t", job_id="first", out_dir=tmp)
        second = A.call_web_gpt("gpt56w", "q", run_id="t", job_id="second", out_dir=tmp)
        self.assertTrue(first["queue_stop"])
        self.assertFalse(first["retry_safe"])
        self.assertEqual(second["attempts"], 0)
        self.assertEqual(len(fake.gpt2_calls), 1)

    def test_explicit_presubmit_does_not_hold_queue(self):
        error = json.dumps({"completed": False, "phase": "pre_submit"}).encode()
        _, _fake = _patch(self, returncode=1, stderr=error)
        meta, _ = _run_call("q")
        self.assertTrue(meta["retry_safe"])
        self.assertFalse(meta["queue_stop"])
        self.assertFalse(A.HOLD_FILE.exists())

    def test_unknown_terminal_holds_queue(self):
        _, _fake = _patch(self, payload_fn=lambda argv: "bad json")
        meta, _ = _run_call("q")
        self.assertTrue(meta["queue_stop"])
        self.assertFalse(meta["retry_safe"])

    def test_effort_mismatch_blocked(self):
        _, fake = _patch(self)
        meta, _ = _run_call("档位测试", effort="high")
        self.assertEqual(meta["status"], "failed")
        self.assertIn("effort mismatch", meta["error"])
        self.assertEqual(len(fake.gpt2_calls), 0)

    def test_unknown_model_key(self):
        _, fake = _patch(self)
        meta, _ = _run_call("x", model_key="gpt99w")
        self.assertEqual(meta["status"], "failed")
        self.assertIn("unknown model_key", meta["error"])
        self.assertEqual(len(fake.gpt2_calls), 0)

    def test_meta_has_identity_evidence(self):
        _, _fake = _patch(
            self, payload_fn=lambda argv: _ok_payload("ok", "gpt-6-thinking"))
        meta, _ = _run_call("身份", model_key="gpt6w")
        for k in ("route", "adapter_version", "requested_model",
                  "reported_model", "prompt_sha256", "response_sha256",
                  "cache_key", "returncode", "attempts"):
            self.assertIn(k, meta, k)
        self.assertEqual(meta["route"], "gpt2")
        self.assertNotIn("cookie", json.dumps(meta).lower())

    def test_no_credentials_saved(self):
        _, _fake = _patch(self, payload_fn=lambda argv: _ok_payload("ok"),
                          stderr=b"secret=abc")
        meta, d = _run_call("凭据检查")
        blob = (d / "meta/j1.json").read_text(encoding="utf-8").lower()
        self.assertNotIn("cookie", blob)
        self.assertNotIn("bearer", blob)
        self.assertNotIn("token", blob)


class CmdArgvTests(unittest.TestCase):
    """gpt2.cmd 经 cmd.exe /c 调用（Windows 参数列表直调 .cmd 曾 FileNotFoundError）。"""

    def setUp(self):
        p = mock.patch.object(A, "HOLD_FILE", Path(tempfile.mkdtemp()) / "hold.json")
        p.start()
        self.addCleanup(p.stop)

    @unittest.skipUnless(sys.platform == "win32", "windows only")
    def test_cmd_and_bat_wrapped(self):
        self.assertEqual(A._cmd_argv(r"D:\x\gpt2.cmd"),
                         ["cmd.exe", "/c", r"D:\x\gpt2.cmd"])
        self.assertEqual(A._cmd_argv(r"D:\x\GPT2.BAT")[:2], ["cmd.exe", "/c"])

    def test_exe_not_wrapped(self):
        self.assertEqual(A._cmd_argv(r"D:\x\gpt2.exe"), [r"D:\x\gpt2.exe"])

    def test_env_override(self):
        import importlib
        global A
        try:
            with mock.patch.dict("os.environ", {"MUSIC_GPT2_CMD": r"D:\stub\gpt2.cmd"}):
                A = importlib.reload(A)
                self.assertEqual(A.GPT2_CMD, r"D:\stub\gpt2.cmd")
        finally:
            A = importlib.reload(A)
        self.assertNotEqual(A.GPT2_CMD, r"D:\stub\gpt2.cmd")

    def test_prompt_file_bytes_exact(self):
        """--file 指向的 prompt 落盘字节 = 发出文本（无 LF->CRLF 翻译）。"""
        _, _fake = _patch(self)
        text = "第一行\n第二行\r\n第三行"
        meta, d = _run_call(text, job_id="nl")
        raw = (d / "prompts/nl.txt").read_bytes()
        self.assertEqual(raw, text.encode("utf-8"))
        self.assertEqual(A.hashlib.sha256(raw).hexdigest(), meta["prompt_sha256"])

    @unittest.skipUnless(sys.platform == "win32", "windows only")
    def test_real_subprocess_cmd_stub(self):
        """不 mock subprocess：真实经 cmd.exe /c 跑一个 .cmd 桩，桩再调 python。"""
        tmp = Path(tempfile.mkdtemp())
        stub_py = tmp / "stub.py"
        stub_py.write_text(
            "import json,sys\n"
            "a=sys.argv[1:]\n"
            "assert a[0]=='ask' and '--json' in a\n"
            "t=open(a[a.index('--file')+1],encoding='utf-8').read()\n"
            "m=a[a.index('--model')+1]\n"
            "sys.stdout.buffer.write(json.dumps({'completed':True,"
            "'response':'桩:'+t,'metadata':{'model':m,'server_metadata_summary':{'model_slug':m}}},ensure_ascii=False).encode('utf-8'))\n",
            encoding="utf-8")
        stub_cmd = tmp / "gpt2.cmd"
        stub_cmd.write_text(f'@"{sys.executable}" -I "{stub_py}" %*\r\n',
                            encoding="utf-8")
        out = tmp / "out"
        meta = A.call_web_gpt("gpt6w", "中文提示", run_id="t", job_id="real",
                              out_dir=out, gpt2_cmd=str(stub_cmd), timeout=60)
        self.assertEqual(meta["status"], "ok", meta.get("error"))
        self.assertEqual(meta["reported_model"], "gpt-6-thinking")
        self.assertEqual((out / "outputs/real.md").read_text(encoding="utf-8"),
                         "桩:中文提示")


if __name__ == "__main__":
    unittest.main(verbosity=2)
