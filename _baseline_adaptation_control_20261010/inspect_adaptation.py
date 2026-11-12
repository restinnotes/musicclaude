#!/usr/bin/env python3
"""Mechanical adaptation-queue inspector for the frozen music baseline.

Reads ONLY frozen structures (manifest + two summary JSONs + canonical
slot metas for status counting). No model calls, no prompt edits, no
rewriting of original answers, no new semantic judgement.

Drama/assertive/single-story writing is NOT a defect and is never scored.

Usage: python -I inspect_adaptation.py [frozen_dir] [out_dir]
"""
import glob
import json
import sys
from collections import Counter
from pathlib import Path

FROZEN = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("D:/musicclaude/_dl_latest_zip_work")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("D:/musicclaude/_baseline_adaptation_control_20261010")
OUT.mkdir(parents=True, exist_ok=True)

M = json.loads((FROZEN / "jobs/manifest.json").read_text(encoding="utf-8"))
S = json.loads((FROZEN / "reports/repeated_stability_summary.json").read_text(encoding="utf-8"))
V = json.loads((FROZEN / "reports/review_and_extension_summary.json").read_text(encoding="utf-8"))
MODELS = M["models"]  # paired dual-model rule: never top up one side alone

blind2job = {}
for j in M["jobs"]:
    if j["track"] == "A_E5":
        for c in j["cases"]:
            blind2job[c] = j["job_id"]


def tpath(model, job, r):
    return f"results/trials/{model}/{job}/r{r:02d}.txt"


# ---------------- A: E5 verdict flips ----------------
A = S["A_case_stability"]
a_jobs = {}
for key, v in sorted(A.items()):
    model, blind = key.split("/", 1)
    job = blind2job.get(blind, "?")
    d = a_jobs.setdefault(job, {"job_id": job, "unstable": [], "stable": []})
    entry = {"model": model, "blind_id": blind, "n_valid": len(v["trials"]),
             "verdict_counts": v["verdict_counts"], "trials": v["trials"],
             "answer_paths": [tpath(model, job, r) for r, _ in v["trials"]],
             "unstable": v["unstable"]}
    (d["unstable"] if v["unstable"] else d["stable"]).append(entry)

modals = {}
for key, v in A.items():
    model, blind = key.split("/", 1)
    c = Counter(w for _, w in v["trials"])
    top = c.most_common(1)[0]
    modals.setdefault(blind, {})[model] = {"modal": top[0], "n": len(v["trials"]), "counts": dict(c)}
flips = sorted(b for b, m in modals.items()
               if len(m) == 2 and m[MODELS[0]]["modal"] != m[MODELS[1]]["modal"])
for job, d in a_jobs.items():
    d["cross_model_modal_flips"] = [b for b in flips if blind2job.get(b) == job]
    d["modal_table"] = {b: modals[b] for b in sorted(modals) if blind2job.get(b) == job}
    d["trigger"] = "E5_label_variability" if d["unstable"] else None
    d["decision"] = "expand_to_r08_paired" if d["unstable"] else "hold_no_trigger"
    d["stage_target"] = 8 if d["unstable"] else None

# ---------------- B: hypothesis verdict flips ----------------
B = S["B_hypothesis_stability"]
b_jobs = {}
for key, v in sorted(B.items()):
    model, job, hyp = key.split("/", 2)
    d = b_jobs.setdefault(job, {"job_id": job, "unstable": [], "stable": []})
    entry = {"model": model, "hypothesis_id": hyp, "n_valid": len(v["trials"]),
             "verdict_counts": v["verdict_counts"], "trials": v["trials"],
             "answer_paths": [tpath(model, job, r) for r, _ in v["trials"]],
             "unstable": v["unstable"]}
    (d["unstable"] if v["unstable"] else d["stable"]).append(entry)
for job, d in b_jobs.items():
    d["trigger"] = "B_relation_verdict_variability" if d["unstable"] else None
    d["decision"] = "expand_to_r08_paired" if d["unstable"] else "hold_no_trigger"
    d["stage_target"] = 8 if d["unstable"] else None

# ---------------- C: F verdicts + r08 slot audit ----------------
Cvar = S["C_editing_variability"]
Frows = V["F_semantic_saturation"]
slots = {}
for p in sorted(glob.glob(str(FROZEN / "results/trials/*/*/r0[678].meta.json"))):
    rel = Path(p).relative_to(FROZEN / "results/trials").as_posix()  # model/job/file
    model, job, f = rel.split("/")
    r = f.split(".")[0]
    try:
        st = json.loads(Path(p).read_text(encoding="utf-8")).get("status")
    except Exception as e:  # noqa: BLE001 - mechanical read guard
        st = "unreadable:" + str(e)[:80]
    slots.setdefault(job, []).append({"model": model, "r": r, "status": st})
c_jobs = {}
for k in (2, 11, 18, 20, 23):
    jid = f"C{k:02d}"
    fr = [x for x in Frows if x["k"] == k]
    trials_n = {key: len(v["trials"]) for key, v in Cvar.items() if key.endswith("/" + jid)}
    remaining = [s for s in slots.get(jid, []) if s["status"] != "success"]
    if jid in ("C02", "C11", "C23"):
        decision, why = "continue_r08_paired_no_duplicates", "F recommend_more=YES/late_new present; r08 already started"
    elif not fr:
        decision, why = "hold_pending_two_judge_F", "no valid F row; saturation unjudgeable"
    else:
        decision, why = "hold_pending_F_pair_complete", "F pair incomplete across writers/judges"
    c_jobs[jid] = {"job_id": jid, "F": fr, "valid_trials_per_model": trials_n,
                   "r08_slots": sorted(slots.get(jid, []), key=lambda s: (s["model"], s["r"])),
                   "r08_remaining_nonsuccess": remaining, "decision": decision, "reason": why}

# ---------------- invalid audit: 145 valid vs 146 meta-success ----------------
statuses = S["statuses"]
invalid = {k: v for k, v in sorted(statuses.items()) if v not in ("valid", "missing")}
invalid_detail = []
for k, reason in invalid.items():
    job, model, r = k.split("/")
    mp = FROZEN / "results/trials" / model / job / f"{r}.meta.json"
    tp = FROZEN / "results/trials" / model / job / f"{r}.txt"
    mstat = None
    if mp.exists():
        try:
            mstat = json.loads(mp.read_text(encoding="utf-8")).get("status")
        except Exception as e:  # noqa: BLE001
            mstat = "unreadable:" + str(e)[:80]
    invalid_detail.append({"slot": k, "validator_reason": reason,
                           "canonical_meta": mstat if mp.exists() else "no_canonical_meta",
                           "txt_bytes": tp.stat().st_size if tp.exists() else None})
base_success = 0
for p in glob.glob(str(FROZEN / "results/trials/*/*/r0[1-5].meta.json")):
    stem = Path(p).name.split(".")[0]
    if stem.startswith("r") and stem[1:].isdigit() and int(stem[1:]) <= 5:
        try:
            if json.loads(Path(p).read_text(encoding="utf-8")).get("status") == "success":
                base_success += 1
        except Exception:  # noqa: BLE001, S110
            pass
n_valid = sum(v == "valid" for k, v in statuses.items() if int(k.rsplit("/r", 1)[1]) <= 5)
n_valid_all = sum(1 for v in statuses.values() if v == "valid")

# ---------------- review gaps (mechanical) ----------------
revrows = V["review_rows"]
f_gaps = [r for r in revrows if r["kind"] == "F" and r["status"] != "valid"]
order_true = [o for o in V["order_sensitivity"] if o["order_disagreement"]]
order_incomplete = [o for o in V["order_sensitivity"] if len(o["results"]) < 2]

queue = {
    "generated_by": "inspect_adaptation.py (mechanical only: frozen verdicts + slot statuses; no model calls)",
    "frozen_inputs": {"manifest": "jobs/manifest.json", "stability": "reports/repeated_stability_summary.json",
                      "reviews": "reports/review_and_extension_summary.json", "rules": "docs/04_REPEATABILITY_AND_SATURATION.md"},
    "frozen_rules": {
        "stage_targets": [8, 12],
        "stage_rule": "r04/r05 late new valuable unit or judgement/order/routing divergence -> both models to r08; "
                      "still new/oscillating at r08 -> both models to r12; still growing at r12 -> NOT_SATURATED, master decides",
        "trigger_sources": ["F recommend_more/late_new_unit_ids", "unstable flag in frozen summaries",
                            "order_disagreement=true", "adaptation_candidates"],
        "paired_dual_model": "expansion always covers both gpt6w and gpt56w together; never top up one side alone",
        "ambiguous_slots_not_reissued": "failure_or_ambiguous / invalid slots are frozen gaps; "
                                        "never regenerate that position, never edit originals; only add new r-numbers",
        "not_evidence": "word counts, token frequencies, source-ID sets are NOT saturation proof; "
                        "music/drama/single-story writing is NOT a defect and is never penalised",
    },
    "invalid_audit_145_vs_146": {
        "n_valid_in_summary_r01_r05": n_valid, "n_valid_all_slots": n_valid_all,
        "canonical_meta_success_r01_r05": base_success,
        "plus_one_slot": "B18/gpt6w/r02",
        "plus_one_detail": [d for d in invalid_detail if d["slot"] == "B18/gpt6w/r02"],
        "action": "do_not_regenerate; keep as frozen invalid gap; expand only via new r-numbers",
        "all_invalid_slots": invalid_detail,
    },
    "A_jobs": a_jobs,
    "B_jobs": b_jobs,
    "C_jobs": c_jobs,
    "order_sensitivity_true": order_true,
    "order_incomplete_pairs_n": len(order_incomplete),
    "order_incomplete_pairs": order_incomplete,
    "F_review_gaps": f_gaps,
    "executable_set": {
        "A_expand_r06_r08_paired": sorted(j for j, d in a_jobs.items() if d["decision"] == "expand_to_r08_paired"),
        "B_expand_r06_r08_paired": sorted(j for j, d in b_jobs.items() if d["decision"] == "expand_to_r08_paired"),
        "C_continue_r08_remaining": {j: d["r08_remaining_nonsuccess"] for j, d in c_jobs.items()
                                     if d["decision"].startswith("continue")},
        "reviews_needed_two_webGPT": [
            "F_k18 gpt56w-writer x both judges (5 valid trials, no F row yet)",
            "F_k02 gpt6w-judge re-run (recorded_failure_or_missing_txt)",
        ],
        "blocked_sample_insufficient_no_reissue": [
            "F_k18 gpt6w-writer (only 3 valid trials r01/r02/r05; r03/r04 invalid)",
            "F_k20 gpt6w-writer (only 4 valid trials; r04 invalid)",
        ],
    },
}
out = OUT / "extension_queue.json"
out.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("WROTE", out)
print("valid", n_valid, "meta_success", base_success)
print("A_expand", queue["executable_set"]["A_expand_r06_r08_paired"])
print("B_expand", queue["executable_set"]["B_expand_r06_r08_paired"])
print("C_remaining", {j: len(v) for j, v in queue["executable_set"]["C_continue_r08_remaining"].items()})
