# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
U = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\A36_units.json", encoding="utf-8"))
hot, others = [], 0
for src, d in U["sources"].items():
    for u in d["units"]:
        if not u["ranges"]:
            hot.append((src, u["uid"], u["chars"], u["head_line"][:40]))
print(f"no-range units: {len(hot)} chars={sum(h[2] for h in hot)}")
for h in hot[:12]: print("  ", h[0], h[1], h[3])
# largest units overall (may need trimming for batch size)
large = sorted(((s,u['uid'],u['chars']) for s,d in U['sources'].items() for u in d['units']), key=lambda x:-x[2])[:8]
print("largest:", large)
