# -*- coding: utf-8 -*-
"""Full inventory of A-int / A-web / A-orig research outputs in music_work_since_1008v3_20261009."""
import json, os, re, hashlib, sys
sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\musicclaude\music_work_since_1008v3_20261009"
RUNS_ROOT = os.path.join(ROOT, "runs")

records = []
sha_to_paths = {}

def sha_of(p):
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def add_record(**kw):
    rec = kw
    records.append(rec)

# Pass 1: all */meta/*.json
for rundir in sorted(os.listdir(RUNS_ROOT)):
    rd = os.path.join(RUNS_ROOT, rundir)
    if not os.path.isdir(rd):
        continue
    metadir = os.path.join(rd, "meta")
    if not os.path.isdir(metadir):
        continue
    for fn in os.listdir(metadir):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(metadir, fn)
        try:
            with open(p, encoding="utf-8") as f:
                m = json.load(f)
        except Exception as e:
            add_record(run=rundir, meta=fn, parse_error=str(e))
            continue
        branch = m.get("branch") or ""
        if not (branch.startswith("A-int") or branch.startswith("A-web") or branch.startswith("A-orig")
                or re.match(r"A[-_]?(int|web|orig)", fn)):
            continue
        outp = m.get("output_file")
        out_abs = os.path.join(rd, outp) if outp else None
        has_out = out_abs and os.path.isfile(out_abs) and os.path.getsize(out_abs) > 0
        real_chars = os.path.getsize(out_abs) if has_out else 0
        sha = sha_of(out_abs) if has_out else None
        add_record(run=rundir, meta=fn, job_id=m.get("job_id"), branch=branch,
                   model_key=m.get("model_key"), model_name=m.get("model_name"),
                   prompt_version=m.get("prompt_version"), work=m.get("work_key"),
                   sample=m.get("sample"), status=m.get("status"),
                   exit=m.get("exit_code"), seconds=m.get("seconds"),
                   started=m.get("started"), claimed_chars=m.get("output_chars"),
                   out_path=out_abs, out_exists=has_out, real_chars=real_chars, sha=sha)

# Pass 2: orphan A-* md files not covered by meta (search all runs)
covered = {r.get("out_path") for r in records if r.get("out_path")}
for rundir in sorted(os.listdir(RUNS_ROOT)):
    rd = os.path.join(RUNS_ROOT, rundir)
    if not os.path.isdir(rd):
        continue
    for dirpath, dirs, files in os.walk(rd):
        if "/meta/" in dirpath.replace(os.sep, "/") and dirpath.split(os.sep)[-1] == "meta":
            # only .md orphan candidates skipped here
            continue
        for fn in files:
            if not re.match(r"A[-_](int|web|orig)", fn):
                continue
            if not (fn.endswith(".md") or fn.endswith(".txt") or fn.endswith(".json")):
                continue
            p = os.path.join(dirpath, fn)
            if "outputs" + os.sep + "raw" in p:
                continue
            npc = p.lower()
            filesz = os.path.getsize(p)
            if fn.endswith(".md") or fn.endswith(".txt"):
                sha = sha_of(p)
                add_record(run=rundir, rel=os.path.relpath(p, RUNS_ROOT), file=fn,
                           real_chars=filesz, sha=sha, orphan=True, out_path=p)
    pass

with open(r"D:\musicclaude\_bead_auto_20261016\out\inventory_A2.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=1)

# dedupe map by sha among non-empty
from collections import defaultdict
by_sha = defaultdict(list)
for r in records:
    if r.get("sha"):
        by_sha[r["sha"]].append(r["out_path"] or r.get("rel"))

groups = {k: v for k, v in by_sha.items() if len(v) > 1}
print(f"total records: {len(records)}")
print(f"duplicate sha groups: {len(groups)}")
with open(r"D:\musicclaude\_bead_auto_20261016\out\inventory_A2_dups.json", "w", encoding="utf-8") as f:
    json.dump({k: v for k, v in by_sha.items() if len(v) > 1}, f, ensure_ascii=False, indent=1)

# summary per branch x model_key x model_name x work
summ = defaultdict(lambda: {"n": 0, "ok": 0, "chars": 0})
for r in records:
    if r.get("orphan"):
        continue
    key = (r["branch"], r.get("model_key"), r.get("model_name"), r.get("work"), r.get("prompt_version"))
    d = summ[key]
    d["n"] += 1
    if r.get("status") == "ok":
        d["ok"] += 1
        d["chars"] += r.get("real_chars") or 0
for key in sorted(summ):
    d = summ[key]
    print("|".join([str(x) for x in key]), f"meta={d['n']} ok={d['ok']} chars={d['chars']}")
