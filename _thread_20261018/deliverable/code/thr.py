"""Op.60 Thread / Inner / Outer research runner (all model work via local gpt3 / GPT Web).

Generic dependency-aware scheduler: tasks are registered as (stage, name) -> (fn, deps).
Cached under runs/<stage>/<name>.*; a task with parsed.json (or response.txt for prose tasks) is never redone.
A call that failed after submission is marked 'uncertain' and never resubmitted automatically.
Concurrency is read live from runs/parallel.txt.
"""
import hashlib, json, re, subprocess, sys, threading, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GPT3 = "D:/musicclaude/gpt2agent-safechain/bin/gpt3.cmd"
RUNS = ROOT / "runs"; RUNS.mkdir(exist_ok=True)
INP = ROOT / "inputs"
MIN_GAP = 6.0
G6, G56 = "gpt-6-thinking", "gpt-5-6-thinking"

STRUCT = json.loads((INP / "structure.json").read_text(encoding="utf-8"))
SEGS = {f"S{i+1:02d}": (mm, lab) for i, (mm, lab) in enumerate(STRUCT["frozen_segments"])}


def mm(seg):
    return SEGS[seg][0].replace("-", "–")


def load_T():
    return {p.stem: p.read_text(encoding="utf-8-sig") for p in sorted((INP / "T").glob("*.md"))}


def load_A():
    return {p.stem: p.read_text(encoding="utf-8-sig") for p in sorted((INP / "A").glob("*.md"))}


def bead(seg):
    return json.loads((INP / "beads" / f"{seg}.json").read_text(encoding="utf-8"))


def norm(s):
    return re.sub(r"[\s\*`“”\"'‘’「」『』《》，。、；：！？,.;:!?（）()\-—–…·]", "", s or "")


# ---------------- gpt3 ----------------
_gap = threading.Lock(); _last = [0.0]; _logl = threading.Lock()


def log(rec):
    with _logl:
        with (RUNS / "calls.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def call(stage, name, prompt_text, attach=(), session=None, model=G6):
    out = RUNS / stage; out.mkdir(parents=True, exist_ok=True)
    pf = out / f"{name}.prompt.txt"; pf.write_text(prompt_text, encoding="utf-8")
    assert len(prompt_text) <= 65000, f"{stage}/{name} prompt too long: {len(prompt_text)}"
    for attempt in range(2):
        with _gap:
            w = MIN_GAP - (time.time() - _last[0])
            if w > 0:
                time.sleep(w)
            _last[0] = time.time()
        cmd = [GPT3] + (["resume", session] if session else ["ask"]) + ["--file", str(pf), "--json", "--model", model]
        for a in attach:
            cmd += ["--attach", str(a)]
        t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S")
        cp = subprocess.run(cmd, capture_output=True)
        dt = time.time() - t0
        (out / f"{name}.stdout.bin").write_bytes(cp.stdout); (out / f"{name}.stderr.bin").write_bytes(cp.stderr)
        try:
            j = json.loads(cp.stdout.decode("utf-8"))
        except Exception:
            j = {}
        md = j.get("metadata") or {}
        job = md.get("job_directory")
        if not job:
            m = re.search(rb'"job_directory":\s*"((?:[^"\\]|\\.)*)"', cp.stdout + cp.stderr)
            job = json.loads(b'"' + m.group(1) + b'"') if m else None
        if not job:
            job = find_job(prompt_text, t0)
        ok = cp.returncode == 0 and j.get("completed") is True and j.get("response")
        rec = {"stage": stage, "name": name, "attempt": attempt, "started": started, "seconds": round(dt),
               "rc": cp.returncode, "completed": bool(ok), "model": md.get("model"), "effort": md.get("thinking_effort"),
               "temporary": md.get("temporary"), "unpersonalized": md.get("unpersonalized"),
               "policy_verified": md.get("generation_policy_verified"), "resume": bool(session),
               "session_handle": md.get("session_handle"), "job": job, "prompt_chars": len(prompt_text),
               "prompt_sha256": hashlib.sha256(prompt_text.encode()).hexdigest(), "attach": [str(a) for a in attach]}
        if ok:
            if md.get("model") != model or md.get("thinking_effort") != "max" or not md.get("temporary") or not md.get("unpersonalized"):
                rec["completed"] = False; rec["why"] = "policy mismatch"; log(rec)
                print(f"[{stage}/{name}] POLICY MISMATCH {md.get('model')}/{md.get('thinking_effort')}", flush=True)
                return None
            resp = j["response"]; rec["response_chars"] = len(resp); log(rec)
            (out / f"{name}.response.txt").write_text(resp, encoding="utf-8")
            (out / f"{name}.meta.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[{stage}/{name}] ok {dt:.0f}s {len(resp)} chars", flush=True)
            return resp, md.get("session_handle")
        submitted = bool(job) and (Path(job) / "submitted.json").exists()
        rec["submitted"] = submitted; rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-600:]
        log(rec)
        print(f"[{stage}/{name}] FAILED rc={cp.returncode} {dt:.0f}s submitted={submitted} job={job}", flush=True)
        # Retry only when we positively know nothing was submitted (job dir found without submitted.json).
        if submitted or not job:
            (out / f"{name}.uncertain.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
            return None
        time.sleep(45)
    return None


GPT3_RUNS = Path("D:/musicclaude/gpt2agent-safechain/runs/gpt3")
GEM = "gemini-3.8-flash-high"
OPENCODE = r"C:\Users\zuoyi\AppData\Local\Programs\@openchamberelectron\resources\opencode-cli\opencode.exe"
_gem_sem = threading.Semaphore(4)  # antigravity-tools proxy: keep Gemini concurrency modest


def call_gemini(stage, name, prompt_text):
    """Gemini 3.8 Flash (high) via opencode antigravity-tools provider; offline (permission deny), standalone server,
    model declared per call. Any tool use voids the answer. One attempt; failures are logged, never auto-resubmitted."""
    import os, tempfile
    out = RUNS / stage; out.mkdir(parents=True, exist_ok=True)
    pf = out / f"{name}.prompt.txt"; pf.write_text(prompt_text, encoding="utf-8")
    cfg = {"permission": "deny", "provider": {"antigravity-tools": {"options": {"timeout": False}, "models": {GEM: {}}}}}
    env = dict(os.environ); env["OPENCODE_CONFIG_CONTENT"] = json.dumps(cfg)
    cwd = tempfile.mkdtemp(prefix="gem_")
    with _gem_sem:
        t0 = time.time(); started = time.strftime("%Y-%m-%dT%H:%M:%S")
        cp = subprocess.run([OPENCODE, "run", "--standalone", "--format", "json", "--model", "antigravity-tools/" + GEM],
                            input=prompt_text.encode("utf-8"), capture_output=True, cwd=cwd, env=env)
    dt = time.time() - t0
    (out / f"{name}.stdout.bin").write_bytes(cp.stdout); (out / f"{name}.stderr.bin").write_bytes(cp.stderr)
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
    if "尝试调取实时信息时遇到了格式异常" in resp:
        err = "proxy canned tool-error reply"
    ok = cp.returncode == 0 and resp and not err
    rec = {"stage": stage, "name": name, "attempt": 0, "started": started, "seconds": round(dt), "rc": cp.returncode,
           "completed": bool(ok), "model": GEM, "effort": "high", "route": "opencode/antigravity-tools", "offline": True,
           "error": err, "prompt_chars": len(prompt_text), "prompt_sha256": hashlib.sha256(prompt_text.encode()).hexdigest()}
    if ok:
        rec["response_chars"] = len(resp); log(rec)
        (out / f"{name}.response.txt").write_text(resp, encoding="utf-8")
        (out / f"{name}.meta.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{stage}/{name}] ok(gemini) {dt:.0f}s {len(resp)} chars", flush=True)
        return resp, None
    rec["stderr_tail"] = cp.stderr.decode("utf-8", "replace")[-600:]; log(rec)
    print(f"[{stage}/{name}] FAILED(gemini) rc={cp.returncode} {dt:.0f}s {err}", flush=True)
    (out / f"{name}.uncertain.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return None


def find_job(prompt_text, t0):
    """Locate the gpt3 evidence directory for this prompt (started after t0) when stdout did not report it."""
    want = prompt_text.strip()
    best = None
    for d in GPT3_RUNS.glob("pro-bridge-*"):
        try:
            if d.stat().st_mtime < t0 - 5:
                continue
            p = d / "prompt.txt"
            if p.exists() and p.read_text(encoding="utf-8-sig").strip() == want:
                if best is None or d.stat().st_mtime > best.stat().st_mtime:
                    best = d
        except Exception:
            pass
    return str(best) if best else None


def parse_json(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S)
    txt = m[-1] if m else resp
    try:
        return json.loads(txt)
    except Exception:
        return json.loads(txt[txt.find("{"): txt.rfind("}") + 1])


def save(stage, name, d):
    (RUNS / stage / f"{name}.parsed.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def load(stage, name):
    p = RUNS / stage / f"{name}.parsed.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def text(stage, name):
    p = RUNS / stage / f"{name}.response.txt"
    return p.read_text(encoding="utf-8") if p.exists() else None


def handle(stage, name):
    p = RUNS / stage / f"{name}.meta.json"
    return json.loads(p.read_text(encoding="utf-8")).get("session_handle") if p.exists() else None


def finish_json(stage, name, r):
    if not r:
        return False
    try:
        save(stage, name, parse_json(r[0]))
        return True
    except Exception as e:
        print(f"[{stage}/{name}] PARSE ERROR {e}", flush=True)
        (RUNS / stage / f"{name}.parse_error.txt").write_text(str(e), encoding="utf-8")
        return False


def finish_text(stage, name, r):
    if not r:
        return False
    (RUNS / stage / f"{name}.done").write_text("ok", encoding="utf-8")
    return True


def zip_of(name, files):
    z = RUNS / f"{name}.zip"
    if not z.exists():
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
            for arc, content in files.items():
                f.writestr(arc, content)
    return z


# ---------------- scheduler ----------------
TASKS = {}  # (stage, name) -> (fn, deps, kind)


def task(stage, name, fn, deps=(), kind="json"):
    TASKS[(stage, name)] = (fn, list(deps), kind)


def done(stage, name):
    d = RUNS / stage
    return (d / f"{name}.parsed.json").exists() or (d / f"{name}.done").exists()


def blocked(stage, name):
    d = RUNS / stage
    return (d / f"{name}.uncertain.json").exists() or (d / f"{name}.parse_error.txt").exists()


def parallel():
    try:
        return int((RUNS / "parallel.txt").read_text().strip())
    except Exception:
        return 12


def run(keys):
    pending = {k for k in keys if not done(*k)}
    running, failed = set(), set(); lock = threading.Lock()

    def worker(k):
        ok = False
        try:
            ok = TASKS[k][0]()
        except Exception as e:
            print(f"[{k[0]}/{k[1]}] EXC {e!r}", flush=True)
        with lock:
            running.discard(k)
            if not ok:
                failed.add(k)

    while True:
        with lock:
            for k in list(pending):
                if blocked(*k):
                    pending.discard(k); failed.add(k)
            dead = [k for k in pending if any(d in failed for d in TASKS[k][1])]
            for k in dead:
                pending.discard(k); failed.add(k)
            ready = sorted(k for k in pending if all(done(*d) for d in TASKS[k][1]))
            launch = ready[:max(0, parallel() - len(running))]
            for k in launch:
                pending.discard(k); running.add(k)
            if not pending and not running:
                break
        for k in launch:
            threading.Thread(target=worker, args=(k,), daemon=True).start(); time.sleep(0.2)
        time.sleep(3)
    print("DONE; failed:", sorted(failed), flush=True)
    return failed
