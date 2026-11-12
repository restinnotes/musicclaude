"""run131：gpt2 CLI 网页 GPT 烟雾测试（R1，Opus 子智能体编写）。

6 个 job 串行：{gpt56w, gpt6w} x {short_q, long_sum, cup}，全部经
tools/gpt2_adapter.call_web_gpt（gpt2.cmd 经 cmd.exe /c 调用）。

  python -I runs/run131_gpt2_smoke/go.py            真实运行（由主会话后台启动）
  python -I runs/run131_gpt2_smoke/go.py --dry-run  用临时桩 CLI，全部产物写到临时目录
  python -I runs/run131_gpt2_smoke/go.py --dry-run --simulate-429  同上，并验证账号保护信号会停队列

续跑：meta/<job_id>.json 为 status=ok 的 job 跳过。
账号保护信号（403/429/challenge/cooldown/rate limit）：立即停掉剩余 job，写 stop_reason.json + FAILED。
  - stderr 一律检查；stdout/错误文本只在该 job 失败时检查（成功回答正文里出现 "429" 之类不算信号）。
结束写 report.md、run_manifest.json、DONE（6 个全部 ok）或 FAILED。
不做任何内容/审美判断；suspect 只看：耗时<60s、水杯题答案≠8、服务端 slug 与请求不符。
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL_RUN = ROOT / "runs" / "run131_gpt2_smoke"
SRC_PROMPTS = REAL_RUN / "prompts"
RUN_ID = "run131_gpt2_smoke"
sys.path.insert(0, str(ROOT / "tools"))

MODELS = ("gpt56w", "gpt6w")
PROMPTS = ("short_q", "long_sum", "cup")
JOB_TIMEOUT = 1800
CUP_EXPECTED = 8
FAST_SECONDS = 60

PROTECT_RE = re.compile(
    r"\b403\b|\b429\b|challenge|cool[\s_-]?down|rate[\s_-]?limit|too many requests",
    re.IGNORECASE)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def git_head() -> str:
    try:
        cp = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                            capture_output=True, timeout=30,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return cp.stdout.decode("utf-8", "replace").strip() or "unknown"
    except Exception:
        return "unknown"


def job_order():
    # 先两个模型的短题（尽早暴露路由问题），再长输入，最后水杯题
    return [(m, p) for p in PROMPTS for m in MODELS]


def job_id_of(model_key: str, prompt_name: str) -> str:
    return f"run131__{model_key}__{prompt_name}"


# ---------------------------------------------------------------- 证据提取
def _walk_slugs(obj, depth=0, path=""):
    """在 CLI metadata 里找所有像模型身份的字段（键名含 model/slug）。"""
    out = []
    if depth > 6:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}" if path else str(k)
            kl = str(k).lower()
            if ("model" in kl or "slug" in kl) and isinstance(v, str) and v:
                out.append((kp, v))
            elif ("model" in kl or "slug" in kl) and isinstance(v, list):
                out.extend((kp, x) for x in v if isinstance(x, str) and x)
            else:
                out.extend(_walk_slugs(v, depth + 1, kp))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            out.extend(_walk_slugs(v, depth + 1, f"{path}[{i}]"))
    return out


def _norm_slug(s: str) -> str:
    return s.strip().lower().replace(".", "-").replace("_", "-")


def slug_evidence(meta: dict) -> dict:
    """服务端报告的模型身份：优先 resolved_model_slugs / server_metadata 中的 slug。"""
    md = meta.get("cli_metadata") if isinstance(meta.get("cli_metadata"), dict) else {}
    found = _walk_slugs(md)
    server = [v for k, v in found
              if "resolved" in k.lower() or "server" in k.lower() or "slug" in k.lower()]
    reported = sorted(set(server or [v for _, v in found]))
    requested = meta.get("requested_model") or ""
    if not reported:
        verdict = "no_slug"
    elif any(_norm_slug(r) == _norm_slug(requested) for r in reported):
        verdict = "match" if all(_norm_slug(r) == _norm_slug(requested) for r in reported) else "mixed"
    else:
        verdict = "mismatch"
    return {"reported_slugs": reported, "slug_fields": [k for k, _ in found][:20],
            "slug_verdict": verdict}


_CUP_PATS = [
    r"x\s*[=＝]\s*(\d+)",
    r"答案(?:是|为|：|:)\s*(\d+)",
    r"最少(?:需要|是|为|要)?\s*(\d+)\s*次",
    r"最坏情况[^\d\n。]{0,24}?(\d+)\s*次",
    r"(\d+)\s*次(?:交换)?(?:即可|就够|是最少|为最少|是最优)",
]


def cup_answer(text: str):
    """从水杯题回答里抽取最终数字（启发式，候选列表一并留存供人工核对）。"""
    t = re.sub(r"[*$\\`]", "", text or "")
    t = t.replace("{", "").replace("}", "")
    cands = []
    for pat in _CUP_PATS:
        for m in re.finditer(pat, t):
            cands.append((m.start(), int(m.group(1))))
    if not cands:
        return None, []
    cands.sort()
    nums = [n for _, n in cands]
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    best = max(counts.items(), key=lambda kv: (kv[1], -nums.index(kv[0])))[0]
    return best, nums[:30]


def protect_signal(run_dir: Path, meta: dict):
    """账号保护信号：stderr 必查；失败 job 再查 stdout 与错误文本。返回命中片段或 None。"""
    texts = []
    try:
        texts.append(("stderr", (run_dir / meta["stderr_file"]).read_text(encoding="utf-8", errors="replace")))
    except Exception:
        texts.append(("stderr", meta.get("stderr_tail") or ""))
    if meta.get("status") != "ok":
        try:
            texts.append(("stdout", (run_dir / meta["stdout_file"]).read_text(encoding="utf-8", errors="replace")))
        except Exception:
            pass
        texts.append(("error", meta.get("error") or ""))
    for src, txt in texts:
        m = PROTECT_RE.search(txt or "")
        if m:
            a, b = max(0, m.start() - 120), min(len(txt), m.end() + 120)
            return {"source": src, "match": m.group(0), "context": txt[a:b]}
    return None


# ---------------------------------------------------------------- 干跑桩
STUB_PY = r'''
import json, sys, time, os
a = sys.argv[1:]
assert a and a[0] == "ask" and "--json" in a, a
text = open(a[a.index("--file") + 1], encoding="utf-8").read()
model = a[a.index("--model") + 1]
time.sleep(0.2)
fail_on = os.environ.get("RUN131_STUB_429_ON", "")
if fail_on and fail_on in text[:200] and model == "gpt-6-thinking":
    sys.stderr.write("HTTP 429 Too Many Requests: account cooldown\n")
    sys.stdout.write(json.dumps({"completed": False, "error_code": "rate_limited"}))
    sys.exit(1)
if "水杯" in text:
    resp = "（桩）最坏情况下最少需要 8 次交换。因此 x = 8。"
else:
    resp = "（桩）回答：" + text[:40]
payload = {"completed": True, "response": resp,
           "metadata": {"session_handle": "stub", "elapsed_seconds": 0.2,
                        "resolved_model_slugs": [model]}}
sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
'''


def make_stub(tmp: Path) -> Path:
    stub_py = tmp / "_stub" / "gpt2_stub.py"
    stub_py.parent.mkdir(parents=True, exist_ok=True)
    stub_py.write_text(STUB_PY, encoding="utf-8")
    stub_cmd = tmp / "_stub" / "gpt2.cmd"
    stub_cmd.write_text(f'@echo off\r\n"{sys.executable}" -I "{stub_py}" %*\r\nexit /b %errorlevel%\r\n',
                        encoding="utf-8")
    return stub_cmd


# ---------------------------------------------------------------- 主流程
def append_progress(run: Path, line: str):
    with (run / "progress.md").open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} {line}\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--dry-dir", type=Path, default=None,
                    help="仅 --dry-run：复用指定临时目录（验证续跑）")
    ap.add_argument("--simulate-429", action="store_true",
                    help="仅 --dry-run：让桩在 gpt6w 的 long_sum 上返回 429，验证停队列")
    a = ap.parse_args(argv)
    if (a.simulate_429 or a.dry_dir) and not a.dry_run:
        ap.error("--simulate-429/--dry-dir 只能与 --dry-run 一起用")
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    gpt2_cmd = None
    if a.dry_run:
        tmp = a.dry_dir or Path(tempfile.mkdtemp(prefix="run131_dry_"))
        if tmp.resolve() == REAL_RUN.resolve() or REAL_RUN.resolve() in tmp.resolve().parents:
            ap.error("干跑目录不能在真实 run 目录里")
        run = tmp / RUN_ID
        run.mkdir(parents=True, exist_ok=True)
        gpt2_cmd = str(make_stub(tmp))
        os.environ["MUSIC_GPT2_CMD"] = gpt2_cmd  # 适配器导入前设好，双保险再显式传参
        if a.simulate_429:
            os.environ["RUN131_STUB_429_ON"] = "肖邦《第四叙事曲》"
        if not (run / "progress.md").exists():
            (run / "progress.md").write_text("# run131 dry-run progress\n", encoding="utf-8")
    else:
        run = REAL_RUN
    import gpt2_adapter  # noqa: E402  (MUSIC_GPT2_CMD 必须先设)

    for name in ("DONE", "FAILED", "stop_reason.json"):
        (run / name).unlink(missing_ok=True)
    print(f"run dir: {run}  dry_run={a.dry_run}  cli={gpt2_cmd or gpt2_adapter.GPT2_CMD}", flush=True)

    prompts = {}
    for p in PROMPTS:
        raw = (SRC_PROMPTS / f"{p}.txt").read_bytes()
        # 源文件是 CRLF；发出前统一成 LF（发出的原文另存 prompts/<job_id>.txt，sha 记在 meta）
        prompts[p] = raw.decode("utf-8-sig").replace("\r\n", "\n")
        if a.dry_run:
            (run / "prompts").mkdir(exist_ok=True)
            (run / "prompts" / f"{p}.txt").write_bytes(raw)

    rows, stop = [], None
    append_progress(run, f"go.py start (dry_run={a.dry_run})")
    for model_key, pname in job_order():
        jid = job_id_of(model_key, pname)
        mp = run / "meta" / f"{jid}.json"
        meta = None
        if mp.exists():
            try:
                old = json.loads(mp.read_text(encoding="utf-8"))
                if old.get("status") == "ok":
                    meta, resumed = old, True
            except Exception:
                meta = None
        if stop is not None:
            if meta is None:
                rows.append({"job_id": jid, "model_key": model_key, "prompt": pname,
                             "status": "skipped_stop"})
                continue
        if meta is None:
            resumed = False
            print(f"[run] {jid}", flush=True)
            meta = gpt2_adapter.call_web_gpt(
                model_key, prompts[pname], run_id=RUN_ID, job_id=jid, out_dir=run,
                effort="max", timeout=JOB_TIMEOUT, max_attempts=1, gpt2_cmd=gpt2_cmd)
        out_text = ""
        try:
            out_text = (run / meta["output_file"]).read_text(encoding="utf-8")
        except Exception:
            pass
        ev = slug_evidence(meta)
        smoke = {
            "prompt_name": pname, "resumed": resumed,
            "elapsed_seconds": meta.get("seconds"),
            "prompt_chars": meta.get("prompt_chars"),
            "output_chars": len(out_text),
            "prompt_sha256": meta.get("prompt_sha256"),
            "output_sha256": sha256_bytes(out_text.encode("utf-8")) if out_text else None,
            **ev,
        }
        reasons = []
        if meta.get("status") == "ok":
            if (meta.get("seconds") or 0) < FAST_SECONDS and not meta.get("cache_hit"):
                reasons.append(f"elapsed<{FAST_SECONDS}s")
            if ev["slug_verdict"] in ("mismatch", "mixed"):
                reasons.append("slug_mismatch")
            if pname == "cup":
                ans, cands = cup_answer(out_text)
                smoke["cup_answer"], smoke["cup_candidates"] = ans, cands
                smoke["cup_ok"] = ans == CUP_EXPECTED
                if ans != CUP_EXPECTED:
                    reasons.append(f"cup_answer={ans}")
        smoke["suspect"] = bool(reasons)
        smoke["suspect_reasons"] = reasons
        sig = protect_signal(run, meta)
        smoke["protect_signal"] = sig
        meta["smoke"] = smoke
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        rows.append({"job_id": jid, "model_key": model_key, "prompt": pname,
                     "status": meta.get("status"), "error": meta.get("error"),
                     "requested_model": meta.get("requested_model"),
                     "cli_version": meta.get("cli_version"),
                     "returncode": meta.get("returncode"), **smoke})
        print(f"[{meta.get('status')}] {jid} {meta.get('seconds')}s {len(out_text)}ch "
              f"slug={ev['reported_slugs']} suspect={reasons}", flush=True)
        append_progress(run, f"{jid}: {meta.get('status')} {meta.get('seconds')}s "
                             f"{len(out_text)}ch suspect={reasons or '-'}")
        if sig and stop is None and not resumed:
            stop = {"job_id": jid, **sig, "time": datetime.now().isoformat(timespec="seconds")}
            (run / "stop_reason.json").write_text(json.dumps(stop, ensure_ascii=False, indent=2),
                                                  encoding="utf-8")
            print(f"[STOP] 账号保护信号 {sig['match']!r} @ {jid}，停止剩余 job", flush=True)
            append_progress(run, f"STOP: protect signal {sig['match']!r} at {jid}")

    write_report(run, rows, stop, a.dry_run)
    write_manifest(run, rows, a.dry_run, gpt2_cmd or gpt2_adapter.GPT2_CMD)
    ok = all(r.get("status") == "ok" for r in rows) and stop is None
    if ok:
        (run / "DONE").write_text("6/6 ok\n", encoding="utf-8")
    else:
        bad = [f"{r['job_id']}={r.get('status')}" for r in rows if r.get("status") != "ok"]
        why = (f"stopped: {stop['match']!r} at {stop['job_id']}; " if stop else "") + ", ".join(bad)
        (run / "FAILED").write_text(why + "\n", encoding="utf-8")
    append_progress(run, f"go.py end: {'DONE' if ok else 'FAILED'}")
    print(f"{'DONE' if ok else 'FAILED'}  -> {run}", flush=True)
    return 0 if ok else 1


def write_report(run: Path, rows, stop, dry_run: bool):
    L = [f"# run131 gpt2 烟雾测试报告{'（干跑，桩 CLI）' if dry_run else ''}", "",
         f"生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}", "",
         "只记录事实证据，不做内容评价。suspect = 耗时<60s，或水杯题答案≠8，或服务端 slug 与请求不符。"
         "（用户规则：疑似≠降智；水杯题正常应 >3 分钟且答 8。）", ""]
    if stop:
        L += [f"**已停队列**：{stop['job_id']} 出现账号保护信号 `{stop['match']}`（来源 {stop['source']}）。", ""]
    L += ["| job | 模型 | 状态 | 耗时(s) | 输出字数 | 服务端 slug | 水杯=8? | suspect |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r.get("status") == "skipped_stop":
            L.append(f"| {r['job_id']} | {r['model_key']} | 未跑（已停） | - | - | - | - | - |")
            continue
        cup = "-" if r["prompt"] != "cup" else (
            "是" if r.get("cup_ok") else f"否（{r.get('cup_answer')}）") if r.get("status") == "ok" else "-"
        slug = ", ".join(r.get("reported_slugs") or []) or "无"
        sus = "是：" + "; ".join(r["suspect_reasons"]) if r.get("suspect") else "否"
        st = r.get("status") + (f"（{(r.get('error') or '')[:60]}）" if r.get("status") != "ok" else "")
        L.append(f"| {r['job_id']} | {r.get('requested_model') or r['model_key']} | {st} | "
                 f"{r.get('elapsed_seconds')} | {r.get('output_chars')} | {slug}（{r.get('slug_verdict')}） | "
                 f"{cup} | {sus} |")
    cups = [r for r in rows if r.get("prompt") == "cup" and r.get("status") == "ok"]
    if cups:
        L += ["", "## 水杯题抽取候选（启发式，供人工核对）", ""]
        for r in cups:
            L.append(f"- {r['job_id']}：答案={r.get('cup_answer')}，候选={r.get('cup_candidates')}，"
                     f"耗时 {r.get('elapsed_seconds')}s")
    L += ["", f"CLI 版本（safechain HEAD）：{', '.join(sorted({str(r.get('cli_version')) for r in rows if r.get('cli_version')})) or '未知'}",
          "", "原始产物：outputs/<job>.md，outputs/raw/<job>.stdout.txt / .stderr.txt，meta/<job>.json（smoke 字段）。"]
    (run / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_manifest(run: Path, rows, dry_run: bool, cli: str):
    def hashes(sub):
        d = run / sub
        if not d.exists():
            return {}
        return {str(p.relative_to(run)).replace("\\", "/"): sha256_file(p)
                for p in sorted(d.rglob("*")) if p.is_file()}
    man = {
        "run_id": RUN_ID, "dry_run": dry_run,
        "created": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_head(), "cli": cli,
        "job_timeout_s": JOB_TIMEOUT,
        "prompts_sha256": hashes("prompts"),
        "outputs_sha256": hashes("outputs"),
        "meta_sha256": hashes("meta"),
        "jobs": [{k: r.get(k) for k in ("job_id", "model_key", "prompt", "status",
                                         "elapsed_seconds", "output_chars", "reported_slugs",
                                         "slug_verdict", "suspect", "suspect_reasons")}
                 for r in rows],
    }
    (run / "run_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2),
                                           encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
