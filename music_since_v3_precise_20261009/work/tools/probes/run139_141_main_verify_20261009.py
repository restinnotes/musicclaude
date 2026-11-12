"""主会话离线验收及最小对抗样本；不改旧 run，不启动模型或网络。"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(relative, name):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def snapshot(folder):
    return {str(p.relative_to(folder)): sha(p.read_bytes())
            for p in sorted(folder.rglob("*")) if p.is_file()}


def accepted(call):
    try:
        value = call()
        return {"accepted": True, "value": value}
    except Exception as exc:
        return {"accepted": False, "error_type": type(exc).__name__, "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    dest = Path(args.output_dir)
    dest.mkdir(parents=True, exist_ok=False)
    folders = [ROOT / "runs/run139_e7_flash_diag", ROOT / "runs/run141_thread_resume_r3"]
    before = [snapshot(p) for p in folders]
    commands = []
    for label, relative, more in (
        ("run139_tests", "tools/tests/test_run139_e7_flash_diag_r3.py", []),
        ("run141_tests", "tools/tests/test_run141_thread_resume_r3.py", []),
        ("run141_strict", "runs/run141_thread_resume_r3/go.py", ["--strict"]),
    ):
        argv = [sys.executable, "-X", "utf8", "-I", "-B", str(ROOT / relative), *more]
        start = time.monotonic()
        # 两套既有测试内部只用 mock/temp；strict 是只读 preflight。
        cp = subprocess.run(argv, cwd=str(ROOT.parent.parent), stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=180, check=False)
        elapsed = time.monotonic() - start
        for suffix, raw in (("stdout", cp.stdout), ("stderr", cp.stderr)):
            # UTF-8 严格解码；只保存这三条已审离线命令的原始安全输出。
            raw.decode("utf-8", "strict")
            with (dest / (label + "." + suffix + ".txt")).open("xb") as stream:
                stream.write(raw)
        commands.append({"label": label, "argv": argv, "returncode": cp.returncode,
                         "elapsed_seconds": elapsed, "stdout_bytes": len(cp.stdout),
                         "stderr_bytes": len(cp.stderr), "stdout_sha256": sha(cp.stdout),
                         "stderr_sha256": sha(cp.stderr), "real_model_submissions": 0})
    g139 = load("runs/run139_e7_flash_diag/go.py", "main_run139_offline_probe")
    g141 = load("runs/run141_thread_resume_r3/go.py", "main_run141_offline_probe")
    rows = []
    for label, raw in (("prefix", 'not a response {"x":1}'),
                       ("trailer", '{"x":1} failed'),
                       ("duplicate", '{"x":1,"x":2}'),
                       ("nonfinite", '{"x":NaN}')):
        value = g139.extract_json_object(raw)
        rows.append({"check": "run139_json_" + label, "accepted": value[0],
                     "scope": "synthetic text; complete-response boundary/strict JSON check"})
        rows.append({"check": "run141_json_" + label, **accepted(lambda raw=raw: g141.extract_json(raw)),
                     "scope": "synthetic text; complete-response boundary/strict JSON check"})
    rows.append({"check": "run141_multiple_json", **accepted(lambda: g141.extract_json('{"x":1}{"x":2}')),
                 "scope": "synthetic text; trailing second JSON silently ignored"})
    positions = tuple(g139.POSITIONS)
    mapping = dict(zip(positions, ("a", "b", "c")))
    payloads = {k: "MOCK_ONLY valid original quote" for k in mapping.values()}
    quoted = "“MOCK_ONLY valid original quote”以及“MOCK_ONLY nonexistent quotation”"
    review = {"ranking": list(positions), "best_moments": {p: quoted for p in positions},
              "worst_moments": {p: quoted for p in positions},
              "hindsight": {p: [] for p in positions}, "only_here": {p: "MOCK_ONLY" for p in positions},
              "why": "MOCK_ONLY"}
    parsed, error = g139.parse_compare(json.dumps(review, ensure_ascii=False), mapping, payloads)
    rows.append({"check": "run139_mixed_valid_invalid_quotes", "accepted": parsed is not None,
                 "error": error, "scope": "one exact quote masks an additional nonexistent quote"})
    slot = {"stage": "step", "chain_id": "v2_gpt56w", "version": "v2", "model_key": "gpt56w", "k": 1}
    fingerprint = {"driver_sha256": "1" * 64, "fingerprint_sha256": "2" * 64}
    identity = {"run_id": g141.RUN_ID, "work_key": g141.WORK_KEY, "slot": slot,
                "model_key": "gpt56w", "model_name": "MOCK_ONLY", "request_id": "unbound_request"}
    producer = {k: "MOCK_ONLY" for k in ("kind", "adapter", "producer_revision", "transport", "provider", "model")}
    producer["adapter_sha256"] = fingerprint["driver_sha256"]
    meta = {"identity": identity, "producer_identity": producer, "queue_stop": False,
            "fingerprint_sha256": fingerprint["fingerprint_sha256"], "execution_mode": "mock_only"}
    rows.append({"check": "run141_wrong_mock_request", **accepted(lambda: g141._validate_identity(meta, slot, fingerprint)),
                 "scope": "mixed and/or expression correctly rejects wrong request for mock_only"})
    nonmock = dict(meta)
    nonmock.pop("execution_mode")
    rows.append({"check": "run141_undeclared_execution_mode", **accepted(lambda: g141._validate_identity(nonmock, slot, fingerprint)),
                 "scope": "unsupported-mode validation gap, not evidence of an actual real route"})
    template_path = ROOT / g141.TEMPLATE_PATHS["ident"]
    template = template_path.read_text(encoding="utf-8")
    pack = g141.build_ident_musepack(template, "MOCK_ONLY statement", 42, "ident:local-probe", sha(template_path.read_bytes()))
    fake = {"transport": "mcp", "provider": "arbitrary local label", "model": "arbitrary local label",
            "schema": {"schema_id": "caller-selected", "required_keys": []}, "raw_response": '{"x":1}',
            "evidence_quotes": ["MOCK_ONLY statement"], "canonicalization": "raw_unverified"}
    rows.append({"check": "run141_unattested_muse_labels_and_caller_schema",
                 **accepted(lambda: g141.validate_muse_return(pack, fake)),
                 "scope": "raw_unverified structural return only; caller labels and declared schema are not transport/provider authentication"})
    after = [snapshot(p) for p in folders]
    report = {"schema": "run139-141-main-offline-verification/1", "date": "2026-10-09",
              "commands": commands, "challenges": rows, "old_run_bytes_unchanged": before == after,
              "real_model_submissions": 0, "music_acceptance": "NOT_PERFORMED", "production_ready": False,
              "limits": "Local fixtures/mock only. No real CLI protocol/authentication claim; no gate/hold changes."}
    # 对抗样本可返回 NaN，但报告自身须严格 JSON；不序列化未验 parsed 值。
    for row in rows:
        row.pop("value", None)
    with (dest / "report.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
    print(json.dumps(report, ensure_ascii=False, allow_nan=False))
    if before != after:
        raise SystemExit("old run changed during offline verification")


if __name__ == "__main__":
    main()
