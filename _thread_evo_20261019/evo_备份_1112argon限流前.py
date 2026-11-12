"""Thread prompt self-evolution: shared runner. Every model call goes through the local `gpt3` CLI.

Layout (per handoff spec): runs/<run_id>/{prompt.txt,input.txt,output.txt,call.log,stdout.bin,stderr.bin}
- prompt.txt  = the prompt-version text used (generation) or the judge/mutator instruction
- input.txt   = the exact full message body sent via `gpt3 ask --file`
- output.txt  = model response (only on verified success)
- call.log    = JSON: command, model evidence, timing, exit code, job dir (no credentials)
A run with output.txt is never redone. Any failure (submitted or not) is retried, up to 3 attempts (user 10-21: resubmitting is fine).
"""
import hashlib, json, re, subprocess, threading, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"; RUNS.mkdir(exist_ok=True)
PKG = ROOT / "inputs" / "pkg"
import os
ACCOUNT = os.environ.get("THREAD_GPT", "gpt3")      # gpt3 = default account, gpt4 = second account (user 10-21)
GPT3 = f"D:/musicclaude/gpt2agent-safechain/bin/{ACCOUNT}.cmd"
GPT3_RUNS = Path(f"D:/musicclaude/gpt2agent-safechain/runs/{ACCOUNT}")
G6, G56 = "gpt-6-thinking", "gpt-5-6-thinking"
ROUTE = os.environ.get("THREAD_ROUTE", "gpt3s")     # 10-27 default: gpt3 max via gpt3_call (spaced, locked); mimic = MimicGate High
MIN_GAP = 7.0
NO_WEB = "\n\n回答时请不要进行联网搜索。"


def want_no_web(meta):
    """11-02 user: "联网这个应该默认完全不管他才对吧 不给限制". Web is never restricted by default (10-27: drafts without web were
    clearly worse). The no-web suffix is added only on request: meta={"no_web": True} or MUSIC_NO_WEB=1."""
    return bool((meta or {}).get("no_web")) or os.environ.get("MUSIC_NO_WEB") == "1"

_gap = threading.Lock(); _last = [0.0]; _logl = threading.Lock()


def rd(p):
    return Path(p).read_text(encoding="utf-8-sig")


def log(rec):
    with _logl:
        with (RUNS / "calls.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def find_job(text, t0, attach=(), model=None):
    """Match prompt, all attachment hashes and the requested model.
    GPT-6/GPT-5.6 often review identical text concurrently; latest prompt alone is ambiguous.
    """
    import hashlib as _h
    want = text.strip(); best = None
    want_sha = sorted(_h.sha256(Path(a).read_bytes()).hexdigest() for a in attach)
    for d in GPT3_RUNS.glob("pro-bridge-*"):
        try:
            if d.stat().st_mtime < t0 - 5:
                continue
            p = d / "prompt.txt"
            if p.exists() and p.read_text(encoding="utf-8-sig").strip() == want:
                mf = d / "attachment-manifest.json"
                got = sorted(x.get("sha256") for x in json.loads(mf.read_text(encoding="utf-8"))) if mf.exists() else []
                if got != want_sha:
                    continue
                if model:
                    rp=d/'result.json'
                    if not rp.exists() or json.loads(rp.read_text(encoding='utf-8')).get('model')!=model:
                        continue
                if best is None or d.stat().st_mtime > best.stat().st_mtime:
                    best = d
        except Exception:
            pass
    return str(best) if best else None


def done(run_id):
    return (RUNS / run_id / "output.txt").exists()


def output(run_id):
    p = RUNS / run_id / "output.txt"
    return rd(p) if p.exists() else None


import threading as _threading
TL = _threading.local()   # 11-05: 每个线程可单独指定路由（并行时 gpt3、gpt4 分流），不改进程环境变量


def selected_route(model=G6):
    if getattr(TL, 'route', None): return TL.route
    return os.environ.get('THREAD_ROUTE_' + ('G6' if model == G6 else 'G56'),
                          os.environ.get('THREAD_ROUTE', ROUTE))


# 11-06 晚 用户：“就直接用gpt4啊 之后不要再问我 报异常就切换 两个都异常再说”“不要降低并发”。
# 账号级保护：某个账号报保护信号，就把它标成冷却 30 分钟（runs/{账号}_protected.json），之后的调用自动走另一个账号；
# 两个账号都在冷却时才全局停下（mg_schedule.fail）。
# 11-07 用户：“如果中间gpt3 gpt4出问题就等五十分钟再重试”。冷却改为 50 分钟；两个都在冷却时不再全局停，而是等到先恢复的那个再重试。
ACCT_COOL = 50 * 60


def _wait_both(run_id):
    import gpt3_call, gpt4_call
    ends = []
    for a in ('gpt3s', 'gpt4s'):
        try: ends.append(json.loads(_acct_file(a).read_text(encoding='utf-8')).get('until', 0))
        except (OSError, ValueError): ends.append(0)
    wait = max(0, min(ends) - time.time()) + 10
    print(f"[{run_id}] 两个账号都在冷却，等 {round(wait/60)} 分钟后重试", flush=True)
    time.sleep(wait)
    for m in (gpt3_call, gpt4_call):
        m._state.update(row=0, total=0, stop=None, last_error='')


def _acct_file(acct):
    return RUNS / f"{acct}_protected.json"


def acct_protected(acct):
    p = _acct_file(acct)
    try:
        return json.loads(p.read_text(encoding='utf-8')).get('until', 0) > time.time()
    except (OSError, ValueError):
        return False


def mark_protected(acct, run_id, why):
    _acct_file(acct).write_text(json.dumps({'until': time.time() + ACCT_COOL, 'run': run_id, 'why': str(why)[:300],
                                            'at': time.strftime('%Y-%m-%d %H:%M:%S')}, ensure_ascii=False), encoding='utf-8')
    with (RUNS / 'acct_switch_events.jsonl').open('a', encoding='utf-8') as h:
        h.write(json.dumps({'event': 'protected', 'acct': acct, 'run': run_id, 'why': str(why)[:300], 'at': time.time()}, ensure_ascii=False) + chr(10))
    print(f"[{run_id}] {acct} 报保护信号，冷却 50 分钟，之后的调用改走另一个账号", flush=True)


def _other(acct):
    return 'gpt4s' if acct == 'gpt3s' else 'gpt3s'


def check_submission(model=G6):
    """A transport outage is route-specific; explicit protection pauses all routes."""
    import mg_schedule
    state = mg_schedule.status()
    if state['cooling'] and (state.get('cooldown_kind') == 'suspicious_behavior'
                             or selected_route(model) == 'mimic'):
        mg_schedule.check()


def call(run_id, message, prompt_text=None, attach=(), model=G6, meta=None, cli_args=()):
    """One fresh gpt3 call. Returns response text or None."""
    d = RUNS / run_id; d.mkdir(parents=True, exist_ok=True)
    if done(run_id):
        return output(run_id)
    # 10-27: per-model override, e.g. THREAD_ROUTE_G6=gpt3s THREAD_ROUTE_G56=mimic. Long structured answers (pool / pick)
    # come back empty about half the time on MimicGate High, while gpt3 max finishes them.
    route = selected_route(model)
    if route in ('gpt3s', 'gpt4s'):
        if acct_protected(route):
            if acct_protected(_other(route)):
                _wait_both(run_id)
                return call(run_id, message, prompt_text, attach, model, meta, cli_args)
            route = _other(route)
    if route in ('mimic', 'gpt3s', 'gpt4s'):
        check_submission(model)
    if route == "mimic":
        import mg_call
        return mg_call.call(run_id, message, prompt_text, model, meta)
    if route == "nozomi":
        import nz_call
        return nz_call.call(run_id, message, prompt_text, model, meta)
    if route == "gpt4s":
        # 11-05 user: gpt4 账号修好了，和 gpt3 一起用。保护信号同样停下，不自动换路。
        import gpt4_call
        if gpt4_call.stopped() and not gpt4_call.protection_signal():
            gpt4_call.resume_transient()   # 普通失败不让 gpt4 一直停着
        r = gpt4_call.call(run_id, message, prompt_text, model, meta) if not gpt4_call.stopped() else None
        if r is not None:
            return r
        if gpt4_call.protection_signal():
            mark_protected('gpt4s', run_id, gpt4_call.stopped())
            if acct_protected('gpt3s'):
                _wait_both(run_id)
                return call(run_id, message, prompt_text, attach, model, meta, cli_args)
        # 普通的上游错误（如 UPSTREAM_STREAM_ERROR）或 gpt4 报保护：这次调用改走 gpt3
        print(f"[{run_id}] gpt4 失败，这次改走 gpt3", flush=True)
        route = "gpt3s"
    if route == "gpt3s":
        # 11-02 user: gpt3 first, MimicGate as backup for transport/availability
        # failures. Ordinary route backoff expires; protection never triggers failover.
        if acct_protected('gpt3s'):   # gpt4 失败转过来、但 gpt3 正在保护冷却
            if acct_protected('gpt4s'):
                _wait_both(run_id)
                return call(run_id, message, prompt_text, attach, model, meta, cli_args)
            print(f"[{run_id}] gpt3 在保护冷却，这次不调", flush=True)
            return None
        down = RUNS / "gpt3_down.txt"
        import gpt3_call
        if down.exists():
            try:
                state = json.loads(down.read_text(encoding='utf-8'))
            except (ValueError, OSError):
                state = {}  # Historical stop stays until an explicit user-authorized retry.
            if state.get('retry_after', float('inf')) <= time.time() and gpt3_call.resume_transient():
                with (RUNS / 'gpt3_route_events.jsonl').open('a', encoding='utf-8') as handle:
                    handle.write(json.dumps({'event': 'ordinary_backoff_expired', **state}, ensure_ascii=False)+'\n')
                down.unlink(missing_ok=True)
        if not down.exists():
            r = gpt3_call.call(run_id, message, prompt_text, model, meta)
            if r is not None or not gpt3_call.stopped():
                return r
            if gpt3_call.protection_signal():
                mark_protected('gpt3s', run_id, gpt3_call.stopped())
                if acct_protected('gpt4s'):
                    _wait_both(run_id)
                    return call(run_id, message, prompt_text, attach, model, meta, cli_args)
                print(f"[{run_id}] 这次改走 gpt4", flush=True)
                TL.route = 'gpt4s'
                try:
                    return call(run_id, message, prompt_text, attach, model, meta, cli_args)
                finally:
                    TL.route = None
            down.write_text(json.dumps({'reason': gpt3_call.stopped(), 'failed_at': time.time(),
                                        'retry_after': time.time()+60}, ensure_ascii=False), encoding='utf-8')
            print(f"[{run_id}] GPT3 unavailable -> MimicGate backup; retry primary after short backoff", flush=True)
        import mg_call
        return mg_call.call(run_id, message, prompt_text, model, meta)
    if route == "gpt2":
        import gpt2_call
        return gpt2_call.call(run_id, message, prompt_text, model, meta)
    # 10-24: when the model calls web.run, the rest of the answer moves to a websocket topic the bridge does not follow,
    # so the call ends INCOMPLETE_RESPONSE with only "thoughts" in the stream; none of these tasks needs the web.
    if want_no_web(meta) and NO_WEB.strip() not in message[-60:]:
        message += NO_WEB
    assert len(message) <= 65000, f"{run_id}: message too long ({len(message)})"
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    inp = d / "input.txt"; inp.write_text(message, encoding="utf-8")
    if meta:
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    for attempt in range(int(os.environ.get("EVO_ATTEMPTS", "4"))):   # long_wait.sh probes with 1 (one message per probe)
        with _gap:
            w = MIN_GAP - (time.time() - _last[0])
            if w > 0:
                time.sleep(w)
            _last[0] = time.time()
        cmd = [GPT3, "ask", "--file", str(inp), "--json", "--model", model]
        cmd += list(cli_args)
        for a in attach:
            cmd += ["--attach", str(a)]
        t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S")
        cp = subprocess.run(cmd, capture_output=True)
        dt = time.time() - t0
        (d / "stdout.bin").write_bytes(cp.stdout); (d / "stderr.bin").write_bytes(cp.stderr)
        try:
            j = json.loads(cp.stdout.decode("utf-8"))
        except Exception:
            j = {}
        md = j.get("metadata") or {}
        # The CLI writes structured transport errors to stderr, including the actual
        # submitted job. Losing this evidence mislabels a sent request as unsubmitted.
        err = {}
        for line in cp.stderr.decode('utf-8', 'replace').splitlines():
            try:
                candidate = json.loads(line)
                if isinstance(candidate, dict) and candidate.get('error_code'):
                    err = candidate
            except (ValueError, TypeError):
                pass
        job = md.get("job_directory") or err.get('job_directory') or find_job(message, t0, attach, model=model)
        ok = cp.returncode == 0 and j.get("completed") is True and bool(j.get("response"))
        rec = {"run_id": run_id, "attempt": attempt, "account": ACCOUNT, "command": " ".join([ACCOUNT] + cmd[1:]), "started": started,
               "seconds": round(dt), "exit_code": cp.returncode, "completed": bool(ok), "model": md.get("model"),
               "thinking_effort": md.get("thinking_effort"), "temporary": md.get("temporary"),
               "unpersonalized": md.get("unpersonalized"), "session_handle": md.get("session_handle"), "job_directory": job,
               "message_chars": len(message), "message_sha256": hashlib.sha256(message.encode()).hexdigest(),
               "attach": [str(a) for a in attach], "meta": meta or {}}
        if ok and (md.get("model") != model or md.get("thinking_effort") != "max"):
            ok = False; rec["completed"] = False; rec["why"] = "model/effort mismatch"
        if ok:
            resp = j["response"]; rec["response_chars"] = len(resp)
            (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            (d / "output.txt").write_text(resp, encoding="utf-8"); log(rec)
            print(f"[{run_id}] ok {dt:.0f}s {len(resp)} chars", flush=True)
            return resp
        if not ok and job and model:   # CLI verifier can reject a finished answer (probridge_incomplete_result): recover it
            try:
                rj = json.loads((Path(job) / "result.json").read_text(encoding="utf-8"))
                rt = (Path(job) / "response.txt").read_text(encoding="utf-8-sig")
                if str(rj.get("ok")) == "True" and rj.get("model") == model and str(rj.get("thinkingEffort")) == "max" and rt.strip():
                    rec.update(completed=True, recovered_from_job=True, response_chars=len(rt),
                               model=rj['model'], thinking_effort=rj['thinkingEffort'],
                               model_evidence='verified completed job result.json')
                    (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
                    (d / "output.txt").write_text(rt, encoding="utf-8"); log(rec)
                    print(f"[{run_id}] recovered from job {dt:.0f}s {len(rt)} chars", flush=True)
                    return rt
            except Exception:
                pass
        submitted = err.get('submitted') is True or (bool(job) and (Path(job) / "submitted.json").exists())
        rec["submitted"] = submitted; rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-800:]
        if err:
            rec.update(error_code=err.get('error_code'), error_type=err.get('error_type'))
        (d / f"call_fail_{attempt}.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8"); log(rec)
        print(f"[{run_id}] FAILED rc={cp.returncode} {dt:.0f}s submitted={submitted} job={job}", flush=True)
        msg429 = False
        try:
            msg429 = "429" in json.loads((Path(job) / "result.json").read_text(encoding="utf-8")).get("message", "")
        except Exception:
            pass
        time.sleep(600 if msg429 else 45)   # HTTP 429 = rate limited: back off 10 min
    return None


def run_parallel(jobs, workers=6):
    """jobs: list of (run_id, fn) where fn() performs the call. Returns {run_id: result}."""
    res = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(fn): rid for rid, fn in jobs}
        for f in futs:
            try:
                res[futs[f]] = f.result()
            except Exception as e:
                print(f"[{futs[f]}] EXC {e!r}", flush=True); res[futs[f]] = None
    return res


def parse_json(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S) or re.findall(r"<CodeBlock[^>]*>(.*?)(?:</CodeBlock>|$)", resp, re.S)
    txt = m[-1] if m else resp
    try:
        return json.loads(txt)
    except Exception:
        pass
    i = resp.rfind("```json")   # unclosed fence (model wrote `` instead of ```): take everything after it
    if i >= 0:
        tail = resp[i + 7:].strip().rstrip("`").strip()
        try:
            return json.loads(tail[tail.find("{"): tail.rfind("}") + 1])
        except Exception:
            pass
    try:
        return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])
    except Exception:
        # MimicGate copies an unfenced JSON answer as rendered Markdown: "&#x20;" for leading spaces and a "\" before every
        # line break (10-27). Undo only that rendering; a backslash before a newline is never valid JSON anyway.
        import html
        txt = re.sub(r"\\\r?\n", "\n", html.unescape(resp))
        return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])


# ---------- non-OpenAI judge: Gemini 3.8 Flash (high) via opencode antigravity-tools (offline) ----------
GEM = "gemini-3.8-flash-high"
OPENCODE = r"C:\Users\zuoyi\AppData\Local\Programs\@openchamberelectron\resources\opencode-cli\opencode.exe"
_gem_sem = threading.Semaphore(4)


def call_gemini(run_id, message, prompt_text=None, meta=None):
    import os, tempfile
    d = RUNS / run_id; d.mkdir(parents=True, exist_ok=True)
    if done(run_id):
        return output(run_id)
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    (d / "input.txt").write_text(message, encoding="utf-8")
    cfg = {"permission": "deny", "provider": {"antigravity-tools": {"options": {"timeout": False}, "models": {GEM: {}}}}}
    env = dict(os.environ); env["OPENCODE_CONFIG_CONTENT"] = json.dumps(cfg)
    cwd = tempfile.mkdtemp(prefix="gem_")
    with _gem_sem:
        t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S")
        cp = subprocess.run([OPENCODE, "run", "--standalone", "--format", "json", "--model", "antigravity-tools/" + GEM],
                            input=message.encode("utf-8"), capture_output=True, cwd=cwd, env=env)
    dt = time.time() - t0
    (d / "stdout.bin").write_bytes(cp.stdout); (d / "stderr.bin").write_bytes(cp.stderr)
    texts, tools, err = [], [], None
    for line in cp.stdout.decode("utf-8", "replace").splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") == "error":
            err = json.dumps(obj.get("error"), ensure_ascii=False)
        part = obj.get("part") or {}
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            texts.append(part["text"])
        elif part.get("type") == "tool" and (part.get("state") or {}).get("status") == "completed":
            tools.append(part.get("tool"))
    resp = "\n\n".join(t.strip() for t in texts if t.strip())
    if tools:
        err = f"tools used: {tools}"
    ok = cp.returncode == 0 and resp and not err
    rec = {"run_id": run_id, "command": f"opencode run --standalone --format json --model antigravity-tools/{GEM}",
           "started": started, "seconds": round(dt), "exit_code": cp.returncode, "completed": bool(ok), "model": GEM,
           "offline": True, "error": err, "message_chars": len(message), "meta": meta or {}}
    if ok:
        rec["response_chars"] = len(resp)
        (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / "output.txt").write_text(resp, encoding="utf-8"); log(rec)
        print(f"[{run_id}] ok(gemini) {dt:.0f}s {len(resp)} chars", flush=True)
        return resp
    rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-600:]; log(rec)
    (d / "call_fail.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{run_id}] FAILED(gemini) rc={cp.returncode} {dt:.0f}s {err}", flush=True)
    return None


def call_gemini_direct(run_id, message, prompt_text=None, meta=None, model_name="gemini-3.8-flash-high"):
    """Gemini via the local Antigravity Tools proxy, non-streaming OpenAI-compatible HTTP (no tools, so offline by
    construction). Bypasses opencode, whose streaming parser fails on this proxy ('content after the finish reason')."""
    import os, urllib.request
    d = RUNS / run_id; d.mkdir(parents=True, exist_ok=True)
    if done(run_id):
        return output(run_id)
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    (d / "input.txt").write_text(message, encoding="utf-8")
    cfg = json.loads(Path(os.path.expanduser("~/.config/opencode/opencode.json")).read_text(encoding="utf-8"))
    o = cfg["provider"]["antigravity-tools"]["options"]
    body = json.dumps({"model": model_name, "messages": [{"role": "user", "content": message}], "stream": False}).encode()
    req = urllib.request.Request(o["baseURL"] + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + o["apiKey"]})
    t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S"); err = None; resp = ""
    with _gem_sem:
        try:
            j = json.loads(urllib.request.urlopen(req, timeout=1200).read().decode("utf-8"))
            resp = (j["choices"][0]["message"].get("content") or "").strip()
            fr = j["choices"][0].get("finish_reason")
            if fr not in ("stop", None):
                err = f"finish_reason={fr}"
        except Exception as e:
            err = repr(e)[:500]
    dt = time.time() - t0
    ok = bool(resp) and not err
    rec = {"run_id": run_id, "command": f"POST {o['baseURL']}/chat/completions (stream=false)", "started": started,
           "seconds": round(dt), "completed": ok, "model": model_name, "offline": True, "error": err,
           "message_chars": len(message), "meta": meta or {}}
    if ok:
        rec["response_chars"] = len(resp)
        (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / "output.txt").write_text(resp, encoding="utf-8"); log(rec)
        print(f"[{run_id}] ok(gemini-direct) {dt:.0f}s {len(resp)} chars", flush=True)
        return resp
    log(rec); (d / "call_fail_direct.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[{run_id}] FAILED(gemini-direct) {dt:.0f}s {err}", flush=True)
    return None

def call_argon_direct(run_id, message, prompt_text=None, meta=None, model_name="gemini-4-argon(high)"):
    """10-31: Gemini 4 Argon via the local AIStudio2API (http://127.0.0.1:2048, config ~/.argon/config.json; the user's
    `argon ask` wraps the same endpoint). Rewriter only, never a judge; the user allows about 100 calls in total.
    Start the service first with `argon ask "hi"` if it is down."""
    import os, urllib.request
    d = RUNS / run_id; d.mkdir(parents=True, exist_ok=True)
    if done(run_id):
        return output(run_id)
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    (d / "input.txt").write_text(message, encoding="utf-8")
    cfg = json.loads(Path(os.path.expanduser("~/.argon/config.json")).read_text(encoding="utf-8"))
    body = json.dumps({"model": model_name, "messages": [{"role": "user", "content": message}], "stream": False}).encode()
    req = urllib.request.Request(cfg["base_url"].rstrip("/") + "/v1/chat/completions", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + cfg["api_key"]})
    t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S"); err = None; resp = ""
    try:
        j = json.loads(urllib.request.urlopen(req, timeout=1200).read().decode("utf-8"))
        resp = (j["choices"][0]["message"].get("content") or "").strip()
        fr = j["choices"][0].get("finish_reason")
        if fr not in ("stop", None):
            err = f"finish_reason={fr}"
    except Exception as e:
        err = repr(e)[:500]
    ok = bool(resp) and not err
    rec = {"run_id": run_id, "command": "POST argon /v1/chat/completions", "started": started, "seconds": round(time.time() - t0),
           "completed": ok, "model": model_name, "offline": True, "error": err, "message_chars": len(message), "meta": meta or {}}
    (d / "meta.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(RUNS.parent / "argon_calls.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[{run_id}] {'ok(argon)' if ok else 'FAILED(argon)'} {round(time.time() - t0)}s {len(resp)} chars {err or ''}", flush=True)
    if ok:
        (d / "output.txt").write_text(resp, encoding="utf-8")
        return resp
    return None
