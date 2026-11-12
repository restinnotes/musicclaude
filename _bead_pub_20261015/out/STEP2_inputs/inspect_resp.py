# -*- coding: utf-8 -*-
import json, re
d = json.load(open(r"D:\musicclaude\_bead_pub_20261015\out\STEP2_batchB_stdout.json", encoding="utf-8-sig"))
r = d.get("response", "")
lines = r.split("\n")
print("TOTAL_LINES:", len(lines))
for i, ln in enumerate(lines[:120]):
    s = ln.strip()
    if s:
        print(i, s[:110])
