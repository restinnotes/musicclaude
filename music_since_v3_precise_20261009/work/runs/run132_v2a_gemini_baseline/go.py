"""run132：V2A 原版提示词 + Gemini 基线重采（R1，Opus 子智能体编写）。

提示词 = prompts/A_orig_V2A.txt，仅把 {{WORK}} 换成 prompts/WORKS.md 里的作品名，其余字节不变。
经 tools/runner.run_jobs 调用（并发 <=3，续跑：meta 为 ok 的 job 跳过）：
  gpro_web  (gemini-3.1-pro-high)  ：Op.60 x3，Op.61 x3，Op.52 x2
  gflash_web(gemini-3.8-flash-high)：每首 x1
suspect（机械判定，不做质量评价）= 代理固定道歉句 / 拒答 / <60s 却有数千字；
suspect 或失败的 job 用新 job_id（__retry1）重跑一次，原件保留。

  python -I runs/run132_v2a_gemini_baseline/go.py            真实运行（主会话后台启动）
  python -I runs/run132_v2a_gemini_baseline/go.py --dry-run  mock runner.run_job，产物写临时目录
  python -I runs/run132_v2a_gemini_baseline/go.py --smoke    真实各调一次 gpro_web/gflash_web「只回复：好」，写 RUN/_smoke
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import random
import re
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REAL_RUN = ROOT / "runs" / "run132_v2a_gemini_baseline"
RUN_ID = "run132_v2a_gemini_baseline"
TEMPLATE = ROOT / "prompts" / "A_orig_V2A.txt"
WORKS_MD = ROOT / "prompts" / "WORKS.md"
sys.path.insert(0, str(ROOT / "tools"))

PLAN = {  # model_key -> {work_key: 采样数}
    "gpro_web": {"op60": 3, "op61": 3, "op52": 2},
    "gflash_web": {"op52": 1, "op60": 1, "op61": 1},
}
MAX_WORKERS = 3
JOB_TIMEOUT = 1800
FAST_SECONDS = 60
FAST_MIN_CHARS = 2000  # <60s 却有 >=2000 字 视为可疑

CANNED = (
    "尝试调取实时信息时遇到了格式异常",
    "遇到了格式异常",
)
REFUSAL_RE = re.compile(
    r"(抱歉|对不起|很遗憾)[，,。\s]*(我)?(无法|不能|没法)|I(?:'m| am) sorry|I can(?:no|')t (?:help|assist|provide)",
    re.IGNORECASE)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_head() -> str:
    try:
        cp = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                            timeout=30, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return cp.stdout.decode("utf-8", "replace").strip() or "unknown"
    except Exception:
        return "unknown"


def load_works() -> dict:
    """WORKS.md 的反引号作品名 -> {op52: name, ...}。"""
    works = {}
    for line in WORKS_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*-\s*`([^`]+)`", line)
        if m:
            op = re.search(r"Op\.(\d+)", m.group(1))
            if op:
                works[f"op{op.group(1)}"] = m.group(1)
    need = {w for plan in PLAN.values() for w in plan}
    missing = need - set(works)
    if missing:
        raise SystemExit(f"WORKS.md 缺作品：{sorted(missing)}")
    return works


def build_prompt(template_bytes: bytes, work_name: str) -> bytes:
    """只替换 {{WORK}}；其余字节不变（不做 BOM/换行处理）。"""
    marker = "{{WORK}}".encode("utf-8")
    if marker not in template_bytes:
        raise SystemExit("A_orig_V2A.txt 里没有 {{WORK}}")
    return template_bytes.replace(marker, work_name.encode("utf-8"))


def make_jobs(prompts: dict, works: dict) -> list:
    jobs = []
    for mk, plan in PLAN.items():
        for wk, n in plan.items():
            for s in range(1, n + 1):
                jobs.append({
                    "job_id": f"run132__{wk}__{mk}__s{s}",
                    "model_key": mk, "branch": "V2A_orig",
                    "prompt": prompts[wk].decode("utf-8"),
                    "prompt_version": "A_orig_V2A", "prompt_template": "prompts/A_orig_V2A.txt",
                    "work_key": wk, "work_name": works[wk], "sample": s,
                    "extra": {"run": RUN_ID},
                })
    return jobs


def assess(run: Path, meta: dict) -> dict:
    """机械指标 + suspect 判定（不评价质量）。"""
    text = ""
    try:
        text = (run / meta["output_file"]).read_text(encoding="utf-8")
    except Exception:
        pass
    paras = [p for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n")) if p.strip()]
    reasons = []
    if meta.get("status") != "ok":
        reasons.append("failed: " + str(meta.get("error"))[:120])
    else:
        hit = [c for c in CANNED if c in text]
        if hit:
            reasons.append("canned_apology")
        if REFUSAL_RE.search(text[:400]) and len(text) < 1500:
            reasons.append("refusal")
        if (meta.get("seconds") or 0) < FAST_SECONDS and len(text) >= FAST_MIN_CHARS:
            reasons.append(f"<{FAST_SECONDS}s with {len(text)} chars")
        if not text.strip():
            reasons.append("empty")
    return {
        "chars": len(text),
        "mm_markers": text.count("mm."),
        "has_mm": "mm." in text,
        "paragraphs": len(paras),
        "replacement_chars": text.count("�"),
        "output_sha256": sha256_bytes(text.encode("utf-8")) if text else None,
        "suspect": bool(reasons), "suspect_reasons": reasons,
    }


# ---------------------------------------------------------------- dry-run mock
def install_mock(runner):
    """替换 runner.run_job：按 runner 的落盘布局写 prompt/output/meta，不调模型。"""
    def fake_run_job(run_dir, job, timeout=3600):
        run_dir = Path(run_dir)
        jid = job["job_id"]
        time.sleep(random.uniform(0.05, 0.2))
        if jid == "run132__op61__gpro_web__s2":
            text = "抱歉，我在尝试调取实时信息时遇到了格式异常。"  # 演练 retry 路径
        else:
            text = (f"（mock）{job['work_name']} 第一段 mm. 1-8\n\n第二段 mm. 9-24\n\n第三段")
        for sub, body in ((f"prompts/{jid}.txt", job["prompt"]), (f"outputs/{jid}.md", text),
                          (f"outputs/raw/{jid}.stdout.txt", ""), (f"outputs/raw/{jid}.stderr.txt", "")):
            p = run_dir / sub
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(body)
        meta = {"job_id": jid, "branch": job.get("branch", ""), "model_key": job["model_key"],
                "model_name": runner.MODEL_NAMES.get(job["model_key"]), "argv": ["<mock>"],
                "stdin_mode": "raw", "prompt_file": f"prompts/{jid}.txt",
                "prompt_version": job.get("prompt_version"), "prompt_template": job.get("prompt_template"),
                "work_key": job.get("work_key"), "work_name": job.get("work_name"),
                "sample": job.get("sample"), "started": datetime.now().isoformat(timespec="seconds"),
                "ended": datetime.now().isoformat(timespec="seconds"), "seconds": 123.4,
                "exit_code": 0, "status": "ok", "error": None, "attempts": 1,
                "output_file": f"outputs/{jid}.md", "stdout_file": f"outputs/raw/{jid}.stdout.txt",
                "stderr_file": f"outputs/raw/{jid}.stderr.txt", "output_chars": len(text),
                "replacement_chars": 0, "tool_counts": {}, "extra": job.get("extra") or {}}
        (run_dir / "meta").mkdir(parents=True, exist_ok=True)
        (run_dir / "meta" / f"{jid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                                      encoding="utf-8")
        return meta
    runner.run_job = fake_run_job


# ---------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    import runner  # noqa: E402

    if a.smoke:
        return smoke(runner)

    if a.dry_run:
        run = Path(tempfile.mkdtemp(prefix="run132_dry_")) / RUN_ID
        run.mkdir(parents=True)
        install_mock(runner)
    else:
        run = REAL_RUN
        run.mkdir(parents=True, exist_ok=True)
    for name in ("DONE", "FAILED"):
        (run / name).unlink(missing_ok=True)
    print(f"run dir: {run}  dry_run={a.dry_run}", flush=True)

    works = load_works()
    tpl = TEMPLATE.read_bytes()
    prompts = {wk: build_prompt(tpl, name) for wk, name in works.items()}
    # 发出的 prompt 原文（字节精确）另存一份；runner 的 prompts/<job>.txt 可能经过换行翻译
    src_dir = run / "prompts_src"
    src_dir.mkdir(parents=True, exist_ok=True)
    for wk, b in prompts.items():
        (src_dir / f"V2A_orig__{wk}.txt").write_bytes(b)

    jobs = make_jobs(prompts, works)
    (run / "jobs.json").write_text(json.dumps(
        [{k: v for k, v in j.items() if k != "prompt"} | {"prompt_sha256": sha256_bytes(j["prompt"].encode("utf-8"))}
         for j in jobs], ensure_ascii=False, indent=2), encoding="utf-8")
    log(run, f"start dry_run={a.dry_run} jobs={len(jobs)} workers={MAX_WORKERS}")
    metas = runner.run_jobs(run, jobs, max_workers=MAX_WORKERS, timeout=JOB_TIMEOUT)

    rows = []
    retry_jobs = []
    for j, m in zip(jobs, metas):
        r = {"job_id": j["job_id"], "model_key": j["model_key"], "work_key": j["work_key"],
             "sample": j["sample"], "status": m.get("status"), "seconds": m.get("seconds"),
             "retry_of": None, **assess(run, m)}
        rows.append(r)
        if r["suspect"]:
            rj = dict(j, job_id=j["job_id"] + "__retry1", extra=dict(j["extra"], retry_of=j["job_id"]))
            retry_jobs.append(rj)
    if retry_jobs:
        log(run, f"retry {len(retry_jobs)}: {[x['job_id'] for x in retry_jobs]}")
        rmetas = runner.run_jobs(run, retry_jobs, max_workers=MAX_WORKERS, timeout=JOB_TIMEOUT)
        for j, m in zip(retry_jobs, rmetas):
            rows.append({"job_id": j["job_id"], "model_key": j["model_key"], "work_key": j["work_key"],
                         "sample": j["sample"], "status": m.get("status"), "seconds": m.get("seconds"),
                         "retry_of": j["extra"]["retry_of"], **assess(run, m)})

    # 每个原始槽位：原件或重跑件里至少有一份 ok 且非 suspect
    usable = {}
    for r in rows:
        slot = r["retry_of"] or r["job_id"]
        usable.setdefault(slot, False)
        if r["status"] == "ok" and not r["suspect"]:
            usable[slot] = True
    write_report(run, rows, usable, a.dry_run)
    write_manifest(run, rows, prompts, a.dry_run)
    ok = all(usable.values())
    if ok:
        (run / "DONE").write_text(f"{len(usable)}/{len(usable)} slots usable\n", encoding="utf-8")
    else:
        bad = [k for k, v in usable.items() if not v]
        (run / "FAILED").write_text("no usable output: " + ", ".join(bad) + "\n", encoding="utf-8")
    log(run, f"end {'DONE' if ok else 'FAILED'}")
    print(f"{'DONE' if ok else 'FAILED'}  -> {run}", flush=True)
    return 0 if ok else 1


def log(run: Path, line: str):
    with (run / "run.log").open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {line}\n")


def smoke(runner) -> int:
    run = REAL_RUN / "_smoke"
    run.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%H%M%S")
    jobs = [{"job_id": f"smoke__{mk}__{stamp}", "model_key": mk, "prompt": "只回复：好",
             "max_attempts": 1, "extra": {"run": RUN_ID, "smoke": True}}
            for mk in ("gpro_web", "gflash_web")]
    metas = runner.run_jobs(run, jobs, max_workers=2, timeout=300)
    ok = True
    for m in metas:
        out = (run / m["output_file"]).read_text(encoding="utf-8") if m.get("output_file") else ""
        print(f"SMOKE {m['model_key']}: {m['status']} {m['seconds']}s out={out.strip()[:40]!r} err={m.get('error')}",
              flush=True)
        ok = ok and m["status"] == "ok"
    return 0 if ok else 1


def write_report(run: Path, rows, usable, dry_run: bool):
    L = [f"# run132 V2A 原版 × Gemini 基线{'（干跑，mock）' if dry_run else ''}", "",
         f"生成时间：{datetime.now():%Y-%m-%d %H:%M:%S}", "",
         "提示词 = prompts/A_orig_V2A.txt 仅替换 {{WORK}}（原文见 prompts_src/）。"
         "以下只列机械指标，不做质量判断。suspect = 代理固定道歉句 / 拒答 / "
         f"<{FAST_SECONDS}s 却有 ≥{FAST_MIN_CHARS} 字 / 失败；suspect 已用新 job_id 重跑一次，原件保留。", "",
         "| job | 模型 | 作品 | 状态 | 耗时(s) | 字数 | 含 mm. 标记 | 段落数 | suspect |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        sus = "是：" + "; ".join(r["suspect_reasons"]) if r["suspect"] else "否"
        mm = f"是（{r['mm_markers']}）" if r["has_mm"] else "否"
        L.append(f"| {r['job_id']} | {r['model_key']} | {r['work_key']} | {r['status']} | {r['seconds']} | "
                 f"{r['chars']} | {mm} | {r['paragraphs']} | {sus} |")
    bad = [k for k, v in usable.items() if not v]
    L += ["", f"可用槽位：{sum(usable.values())}/{len(usable)}" + (f"；无可用产物：{', '.join(bad)}" if bad else ""),
          "", "原始产物：outputs/<job>.md，outputs/raw/，meta/<job>.json；作业清单 jobs.json。"]
    (run / "report.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def write_manifest(run: Path, rows, prompts, dry_run: bool):
    def hashes(sub):
        d = run / sub
        if not d.exists():
            return {}
        return {str(p.relative_to(run)).replace("\\", "/"): sha256_bytes(p.read_bytes())
                for p in sorted(d.rglob("*")) if p.is_file()}
    man = {
        "run_id": RUN_ID, "dry_run": dry_run, "created": datetime.now().isoformat(timespec="seconds"),
        "git_commit": git_head(),
        "template": {"path": "prompts/A_orig_V2A.txt", "sha256": sha256_bytes(TEMPLATE.read_bytes())},
        "works_md_sha256": sha256_bytes(WORKS_MD.read_bytes()),
        "sent_prompts_sha256": {wk: sha256_bytes(b) for wk, b in prompts.items()},
        "plan": PLAN, "max_workers": MAX_WORKERS, "job_timeout_s": JOB_TIMEOUT,
        "prompts_sha256": {**hashes("prompts_src"), **hashes("prompts")},
        "outputs_sha256": hashes("outputs"),
        "meta_sha256": hashes("meta"),
        "rows": rows,
    }
    (run / "run_manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
