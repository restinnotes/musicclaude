"""10-29: w8 = w7 (Op.60 S14; Op.61 S07/S11/S13 refixed on w6) + w7x (Op.60 S02/S04; Op.61 S01/S08 refixed on w6), run in parallel
for time; the two touch disjoint segments. Links to ids that no longer exist are dropped by tidy."""
import json
import v6fix as V
SW = {"op60": {"S02", "S04"}, "op61": {"S01", "S08"}}
for w in ("op60", "op61"):
    a = json.loads((V.OUT / f"{w}_w7.json").read_text(encoding="utf-8")); b = json.loads((V.OUT / f"{w}_w7x.json").read_text(encoding="utf-8"))
    bs = {s["sec"]: s for s in b["graph"]["segments"]}
    g = {"center": a["graph"]["center"], "segments": [bs[s["sec"]] if s["sec"] in SW[w] else s for s in a["graph"]["segments"]]}
    rows = dict(a["rows"]); rows.update({k: v for k, v in b["rows"].items() if k in SW[w]})
    V.tidy(g)
    json.dump({"graph": g, "rows": rows, "base": "w7+w7x"}, open(V.OUT / f"{w}_w8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    (V.OUT / f"{w}_w8.md").write_text(f"# {'Op.60' if w == 'op60' else 'Op.61'}｜关系图（在 v6 上修补，w8）\n\n" + V.view(g), encoding="utf-8")
    print(w, "merged", sum(len(s["items"]) for s in g["segments"]), "条", flush=True)
