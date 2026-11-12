from pathlib import Path
p=Path("pipe.py"); t=p.read_text(encoding="utf-8")
old='''        m = _re.search(r"\[.*\]", evo.output(rid) or "", _re.S)
'''
assert old in t
new='''        # 11-02: the web route sometimes returns markdown-escaped text (a backslash at each line end, &#x20; for spaces); undo that first
        raw = (evo.output(rid) or "").replace("&#x20;", " ").replace("\\\n", "\n").replace("\\[", "[").replace("\\]", "]").replace("\\_", "_")
        try:
            obj = json.loads(raw.strip().rstrip("\\\\").strip())
            result = obj if isinstance(obj, dict) else {"items": obj}
        except Exception:
            pass
        m = _re.search(r"\[.*\]", raw, _re.S) if result is None else None
'''
t=t.replace(old,new)
p.write_text(t,encoding="utf-8")
