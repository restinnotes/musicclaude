"""Offline Windows integration tests. Run: python -B _codex/test_gap.py

Every real module is loaded from UTF-8 source without creating bytecode. evo's
path assignments are replaced in memory before module execution. Workers audit
filesystem writes and block networking; their Popen accepts only the temp fake.
No real GPT executable is launched and no real runs/locks/stamp are written.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import types
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MODEL = "gpt-6-thinking"
NO_WEB = "\n\n\u56de\u7b54\u65f6\u8bf7\u4e0d\u8981\u8fdb\u884c\u8054\u7f51\u641c\u7d22\u3002"

FAKE_SOURCE = r'''
import json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
root = Path(__file__).resolve().parent
args = sys.argv[1:]
inp = Path(args[args.index("--file") + 1])
rid = inp.parent.name
cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))[rid]
message = inp.read_text(encoding="utf-8")
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
event = {"run_id": rid, "launch": time.time(), "args": args, "message": message,
         "attempt": len(list(root.glob(rid + "-event-*.json")))}
ep = root / (rid + "-event-" + str(os.getpid()) + ".json")
save(ep, event)
job = None
if not cfg.get("no_job"):
    time.sleep(cfg.get("delay", 0))
    job = root / "jobs" / ("pro-bridge-" + str(time.time_ns()) + "-" + rid)
    job.mkdir()
    (job / "prompt.txt").write_text(message.rstrip(), encoding="utf-8")
    save(job / "started.json", {"utc": datetime.now(timezone.utc).isoformat()})
    if cfg.get("partial"):
        (job / "submitted.json").write_text('{"utc":', encoding="utf-8")
        (job / "generation-network.json").write_text('{', encoding="utf-8")
        time.sleep(0.12)
    if not cfg.get("no_submit"):
        utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        event["submit"] = datetime.fromisoformat(utc.replace("Z", "+00:00")).timestamp()
        event["submitted_utc"] = utc
        save(job / "submitted.json", {"utc": utc})
        save(job / "generation-network.json", {"first_chunk_ms": None})
        save(ep, event)
        if not cfg.get("no_chunk"):
            time.sleep(cfg.get("chunk_delay", 0.05))
            save(job / "generation-network.json", {"first_chunk_ms": cfg.get("first_chunk_ms", 5)})
            event["first_chunk"] = time.time()
            save(ep, event)
time.sleep(cfg.get("tail", 0))
event["exit"] = time.time()
save(ep, event)
if cfg.get("protection"):
    print("hit your limit", file=sys.stderr)
rc = cfg.get("rc", 0)
if cfg.get("invalid_json"):
    print("not json")
else:
    print(json.dumps({"completed": cfg.get("completed", True), "response": "answer:" + rid,
                      "metadata": {"model": cfg.get("result_model", args[args.index("--model") + 1]),
                                   "thinking_effort": cfg.get("effort", "max"),
                                   "job_directory": str(job) if job else None}}))
sys.exit(rc)
'''


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_sandboxed(root):
    """Load the actual code, replacing only evo path constants before execution."""
    tree = ast.parse((ROOT / "evo.py").read_text(encoding="utf-8"))
    replaced = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("RUNS", "GPT3_RUNS"):
                    folder = root / ("runs" if target.id == "RUNS" else "jobs")
                    node.value = ast.parse("Path(" + repr(str(folder)) + ")", mode="eval").body
                    replaced.add(target.id)
    assert replaced == {"RUNS", "GPT3_RUNS"}
    ast.fix_missing_locations(tree)
    evo = types.ModuleType("evo"); evo.__file__ = str(ROOT / "evo.py")
    sys.modules["evo"] = evo
    exec(compile(tree, evo.__file__, "exec"), evo.__dict__)
    gc = types.ModuleType("gpt3_call"); gc.__file__ = str(ROOT / "gpt3_call.py")
    sys.modules["gpt3_call"] = gc
    exec(compile((ROOT / "gpt3_call.py").read_text(encoding="utf-8"), gc.__file__, "exec"), gc.__dict__)
    gc.GPT3 = str(root / "fake_gpt3.cmd")
    gc.STAMP = root / "stamp.txt"; gc.GATE = root / "gate.lock"; gc.LOCK = root / "slots.lock"
    gc.SLOTS_FILE = root / "gpt3_slots.txt"
    gc.GAP = read_json(root / "settings.json").get("gap", 0.3)
    gc.SUBMIT_TIMEOUT = read_json(root / "settings.json").get("timeout", 8)
    gc.SUBMIT_POLL = 0.025
    gc.random.uniform = lambda a, b: 0.0
    original_popen = subprocess.Popen
    def safe_popen(command, *args, **kwargs):
        assert Path(command[0]).resolve() == Path(gc.GPT3).resolve(), command
        return original_popen(command, *args, **kwargs)
    gc.subprocess.Popen = safe_popen
    return evo, gc


def worker(root, rid):
    root = root.resolve()
    def within(path):
        if isinstance(path, int):
            return True
        return Path(os.fsdecode(path)).resolve().is_relative_to(root)
    def audit(event, args):
        if event == "open":
            path, mode, flags = args
            write = any(c in (mode or "") for c in "wax+") or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
            if write and not within(path):
                raise AssertionError("Write escaped sandbox: " + str(path))
        elif event in ("os.mkdir", "os.remove", "os.rmdir"):
            if not within(args[0]):
                raise AssertionError("Mutation escaped sandbox: " + str(args[0]))
        elif event in ("socket.connect", "socket.bind", "socket.getaddrinfo"):
            raise AssertionError("Network forbidden in offline test")
    sys.addaudithook(audit)
    evo, gc = load_sandboxed(root)
    cfg = read_json(root / "config.json")[rid]
    message = cfg.get("message", "prompt:" + rid + " \u4e2d\u6587\n")
    meta = cfg.get("meta", {})
    before = time.time()
    answer = gc.call(rid, message, cfg.get("prompt_text"), MODEL, meta)
    after = time.time()
    if cfg.get("check_stopped"):
        assert gc.call(rid, message, None, MODEL, meta) is None
    (root / (rid + "-result.json")).write_text(json.dumps({"answer": answer, "before": before,
        "after": after, "state": gc._state, "input_message": message}, ensure_ascii=False), encoding="utf-8")


class GapTests(unittest.TestCase):
    def setup_case(self, root, config, gap=0.3, timeout=8, seed=None):
        (root / "jobs").mkdir(); (root / "runs").mkdir()
        (root / "fake_gpt3.py").write_text(FAKE_SOURCE, encoding="utf-8")
        (root / "fake_gpt3.cmd").write_text('@echo off\n"' + sys.executable + '" -B "' + str(root / "fake_gpt3.py") + '" %*\n', encoding="utf-8")
        (root / "config.json").write_text(json.dumps(config), encoding="utf-8")
        (root / "settings.json").write_text(json.dumps({"gap": gap, "timeout": timeout}), encoding="utf-8")
        (root / "gpt3_slots.txt").write_text("4", encoding="utf-8")
        for rid in config:
            (root / "runs" / rid).mkdir()
        if seed is not None:
            (root / "stamp.txt").write_text(str(seed), encoding="utf-8")

    def start(self, root, rid):
        return subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(root), rid],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def finish(self, proc):
        try:
            out, err = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill(); out, err = proc.communicate()
            self.fail("Worker stuck: " + out.decode("utf-8", "replace") + err.decode("utf-8", "replace"))
        self.assertEqual(proc.returncode, 0, out.decode("utf-8", "replace") + err.decode("utf-8", "replace"))
        return out.decode("utf-8", "replace")

    def wait_event(self, root, rid, field):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            for ep in root.glob(rid + "-event-*.json"):
                try:
                    if field in read_json(ep):
                        return read_json(ep)
                except (ValueError, OSError):
                    pass
            time.sleep(0.02)
        self.fail("Missing event " + rid + ":" + field)

    def events(self, root):
        return sorted((read_json(p) for p in root.glob("*-event-*.json")), key=lambda e: e["launch"])

    def test_four_processes_real_submit_spacing_and_first_chunk(self):
        with tempfile.TemporaryDirectory(prefix="gap_test_") as td:
            root = Path(td)
            config = {"slow_upload": {"delay": 1.5, "chunk_delay": 0.7, "tail": 2.5, "partial": True},
                      "fast_b": {"delay": 0.01, "chunk_delay": 0.1, "tail": 0.8},
                      "fast_c": {"delay": 0.03, "chunk_delay": 0.1, "tail": 0.6},
                      "fast_d": {"delay": 0.02, "chunk_delay": 0.1, "tail": 0.4, "first_chunk_ms": 0}}
            self.setup_case(root, config)
            # Same-prompt stale jobs must never satisfy this call, even if modified later.
            stale = root / "jobs" / "pro-bridge-stale"; stale.mkdir()
            (stale / "prompt.txt").write_text("prompt:slow_upload \u4e2d\u6587\n" + NO_WEB, encoding="utf-8")
            (stale / "submitted.json").write_text('{"utc":"2026-01-01T00:00:00Z"}', encoding="utf-8")
            (stale / "generation-network.json").write_text('{"first_chunk_ms":0}', encoding="utf-8")
            procs = [self.start(root, "slow_upload")]
            self.wait_event(root, "slow_upload", "launch")
            procs.extend(self.start(root, rid) for rid in ("fast_b", "fast_c", "fast_d"))
            outputs = [self.finish(p) for p in procs]
            events = self.events(root)
            self.assertEqual(len(events), 4)
            gaps = []
            for index, e in enumerate(events):
                self.assertIn("--allow-topic-stream", e["args"])
                self.assertEqual(e["args"][:1], ["ask"])
                self.assertEqual(e["message"], "prompt:" + e["run_id"] + " \u4e2d\u6587\n" + NO_WEB)
                result = read_json(root / (e["run_id"] + "-result.json"))
                self.assertEqual(result["answer"], "answer:" + e["run_id"])
                rec = read_json(root / "runs" / e["run_id"] / "call.log")
                self.assertEqual(rec["submitted_utc"], e["submitted_utc"])
                self.assertEqual(rec["message_sha256"], hashlib.sha256(e["message"].encode()).hexdigest())
                if index:
                    prev = events[index - 1]
                    gap = e["submit"] - prev["submit"]; gaps.append(gap)
                    self.assertGreaterEqual(gap, 0.3)
                    self.assertGreaterEqual(e["launch"], prev["first_chunk"])
                    self.assertAlmostEqual(rec["gap_since_prev_submit_s"], gap, places=5)
                else:
                    self.assertIsNone(rec["gap_since_prev_submit_s"])
            # GATE is released before completion, and completion never overwrites STAMP.
            self.assertLess(events[1]["launch"], events[0]["exit"])
            self.assertAlmostEqual(float((root / "stamp.txt").read_text(encoding="utf-8")), events[-1]["submit"], places=5)
            calls = (root / "runs" / "calls.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls), 4)
            print("four-process actual submit gaps:", [round(g, 4) for g in gaps], flush=True)

    def test_timeout_releases_gate_and_keeps_real_submit(self):
        with tempfile.TemporaryDirectory(prefix="gap_test_") as td:
            root = Path(td)
            self.setup_case(root, {"timeout": {"delay": 0.03, "no_chunk": True, "tail": 2},
                                   "follower": {"delay": 0.01}}, timeout=0.45)
            a = self.start(root, "timeout")
            self.wait_event(root, "timeout", "submit")
            b = self.start(root, "follower")
            out = self.finish(a); self.finish(b)
            self.assertIn("WARNING", out); self.assertIn("timed out", out)
            events = self.events(root); self.assertEqual(len(events), 2)
            self.assertLess(events[1]["launch"], events[0]["exit"])
            self.assertGreaterEqual(events[1]["submit"] - events[0]["submit"], 0.3)
            rec = read_json(root / "runs" / "timeout" / "call.log")
            self.assertEqual(rec["submitted_utc"], events[0]["submitted_utc"])
            self.assertAlmostEqual(float((root / "stamp.txt").read_text(encoding="utf-8")), events[1]["submit"], places=5)

    def test_timeout_without_submit_falls_back_to_now(self):
        with tempfile.TemporaryDirectory(prefix="gap_test_") as td:
            root = Path(td)
            self.setup_case(root, {"unknown": {"no_job": True, "tail": 0.9}}, timeout=0.2)
            out = self.finish(self.start(root, "unknown"))
            self.assertIn("WARNING", out)
            result = read_json(root / "unknown-result.json")
            stamp = float((root / "stamp.txt").read_text(encoding="utf-8"))
            self.assertGreaterEqual(stamp, result["before"])
            self.assertLess(stamp, self.events(root)[0]["exit"])
            rec = read_json(root / "runs" / "unknown" / "call.log")
            self.assertIsNone(rec["submitted_utc"]); self.assertIsNone(rec["gap_since_prev_submit_s"])

    def test_early_exit_retry_and_stop(self):
        for protected in (False, True):
            with self.subTest(protected=protected), tempfile.TemporaryDirectory(prefix="gap_test_") as td:
                root = Path(td)
                self.setup_case(root, {"exit": {"no_job": True, "rc": 7, "protection": protected,
                                               "check_stopped": True}}, timeout=5)
                out = self.finish(self.start(root, "exit"))
                self.assertNotIn("WARNING", out)
                self.assertIn("GPT3 STOPPED", out)
                events = self.events(root)
                self.assertEqual(len(events), 1 if protected else 2)
                result = read_json(root / "exit-result.json")
                self.assertIsNone(result["answer"])
                self.assertEqual(result["state"]["total"], len(events))
                self.assertIsNotNone(result["state"]["stop"])
                for i in range(len(events)):
                    rec = read_json(root / "runs" / "exit" / ("call_fail_" + str(i) + ".log"))
                    self.assertIsNone(rec["submitted_utc"])
                    self.assertIsNone(rec["gap_since_prev_submit_s"])
                if not protected:
                    self.assertGreaterEqual(events[1]["launch"] - events[0]["exit"], 0.3)

    def test_exit_after_submit_without_chunk(self):
        with tempfile.TemporaryDirectory(prefix="gap_test_") as td:
            root = Path(td)
            seed = time.time() - 1
            self.setup_case(root, {"exit_submit": {"no_chunk": True, "tail": 0.1}}, seed=seed)
            out = self.finish(self.start(root, "exit_submit"))
            self.assertNotIn("WARNING", out)
            event = self.events(root)[0]
            rec = read_json(root / "runs" / "exit_submit" / "call.log")
            self.assertEqual(rec["submitted_utc"], event["submitted_utc"])
            self.assertAlmostEqual(rec["gap_since_prev_submit_s"], event["submit"] - seed, places=5)
            self.assertAlmostEqual(float((root / "stamp.txt").read_text(encoding="utf-8")), event["submit"], places=5)

    def test_prompt_web_attachment_and_long_prompt_semantics(self):
        with tempfile.TemporaryDirectory(prefix="gap_test_") as td:
            root = Path(td)
            attachment = root / "attachment.txt"; attachment.write_text("payload", encoding="utf-8")
            empty = root / "empty.txt"; empty.write_text("", encoding="utf-8")
            config = {"long": {"message": "x" * 60001, "meta": {"web": True, "attach": [str(attachment), str(empty)]}},
                      "web": {"message": "unchanged web prompt \n\n", "meta": {"web": True}},
                      "no_web_existing": {"message": "already restricted" + NO_WEB}}
            self.setup_case(root, config)
            for rid in config:
                self.finish(self.start(root, rid))
            events = {e["run_id"]: e for e in self.events(root)}
            self.assertEqual(events["web"]["message"], config["web"]["message"])
            rec = read_json(root / "runs" / "web" / "call.log")
            self.assertIsNotNone(rec["submitted_utc"])
            self.assertEqual(events["no_web_existing"]["message"], config["no_web_existing"]["message"])
            long = events["long"]
            self.assertIn("full_prompt.txt", long["message"])
            self.assertEqual((root / "runs" / "long" / "full_prompt.txt").read_text(encoding="utf-8"), "x" * 60001)
            attachments = [long["args"][i + 1] for i, arg in enumerate(long["args"]) if arg == "--attach"]
            self.assertEqual(attachments, [str(attachment), str(root / "runs" / "long" / "full_prompt.txt")])
            self.assertEqual((root / "runs" / "long" / "input.txt").read_text(encoding="utf-8"), long["message"])

    def test_model_and_effort_checks_remain_strict(self):
        for bad in ({"result_model": "wrong-model"}, {"effort": "high"}, {"invalid_json": True}):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory(prefix="gap_test_") as td:
                root = Path(td)
                self.setup_case(root, {"bad": dict(bad, check_stopped=True)})
                self.finish(self.start(root, "bad"))
                result = read_json(root / "bad-result.json")
                self.assertIsNone(result["answer"])
                self.assertEqual(result["state"]["total"], 2)
                self.assertFalse((root / "runs" / "bad" / "output.txt").exists())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        worker(Path(sys.argv[2]), sys.argv[3])
    else:
        if os.name != "nt":
            raise SystemExit("Run on Windows: tests exercise real msvcrt byte locks")
        unittest.main(verbosity=2)
