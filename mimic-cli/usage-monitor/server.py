from __future__ import annotations

import copy
import json
import os
import queue
import subprocess
import threading
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.html"
STATE_FILE = ROOT / "mimicgate-usage-state.json"
API_URL = "http://127.0.0.1:8652/v1/gateway/activity"
CONTAINER = "yi-mimicgate-20261002"
WEEKLY_LIMIT = 3000
POLL_INTERVAL_SECONDS = 1.0


def _creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _read_api_token() -> str:
    # Read the active token from this Docker container into memory only.
    code = "from src.config import Config; import sys; sys.stdout.write(Config.API_TOKEN)"
    try:
        result = subprocess.run(
            ["docker", "exec", "-w", "/app", CONTAINER,
             "/opt/venv/bin/python", "-c", code],
            capture_output=True, text=True, timeout=15,
            creationflags=_creation_flags(),
        )
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError("docker_auth_unavailable") from None
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("docker_auth_unavailable")
    return result.stdout.strip()


def _container_identity() -> tuple[str, str, float | None]:
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.Id}}|{{.State.StartedAt}}", CONTAINER],
            capture_output=True, text=True, timeout=10,
            creationflags=_creation_flags(),
        )
    except (OSError, subprocess.TimeoutExpired):
        return "", "", None
    if result.returncode != 0:
        return "", "", None
    parts = result.stdout.strip().split("|", 1)
    if len(parts) != 2:
        return "", "", None
    container_id, started_at = parts
    try:
        stamp = datetime.fromisoformat(started_at.replace("Z", "+00:00")).timestamp()
    except (ValueError, OverflowError):
        stamp = None
    return container_id, started_at, stamp


def _fetch_activity(token: str) -> dict:
    request = urllib.request.Request(
        API_URL,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
        method="GET",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"gateway_http_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, UnicodeError):
        raise RuntimeError("gateway_unavailable") from None
    if not isinstance(data, dict) or not isinstance(data.get("summary"), dict):
        raise RuntimeError("gateway_invalid_activity")
    return data


def _as_int(value, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _as_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _normalize_requests(rows: object) -> list[dict]:
    result = []
    if not isinstance(rows, list):
        return result
    for row in rows:
        if not isinstance(row, dict):
            continue
        req_id = str(row.get("id") or "")
        try:
            seq = int(req_id.rsplit("-", 1)[-1])
            ts = float(row.get("timestamp"))
            status = int(row.get("status_code", 0))
        except (TypeError, ValueError, OverflowError):
            continue
        # Deliberately keep metadata only. Never persist prompt, payload,
        # response preview, client IP, or any authentication material.
        result.append({
            "id": req_id,
            "seq": seq,
            "ts": ts,
            "status_code": status,
            "model": str(row.get("model") or "default")[:120],
        })
    return result


def _event(ts: float, count: int, successes: int, failures: int,
           model: str = "", request_id: str = "", estimated: bool = False) -> dict:
    count = max(0, int(count))
    successes = max(0, min(count, int(successes)))
    failures = max(0, min(count - successes, int(failures)))
    if successes + failures < count:
        successes += count - successes - failures
    return {
        "ts": float(ts), "count": count, "successes": successes,
        "failures": failures, "model": str(model)[:120],
        "request_id": str(request_id)[:80], "estimated_time": bool(estimated),
    }


class ActivityMonitor:
    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.subscriber_lock = threading.Lock()
        self.subscribers: set[queue.Queue] = set()
        self.token = ""
        self.state = self._load_state()
        self.latest_summary: dict = {}
        self.available = False
        self.last_error = "starting"
        self.last_poll_at = 0.0
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None

    @staticmethod
    def _load_state() -> dict | None:
        try:
            value = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(value, dict) and value.get("schema_version") == 1:
                value.setdefault("events", [])
                return value
        except (OSError, ValueError, TypeError):
            pass
        return None

    def _save_locked(self) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        os.replace(tmp, STATE_FILE)

    def _append_locked(self, ts: float, count: int, successes: int, failures: int,
                       model: str = "", request_id: str = "", estimated: bool = False) -> None:
        if count <= 0:
            return
        self.state.setdefault("events", []).append(
            _event(ts, count, successes, failures, model, request_id, estimated)
        )

    def _publish(self, message: dict) -> None:
        with self.subscriber_lock:
            subscribers = list(self.subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(message)
            except queue.Full:
                try:
                    subscriber.get_nowait()
                    subscriber.put_nowait(message)
                except (queue.Empty, queue.Full):
                    pass

    def add_subscriber(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=64)
        with self.subscriber_lock:
            self.subscribers.add(q)
        return q

    def remove_subscriber(self, q: queue.Queue) -> None:
        with self.subscriber_lock:
            self.subscribers.discard(q)

    def _new_epoch_locked(self, summary: dict, rows: list[dict],
                          container_id: str, started_at: str, started_ts: float | None,
                          now: float, bootstrap: bool) -> list[dict]:
        total = _as_int(summary.get("total_requests"))
        successful = _as_int(summary.get("successful_requests"))
        failed = _as_int(summary.get("failed_requests"))
        rows = sorted((r for r in rows if 0 < r["seq"] <= total), key=lambda r: r["seq"])
        known_success = sum(1 for r in rows if 200 <= r["status_code"] < 400)
        known_failed = len(rows) - known_success
        missing = max(0, total - len(rows))
        missing_success = max(0, successful - known_success)
        missing_failed = max(0, failed - known_failed)
        epoch_start = started_ts if started_ts is not None else now
        if missing:
            self._append_locked(epoch_start, missing, missing_success, missing_failed,
                                "container-start baseline", "", False)
        for row in rows:
            ok = 200 <= row["status_code"] < 400
            self._append_locked(row["ts"], 1, int(ok), int(not ok), row["model"], row["id"])
        if not bootstrap:
            self.state["total_all"] = _as_int(self.state.get("total_all")) + total
            self.state["successful_all"] = _as_int(self.state.get("successful_all")) + successful
            self.state["failed_all"] = _as_int(self.state.get("failed_all")) + failed
        else:
            self.state["total_all"] = total
            self.state["successful_all"] = successful
            self.state["failed_all"] = failed
            local_today = datetime.now().astimezone().date()
            start_day = datetime.fromtimestamp(epoch_start).astimezone().date()
            self.state["history_note"] = (
                "" if start_day == local_today else
                "首次接入时 Docker 已运行跨日；启动前的逐日分布不能由运行态接口完整还原。"
            )
            self.state["coverage_started_at"] = now
        self.state["container_id"] = container_id
        self.state["container_started_at"] = started_at
        self.state["last_total"] = total
        self.state["last_successful"] = successful
        self.state["last_failed"] = failed
        self.state["last_seq"] = total
        self.state["event_detail_gaps"] = _as_int(self.state.get("event_detail_gaps")) + (missing if not bootstrap else 0)
        return rows

    def _apply(self, data: dict, container_id: str, started_at: str,
               started_ts: float | None, now: float) -> None:
        summary = data.get("summary", {})
        rows = _normalize_requests(data.get("requests", []))
        total = _as_int(summary.get("total_requests"))
        successful = _as_int(summary.get("successful_requests"))
        failed = _as_int(summary.get("failed_requests"))
        published = []
        with self.lock:
            if self.state is None:
                self.state = {
                    "schema_version": 1, "events": [], "total_all": 0,
                    "successful_all": 0, "failed_all": 0,
                    "event_detail_gaps": 0, "history_note": "",
                }
                self._new_epoch_locked(summary, rows, container_id, started_at,
                                       started_ts, now, bootstrap=True)
            else:
                s = self.state
                previous_total = _as_int(s.get("last_total"))
                previous_success = _as_int(s.get("last_successful"))
                previous_failed = _as_int(s.get("last_failed"))
                previous_seq = _as_int(s.get("last_seq"))
                current_seq = max((r["seq"] for r in rows), default=total)
                new_epoch = (
                    (started_at and s.get("container_started_at") and started_at != s.get("container_started_at"))
                    or total < previous_total
                    or successful < previous_success
                    or failed < previous_failed
                    or (current_seq > 0 and previous_seq > 0 and current_seq < previous_seq)
                )
                if new_epoch:
                    epoch_ts = started_ts
                    if not started_at or started_at == s.get("container_started_at"):
                        epoch_ts = now
                    self._new_epoch_locked(summary, rows, container_id, started_at,
                                           epoch_ts, now, bootstrap=False)
                elif total > previous_total:
                    delta = total - previous_total
                    fresh = [r for r in rows if previous_seq < r["seq"] <= total]
                    fresh.sort(key=lambda r: r["seq"])
                    if len(fresh) > delta:
                        fresh = fresh[-delta:]
                    success_delta = max(0, successful - previous_success)
                    failed_delta = max(0, failed - previous_failed)
                    known_success = 0
                    known_failed = 0
                    for row in fresh:
                        ok = 200 <= row["status_code"] < 400
                        known_success += int(ok)
                        known_failed += int(not ok)
                        self._append_locked(row["ts"], 1, int(ok), int(not ok), row["model"], row["id"])
                        published.append({
                            "type": "turn", "user": "MimicGate Docker",
                            "model": row["model"], "conversation_id": row["id"],
                            "ts": row["ts"], "status_code": row["status_code"],
                        })
                    missing = max(0, delta - len(fresh))
                    if missing:
                        miss_success = max(0, success_delta - known_success)
                        miss_failed = max(0, failed_delta - known_failed)
                        self._append_locked(now, missing, miss_success, miss_failed,
                                            "missed detail", "", True)
                        s["event_detail_gaps"] = _as_int(s.get("event_detail_gaps")) + missing
                    s["total_all"] = _as_int(s.get("total_all")) + delta
                    s["successful_all"] = _as_int(s.get("successful_all")) + success_delta
                    s["failed_all"] = _as_int(s.get("failed_all")) + failed_delta
                    s["last_total"] = total
                    s["last_successful"] = successful
                    s["last_failed"] = failed
                    s["last_seq"] = total
                s["container_id"] = container_id or s.get("container_id", "")
                if started_at:
                    s["container_started_at"] = started_at
            cutoff = now - 31 * 86400
            self.state["events"] = [e for e in self.state.get("events", [])
                                     if _as_float(e.get("ts")) >= cutoff]
            self.latest_summary = {
                k: summary[k] for k in (
                    "total_requests", "successful_requests", "failed_requests",
                    "success_rate_percent", "avg_latency_ms", "in_flight"
                ) if k in summary
            }
            self.available = True
            self.last_error = ""
            self.last_poll_at = now
            self._save_locked()
        for message in published:
            self._publish(message)

    def poll_once(self) -> None:
        try:
            if not self.token:
                self.token = _read_api_token()
            container_id, started_at, started_ts = _container_identity()
            data = _fetch_activity(self.token)
            self._apply(data, container_id, started_at, started_ts, time.time())
        except Exception as exc:
            # Keep only the error class; never log HTTP bodies or credentials.
            with self.lock:
                self.available = False
                self.last_error = type(exc).__name__
                self.last_poll_at = time.time()

    def start(self) -> None:
        self.poll_once()
        self.thread = threading.Thread(target=self._poll_loop, name="mimicgate-activity-poller", daemon=True)
        self.thread.start()

    def _poll_loop(self) -> None:
        while not self.stop_event.wait(POLL_INTERVAL_SECONDS):
            self.poll_once()

    def stop(self) -> None:
        self.stop_event.set()

    def stats(self) -> dict:
        now = time.time()
        now_dt = datetime.now().astimezone()
        today_start = now_dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        week_start = (now_dt.replace(hour=0, minute=0, second=0, microsecond=0)
                      - timedelta(days=now_dt.weekday())).timestamp()
        rolling_start = now - 7 * 86400
        with self.lock:
            state = copy.deepcopy(self.state) if self.state is not None else {
                "events": [], "total_all": 0, "successful_all": 0, "failed_all": 0,
                "event_detail_gaps": 0, "history_note": "MimicGate 数据尚未连接。",
            }
            summary = dict(self.latest_summary)
            available = self.available
            error = self.last_error
            last_poll_at = self.last_poll_at
        counts = {"today": [0, 0, 0], "week": [0, 0, 0], "rolling_7d": [0, 0, 0]}
        daily = defaultdict(lambda: [0, 0, 0])
        all_events = state.get("events", [])
        for event in all_events:
            ts = _as_float(event.get("ts"))
            n = _as_int(event.get("count"))
            ok = _as_int(event.get("successes"))
            bad = _as_int(event.get("failures"))
            local_day = datetime.fromtimestamp(ts).astimezone().strftime("%Y-%m-%d")
            daily[local_day][0] += n
            daily[local_day][1] += ok
            daily[local_day][2] += bad
            if ts >= today_start:
                for i, v in enumerate((n, ok, bad)): counts["today"][i] += v
            if ts >= week_start:
                for i, v in enumerate((n, ok, bad)): counts["week"][i] += v
            if ts >= rolling_start:
                for i, v in enumerate((n, ok, bad)): counts["rolling_7d"][i] += v
        limit = WEEKLY_LIMIT
        t = counts["today"][0]
        w = counts["week"][0]
        r = counts["rolling_7d"][0]
        total_all = _as_int(state.get("total_all"))
        start_date = now_dt.date() - timedelta(days=29)
        earliest = min((datetime.strptime(d, "%Y-%m-%d").date() for d in daily), default=now_dt.date())
        num_days = max(7, min(30, (now_dt.date() - max(start_date, earliest)).days + 1))
        begin = now_dt.date() - timedelta(days=num_days - 1)
        bars = []
        peak, peak_date, sum_recent, nonzero = 0, now_dt.strftime("%Y-%m-%d"), 0, 0
        names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        day = begin
        while day <= now_dt.date():
            key = day.strftime("%Y-%m-%d")
            values = daily.get(key, [0, 0, 0])
            n, ok, bad = values
            if n > peak:
                peak, peak_date = n, key
            if n:
                nonzero += 1
            sum_recent += n
            bars.append({
                "date": key, "label": day.strftime("%m-%d"), "weekday": names[day.weekday()],
                "is_today": day == now_dt.date(), "is_weekend": day.weekday() >= 5,
                "total": n, "gateway": ok, "external": bad, "projects": {},
            })
            day += timedelta(days=1)
        daily_stats = {
            "bars": bars, "peak_total": peak, "peak_date": peak_date,
            "sum_recent": sum_recent,
            "avg_daily": round(sum_recent / max(nonzero, 1), 1) if nonzero else 0.0,
            "days_count": len(bars),
        }
        return {
            "timezone": str(now_dt.tzname() or ""),
            "local_now": now_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "limit_per_week": limit,
            "total_today": t, "total_week": w, "total_rolling_7d": r,
            "total_all": total_all,
            "remaining_week": max(limit - w, 0),
            "remaining_rolling_7d": max(limit - r, 0),
            "used_pct_week": round(w / limit * 100, 2) if limit else 0.0,
            "used_pct_rolling_7d": round(r / limit * 100, 2) if limit else 0.0,
            "per_user": [{
                "user": "MimicGate Docker", "today": t, "week": w,
                "rolling_7d": r, "total": total_all,
            }],
            "per_project": [],
            "sources": {
                "gateway": {"today": counts["today"][1], "week": counts["week"][1],
                            "rolling_7d": counts["rolling_7d"][1],
                            "total": _as_int(state.get("successful_all"))},
                "external": {"today": counts["today"][2], "week": counts["week"][2],
                             "rolling_7d": counts["rolling_7d"][2],
                             "total": _as_int(state.get("failed_all"))},
            },
            "daily_stats": daily_stats,
            "backend": "mimicgate-yi-docker",
            "counter_scope": "All request records from current yi MimicGate Docker telemetry; successful and failed requests are counted.",
            "limit_source": "Local display threshold, not an account quota.",
            "gateway_runtime": {**summary, "available": available},
            "container_started_at": state.get("container_started_at", ""),
            "coverage_started_at": state.get("coverage_started_at", 0),
            "history_note": state.get("history_note", ""),
            "event_detail_gaps": _as_int(state.get("event_detail_gaps")),
            "last_error": error,
            "last_poll_at": last_poll_at,
            "storage": str(STATE_FILE),
            "generated_at": now,
        }


monitor = ActivityMonitor()


class Handler(BaseHTTPRequestHandler):
    server_version = "MimicGateUsageMonitor/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send_json(self, value: dict, status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/":
            try:
                body = INDEX_FILE.read_bytes()
            except OSError:
                self.send_error(500)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        elif path == "/health":
            stats = monitor.stats()
            self._send_json({"status": "ok" if stats["gateway_runtime"].get("available") else "degraded",
                             "service": "usage-monitor", "backend": stats["backend"]},
                            200 if stats["gateway_runtime"].get("available") else 503)
        elif path == "/api/stats":
            self._send_json(monitor.stats())
        elif path == "/api/events":
            self._handle_events()
        else:
            self.send_error(404)

    def _handle_events(self) -> None:
        subscriber = monitor.add_subscriber()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        try:
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while True:
                try:
                    event = subscriber.get(timeout=15)
                    payload = "data: " + json.dumps(event, ensure_ascii=False) + "\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                except queue.Empty:
                    self.wfile.write(b": heartbeat\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            monitor.remove_subscriber(subscriber)


def main() -> None:
    monitor.start()
    server = ThreadingHTTPServer(("127.0.0.1", 9101), Handler)
    server.daemon_threads = True
    server.serve_forever(poll_interval=0.5)


if __name__ == "__main__":
    main()