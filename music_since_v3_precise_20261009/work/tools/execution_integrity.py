"""新调用的身份、只读续跑、脱敏和进程边界；旧历史不补写。"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

VERSION = "20261009.1"
ROOT = Path(__file__).resolve().parents[1]
PROTECT_RE = re.compile(r"\b403\b|\b429\b|challenge|cool[\s_-]?down|rate[\s_-]?limit|too many requests", re.I)
PRIVATE_KEY_RE = re.compile(r"cookie|authorization|password|credential|session_handle|access_token|refresh_token|api_key|secret", re.I)
PRIVATE_VALUE_RE = re.compile(r"(?i)(bearer\s+)[^\s\"']+|((?:secret|password|api[_-]?key|access[_-]?token|refresh[_-]?token|session_handle|cookie)\s*[=:]\s*)[^\s,;\"']+")


class ArtifactConflict(RuntimeError):
    pass


class PolicyBlocked(RuntimeError):
    pass


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(obj):
    return sha_text(canonical(obj))


def safe_text(text):
    def sub(m):
        return (m.group(1) or m.group(2) or "") + "<redacted>"
    text = PRIVATE_VALUE_RE.sub(sub, str(text))
    text = re.sub(r'(?im)^((?:cookie|set-cookie|authorization)\s*:\s*).+$',
                  r'\1<redacted>', text)
    return re.sub(r'''(?i)(["']?(?:secret|password|api[_-]?key|access[_-]?token|refresh[_-]?token|session_handle|cookie)["']?\s*[=:]\s*)(["'])(.*?)\2''',
                  lambda m: m.group(1) + m.group(2) + "<redacted>" + m.group(2), text)


def safe_records(text):
    """JSON/JSONL raw 逐字段脱敏；非结构化日志再按敏感赋值/HTTP头脱敏。"""
    try:
        return json.dumps(safe_metadata(json.loads(text)), ensure_ascii=False, indent=2)
    except (ValueError, TypeError):
        lines = []
        for line in str(text).splitlines(keepends=True):
            try:
                ending = "\n" if line.endswith("\n") else ""
                lines.append(json.dumps(safe_metadata(json.loads(line)), ensure_ascii=False) + ending)
            except (ValueError, TypeError):
                lines.append(safe_text(line))
        return "".join(lines)


def safe_metadata(obj):
    if isinstance(obj, dict):
        return {str(k): ("<redacted>" if PRIVATE_KEY_RE.search(str(k)) else safe_metadata(v))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_metadata(v) for v in obj]
    if isinstance(obj, str):
        return safe_text(obj)
    return obj


def write_text(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        f.write(text)


def write_json(path, obj):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    write_text(tmp, json.dumps(safe_metadata(obj), ensure_ascii=False, indent=2))
    tmp.replace(p)


def check_policy(model_key):
    if model_key.startswith("opus") or model_key.startswith("sol"):
        raise PolicyBlocked("2026-10-09: 禁止新增 Opus/Sol 调用；历史产物只读")
    if model_key in ("muse", "muse_web", "muse_exec"):
        raise PolicyBlocked("Muse 必须用 T3 delegate_task / claude-proxy / muse-spark-1.3-contributor-free / xhigh")


def canonical_model(key):
    return {"gpro_web": "gpro", "gflash_web": "gflash",
            "gflash37_web": "gflash37", "luna": "luna_noweb",
            "muse_web": "muse", "muse_exec": "muse"}.get(key, key)


def source_fingerprint(root, relative_dirs, suffixes=(".py", ".js", ".cjs", ".mjs", ".ts", ".cmd", ".bat")):
    root = Path(root)
    records = {}
    for rel in relative_dirs:
        base = root / rel
        paths = [base] if base.is_file() else base.rglob("*") if base.is_dir() else []
        for p in paths:
            if not p.is_file() or p.suffix.lower() not in suffixes:
                continue
            if any(x in ("node_modules", "__pycache__", ".git") for x in p.parts):
                continue
            records[p.relative_to(root).as_posix()] = sha_file(p)
    return {"sha256": digest(records), "files": len(records), "missing": not records}


def implementation_identity(paths):
    return {Path(p).name: sha_file(p) for p in paths}


def job_identity(job, producer):
    return {"schema": VERSION, "producer": producer,
            "model_key": job["model_key"], "prompt_sha256": sha_text(job["prompt"]),
            "prompt_version": job.get("prompt_version", ""),
            "prompt_template": job.get("prompt_template"),
            "work_key": job.get("work_key", ""), "sample": job.get("sample", 0),
            "forbid_tools": sorted(job.get("forbid_tools") or []),
            "extra_sha256": digest(safe_metadata(job.get("extra") or {})),
            "image_sha256": {str(p): sha_file(p) for p in (job.get("extra") or {}).get("images", [])},
            "sampling_key": job.get("sampling_key", job["job_id"])}


def checked_resume(run_dir, job_id, identity):
    """只返回 exact identity + 非空/hash一致的完成输出；缺证据绝不补造。"""
    run_dir = Path(run_dir)
    mp = run_dir / "meta" / (job_id + ".json")
    if not mp.exists():
        return None
    data = json.loads(mp.read_text(encoding="utf-8"))
    if data.get("request_identity") != identity:
        raise ArtifactConflict("job_id 已存在但身份不一致/旧身份未知；请用新 run/job_id：" + job_id)
    if data.get("status") != "ok":
        raise ArtifactConflict("失败记录只读；重试需新 attempt job_id：" + job_id)
    rel = data.get("output_file")
    p = (run_dir / rel).resolve() if isinstance(rel, str) else None
    if p is None or not p.is_relative_to(run_dir.resolve()) or not p.is_file():
        raise ArtifactConflict("缓存输出缺失或越界：" + job_id)
    raw = p.read_bytes()
    if not raw.strip() or hashlib.sha256(raw).hexdigest() != data.get("response_sha256"):
        raise ArtifactConflict("缓存输出为空/哈希不符：" + job_id)
    pf = (run_dir / str(data.get("prompt_file", ""))).resolve()
    if not pf.is_relative_to(run_dir.resolve()) or not pf.is_file() or sha_file(pf) != identity["prompt_sha256"]:
        raise ArtifactConflict("缓存输入哈希不符：" + job_id)
    return dict(data, resumed=True, consumer_identity=identity["producer"])


class GlobalSlot:
    """直接 adapter 与 runner 共用 OS 文件锁，异常退出由 OS 释放。"""
    def __init__(self, pool, cap=1):
        self.pool, self.cap = pool, cap

    def __enter__(self):
        base = ROOT / "runs" / "_call_slots" / self.pool
        base.mkdir(parents=True, exist_ok=True)
        while True:
            for i in range(self.cap):
                fd = os.open(str(base / ("slot%03d" % i)), os.O_RDWR | os.O_CREAT)
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    if sys.platform == "win32":
                        import msvcrt
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    os.close(fd)
                    continue
                self.fd = fd
                return self
            time.sleep(.25)

    def __exit__(self, *exc):
        try:
            os.lseek(self.fd, 0, os.SEEK_SET)
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.fd, fcntl.LOCK_UN)
        finally:
            os.close(self.fd)
        return False


def run_process(argv, *, input=None, capture_output=True, timeout=None, **kw):
    """参数列表+bytes；本地超时回收本调用进程树，服务端状态仍未知、不得自动重发。"""
    if not capture_output:
        raise ValueError("only capture_output=True supported")
    if sys.platform != "win32":
        kw["start_new_session"] = True
    p = subprocess.Popen(argv, stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)
    try:
        out, err = p.communicate(input, timeout=timeout)
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"],
                           capture_output=True, timeout=30,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        else:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(p.pid, signal.SIGKILL)
        if p.poll() is None:
            p.kill()
        out, err = p.communicate(timeout=30)
        raise subprocess.TimeoutExpired(argv, timeout, output=out, stderr=err)
    return subprocess.CompletedProcess(argv, p.returncode, out, err)


def model_evidence(metadata, requested):
    """只采后端 model_slug/resolved_model_slugs；requested/model/experience不是实际型号证据。"""
    metadata = metadata if isinstance(metadata, dict) else {}
    found = []
    def visit(obj, path=""):
        if not isinstance(obj, dict):
            return
        for k, v in obj.items():
            at = (path + "." + k).lstrip(".")
            if k == "resolved_model_slugs" and isinstance(v, list):
                found.extend((at, x) for x in v if isinstance(x, str))
            elif k == "model_slug" and isinstance(v, str) and ("server" in path or "resolved" in path):
                found.append((at, v))
            elif isinstance(v, dict):
                visit(v, at)
    visit(metadata)
    normalize = lambda s: s.strip().lower().replace(".", "-").replace("_", "-")
    slugs = sorted(set(v for _, v in found))
    verdict = "unverified" if not slugs else "match" if all(normalize(s) == normalize(requested) for s in slugs) else "mismatch"
    return {"verdict": verdict, "server_slugs": slugs, "fields": sorted(set(k for k, _ in found)),
            "client_requested_model": metadata.get("model") or metadata.get("requested_model"),
            "requested_experience": (metadata.get("server_metadata_summary") or {}).get("requested_model_experience")
            if isinstance(metadata.get("server_metadata_summary"), dict) else None}
