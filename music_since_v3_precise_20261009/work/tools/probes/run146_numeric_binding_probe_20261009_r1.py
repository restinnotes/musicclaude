"""Targeted r6 full-ingress numeric binding probes. No provider calls."""
import argparse
import copy
import json
import sys
from pathlib import Path
from unittest import mock


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out_dir.resolve()
    out.mkdir(parents=False, exist_ok=False)
    sys.path.insert(0, str(root / "tools/probes"))
    import run144_145_main_verify_20261009_r1 as h
    import tempfile
    (out / "scratch").mkdir()
    tempfile.tempdir = str(out / "scratch")
    blocked, original = h.guard(out)
    guards = h.negatives(root, original)
    f = h.load(root / "tools/tests/test_run146_e7_flash_diag_r6.py", "numeric_binding_fixture")
    cls, captured = f.Run146Tests, {}
    cls.setUpClass()
    try:
        g = cls.go
        original_validate = g.validate_external_review_results
        def capture(pack, results, expected_model, transport_verifier=None):
            if not captured and callable(transport_verifier):
                receipts = {}
                for row in results:
                    paths = {name: Path(path) for name, path in row["artifacts"].items()}
                    receipts[row["task_id"]] = transport_verifier(row, g.read_json(paths["meta"]),
                        g.read_json(paths["terminal"]), paths["output"].read_bytes())
                captured.update(pack=copy.deepcopy(pack), results=copy.deepcopy(results), model=expected_model, receipts=receipts)
            return original_validate(pack, results, expected_model, transport_verifier)
        case = cls("test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections")
        with mock.patch.object(g, "validate_external_review_results", side_effect=capture):
            case.test_external_muse_sourcebound_receipt_valid_path_and_binding_rejections()
        # The source fixture deliberately tampers its first output at the end.
        # Restore the first output/meta to exact captured bytes before these
        # independent mutations; only temporary mock evidence is rewritten.
        for row in captured["results"]:
            paths = {name: Path(path) for name, path in row["artifacts"].items()}
            raw = row["raw_response"].encode("utf-8")
            paths["output"].write_bytes(raw)
            meta = g.read_json(paths["meta"])
            meta["output_sha256"], meta["raw_output_size"] = g.sha256_bytes(raw), len(raw)
            paths["meta"].write_bytes(g.json_bytes(meta))
        checks = []
        for kind in ("positive", "pack_seed_float_and_receipt_float", "pack_order_index_float", "result_seed_float", "meta_raw_size_float", "meta_identity_seed_float", "terminal_identity_seed_float"):
            pack, results, receipts = copy.deepcopy(captured["pack"]), copy.deepcopy(captured["results"]), copy.deepcopy(captured["receipts"])
            task, row = pack["tasks"][0], results[0]
            paths = {name: Path(path) for name, path in row["artifacts"].items()}
            original_meta, original_terminal = paths["meta"].read_bytes(), paths["terminal"].read_bytes()
            meta, terminal = g.read_json(paths["meta"]), g.read_json(paths["terminal"])
            if kind == "pack_seed_float_and_receipt_float":
                task["seed"] = float(task["seed"])
                receipts[task["task_id"]]["seed"] = task["seed"]
            elif kind == "pack_order_index_float":
                task["order_index"] = float(task["order_index"])
            elif kind == "result_seed_float":
                row["seed"] = float(row["seed"])
            elif kind == "meta_raw_size_float":
                meta["raw_output_size"] = float(meta["raw_output_size"])
                paths["meta"].write_bytes(g.json_bytes(meta))
            elif kind == "meta_identity_seed_float":
                meta["identity"]["seed"] = float(meta["identity"]["seed"])
                paths["meta"].write_bytes(g.json_bytes(meta))
            elif kind == "terminal_identity_seed_float":
                terminal["identity"]["seed"] = float(terminal["identity"]["seed"])
                terminal_raw = g.json_bytes(terminal)
                paths["terminal"].write_bytes(terminal_raw)
                meta["terminal_sha256"] = g.sha256_bytes(terminal_raw)
                paths["meta"].write_bytes(g.json_bytes(meta))
            def verifier(result, _meta, _terminal, _raw):
                return receipts[result["task_id"]]
            try:
                accepted_rows = original_validate(pack, results, captured["model"], verifier)
                accepted, error = True, None
            except g.IntegrityError as exc:
                accepted_rows, accepted, error = [], False, str(exc)
            finally:
                paths["meta"].write_bytes(original_meta)
                paths["terminal"].write_bytes(original_terminal)
            checks.append({"case": kind, "accepted": accepted, "expected_accept": kind == "positive",
                "passed": accepted is (kind == "positive"), "exception": error, "normalized_rows": len(accepted_rows),
                "all_real_returns_zero": bool(accepted_rows and all(x["real_return_count"] == 0 for x in accepted_rows)),
                "scope": "Complete TEST_ONLY ingestion with independent source-bound receipt; not backend/service authentication."})
        case.doCleanups()
        result = {"schema": "r6-numeric-binding-main/1", "checks": checks, "guard_negatives": guards,
            "guard_blocked_counts": blocked, "real_model_submissions": 0, "model_cli_invocations": 0,
            "music_acceptance": "NOT_PERFORMED", "production_ready": False}
        h.save(out / "report.json", result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if all(row["passed"] for row in checks) else 1
    finally:
        cls.tearDownClass()


if __name__ == "__main__":
    raise SystemExit(main())
