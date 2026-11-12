from pathlib import Path
p = Path("pipe.py"); t = p.read_text(encoding="utf-8")
old = "    result = V.parse(rid)\n"
assert old in t
new = '''    result = V.parse(rid)
    if result is None:      # 11-02: a model may answer with a bare JSON array (scqb_op60_A1); keep it as {"items": [...]}
        import re as _re
        m = _re.search(r"\[.*\]", evo.output(rid) or "", _re.S)
        if m:
            try:
                result = {"items": json.loads(m.group(0))}
            except Exception:
                pass
'''
t = t.replace(old, new, 1); p.write_text(t, encoding="utf-8"); print("ok")
