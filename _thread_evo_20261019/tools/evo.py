"""Thread prompt evolution runner. All model inference goes through the local `gpt3` CLI
(default gpt-6-thinking / max). This script only renders inputs, calls gpt3, and archives.

  python evo.py gen  --prompt P0 --work op60 --cond D0,D3,D4 --reps 3 --tag r1
  python evo.py ask  --file some_prompt.txt --out evaluations/x [--attach f ...]
  python evo.py render --prompt P0 --work op60 --cond D3     (print, no model call)

Run ids: <tag>_<prompt>_<work>_<cond>_<rep>; artifacts in runs/<run-id>/.
"""
import argparse, hashlib, json, re, subprocess, sys, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GPT3 = r"D:\musicclaude\gpt2agent-safechain\bin\gpt3.cmd"
GAP = 8.0
_lock = threading.Lock()
_last = [0.0]

WRAP = ("\n\n---\n以下是可供核对的额外参考材料（并非必须模仿的文章或固定剧情）。"
        "请优先完成原提示词规定的 Thread 任务；材料只是可参考的局部体验依据。\n\n")


def load_work(work):
    d = ROOT / "works" / work
    seg = json.loads((d / "segments.json").read_text(encoding="utf-8"))
    return d, seg


def seg_fields(seg):
    """Everything a prompt template may consume about segmentation (machine-readable -> text)."""
    s = seg["segments"]
    w = seg["work"]
    n = w["total_measures"]
    lines = []
    for x in s:
        lines.append(f"{x['id']}｜第{x['start']}—{x['end']}小节" if x["start"] != x["end"]
                     else f"{x['id']}｜第{x['start']}小节")
    return {
        "WORK_SHORT": w.get("short_zh") or w["title_zh"],
        "WORK_TITLE": w["title_zh"],
        "TOTAL_MEASURES": str(n),
        "SEG_COUNT": str(len(s)),
        # P0's original phrasing: left-closed boundaries including the right edge n+1
        "SEG_LIST": ", ".join(str(b) for b in seg["boundaries_left_closed"]),
        # unambiguous closed intervals
        "SEG_TABLE": "\n".join(lines),
    }


def render(prompt, work, cond):
    d, seg = load_work(work)
    tpl = (ROOT / "prompt_versions" / f"{prompt}.txt").read_text(encoding="utf-8")
    f = seg_fields(seg)
    body = tpl
    for k, v in f.items():
        body = body.replace("{" + k + "}", v)
    left = re.findall(r"\{[A-Z_]+\}", body)
    assert not left, left
    body = body.strip()
    if cond in ("D0", "", None):
        return body + "\n"
    mat = (d / "materials" / f"{cond}.md").read_text(encoding="utf-8").strip()
    if "{MATERIAL}" in tpl:
        raise SystemExit("templates with {MATERIAL} not supported here")
    return body + WRAP + mat + "\n"


def gpt3_call(text, outdir: Path, attach=(), model=None, session=None):
    outdir.mkdir(parents=True, exist_ok=True)
    pf = outdir / "input.txt"
    pf.write_text(text, encoding="utf-8")
    with _lock:
        w = GAP - (time.time() - _last[0])
        if w > 0:
            time.sleep(w)
        _last[0] = time.time()
    cmd = [GPT3, "ask", "--file", str(pf), "--json"]
    if model:
        cmd += ["--model", model]
    if session:
        cmd += ["--session", session]
    for a in attach:
        cmd += ["--attach", str(a)]
    t0 = time.time()
    start = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    cp = subprocess.run(cmd, capture_output=True)
    dt = time.time() - t0
    (outdir / "stdout.json").write_bytes(cp.stdout)
    (outdir / "stderr.txt").write_bytes(cp.stderr)
    resp, meta = None, {}
    try:
        j = json.loads(cp.stdout.decode("utf-8-sig"))
        meta = j.get("metadata", {})
        if cp.returncode == 0 and j.get("completed"):
            resp = j.get("response")
    except Exception as e:  # noqa
        meta = {"parse_error": repr(e)}
    log = {"command": " ".join(f'"{c}"' if " " in c else c for c in cmd), "start": start,
           "seconds": round(dt, 1), "exit_code": cp.returncode, "completed": resp is not None,
           "model": meta.get("model"), "thinking_effort": meta.get("thinking_effort"),
           "temporary": meta.get("temporary"), "unpersonalized": meta.get("unpersonalized"),
           "session_handle": meta.get("session_handle"), "job_directory": meta.get("job_directory"),
           "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "attach": [str(a) for a in attach]}
    (outdir / "call.log").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    if resp is not None:
        (outdir / "output.txt").write_text(resp, encoding="utf-8")
    print(f"[{outdir.name}] {'ok' if resp else 'FAIL'} rc={cp.returncode} {dt:.0f}s "
          f"{log['model']}/{log['thinking_effort']} chars={len(resp or '')}", flush=True)
    return resp, log


def cmd_gen(a):
    jobs = []
    for cond in a.cond.split(","):
        for r in range(a.start, a.start + a.reps):
            rid = f"{a.tag}_{a.prompt}_{a.work}_{cond}_{r}"
            out = ROOT / "runs" / rid
            if (out / "output.txt").exists():
                print(f"[{rid}] cached"); continue
            text = render(a.prompt, a.work, cond)
            out.mkdir(parents=True, exist_ok=True)
            (out / "prompt.txt").write_text((ROOT / "prompt_versions" / f"{a.prompt}.txt").read_text(encoding="utf-8"), encoding="utf-8")
            (out / "run.json").write_text(json.dumps({"prompt": a.prompt, "work": a.work, "cond": cond, "rep": r, "tag": a.tag}), encoding="utf-8")
            jobs.append((text, out))
    ths = [threading.Thread(target=gpt3_call, args=(t, o)) for t, o in jobs]
    for t in ths: t.start()
    for t in ths: t.join()


def cmd_ask(a):
    text = Path(a.file).read_text(encoding="utf-8")
    gpt3_call(text, ROOT / a.out, a.attach or (), a.model, a.session)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="c", required=True)
    g = sp.add_parser("gen"); g.add_argument("--prompt", required=True); g.add_argument("--work", required=True)
    g.add_argument("--cond", default="D0"); g.add_argument("--reps", type=int, default=1); g.add_argument("--start", type=int, default=1)
    g.add_argument("--tag", required=True)
    k = sp.add_parser("ask"); k.add_argument("--file", required=True); k.add_argument("--out", required=True)
    k.add_argument("--attach", action="append"); k.add_argument("--model"); k.add_argument("--session")
    r = sp.add_parser("render"); r.add_argument("--prompt", required=True); r.add_argument("--work", required=True); r.add_argument("--cond", default="D0")
    a = ap.parse_args()
    if a.c == "gen": cmd_gen(a)
    elif a.c == "ask": cmd_ask(a)
    else: sys.stdout.reconfigure(encoding="utf-8"); print(render(a.prompt, a.work, a.cond))
