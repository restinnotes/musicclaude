"""Segmentation stage: produce machine-readable works/<work>/segments.json.

Routes (model work via gpt3 / GPT-6 Max; this script only renders, validates, compares):
  derive : from the score PDF alone            python seg.py derive --work op60 --title "..." --score X.pdf --reps 2
  select : from verified published structures  python seg.py select --work op61 --title "..." --measures 288 --sources DIR --score X.pdf
  compare: boundary agreement between proposals python seg.py compare --a A.json --b B.json
  freeze : write works/<work>/segments.json     python seg.py freeze --work op61 --from segmentation/op61/select_1/parsed.json --short "..."
"""
import argparse, json, re, sys, threading, zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evo  # noqa

ROOT = evo.ROOT


def parse(resp):
    m = re.findall(r"```json\s*(.*?)```", resp, re.S)
    return json.loads(m[-1] if m else resp)


def validate(d, total=None):
    """Return list of problems; empty means usable."""
    errs = []
    s = d.get("segments") or []
    n = total or d.get("total_measures")
    if not s:
        return ["no segments"]
    if s[0]["start"] != 1:
        errs.append(f"first segment starts at {s[0]['start']}")
    for a, b in zip(s, s[1:]):
        if b["start"] != a["end"] + 1:
            errs.append(f"gap/overlap between {a['start']}-{a['end']} and {b['start']}-{b['end']}")
    for x in s:
        if x["end"] < x["start"]:
            errs.append(f"empty segment {x}")
    if n and s[-1]["end"] != n:
        errs.append(f"last segment ends at {s[-1]['end']} but total is {n}")
    return errs


def starts(d):
    return [x["start"] for x in d["segments"]]


def agreement(a, b, tol=2):
    A, B = starts(a)[1:], starts(b)[1:]   # internal boundaries
    hit = lambda X, Y: sum(1 for x in X if any(abs(x - y) <= tol for y in Y))
    exact = len(set(A) & set(B))
    p = hit(A, B) / len(A) if A else 1
    r = hit(B, A) / len(B) if B else 1
    return {"n_a": len(A) + 1, "n_b": len(B) + 1, "exact_shared": exact, f"within_{tol}_a_in_b": round(p, 2),
            f"within_{tol}_b_in_a": round(r, 2), "only_a": [x for x in A if not any(abs(x - y) <= tol for y in B)],
            "only_b": [y for y in B if not any(abs(x - y) <= tol for x in A)]}


def run_one(text, out, attach, total):
    resp, log = evo.gpt3_call(text, out, attach)
    if resp is None:
        return
    try:
        d = parse(resp)
    except Exception as e:
        (out / "parse_error.txt").write_text(repr(e), encoding="utf-8"); return
    d["_validation"] = validate(d, total)
    (out / "parsed.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out.name, "segments", len(d.get("segments", [])), "problems", d["_validation"])


def cmd_derive(a):
    tpl = (ROOT / "prompts" / f"{a.prompt}.md").read_text(encoding="utf-8").replace("{WORK_TITLE}", a.title)
    ths = []
    for r in range(1, a.reps + 1):
        out = ROOT / "segmentation" / a.work / f"derive_{a.prompt}_{r}"
        if (out / "parsed.json").exists():
            continue
        ths.append(threading.Thread(target=run_one, args=(tpl, out, [a.score], a.measures)))
    for t in ths: t.start()
    for t in ths: t.join()


def cmd_select(a):
    src = Path(a.sources)
    bundle = ROOT / "segmentation" / a.work / "sources_bundle.zip"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle, "w") as z:
        for f in sorted(src.rglob("*")):
            if f.is_file() and f.suffix in (".md", ".json", ".txt"):
                z.write(f, f.relative_to(src))
    tpl = (ROOT / "prompts" / f"{a.prompt}.md").read_text(encoding="utf-8")
    tpl = tpl.replace("{WORK_TITLE}", a.title).replace("{TOTAL_MEASURES}", str(a.measures))
    att = [bundle] + ([a.score] if a.score else [])
    ths = []
    for r in range(1, a.reps + 1):
        out = ROOT / "segmentation" / a.work / f"select_{a.prompt}_{r}"
        if (out / "parsed.json").exists():
            continue
        ths.append(threading.Thread(target=run_one, args=(tpl, out, att, a.measures)))
    for t in ths: t.start()
    for t in ths: t.join()


def cmd_compare(a):
    A = json.loads(Path(a.a).read_text(encoding="utf-8"))
    B = json.loads(Path(a.b).read_text(encoding="utf-8"))
    print(json.dumps(agreement(A, B, a.tol), ensure_ascii=False))


def cmd_freeze(a):
    d = json.loads(Path(a.src).read_text(encoding="utf-8"))
    errs = validate(d, a.measures)
    if errs:
        raise SystemExit(f"not valid: {errs}")
    segs = [{"id": f"S{i:02d}", "start": x["start"], "end": x["end"], "label_source": x.get("label"),
             "boundary_event": x.get("boundary_event"), "confidence": x.get("confidence")} for i, x in enumerate(d["segments"], 1)]
    n = segs[-1]["end"]
    doc = {"schema": "segments/v1",
           "work": {"id": a.work, "title_zh": a.title, "short_zh": a.short or a.title, "total_measures": n},
           "unit": "measure", "interval": "closed", "segments": segs,
           "boundaries_left_closed": [s["start"] for s in segs] + [n + 1],
           "provenance": {"method": d.get("selected_source") and "published_structure" or "derived_from_score",
                          "selected_source": d.get("selected_source"), "selected_hierarchy": d.get("selected_hierarchy"),
                          "proposal_file": str(Path(a.src)), "numbering_note": d.get("numbering_note")}}
    out = ROOT / "works" / a.work / "segments.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("froze", out, len(segs), "segments")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="c", required=True)
    d = sp.add_parser("derive"); d.add_argument("--work", required=True); d.add_argument("--title", required=True)
    d.add_argument("--score", required=True); d.add_argument("--measures", type=int); d.add_argument("--reps", type=int, default=1)
    d.add_argument("--prompt", default="seg_derive_v1")
    s = sp.add_parser("select"); s.add_argument("--work", required=True); s.add_argument("--title", required=True)
    s.add_argument("--measures", type=int, required=True); s.add_argument("--sources", required=True); s.add_argument("--score")
    s.add_argument("--reps", type=int, default=1); s.add_argument("--prompt", default="seg_select_v1")
    c = sp.add_parser("compare"); c.add_argument("--a", required=True); c.add_argument("--b", required=True); c.add_argument("--tol", type=int, default=2)
    f = sp.add_parser("freeze"); f.add_argument("--work", required=True); f.add_argument("--src", required=True)
    f.add_argument("--title", required=True); f.add_argument("--short"); f.add_argument("--measures", type=int)
    a = ap.parse_args()
    {"derive": cmd_derive, "select": cmd_select, "compare": cmd_compare, "freeze": cmd_freeze}[a.c](a)
