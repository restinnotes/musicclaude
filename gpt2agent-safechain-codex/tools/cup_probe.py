# ChatGPT Web route (gpt2agent-safechain) for the music runs, with a degradation gate.
# One provider and one event loop per process; the transport serialises turns per account and spaces them
# >= GPT2AGENT_MIN_ACCOUNT_INTERVAL_SECONDS (default 5 s). Uses the local Codex login (~/.codex/auth.json).
#
# Degradation policy (user, 2026-09-26):
#   - Only gpt-5-6-thinking at max effort.
#   - A job is *suspect* when the server resolves another slug, or a non-"light" job finishes in < SUSPECT_SECONDS.
#   - A suspect job triggers the fixed cup-matching probe. The probe normally takes > 3 min and answers 8.
#     Probe >= PROBE_MIN_SECONDS and answer 8 -> not degraded: the suspect job's output is kept, queue continues.
#     Otherwise -> high-confidence degradation: the queue stops.
#   - Account-protection signals (403/429/challenge/cooldown/latch) stop the queue; other single-job failures are
#     logged and skipped. Jobs whose meta is "ok" are skipped; jobs with a submit marker but no ok result are never
#     resubmitted.
# Non-web jobs get HARNESS_NO_WEB appended (user: instruction following keeps it offline well enough).
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", r"D:\musicclaude\gpt2agent-safechain"))
MODEL = "gpt-5-6-thinking"
EFFORT = "max"
SUSPECT_SECONDS = float(os.environ.get("CHATGPT_SUSPECT_SECONDS", "60"))
PROBE_MIN_SECONDS = float(os.environ.get("CHATGPT_PROBE_MIN_SECONDS", "180"))
HARNESS_NO_WEB = "\n\n回答时请不要进行联网搜索。"
PROTECTION = re.compile(r"\b(403|429)\b|challenge|cooldown|latch|rate.?limit|usage.?limit|protect", re.I)
PROBE_PROMPT = """有一个水杯配对游戏。共有 4 种不同颜色的水杯，每种颜色各有两个。将同色的两个水杯分别放在上下两层，因此
上下两层各有 4 个水杯。下层 4 个水杯按某个未知顺序排列，挑战者无法看到它们；上层水杯的颜色和位置则完
全可见。游戏开始后，挑战者可以反复进行以下操作：

1. 向裁判询问当前有多少个位置满足“上下两个水杯颜色相同”。裁判只回答匹配位置的总数，不透露具体是哪些位置；
2. 根据目前获得的所有信息，挑战者可以选择交换上层任意两个相邻位置的水杯，注意只能是相邻，不能是任意两个。

当 4 个位置全部匹配时，游戏结束。问题：
挑战者应采用何种策略，才能保证对于下层水杯的任意排列都能完成配对？
所有能保证成功的策略中，最坏情况所需的交换次数最少是多少？
回答时请不要进行联网搜索，也不要写代码来辅助计算(包括思考过程中)。
假设答案是 x ，你需要给出严格的证明，为什么 x 可行，为什么小于 x 不可行。"""
PROBE_ANSWER = re.compile(r"x\s*[=＝]\s*8|答案[^0-9\n]{0,12}8|最少[^0-9\n]{0,20}8|8\s*次")


def _save(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def _elapsed(record: dict) -> float:
    meta = record.get("provider_meta") or {}
    return float(meta.get("turn_elapsed_seconds") or record.get("seconds") or 0)


def suspect_reason(job: dict, record: dict) -> str | None:
    slugs = (record.get("provider_meta") or {}).get("resolved_model_slugs") or []
    if job.get("model", MODEL) not in slugs:
        return f"server resolved {slugs}, not {job.get('model', MODEL)}"
    if not job.get("light") and _elapsed(record) < SUSPECT_SECONDS:
        return f"answered in {_elapsed(record):.0f}s < {SUSPECT_SECONDS:.0f}s"
    return None


class Runner:
    def __init__(self, run_dir: Path):
        sys.path[:0] = [str(REPO / "vendor"), str(REPO / "src")]
        from chatgpt_provider.gpt2agent_provider import GPT2AgentProvider
        from chatgpt_provider.protocol import JobConfig, ProviderError
        self.JobConfig, self.ProviderError = JobConfig, ProviderError
        self.provider = GPT2AgentProvider(site_packages=str(REPO / "vendor"))
        self.run_dir = Path(run_dir).resolve()
        self.log_path = self.run_dir / "chatgpt_gate.log"

    def log(self, line: str) -> None:
        line = f"{time.strftime('%m-%d %H:%M:%S')} {line}"
        print(line, flush=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    async def turn(self, job: dict) -> dict:
        """Submit one job exactly once; returns its saved record."""
        rd = self.run_dir
        job_id = job["job_id"]
        meta_path, marker = rd / "meta" / f"{job_id}.json", rd / "meta" / f"{job_id}.submitted.json"
        model, effort = job.get("model", MODEL), job.get("thinking_effort", EFFORT)
        prompt = job["prompt"]
        (rd / "prompts").mkdir(parents=True, exist_ok=True)
        (rd / "prompts" / f"{job_id}.txt").write_text(prompt, encoding="utf-8")
        record = {k: v for k, v in job.items() if k != "prompt"}
        record.update(status="queued", model_key="gpt56_web", model_name=model, thinking_effort=effort,
                      prompt_file=f"prompts/{job_id}.txt", output_file=f"outputs/{job_id}.md",
                      prompt_chars=len(prompt), attempts=0, output_chars=0, tool_counts={})
        _save(meta_path, record)
        started = time.monotonic()

        async def before_submit():
            marker.parent.mkdir(parents=True, exist_ok=True)
            with marker.open("x", encoding="utf-8") as s:
                json.dump({"job_id": job_id, "model": model,
                           "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest()}, s)
            record.update(status="submitting", attempts=1)
            _save(meta_path, record)

        try:
            result = await self.provider.complete_chat(
                prompt=prompt, config=self.JobConfig(model=model, thinking_effort=effort), pre_submit=before_submit)
            out = rd / record["output_file"]
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(result.text, encoding="utf-8")
            record.update(status="ok", output_chars=len(result.text), provider_meta=result.meta)
        except self.ProviderError as exc:
            record.update(status="failed", error=str(exc), phase=exc.phase.value,
                          retryable=exc.retryable, ambiguous=exc.ambiguous)
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}", ambiguous=marker.exists())
        record["seconds"] = round(time.monotonic() - started, 1)
        if record["status"] == "ok":
            marker.unlink(missing_ok=True)  # the marker only guards submits whose outcome is unknown
        _save(meta_path, record)
        pm = record.get("provider_meta") or {}
        self.log(f"{record['status']} {job_id} {_elapsed(record):.0f}s out={record['output_chars']} "
                 f"slugs={pm.get('resolved_model_slugs')} web={pm.get('web_citations', 0)} {record.get('error', '')[:200]}")
        return record

    async def probe(self, why: str) -> bool:
        pid = "probe__cup__" + time.strftime("%m%d_%H%M%S")
        self.log(f"PROBE start ({why})")
        rec = await self.turn({"job_id": pid, "prompt": PROBE_PROMPT, "branch": "probe", "light": True})
        text = (self.run_dir / rec["output_file"]).read_text(encoding="utf-8") if rec["status"] == "ok" else ""
        answered_8 = bool(PROBE_ANSWER.search(text))
        passed = rec["status"] == "ok" and _elapsed(rec) >= PROBE_MIN_SECONDS and answered_8
        rec.update(probe_answer_8=answered_8, probe_passed=passed)
        _save(self.run_dir / "meta" / f"{pid}.json", rec)
        self.log(f"PROBE {'PASS' if passed else 'FAIL'} {pid} {_elapsed(rec):.0f}s answer8={answered_8}")
        return passed

    async def run(self, jobs: list[dict], baseline_probe: bool = True) -> str:
        try:
            if baseline_probe and not await self.probe("baseline before queue"):
                return "degraded_at_start"
            for job in jobs:
                meta_path = self.run_dir / "meta" / f"{job['job_id']}.json"
                marker = self.run_dir / "meta" / f"{job['job_id']}.submitted.json"
                if meta_path.exists() and json.loads(meta_path.read_text(encoding="utf-8")).get("status") in ("ok", "fast_ok"):
                    continue
                if marker.exists():
                    self.log(f"skip {job['job_id']}: submitted earlier with unknown outcome; not resubmitting")
                    continue
                rec = await self.turn(job)
                if rec["status"] != "ok":
                    if PROTECTION.search(rec.get("error", "")):
                        self.log("STOP: account-protection signal")
                        return "protection_stop"
                    continue  # single-job failure: logged, move on
                reason = suspect_reason(job, rec)
                if reason:
                    if not await self.probe(f"{job['job_id']}: {reason}"):
                        rec.update(status="degraded", degradation_reason=reason)
                        _save(meta_path, rec)
                        self.log("STOP: high-confidence degradation confirmed by probe")
                        return "degraded"
                    rec.update(status="fast_ok", fast_reason=reason)  # genuine quick answer, probe healthy
                    _save(meta_path, rec)
            return "done"
        finally:
            await self.provider.aclose()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=Path, required=True)
    ap.add_argument("--run-dir", type=Path, required=True)
    ap.add_argument("--no-baseline-probe", action="store_true")
    a = ap.parse_args()
    jobs = json.loads(a.jobs.read_text(encoding="utf-8"))
    r = Runner(a.run_dir)
    outcome = asyncio.run(r.run(jobs, baseline_probe=not a.no_baseline_probe))
    r.log(f"QUEUE {outcome}")
    return 0 if outcome == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
