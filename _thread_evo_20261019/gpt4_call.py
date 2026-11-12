"""11-05 由 gpt3_call.py 机械复制：只换 CLI、槽位、锁、记录里的账号名。"""
"""Careful gpt3 route for evo.call (10-26/27, user: retry the gpt3 account (yi) at Extra High / max, serial, ~20 s apart).
- shared slots limit requests in flight; at least GAP s (+ up to 10 s jitter) between real submissions;
- hold the submission gate until the previous request starts returning (or exits / times out);
- --allow-topic-stream: when an answer moves to the websocket topic (the 10-24 truncation cause), the CLI follows that
  same turn instead of ending with thoughts only; it never regenerates;
- stop for good on a usage-limit / protection message, after 2 failures in a row, or after 3 failures in total.
No fingerprint, verification or anti-bot tricks: only pacing and honest stopping."""
import hashlib, json, os, random, re, subprocess, threading, time
from pathlib import Path
from datetime import datetime, timezone
import evo

GPT3 = "D:/musicclaude/gpt2agent-safechain/bin/gpt4.cmd"  # 11-05: gpt4 账号，和 gpt3 并行
GAP = float(os.environ.get("GPT3_GAP", "20"))
SLOTS_FILE = evo.RUNS / "gpt4_slots.txt"
from pathlib import Path as _P
GPT4_RUNS = _P("D:/musicclaude/gpt2agent-safechain/runs/gpt4")           # 10-27 user: a normal heavy user's pace, raised live if the deadline needs it


def slots():
    try:
        return max(1, int(SLOTS_FILE.read_text().strip()))
    except Exception:
        return int(os.environ.get("GPT3_SLOTS", "1"))
_one = threading.Semaphore(8); _last = [0.0]
LOCK = evo.RUNS / "gpt4_serial.lock"; STAMP = evo.RUNS / "gpt4_last_submit.txt"


class _Serial:
    """at most GPT3_SLOTS gpt3 requests in flight across all processes (one msvcrt byte lock per slot on a shared file)"""
    def __enter__(s):
        import msvcrt
        _one.acquire(); s.f = open(LOCK, "a+")
        while True:
            for i in range(slots()):
                try:
                    s.f.seek(i); msvcrt.locking(s.f.fileno(), msvcrt.LK_NBLCK, 1); s.i = i; return s
                except OSError:
                    pass
            time.sleep(5)

    def __exit__(s, *a):
        import msvcrt
        s.f.seek(s.i); msvcrt.locking(s.f.fileno(), msvcrt.LK_UNLCK, 1); s.f.close(); _one.release()


_state = {"row": 0, "total": 0, "stop": None, "last_error": ""}
STOP_WORDS = ("hit your limit", "429", "unusual activity", "UNUSUAL_ACTIVITY", "rate limit", "too many requests")


def stopped():
    return _state["stop"]


def protection_signal():
    import mg_schedule
    return mg_schedule.suspicious(_state.get('last_error', ''))


def resume_transient():
    """Only the ordinary route-backoff expiry can reset consecutive failures."""
    if protection_signal():
        return False
    _state.update(row=0, total=0, stop=None, last_error='')
    return True


def _fail(run_id, why):
    _state['last_error'] = why
    _state["row"] += 1; _state["total"] += 1
    # Job-directory timestamps can contain the digits 429. Only a standalone
    # status number is evidence of HTTP 429; retain all explicit limit signals.
    limit = (any(w.lower() in why.lower() for w in STOP_WORDS if w != '429')
             or re.search(r'(?<!\d)429(?!\d)', why) is not None)
    if protection_signal() or limit:
        _state["stop"] = f"protection/limit signal at {run_id}"
    elif _state["row"] >= 2 or _state["total"] >= 3:
        _state["stop"] = f"{_state['row']} in a row / {_state['total']} total failures (last {run_id})"
    if _state["stop"]:
        print(f"GPT3 STOPPED: {_state['stop']}", flush=True)


GATE = evo.RUNS / "gpt4_submit.lock"


SUBMIT_TIMEOUT = 180
SUBMIT_POLL = 1


def _wait_submission(proc, message, t0, existing, run_id):
    """Observe only this launch's new prompt-matched job while holding GATE."""
    deadline = time.monotonic() + SUBMIT_TIMEOUT
    job = None; submitted_utc = None; submitted_epoch = None
    want = message.rstrip()  # The CLI rstrips the input before saving prompt.txt.
    while True:
        if job is None:
            for candidate in GPT4_RUNS.glob("pro-bridge-*"):
                try:
                    if candidate in existing or candidate.stat().st_ctime < t0:
                        continue
                    if (candidate / "prompt.txt").read_text(encoding="utf-8-sig").rstrip() == want:
                        job = candidate
                        break
                except (OSError, UnicodeError):
                    pass  # The CLI may still be creating the directory / writing the prompt.
        if job is not None:
            try:
                utc = json.loads((job / "submitted.json").read_text(encoding="utf-8"))["utc"]
                parsed = datetime.fromisoformat(utc.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                submitted_epoch = parsed.timestamp(); submitted_utc = utc
            except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError):
                pass  # Missing or partially written evidence is retried on the next poll.
            try:
                network = json.loads((job / "generation-network.json").read_text(encoding="utf-8"))
                if submitted_epoch is not None and network.get("first_chunk_ms") is not None:
                    break
            except (OSError, ValueError, AttributeError):
                pass
        if proc.poll() is not None:
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(f"[{run_id}] WARNING: submission/first-chunk wait timed out after {SUBMIT_TIMEOUT}s; releasing GATE", flush=True)
            break
        time.sleep(min(SUBMIT_POLL, remaining))
    return submitted_utc, submitted_epoch


def _space_submission(command, message, run_id):
    """Wait from the previous real submit, launch, and observe first return under GATE."""
    import msvcrt
    with open(GATE, "a+") as f:
        while True:
            try:
                f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1); break
            except OSError:
                time.sleep(1)
        try:
            last = float(STAMP.read_text(encoding="utf-8")) if STAMP.exists() else 0.0
            w = GAP + random.uniform(0, 10) - (time.time() - last)
            if w > 0:
                time.sleep(w)
            existing = set(GPT4_RUNS.glob("pro-bridge-*"))
            started = time.strftime("%Y-%m-%dT%H:%M:%S"); t0 = time.time()
            evo.check_submission()
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            submitted_utc, submitted_epoch = _wait_submission(proc, message, t0, existing, run_id)
            STAMP.write_text(str(submitted_epoch if submitted_epoch is not None else time.time()), encoding="utf-8")
            gap = submitted_epoch - last if submitted_epoch is not None and last else None
            return proc, started, t0, submitted_utc, gap
        finally:
            f.seek(0); msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


def call(run_id, message, prompt_text, model, meta):
    d = evo.RUNS / run_id
    if evo.want_no_web(meta) and evo.NO_WEB.strip() not in message[-60:]:
        message += evo.NO_WEB
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    inp = d / "input.txt"; inp.write_text(message, encoding="utf-8")
    if meta:
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    attach = [str(a) for a in (meta or {}).get("attach") or [] if os.path.getsize(a) > 0]     # gpt3 rejects empty files
    if len(message) > 60000:              # 10-27 user: the body is capped at 65,536 chars, attachments are not
        full = d / "full_prompt.txt"; full.write_text(message, encoding="utf-8"); attach.append(str(full))
        message = ("这次的任务全文太长，放在附件 full_prompt.txt 里。请把附件从头到尾完整读完（不要只检索片段），"
                   "然后严格按附件里的要求作答，只输出附件要求的格式。")
        inp.write_text(message, encoding="utf-8")
        print(f"[{run_id}] long prompt ({full.stat().st_size} bytes) sent as attachment", flush=True)
    for attempt in range(2):
        with _Serial():
            if stopped():
                print(f"[{run_id}] SKIPPED ({stopped()})", flush=True); return None
            command = [GPT3, "ask", "--file", str(inp), "--json", "--model", model, "--allow-topic-stream"] \
                      + [x for a in attach for x in ("--attach", a)]
            proc, started, t0, submitted_utc, gap = _space_submission(command, message, run_id)
            stdout, stderr = proc.communicate()
            cp = subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
        dt = time.time() - t0
        (d / "stdout.bin").write_bytes(cp.stdout); (d / "stderr.bin").write_bytes(cp.stderr)
        try:
            j = json.loads(cp.stdout.decode("utf-8"))
        except Exception:
            j = {}
        md = j.get("metadata") or {}; resp = j.get("response") or ""
        ok = (cp.returncode == 0 and j.get("completed") is True and resp.strip()
              and md.get("model") == model and md.get("thinking_effort") == "max")
        rec = {"run_id": run_id, "attempt": attempt, "account": "gpt4", "route": "gpt4-serial", "started": started,
               "submitted_utc": submitted_utc, "gap_since_prev_submit_s": gap,
               "seconds": round(dt), "exit_code": cp.returncode, "completed": bool(ok), "model": md.get("model"),
               "thinking_effort": md.get("thinking_effort"), "job_directory": md.get("job_directory"),
               "message_chars": len(message), "message_sha256": hashlib.sha256(message.encode()).hexdigest(), "meta": meta or {}}
        if ok:
            _state["row"] = 0; rec["response_chars"] = len(resp)
            if len(message) > 3000 and dt < 60:
                rec["fast"] = True; print(f"[{run_id}] FAST {dt:.0f}s -> cup probe", flush=True)
            (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "output.txt").write_text(resp, encoding="utf-8"); evo.log(rec)
            print(f"[{run_id}] ok {dt:.0f}s {len(resp)} chars", flush=True)
            return resp
        err = cp.stderr.decode("utf-8", "replace")
        rec["stderr_tail"] = err[-800:]
        (d / f"call_fail_{attempt}.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8"); evo.log(rec)
        print(f"[{run_id}] FAILED rc={cp.returncode} {dt:.0f}s {err[-160:]!r}", flush=True)
        _fail(run_id, err + json.dumps(j, ensure_ascii=False)[-400:])
    return None
