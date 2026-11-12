"""核真实五包/60映射，既有输入只读；不提交模型或重写 prepare。"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_integrity_v4 as I
import run140_mech_independent_review as M


def verify():
    cases = M.load_and_validate()
    packs, entries = M.build_packs(cases)
    directory = M.OUT
    plan = I.strict_json((directory / "plan.json").read_bytes().decode("utf-8"))
    mapping = I.strict_json((directory / "case_mapping.json").read_bytes().decode("utf-8"))
    checks = []
    def add(name, good):
        checks.append({"check": name, "passed": bool(good)})
    add("driver_sha256", plan["driver_sha256"] == I.sha_file(M.__file__))
    add("template_sha256", plan["template_sha256"] == I.sha_text(M.REVIEW_TEMPLATE))
    add("mapping_bytes_sha256", plan["case_mapping_sha256"] == I.sha_file(directory / "case_mapping.json"))
    add("seed_exact", plan["seed"] == M.SEED and plan["blind_seed"] == M.BLIND_SEED)
    all_ids = []
    rows = []
    for pack, planned in zip(packs, plan["packs"]):
        rel = "review_prompts/%s.txt" % pack["pack_id"]
        raw = (directory / rel).read_bytes()
        text = raw.decode("utf-8", "strict")
        expected = M.render_pack_prompt(pack)
        add(pack["pack_id"] + ":exact_payload", raw == expected.encode("utf-8"))
        add(pack["pack_id"] + ":frozen_sha", I.sha_file(directory / rel) == planned["prompt_sha256"])
        add(pack["pack_id"] + ":exact_ids", planned["blind_ids"] == [case["blind_id"] for case in pack["cases"]])
        add(pack["pack_id"] + ":no_replacement_char", "�" not in text)
        all_ids.extend(planned["blind_ids"])
        for entry in entries:
            if entry["pack_id"] == pack["pack_id"]:
                entry.update(prompt_file=rel, prompt_sha256=I.sha_text(expected))
        rows.append({"pack_id": pack["pack_id"], "bytes": len(raw), "characters": len(text),
                     "sha256": I.sha_file(directory / rel), "cases": len(pack["cases"])})
    add("60_exact_mapping", sorted(entries, key=lambda entry: entry["blind_id"]) == mapping["entries"])
    add("all60_ids_once", len(all_ids) == 60 and set(all_ids) == {"B%03d" % n for n in range(1, 61)})
    add("composition", dict(Counter(case["work"] for case in cases)) == {"op52": 32, "op60": 28})
    add("not_production", plan["production_ready"] is False and plan["model_submissions"] == 0)
    return {"date": "2026-10-09", "real_model_submissions": 0, "checks": checks, "packs": rows,
            "all_passed": all(check["passed"] for check in checks),
            "generator_canonical_counts": dict(Counter(entry["gen_canonical"] for entry in entries)),
            "limits": "byte/payload checks only; no music verdict; mapping private, not sent to reviewers"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = verify()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
    if not result["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
