# -*- coding: utf-8 -*-
"""Scan heading-like lines of adopted (historical) sources to design unit split patterns."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

os = sys.modules["os"]  # noqa
import os as _os

LED = json.load(open(r"D:\musicclaude\_bead_auto_20261016\out\A36_LEDGER.json", encoding="utf-8"))
pat = re.compile(r"^#{1,4}\s+\S|^\*\*[^*]{2,120}\*\*$|^##\s|^---$|^第.{1,6}[段段阶时期]|.*mm\.\s*\d")

for a in LED["adopted"]:
    p = a.get("path")
    if not p or a.get("kind") != "historical" or a.get("pending"):
        continue
    try:
        txt = open(p, encoding="utf-8").read()
    except Exception as e:
        print(f"{a['src_id']} READ_FAIL {e}")
        continue
    lines = txt.split("\n")
    heads = [(i, l.strip()) for i, l in enumerate(lines) if pat.match(l.strip())]
    print(f"== {a['src_id']} {a['group']} ({len(lines)} lines, {a['chars']}ch)")
    for i, l in heads[:14]:
        print(f"   {i:4d} {l[:110]}")
    if len(heads) > 14:
        print(f"   ... +{len(heads)-14} more")
