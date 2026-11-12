"""N02 parameterized A prompts. Default: original 10 GPT supplements; --corpus24: full corpus."""
import argparse, json, os, re, subprocess, sys, threading, time
from pathlib import Path
D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[1] / "_thread_evo_20261019"))
import work_meta
WORK = None

def render(pv, work="op61"):
    d = work_meta.load(work)
    return work_meta.render((D.parent / "prompts" / f"{pv}.param.txt").read_text(encoding="utf-8"), d)

GPT3 = "D:/musicclaude/gpt2agent-safechain/bin/gpt3.cmd"
JOBS = [(f"gpt6w-int-{i}", "A_int_v1", "gpt-6-thinking") for i in (1, 2, 3)] + \
       [(f"gpt6w-web-{i}", "A_web_v2", "gpt-6-thinking") for i in (1, 2, 3)] + \
       [(f"gpt56w-int-{i}", "A_int_v1", "gpt-5-6-thinking") for i in (2, 3)] + \
       [(f"gpt56w-web-{i}", "A_web_v2", "gpt-5-6-thinking") for i in (2, 3)]
lock = threading.Lock(); last = [0.0]
def output_dir():
    return D / "out" if WORK == "op61" else work_meta.load(WORK)["_dir"] / "gen_A" / "out"


def run(name, pv, model, prompt_text=None):
    prompt_text = render(pv, WORK) if prompt_text is None else prompt_text
    out = output_dir()
    out.mkdir(parents=True, exist_ok=True)
    if (out / f"{name}.md").exists() or (out / f"{name}.submitted").exists():
        print(f"[{name}] skip (exists/submitted)", flush=True); return
    pf = out / f"{name}.prompt.txt"
    if not pf.exists():
        pf.write_text(prompt_text, encoding="utf-8")
    elif pf.read_text(encoding="utf-8") != prompt_text:
        raise ValueError(f"rendered prompt changed: {pf}")
    with lock:
        w = 7 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        last[0] = time.time()
    (out / f"{name}.submitted").write_text(time.ctime(), encoding="utf-8")
    cp = subprocess.run([GPT3, "ask", "--file", str(pf), "--model", model, "--json"], capture_output=True)
    (out / f"{name}.stdout.bin").write_bytes(cp.stdout); (out / f"{name}.stderr.bin").write_bytes(cp.stderr)
    m = re.search(rb'"job_directory":\s*"((?:[^"\\]|\\.)*)"', cp.stdout)
    job = Path(json.loads(b'"' + m.group(1) + b'"')) if m else None
    if cp.returncode == 0 and job and (job / "response.txt").exists() and b'"completed": true' in cp.stdout:
        resp = (job / "response.txt").read_text(encoding="utf-8")
        tv = json.loads((job / "terminal-verification.json").read_text(encoding="utf-8"))
        jr = json.loads((job / "result.json").read_text(encoding="utf-8"))
        fm = (tv.get("final_messages") or [{}])[0]
        meta = {"name": name, "prompt": pv, "model_req": model, "model": fm.get("model"), "effort": fm.get("effort"),
                "tools_used": jr.get("toolsUsed"), "temporary": jr.get("temporary"), "unpersonalized": jr.get("unpersonalized"),
                "elapsed_seconds": jr.get("elapsed_seconds"), "job_directory": str(job)}
        (out / f"{name}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        (out / f"{name}.md").write_text(resp, encoding="utf-8")
        print(f"[{name}] ok {meta['model']}/{meta['effort']} tools={meta['tools_used']} {len(resp)}ch", flush=True)
    else:
        print(f"[{name}] FAILED rc={cp.returncode} job={job}", flush=True)
def corpus_jobs(work):
    """Same four models, two prompt branches, three independent samples."""
    jobs = []
    suffixes = work_meta.load(work).get("a_job_suffixes", {})
    for family, models in (("gflash", ("gflash", "gflash_web")), ("luna", ("luna_noweb", "luna")),
                           ("gpt56w", ("gpt-5-6-thinking",) * 2), ("gpt6w", ("gpt-6-thinking",) * 2)):
        for branch, pv, model in zip(("int", "web"), ("A_int_v1", "A_web_v2"), models):
            for i in (1, 2, 3):
                jobs.append({"name": f"{family}-{branch}-{i}", "pv": pv, "model": model,
                             "family": family, "branch": branch, "sample": i, "prompt": render(pv, work) + suffixes.get(f"{family}-{branch}-{i}", "")})
    return jobs


def corpus24():
    d = work_meta.load(WORK); dest = work_meta.source_dir(d)
    jobs = corpus_jobs(WORK)
    expected = {"SRC-" + j["name"] + ".md" for j in jobs}
    present = {p.name for p in dest.glob("*.md")}
    if present == expected:
        print("24 A sources already present:", dest); return
    if present:
        raise ValueError(f"partial/existing A directory: {dest}; finish or collect sources explicitly before running corpus24")
    # Keep the established GPT launcher, pacing and submitted markers.
    ts = [threading.Thread(target=run, args=(j["name"], j["pv"], j["model"], j["prompt"])) for j in jobs if j["family"].startswith("gpt")]
    [t.start() for t in ts]; [t.join() for t in ts]
    # Reuse the existing non-GPT runner, including its policy/cache/launcher behavior.
    runner_dir = Path(d.get("a_runner_dir") or D.parents[1] / "music_work_since_1008v3_20261009" / "tools")
    sys.path.insert(0, str(runner_dir))
    import runner
    other = []
    for j in jobs:
        if j["family"].startswith("gpt"):
            continue
        item = {"job_id": j["name"], "branch": "A-" + j["branch"], "model_key": j["model"],
                "prompt": j["prompt"], "prompt_version": j["pv"], "work_key": WORK,
                "work_name": work_meta.name(d, True), "sample": j["sample"]}
        if j["branch"] == "int":
            item["forbid_tools"] = ["search_web", "read_url_content", "browser_subagent", "open_browser_url",
                                    "read_browser_page", "call_mcp_tool", "run_command"]
            item["max_attempts"] = 6
        other.append(item)
    run_dir = output_dir().parent / "other_models"
    results = runner.run_jobs(run_dir, other, max_workers=6, timeout=3600)
    if any(m["status"] != "ok" for m in results):
        raise RuntimeError("non-GPT A jobs incomplete; A source directory has not been populated")
    texts = {}
    for j in jobs:
        f = output_dir() / (j["name"] + ".md") if j["family"].startswith("gpt") else run_dir / "outputs" / (j["name"] + ".md")
        texts["SRC-" + j["name"] + ".md"] = f.read_text(encoding="utf-8")
    work_meta.write_prompts(dest, texts)
    print("24 A sources collected:", dest)


def main():
    global WORK
    ap = argparse.ArgumentParser(description="Existing 10 GPT supplemental A jobs; --render-dir is strictly offline")
    ap.add_argument("--work", default=os.environ.get("WORK", "op61"))
    ap.add_argument("--render-dir")
    ap.add_argument("--corpus24", action="store_true", help="generate and collect all 24 A drafts")
    a = ap.parse_args(); WORK = a.work
    if a.render_dir:
        prompts = {f"{pv}.txt": render(pv, WORK) for pv in ("A_int_v1", "A_web_v2")}
        if a.corpus24:
            prompts["jobs24.json"] = json.dumps(corpus_jobs(WORK), ensure_ascii=False, indent=2)
        work_meta.write_prompts(a.render_dir, prompts)
        return
    if a.corpus24:
        corpus24(); return
    ts = [threading.Thread(target=run, args=j) for j in JOBS]
    [t.start() for t in ts]; [t.join() for t in ts]


if __name__ == "__main__":
    main()
