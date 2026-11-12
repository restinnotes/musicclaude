"""MimicGate route for evo.call (10-26, user: only the mimicgate web, High, up to 5 in parallel).
Each attempt is one request file in the yi container spool, sent once by the container-side receiver.py
(Temporary + Unpersonalized, model verified before Send); this side only polls result.json.
Same runs/<run_id>/ layout as evo.call: output.txt only on a verified complete answer."""
import hashlib, json, subprocess, threading, time
import evo
import mg_schedule

CONTAINER = "yi-mimicgate-20261002"
SPOOL = "/app/state/music-result-spool-v1"
MODEL = {evo.G6: "gpt-6", evo.G56: "gpt-5.6-sol"}
SLOTS = threading.Semaphore(int(__import__("os").environ.get("MG_SLOTS", "5")))     # 10-28: run with MG_SLOTS=3


class _GlobalSlot:
    """11-01: MG_SLOTS is per process; parallel chains and measurements stacked up to ~20 in flight. This caps in-flight
    MimicGate calls across all processes on the machine (MG_GLOBAL, default 10) with one lock file per slot."""
    def __enter__(self):
        import os, msvcrt
        from pathlib import Path
        n = int(os.environ.get("MG_GLOBAL", "10")); d = Path(__file__).parent / "runs" / "_mg_slots"; d.mkdir(parents=True, exist_ok=True)
        while True:
            mg_schedule.check()
            for i in range(n):
                f = open(d / f"slot{i}.lock", "a+")
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1); self.f = f; return self
                except OSError:
                    f.close()
            time.sleep(5)

    def __exit__(self, *a):
        import msvcrt
        try:
            self.f.seek(0); msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
        finally:
            self.f.close()
FAST = 60          # user rule: a substantive answer much faster than history is suspect -> cup probe
# 11-02 user correction: half-hour pause only for explicit suspicious behavior;
# ordinary gateway/transport failures use mg_schedule's short retry delay.


def docker(*args):
    return subprocess.run(["docker", *args], capture_output=True, text=True, encoding="utf-8",
                          env={**__import__("os").environ, "MSYS_NO_PATHCONV": "1"}, check=True).stdout


def verified(r, model):
    body = r.get("body") or {}; dg = body.get("mimicgate_diagnostics") or {}; m = dg.get("model") or {}
    ch = (body.get("choices") or [{}])[0]; ans = (ch.get("message") or {}).get("content") or ""
    ok = (r.get("http_status") == 200 and not body.get("error") and not body.get("partial_response")
          and (dg.get("temporary_chat") or {}).get("verified") is True and (dg.get("non_personalized") or {}).get("verified") is True
          and dg.get("prompt_content_verified") is True and dg.get("response_complete") is True
          and m.get("model") == model and m.get("selected_effort") == "high" and ch.get("finish_reason") == "stop" and ans.strip())
    return bool(ok), ans, dg


def poll(directory, limit=1800):
    """10-31: give up after `limit` s (a receiver killed by a gateway restart never writes result.json; the old loop
    waited forever) -> counted as a failed attempt and retried."""
    t0 = time.time()
    while True:
        time.sleep(10)
        if time.time() - t0 > limit:
            return {"error": {"kind": "client", "message": f"no result.json after {limit}s (receiver gone)"}}
        txt = docker("exec", CONTAINER, "python", "-c",
                     f"from pathlib import Path;p=Path('{directory}/result.json');print(p.read_text() if p.exists() else 'null')")
        r = json.loads(txt)
        if r is not None:
            return r


def pending(run_id, message):
    """A request this run already handed to the container (caller killed): poll it instead of sending again."""
    f = evo.RUNS / run_id / "mg_request.json"
    req = json.loads(f.read_text(encoding="utf-8"))
    if req.get("prompt") != message:
        return None
    # A failure from an older remote attempt says nothing about the latest receiver.
    for failed in (evo.RUNS / run_id).glob("call_fail_*.log"):
        if json.loads(failed.read_text(encoding="utf-8")).get("remote_id") == req["remote_id"]:
            return None
    directory = f"{SPOOL}/{req['remote_id']}"
    if docker("exec", CONTAINER, "sh", "-c", f"test -f {directory}/request.json && echo y || echo n").strip() != "y":
        return None
    alive = docker("exec", CONTAINER, "sh", "-c", f"test -f {directory}/result.json && echo y || (ps aux | grep -c '[r]eceiver.py {directory}'; true)").strip()
    if alive in ("0", ""):          # Receiver died: record failure/cool down before any retry.
        return req["remote_id"], {"error": {"kind": "receiver_gone", "message": "submitted request has no receiver or result"}}
    return req["remote_id"], poll(directory)


def busy(r):
    """Gateway queue timeout (HTTP 429, kind busy): nothing reached the model, so it is not a failed attempt."""
    e = json.dumps((r.get("body") or {}).get("error") or r.get("error") or {}, ensure_ascii=False).lower()
    return r.get("http_status") == 429 and "busy" in e


def once(run_id, attempt, message, model):
    rid = hashlib.sha256(f"{run_id}\n{attempt}\n{time.time()}".encode()).hexdigest()[:20]
    d = evo.RUNS / run_id; directory = f"{SPOOL}/{rid}"
    req = {"key": f"{run_id}#{attempt}", "model": model, "effort": "high", "prompt": message,
           "prompt_sha256": hashlib.sha256(message.encode()).hexdigest(), "remote_id": rid}
    (d / "mg_request.json").write_text(json.dumps(req, ensure_ascii=False), encoding="utf-8")
    docker("exec", CONTAINER, "mkdir", "-p", directory)
    docker("cp", str(d / "mg_request.json"), f"{CONTAINER}:{directory}/request.json")
    try:
        mg_schedule.reserve(run_id, submit=lambda: docker(
            "exec", "-d", "-w", "/app", CONTAINER, "/opt/venv/bin/python", f"{SPOOL}/receiver.py", directory))
    except mg_schedule.CoolingDown:
        # reserve raises before dispatch. Keep the prepared request as audit,
        # without making pending() mistake it for a lost live receiver.
        (d / "mg_request.json").replace(d / f"mg_unsubmitted_{rid}.json")
        raise
    return rid, poll(directory)


def call(run_id, message, prompt_text, model, meta):
    d = evo.RUNS / run_id
    if evo.want_no_web(meta) and evo.NO_WEB.strip() not in message[-60:]:
        message += evo.NO_WEB
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    (d / "input.txt").write_text(message, encoding="utf-8")
    if meta:
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    mg = MODEL[model]
    attempt = 0
    try:
        resumed = pending(run_id, message) if (d / "mg_request.json").exists() else None
    except Exception as e:
        state = mg_schedule.fail(run_id, repr(e))
        print(f"[{run_id}] pending collection failed; cooldown until {state['resume_after_utc']}", flush=True)
        return None
    while attempt < int(__import__("os").environ.get("MG_ATTEMPTS", "2")):     # 10-28: incomplete_response is a browser-side miss
        started = time.strftime("%Y-%m-%dT%H:%M:%S"); t0 = time.time()
        try:
            if resumed:
                rid, r = resumed  # collecting an existing answer needs no submission slot
            else:
                with SLOTS, _GlobalSlot():
                    rid, r = once(run_id, attempt, message, mg)
        except mg_schedule.CoolingDown as e:
            print(f"[{run_id}] SKIPPED ({e})", flush=True)
            return None
        except Exception as e:
            rid, r = None, {"error": {"kind": "client", "message": repr(e)[:300]}}
        resumed = None
        dt = time.time() - t0
        ok, ans, dg = verified(r, mg)
        rec = {"run_id": run_id, "attempt": attempt, "account": "mimicgate-yi", "route": "mimic", "started": started,
               "seconds": round(dt), "completed": ok, "model": mg, "thinking_effort": "high", "remote_id": rid,
               "http_status": r.get("http_status"), "receiver_seconds": r.get("seconds"),
               "message_chars": len(message), "message_sha256": hashlib.sha256(message.encode()).hexdigest(), "meta": meta or {}}
        if ok:
            rec["response_chars"] = len(ans)
            if len(message) > 3000 and dt < FAST:
                rec["fast"] = True; print(f"[{run_id}] FAST {dt:.0f}s -> cup probe", flush=True)
            (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "output.txt").write_text(ans, encoding="utf-8"); evo.log(rec)
            print(f"[{run_id}] ok {dt:.0f}s {len(ans)} chars", flush=True)
            return ans
        body = r.get("body") or {}
        rec["error"] = body.get("error") or r.get("error") or {"kind": "state_evidence"}
        partial = (((body.get("choices") or [{}])[0].get("message") or {}).get("content") or "") or str(body.get("partial_response") or "")
        if partial:
            partial_path = d / f"partial_{attempt}.txt"
            if partial_path.exists():
                partial_path = d / f"partial_{attempt}_{time.time_ns()}.txt"
            partial_path.write_text(partial, encoding="utf-8")
        failure_path = d / f"call_fail_{attempt}.log"
        if failure_path.exists():
            failure_path = d / f"call_fail_{attempt}_{time.time_ns()}.log"
        failure_path.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8"); evo.log(rec)
        print(f"[{run_id}] FAILED {dt:.0f}s {json.dumps(rec['error'], ensure_ascii=False)[:200]}", flush=True)
        # User correction: 30 minutes only for suspicious behavior; ordinary 502s
        # keep their evidence and use a short retry delay instead.
        state = mg_schedule.fail(run_id, json.dumps(rec["error"], ensure_ascii=False))
        print(f"MIMIC {state['cooldown_kind']} pause {state['cooldown_seconds']}s until {state['resume_after_utc']}", flush=True)
        return None
    return None
