# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
U = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\A36_units.json", encoding="utf-8"))
d = U["sources"]["SRC-luna-web-1"]
tot = 0
for u in d["units"]:
    n = len(u["text"].split("\n"))
    ti = len(u.get("title_inherited", []))
    tot += n + ti
    print(f"{u['uid']} k={u['kind']:13s} rl={n:2d} ti={ti} ch={u['chars']:4d} head={u['head_line'][:38]!r}")
print("total lines accounted:", tot, "file lines:", d["n_lines"])
