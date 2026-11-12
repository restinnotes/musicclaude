# -*- coding: utf-8 -*-
"""Map A36 units to frozen C2 segments by range intersection (mechanical pre-assign).
Assignment rules (all deterministic; GPT-6w STEP3 review later confirms/corrects):
  - unit ranges == [(a,b)] and contained in ONE segment   -> PRIMARY that segment
  - unit partially overlapping multiple segments          -> CROSS_SEGMENT on each covered
  - unit has ranges list (multi)                          -> same logic across all ranges
  - range_main None -> bucket NO_RANGE (review decides)
  - any range end/start > 116 -> OUT_OF_BOUNDS (review decides; source text kept verbatim)
  - preamble/段落 kinds with no range -> NO_RANGE bucket (review decides GLOBAL vs UNCERTAIN)
Also computes, for the coverage audit: every unit must appear >=1 segment-slot or in a review bucket.
"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")

UJ = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\A36_units.json", encoding="utf-8"))
OUT = r"D:\musicclaude\_bead_auto_20261016\out"

SEGMENTS = [
    ("S01", 1, 3), ("S02", 4, 16), ("S03", 17, 23), ("S04", 24, 34),
    ("S05", 35, 39), ("S06", 40, 50), ("S07", 51, 61), ("S08", 62, 71),
    ("S09", 72, 77), ("S10", 78, 83), ("S11", 84, 92), ("S12", 93, 102),
    ("S13", 103, 110), ("S14", 111, 116),
]

def primary_for(rng):
    segs = [(sid, a, b) for sid, a, b in SEGMENTS if rng[0] >= a and rng[1] <= b]
    return segs

def covered_for(rng):
    segs = [(sid, a, b) for sid, a, b in SEGMENTS if not (rng[1] < a or rng[0] > b)]
    return segs

pool = {sid: {"primary": [], "cross": [], "uncertain": [], "unresolved": [], "out_of_range": []} for sid, _, _ in SEGMENTS}
pool["NO_RANGE"] = []
pool["OUT_OF_BOUNDS"] = []
pool["LONG_RANGE_CAND"] = []
stats = {"primary": 0, "cross": 0, "no_range": 0, "oob": 0, "multi_slot": 0}

for src, d in UJ["sources"].items():
    for u in d["units"]:
        e = {"src": src, "uid": u["uid"],
             "ranges": ["%d-%d" % (rk[0], rk[1]) for rk in u["ranges"]],
             "chars": u["chars"], "kind": u["kind"], "head": u["head_line"][:80]}
        if u.get("title_inherited"):
            e["titles_inherited"] = u["title_inherited"]
        rngs = u["ranges"]
        if not rngs:
            e["slot"] = "NO_RANGE"
            pool["NO_RANGE"].append(e); stats["no_range"] += 1
            continue
        if any(r[1] > 116 or r[0] > 116 for r in rngs):
            e["slot"] = "OUT_OF_BOUNDS"
            pool["OUT_OF_BOUNDS"].append(e); stats["oob"] += 1
            continue
        # exact-primary: all ranges within a single same segment, and unit fully inside
        hits = set()
        for r in rngs:
            for s_, _, _ in covered_for(r):
                hits.add(s_)
        if len(rngs) == 1 and len(primary_for(rngs[0])) == 1:
            sid = primary_for(rngs[0])[0][0]
            e["slot"] = "PRIMARY"; e["seg"] = sid
            pool[sid]["primary"].append(e); stats["primary"] += 1
            continue
        if len(hits) == 1 and len(rngs) > 1:
            # multiple ranges, all inside one segment -> still PRIMARY that segment
            sid = next(iter(hits))
            e["slot"] = "PRIMARY"; e["seg"] = sid
            pool[sid]["primary"].append(e); stats["primary"] += 1
            continue
        e["slot"] = "CROSS"
        e["segs"] = sorted(hits)
        for sid in sorted(hits):
            pool[sid]["cross"].append(e)
        stats["cross"] += 1; stats["multi_slot"] += 1
        if len(hits) == 0:
            # range inside piece but hits nothing (impossible given full cover) — safety
            e["slot"] = "UNRESOLVED"
            pool["NO_RANGE"].append(e); stats["cross"] -= 1; stats["multi_slot"] -= 1

seg_coverage = {sid: (len(pool[sid]["primary"]), len(pool[sid]["cross"])) for sid, _, _ in SEGMENTS}
for sid, a, b in SEGMENTS:
    p, c = seg_coverage[sid]
    print(f"{sid} mm.{a:3d}-{b:3d}  primary={p:3d} cross={c:3d}")
print(f"NO_RANGE={len(pool['NO_RANGE'])} OUT_OF_BOUNDS={len(pool['OUT_OF_BOUNDS'])}")
print(f"stats={stats}")

json.dump({"_meta": {"generator": "map_units_to_segments.py", "segments": SEGMENTS},
           "pool": pool, "stats": stats},
          open(os.path.join(OUT, "A_POOL_MAP_v3_prejson.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("written A_POOL_MAP_v3_prejson.json")

# coverage audit: count non-preamble units vs accounted
n_units = sum(len(d["units"]) for d in UJ["sources"].values())
n_acc = stats["primary"] + stats["cross"] + stats["no_range"] + stats["oob"]
print(f"audit: units={n_units} accounted={n_acc} delta={n_units - n_acc}")
