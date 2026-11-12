#!/usr/bin/env python3
"""Local 8-inflight / 1-init pipeline for the frozen 2026-10-09 music baseline.

Trusted scheduler code. Lives in D:/musicclaude/_baseline_parallel_control_20261010.
Frozen data/scripts under --data-root are NEVER modified here.

Rules (from task brief):
- ThreadPool max_workers=8 concurrent `gpt2 ask --file ABS --model EXACT --json`.
  Browser-init serialization is enforced natively by HeadlessNative provider's
  InitializerLock (OS-global file lock, 600s timeout); this scheduler does NOT
  add its own init gate, does NOT touch credentials, does NOT kill/restart
  in-flight calls.
- Preserve existing success AND ambiguous evidence (no overwrite, no retry of
  ambiguous). Confirmed pre-submit failures (local evidence: phase=pre_submit
  marker in stderr/meta) get exactly one explicit retry, old files archived to
  attemptNN (nothing deleted).
- Per-task failure stops only that task; queue continues; no auto retry loop.
- Protection: on 403/429/challenge/captcha/rate-limit signals -> pause new
  submissions, drain in-flight, write terminal marker, exit 3.
- All children hidden: CREATE_NO_WINDOW (+STARTF_USESHOWWINDOW), detached.
- status.json + events.jsonl throughout; pipeline_terminal.json ALWAYS written.
"""
import argparse
import datetime
import hashlib
import json
import os
import queue as queue_mod
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path


def _wait_any(futs: set):
    done, pending = wait(futs, return_when=FIRST_COMPLETED)
    return done, pending

HERE = Path(__file__).resolve().parent
os.chdir(HERE)  # trusted cwd; run under `python -I`
sys.path.insert(0, str(HERE))

SAFECHAIN_ROOT = Path(r"D:\musicclaude\gpt2agent-safechain")
GPT2_PY = SAFECHAIN_ROOT / ".venv-local" / "Scripts" / "python.exe"
GPT2_CLI = SAFECHAIN_ROOT / "tools" / "chatgpt_web" / "gpt2_cli.py"
# NOTE(2026-10-10 r01 postmortem): never spawn gpt2.cmd via cmd.exe — the
# console host opens a visible WindowsTerminal window that CREATE_NO_WINDOW on
# the outer Popen cannot suppress. Spawn the venv interpreter on gpt2_cli.py
# directly; argv-equivalent to `gpt2 ask --file --model --json`. Provider files
# themselves are untouched (all inner spawns already carry CREATE_NO_WINDOW).
MODEL = {"gpt6w": "gpt-6-thinking", "gpt56w": "gpt-5-6-thinking"}
INIT_LOCK_PATH = Path(r"D:\musicclaude\gpt2agent-safechain\runs\yi-cookie-repair-20261006\headless-initializer.lock")
RUN_DIR = HERE / "run"
PAUSE_FLAG = RUN_DIR / "pause.flag"
STOP_FLAG = RUN_DIR / "stop.flag"

PROTECT_TOKENS = ("403", "429", "challenge", "captcha", "rate_limit",
                  "rate-limit", "ratelimit", "cloudflare", "too many requests",
                  "temporarily blocked", "access denied")


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def hidden_popen_kwargs():
    # NOTE(2026-10-10 r01 postmortem): CREATE_NO_WINDOW alone. DETACHED_PROCESS
    # must NOT be OR-ed in — on Windows it detaches the child into a new
    # console session and CREATE_NO_WINDOW is ignored, which is exactly the
    # visible-terminal regression seen in r01.
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kw["startupinfo"] = si
    else:
        kw["start_new_session"] = True
    kw["stdin"] = subprocess.DEVNULL
    return kw


def save_atomic(p: Path, text: str):
    """Write new evidence file; refuse to overwrite."""
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() or os.path.lexists(p):
        raise FileExistsError(f"Would overwrite immutable evidence: {p}")
    tmp = p.with_name("." + p.name + ".writing")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)


def compact(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


class Reporter:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = run_dir / "events.jsonl"
        self.status_path = run_dir / "status.json"
        self.lock = threading.Lock()
        self.status = {}

    def event(self, etype: str, **fields):
        rec = {"utc": utcnow(), "type": etype}
        rec.update(fields)
        line = json.dumps(rec, ensure_ascii=False)
        with self.lock:
            with self.events_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        return rec

    def set_status(self, **fields):
        with self.lock:
            self.status.update(fields)
            self.status["updated_utc"] = utcnow()
            tmp = self.status_path.with_name(".status.json.writing")
            tmp.write_text(compact(self.status), encoding="utf-8")
            tmp.replace(self.status_path)


# ---------------- queue construction (read-only scan of frozen data-root) ----

def classify_trial_slot(data_root: Path, model: str, job_id: str, rnd: str):
    """Return (decision, detail). decision in: preserve / retry_presubmit / new / skip_ambiguous."""
    meta_p = data_root / "results" / "trials" / model / job_id / (rnd + ".meta.json")
    txt_p = data_root / "results" / "trials" / model / job_id / (rnd + ".txt")
    if not meta_p.exists():
        return ("new", "missing meta")
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
    except Exception as e:
        return ("skip_ambiguous", f"unreadable meta: {e}")
    if txt_p.exists() and meta.get("status") == "success" and meta.get("completed") is True:
        return ("preserve", "success exists")
    if meta.get("status") == "confirmed_pre_submit_failure" and meta.get("phase") == "pre_submit":
        # local evidence required: pre_submit marker in stderr file
        err_p = data_root / "results" / "trials" / model / job_id / (rnd + ".stderr.txt")
        try:
            err = err_p.read_text(encoding="utf-8", errors="replace") if err_p.exists() else ""
        except Exception:
            err = ""
        if '"phase": "pre_submit"' in err or '"phase":"pre_submit"' in err or meta.get("phase") == "pre_submit":
            return ("retry_presubmit", "confirmed pre-submit w/ local evidence")
    return ("skip_ambiguous", f"status={meta.get('status')} phase={meta.get('phase')}")


def classify_review_slot(data_root: Path, judge: str, jid: str):
    meta_p = data_root / "results" / "reviews" / judge / (jid + ".meta.json")
    txt_p = data_root / "results" / "reviews" / judge / (jid + ".txt")
    if not meta_p.exists():
        return ("new", "missing meta")
    try:
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
    except Exception as e:
        return ("skip_ambiguous", f"unreadable meta: {e}")
    if txt_p.exists() and meta.get("status") == "success" and meta.get("completed") is True:
        return ("preserve", "success exists")
    if meta.get("status") == "confirmed_pre_submit_failure" and meta.get("phase") == "pre_submit":
        err_p = data_root / "results" / "reviews" / judge / (jid + ".stderr.txt")
        try:
            err = err_p.read_text(encoding="utf-8", errors="replace") if err_p.exists() else ""
        except Exception:
            err = ""
        if '"phase": "pre_submit"' in err or '"phase":"pre_submit"' in err or meta.get("phase") == "pre_submit":
            return ("retry_presubmit", "confirmed pre-submit w/ local evidence")
    return ("skip_ambiguous", f"status={meta.get('status')} phase={meta.get('phase')}")


def next_attempt_index(prefix: Path) -> int:
    i = 1
    while Path(str(prefix) + f".attempt{i:02d}.meta.json").exists():
        i += 1
    return i


def build_queue(data_root: Path):
    """Return (tasks, skipped). Each task: dict with stable unique prefix."""
    manifest = json.loads((data_root / "jobs" / "manifest.json").read_text(encoding="utf-8"))
    plan = json.loads((data_root / "jobs" / "repetition_plan.json").read_text(encoding="utf-8"))
    rev_manifest = json.loads((data_root / "jobs" / "reviews" / "review_manifest.json").read_text(encoding="utf-8"))
    prompt_by_job_model = {j["job_id"]: j["model_prompt_paths"] for j in manifest["jobs"]}
    hash_by_job = {j["job_id"]: j["input_sha256"] for j in manifest["jobs"]}

    tasks, skipped = [], []

    # 1) base r01-r05 non-success slots (dynamic classify; expect 9 retry + 5 ambiguous skip)
    for j in plan["jobs"]:
        jid = j["job_id"]
        for rnd in ("r01", "r02", "r03", "r04", "r05"):
            for model in ("gpt6w", "gpt56w"):
                dec, why = classify_trial_slot(data_root, model, jid, rnd)
                slot = f"{model}/{jid}/{rnd}"
                if dec == "preserve":
                    skipped.append((slot, "preserve_success"))
                elif dec == "skip_ambiguous":
                    skipped.append((slot, f"skip_ambiguous ({why})"))
                elif dec == "retry_presubmit":
                    tasks.append({"kind": "trial", "model": model, "job_id": jid, "round": rnd,
                                  "mode": "retry_presubmit",
                                  "prompt_rel": prompt_by_job_model[jid][model],
                                  "prompt_hash": hash_by_job[jid]})
                # "new" cannot happen for base (metas exist); if it does, still queue it
                elif dec == "new":
                    tasks.append({"kind": "trial", "model": model, "job_id": jid, "round": rnd,
                                  "mode": "new",
                                  "prompt_rel": prompt_by_job_model[jid][model],
                                  "prompt_hash": hash_by_job[jid]})

    # 2) review manifest non-success (manifest order; expect 15 retry + 4 ambiguous skip)
    for row in rev_manifest["jobs"]:
        jid, judge = row["job_id"], row["judge_model"]
        dec, why = classify_review_slot(data_root, judge, jid)
        slot = f"review/{judge}/{jid}"
        if dec == "preserve":
            skipped.append((slot, "preserve_success"))
        elif dec == "skip_ambiguous":
            skipped.append((slot, f"skip_ambiguous ({why})"))
        else:  # retry_presubmit or new
            tasks.append({"kind": "review", "model": judge, "job_id": jid,
                          "round": row.get("kind", "?"), "mode": dec,
                          "prompt_rel": row["prompt_file"],
                          "prompt_hash": row["prompt_sha256"]})

    # 3) ext r06-r08 for C02/C11/C23 (missing -> new; pre-submit -> retry; expect 9)
    for jid in ("C02", "C11", "C23"):
        for rnd in ("r06", "r07", "r08"):
            for model in ("gpt6w", "gpt56w"):  # interleave: round-major, both models
                dec, why = classify_trial_slot(data_root, model, jid, rnd)
                slot = f"{model}/{jid}/{rnd}"
                if dec == "preserve":
                    skipped.append((slot, "preserve_success"))
                elif dec == "skip_ambiguous":
                    skipped.append((slot, f"skip_ambiguous ({why})"))
                else:
                    tasks.append({"kind": "trial", "model": model, "job_id": jid, "round": rnd,
                                  "mode": dec,
                                  "prompt_rel": prompt_by_job_model[jid][model],
                                  "prompt_hash": hash_by_job[jid]})

    # stable task ids / prefixes (unique by construction)
    for t in tasks:
        if t["kind"] == "trial":
            t["task_id"] = f"{t['model']}:{t['job_id']}:{t['round']}:{t['mode']}"
            t["prefix_rel"] = f"results/trials/{t['model']}/{t['job_id']}/{t['round']}"
        else:
            t["task_id"] = f"review:{t['model']}:{t['job_id']}:{t['mode']}"
            t["prefix_rel"] = f"results/reviews/{t['model']}/{t['job_id']}"
    seen = set()
    for t in tasks:
        assert t["prefix_rel"] not in seen, f"duplicate prefix {t['prefix_rel']}"
        seen.add(t["prefix_rel"])
    return tasks, skipped


# ---------------- worker -----------------------------------------------------

def looks_like_protection(text: str) -> str | None:
    low = (text or "").lower()
    for tok in PROTECT_TOKENS:
        if tok in low:
            return tok
    return None


def run_one(task: dict, data_root: Path, rep: Reporter, state: dict, timeout: int, worker_no: int):
    prefix = data_root / task["prefix_rel"]
    prompt_abs = (data_root / task["prompt_rel"]).resolve()
    rep.event("launched", task=task["task_id"], prefix=str(prefix),
              model=MODEL[task["model"]], mode=task["mode"], worker=worker_no)
    data = prompt_abs.read_bytes()  # prompt path treated as data
    actual = sha(data)
    if actual != task["prompt_hash"]:
        rep.event("failed", task=task["task_id"], reason="prompt_hash_mismatch",
                  expected=task["prompt_hash"][:12], actual=actual[:12])
        return ("hash_mismatch", task)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        rep.event("failed", task=task["task_id"], reason=f"prompt_not_utf8: {e}")
        return ("bad_prompt", task)
    if len(text) > 65536:
        rep.event("failed", task=task["task_id"], reason="prompt_over_65536_chars")
        return ("prompt_too_long", task)

    if task["mode"] == "retry_presubmit":
        idx = next_attempt_index(prefix)
        for suffix in (".meta.json", ".stderr.txt", ".raw.json"):
            src = Path(str(prefix) + suffix)
            if src.exists():
                dst = Path(str(prefix) + f".attempt{idx:02d}" + suffix)
                if dst.exists():
                    rep.event("failed", task=task["task_id"],
                              reason=f"archive_target_exists: {dst.name}")
                    return ("archive_collision", task)
                src.rename(dst)
        rep.event("archived", task=task["task_id"], attempt=f"{idx:02d}")

    # Direct interpreter spawn: argv-equivalent of
    #   gpt2 ask --file ABS --model EXACT --json
    # bypassing gpt2.cmd/cmd.exe (visible-terminal root cause, r01).
    # NOTE(2026-10-10 r01 postmortem #2): do NOT pass -I here. gpt2_cli.py does
    # `import headless_client` (sibling in tools/chatgpt_web/), which relies on
    # the script directory on sys.path; -I strips it and every call fails
    # locally with ModuleNotFoundError (rc=1, empty outputs — exactly the r01
    # signature; nothing was submitted). cwd=SAFECHAIN_ROOT keeps module
    # resolution identical to the gpt2.cmd entry.
    # NOTE: --timeout-seconds here is the LOCAL wait budget only. On expiry the
    # child is NEVER killed (in-flight turns must not be disturbed); the slot is
    # recorded as slow_worker_unknown (ambiguous) and the queue drains.
    cmd = [str(GPT2_PY), str(GPT2_CLI), "ask",
           "--file", str(prompt_abs), "--model", MODEL[task["model"]], "--json"]
    start = time.monotonic()
    utc = utcnow()
    ret = None
    soft_timeout = False
    stdout, stderr, error = "", "", None
    spawned = False
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                cwd=str(SAFECHAIN_ROOT),
                                encoding="utf-8", errors="replace", **hidden_popen_kwargs())
        spawned = True
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            ret = proc.returncode
        except subprocess.TimeoutExpired:
            # Soft timeout: NEVER kill. Leave the child alone; record the slot
            # as unknown/ambiguous and let the queue drain. Recovery of a
            # possibly-submitted turn is the orchestrator's read-only job.
            soft_timeout = True
            error = ("SOFT_TIMEOUT_UNKNOWN: local wait budget elapsed; child NOT killed, "
                     "NOT resubmitted; treat as ambiguous, no retry")
            # Non-blocking drain of whatever output exists so far (no kill).
            try:
                stdout, stderr = proc.communicate(timeout=5)
                ret = proc.returncode
                error += f" | late_exit={ret}"
            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
                error += " | child_still_running_detached"
    except Exception as e:
        if not spawned:
            error = f"spawn_failed_pre_submit: {e}"
        else:
            error = f"worker_error_after_spawn_ambiguous: {e}"
    elapsed = round(time.monotonic() - start, 3)
    pre_submit_spawn_failure = error is not None and error.startswith("spawn_failed_pre_submit")

    output, wrapper, server_meta, response = None, {}, {}, ""
    if isinstance(stdout, str) and stdout.strip():
        try:
            output = json.loads(stdout.strip().lstrip("\ufeff"))
            if isinstance(output, dict):
                wrapper = output
                server_meta = output.get("metadata") or {}
                response = output.get("response") or ""
        except (ValueError, TypeError):
            pass
    route = server_meta.get("model")
    effort = server_meta.get("thinking_effort")
    success = (error is None and ret == 0 and wrapper.get("completed") is True
               and isinstance(response, str) and len(response.strip()) > 0
               and route == MODEL[task["model"]] and effort == "max")
    phase = wrapper.get("phase")
    for blob in (stderr or "", stdout or ""):
        if '"phase": "pre_submit"' in blob or '"phase":"pre_submit"' in blob:
            phase = "pre_submit"
    # Classification:
    # - spawn_failed_pre_submit (Popen itself raised: nothing was submitted) ->
    #   confirmed_pre_submit_failure, eligible for ONE explicit retry later.
    # - everything else without verified success -> failure_or_ambiguous,
    #   NEVER auto-retried, NEVER promoted to pre-submit on guesswork
    #   (r01 lesson: ret=1 + empty stdout/stderr is NOT proof of pre-submit).
    status = ("success" if success
              else ("confirmed_pre_submit_failure" if pre_submit_spawn_failure
                    else "failure_or_ambiguous"))
    if pre_submit_spawn_failure:
        phase = "pre_submit"
    job_dir = server_meta.get("job_directory")
    markers = []
    if isinstance(job_dir, str) and job_dir:
        jd = Path(job_dir)
        for m in ("windows-browser-closed.json", "handoff-public.json",
                  "initializer-aborted.json", "submit-authorized.json"):
            try:
                if (jd / m).exists():
                    markers.append(m)
            except OSError:
                pass
    meta = {"id": task["task_id"], "kind": task["kind"], "job": task["job_id"],
            "model_requested": MODEL[task["model"]], "model_reported": route,
            "thinking_effort": effort, "prompt_sha256": actual,
            "response_sha256_observed": sha(response.encode("utf-8")) if response else None,
            "response_sha256_reported": server_meta.get("response_sha256"),
            "completed": wrapper.get("completed"), "exit_code": ret,
            "elapsed_seconds": elapsed, "utc_start": utc, "utc_end": utcnow(),
            "status": status, "phase": phase, "error": error,
            "new_session": True, "runner": "gpt2 ask --file --model --json",
            "no_automatic_retry": True, "response_chars": len(response),
            "scheduler": "baseline_parallel_control_20261010/pipeline.py",
            "scheduler_mode": task["mode"], "worker": worker_no,
            "provider_job_directory": job_dir, "init_markers_observed": markers}
    try:
        save_atomic(Path(str(prefix) + ".meta.json"), compact(meta))
        save_atomic(Path(str(prefix) + ".stderr.txt"), stderr or "")
        save_atomic(Path(str(prefix) + ".raw.json"), stdout or "")
        if success:
            save_atomic(Path(str(prefix) + ".txt"), response)
    except FileExistsError as e:
        rep.event("failed", task=task["task_id"], reason=f"evidence_collision: {e}")
        return ("collision", task)

    prot = looks_like_protection(stderr) or looks_like_protection(stdout)
    if prot and not success:
        with state["lock"]:
            state["protection_hit"] = prot
        rep.event("protection_signal", task=task["task_id"], token=prot,
                  note="pausing NEW submissions; draining in-flight; no account/credential change")
    if success:
        rep.event("result", task=task["task_id"], status="success",
                  elapsed=elapsed, response_chars=len(response),
                  job_directory=job_dir, init_markers=markers)
    else:
        rep.event("result", task=task["task_id"], status=status,
                  elapsed=elapsed, phase=phase, error=error,
                  job_directory=job_dir, init_markers=markers,
                  note="per-task failure only; queue continues; no auto retry")
    return (status, task)


# ---------------- phase 2: mechanical summaries (frozen scripts) --------------

def _snapshot_tree(root: Path, rels):
    """Read-only content snapshot of files phase2 is allowed to (re)generate."""
    snap = {}
    for rel in rels:
        p = root / rel
        if p.exists() and p.is_file():
            snap[rel] = sha(p.read_bytes())
        else:
            snap[rel] = None
    return snap


def run_phase2(data_root: Path, rep: Reporter):
    rep.event("phase2_started", note="mechanical summaries via frozen scripts; additive-only")
    # Snapshot review/manif est/report outputs BEFORE running builders, so any
    # overwrite of existing different bytes is detected and reported.
    # NOTE: trusted scheduler cwd is HERE (own dir), never data_root; frozen
    # inputs are passed by absolute path as data. The frozen scripts resolve
    # their own ROOT from __file__, so cwd does not change their behavior —
    # but we keep cwd trusted regardless (untrusted-dir rule).
    watch = ["jobs/reviews/review_manifest.json",
             "private/review_mapping_DO_NOT_SHOW_JUDGES.json",
             "reports/judge_build_summary.json",
             "reports/repeated_stability_summary.json",
             "reports/review_and_extension_summary.json"]
    before = _snapshot_tree(data_root, watch)
    review_prompts_before = _snapshot_tree(
        data_root, [str(p.relative_to(data_root)).replace("\\", "/")
                    for p in (data_root / "jobs" / "reviews").rglob("*.txt")])
    out = {}
    for script in ("scripts/analyze_repeats.py", "scripts/build_repeat_judges.py",
                   "scripts/summarize_reviews.py"):
        sp = data_root / script
        log = ""
        try:
            r = subprocess.run([sys.executable, "-I", str(sp)], cwd=str(HERE),
                               capture_output=True, encoding="utf-8", errors="replace",
                               timeout=600, **hidden_popen_kwargs())
            log = (r.stdout or "")[-2000:] + "\n---STDERR---\n" + (r.stderr or "")[-2000:]
            out[script] = {"rc": r.returncode, "tail": log}
        except Exception as e:
            out[script] = {"rc": None, "error": str(e)}
        rep.event("phase2_step", script=script, rc=out[script].get("rc"),
                  error=out[script].get("error"))
    after = _snapshot_tree(data_root, watch)
    review_prompts_after = _snapshot_tree(
        data_root, [str(p.relative_to(data_root)).replace("\\", "/")
                    for p in (data_root / "jobs" / "reviews").rglob("*.txt")])
    overwritten = [k for k in watch
                   if before[k] is not None and after[k] != before[k]]
    prompt_overwritten = [k for k in review_prompts_after
                          if k in review_prompts_before
                          and review_prompts_before[k] is not None
                          and review_prompts_after[k] != review_prompts_before[k]]
    version_note = None
    if overwritten or prompt_overwritten:
        version_note = ("phase2 builders rewrote existing files; "
                        "scheduler is additive-only and did not restore them; "
                        "orchestrator must diff before trusting summaries")
        rep.event("phase2_overwrite_detected", files=overwritten,
                  prompts=prompt_overwritten, note=version_note)
    added = [k for k in watch if before[k] is None and after[k] is not None]
    # newly-available r08 review jobs (missing metas only; never overwrite)
    new_reviews = []
    try:
        rev_manifest = json.loads((data_root / "jobs" / "reviews" / "review_manifest.json").read_text(encoding="utf-8"))
        for row in rev_manifest["jobs"]:
            mp = data_root / "results" / "reviews" / row["judge_model"] / (row["job_id"] + ".meta.json")
            if not mp.exists() and row["job_id"] not in {t.get("job_id") for t in new_reviews}:
                new_reviews.append(row)
    except Exception as e:
        rep.event("phase2_step", script="scan_new_r08_reviews", error=str(e))
    (RUN_DIR / "phase2_summary.json").write_text(
        compact({"utc": utcnow(), "steps": out,
                 "files_added": added, "files_overwritten": overwritten,
                 "prompts_overwritten": prompt_overwritten,
                 "version_note": version_note,
                 "new_r08_review_jobs_missing": [r["job_id"] for r in new_reviews]}), encoding="utf-8")
    rep.event("phase2_done", new_r08_review_missing=len(new_reviews))
    return new_reviews


# ---------------- main --------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--max-inflight", type=int, default=8)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--timeout-seconds", type=int, default=1200)
    ap.add_argument("--no-phase2", action="store_true")
    a = ap.parse_args()
    data_root = Path(a.data_root).resolve()
    if not (data_root / "jobs" / "manifest.json").exists():
        print(f"bad data-root: {data_root}", flush=True)
        return 1

    if a.selftest:
        return selftest(data_root, a.max_inflight)

    tasks, skipped = build_queue(data_root)
    n_retry = sum(1 for t in tasks if t["mode"] == "retry_presubmit")
    n_new = sum(1 for t in tasks if t["mode"] == "new")
    print(f"QUEUE total={len(tasks)} retry_presubmit={n_retry} new={n_new} "
          f"skipped={len(skipped)} (success-preserved or ambiguous-excluded)", flush=True)
    for t in tasks:
        print(f"  PLAN {t['task_id']} {t['prompt_hash'][:12]}", flush=True)
    if a.dry_run:
        print("DRY-RUN: no submissions, no writes.", flush=True)
        return 0

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rep = Reporter(RUN_DIR)
    run_id = f"pipeline-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    state = {"lock": threading.Lock(), "protection_hit": None,
             "inflight": 0, "peak": 0, "launched": 0,
             "results": {"success": 0, "confirmed_pre_submit_failure": 0,
                         "failure_or_ambiguous": 0, "other": 0}}
    rep.set_status(run_id=run_id, phase="running-queue",
                   total_queued=len(tasks), skipped=len(skipped),
                   launched=0, inflight=0, inflight_peak=0,
                   max_inflight=a.max_inflight, protection_paused=False,
                   init_lock={"path": str(INIT_LOCK_PATH),
                              "exists": INIT_LOCK_PATH.exists(),
                              "kind": "HeadlessNativeGPT2AgentProvider InitializerLock (OS-global file lock, 600s timeout)",
                              "note": "browser-init serialization is native; 8-wide window covers HTTP-answer waiting, NOT 8 lock waiters"},
                   data_root=str(data_root), gpt2=GPT2)
    rep.event("run_started", run_id=run_id, max_inflight=a.max_inflight,
              queue_total=len(tasks), retry_presubmit=n_retry, new=n_new,
              skipped=len(skipped),
              init_lock_exists=INIT_LOCK_PATH.exists(),
              lock_module="gpt2agent-safechain/tools/chatgpt_web/headless_initializer_lock.py",
              lock_release_before_http_wait="windows_native_provider_runner.py:87 lock.close() then worker.wait(); "
                                            "linux_native_provider_runner.py:412-415 initializer_lock.close() then worker.wait()")
    for s, why in skipped:
        rep.event("queued_skip", slot=s, reason=why)
    for t in tasks:
        rep.event("queued", task=t["task_id"], mode=t["mode"])

    claimed = set()
    claim_lock = threading.Lock()
    stop = threading.Event()
    exit_code, term_status = 0, "finished"

    def protection_active():
        with state["lock"]:
            hit = state["protection_hit"]
        return hit or PAUSE_FLAG.exists() or STOP_FLAG.exists()

    def worker_fn(t, worker_no):
        nonlocal exit_code, term_status
        # Rolling-window gate: re-check protection immediately BEFORE spawning.
        # Queued futures that lose the race exit without submitting anything.
        if protection_active():
            rep.event("suppressed_before_spawn", task=t["task_id"], worker=worker_no,
                      token=state["protection_hit"],
                      note="protection/operator hold seen at execution time; nothing submitted")
            with state["lock"]:
                state["results"]["other"] += 1
            return
        with claim_lock:
            assert t["prefix_rel"] not in claimed, f"double-claim {t['prefix_rel']}"
            claimed.add(t["prefix_rel"])
        with state["lock"]:
            state["inflight"] += 1
            state["peak"] = max(state["peak"], state["inflight"])
            state["launched"] += 1
            peak, inf, launched = state["peak"], state["inflight"], state["launched"]
        rep.set_status(launched=launched, inflight=inf, inflight_peak=peak)
        try:
            st, _ = run_one(t, data_root, rep, state, a.timeout_seconds, worker_no)
            with state["lock"]:
                state["results"]["success" if st == "success" else
                                  ("confirmed_pre_submit_failure" if st == "confirmed_pre_submit_failure"
                                   else ("failure_or_ambiguous" if st == "failure_or_ambiguous" else "other"))] += 1
        finally:
            with state["lock"]:
                state["inflight"] -= 1
                inf = state["inflight"]
            rep.set_status(inflight=inf, inflight_peak=state["peak"],
                           succeeded=state["results"]["success"],
                           failed=dict(state["results"]))

    try:
        with ThreadPoolExecutor(max_workers=a.max_inflight,
                                thread_name_prefix="gpt2w") as pool:
            # Rolling window: at most max_inflight live futures; refill only as
            # workers complete. Protection is re-checked at BOTH submit time and
            # worker execution time, so a post-submit rate-limit can no longer be
            # followed by a storm of still-queued submissions.
            futs = set()
            pending = list(tasks)
            worker_no = 0
            submitting = True
            while pending or futs:
                if submitting and (protection_active()):
                    rep.event("protection_paused" if state["protection_hit"] else "operator_hold",
                              token=state["protection_hit"],
                              note="no NEW submissions; draining in-flight")
                    rep.set_status(protection_paused=True, phase="draining")
                    submitting = False
                while submitting and pending and len(futs) < a.max_inflight:
                    worker_no += 1
                    futs.add(pool.submit(worker_fn, pending.pop(0), worker_no))
                    time.sleep(0.2)
                if not futs:
                    break
                done, futs = _wait_any(futs)
                for f in done:
                    try:
                        f.result()
                    except AssertionError as e:
                        rep.event("fatal", reason=f"claim_violation: {e}")
                        term_status, exit_code = "fatal", 1
                    except Exception as e:  # noqa: BLE001 - isolate per-task crash
                        rep.event("failed", reason=f"worker_crash: {e}")
                if not submitting and not pending:
                    # drain remaining in-flight without new submissions
                    continue
        with state["lock"]:
            paused = state["protection_hit"]
        if paused:
            term_status, exit_code = "protection_paused_drained", 3
        elif STOP_FLAG.exists():
            term_status, exit_code = "operator_stopped_drained", 3
        elif state["results"]["failure_or_ambiguous"] or state["results"]["other"] \
                or state["results"]["confirmed_pre_submit_failure"]:
            exit_code = 2  # queue drained; some tasks need attention; NOT a global STOP
        # phase 2 (mechanical summaries + newly-missing r08 review scan)
        new_reviews = []
        if not a.no_phase2 and term_status == "finished":
            rep.set_status(phase="phase2-summaries")
            try:
                new_reviews = run_phase2(data_root, rep)
            except Exception as e:  # noqa: BLE001 - phase2 never fails the run
                rep.event("phase2_step", script="phase2_runner", error=str(e))
            pending = {"utc": utcnow(),
                       "note": "r12/music-review need human+web-GPT judgement; scheduler only reports, never composes music",
                       "new_r08_review_missing": [r["job_id"] for r in new_reviews],
                       "ab_trigger_status": "pending: A/B extension triggers require review of phase2 summaries by orchestrator"}
            (RUN_DIR / "pending_decisions.json").write_text(compact(pending), encoding="utf-8")
    except Exception as e:  # noqa: BLE001 - always land the terminal marker
        term_status, exit_code = f"fatal: {e}", 1
        try:
            rep.event("fatal", reason=str(e))
        except Exception:
            pass

    remaining = []
    for t in tasks:
        mp = data_root / t["prefix_rel"]
        if not Path(str(mp) + ".meta.json").exists():
            remaining.append(t["task_id"])
    terminal = {"utc": utcnow(), "run_id": run_id, "exit": exit_code,
                # QUEUE_FAILED (exit 2) = queue drained with per-task failures
                # needing recovery analysis; it is NOT user-task "finished".
                "status": ("QUEUE_FAILED" if exit_code == 2 else term_status),
                "counts": {"queued": len(tasks), "launched": state["launched"],
                           "results": dict(state["results"]), "skipped": len(skipped)},
                "inflight_peak": state["peak"], "max_inflight": a.max_inflight,
                "remaining_without_meta": remaining,
                "paths": {"status": str(RUN_DIR / "status.json"),
                          "events": str(RUN_DIR / "events.jsonl"),
                          "run_handle": str(RUN_DIR / "run_handle.json"),
                          "terminal": str(RUN_DIR / "pipeline_terminal.json")},
                "data_root": str(data_root)}
    (RUN_DIR / "pipeline_terminal.json").write_text(compact(terminal), encoding="utf-8")
    rep.event("finished" if exit_code == 0 else "fatal", status=term_status,
              exit=exit_code, remaining=len(remaining))
    rep.set_status(phase="terminal", terminal=term_status)
    print(f"TERMINAL {term_status} exit={exit_code} remaining={len(remaining)} "
          f"peak={state['peak']} results={dict(state['results'])}", flush=True)
    return exit_code


# ---------------- offline self-test (NO external submission) -----------------

def selftest(data_root: Path, max_inflight: int):
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    logp = RUN_DIR / "selftest.log"
    lines = []

    def log(s):
        lines.append(s)
        print(s, flush=True)

    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        mark = "PASS" if cond else "FAIL"
        if not cond:
            ok = False
        log(f"[{mark}] {name} {detail}")

    # 1) queue builds; frozen hashes verify against on-disk bytes (read-only)
    # NOTE: counts are state-dependent (r01 wrote 33 new metas). Assert
    # invariants instead of frozen numbers: retry⊆confirmed-pre-submit,
    # new⊆missing-meta, no success/ambiguous queued, prefixes unique.
    tasks, skipped = build_queue(data_root)
    check("queue_builds", len(tasks) > 0, f"tasks={len(tasks)} skipped={len(skipped)}")
    n_retry = sum(1 for t in tasks if t["mode"] == "retry_presubmit")
    n_new = sum(1 for t in tasks if t["mode"] == "new")
    inv_ok = True
    for t in tasks:
        mp = data_root / t["prefix_rel"]
        m = Path(str(mp) + ".meta.json")
        x = Path(str(mp) + ".txt")
        if t["mode"] == "new":
            if m.exists():
                inv_ok = False
                log(f"  invariant: new-but-meta-exists: {t['task_id']}")
                break
        else:
            try:
                meta = json.loads(m.read_text(encoding="utf-8"))
            except Exception as e:
                inv_ok = False
                log(f"  invariant: retry-unreadable-meta: {t['task_id']}: {e}")
                break
            if not (meta.get("status") == "confirmed_pre_submit_failure"
                    and meta.get("phase") == "pre_submit" and not x.exists()):
                inv_ok = False
                log(f"  invariant: retry-not-confirmed-presubmit: {t['task_id']}")
                break
    check("queue_invariants", inv_ok,
          f"tasks={len(tasks)} retry={n_retry} new={n_new} skipped={len(skipped)}")
    hash_ok = True
    for t in tasks:
        p = (data_root / t["prompt_rel"]).resolve()
        if not p.exists() or sha(p.read_bytes()) != t["prompt_hash"]:
            hash_ok = False
            log(f"  hash mismatch: {t['task_id']}")
            break
        if len(p.read_text(encoding="utf-8")) > 65536:
            hash_ok = False
            log(f"  prompt too long: {t['task_id']}")
            break
    check("freeze_hash_all_tasks", hash_ok)

    # 2) no-overwrite: every target meta either absent (new) or non-success (retry);
    #    ambiguous/success never queued
    no_overwrite_ok = True
    for t in tasks:
        mp = data_root / t["prefix_rel"]
        m = Path(str(mp) + ".meta.json")
        x = Path(str(mp) + ".txt")
        if t["mode"] == "new" and m.exists():
            no_overwrite_ok = False
            log(f"  new-but-meta-exists: {t['task_id']}")
            break
        if t["mode"] == "retry_presubmit":
            if not m.exists() or x.exists():
                no_overwrite_ok = False
                log(f"  retry-without-proper-state: {t['task_id']}")
                break
    amb_queued = [t["task_id"] for t in tasks
                  if t["mode"] not in ("new", "retry_presubmit")]
    check("no_overwrite_no_ambiguous_retry", no_overwrite_ok and not amb_queued,
          f"ambiguous_queued={amb_queued}")

    # 3) one prefix <-> one worker (mock pool, no gpt2): peak<=window, unique claims
    peak = [0]
    cur = [0]
    clock = threading.Lock()
    seen = set()

    def fake(tid):
        with clock:
            assert tid not in seen, f"double claim {tid}"
            seen.add(tid)
            cur[0] += 1
            peak[0] = max(peak[0], cur[0])
        time.sleep(0.05)
        with clock:
            cur[0] -= 1

    mock_ids = [f"mock:{i:02d}" for i in range(24)]
    with ThreadPoolExecutor(max_workers=max_inflight) as pool:
        list(pool.map(fake, mock_ids))
    check("mock_window_and_unique_claim",
          peak[0] <= max_inflight and len(seen) == len(mock_ids),
          f"peak={peak[0]} window={max_inflight} unique={len(seen)}/{len(mock_ids)}")

    # 4) hidden subprocess flags present
    kw = hidden_popen_kwargs()
    if os.name == "nt":
        has = (kw.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0)) != 0
        has = has and kw.get("startupinfo") is not None
    else:
        has = kw.get("start_new_session") is True
    check("hidden_subprocess_flags", has, f"keys={sorted(kw)}")

    # 5) save_atomic refuses overwrite
    probe = RUN_DIR / "_selftest_probe.txt"
    try:
        if probe.exists():
            probe.unlink()
        save_atomic(probe, "a")
        try:
            save_atomic(probe, "b")
            check("save_atomic_no_overwrite", False, "second write did not raise")
        except FileExistsError:
            check("save_atomic_no_overwrite", True)
    finally:
        try:
            probe.unlink()
        except OSError:
            pass

    # 6) protection token scan
    check("protection_scan",
          looks_like_protection('{"error": "HTTP 429 too many requests"}') == "429"
          and looks_like_protection("all clear") is None)

    # 7) native init lock file present (serialization proof target)
    check("native_init_lock_present", INIT_LOCK_PATH.exists(), str(INIT_LOCK_PATH))

    # Static guards: scan code lines only. A line counts as code if, after
    # stripping leading whitespace, it is not a comment, docstring fence or
    # bullet prose, AND it contains an assignment/call/class/def/import token.
    # (Pure prose lines like `bypassing gpt2.cmd` must not false-positive.)
    import re as _re
    _codelines = []
    for _l in Path(__file__).read_text(encoding="utf-8").split("def selftest(")[0].splitlines():
        _s = _l.strip()
        if not _s or _s.startswith(("#", '"""', "'''", "*", "-")):
            continue
        if not _re.search(r"[=({\[]|def |class |import |return |raise |await |\+=|-=", _l):
            continue
        _codelines.append(_l)
    body = "\n".join(_codelines)
    norm = body.replace('"', "'")
    check("cmd_shape_no_resume",
          ("resume" not in norm
           and "ask" in norm and "--file" in norm and "--model" in norm and "--json" in norm),
          "only `ask --file --model --json`, no resume/fallback path")
    check("no_account_switching_code",
          "CODEX_HOME" not in body and "cookie_scope" not in body.lower()
          and "cookie_snapshot" not in body.lower()
          and "setx" not in body.lower())

    # 9) r01 regression guards: no proc.kill, no DETACHED_PROCESS, direct
    #    interpreter spawn (no .cmd), rolling-window submit, QUEUE_FAILED name
    check("no_proc_kill", "proc.kill()" not in body and ".kill()" not in body,
          "soft timeout must never kill in-flight children")
    check("no_detached_process", "DETACHED_PROCESS" not in body,
          "DETACHED_PROCESS nullifies CREATE_NO_WINDOW on Windows")
    check("direct_interpreter_spawn",
          "gpt2_cli" in body and "GPT2_PY" in body,
          "bypass cmd.exe visible-terminal root cause; provider files untouched")
    check("rolling_window_submit", "_wait_any" in body and "FIRST_COMPLETED" in body,
          "refill only on completion, not bulk submit")
    check("worker_pre_spawn_gate", "suppressed_before_spawn" in body,
          "execution-time protection re-check before any submission")
    check("queue_failed_terminal_name", "QUEUE_FAILED" in body,
          "exit 2 must not be labeled user-task finished")

    log(f"SELFTEST {'OK' if ok else 'FAILED'} tasks={len(tasks)} "
        f"retry={n_retry} new={n_new} skipped={len(skipped)}")
    logp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
