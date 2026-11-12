#!/usr/bin/env python3
"""交付打包工具（只读源数据，不调用任何模型，不产生子进程）。

把冻结实验数据 + 可信控制代码 + 验证报告打成一个 ZIP，供主控后续按真实完成度调用。
现在不要打成“最终”ZIP：未来主控按真实完成情况传 --output 调用本工具。

包含：
  data/...   原冻结 prompt（jobs/、prompts/）、source（inputs/）、docs/、jobs 私有 mapping（含 private/）、
             所有原始 results/、reports/、运行日志（*.log、*.note.txt、*.ps1 运行记录）。
排除（附排除清单）：
  token/凭证/DPAPI/browser profile/session-state/绝对 secret 源文件名模式，以及 *.pid 临时进程文件。
  control/... 本可信目录的验证工具与报告（validate_delivery.py、package_delivery.py、
             REPORT_OUTLINE.md、delivery_validation.json、delivery_validation_summary.txt，存在才附）。

ZIP 写完后自动读回核验：条目数量、逐文件 hash、总字节；并写 .sha256 伴随文件。

用法（必须 -I）：
  python -I package_delivery.py --data-root D:/musicclaude/_dl_latest_zip_work --report-dir D:/musicclaude/_baseline_delivery_control_20261010 --output D:/musicclaude/_baseline_delivery_control_20261010/test_delivery_20261010.zip
"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

EXCLUDE_SUBSTR = ("token", "credential", "secret", "apikey", "api_key", "dpapi",
                  "password", "passwd", ".pem", "session-state", "session_state",
                  "browser_profile", "browser-profile")
EXCLUDE_DIRNAMES = {"browser", "profile", "profiles", "session-state", "session_state", "dpapi"}
CONTROL_ALLOW = ("validate_delivery.py", "package_delivery.py", "REPORT_OUTLINE.md",
                 "delivery_validation.json", "delivery_validation_summary.txt")


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
    for s in EXCLUDE_SUBSTR:
        if s in name:
            return f"name-pattern:{s}"
    return None


def main():
    ap = argparse.ArgumentParser(description="交付打包（只读，不调用模型）")
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--report-dir", default=None)
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
    if out.parent and str(out.parent) not in ("", "."):
        out.parent.mkdir(parents=True, exist_ok=True)
    entries: list[tuple[str, Path]] = []
    skipped: list[dict] = []
    for p in sorted(data_root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(data_root).as_posix()
        # 绝不把输出 ZIP 自身（若放在数据目录内）再打进去
        try:
            if p.resolve() == out.resolve():
                skipped.append({"file": rel, "reason": "output-itself"})
                continue
        except OSError:
            pass
        reason = excluded(rel)
        if reason:
            skipped.append({"file": rel, "reason": reason})
            continue
        entries.append((f"data/{rel}", p))
    for name in CONTROL_ALLOW:
        for base in (trusted, report_dir):
            p = base / name
            if p.is_file():
                entries.append((f"control/{name}", p))
                break
    if not entries:
        print("ERROR: 无可打包文件", file=sys.stderr)
        return 2
    manifest = []
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, p in entries:
            blob = p.read_bytes()  # 只读
            z.writestr(arc, blob)
            manifest.append({"arc": arc, "sha256": sha_bytes(blob), "bytes": len(blob),
                             "source": str(p)})
        z.writestr("delivery_SHA256_MANIFEST.json",
                   json.dumps({"files": [{"arc": m["arc"], "sha256": m["sha256"], "bytes": m["bytes"]} for m in manifest],
                               "excluded": skipped}, ensure_ascii=False, indent=2) + "\n")
    # 读回核验：条目/hash/数量
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
