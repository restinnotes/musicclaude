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
MIN_GAP = 7.0
_gap = threading.Lock(); _last = [0.0]; _logl = threading.Lock()


def rd(p):
    return Path(p).read_text(encoding="utf-8-sig")


def log(rec):
    with _logl:
        with (RUNS / "calls.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def find_job(text, t0, attach=()):
    """Match a gpt3 job dir by prompt text AND attachment hashes (identical prompts with different attachments
    run concurrently in the music check, so text alone is ambiguous)."""
    import hashlib as _h
    want = text.strip(); best = None
    want_sha = sorted(_h.sha256(Path(a).read_bytes()).hexdigest() for a in attach)
    for d in GPT3_RUNS.glob("pro-bridge-*"):
        try:
            if d.stat().st_mtime < t0 - 5:
                continue
            p = d / "prompt.txt"
            if p.exists() and p.read_text(encoding="utf-8-sig").strip() == want:
                if want_sha:
                    mf = d / "attachment-manifest.json"
                    got = sorted(x.get("sha256") for x in json.loads(mf.read_text(encoding="utf-8"))) if mf.exists() else []
                    if got != want_sha:
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


def call(run_id, message, prompt_text=None, attach=(), model=G6, meta=None):
    """One fresh gpt3 call. Returns response text or None."""
    d = RUNS / run_id; d.mkdir(parents=True, exist_ok=True)
    if done(run_id):
        return output(run_id)
    assert len(message) <= 65000, f"{run_id}: message too long ({len(message)})"
    (d / "prompt.txt").write_text(prompt_text if prompt_text is not None else message, encoding="utf-8")
    inp = d / "input.txt"; inp.write_text(message, encoding="utf-8")
    if meta:
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    for attempt in range(4):
        with _gap:
            w = MIN_GAP - (time.time() - _last[0])
            if w > 0:
                time.sleep(w)
            _last[0] = time.time()
        cmd = [GPT3, "ask", "--file", str(inp), "--json", "--model", model]
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
        job = md.get("job_directory") or find_job(message, t0, attach)
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
                    rec.update(completed=True, recovered_from_job=True, response_chars=len(rt))
                    (d / "call.log").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
                    (d / "output.txt").write_text(rt, encoding="utf-8"); log(rec)
                    print(f"[{run_id}] recovered from job {dt:.0f}s {len(rt)} chars", flush=True)
                    return rt
            except Exception:
                pass
        submitted = bool(job) and (Path(job) / "submitted.json").exists()
        rec["submitted"] = submitted; rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-800:]
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
