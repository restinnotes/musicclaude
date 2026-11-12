"""只读核 source/评审清单字节与条数；不运行历史代码，不提交模型。"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verify(root):
    root = Path(root)
    inventory = json.loads((root / "notes/research/d3d4_source_inventory_20261009.json").read_bytes())
    rows = []
    def add(path, expected, label):
        if not isinstance(path, str) or "{" in path:
            return
        p = root / path
        actual = sha(p.read_bytes()) if p.is_file() else None
        rows.append({"path": path, "label": label, "expected": expected, "actual": actual,
                     "expected_is_full_sha256": isinstance(expected, str) and len(expected) == 64,
                     "match": actual is not None and expected == actual})
    for obj in inventory["hypothesis_text_sources"] + inventory["verified_musical_fact_sources"]:
        if "sha256" in obj:
            add(obj["path"], obj["sha256"], "source")
        for field in ("clean_beads", "steps", "downstream_template", "prompt_template"):
            path = obj.get(field + "_path") or obj.get(field)
            expected = obj.get(field + "_sha256")
            if path is not None and expected is not None:
                add(path, expected, field)
        for result in obj.get("results", []):
            add(result["output_path"], result["output_sha256"], "run70_output")
    prompts = {model: (root / ("runs/run70_bead/prompts/BEAD__op60__mm17-34__%s.txt" % model)).read_bytes()
               for model in ("gflash", "luna_noweb", "muse")}
    source = (root / "runs/run53_struct_v1/outputs/STRUCT__STRUCT_v1__muse__op60__s1.md").read_bytes().decode("utf-8")
    section = source[source.index("【mm.17-34】"):source.index("【mm.35-39】")].strip()
    injected = {model: raw.decode("utf-8").split("【这一处的内容】", 1)[1].strip()
                for model, raw in prompts.items()}
    segments = {}
    for model in prompts:
        obj = json.loads((root / ("runs/run70_bead/outputs/BEAD__op60__mm17-34__%s.md" % model)).read_bytes())
        segments[model] = [s["mm"] for s in obj["segments"]]
    audit = json.loads((root / "notes/research/judge_clause_audit_20261009.json").read_bytes())
    files, errors, full_hashes = [], [], set()
    for item in audit["perfile"]:
        p = root / "runs" / item["file"]
        actual = sha(p.read_bytes()) if p.is_file() else None
        ok = actual == item["sha256"] and p.is_file() and p.stat().st_size == item["bytes"]
        if not ok:
            errors.append({"path": str(p.relative_to(root)), "expected": item["sha256"], "actual": actual})
        files.append(item["file"])
        if actual:
            full_hashes.add(actual)
    cases = json.loads((root / "runs/run138_e5_counterfactual/cases.json").read_bytes())
    plan = json.loads((root / "runs/run138_e5_counterfactual/plan.json").read_bytes())
    prompt_files = sorted((root / "runs/run138_e5_counterfactual/audit_prompts").glob("*.txt"))
    return {"date": "2026-10-09", "scope": "local byte verification only; not score/music judgment",
            "model_submissions": 0, "source_hash_rows": rows,
            "source_hash_passed": sum(row["match"] for row in rows),
            "source_hash_errors": [row for row in rows if not row["match"]],
            "run70": {"prompt_full_sha256": {m: sha(raw) for m, raw in prompts.items()},
                      "prompts_byte_equal": len(set(prompts.values())) == 1,
                      "text_matches_run53": {m: text == section for m, text in injected.items()},
                      "segments": segments, "new_segment_starts": {"gflash": 24, "luna_noweb": 26, "muse": 25},
                      "score_verification": "none"},
            "judge_manifest": {"claimed_counts": audit.get("counts"), "files": len(files),
                               "unique_paths": len(set(files)), "actual_unique_sha256": len(full_hashes),
                               "errors": errors, "presence_or_causality_not_verified_by_hash": True},
            "run138": {"cases_container_type": type(cases).__name__,
                       "cases_count": len(cases), "case_ids": [c.get("case_id") for c in cases] if isinstance(cases, list) else None,
                       "audit_prompt_files": len(prompt_files),
                       "case_sha256": sha((root / "runs/run138_e5_counterfactual/cases.json").read_bytes()),
                       "plan_keys": list(plan), "not_model_execution_evidence": True}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError("use a new evidence filename")
    result = verify(args.root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode())
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
