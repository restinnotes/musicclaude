"""严格核已归档回执；只新建解析报告，不改 prompt/plan/原回复。"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_integrity_v4 as I
import run140_mech_independent_review as M


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--pack", required=True)
    args = parser.parse_args()
    directory = Path(args.archive)
    meta = I.strict_json((directory / "meta.json").read_bytes().decode("utf-8"))
    task = (directory / "task.txt").read_bytes()
    response = (directory / "response.txt").read_bytes()
    cases = M.load_and_validate()
    packs, _ = M.build_packs(cases)
    pack = next(p for p in packs if p["pack_id"] == args.pack)
    if (I.sha_text(task.decode("utf-8")) != meta["task_sha256"]
            or I.sha_text(response.decode("utf-8")) != meta["response_sha256"]
            or task != M.render_pack_prompt(pack).encode("utf-8")):
        raise I.ArtifactConflict("archived actual task/response conflicts with frozen payload/hash")
    text = response.decode("utf-8", "strict")
    # 在冻结 parser 外额外拒非 JSON 数值常量，冻结 driver 保持原样。
    I.strict_json(text)
    parsed, error = M.parse_review(text, pack)
    report = {"schema": "run140-return-parse/1", "date": "2026-10-09", "pack_id": args.pack,
              "schema_pass": parsed is not None, "error": error, "response_sha256": meta["response_sha256"],
              "actual_task_sha256": meta["task_sha256"], "actual_task_equals_frozen": True,
              "requested_target": meta["requested_target"], "observed_t3_model": meta["observed_t3_model"],
              "production_ready": False, "music_verdict": "not adjudicated by parser",
              "limits": "Legacy-input diagnosis; T3 reported identity not independent remote attestation; historical backend unknown."}
    if parsed is not None:
        report["verdict_counts_raw_reviewer_only"] = dict(Counter(r["verdict"] for r in parsed["reviews"]))
        report["quoted_items_exact"] = True
        report["quoted_relation_exact"] = True
        report["parsed"] = parsed
    with (directory / "parse_report.json").open("x", encoding="utf-8", newline="") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in report.items() if k != "parsed"}, ensure_ascii=False))
    if parsed is None:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
