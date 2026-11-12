"""Cross-process spacing; half-hour protection pause only for suspicious behavior.

This module never submits requests or changes model/prompt/account settings.
Completed and already-submitted requests can still be collected during cooldown.
"""
import json
import os
import re
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent / "runs" / "_mg_schedule"
GAP = 20
COOLDOWN = 1800  # user correction: only explicit suspicious-behavior signals
RETRY_DELAY = 60  # ordinary gateway/transport failures: short, bounded retry delay


class CoolingDown(RuntimeError):
    pass


def utc(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


@contextmanager
def locked(directory=None):
    directory = Path(directory or DIRECTORY)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "schedule.lock").open("a+b") as handle:
        if handle.seek(0, 2) == 0:
            handle.write(b"\0")
            handle.flush()
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (OSError, BlockingIOError):
                time.sleep(0.05)
        try:
            yield directory
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _read(directory):
    path = directory / "state.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _write(directory, state):
    path = directory / "state.json"
    temp = directory / f"state.{os.getpid()}.tmp"
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def suspicious(reason):
    text = json.dumps(reason, ensure_ascii=False) if not isinstance(reason, str) else reason
    return bool(re.search(r"suspicious(?:[\s_-]+user)?[\s_-]+(?:behaviou?r|activity)|unusual[\s_-]+activity|可疑(?:行为|活动)", text, re.I))


def _normalize(state):
    """Also correct writes from old in-flight callers, using the original failure time."""
    before = dict(state)
    stamp = state.get("failed_at")
    if stamp is not None and state.get("classified_failure_at") != stamp:
        protected = suspicious(state.get("reason", ""))
        field, delay = ("protection_until", COOLDOWN) if protected else ("retry_until", RETRY_DELAY)
        state[field] = max(state.get(field, 0), stamp + delay)
        state.update(classified_failure_at=stamp,
                     failure_kind="suspicious_behavior" if protected else "transient_failure")
        if protected:
            state.update(protection_run=state.get("failed_run"), protection_reason=state.get("reason"))
    protection, retry = state.get("protection_until", 0), state.get("retry_until", 0)
    deadline = max(protection, retry)
    state.update(cooldown_until=deadline, resume_after_utc=utc(deadline),
                 cooldown_seconds=COOLDOWN if protection > retry else RETRY_DELAY,
                 cooldown_kind="suspicious_behavior" if protection > retry else "transient_failure")
    return state != before


def status(directory=None):
    with locked(directory) as folder:
        state = _read(folder)
        if _normalize(state):
            _write(folder, state)
    state["cooling"] = state.get("cooldown_until", 0) > time.time()
    return state


def check(directory=None):
    state = status(directory)
    if state["cooling"]:
        raise CoolingDown(f"冷却至 {utc(state['cooldown_until'])}: {state.get('reason', '')}")


def fail(run_id, reason, directory=None, now=None):
    """Record failure evidence; only explicit suspicious behavior gets 30 minutes."""
    observed = time.time() if now is None else now
    with locked(directory) as folder:
        state = _read(folder)
        _normalize(state)
        state.update(failed_at=observed, failed_at_utc=utc(observed), failed_run=run_id,
                     reason=str(reason)[:600])
        _normalize(state)
        _write(folder, state)
    return state


def reserve(run_id, directory=None, gap=GAP, submit=None):
    """Reserve one submission instant, serialized across all caller processes."""
    while True:
        with locked(directory) as folder:
            state = _read(folder)
            if _normalize(state):
                _write(folder, state)
            now = time.time()
            if state.get("cooldown_until", 0) > now:
                raise CoolingDown(f"冷却至 {utc(state['cooldown_until'])}: {state.get('reason', '')}")
            wait = state.get("last_submit", 0) + gap - now
            if wait <= 0:
                state.update(last_submit=now, last_submit_utc=utc(now), last_run=run_id)
                _write(folder, state)
                # Keep the lock through dispatch so delayed processes cannot bunch sends.
                return submit() if submit is not None else now
        time.sleep(min(wait, 0.25))
