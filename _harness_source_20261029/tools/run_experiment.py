# -*- coding: utf-8 -*-
"""Run one S01 Pool pilot and preserve prompt, raw stream, parsed output and trace.

    python tools\\run_experiment.py --harness opencode --model codex-proxy-azure/gpt-6-luna#max
    python tools\\run_experiment.py --harness codex --model gpt-6-luna
    python tools\\run_experiment.py --harness gpt3 --model gpt-6-thinking

Every run gets runs/<UTC>_<harness>_<model>/
    prompt.txt          exact message body sent
    cwd/input/          the 24 sources handed to the model (file harnesses)
    stdout.bin          raw stdout
    stderr.bin          raw stderr
    events.jsonl        raw event stream (copied from stdout for opencode/codex)
    output.md           final answer text
    output.json         parsed JSON block
    trace.json          normalized tool trace + classification
    meta.json           timing, argv, exit code, hashes
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
RUNS = ROOT / "runs"
CWD_ROOT = Path(os.environ.get("TEMP", r"C:\Windows\Temp")) / "harness_source_20261029"
GPT3 = Path(r"D:\musicclaude\gpt2agent-safechain\bin\gpt3.cmd")
GPT3_RUNS = Path(r"D:\musicclaude\_thread_evo_20261019\runs")


def now():
    return datetime.now(timezone.utc)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha_bytes(Path(p).read_bytes())


def source_ids():
    return sorted(p.stem for p in (INPUT / "A").glob("*.md"))


def prepare_workdir(run_id):
    wd = CWD_ROOT / run_id
    if wd.exists():
        shutil.rmtree(wd)
    (wd / "input").mkdir(parents=True)
    shutil.copytree(INPUT / "A", wd / "input" / "A")
    shutil.copy2(INPUT / "structure.json", wd / "input" / "structure.json")
    return wd


def run_streaming(cmd, cwd, stdout_path, stderr_path, timeout):
    """Stream stdout/stderr straight to disk so a long run leaves evidence even if it dies."""
    t0 = time.time()
    with open(stdout_path, "wb") as fo, open(stderr_path, "wb") as fe:
        p = subprocess.Popen(cmd, cwd=str(cwd), stdin=subprocess.DEVNULL,
                             stdout=fo, stderr=fe)
        try:
            rc = p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait()
            rc = -9
    return rc, round(time.time() - t0, 1)


def json_block(text):
    """Return (obj, raw_block) for the last parseable fenced JSON block."""
    blocks = re.findall(r"```(?:json)?\s*\n(.*?)```", text, flags=re.S | re.I)
    for b in reversed(blocks):
        try:
            return json.loads(b), b
        except Exception:
            continue
    # fallback: last balanced {...}
    start = text.rfind("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1]), text[start:i + 1]
                    except Exception:
                        break
        start = text.rfind("{", 0, start)
    return None, None


def url_list(text):
    return re.findall(r"https?://[^\s\]\)\"'，。；]+", text or "")


# ---------------------------------------------------------------- opencode
def trace_opencode(raw):
    rows = []
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"type": "_unparsed", "raw": line[:400]})
    tools, searches, fetches, files, errors = [], [], [], [], []
    texts = []
    session = None
    usage = {}
    for r in rows:
        t = r.get("type")
        session = r.get("sessionID") or session
        if t == "text":
            texts.append(r.get("part", {}).get("text", ""))
        elif t == "error":
            errors.append(r.get("error"))
        elif t == "step_finish":
            part = r.get("part", {})
            if part.get("tokens"):
                usage = part["tokens"]
        elif t == "tool_use":
            part = r.get("part", {})
            name = part.get("tool")
            st = part.get("state", {}) or {}
            inp = st.get("input", {}) or {}
            status = st.get("status")
            out = st.get("output")
            rec = {"tool": name, "status": status, "input": inp,
                   "output_chars": len(out) if isinstance(out, str) else None}
            tools.append(rec)
            if status == "error":
                errors.append({"tool": name, "error": st.get("error")})
            if name in ("websearch", "search"):
                searches.append({"via": name, "query": inp.get("query") or inp.get("q"),
                                 "ok": status == "completed"})
            elif name == "webfetch":
                fetches.append({"via": name, "url": inp.get("url") or inp.get("href"),
                                "ok": status == "completed",
                                "error": st.get("error") if status != "completed" else None})
            elif name == "read":
                files.append(inp.get("filePath") or inp.get("path"))
            elif name == "execute":
                code = inp.get("code", "") or ""
                for m in re.finditer(r"tools\.(websearch|search|webfetch|read)\s*\(", code):
                    kind = m.group(1)
                    if kind in ("websearch", "search"):
                        q = re.search(r"query\s*:\s*\"([^\"]+)\"", code)
                        searches.append({"via": "execute.tools." + kind,
                                         "query": q.group(1) if q else None,
                                         "ok": status == "completed"})
                    elif kind == "webfetch":
                        u = re.search(r"url\s*:\s*\"([^\"]+)\"", code)
                        fetches.append({"via": "execute.tools.webfetch",
                                        "url": u.group(1) if u else None,
                                        "ok": status == "completed"})
                    else:
                        f = re.search(r"filePath\s*:\s*\"([^\"]+)\"", code)
                        files.append(f.group(1) if f else None)
    return {"session": session, "usage": usage, "tools": tools,
            "searches": searches, "fetches": fetches, "file_reads": files,
            "errors": errors, "texts": texts}


# ---------------------------------------------------------------- codex
def trace_codex(raw):
    rows = []
    for line in raw.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            rows.append({"type": "_unparsed", "raw": line[:400]})
    tools, searches, fetches, files, errors = [], [], [], [], []
    texts, reasoning = [], []
    usage = {}
    thread = None
    for r in rows:
        t = r.get("type")
        thread = r.get("thread_id") or thread
        if t == "turn.completed":
            usage = r.get("usage", {})
        if t not in ("item.started", "item.completed"):
            continue
        item = r.get("item", {}) or {}
        if t == "item.started":
            continue
        it = item.get("type")
        if it == "web_search":
            action = item.get("action") or {}
            searches.append({"via": "native_web_search",
                             "query": action.get("query") or item.get("query"),
                             "ok": True,
                             "results": [x.get("url") for x in (item.get("results") or [])]})
            tools.append({"tool": "web_search", "detail": action})
        elif it == "command_execution":
            cmd = item.get("command") or ""
            tools.append({"tool": "command_execution", "command": cmd,
                          "exit_code": item.get("exit_code")})
            if re.search(r"\b(curl|wget|Invoke-WebRequest|iwr)\b", cmd, re.I):
                fetches.append({"via": "shell", "url": (url_list(cmd) or [None])[0],
                                "ok": item.get("exit_code") == 0})
        elif it == "agent_message":
            texts.append(item.get("text", ""))
        elif it == "reasoning":
            reasoning.append(item.get("text", ""))
        elif it == "error":
            errors.append(item.get("message"))
        elif it == "file_change":
            files.append(item.get("path") or str(item)[:200])
        elif it == "mcp_tool_call":
            tools.append({"tool": "mcp", "detail": item.get("tool") or item.get("name")})
    return {"session": thread, "usage": usage, "tools": tools,
            "searches": searches, "fetches": fetches, "file_reads": files,
            "errors": errors, "texts": texts, "reasoning": reasoning}


# ---------------------------------------------------------------- gpt3
def trace_gpt3(stdout_bytes):
    payload = None
    text = stdout_bytes.decode("utf-8", "replace").strip()
    for line in reversed(text.splitlines()):
        s = line.strip()
        if s.startswith("{"):
            try:
                payload = json.loads(s)
                break
            except Exception:
                continue
    if not payload:
        return {"searches": [], "fetches": [], "file_reads": [], "errors": [],
                "texts": [], "job": None, "result": None, "tools_used": [], "sources": []}
    meta = payload.get("metadata") or {}
    job = Path(meta.get("job_directory") or "")
    result = None
    if job and (job / "result.json").exists():
        try:
            result = json.loads((job / "result.json").read_text(encoding="utf-8"))
        except Exception:
            result = None
    r = result or {}
    tools_used = r.get("toolsUsed") or []
    sources = r.get("sources") or []
    searches = []
    if any("web" in str(t).lower() or "search" in str(t).lower() for t in tools_used):
        searches.append({"via": ",".join(map(str, tools_used)), "query": None, "ok": True,
                         "results": [s.get("url") for s in sources]})
    return {"searches": searches, "fetches": [], "file_reads": [], "errors": [],
            "texts": [r.get("answer") or payload.get("response") or ""],
            "job": str(job), "result": r, "tools_used": tools_used, "sources": sources}


# ---------------------------------------------------------------- gpt3 gate
class Gpt3Gate:
    """Use the same byte locks / submit spacing as _thread_evo_20261019/gpt3_call.py."""
    def __init__(self, gap=None):
        self.gap = float(gap if gap is not None else os.environ.get("GPT3_GAP", "20"))
        self.lock = GPT3_RUNS / "gpt3_serial.lock"
        self.stamp = GPT3_RUNS / "gpt3_last_submit.txt"
        self.gate = GPT3_RUNS / "gpt3_submit.lock"
        self.slots_file = GPT3_RUNS / "gpt3_slots.txt"

    def slots(self):
        try:
            return max(1, int(self.slots_file.read_text().strip()))
        except Exception:
            return int(os.environ.get("GPT3_SLOTS", "1"))

    def __enter__(self):
        import msvcrt
        self.f = open(self.lock, "a+")
        while True:
            for i in range(self.slots()):
                try:
                    self.f.seek(i)
                    msvcrt.locking(self.f.fileno(), msvcrt.LK_NBLCK, 1)
                    self.pos = i
                    return self
                except OSError:
                    pass
            time.sleep(5)

    def __exit__(self, *a):
        import msvcrt
        self.f.seek(self.pos)
        msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
        self.f.close()

    def space(self):
        import msvcrt, random
        with open(self.gate, "a+") as f:
            while True:
                try:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    time.sleep(1)
            try:
                last = float(self.stamp.read_text()) if self.stamp.exists() else 0.0
                wait = self.gap + random.uniform(0, 10) - (time.time() - last)
                if wait > 0:
                    time.sleep(wait)
                self.stamp.write_text(str(time.time()))
            finally:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)


def classify(tr, out_obj):
    searches = tr.get("searches") or []
    fetches = tr.get("fetches") or []
    errs = tr.get("errors") or []
    web_sources = (out_obj or {}).get("web_sources") or []
    trace_urls = []
    for s in searches:
        trace_urls += (s.get("results") or [])
    for f in fetches:
        if f.get("url"):
            trace_urls.append(f["url"])
    trace_urls = [u for u in trace_urls if u]
    ok_fetch = [f for f in fetches if f.get("ok")]
    bad_fetch = [f for f in fetches if not f.get("ok")]
    if not searches and not fetches:
        mode = "no_web_call"
    elif searches and not fetches:
        mode = "search_only"
    elif ok_fetch and not bad_fetch:
        mode = "search_and_fetch_ok"
    elif ok_fetch:
        mode = "fetch_partly_failed"
    else:
        mode = "fetch_failed"
    return {
        "mode": mode,
        "searches": len(searches),
        "fetches": len(fetches),
        "fetch_ok": len(ok_fetch),
        "fetch_failed": len(bad_fetch),
        "file_reads": len([x for x in (tr.get("file_reads") or []) if x]),
        "tool_errors": len(errs),
        "trace_urls": len(set(trace_urls)),
        "reported_web_sources": len(web_sources),
        "reported_urls": [w.get("url") for w in web_sources if w.get("url")],
        "search_used_in_output": bool(web_sources) or bool(url_list((out_obj or {}).get("web_notes", ""))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", required=True, choices=["opencode", "codex", "gpt3"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", default=None)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--gap", type=float, default=None)
    ap.add_argument("--no-standalone", action="store_true")
    args = ap.parse_args()

    run_id = now().strftime("%Y%m%dT%H%M%SZ") + "_" + (args.label or args.harness) + "_" + str(os.getpid())[-4:] + "_" + uuid.uuid4().hex[:4]
    d = RUNS / run_id
    d.mkdir(parents=True, exist_ok=False)
    prompt_file = ROOT / ("prompt_S01_zip.md" if args.harness == "gpt3" else "prompt_S01_files.md")
    prompt = prompt_file.read_text(encoding="utf-8")
    (d / "prompt.txt").write_text(prompt, encoding="utf-8")

    wd = prepare_workdir(run_id) if args.harness != "gpt3" else ROOT

    meta = {
        "run_id": run_id, "harness": args.harness, "model": args.model,
        "started_utc": now().isoformat(), "prompt_sha256": sha_bytes(prompt.encode()),
        "prompt_chars": len(prompt), "source_ids": source_ids(),
        "input_zip_sha256": sha_file(ROOT / "input_bundle.zip"),
    }

    t0 = time.time()
    if args.harness == "opencode":
        cmd = ["opencode", "run", "--model", args.model, "--format", "json",
               "--auto", "--title", run_id] + ([] if args.no_standalone else ["--standalone"]) + [prompt]
        rc, elapsed = run_streaming(cmd, wd, d / "stdout.bin", d / "stderr.bin", args.timeout)
    elif args.harness == "codex":
        cmd = ["codex", "exec", "-m", args.model, "-c", 'web_search="live"',
               "--json", "-s", "danger-full-access", "--skip-git-repo-check",
               "--color", "never", "-C", str(wd),
               "-o", str(d / "last_message.txt"), prompt]
        rc, elapsed = run_streaming(cmd, wd, d / "stdout.bin", d / "stderr.bin", args.timeout)
    else:
        cmd = [str(GPT3), "ask", "--file", str(d / "prompt.txt"), "--json",
               "--model", args.model, "--allow-topic-stream",
               "--attach", str(ROOT / "input_bundle.zip")]
        with Gpt3Gate(args.gap) as gate:
            gate.space()
            rc, elapsed = run_streaming(cmd, d, d / "stdout.bin", d / "stderr.bin", args.timeout)

    cp_stdout = (d / "stdout.bin").read_bytes()
    cp_stderr = (d / "stderr.bin").read_bytes()

    if args.harness == "opencode":
        tr = trace_opencode(cp_stdout)
        text = "\n".join(tr.get("texts") or [])
        (d / "events.jsonl").write_bytes(cp_stdout)
    elif args.harness == "codex":
        tr = trace_codex(cp_stdout)
        text = (d / "last_message.txt").read_text(encoding="utf-8", errors="replace") if (d / "last_message.txt").exists() else ""
        if not text.strip():
            text = "\n".join(tr.get("texts") or [])
        (d / "events.jsonl").write_bytes(cp_stdout)
    else:
        tr = trace_gpt3(cp_stdout)
        text = "\n".join(tr.get("texts") or [])
        (d / "job_result.json").write_text(json.dumps(tr.get("result"), ensure_ascii=False, indent=1), encoding="utf-8")

    obj, block = json_block(text)
    (d / "output.md").write_text(text, encoding="utf-8")
    (d / "output.json").write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")

    cls = classify(tr, obj)
    trace = {
        "harness": args.harness, "model": args.model,
        "exit_code": rc, "seconds": elapsed,
        "session": tr.get("session"), "usage": tr.get("usage"),
        "searches": tr.get("searches"), "fetches": tr.get("fetches"),
        "file_reads": tr.get("file_reads"), "errors": tr.get("errors"),
        "tools_used": tr.get("tools_used"), "sources": tr.get("sources"),
        "classification": cls,
        "json_extracted": bool(obj),
    }
    (d / "trace.json").write_text(json.dumps(trace, ensure_ascii=False, indent=1), encoding="utf-8")

    meta.update({"finished_utc": now().isoformat(), "seconds": elapsed,
                 "exit_code": rc, "stdout_chars": len(cp_stdout),
                 "stderr_tail": cp_stderr.decode("utf-8", "replace")[-1500:],
                 "output_chars": len(text), "json_extracted": bool(obj),
                 **cls})
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"run_dir": str(d), **{k: meta[k] for k in
          ("harness", "model", "seconds", "exit_code", "mode", "searches", "fetches",
           "file_reads", "reported_web_sources", "json_extracted")}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
