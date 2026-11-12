#!/usr/bin/env python3
"""交付打包工具 v2（只读源数据，不调用任何模型，不产生子进程）。

相对 v1 新增（主控 2026-10-10）：
  --evidence-dir 可重复：把 recovery / parallel / adaptation 等指定可信证据目录
    以 evidence/<name>/ 前缀归档（<name> 为目录 basename）。
  归档卫生：
    跳过 __pycache__/、*.pyc、测试 zip（test_*.zip / *_test.zip / *.sha256 伴随）、
    临时大 log（*.log 超过 --max-log-bytes，默认 2MB，超限只记清单不归档）、
    *.pid 临时进程文件。
  敏感排除（沿用 v1 并扩展）：
    token/credential/secret/apikey/dpapi/password/browser profile/session-state 等
    按名命中即排除；owned job 池默认不整目录归档，普通 provider 证据只白名单：
    started.json / result.json / submitted.json / response.txt / response_sha 文件、
    capture-binding-diagnostic.json / handoff-summary.json /
    execution-worker-attestation.json / http-worker-console.txt / requests.jsonl，
    其余（memory.jsonl / session-state.dpapi / sealed / runtime-snapshot 等）一律排除。
    --owned-job 指向单个已验证恢复源 job 时，仅按上述白名单归档该 job。
  普通 provider 证据“只白名单 started/submitted/result/response 及必要安全 diagnostic，
    不整 runs 目录塞 zip”。

ZIP 写完读回核验：条目/hash/数量，并写 .sha256。
仅写当前验证 test 与新 report root，不作最终 Downloads 包（由主控按真实完成度调用）。

用法（必须 -I）：
  python -I package_delivery_v2.py --data-root D:/musicclaude/_dl_latest_zip_work --report-dir <新report root> --evidence-dir D:/musicclaude/_baseline_recovery_control_20261010 --output <新唯一ZIP>
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

EXCLUDE_SUBSTR = ("token", "credential", "secret", "apikey", "api_key", "dpapi",
                  "password", "passwd", ".pem", "session-state", "session_state",
                  "browser_profile", "browser-profile", "sealed", "ciphertext")
EXCLUDE_DIRNAMES = {"browser", "profile", "profiles", "session-state", "session_state", "dpapi",
                    "__pycache__"}
CONTROL_ALLOW = ("validate_delivery.py", "validate_delivery_v2.py",
                 "package_delivery.py", "package_delivery_v2.py", "REPORT_OUTLINE.md",
                 "delivery_validation.json", "delivery_validation_summary.txt",
                 "delivery_validation_v2.json", "delivery_validation_v2_summary.txt")
# 测试 zip：只跳过测试产物，不跳过生产包（当前不产生产包，仅规则保留）
TESTZIP_RE = ("test_", "_test.zip")
# owned job 白名单（普通 provider 证据）
OWNED_ALLOW = {"started.json", "result.json", "submitted.json", "response.txt",
               "capture-binding-diagnostic.json", "handoff-summary.json",
               "execution-worker-attestation.json", "http-worker-console.txt",
               "requests.jsonl"}


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def excluded(rel: str) -> str | None:
    low = rel.replace("\\", "/").lower()
    parts = low.split("/")
    if any(p in EXCLUDE_DIRNAMES for p in parts):
        return "excluded-dir"
    name = parts[-1]
    if name.endswith(".pid"):
        return "ephemeral-pid"
    if name.endswith(".pyc"):
        return "bytecode"
    for s in EXCLUDE_SUBSTR:
        if s in name:
            return f"name-pattern:{s}"
    return None


def main():
    ap = argparse.ArgumentParser(description="交付打包 v2（只读，不调用模型）")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--report-dir", default=None)
    ap.add_argument("--evidence-dir", action="append", default=[], help="可重复：指定可信证据目录")
    ap.add_argument("--owned-job", default=None, help="单个 owned 源 job 目录（仅白名单归档）")
    ap.add_argument("--max-log-bytes", type=int, default=2 * 1024 * 1024)
    ap.add_argument("--output", required=True, help="新的唯一 ZIP 路径；目标不得已存在")
    ap.add_argument("--trusted-dir", default=None)
    a = ap.parse_args()
    data_root = Path(a.data_root)
    trusted = Path(a.trusted_dir) if a.trusted_dir else Path(__file__).resolve().parent
    report_dir = Path(a.report_dir) if a.report_dir else trusted
    out = Path(a.output)
    if not data_root.is_dir():
        print(f"ERROR: --data-root 不存在: {data_root}", file=sys.stderr)
        return 2
    if out.exists():
        print(f"ERROR: 目标已存在，拒绝覆盖: {out}", file=sys.stderr)
        return 2
    sidecar = Path(str(out) + ".sha256")
    if sidecar.exists():
        print(f"ERROR: sha sidecar 已存在，拒绝覆盖: {sidecar}", file=sys.stderr)
        return 2
    if out.parent and str(out.parent) not in ("", "."):
        out.parent.mkdir(parents=True, exist_ok=True)
    entries: list[tuple[str, Path]] = []
    skipped: list[dict] = []

    def consider(src: Path, arc: str):
        reason = excluded(arc)
        if reason:
            skipped.append({"file": arc, "reason": reason})
            return
        nm = src.name
        if nm.endswith(".zip") and (nm.startswith("test_") or "_test" in nm):
            skipped.append({"file": arc, "reason": "test-zip-nesting"})
            return
        if nm.endswith(".sha256") and (nm.startswith("test_") or "_test" in nm):
            skipped.append({"file": arc, "reason": "test-zip-sidecar"})
            return
        if nm.endswith(".log") and src.stat().st_size > a.max_log_bytes:
            skipped.append({"file": arc, "reason": f"large-temp-log:{src.stat().st_size}"})
            return
        entries.append((arc, src))

    out_resolved = None
    try:
        out_resolved = out.resolve()
    except OSError:
        pass
    for p in sorted(data_root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(data_root).as_posix()
        try:
            if out_resolved is not None and p.resolve() == out_resolved:
                skipped.append({"file": rel, "reason": "output-itself"})
                continue
        except OSError:
            pass
        consider(p, f"data/{rel}")
    # control：v2.1 起归档整个 --report-dir（敏感 filter 全覆盖），避免 CONTROL_ALLOW
    # 漏掉最终 REPORT.md；report/ 前缀优先，若与 trusted 同名旧文件冲突，report 最新版为准
    # （trusted 同名旧文件跳过并记清单）。
    seen_control: set[str] = set()
    if report_dir.is_dir():
        for p in sorted(report_dir.rglob("*")):
            if p.is_dir():
                continue
            rel = p.relative_to(report_dir).as_posix()
            try:
                if out_resolved is not None and p.resolve() == out_resolved:
                    skipped.append({"file": f"report/{rel}", "reason": "output-itself"})
                    continue
            except OSError:
                pass
            before = len(entries)
            consider(p, f"report/{rel}")
            if len(entries) > before:
                seen_control.add(Path(rel).name)
    for name in CONTROL_ALLOW:
        if name in seen_control:
            continue
        p = trusted / name
        if p.is_file():
            consider(p, f"control/{name}")
    for edir in a.evidence_dir:
        ed = Path(edir)
        if not ed.is_dir():
            print(f"ERROR: --evidence-dir 不存在: {ed}", file=sys.stderr)
            return 2
        tag = ed.name
        for p in sorted(ed.rglob("*")):
            if p.is_dir():
                continue
            rel = p.relative_to(ed).as_posix()
            consider(p, f"evidence/{tag}/{rel}")
    if a.owned_job:
        oj = Path(a.owned_job)
        if not oj.is_dir():
            print(f"ERROR: --owned-job 不存在: {oj}", file=sys.stderr)
            return 2
        for fn in sorted(OWNED_ALLOW):
            p = oj / fn
            if p.is_file():
                consider(p, f"evidence_owned_job/{oj.name}/{fn}")
            else:
                skipped.append({"file": f"evidence_owned_job/{oj.name}/{fn}", "reason": "whitelist-absent"})
    if not entries:
        print("ERROR: 无可打包文件", file=sys.stderr)
        return 2
    manifest = []
    with zipfile.ZipFile(out, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, p in entries:
            blob = p.read_bytes()  # 只读
            z.writestr(arc, blob)
            manifest.append({"arc": arc, "sha256": sha_bytes(blob), "bytes": len(blob),
                             "source": str(p)})
        z.writestr("delivery_SHA256_MANIFEST.json",
                   json.dumps({"files": [{"arc": m["arc"], "sha256": m["sha256"], "bytes": m["bytes"]} for m in manifest],
                               "excluded": skipped}, ensure_ascii=False, indent=2) + "\n")
    with zipfile.ZipFile(out, "r") as z:
        names = z.namelist()
        by_manifest = {m["arc"]: m["sha256"] for m in manifest}
        errors = []
        for arc, expect in by_manifest.items():
            try:
                actual = sha_bytes(z.read(arc))
            except KeyError:
                errors.append(f"missing:{arc}")
                continue
            if actual != expect:
                errors.append(f"hash-mismatch:{arc}")
        if "delivery_SHA256_MANIFEST.json" not in names:
            errors.append("missing:delivery_SHA256_MANIFEST.json")
        count_ok = (len([n for n in names if n != "delivery_SHA256_MANIFEST.json"]) == len(manifest))
        if not count_ok:
            errors.append(f"count mismatch zip={len(names)} manifest={len(manifest)}")
        if errors:
            print("VERIFY-FAILED:", file=sys.stderr)
            for e in errors:
                print(f"  {e}", file=sys.stderr)
            return 3
    digest = sha_bytes(out.read_bytes())
    (Path(str(out) + ".sha256")).write_text(f"{digest}  {out.name}\n", encoding="utf-8")
    total = sum(m["bytes"] for m in manifest)
    print(f"packed_files={len(manifest)} total_bytes={total} excluded={len(skipped)}")
    print(f"zip={out}")
    print(f"sha256={digest}")
    print(f"wrote {out}.sha256")
    print("verify=OK (entries/hash/count re-read)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
