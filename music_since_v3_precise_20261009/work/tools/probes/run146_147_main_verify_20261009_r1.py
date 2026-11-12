"""Reuse the frozen r5 finite offline harness with explicit r6 fixture bindings.
All old driver/suite/report paths remain protected. No provider execution.
"""
import argparse
import importlib.util
import sys
from pathlib import Path

BASE = Path(__file__).with_name("run144_145_main_verify_20261009_r1.py")
spec = importlib.util.spec_from_file_location("frozen_r5_main_offline_harness", BASE)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
load_original = base.load
snapshot_original = base.snapshot

REVISIONS = {"run144_e7_flash_diag_r5": "run146_e7_flash_diag_r6",
             "run145_thread_resume_r5": "run147_thread_resume_r6"}


def revised_load(path, name):
    transformed = str(path)
    for old, new in REVISIONS.items():
        if Path(path).name == "test_" + old + ".py":
            transformed = transformed.replace("test_" + old + ".py", "test_" + new + ".py")
    module = load_original(Path(transformed), name)
    if Path(transformed).name == "test_run146_e7_flash_diag_r6.py":
        # The old harness accesses one fixed class name. A module __getattr__ seam
        # preserves that access without adding a second class to unittest's dir().
        def compatibility(attr):
            if attr == "Run144Tests":
                return module.Run146Tests
            raise AttributeError(attr)
        module.__getattr__ = compatibility
    return module


def protected_snapshot(root):
    rows = snapshot_original(root)
    for revision in REVISIONS.values():
        paths = list((root / "runs" / revision).rglob("*"))
        paths.append(root / "tools/tests" / ("test_" + revision + ".py"))
        for path in paths:
            if path.is_file():
                rows[path.relative_to(root).as_posix()] = {"bytes": path.stat().st_size, "sha256": base.sha(path.read_bytes())}
    return rows


def revision_manifest_parity(root):
    result = {"legacy_evidence_parity": evidence_original(root), "r6_manifest_checks": []}
    for revision in REVISIONS.values():
        import json
        manifest = json.loads((root / "runs" / revision / "manifest.json").read_bytes())
        artifact = manifest["artifacts"]
        expected = {"runs/" + revision + "/go.py": artifact["go_py_sha256"],
            "runs/" + revision + "/README.md": artifact["readme_sha256"],
            "tools/tests/test_" + revision + ".py": artifact["test_py_sha256"], **manifest["frozen_input_sha256"]}
        result["r6_manifest_checks"].append({"run": revision, "checks": [{"path": path,
            "matches": base.sha((root / path).read_bytes()) == digest} for path, digest in expected.items()]})
    result["harness"] = {"base_source_sha256": base.sha(BASE.read_bytes()),
        "binding_seam": "Only the two test module paths and a class lookup are redirected to r6. Old source/reports are unchanged.",
        "probe_source_sha256": base.sha(Path(__file__).read_bytes())}
    return result


evidence_original = base.evidence_parity
base.load = revised_load
base.snapshot = protected_snapshot
base.evidence_parity = revision_manifest_parity


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--worker", choices=("suites", "challenges", "preflight"))
    args = parser.parse_args()
    if args.worker == "preflight":
        # Base preflight intentionally binds the old run144 direct module. The
        # current r6 suites already verify both direct r6 blocked entry paths;
        # keep base captured preflight explicitly labelled legacy in this probe.
        pass
    if args.worker:
        raise SystemExit(base.worker(args.root.resolve(), args.out_dir.resolve(), args.worker))
    base.__file__ = str(Path(__file__).resolve())
    raise SystemExit(base.main())
