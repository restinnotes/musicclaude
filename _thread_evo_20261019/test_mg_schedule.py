"""Offline regression checks: actual process contention, cooldown, and caller dispatch."""
import json
import multiprocessing
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import mg_schedule as schedule


def reserve_worker(folder, queue):
    try:
        queue.put(("ok", schedule.reserve("child", directory=folder, gap=0.15)))
    except schedule.CoolingDown:
        queue.put(("cooldown", None))


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_independent_processes_share_spacing(self):
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        children = [ctx.Process(target=reserve_worker, args=(self.temp.name, queue)) for _ in range(4)]
        for child in children:
            child.start()
        rows = [queue.get(timeout=15) for _ in children]
        for child in children:
            child.join(15)
            self.assertEqual(child.exitcode, 0)
        self.assertTrue(all(kind == "ok" for kind, _ in rows))
        times = sorted(value for _, value in rows)
        self.assertTrue(all(b - a >= 0.149 for a, b in zip(times, times[1:])), times)

    def test_failure_blocks_fresh_process(self):
        now = time.time()
        state = schedule.fail("failed", "suspicious behavior", directory=self.folder, now=now)
        self.assertEqual(state["cooldown_until"], now + 1800)
        ctx = multiprocessing.get_context("spawn")
        queue = ctx.Queue()
        child = ctx.Process(target=reserve_worker, args=(self.temp.name, queue))
        child.start()
        self.assertEqual(queue.get(timeout=15)[0], "cooldown")
        child.join(15)
        self.assertEqual(child.exitcode, 0)
        self.assertEqual(schedule.status(self.folder)["cooldown_until"], now + 1800)

    def test_read_does_not_extend_and_expiry_allows_one_submission(self):
        state = schedule.fail("old", "timeout", directory=self.folder, now=time.time() - 1801)
        self.assertFalse(schedule.status(self.folder)["cooling"])
        schedule.reserve("resume", directory=self.folder)
        self.assertEqual(schedule.status(self.folder)["cooldown_until"], state["cooldown_until"])

    def test_cooldown_prevents_dispatch_callback(self):
        schedule.fail("failed", "suspicious_user_activity", directory=self.folder)
        with self.assertRaises(schedule.CoolingDown):
            schedule.reserve("new", directory=self.folder, submit=lambda: self.fail("must not send"))

    def test_inflight_old_policy_is_shortened_without_restarting_timer(self):
        failed_at = time.time() - 100
        with schedule.locked(self.folder) as folder:
            schedule._write(folder, {"failed_at": failed_at, "reason": "suspicious behavior", "cooldown_until": failed_at + 3600})
        state = schedule.status(self.folder)
        self.assertEqual(state["cooldown_until"], failed_at + 1800)
        self.assertEqual(schedule.status(self.folder)["cooldown_until"], failed_at + 1800)

    def test_502_is_short_retry_not_protection(self):
        now = time.time()
        state = schedule.fail("gateway", '{"type":"incomplete_response","message":"HTTP 502"}', directory=self.folder, now=now)
        self.assertEqual(state["cooldown_until"], now + 60)
        self.assertEqual(state["failure_kind"], "transient_failure")
        self.assertNotIn("protection_until", state)

    def test_legacy_502_pause_is_corrected_without_restarting(self):
        stamp = time.time() - 100
        with schedule.locked(self.folder) as folder:
            schedule._write(folder, {"failed_at": stamp, "reason": "incomplete_response", "cooldown_until": stamp + 1800})
        state = schedule.status(self.folder)
        self.assertEqual(state["cooldown_until"], stamp + 60)
        self.assertFalse(state["cooling"])
        self.assertEqual(schedule.status(self.folder)["cooldown_until"], stamp + 60)

    def test_ordinary_failure_cannot_clear_active_protection(self):
        now = time.time()
        schedule.fail("protect", "suspicious behavior detected", directory=self.folder, now=now)
        state = schedule.fail("gateway", "HTTP 502", directory=self.folder, now=now+10)
        self.assertEqual(state["cooldown_until"], now+1800)
        self.assertEqual(state["cooldown_kind"], "suspicious_behavior")
        self.assertEqual(state["protection_run"], "protect")

    def test_old_caller_writing_30_minutes_after_migration_is_corrected(self):
        stamp = time.time()-100
        schedule.fail("old", "HTTP 502", directory=self.folder, now=stamp)
        with schedule.locked(self.folder) as folder:
            state = schedule._read(folder)
            state.update(failed_at=stamp+10, reason="incomplete_response", cooldown_until=stamp+1810)
            schedule._write(folder, state)
        self.assertEqual(schedule.status(self.folder)["cooldown_until"], stamp+70)

    def test_only_explicit_suspicious_signals_trigger_long_pause(self):
        for reason in ("suspicious behavior", "suspicious_user_activity", "unusual activity", "可疑行为"):
            self.assertTrue(schedule.suspicious(reason), reason)
        for reason in ("HTTP 502", "HTTP 429 busy", "timeout", "state_evidence", "protection", "incomplete_response"):
            self.assertFalse(schedule.suspicious(reason), reason)

    def test_route_preserves_prompt_and_collects_no_new_work_when_cooling(self):
        import evo
        import mg_call
        schedule.fail("failed", "timeout", directory=self.folder)
        root = self.folder / "runs"
        (root / "blocked").mkdir(parents=True)
        with patch.object(schedule, "DIRECTORY", self.folder), patch.object(evo, "RUNS", root), \
             patch.object(mg_call, "docker", side_effect=AssertionError("must not contact gateway")):
            self.assertIsNone(mg_call.call("blocked", "原提示词", None, evo.G6, {}))
        self.assertEqual((root / "blocked/input.txt").read_text(encoding="utf-8"), "原提示词")

    def test_existing_success_is_collected_during_cooldown(self):
        import evo
        import mg_call
        schedule.fail("other", "timeout", directory=self.folder)
        root = self.folder / "runs"
        target = root / "existing"
        target.mkdir(parents=True)
        (target / "mg_request.json").write_text("{}", encoding="utf-8")
        with patch.object(schedule, "DIRECTORY", self.folder), patch.object(evo, "RUNS", root), \
             patch.object(mg_call, "pending", return_value=("remote", {})), \
             patch.object(mg_call, "verified", return_value=(True, "已完成", {})), \
             patch.object(evo, "log"), patch.object(mg_call, "once", side_effect=AssertionError("must not resend")):
            self.assertEqual(mg_call.call("existing", "原提示词", None, evo.G6, {}), "已完成")
        self.assertEqual((target / "output.txt").read_text(encoding="utf-8"), "已完成")

    def test_old_failure_does_not_discard_latest_pending_request(self):
        import evo
        import mg_call
        target = self.folder / "pending"
        target.mkdir()
        (target / "mg_request.json").write_text(json.dumps({"prompt": "same", "remote_id": "new"}), encoding="utf-8")
        (target / "call_fail_0.log").write_text(json.dumps({"remote_id": "old"}), encoding="utf-8")
        with patch.object(evo, "RUNS", self.folder), patch.object(mg_call, "docker", side_effect=["y", "1"]), \
             patch.object(mg_call, "poll", return_value={"existing": True}):
            self.assertEqual(mg_call.pending("pending", "same"), ("new", {"existing": True}))


if __name__ == "__main__":
    unittest.main()
