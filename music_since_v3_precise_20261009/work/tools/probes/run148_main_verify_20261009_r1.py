"""Finite isolated r7 main verification; frozen C5/C6 reproducers kept unchanged."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REVISION = "run148_e7_flash_diag_r7"
BASE = Path(__file__).with_name("run144_145_main_verify_20261009_r1.py")
spec = importlib.util.spec_from_file_location("run144_145_main_verify_20261009_r1", BASE)
h = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = h
spec.loader.exec_module(h)


def fixture(root):
    module = h.load(root / "tools/tests" / ("test_" + REVISION + ".py"), "main_r7_fixtures")
    def compatibility(attr):
        if attr in ("Run144Tests", "Run146Tests"):
            return module.Run148Tests
        raise AttributeError(attr)
    module.__getattr__ = compatibility
    return module


def snapshot(root):
    rows = h.snapshot(root)
    paths = []
    for revision in ("run146_e7_flash_diag_r6", "run147_thread_resume_r6", REVISION):
        paths.extend((root / "runs" / revision).rglob("*"))
        paths.append(root / "tools/tests" / ("test_" + revision + ".py"))
    for name in ("run144145_main_verify_20261009_r1", "run146147_main_verify_20261009_r1", "run146_numeric_binding_probe_20261009_r1"):
        paths.append(root / "notes/research" / name / "report.json")
    for name in ("run144145_r5_and_run146147_r6_main_disposition_20261009.md", "integrity_v8_main_disposition_20261009_r2.md"):
        paths.append(root / "notes/research" / name)
    paths.extend((Path(__file__), BASE, Path(__file__).with_name("build_run148_r7_20261009.py"),
        Path(__file__).with_name("run146_numeric_binding_probe_20261009_r1.py")))
    for path in paths:
        if path.is_file():
            rows[path.relative_to(root).as_posix()] = {"bytes": path.stat().st_size, "sha256": h.sha(path.read_bytes())}
    return rows


def worker(root, out, mode):
    if mode == "numeric":
        # Replay the exact six C6 inputs, changing only the module/class lookup.
        original_load = h.load
        def bind_r7(path, name):
            if Path(path).name == "test_run146_e7_flash_diag_r6.py":
                return fixture_original(root, name)
            return original_load(path, name)
        def fixture_original(root, name):
            module = original_load(root / "tools/tests" / ("test_" + REVISION + ".py"), name)
            module.__getattr__ = lambda attr: module.Run148Tests if attr == "Run146Tests" else (_ for _ in ()).throw(AttributeError(attr))
            return module
        h.load = bind_r7
        frozen = original_load(Path(__file__).with_name("run146_numeric_binding_probe_20261009_r1.py"), "frozen_c6_reproducer")
        sys.argv = [str(Path(__file__)), "--root", str(root), "--out-dir", str(out)]
        rc = frozen.main()
        h.save(out / "binding_seam.json", {"schema": "frozen-c6-r7-binding/1", "legacy_report_label": "r6-numeric-binding-main/1",
            "actual_revision": REVISION, "change": "Only test module and class lookup; exact frozen C6 mutations and expectations unchanged.",
            "frozen_probe_sha256": h.sha(Path(frozen.__file__).read_bytes()), "returncode": rc})
        return rc
    (out / "scratch").mkdir()
    tempfile.tempdir = str(out / "scratch")
    blocked, original = h.guard(out)
    guards = h.negatives(root, original)
    f = fixture(root)
    data = {"schema": "r7-main-worker/1", "revision": REVISION, "mode": mode, "guard_negatives": guards,
        "real_model_submissions": 0, "provider_or_model_cli_invocations": 0, "music_acceptance": "NOT_PERFORMED"}
    if mode == "suites":
        result = unittest.TextTestRunner(verbosity=2, resultclass=h.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromModule(f))
        data.update(tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
            tests=result.rows, was_successful=result.wasSuccessful(),
            first_full_mock_submissions=f.Run148Tests.first_result["new_mock_submissions"])
    elif mode == "c5":
        rows = h.receipt144_challenges(f, out)
        data.update(checks=rows, legacy_check_labels="run144 names retained; actual frozen r7 suite and ingress", was_successful=all(row["passed"] for row in rows))
    else:
        g = h.load(root / "runs" / REVISION / "go.py", "r7_readonly_preflight")
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            rc = g.main(["--real"])
        raw = stream.getvalue().encode("utf-8")
        with (out / "stdout_callback.bin").open("xb") as file:
            file.write(raw)
        data.update(was_successful=rc == 3, returncode=rc, expected_returncode=3,
            stdout_callback_sha256=h.sha(raw), scope="In-process real CLI entry callback; no child/model CLI invoked.")
    data["guard_blocked_counts"] = blocked
    data["guard_scope"] = "Finite Python audit/class-preserving process guard, not OS sandbox or containment of malicious native code."
    h.save(out / "worker_report.json", data)
    print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    return 0 if data["was_successful"] and all(row["passed"] for row in guards) and blocked == {"process": 4, "network": 1, "write": 1} else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--worker", choices=("suites", "c5", "numeric", "preflight"))
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out_dir.resolve()
    if args.worker:
        return worker(root, out, args.worker)
    out.mkdir(parents=False, exist_ok=False)
    before = snapshot(root)
    h.save(out / "protected_before.json", before)
    manifest = json.loads((root / "runs" / REVISION / "manifest.json").read_bytes())
    checks = {"runs/" + REVISION + "/go.py": manifest["artifacts"]["go_py_sha256"],
        "runs/" + REVISION + "/README.md": manifest["artifacts"]["readme_sha256"],
        "tools/tests/test_" + REVISION + ".py": manifest["artifacts"]["test_py_sha256"], **manifest["frozen_input_sha256"]}
    report = {"schema": "r7-main-isolated-offline/1", "date": "2026-10-09", "revision": REVISION,
        "probe_sha256": h.sha(Path(__file__).read_bytes()), "base_harness_sha256": h.sha(BASE.read_bytes()),
        "manifest_checks": [{"path": path, "matches": h.sha((root / path).read_bytes()) == digest} for path, digest in checks.items()],
        "commands": [], "music_acceptance": "NOT_PERFORMED", "production_ready": False,
        "real_gate_changed": False, "two_w_hold_changed": False, "independent_review": "PENDING_AT_PROBE_CREATION"}
    for mode in ("suites", "c5", "numeric", "preflight"):
        child_out = out / mode
        if mode != "numeric":
            child_out.mkdir()
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(Path(__file__).resolve()), "--root", str(root), "--out-dir", str(child_out), "--worker", mode]
        start = time.monotonic()
        try:
            done = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
            raw_out, raw_err, rc, timeout = done.stdout, done.stderr, done.returncode, False
        except subprocess.TimeoutExpired as exc:
            raw_out, raw_err, rc, timeout = exc.stdout or b"", exc.stderr or b"", None, True
        if not child_out.exists():
            child_out.mkdir()
        for channel, raw in (("stdout", raw_out), ("stderr", raw_err)):
            with (child_out / (channel + ".bin")).open("xb") as stream:
                stream.write(raw)
        row = {"mode": mode, "argv": argv, "returncode": rc, "timed_out": timeout,
            "elapsed_seconds": round(time.monotonic() - start, 3), "stdout_sha256": h.sha(raw_out), "stderr_sha256": h.sha(raw_err),
            "stdout_bytes": len(raw_out), "stderr_bytes": len(raw_err)}
        result = child_out / ("report.json" if mode == "numeric" else "worker_report.json")
        if result.is_file():
            row["result"] = json.loads(result.read_bytes())
        report["commands"].append(row)
    after = snapshot(root)
    h.save(out / "protected_after.json", after)
    report["protected_unchanged"] = before == after
    report["changed_protected_paths"] = [path for path in sorted(set(before) | set(after)) if before.get(path) != after.get(path)]
    h.save(out / "report.json", report)
    print(json.dumps({"output": str(out), "commands": [{key: row[key] for key in ("mode", "returncode", "timed_out", "elapsed_seconds")} for row in report["commands"]],
        "protected_unchanged": report["protected_unchanged"], "production_ready": False}, ensure_ascii=False))
    return 0 if before == after and all(row["returncode"] == 0 for row in report["commands"]) and all(row["matches"] for row in report["manifest_checks"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
