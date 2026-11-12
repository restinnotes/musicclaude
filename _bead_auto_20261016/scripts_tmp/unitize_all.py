# -*- coding: utf-8 -*-
"""Unitize every adopted A source into mm.-annotated units, verbatim text.
Deterministic rules only:
  A) ^#{1,4} heading                     -> unit start (level=head)
  B) bullet line starting bold mm.       -> unit start (level=sub)
  C) standalone bold line starting mm.   -> unit start (level=head)
  D) standalone bold line containing mm. -> unit start (level=head)
  ranges: all "mm.N[-M]" matches in the unit's heading line (en/em/minus/tilde dash).
No-range units: range=null, flag for GPT-6w STEP3 review. Text never altered.
"""
import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")

LED = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\A36_LEDGER.json", encoding="utf-8"))
OUT = r"D:\musicclaude\_bead_auto_20261016\out"

RANGE = re.compile(r"mm\.\s*(\d{1,3})(?:\s*[-–—－~〜]\s*(\d{1,3}))?")
SPLIT_HEAD = re.compile(r"^\s*#{1,4}\s+\S")
SPLIT_BULLET_MM = re.compile(r"^\s*[-*]\s+\*\*mm\.?\s*\d")
SPLIT_BULLET_SECTION = re.compile(r"^\s*[-*]\s+\*\*对应小节\*\*")
SPLIT_NUM_BOLD_MM = re.compile(r"^\s*\d{1,2}[.、]\s*\*\*mm\.?\s*\d")
SPLIT_BOLD_MM = re.compile(r"^\s*\*\*mm\.?\s*\d")
SPLIT_BOLD_ANY = re.compile(r"^\s*\*\*[^*]+\*\*\s*$")

def parse_ranges(line):
    out = []
    for m in RANGE.finditer(line):
        a = int(m.group(1)); b = m.group(2)
        out.append((a, int(b) if b is not None else a))
    return out

def find_split(line):
    """return (kind, level, range_from_line) if line starts an unit else None."""
    if SPLIT_HEAD.match(line): return ("head", 1, True)
    if SPLIT_BULLET_MM.match(line): return ("bullet-mm", 2, True)
    if SPLIT_BULLET_SECTION.match(line): return ("bullet-section", 2, True)
    if SPLIT_NUM_BOLD_MM.match(line): return ("num-mm", 1, True)
    if SPLIT_BOLD_MM.match(line): return ("bold-mm", 1, True)
    if SPLIT_BOLD_ANY.match(line) and RANGE.search(line): return ("bold-mm-any", 1, True)
    return None

units_all = {}
bad = []
for a in LED["adopted"]:
    if a.get("pending") or not a.get("path"):
        continue
    src = a["src_id"]
    try:
        txt = open(a["path"], encoding="utf-8").read()
    except Exception as e:
        bad.append(f"{src} READ_FAIL {e}"); continue
    lines = txt.split("\n")
    units = []
    cur = None
    for i, line in enumerate(lines):
        sp = find_split(line)
        if sp:
            kind, level, is_head = sp
            cur = {"uid": f"{src}-U{len(units)+1:02d}", "kind": kind, "level": level,
                   "head_line": line.strip(), "lines": [line]}
            units.append(cur)
        elif cur is None:
            cur = {"uid": f"{src}-U01", "kind": "preamble", "level": 0,
                   "head_line": "", "lines": [line]}
            units.append(cur)
        else:
            cur["lines"].append(line)
    for u in units:
        u["text"] = "\n".join(u["lines"]); del u["lines"]
        u["ranges"] = parse_ranges(u["head_line"]) if u["kind"] not in ("preamble",) else []
        u["ranges"] = sorted(set(u["ranges"]), key=lambda r: r[0])  # dedupe
        u["range_main"] = u["ranges"][0] if u["ranges"] else None
        u["multi_ranges"] = len(u["ranges"]) > 1
        oob = [r for r in u["ranges"] if r[1] > 116 or r[0] > 116]
        u["flags"] = []
        if oob: u["flags"].append("out_of_bounds")
        if u["range_main"] is None: u["flags"].append("no_range")
        u["chars"] = len(u["text"])
    # title-only pass: head unit with no own range and no body beyond the heading
    # line -> fold its heading into the next unit (keeps pool free of empty titles)
    for i, u in enumerate(units):
        if u["kind"].startswith("head") and u["range_main"] is None and u["text"].strip() == u["head_line"] and i + 1 < len(units):
            nxt = units[i + 1]
            nxt.setdefault("title_inherited", [])
            nxt["title_inherited"].extend(u.get("title_inherited", []))  # chain
            nxt["title_inherited"].append(u["head_line"])
            u["title_only"] = True
    units_all[src] = {
        "path": a["path"], "group": a["group"], "kind_src": a.get("kind"),
        "n_lines": len(lines), "n_units": len(units),
        "text_chars": len(txt),
        "unit_chars": sum(u["chars"] for u in units),
        "units": units,
    }

missing_head = [s for s, d in units_all.items() if d["n_units"] <= 1 and d["units"][0]["range_main"] is None]
for s, d in units_all.items():
    d["n_units_real"] = len(real_units := [u for u in d["units"] if not u.get("title_only")])
    d["unit_chars"] = sum(u["chars"] for u in real_units)
    d["units"] = real_units  # drop title-only shells from JSON

print(f"sources={len(units_all)} bad={len(bad)}")
for s, d in units_all.items():
    rs = []
    for u in d["units"]:
        r = ",".join(f"{x[0]}-{x[1]}" for x in u["ranges"]) or "—"
        rs.append(r)
    flag_note = ""
    lost = d["n_lines"] - (sum(len(u["text"].split("\n")) + len(u.get("title_inherited", [])) for u in d["units"]))
    if lost not in (0, 1):  # 1 = benign trailing blank
        flag_note = f" LOST={lost}"
    print(f"{s:18s} units={d['n_units']:3d} lines={d['n_lines']:5d} chars={d['text_chars']:6d} ranges={' | '.join(rs)}{flag_note}")

# rare print of table data
tb = sum(1 for s, d in units_all.items() for u in d["units"] for f in u["flags"] if f == "no_range")
print(f"units_total={sum(d['n_units'] for d in units_all.values())} no_range_units={tb}")

json.dump({"_meta": {"generator": "unitize_all.py", "rules": "head/bullet-mm/bold-mm/bold-any-mm verbatim"},
           "sources": units_all},
          open(os.path.join(OUT, "A36_units.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("written", os.path.join(OUT, "A36_units.json"))
if bad:
    print("BAD:"); [print(" ", b) for b in bad]
