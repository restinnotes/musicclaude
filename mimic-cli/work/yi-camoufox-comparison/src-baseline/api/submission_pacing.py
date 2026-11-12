"""One MimicGate instance's standard-send spacing, under its browser UI lock."""
import asyncio
import time

MIN_INTERVAL_SECONDS = 5.0
_last_attempt_monotonic = None

async def wait_for_submission_slot():
    delay = (max(0.0, MIN_INTERVAL_SECONDS - (time.monotonic() - _last_attempt_monotonic))
             if _last_attempt_monotonic is not None else 0.0)
    if delay:
        await asyncio.sleep(delay)
    return {'minimum_interval_seconds': MIN_INTERVAL_SECONDS, 'waited_seconds': round(delay, 3)}

def record_submission_attempt():
    global _last_attempt_monotonic
    now = time.monotonic()
    interval = now - _last_attempt_monotonic if _last_attempt_monotonic is not None else None
    _last_attempt_monotonic = now
    return {'send_attempt_at':time.time(),
            'previous_attempt_gap_seconds':round(interval,3) if interval is not None else None}
