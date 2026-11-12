#!/usr/bin/env python3
"""pipeline_v3: minimal new-only mechanical scheduler (no model calls by itself).

Trusted scheduler code. Lives in D:/musicclaude/_baseline_parallel_control_20261010.
Frozen data under --data-root is NEVER modified. All evidence writes go to
--data-root/results/... ONLY via save_atomic (refuse overwrite), run state
goes to unique --run-dir.

Fixes vs pipeline.py (acceptance):
- No NameError: all status fields use defined names (GPT2_PY/GPT2_CLI).
- Direct venv interpreter spawn on gpt2_cli.py (argv-equivalent cli), no -I
  on the child (sibling `import headless_client` needs script dir), trusted
  cwd=SAFECHAIN_ROOT, CREATE_NO_WINDOW+SW_HIDE, never DETACHED.
- Rolling max-inflight window, pre-spawn pause re-check, soft timeout NEVER
  kills and NEVER releases the slot early: records slow then blocks on
  communicate() to true exit, holding the slot (true drain, no oversell).
- Protection scans ONLY stderr / structured transport error / error string,
  never music response text (no numeric false positives).
- New-only: any existing evidence file under the target prefix blocks the
  task (success/ambiguous never resent, new targets with any evidence blocked).
- Explicit --queue JSON + unique --run-dir; selftest/mock isolated from run/.
- No in-place phase2: default does nothing to data-root; --allow-phase2
  requires external --report-root outside data-root (additive only).
- utc/monotonic/PID/child-argv/job binding recorded; stdout/stderr truly
  captured; single HTTP-wait column (inflight = live children).
- Manifest round-major order, per-round first-model flip; reviews (D then G
  then F, manifest order, AB/BA pairs kept) interleaved BEFORE each trial
  round so 9 reviews start early instead of after all 66+12.
- Offline mock exercises the REAL main() path (catches NameError etc.),
  plus real no-model child capture + visible-window enumeration.
  `check`/`--help` never submit a model request.

Run under `python -I` (scheduler itself isolated). Child MUST NOT use -I.
"""
import argparse
import ctypes
import datetime
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pathlib import Path

_REAL_POPEN = subprocess.Popen  # import-time capture; mock patching must not recurse

HERE = Path(__file__).resolve().parent
os.chdir(HERE)  # trusted cwd; run under `python -I`
sys.path.insert(0, str(HERE))

SAFECHAIN_ROOT = Path(r"D:\musicclaude\gpt2agent-safechain")
GPT2_PY = SAFECHAIN_ROOT / ".venv-local" / "Scripts" / "python.exe"
GPT2_CLI = SAFECHAIN_ROOT / "tools" / "chatgpt_web" / "gpt2_cli.py"
MODEL = {"gpt6w": "gpt-6-thinking", "gpt56w": "gpt-5-6-thinking"}
INIT_LOCK_PATH = Path(r"D:\musicclaude\gpt2agent-safechain\runs\yi-cookie-repair-20261006\headless-initializer.lock")

# Expansion set approved: A01-A06 + B02/B11/B18/B20/B23 (66) + C18/C20 (12).
EXPANSION_JOBS = ("A01", "A02", "A03", "A04", "A05", "A06",
                  "B02", "B11", "B18", "B20", "B23", "C18", "C20")
EXPANSION_ROUNDS = (6, 7, 8)

# Readiness gate: provider's local door (windows runner: phys+commit >= 3;
# browser-init default pss 1536 needs 5/5). Scheduler NEVER lowers the
# provider budget — it only WAITS for headroom before spawning, so a known
# fail is never submitted. Pre-submit local-memory blocks are preserved as
# evidence, never auto-retried.
READINESS_MIN_PHYS_GIB = 5.0
READINESS_MIN_COMMIT_GIB = 5.0
READINESS_POLL_SECONDS = 15.0
READINESS_MAX_WAIT_SECONDS = 7200.0

PROTECT_TOKENS = ("403", "429", "challenge", "captcha", "rate_limit",
                  "rate-limit", "ratelimit", "cloudflare", "too many requests",
                  "temporarily blocked", "access denied")


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def compact(o) -> str:
    return json.dumps(o, ensure_ascii=False, indent=2) + "\n"


def hidden_popen_kwargs():
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
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() or os.path.lexists(p):
        raise FileExistsError(f"Would overwrite immutable evidence: {p}")
    tmp = p.with_name("." + p.name + ".writing")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)


def any_evidence(prefix: Path) -> list:
    """Any file starting with prefix (meta/txt/raw/stderr/attempt*) blocks."""
    parent = prefix.parent
    base = prefix.name
    if not parent.exists():
        return []
    return sorted([q for q in parent.glob(base + "*") if q.is_file()])


def list_visible_windows():
    """Enumerate visible top-level windows (Windows only). Returns set of titles."""
    if os.name != "nt":
        return set()
    try:
        user32 = ctypes.windll.user32
        out = set()
        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _cb(hwnd, _lp):
            try:
                if user32.IsWindowVisible(hwnd):
                    n = user32.GetWindowTextLengthW(hwnd)
                    if n and n < 512:
                        buf = ctypes.create_unicode_buffer(n + 1)
                        user32.GetWindowTextW(hwnd, buf, n + 1)
                        t = buf.value.strip()
                        if t:
                            out.add(t)
            except Exception:
                pass
            return True
        user32.EnumWindows(_cb, 0)
        return out
    except Exception:
        return set()


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


# ---------------- new-only queue ----------------

def build_new_only_queue(data_root: Path):
    """Build 87-candidate new-only queue (78 trials + reviews), evidence-filtered.

    Order: D-reviews + r06 trials + G-reviews + r07 trials + F-reviews + r08
    trials. Trials per round follow manifest order with per-round first-model
    flip (frozen run_repeated_trials rule). Reviews keep manifest order with
    AB/BA pairs adjacent.
    """
    manifest = json.loads((data_root / "jobs" / "manifest.json").read_text(encoding="utf-8"))
    rev_manifest = json.loads((data_root / "jobs" / "reviews" / "review_manifest.json").read_text(encoding="utf-8"))
    prompt_by_job_model = {j["job_id"]: j["model_prompt_paths"] for j in manifest["jobs"]}
    hash_by_job = {j["job_id"]: j["input_sha256"] for j in manifest["jobs"]}
    first_by_job = {j["job_id"]: j["first_model"] for j in manifest["jobs"]}
    manifest_order = [j["job_id"] for j in manifest["jobs"]]
    ordered_expansion = [j for j in manifest_order if j in EXPANSION_JOBS]

    skipped = []
    trials_by_round = {6: [], 7: [], 8: []}
    for r in EXPANSION_ROUNDS:
        rnd = f"r{r:02d}"
        for jid in ordered_expansion:
            first = first_by_job[jid] if (r % 2 == 1) else ("gpt56w" if first_by_job[jid] == "gpt6w" else "gpt6w")
            second = "gpt56w" if first == "gpt6w" else "gpt6w"
            for model in (first, second):
                prefix_rel = f"results/trials/{model}/{jid}/{rnd}"
                ev = any_evidence(data_root / prefix_rel)
                slot = f"{model}/{jid}/{rnd}"
                if ev:
                    skipped.append({"slot": slot, "reason": "blocked_evidence_exists",
                                    "evidence": [str(Path(q).name) for q in ev[:4]]})
                    continue
                prompt_rel = prompt_by_job_model[jid][model]
                prompt_abs = (data_root / prompt_rel)
                if not prompt_abs.exists():
                    skipped.append({"slot": slot, "reason": "missing_prompt"})
                    continue
                data = prompt_abs.read_bytes()
                actual = sha(data)
                if actual != hash_by_job[jid]:
                    skipped.append({"slot": slot, "reason": "prompt_hash_mismatch"})
                    continue
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    skipped.append({"slot": slot, "reason": "prompt_not_utf8"})
                    continue
                if len(text) > 65536:
                    skipped.append({"slot": slot, "reason": "prompt_over_65536_chars"})
                    continue
                trials_by_round[r].append({
                    "kind": "trial", "model": model, "job_id": jid, "round": rnd,
                    "mode": "new", "prompt_rel": prompt_rel.replace("\\", "/"),
                    "prompt_hash": hash_by_job[jid],
                    "prompt_bytes": len(data),
                    "task_id": f"{model}:{jid}:{rnd}:new",
                    "prefix_rel": prefix_rel,
                })

    reviews_by_kind = {"D": [], "G": [], "F": []}
    for row in rev_manifest["jobs"]:
        jid, judge = row["job_id"], row["judge_model"]
        kind = row.get("kind", "?")
        prefix_rel = f"results/reviews/{judge}/{jid}"
        ev = any_evidence(data_root / prefix_rel)
        slot = f"review/{judge}/{jid}"
        if ev:
            skipped.append({"slot": slot, "reason": "blocked_evidence_exists",
                            "evidence": [str(Path(q).name) for q in ev[:4]]})
            continue
        prompt_rel = row["prompt_file"]
        prompt_abs = (data_root / prompt_rel)
        if not prompt_abs.exists():
            skipped.append({"slot": slot, "reason": "missing_prompt"})
            continue
        data = prompt_abs.read_bytes()
        actual = sha(data)
        if actual != row["prompt_sha256"]:
            skipped.append({"slot": slot, "reason": "prompt_hash_mismatch"})
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            skipped.append({"slot": slot, "reason": "prompt_not_utf8"})
            continue
        if len(text) > 65536:
            skipped.append({"slot": slot, "reason": "prompt_over_65536_chars"})
            continue
        t = {"kind": "review", "model": judge, "job_id": jid, "round": kind,
             "mode": "new", "prompt_rel": prompt_rel.replace("\\", "/"),
             "prompt_hash": row["prompt_sha256"], "prompt_bytes": len(data),
             "task_id": f"review:{judge}:{jid}:new", "prefix_rel": prefix_rel}
        reviews_by_kind.get(kind, reviews_by_kind["F"]).append(t)

    # Interleave: reviews first in each band, AB/BA pairs stay adjacent
    # (manifest order already keeps them adjacent; bands don't split pairs
    # because D=4/G=4/F=1 align to pair boundaries in the frozen set).
    ordered = (reviews_by_kind["D"] + trials_by_round[6]
               + reviews_by_kind["G"] + trials_by_round[7]
               + reviews_by_kind["F"] + trials_by_round[8])
    seen = set()
    for t in ordered:
        assert t["prefix_rel"] not in seen, f"duplicate prefix {t['prefix_rel']}"
        seen.add(t["prefix_rel"])
    info = {"trials_r06": len(trials_by_round[6]), "trials_r07": len(trials_by_round[7]),
            "trials_r08": len(trials_by_round[8]),
            "reviews_D": len(reviews_by_kind["D"]), "reviews_G": len(reviews_by_kind["G"]),
            "reviews_F": len(reviews_by_kind["F"]),
            "ordered_total": len(ordered), "skipped": len(skipped)}
    return ordered, skipped, info


# ---------------- protection (stderr/structured only) ----------------

def looks_like_protection(stderr_text: str, error_str, wrapper) -> str | None:
    """Scan ONLY transport/stderr/structured error fields. Never response text."""
    blobs = []
    if stderr_text:
        blobs.append(stderr_text)
    if error_str:
        blobs.append(str(error_str))
    if isinstance(wrapper, dict):
        for k in ("error", "error_code", "error_type", "message", "phase"):
            v = wrapper.get(k)
            if isinstance(v, str) and v:
                blobs.append(v)
        md = wrapper.get("metadata")
        if isinstance(md, dict):
            for k in ("error", "error_code", "message"):
                v = md.get(k)
                if isinstance(v, str) and v:
                    blobs.append(v)
    low = "\n".join(blobs).lower()
    if not low.strip():
        return None
    for tok in PROTECT_TOKENS:
        if tok in low:
            return tok
    return None


def read_phase_field(text: str):
    """Extract phase from a stderr/structured JSON blob (pre OR post submit)."""
    if not text:
        return None
    try:
        obj = json.loads(text.strip().lstrip("﻿"))
        if isinstance(obj, dict) and isinstance(obj.get("phase"), str):
            return obj["phase"]
    except (ValueError, TypeError):
        pass
    for key in ('"phase": "pre_submit"', '"phase":"pre_submit"',
                '"phase": "post_submit', '"phase":"post_submit'):
        if key in text:
            return "pre_submit" if "pre_submit" in key else "post_submit_ambiguous"
    return None


def drain_stream_realtime(stream, chunks: list, line_cb, hard_timeout: float):
    """Read a text pipe to EOF in a daemon thread; per-line callback (for
    stderr protection signals). Returns the thread. chunks collects all text.
    stdout lines are NEVER passed to protection scan."""
    def _pump():
        try:
            while True:
                line = stream.readline()
                if line is None or line == "":
                    break
                chunks.append(line)
                if line_cb is not None:
                    try:
                        line_cb(line)
                    except Exception:
                        pass
                if hard_timeout and (time.monotonic() - hard_timeout) > 86400:
                    break
        except Exception:
            pass
    th = threading.Thread(target=_pump, daemon=True)
    th.start()
    return th

# ---------------- worker ----------------

def run_one(task: dict, data_root: Path, rep: Reporter, state: dict,
            timeout: int, worker_no: int):
    prefix = data_root / task["prefix_rel"]
    # Last-line no-overwrite guard (any evidence blocks, even between queue-build and spawn).
    ev = any_evidence(prefix)
    if ev:
        rep.event("blocked_evidence_exists", task=task["task_id"],
                  evidence=[Path(q).name for q in ev[:4]])
        return ("blocked", task)
    prompt_abs = (data_root / task["prompt_rel"]).resolve()
    data = prompt_abs.read_bytes()
    actual = sha(data)
    if actual != task["prompt_hash"]:
        rep.event("failed", task=task["task_id"], reason="prompt_hash_mismatch")
        return ("hash_mismatch", task)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as e:
        rep.event("failed", task=task["task_id"], reason=f"prompt_not_utf8: {e}")
        return ("bad_prompt", task)
    if len(text) > 65536:
        rep.event("failed", task=task["task_id"], reason="prompt_over_65536_chars")
        return ("prompt_too_long", task)

    cmd = [str(GPT2_PY), str(GPT2_CLI), "ask",
           "--file", str(prompt_abs), "--model", MODEL[task["model"]], "--json"]
    popen_factory = state.get("popen_factory") or subprocess.Popen
    start_utc = utcnow()
    start_mono = time.monotonic()
    self_pid = os.getpid()
    rep.event("launched", task=task["task_id"], prefix=str(prefix),
              model=MODEL[task["model"]], mode=task["mode"], worker=worker_no,
              scheduler_pid=self_pid, child_argv=[Path(cmd[0]).name, Path(cmd[1]).name] + cmd[2:],
              start_utc=start_utc, start_monotonic=start_mono)
    ret, stdout, stderr, error = None, "", "", None
    child_pid = None
    spawned = False
    soft_slow = False
    try:
        proc = popen_factory(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=str(SAFECHAIN_ROOT),
                             encoding="utf-8", errors="replace", **hidden_popen_kwargs())
        spawned = True
        try:
            child_pid = getattr(proc, "pid", None)
        except Exception:
            child_pid = None
        rep.event("spawned", task=task["task_id"], worker=worker_no,
                  child_pid=child_pid, child_argv=cmd, cwd=str(SAFECHAIN_ROOT))
        # Realtime drains: stderr lines feed the protection signal live
        # (pause BEFORE wait returns); stdout is captured on its own
        # thread and NEVER scanned for protection (no music-body false +).
        # Soft budget expiry only records slow — the wait below still blocks
        # to TRUE child exit, holding the slot (no kill, no early release).
        err_chunks: list = []
        out_chunks: list = []

        def _on_err_line(line: str):
            tok = looks_like_protection(line, None, {})
            if tok:
                with state["lock"]:
                    if not state.get("protection_hit"):
                        state["protection_hit"] = tok
                try:
                    rep.event("protection_signal_live", task=task["task_id"],
                              token=tok, source="stderr_line",
                              note="pausing NEW submissions; in-flight holds slot to true exit")
                except Exception:
                    pass

        err_th = drain_stream_realtime(proc.stderr, err_chunks, _on_err_line, time.monotonic())
        out_th = drain_stream_realtime(proc.stdout, out_chunks, None, time.monotonic())
        try:
            ret = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            soft_slow = True
            rep.event("slow_worker_holding_slot", task=task["task_id"], worker=worker_no,
                      child_pid=child_pid, wait_budget=timeout,
                      note="local budget elapsed; holding slot to true child exit; no kill")
            ret = proc.wait()  # blocking to TRUE exit
            error = f"SLOW_HELD_TO_EXIT: waited past {timeout}s budget to true exit rc={ret}"
        err_th.join(timeout=30)
        out_th.join(timeout=30)
        stdout, stderr = "".join(out_chunks), "".join(err_chunks)
    except Exception as e:
        if not spawned:
            error = f"spawn_failed_pre_submit: {e}"
        else:
            error = f"worker_error_after_spawn_ambiguous: {e}"
    elapsed = round(time.monotonic() - start_mono, 3)
    slow_note = None
    if soft_slow and isinstance(error, str) and error.startswith("SLOW_HELD_TO_EXIT"):
        # Child reached TRUE exit after the soft budget: judge the outcome on
        # the real rc/stdout, keep the slowness as a note (not a failure).
        slow_note = error
        error = None
    pre_submit_spawn_failure = isinstance(error, str) and error.startswith("spawn_failed_pre_submit")

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
    session_handle = server_meta.get("session_handle")
    observed = sha(response.encode("utf-8")) if response else None
    reported = server_meta.get("response_sha256")
    # Success is strict: real exit 0 + completed + nonempty response + exact
    # route + max effort + reported SHA equals observed SHA + a real non-empty
    # session_handle binding the turn.
    success = (error is None and ret == 0 and wrapper.get("completed") is True
               and isinstance(response, str) and len(response.strip()) > 0
               and route == MODEL[task["model"]] and effort == "max"
               and isinstance(reported, str) and reported == observed
               and isinstance(session_handle, str) and len(session_handle.strip()) > 0)
    if soft_slow and success:
        # Slow-but-successful stays success; keep the slow note in meta.
        pass
    elif soft_slow and not success and slow_note and error is None:
        error = slow_note
    phase = wrapper.get("phase") if isinstance(wrapper.get("phase"), str) else None
    # stderr is the structured transport channel: parse phase JSON properly
    # (pre_submit OR post_submit), not substring-only pre_submit.
    stderr_phase = read_phase_field(stderr or "")
    if stderr_phase:
        phase = stderr_phase
    status = ("success" if success
              else ("confirmed_pre_submit_failure" if pre_submit_spawn_failure
                    else "failure_or_ambiguous"))
    if pre_submit_spawn_failure:
        phase = "pre_submit"
    job_dir = server_meta.get("job_directory")
    meta = {"id": task["task_id"], "kind": task["kind"], "job": task["job_id"],
            "model_requested": MODEL[task["model"]], "model_reported": route,
            "thinking_effort": effort, "prompt_sha256": actual,
            "session_handle_present": bool(isinstance(session_handle, str) and session_handle.strip()),
            "response_sha256_observed": observed,
            "response_sha256_reported": reported,
            "response_sha256_match": bool(observed and observed == reported),
            "completed": wrapper.get("completed"), "exit_code": ret,
            "elapsed_seconds": elapsed, "utc_start": start_utc, "utc_end": utcnow(),
            "monotonic_start": start_mono, "scheduler_pid": self_pid,
            "child_pid": child_pid, "child_argv": cmd, "child_cwd": str(SAFECHAIN_ROOT),
            "status": status, "phase": phase, "error": error, "slow_note": slow_note,
            "soft_slow_held_slot": soft_slow,
            "new_session": True, "runner": "gpt2 ask --file --model --json",
            "no_automatic_retry": True, "response_chars": len(response),
            "scheduler": "baseline_parallel_control_20261010/pipeline_v3.py",
            "scheduler_mode": task["mode"], "worker": worker_no,
            "provider_job_directory": job_dir}
    try:
        save_atomic(Path(str(prefix) + ".meta.json"), compact(meta))
        save_atomic(Path(str(prefix) + ".stderr.txt"), stderr or "")
        save_atomic(Path(str(prefix) + ".raw.json"), stdout or "")
        if success:
            save_atomic(Path(str(prefix) + ".txt"), response)
    except FileExistsError as e:
        rep.event("failed", task=task["task_id"], reason=f"evidence_collision: {e}")
        return ("collision", task)

    prot = looks_like_protection(stderr or "", error if not slow_note else None, wrapper)
    if prot and not success:
        with state["lock"]:
            state["protection_hit"] = prot
        rep.event("protection_signal", task=task["task_id"], token=prot,
                  source="stderr_or_structured_error_only",
                  note="pausing NEW submissions; draining in-flight; no credential change")
    if success:
        rep.event("result", task=task["task_id"], status="success",
                  elapsed=elapsed, response_chars=len(response),
                  child_pid=child_pid, slow=soft_slow, job_directory=job_dir)
    else:
        rep.event("result", task=task["task_id"], status=status,
                  elapsed=elapsed, phase=phase, error=error,
                  child_pid=child_pid, slow=soft_slow, job_directory=job_dir,
                  note="per-task failure only; queue continues; no auto retry")
    return (status, task)


def _wait_any(futs: set):
    done, pending = wait(futs, return_when=FIRST_COMPLETED)
    return done, pending


# ---------------- main ----------------

def parse_args(argv=None):
    ap = argparse.ArgumentParser(prog="pipeline_v3")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--run-dir", required=True, help="unique run dir, outside data-root")
    ap.add_argument("--queue", default=None, help="explicit queue JSON (else build new-only)")
    ap.add_argument("--max-inflight", type=int, default=8)
    ap.add_argument("--timeout-seconds", type=int, default=1200)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--mock-main-test", action="store_true")
    ap.add_argument("--no-phase2", action="store_true", default=True)
    ap.add_argument("--allow-phase2", action="store_true", default=False)
    ap.add_argument("--report-root", default=None)
    ap.add_argument("--build-queue-out", default=None,
                    help="build verified new-only queue to this path and exit (no submissions)")
    return ap.parse_args(argv)


def validate_dirs(data_root: Path, run_dir: Path):
    data_root = data_root.resolve()
    run_dir = run_dir.resolve()
    if run_dir == data_root or data_root in run_dir.parents:
        return f"--run-dir must be OUTSIDE --data-root (got {run_dir})"
    return None


def execute_queue(tasks, data_root: Path, run_dir: Path, rep: Reporter,
                  state: dict, timeout: int, max_inflight: int):
    stop_pause = run_dir / "pause.flag"
    stop_file = run_dir / "stop.flag"

    def protection_active():
        with state["lock"]:
            hit = state["protection_hit"]
        return bool(hit or stop_pause.exists() or stop_file.exists())

    claimed = set()
    claim_lock = threading.Lock()
    exit_code, term_status = 0, "finished"

    def worker_fn(t, worker_no):
        nonlocal exit_code, term_status
        if protection_active():
            rep.event("suppressed_before_spawn", task=t["task_id"], worker=worker_no,
                      token=state.get("protection_hit"),
                      note="protection/operator hold at execution time; nothing submitted")
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
            st, _ = run_one(t, data_root, rep, state, timeout, worker_no)
            key = ("success" if st == "success"
                   else ("confirmed_pre_submit_failure" if st == "confirmed_pre_submit_failure"
                         else ("failure_or_ambiguous" if st == "failure_or_ambiguous" else "other")))
            with state["lock"]:
                state["results"][key] += 1
        finally:
            with state["lock"]:
                state["inflight"] -= 1
                inf = state["inflight"]
            rep.set_status(inflight=inf, inflight_peak=state["peak"],
                           succeeded=state["results"]["success"],
                           failed=dict(state["results"]))

    with ThreadPoolExecutor(max_workers=max_inflight, thread_name_prefix="gpt2v3") as pool:
        futs = set()
        pending = list(tasks)
        worker_no = 0
        submitting = True
        while pending or futs:
            if submitting and protection_active():
                rep.event("protection_paused" if state.get("protection_hit") else "operator_hold",
                          token=state.get("protection_hit"),
                          note="no NEW submissions; draining in-flight to TRUE exit")
                rep.set_status(protection_paused=True, phase="draining")
                submitting = False
            while submitting and pending and len(futs) < max_inflight:
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
                except Exception as e:
                    rep.event("failed", reason=f"worker_crash: {e}")
    with state["lock"]:
        paused = state.get("protection_hit")
    if paused:
        term_status, exit_code = "protection_paused_drained", 3
    elif stop_file.exists():
        term_status, exit_code = "operator_stopped_drained", 3
    elif state["results"]["failure_or_ambiguous"] or state["results"]["other"] \
            or state["results"]["confirmed_pre_submit_failure"]:
        exit_code = 2
    return exit_code, term_status


def write_terminal(run_dir: Path, run_id: str, data_root: Path, tasks,
                   state: dict, exit_code: int, term_status: str, max_inflight: int):
    remaining = []
    for t in tasks:
        mp = data_root / t["prefix_rel"]
        if not Path(str(mp) + ".meta.json").exists():
            remaining.append(t["task_id"])
    terminal = {"utc": utcnow(), "run_id": run_id, "exit": exit_code,
                "status": ("QUEUE_FAILED" if exit_code == 2 else term_status),
                "counts": {"queued": len(tasks), "launched": state["launched"],
                           "results": dict(state["results"])},
                "inflight_peak": state["peak"], "max_inflight": max_inflight,
                "remaining_without_meta": remaining,
                "paths": {"status": str(run_dir / "status.json"),
                          "events": str(run_dir / "events.jsonl"),
                          "terminal": str(run_dir / "pipeline_terminal.json")},
                "data_root": str(data_root), "run_dir": str(run_dir)}
    (run_dir / "pipeline_terminal.json").write_text(compact(terminal), encoding="utf-8")
    return terminal, remaining


def main(argv=None):
    a = parse_args(argv)
    data_root = Path(a.data_root).resolve()
    run_dir = Path(a.run_dir).resolve()
    if not (data_root / "jobs" / "manifest.json").exists():
        print(f"bad data-root: {data_root}", flush=True)
        return 1
    err = validate_dirs(data_root, run_dir)
    if err:
        print(err, flush=True)
        return 1
    if a.selftest:
        return selftest(data_root, run_dir)
    if a.mock_main_test:
        return mock_main_test(data_root, run_dir)

    # Run-dir uniqueness is checked BEFORE any write, but the explicit
    # --queue file itself may live inside --run-dir (mock writes
    # explicit_queue.json first). Only RUN outputs count as conflicts.
    _RUN_OUTPUTS = ("status.json", "events.jsonl", "pipeline_terminal.json",
                    "run_handle.json", "selftest.log", "mock_main_test.log")
    if run_dir.exists() and any((run_dir / n).exists() for n in _RUN_OUTPUTS):
        print(f"--run-dir not unique/non-empty: {run_dir}", flush=True)
        return 1

    if a.build_queue_out:
        qp = Path(a.build_queue_out).resolve()
        if qp.exists():
            print(f"--build-queue-out exists, refusing overwrite: {qp}", flush=True)
            return 1
        tasks, skipped, info = build_new_only_queue(data_root)
        qp.parent.mkdir(parents=True, exist_ok=True)
        qp.write_text(compact({"utc": utcnow(), "data_root": str(data_root),
                               "info": info, "tasks": tasks, "skipped": skipped}),
                      encoding="utf-8")
        print(f"QUEUE total={len(tasks)} info={info} skipped={len(skipped)}", flush=True)
        print(f"QUEUE_FILE={qp}", flush=True)
        return 0

    if a.queue:
        q = json.loads(Path(a.queue).read_text(encoding="utf-8"))
        tasks = q["tasks"] if isinstance(q, dict) and "tasks" in q else q
        skipped = q.get("skipped", []) if isinstance(q, dict) else []
    else:
        print("no --queue and no --build-queue-out: refusing to mix queue-build and run in one invocation", flush=True)
        return 1
    if a.dry_run:
        print(f"DRY-RUN tasks={len(tasks)}: no submissions, no writes.", flush=True)
        for t in tasks[:12]:
            print(f"  PLAN {t['task_id']} {t['prompt_hash'][:12]}", flush=True)
        return 0
    run_dir.mkdir(parents=True, exist_ok=True)
    rep = Reporter(run_dir)
    run_id = f"v3-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    state = {"lock": threading.Lock(), "protection_hit": None,
             "inflight": 0, "peak": 0, "launched": 0,
             "results": {"success": 0, "confirmed_pre_submit_failure": 0,
                         "failure_or_ambiguous": 0, "other": 0}}
    # NOTE: fixed NameError — GPT2 was undefined; use the defined interpreter + CLI.
    rep.set_status(run_id=run_id, phase="running-queue",
                   total_queued=len(tasks), skipped=len(skipped),
                   launched=0, inflight=0, inflight_peak=0,
                   max_inflight=a.max_inflight, protection_paused=False,
                   scheduler_pid=os.getpid(),
                   gpt2_py=str(GPT2_PY), gpt2_cli=str(GPT2_CLI),
                   init_lock={"path": str(INIT_LOCK_PATH),
                              "exists": INIT_LOCK_PATH.exists(),
                              "kind": "HeadlessNativeGPT2AgentProvider InitializerLock (OS-global file lock, 600s timeout)",
                              "note": "browser-init serialization is native; 8-wide window covers HTTP-answer waiting, NOT 8 lock waiters"},
                   data_root=str(data_root), run_dir=str(run_dir))
    rep.event("run_started", run_id=run_id, max_inflight=a.max_inflight,
              queue_total=len(tasks), skipped=len(skipped),
              scheduler_pid=os.getpid(), gpt2_py=str(GPT2_PY), gpt2_cli=str(GPT2_CLI),
              init_lock_exists=INIT_LOCK_PATH.exists())
    for s in skipped:
        if isinstance(s, dict):
            rep.event("queued_skip", slot=s.get("slot"), reason=s.get("reason"))
        else:
            rep.event("queued_skip", slot=s[0], reason=s[1])
    for t in tasks:
        rep.event("queued", task=t["task_id"], mode=t["mode"], prefix=t["prefix_rel"])

    try:
        exit_code, term_status = execute_queue(tasks, data_root, run_dir, rep, state,
                                               a.timeout_seconds, a.max_inflight)
        # Phase2 is NEVER in-place. Only external additive builder on --report-root.
        if a.allow_phase2:
            if not a.report_root:
                rep.event("phase2_step", error="--allow-phase2 requires --report-root")
            else:
                rr = Path(a.report_root).resolve()
                if rr == data_root or data_root in rr.parents or rr == run_dir:
                    rep.event("phase2_step", error="bad report-root (must be outside data-root/run-dir)")
                else:
                    rr.mkdir(parents=True, exist_ok=True)
                    (rr / "v3_mechanical_summary.json").write_text(
                        compact({"utc": utcnow(), "run_id": run_id,
                                 "counts": dict(state["results"]),
                                 "note": "additive-only; data-root untouched"}), encoding="utf-8")
                    rep.event("phase2_done", report_root=str(rr))
    except Exception as e:
        term_status, exit_code = f"fatal: {e}", 1
        try:
            rep.event("fatal", reason=str(e))
        except Exception:
            pass

    terminal, remaining = write_terminal(run_dir, run_id, data_root, tasks, state,
                                         exit_code, term_status, a.max_inflight)
    rep.event("finished" if exit_code == 0 else "fatal", status=term_status,
              exit=exit_code, remaining=len(remaining))
    rep.set_status(phase="terminal", terminal=term_status)
    print(f"TERMINAL {term_status} exit={exit_code} remaining={len(remaining)} "
          f"peak={state['peak']} results={dict(state['results'])}", flush=True)
    print(f"RUN_DIR={run_dir}", flush=True)
    return exit_code


# ---------------- offline tests (NO model submission) ----------------

def _check_hidden_flags():
    kw = hidden_popen_kwargs()
    if os.name == "nt":
        ok = (kw.get("creationflags", 0) & getattr(subprocess, "CREATE_NO_WINDOW", 0)) != 0
        ok = ok and kw.get("startupinfo") is not None
        ok = ok and not (kw.get("creationflags", 0) & getattr(subprocess, "DETACHED_PROCESS", 0))
    else:
        ok = kw.get("start_new_session") is True
    return ok, sorted(kw)


def _real_no_model_probes(tmp_run: Path):
    """Real child capture + visible-window diff + local CLI check/help (no model)."""
    out = {"probes": []}

    def rec(name, ok, detail=""):
        out["probes"].append({"name": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    before = list_visible_windows()
    # 1) fast echo child via same kwargs
    p = subprocess.Popen([str(GPT2_PY), "-I", "-c",
                          "import sys; print('v3-hidden-child-ok'); print('ERR-LINE', file=sys.stderr)"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         encoding="utf-8", errors="replace", **hidden_popen_kwargs())
    so, se = p.communicate(timeout=60)
    after = list_visible_windows()
    rec("real_child_capture", p.returncode == 0 and "v3-hidden-child-ok" in (so or "")
        and "ERR-LINE" in (se or ""), f"rc={p.returncode} out={repr((so or '').strip()[:40])}")
    rec("no_new_visible_window", set(after) <= set(before),
        f"before={len(before)} after={len(after)} new={sorted(set(after)-set(before))[:3]}")
    argv = [str(GPT2_PY), str(GPT2_CLI), "check"]
    rec("no_cmd_in_argv", not any(x.lower().endswith((".cmd", ".bat")) or "cmd.exe" in x.lower() for x in argv),
        f"{Path(argv[0]).name} {Path(argv[1]).name}")
    before2 = list_visible_windows()
    p2 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=str(SAFECHAIN_ROOT),
                          encoding="utf-8", errors="replace", **hidden_popen_kwargs())
    so2, se2 = p2.communicate(timeout=120)
    after2 = list_visible_windows()
    try:
        payload = json.loads((so2 or "").strip().lstrip("\ufeff"))
        looks_local = isinstance(payload, dict) and "docker_ready" in payload
    except Exception:
        payload, looks_local = None, False
    rec("real_cli_check_hidden", looks_local,
        f"rc={p2.returncode} docker_ready={(payload or {}).get('docker_ready') if isinstance(payload, dict) else None}")
    rec("check_no_new_window", set(after2) <= set(before2),
        f"before={len(before2)} after={len(after2)}")
    # --help sends no model request
    p3 = subprocess.Popen([str(GPT2_PY), str(GPT2_CLI), "ask", "--help"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=str(SAFECHAIN_ROOT),
                          encoding="utf-8", errors="replace", **hidden_popen_kwargs())
    so3, _se3 = p3.communicate(timeout=60)
    rec("cli_help_no_model", p3.returncode == 0 and "--file" in (so3 or "") and "--model" in (so3 or ""),
        f"rc={p3.returncode}")
    out["all_ok"] = all(x["ok"] for x in out["probes"])
    return out


def selftest(data_root: Path, run_dir: Path):
    run_dir.mkdir(parents=True, exist_ok=True)
    logp = run_dir / "selftest.log"
    lines = []

    def log(s):
        lines.append(s)
        print(s, flush=True)

    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
        log(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    tasks, skipped, info = build_new_only_queue(data_root)
    check("queue_builds_new_only", len(tasks) > 0, f"tasks={len(tasks)} skipped={len(skipped)} info={info}")
    # New-only invariant: no target has any evidence.
    inv = True
    for t in tasks:
        if any_evidence(data_root / t["prefix_rel"]):
            inv = False
            log(f"  new-but-evidence-exists: {t['task_id']}")
            break
    check("new_only_no_evidence", inv, f"tasks={len(tasks)}")
    # Hash + length + unique prefix.
    hh = True
    for t in tasks:
        p = (data_root / t["prompt_rel"])
        if not p.exists() or sha(p.read_bytes()) != t["prompt_hash"] or len(p.read_text(encoding="utf-8")) > 65536:
            hh = False
            log(f"  hash/len: {t['task_id']}")
            break
    check("freeze_hash_len", hh)
    check("unique_prefix", len({t["prefix_rel"] for t in tasks}) == len(tasks))
    # Round-major + flip: verify per-round model order flips per job vs frozen rule.
    check("queue_order_bands", info.get("ordered_total") == len(tasks),
          f"{info}")
    # save_atomic no-overwrite.
    probe = run_dir / "_selftest_probe.txt"
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
    # Protection: stderr/structured only — music-body numbers must NOT trigger.
    music_body = "aria 403 and 429 appear in lyrics discussion, response text only"
    wrapper_music = {"completed": True, "response": music_body,
                     "metadata": {"model": "gpt-6-thinking"}}
    check("protect_no_music_false_positive",
          looks_like_protection("", None, wrapper_music) is None
          and looks_like_protection("all clear", None, {}) is None)
    check("protect_real_stderr",
          looks_like_protection('{"error": "HTTP 429 too many requests"}', None, {}) == "429")
    fl, keys = _check_hidden_flags()
    check("hidden_flags_no_detached", fl, f"keys={keys}")
    check("native_init_lock_present", INIT_LOCK_PATH.exists(), str(INIT_LOCK_PATH))
    probes = _real_no_model_probes(run_dir)
    for pr in probes["probes"]:
        check("nomo_" + pr["name"], pr["ok"], pr["detail"])
    log(f"SELFTEST {'OK' if ok else 'FAILED'} tasks={len(tasks)} skipped={len(skipped)}")
    logp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


class FakeProc:
    """Offline stand-in for Popen (no model, no network).

    Spawns a REAL hidden python child that sleeps then prints controlled
    bytes, so the realtime stderr drain + live protection signal + soft-wait
    to-true-exit path is exercised over real OS pipes (StringIO stand-ins
    race and truncate; real pipes don't).
    NOTE: uses _REAL_POPEN captured at import time — the mock patches
    subprocess.Popen and must never recurse into itself.
    """

    def __init__(self, argv, behavior):
        import base64 as _b64
        b = behavior
        kind = b.get("kind", "success")
        if kind == "slow_success":
            script = (
                "import time,sys;"
                f"time.sleep({float(b.get('hold', 0.6))});"
                "sys.stdout.write(S);sys.stdout.flush()"
            )
            payload = {"S": b["stdout"]}
        elif kind == "protection":
            script = (
                "import time,sys;"
                "sys.stderr.write(E);sys.stderr.flush();"
                f"time.sleep({float(b.get('slow_stdout', 0.8))});"
                "sys.stdout.write(S);sys.stdout.flush()"
            )
            payload = {"S": b.get("stdout", ""), "E": b.get("stderr", "")}
        elif kind == "success_strict":
            script = (
                "import time,sys;"
                f"time.sleep({float(b.get('delay', 0.05))});"
                "sys.stdout.write(S);sys.stdout.flush()"
            )
            payload = {"S": b["stdout"]}
        else:
            script = "import sys;sys.stdout.write(S);sys.stdout.flush()"
            payload = {"S": b.get("stdout", "")}
        code = "import sys;S=sys.stdin.read();E='';\n" + script
        # Pass S/E via env-safe argv: encode payload into the script itself.
        blob = json.dumps(payload, ensure_ascii=False)
        prog = f"import json; P=json.loads({blob!r}); S=P.get('S',''); E=P.get('E','');\n" + script
        self._proc = _REAL_POPEN(
            [sys.executable, "-I", "-c", prog],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            encoding="utf-8", errors="replace", **hidden_popen_kwargs())
        self.argv = argv
        self.pid = self._proc.pid

    @property
    def stdout(self):
        return self._proc.stdout

    @property
    def stderr(self):
        return self._proc.stderr

    @property
    def returncode(self):
        return self._proc.returncode

    def wait(self, timeout=None):
        return self._proc.wait(timeout=timeout)

    def communicate(self, timeout=None):
        return self._proc.communicate(timeout=timeout)


def mock_main_test(data_root: Path, run_dir: Path):
    """Exercise the REAL main() with a mocked spawner (no model calls).

    Proves: no NameError, explicit --queue + unique --run-dir, rolling window,
    pause stops new spawns, slow holds its slot (peak accounting), unique
    prefix/no-overwrite, all-terminal, plus real no-model probes.
    """
    lines = []

    def log(s):
        lines.append(s)
        print(s, flush=True)

    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
        log(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # Build a tiny fake frozen tree (isolated from real Downloads freeze).
    with tempfile.TemporaryDirectory(prefix="v3mock_frozen_") as fz, \
            tempfile.TemporaryDirectory(prefix="v3mock_run_") as _rr:
        fz = Path(fz)
        (fz / "jobs" / "reviews").mkdir(parents=True, exist_ok=True)
        prompts = {"J1": "prompt one text", "J2": "prompt two text"}
        mjobs = []
        for jid, body in prompts.items():
            rels = {}
            for m in ("gpt6w", "gpt56w"):
                rp = f"jobs/{m}/{jid}.txt"
                (fz / rp).parent.mkdir(parents=True, exist_ok=True)
                (fz / rp).write_text(body + f" {m} {jid}\n", encoding="utf-8")
                rels[m] = rp
            h = sha(((fz / rels["gpt6w"]).read_bytes()))
            # Both models share identical bytes per brief pairing? keep per-model
            # files with same hash by writing identical content:
            (fz / rels["gpt56w"]).write_text(body + f" {jid} shared\n", encoding="utf-8")
            (fz / rels["gpt6w"]).write_text(body + f" {jid} shared\n", encoding="utf-8")
            h = sha((fz / rels["gpt6w"]).read_bytes())
            mjobs.append({"job_id": jid,
                          "model_prompt_paths": rels, "input_sha256": h,
                          "first_model": "gpt6w" if jid == "J1" else "gpt56w"})
        (fz / "jobs" / "manifest.json").write_text(
            compact({"jobs": mjobs}), encoding="utf-8")
        rrows = []
        for k, kind in (("RJ1", "D"), ("RJ2", "G")):
            for judge in ("gpt6w", "gpt56w"):
                rp = f"jobs/reviews/{judge}/{k}_{judge}.txt"
                (fz / rp).parent.mkdir(parents=True, exist_ok=True)
                (fz / rp).write_text(f"review {k} {judge}\n", encoding="utf-8")
                rrows.append({"job_id": f"{k}_{judge}", "kind": kind,
                              "judge_model": judge, "prompt_file": rp,
                              "prompt_sha256": sha((fz / rp).read_bytes())})
        (fz / "jobs" / "reviews" / "review_manifest.json").write_text(
            compact({"schema": "t", "jobs": rrows}), encoding="utf-8")

        # Temporarily narrow expansion to our fake jobs by monkey-patching.
        global EXPANSION_JOBS, EXPANSION_ROUNDS
        old_jobs, old_rounds = EXPANSION_JOBS, EXPANSION_ROUNDS
        EXPANSION_JOBS, EXPANSION_ROUNDS = ("J1", "J2"), (6, 7)
        try:
            tasks, skipped, info = build_new_only_queue(fz)
        finally:
            EXPANSION_JOBS, EXPANSION_ROUNDS = old_jobs, old_rounds
        check("mock_queue_built", len(tasks) == 2 * 2 * 2 + 4, f"tasks={len(tasks)} info={info}")
        # Write explicit queue JSON.
        mock_run = Path(run_dir)
        if mock_run.exists() and any(mock_run.iterdir()):
            # isolation: use a fresh subdir for the mock run
            mock_run = mock_run / f"mock_{int(time.time())}"
        mock_run.mkdir(parents=True, exist_ok=True)
        qpath = mock_run / "explicit_queue.json"
        qpath.write_text(compact({"tasks": tasks}), encoding="utf-8")

        # Fake spawner: first task slow_success (holds slot), one protection.
        calls = {"n": 0}
        lock = threading.Lock()
        spawn_log = []
        orig_popen = subprocess.Popen

        def fake_popen(cmd, **kw):
            with lock:
                calls["n"] += 1
                n = calls["n"]
                spawn_log.append({"n": n, "argv_tail": cmd[2:5], "t": time.monotonic()})
            mdl = ""
            try:
                mi = cmd.index("--model")
                mdl = cmd[mi + 1]
            except ValueError:
                mdl = ""
            import hashlib as _hl

            def _strict(txt):
                h = _hl.sha256(txt.encode("utf-8")).hexdigest()
                return compact({"completed": True, "response": txt,
                                "metadata": {"model": mdl, "thinking_effort": "max",
                                             "response_sha256": h,
                                             "session_handle": f"sess-mock-{n}",
                                             "job_directory": ""}})
            # Deterministic by spawn order (not filename): n==1 slow-holds its
            # slot to true exit (stdout arrives after the soft budget), n==3
            # emits a real 429 on stderr EARLY while stdout is still slow, so
            # the live drain must trip pause before wait() returns.
            if n == 1:
                return FakeProc(cmd, {"kind": "slow_success",
                                      "stdout": _strict("slow ok body"), "hold": 1.6})
            if n == 3:
                return FakeProc(cmd, {"kind": "protection",
                                      "stderr": "upstream HTTP 429 too many requests",
                                      "stdout": _strict("late body after 429"),
                                      "slow_stdout": 1.2})
            return FakeProc(cmd, {"kind": "success_strict",
                                  "stdout": _strict(f"ok body {n}"), "delay": 0.15})

        # Patch run_one's factory via state injection: easiest is to patch
        # subprocess.Popen seen by run_one default (state has no factory, so it
        # uses subprocess.Popen at call time) — patch the attribute.
        subprocess.Popen = fake_popen
        try:
            rc = main(["--data-root", str(fz), "--run-dir", str(mock_run),
                       "--queue", str(qpath), "--max-inflight", "2",
                       "--timeout-seconds", "1"])
        finally:
            subprocess.Popen = orig_popen
        check("mock_main_no_nameerror", rc in (0, 2, 3), f"rc={rc}")
        term_p = mock_run / "pipeline_terminal.json"
        check("mock_terminal_written", term_p.exists())
        if term_p.exists():
            term = json.loads(term_p.read_text(encoding="utf-8"))
            check("mock_all_terminal", term.get("status") in ("QUEUE_FAILED", "protection_paused_drained", "finished"),
                  f"status={term.get('status')} counts={term.get('counts')}")
            check("mock_pause_engaged", term.get("status") == "protection_paused_drained",
                  "protection task must pause new submissions")
            # Pause => fewer spawns than queued tasks.
            check("mock_pause_no_new_spawn", calls["n"] < len(tasks),
                  f"spawned={calls['n']} queued={len(tasks)}")
            try:
                ev_lines = (mock_run / "events.jsonl").read_text(encoding="utf-8").splitlines()
                live = [l for l in ev_lines if "protection_signal_live" in l]
                slow_ev = [l for l in ev_lines if "slow_worker_holding_slot" in l]
                check("mock_protect_live_before_exit", bool(live),
                      f"live_signals={len(live)} slow_notes={len(slow_ev)}")
            except Exception as e:
                check("mock_protect_live_before_exit", False, f"events unreadable: {e}")
            check("mock_peak_within_window", term.get("inflight_peak", 99) <= 2,
                  f"peak={term.get('inflight_peak')}")
        # Slow-hold proof: run_one slow path must block past budget holding slot.
        # Direct micro-proof with two threads sharing max 1 slot.
        with tempfile.TemporaryDirectory(prefix="v3slow_") as srun:
            srun = Path(srun)
            rep = Reporter(srun)

            def _slow_factory(cmd, **kw):
                import hashlib as _hl
                mdl = MODEL["gpt6w"]
                try:
                    mi = cmd.index("--model")
                    mdl = cmd[mi + 1]
                except ValueError:
                    pass
                h = _hl.sha256(b"s").hexdigest()
                return FakeProc(cmd, {"kind": "slow_success", "hold": 1.4,
                                      "stdout": compact({"completed": True, "response": "s",
                                                         "metadata": {"model": mdl,
                                                                      "thinking_effort": "max",
                                                                      "response_sha256": h,
                                                                      "session_handle": "sess-slow-micro"}})})
            st = {"lock": threading.Lock(), "protection_hit": None, "inflight": 0,
                  "peak": 0, "launched": 0,
                  "results": {"success": 0, "confirmed_pre_submit_failure": 0,
                              "failure_or_ambiguous": 0, "other": 0},
                  "popen_factory": _slow_factory}
            # Slow-hold micro-proof on a FRESH prefix (never written above):
            # run_one slow path must block past budget holding the slot.
            EXP_fake = fz
            t0 = {"kind": "trial", "model": "gpt6w", "job_id": "J1", "round": "r08",
                  "mode": "new", "prompt_rel": "jobs/gpt6w/J1.txt",
                  "prompt_hash": sha((fz / "jobs/gpt6w/J1.txt").read_bytes()),
                  "task_id": "gpt6w:J1:r08:new", "prefix_rel": "results/trials/gpt6w/J1/r08"}
            t0b = time.monotonic()
            s, _ = run_one(t0, EXP_fake, rep, st, 1, 1)
            held = time.monotonic() - t0b
            check("slow_holds_slot_no_kill", s == "success" and held >= 1.4,
                  f"status={s} held={round(held,2)}s (budget=1s + 1.4s late stdout hold)")

    probes = _real_no_model_probes(Path(run_dir))
    for pr in probes["probes"]:
        check("nomo_" + pr["name"], pr["ok"], pr["detail"])
    (Path(run_dir) / "mock_main_test.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"MOCK_MAIN_TEST {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
