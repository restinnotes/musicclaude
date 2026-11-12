"""Hash only the explicitly protected, non-secret input files and named old-run trees."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
FIXED_FILES = (
    "runs/run142_e7_flash_diag_r4/go.py", "runs/run142_e7_flash_diag_r4/README.md",
    "runs/run142_e7_flash_diag_r4/manifest.json",
    "runs/run143_thread_resume_r4/go.py", "runs/run143_thread_resume_r4/README.md",
    "runs/run143_thread_resume_r4/manifest.json",
    "tools/tests/test_run139_e7_flash_diag_r3.py", "tools/tests/test_run141_thread_resume_r3.py",
    "tools/tests/test_run142_e7_flash_diag_r4.py", "tools/tests/test_run143_thread_resume_r4.py",
    "notes/research/run142_143_main_verify_20261009_r2/report.json",
    "notes/research/run142_143_main_disposition_20261009_r2.md",
    "runs/run130_thread_e6/beads_clean.md", "runs/run130_thread_e6/steps.json",
    "runs/run124_render/surface__B__gpt56w__op60.md",
    "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gpro_web__s3.md",
    "runs/run132_v2a_gemini_baseline/meta/run132__op60__gpro_web__s3.json",
    "runs/run132_v2a_gemini_baseline/outputs/run132__op60__gflash_web__s1.md",
    "runs/run132_v2a_gemini_baseline/meta/run132__op60__gflash_web__s1.json",
    "prompts/versions/WHY_GATE_v4.txt", "prompts/tooling/MECH_v1.txt",
    "prompts/tooling/MECH_AUDIT_v0.txt", "prompts/versions/E7_SURFACE_v0.txt",
    "prompts/tooling/E7_COMPARE_v0.txt", "prompts/versions/C7_STEP_v2.txt",
    "prompts/versions/C7_STEP_v3.txt", "prompts/versions/CENTER_v0.txt",
    "prompts/tooling/THREAD_IDENT_v0.txt", "prompts/tooling/THREAD_COMPARE_v0.txt",
    "03_CONSTITUTION_CHECK.md", "runs/run133_thread_spec/06_ACCEPTANCE_CRITERIA.md",
)
OLD_RUN_TREES = ("runs/run141_thread_resume_r3", "runs/run142_e7_flash_diag_r4",
                 "runs/run143_thread_resume_r4")
ABSENCE_PROBES = ("runs/run139_e7_flash_diag_r3", "runs/run133_thread_spec/06_ACCEPTANCE_CRITERIA.md",
                  "runs/run135", "production", "gate", "hold")
SENSITIVE_NAME = re.compile(r"(?i)(credential|cookie|token|secret|\.env|\.pem$|\.key$|auth)")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "before"
    files = {}
    for relative in FIXED_FILES:
        path = ROOT / relative
        if path.is_file() and not SENSITIVE_NAME.search(path.name):
            files[relative] = {"present": True, "size": path.stat().st_size, "sha256": digest(path)}
        else:
            files[relative] = {"present": False}
    inventories = {}
    for relative in OLD_RUN_TREES:
        folder = ROOT / relative
        entries = {}
        if folder.is_dir():
            for path in sorted(folder.rglob("*")):
                if path.is_file() and not SENSITIVE_NAME.search(path.name):
                    entries[path.relative_to(ROOT).as_posix()] = {
                        "size": path.stat().st_size, "sha256": digest(path)}
        inventories[relative] = entries
    absence = {relative: (ROOT / relative).exists() for relative in ABSENCE_PROBES}
    payload = {"snapshot": label, "fixed_protected_files": files,
               "old_run_inventories": inventories, "presence_only_probes": absence,
               "scope_note": "No run140 source archive or shared v7 path was enumerated, hashed, read, or written."}
    output = EVIDENCE / ("protected_" + label + ".json")
    output.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(json.dumps({"snapshot": label, "fixed_hash_count": sum(
        row.get("present", False) for row in files.values()),
        "old_run_inventory_counts": {key: len(value) for key, value in inventories.items()},
        "output": str(output)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
