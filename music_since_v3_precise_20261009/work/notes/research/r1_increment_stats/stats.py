"""R1 统计脚本：E5 每站条数/NONE、R6/History 空步比例、Thread 中心列表。
输入：run128 cache_gen.json、run130 steps.json + centers.json、run97 relations（如有）。
输出：本目录下 stats.json + 打印摘要。全部用脚本计算，不估计。
"""
import json, collections, pathlib, sys

ROOT = pathlib.Path(r"D:\musicclaude\unified_run_handoff_20260924\unified_run_handoff_20260924")
OUT = ROOT / "notes" / "research" / "r1_increment_stats"
OUT.mkdir(parents=True, exist_ok=True)

MODELS = ("muse", "gpt56w", "luna_noweb")
result = {}

# ---- 1. run128 E5：每站条数分布、NONE 比例 ----
gen = json.load(open(ROOT / "runs/run128_mech_calib/cache_gen.json", encoding="utf-8"))
recs = [r for r in gen["records"] if r.get("model") in MODELS]
e5 = {}
for r in recs:
    model, ver, work = r["model"], r.get("prompt_version"), r["key"][1]
    n = len(r.get("parsed") or [])
    e5.setdefault((model, ver, work), []).append(n)
e5_table = []
for key in sorted(e5):
    ns = e5[key]
    dist = dict(sorted(collections.Counter(ns).items()))
    none = sum(1 for n in ns if n == 0)
    e5_table.append({"model": key[0], "prompt": key[1], "work": key[2],
                     "stations": len(ns), "count_dist": dist,
                     "none_stations": none,
                     "none_rate": round(none / len(ns), 4),
                     "mean": round(sum(ns) / len(ns), 4)})
result["e5_per_station"] = e5_table

# ---- 2. R6/History：new_changes 有无变化比例 ----
steps = json.load(open(ROOT / "runs/run130_thread_e6/steps.json", encoding="utf-8"))
st = steps["steps"]
hist = []
by_model = collections.defaultdict(list)
for s in st:
    p = s.get("parsed") or {}
    n = len(p.get("new_changes") or [])
    by_model[s.get("model")].append(n)
    hist.append({"model": s.get("model"), "k": s.get("k"), "n_new_changes": n,
                 "thread": (p.get("thread") or "")[:120]})
dist_all = dict(sorted(collections.Counter(h["n_new_changes"] for h in hist).items()))
empty = sum(1 for h in hist if h["n_new_changes"] == 0)
result["history_steps"] = {
    "n_steps": len(hist),
    "new_changes_dist": dist_all,
    "empty_steps": empty,
    "empty_rate": round(empty / len(hist), 4) if hist else None,
    "by_model": {m: {"n": len(v), "dist": dict(sorted(collections.Counter(v).items())),
                     "empty": sum(1 for x in v if x == 0)}
                for m, v in sorted(by_model.items())},
}
result["history_step_detail"] = hist

# ---- 3. Thread 中心表述列表 ----
centers = json.load(open(ROOT / "runs/run130_thread_e6/centers.json", encoding="utf-8"))
clist = []
for c in centers["centers"]:
    for ctr in c.get("centers", []):
        clist.append({"model": c.get("model"), "work": c.get("work"),
                      "center": ctr.get("center"),
                      "covers": ctr.get("covers"), "strains": ctr.get("strains"),
                      "note": ctr.get("note")})
    if c.get("no_single_center"):
        clist.append({"model": c.get("model"), "work": c.get("work"),
                      "center": "NO_SINGLE_CENTER"})
result["thread_centers"] = clist

# ---- 4. run97 附带：keepers 投票分布（若文件存在）----
try:
    rel = json.load(open(ROOT / "runs/run97_rel_select/relations.json", encoding="utf-8"))
    n_cand, n_keep, votes = 0, 0, collections.Counter()
    for s in rel.get("stations", []):
        for cd in s.get("candidates", []):
            n_cand += 1
            v = len(cd.get("keepers") or [])
            votes[v] += 1
            if v > 0:
                n_keep += 1
    result["run97"] = {"n_candidates": n_cand, "n_kept": n_keep,
                       "vote_dist": dict(sorted(votes.items()))}
except FileNotFoundError:
    result["run97"] = None

json.dump(result, open(OUT / "stats.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("== E5 每站条数 / NONE ==")
for row in e5_table:
    print(row)
print("== History 空步 ==")
print(json.dumps(result["history_steps"]["by_model"], ensure_ascii=False, indent=1))
print("overall:", {k: v for k, v in result["history_steps"].items() if k != "by_model"})
print("== Thread 中心数 ==", len(clist))
print("== run97 ==", result["run97"])
