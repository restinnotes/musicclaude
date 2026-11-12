# -*- coding: utf-8 -*-
"""Detail op60 A-int/A-web candidates per model, dedup by sha, list runs."""
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")

inv = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\inventory_A2.json", encoding="utf-8"))

rows = []
for r in inv:
    if r.get("parse_error") or r.get("orphan"):
        continue
    if r.get("work") != "op60":
        continue
    if not (r.get("branch") == "A-int" or r.get("branch") == "A-web" or r.get("branch") == "A-orig"):
        continue
    rows.append(r)

rows.sort(key=lambda r: (r["branch"], r.get("model_key") or "", r.get("prompt_version") or "", str(r.get("sample"))))

# group by sha among rows to detect dups
from collections import defaultdict
sha_seen = defaultdict(list)
outp = []
for r in rows:
    tag = ""
    sh = r.get("sha")
    if sh:
        seen = [o for o in rows if o.get("sha") == sh and o.get("out_path") != r.get("out_path") and o.get("out_path")]
        # find path of earliest
        sha_seen[sh].append(r.get("out_path"))
    outp.append(r)

with open(r"D:\musicclaude\_bead_auto_20261016\out\inv_op60_A.txt", "w", encoding="utf-8") as f:
    seen_sha = set()
    for r in rows:
        sh = r.get("sha")
        dup_note = ""
        if sh:
            paths_same = sha_seen[sh]
            first = sorted(p for p in paths_same)[0]
            if first != r.get("out_path") and paths_same.count(first) and sorted(paths_same)[0] != r.get("out_path"):
                dup_note = f" DUP_OF={os.path.relpath(first, 'D:\\\\musicclaude\\\\music_work_since_1008v3_20261009')}" if first != r.get("out_path") else ""
        rel_out = r.get("out_path")
        rel_out = os.path.relpath(rel_out, r"D:\musicclaude\music_work_since_1008v3_20261009") if rel_out else "NO_OUTPUT"
        f.write(f"{r['branch']}\t{r.get('model_key')}\t{r.get('model_name')}\t{r.get('prompt_version')}\ts={r.get('sample')}\t{r.get('status')}\t{r.get('seconds')}s\t{r.get('real_chars')}ch\t{str(r.get('started') or '')[:16]}\trun={r.get('run')}\t{rel_out}{dup_note}\tmeta={r.get('meta')}\n")
print("written inv_op60_A.txt")
