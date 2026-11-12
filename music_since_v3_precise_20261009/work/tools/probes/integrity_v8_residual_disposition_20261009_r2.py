"""Correct the r1 diagnostic input type, keeping r1 evidence immutable."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

BASE = Path(__file__).with_name("integrity_v8_residual_disposition_20261009_r1.py")
spec = importlib.util.spec_from_file_location("frozen_v8_residual_probe_r1", BASE)
base = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = base
spec.loader.exec_module(base)
original_import = __import__


class TextInputContract:
    def __init__(self, module):
        self.module = module
    def __getattr__(self, attr):
        return getattr(self.module, attr)
    def parse_codex(self, payload):
        if not isinstance(payload, bytes):
            raise TypeError("r1 diagnostic seam expects its known UTF-8 bytes fixture")
        return self.module.parse_codex(payload.decode("utf-8"))


def import_with_text_contract(name, globals=None, locals=None, fromlist=(), level=0):
    module = original_import(name, globals, locals, fromlist, level)
    return TextInputContract(module) if name == "execution_integrity_v8" else module


if __name__ == "__main__":
    base.__builtins__ = dict(vars(__import__("builtins")), __import__=import_with_text_contract)
    # Function global lookup uses the builtins object captured when it is created,
    # so call a recompiled copy with the explicit import seam, not a global patch.
    import inspect
    namespace = dict(base.__dict__)
    namespace["__file__"] = str(Path(__file__).resolve())
    namespace["__builtins__"] = dict(vars(__import__("builtins")), __import__=import_with_text_contract)
    exec(compile(inspect.getsource(base.main), str(Path(__file__).resolve()), "exec"), namespace)
    namespace["main"]()
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.out_dir / "report.json").read_bytes())
    rows = report["duplicate_started"]
    expected = {"duplicate_started_complete_terminal": True, "duplicate_started_incomplete_reasoning": False,
        "duplicate_started_no_turn_terminal": False}
    passed = all(row["accepted"] is expected[row["case"]] for row in rows)
    correction = {"schema": "v8-residual-probe-correction/1", "base_probe_sha256": base.sha(BASE.read_bytes()),
        "r1_disposition": "INVALID_PARSER_DIAGNOSTIC: r1 passed bytes to parse_codex, whose contract requires str. All three rejects were input-type errors, not event-state evidence.",
        "r2_change": "Only diagnostic UTF-8 bytes are decoded to text at the parser boundary; production module and old reports untouched.",
        "parser_expectations_passed": passed, "music_acceptance": "NOT_PERFORMED", "production_ready": False}
    with (args.out_dir / "correction.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(correction, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    if not passed:
        raise SystemExit(1)
