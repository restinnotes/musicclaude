#!/usr/bin/env python3
"""Summary-control mechanical builder (read-only stats + additive review builder).

NO model calls. NO writes into the frozen data root. NO writes into the
supplement dir. All outputs go to --out-dir (a NEW report root).

Reads (frozen logic reference, never executed in place):
  <data-root>/scripts/analyze_repeats.py   (trial normalize rules)
  <data-root>/scripts/build_repeat_judges.py (D/G/F prompt assembly rules)
  <data-root>/scripts/summarize_reviews.py  (review parse rules)

Usage:
  python3 -I tools/summary_builder.py --data-root D:/musicclaude/_dl_latest_zip_work \
      --supplement-dir D:/musicclaude/_baseline_recovery_control_20261010 \
      --out-dir out-v1 [--also-build-prompts]
"""
import argparse, collections, hashlib, json, re, sys
from pathlib import Path

MODELS = ["gpt6w", "gpt56w"]
MODEL_REPORTED = {"gpt6w": "gpt-6-thinking", "gpt56w": "gpt-5-6-thinking"}
ALLOWED_A = {"insight", "restatement", "manufactured", "imported", "undetermined"}
ALLOWED_B = {"valuable_new_link", "restatement", "unsupported_causality",
             "premature_lock", "not_enough_evidence"}
ALLOWED_C = {"KEEP", "RETIRE", "REPLACE", "APPEND", "SILENCE"}
STATIONS = (2, 11, 18, 20, 23)
BASE_ROUNDS = range(1, 6)


def parse(s):
    s = s.strip().lstrip("﻿")
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s)
    return json.loads(s)


def trial_slot(data_root, job, model, r):
    """Return (status, detail). status in valid/missing/invalid:<err>/failure:<phase>.

    Mirrors analyze_repeats.normalize but keeps transport phase separate from
    schema outcome so infra failure is never counted as quality signal.
    """
    p = data_root / "results" / "trials" / model / job["job_id"] / f"r{r:02d}"
    mp = Path(str(p) + ".meta.json")
    txt = Path(str(p) + ".txt")
    if not mp.exists():
        return "missing", {"reason": "no_meta"}
    try:
        meta = json.loads(mp.read_text(encoding="utf-8"))
    except Exception as e:
        return "invalid:unreadable_meta", {"error": str(e)[:200]}
    transport = {
        "status": meta.get("status"),
        "phase": meta.get("phase"),
        "exit_code": meta.get("exit_code"),
        "completed": meta.get("completed"),
        "model_reported": meta.get("model_reported"),
        "prompt_sha256": meta.get("prompt_sha256"),
        "imported_from_pilot": meta.get("imported_from_pilot"),
        "context_warning": meta.get("context_warning"),
    }
    if meta.get("status") != "success":
        return (f"failure:{meta.get('phase') or meta.get('status')}", transport)
    # schema checks only reached on transport success
    try:
        assert meta.get("model_reported") == MODEL_REPORTED[model], "model_reported"
        assert meta.get("prompt_sha256") == job["input_sha256"], "prompt_sha"
        assert txt.is_file(), "txt_missing"
        obj = parse(txt.read_text(encoding="utf-8"))
        if job["track"] == "A_E5":
            assert obj["batch_id"] == job["job_id"]
            rev = obj["reviews"]
            assert [q["blind_id"] for q in rev] == job["cases"]
            assert all(q["verdict"] in ALLOWED_A for q in rev)
            src = (data_root / f"inputs/e5/{job['job_id']}_source.txt").read_text(encoding="utf-8")
            assert all(q["quote"] in src for row in rev for q in row["evidence"])
        elif job["track"] == "B_RELATION":
            orig = json.loads((data_root / f"inputs/op60/B_k{job['k']:02d}.json").read_text(encoding="utf-8"))
            ids = {z["id"] for typ in ("thread_hypotheses", "why_hypotheses", "mech_hypotheses") for z in orig[typ]}
            assert obj["station_k"] == job["k"] and obj["task"] == "B"
            assert {q["hypothesis_id"] for q in obj["reviews"]} == ids
            assert all(q["verdict"] in ALLOWED_B for q in obj["reviews"])
        else:
            orig = json.loads((data_root / f"inputs/op60/C_k{job['k']:02d}.json").read_text(encoding="utf-8"))
            assert obj["station_k"] == job["k"] and obj["task"] == "C" and obj["action"] in ALLOWED_C
            previous = {z["id"]: z["text"] for z in orig["screen_before"]}
            candidates = {z["id"] for z in orig["current_candidates"]}
            keep, retire = obj["keep_ids"], obj["retire_ids"]
            assert set(keep) | set(retire) == set(previous) and not (set(keep) & set(retire))
            assert all(z["text"] and z["source_ids"] and set(z["source_ids"]) <= candidates
                       for z in obj["new_screen_items"])
            assert obj["final_screen_text"] == [z["text"] for z in orig["screen_before"] if z["id"] in keep] + \
                [z["text"] for z in obj["new_screen_items"]]
        return "valid", {"transport": transport}
    except Exception as e:
        transport["schema_error"] = str(e)[:200]
        return "invalid:schema", transport


def build_trial_census(data_root, manifest, max_round=12):
    census = {}
    for job in manifest["jobs"]:
        for m in MODELS:
            for r in range(1, max_round + 1):
                status, detail = trial_slot(data_root, job, m, r)
                census[f"{job['job_id']}/{m}/r{r:02d}"] = {"status": status, "detail": detail}
    return census


def summarize_trials(census, manifest):
    by_job_model = collections.defaultdict(lambda: {"n_valid": 0, "n_missing": 0,
                                                    "n_failure": 0, "n_invalid_schema": 0,
                                                    "valid_rounds": [], "gap_rounds": []})
    for key, v in census.items():
        job, m, r = key.split("/")
        r = int(r[1:])
        cell = by_job_model[(job, m)]
        st = v["status"]
        if st == "valid":
            cell["n_valid"] += 1
            cell["valid_rounds"].append(r)
        elif st == "missing":
            cell["n_missing"] += 1
            cell["gap_rounds"].append(r)
        elif st.startswith("failure:"):
            cell["n_failure"] += 1
            cell["gap_rounds"].append(r)
        else:
            cell["n_invalid_schema"] += 1
            cell["gap_rounds"].append(r)
    return {f"{j}/{m}": dict(v, valid_rounds=sorted(v["valid_rounds"]),
                             gap_rounds=sorted(v["gap_rounds"]))
            for (j, m), v in sorted(by_job_model.items())}


def ab_distributions(data_root, manifest, census):
    """Mechanical A/B verdict distributions per case/hypothesis. No majority vote."""
    A = collections.defaultdict(list)
    B = collections.defaultdict(list)
    for job in manifest["jobs"]:
        for m in MODELS:
            for r in range(1, 13):
                if census[f"{job['job_id']}/{m}/r{r:02d}"]["status"] != "valid":
                    continue
                txt = data_root / "results" / "trials" / m / job["job_id"] / f"r{r:02d}.txt"
                obj = parse(txt.read_text(encoding="utf-8"))
                if job["track"] == "A_E5":
                    for z in obj["reviews"]:
                        A[(m, z["blind_id"])].append([r, z["verdict"]])
                elif job["track"] == "B_RELATION":
                    for z in obj["reviews"]:
                        B[(m, job["job_id"], z["hypothesis_id"])].append([r, z["verdict"]])
    cases = {}
    for (m, c), vals in sorted(A.items()):
        cnt = dict(collections.Counter(x for _, x in vals))
        cases[f"{m}/{c}"] = {"trials": vals, "verdict_counts": cnt,
                             "unstable": len(cnt) > 1}
    threads = {}
    for (m, j, h), vals in sorted(B.items()):
        cnt = dict(collections.Counter(x for _, x in vals))
        threads[f"{m}/{j}/{h}"] = {"trials": vals, "verdict_counts": cnt,
                                   "unstable": len(cnt) > 1}
    return cases, threads


def review_census(data_root, review_manifest):
    pmap = {}
    pmap_file = data_root / "private" / "review_mapping_DO_NOT_SHOW_JUDGES.json"
    if pmap_file.exists():
        for j in json.loads(pmap_file.read_text(encoding="utf-8"))["jobs"]:
            pmap[j["job_id"]] = j
    rows = []
    for job in review_manifest["jobs"]:
        judge = job["judge_model"]
        name = job["job_id"]
        pm = pmap.get(name, {})
        p = data_root / "results" / "reviews" / judge / name
        txt = Path(str(p) + ".txt")
        meta = Path(str(p) + ".meta.json")
        line = {"job_id": name, "kind": job["kind"], "judge": judge, "status": "missing"}
        if txt.exists() and meta.exists():
            try:
                m = json.loads(meta.read_text(encoding="utf-8"))
                assert m.get("status") == "success", "meta_status"
                assert m.get("model_reported") == MODEL_REPORTED[judge], "model_reported"
                x = parse(txt.read_text(encoding="utf-8"))
                assert x.get("task") == job["kind"], "task"
                assert x.get("station_k") == job["station_k"], "station_k"
                if job["kind"] in ("D", "G"):
                    assert x["winner"] in ("A", "B", "TIE", "UNDETERMINED"), "winner"
                    if job["kind"] == "D":
                        winner = ("new" if x["winner"] == pm.get("new_side")
                                  else "legacy" if x["winner"] == pm.get("old_side") else x["winner"])
                        key = (job["kind"], pm.get("k"), pm.get("repeat"), pm.get("generating_model"), judge)
                    else:
                        winner = (pm.get("A_model") if x["winner"] == "A"
                                  else pm.get("B_model") if x["winner"] == "B" else x["winner"])
                        key = (job["kind"], pm.get("k"), pm.get("repeat"), judge)
                    line.update(status="valid", interpreted_winner=winner, side=x["winner"],
                                order=name[-2:], pair_key=str(key))
                else:
                    assert x.get("sample_count") == pm.get("sample_count"), "sample_count"
                    assert x["saturation_assessment"] in ("SATURATED_WITHIN_SAMPLE", "NOT_SATURATED", "UNCERTAIN")
                    line.update(status="valid", assessment=x["saturation_assessment"],
                                recommend_more=x.get("recommend_more"),
                                best_trial_candidate=x.get("best_trial_candidate"),
                                late_new_unit_ids=x.get("late_round_new_valuable_unit_ids", []),
                                n_semantic_units=len(x.get("semantic_units", [])))
            except Exception as e:
                line.update(status="invalid", error=str(e)[:250])
        elif meta.exists():
            m = json.loads(meta.read_text(encoding="utf-8"))
            line.update(status="recorded_failure_or_missing_txt",
                        failure_status=m.get("status"), failure_phase=m.get("phase"),
                        failure_error=(m.get("stderr") or m.get("error") or "")[:200])
        rows.append(line)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--supplement-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    data_root = Path(args.data_root)
    out = Path(args.out_dir)
    assert (data_root / "jobs" / "manifest.json").exists(), "data-root must hold frozen jobs/manifest.json"
    assert (data_root / "jobs" / "reviews" / "review_manifest.json").exists(), "missing frozen review manifest"
    assert Path(args.supplement_dir).exists(), "supplement dir missing"
    out.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((data_root / "jobs" / "manifest.json").read_text(encoding="utf-8"))
    review_manifest = json.loads((data_root / "jobs" / "reviews" / "review_manifest.json").read_text(encoding="utf-8"))

    census = build_trial_census(data_root, manifest)
    (out / "trial_census.json").write_text(
        json.dumps({"data_root": str(data_root), "slots": census}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    by_jm = summarize_trials(census, manifest)
    (out / "trial_gaps.json").write_text(
        json.dumps(by_jm, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cases, threads = ab_distributions(data_root, manifest, census)
    (out / "ab_distributions.json").write_text(
        json.dumps({"A_case_verdicts": cases, "B_hypothesis_verdicts": threads,
                    "note": "mechanical counts only; any swing reported as unstable, never pressed into majority"},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rows = review_census(data_root, review_manifest)
    (out / "review_census.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # supplement pointer: A01r03 owned-job recovery lives in supplement dir
    supp_meta = Path(args.supplement_dir) / "SUPPLEMENTAL_RECOVERED_FROM_OWNED_EVIDENCE__A01r03_retry_presubmit.txt.meta.json"
    supp = json.loads(supp_meta.read_text(encoding="utf-8")) if supp_meta.exists() else None

    base = {k: v for k, v in census.items() if int(k.rsplit("/r", 1)[-1]) <= 5}
    ext = {k: v for k, v in census.items() if int(k.rsplit("/r", 1)[-1]) > 5}
    summary = {
        "base_r01_r05": {
            "valid": sum(v["status"] == "valid" for v in base.values()),
            "missing": sum(v["status"] == "missing" for v in base.values()),
            "failure_infra": sum(v["status"].startswith("failure:") for v in base.values()),
            "invalid_schema": sum(v["status"].startswith("invalid:") for v in base.values()),
        },
        "ext_r06_r12": {
            "valid": sum(v["status"] == "valid" for v in ext.values()),
            "missing": sum(v["status"] == "missing" for v in ext.values()),
            "failure_infra": sum(v["status"].startswith("failure:") for v in ext.values()),
            "invalid_schema": sum(v["status"].startswith("invalid:") for v in ext.values()),
        },
        "reviews": dict(collections.Counter(x["status"] for x in rows)),
        "A_cases_unstable": sum(v["unstable"] for v in cases.values()),
        "A_cases_total": len(cases),
        "B_hypotheses_unstable": sum(v["unstable"] for v in threads.values()),
        "B_hypotheses_total": len(threads),
        "supplement_A01r03_recovered": bool(supp and supp.get("RECOVERED_FROM_OWNED_EVIDENCE")),
        "frozen_dirs_untouched": True,
    }
    (out / "out_v1_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("WROTE", out)
    print("base r01-05:", summary["base_r01_r05"])
    print("ext  r06-12:", summary["ext_r06_r12"])
    print("reviews:", summary["reviews"])
    print("A unstable %d/%d  B unstable %d/%d" % (
        summary["A_cases_unstable"], summary["A_cases_total"],
        summary["B_hypotheses_unstable"], summary["B_hypotheses_total"]))
    print("supplement A01r03 recovered:", summary["supplement_A01r03_recovered"])


if __name__ == "__main__":
    main()
