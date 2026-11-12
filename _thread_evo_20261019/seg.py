"""Upstream segmentation stage -> machine-readable works/<key>/segmentation.json.

Two producers, one schema:
  import-op60          convert the existing published-structure upstream product (bead_chain structure.json, PTNA/C2)
  research <key>       GPT-6 Max (gpt3) extracts published structure tables and auto-selects one; script validates
Consumers never hand-type bar numbers: the Thread prompt's segment clause is rendered from this file (render_clause).

Schema: {work, short_name, total_measures, boundaries:[s1,...,sN,total+1] (right-open, last is a boundary, not a bar),
         segments:[{id,start,end,label}], source:{...}, method, alternatives:[...]}
"""
import json, sys
from pathlib import Path
import evo

WORKS = evo.ROOT / "works"
CFG = {
    "op60": {"work": "Frédéric Chopin, Barcarolle in F-sharp major, Op. 60", "ident": "单乐章，通行版本共116小节"},
    "op61": {"work": "Frédéric Chopin, Polonaise-Fantaisie in A-flat major, Op. 61", "ident": "单乐章，通行版本共288小节"},
    "op52": {"work": "Frédéric Chopin, Ballade No. 4 in F minor, Op. 52", "ident": "单乐章，通行版本共239小节"},
}


def validate(segs, total):
    errs = []
    if not segs:
        return ["no segments"]
    if segs[0]["start"] != 1:
        errs.append(f"first segment starts at {segs[0]['start']}")
    for a, b in zip(segs, segs[1:]):
        if b["start"] != a["end"] + 1:
            errs.append(f"gap/overlap between {a['start']}-{a['end']} and {b['start']}-{b['end']}")
    for s in segs:
        if not (isinstance(s["start"], int) and isinstance(s["end"], int)) or s["start"] > s["end"]:
            errs.append(f"bad segment {s}")
    if total and segs[-1]["end"] != total:
        errs.append(f"last segment ends at {segs[-1]['end']} != total {total}")
    return errs


def build(work, short, total, segs, source, method, alternatives=()):
    segs = [{"id": f"S{i+1:02d}", "start": s["start"], "end": s["end"], "label": s.get("label", "")} for i, s in enumerate(segs)]
    errs = validate(segs, total)
    assert not errs, errs
    return {"work": work, "short_name": short, "total_measures": total,
            "boundaries": [s["start"] for s in segs] + [total + 1], "segments": segs,
            "source": source, "method": method, "alternatives": list(alternatives)}


def save(key, d):
    p = WORKS / key; p.mkdir(parents=True, exist_ok=True)
    (p / "segmentation.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{key}: {len(d['segments'])} segments, boundaries {d['boundaries']}")


def load(key):
    return json.loads((WORKS / key / "segmentation.json").read_text(encoding="utf-8"))


def import_op60():
    s = json.loads((evo.ROOT / "inputs" / "op60_structure_published.json").read_text(encoding="utf-8"))
    segs = []
    for rng, lab in s["frozen_segments"]:
        a, b = map(int, rng.split("-")); segs.append({"start": a, "end": b, "label": lab})
    save("op60", build(CFG["op60"]["work"], "肖邦船歌", 116, segs, s["evidence"], "published_structure_select (bead_chain upstream, C2)"))


def research(key):
    c = CFG[key]
    tpl = evo.rd(evo.ROOT / "prompts" / "seg_published_v1.txt")
    msg = tpl.replace("{WORK}", c["work"]).replace("{IDENT}", c["ident"])
    rid = f"seg_{key}_v1"
    resp = evo.call(rid, msg, prompt_text=tpl, meta={"stage": "segmentation", "work": key})
    if not resp:
        sys.exit(f"{rid}: no response")
    j = evo.parse_json(resp)
    (evo.RUNS / rid / "parsed.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
    if j.get("insufficient_evidence"):
        sys.exit(f"{key}: insufficient evidence")
    sel = j["selected"]; total = int(j["total_measures"])
    segs = [{"start": int(x["start"]), "end": int(x["end"]), "label": x.get("label", "")} for x in sel["segments"]]
    errs = validate(segs, total)
    # The selected table must be one source's own level verbatim (no mixing).
    # Allowed: one level verbatim, or several of the same source's levels concatenated in order
    # (e.g. a source that lists sub-sections separately under each of its large parts).
    src = next((s for s in j["sources"] if s["id"] == sel["source_id"]), None)
    want = [(x["start"], x["end"]) for x in segs]
    lv = [[(int(x["start"]), int(x["end"])) for x in l["segments"]] for l in (src or {}).get("levels", [])
          if all(x.get("start") is not None and x.get("end") is not None for x in l["segments"])]
    if want not in lv and want != [p for l in lv for p in l]:
        errs.append("selected segments are not verbatim from one source")
    alts = []
    for s in j["sources"]:
        for l in s.get("levels", []):
            try:
                ss = [{"start": int(x["start"]), "end": int(x["end"]), "label": x.get("label", "")} for x in l["segments"]]
            except Exception:
                continue
            if not validate(ss, total):
                alts.append({"source_id": s["id"], "who": s.get("author_or_institution"), "level": l["level"],
                             "boundaries": [x["start"] for x in ss] + [total + 1]})
    (evo.RUNS / rid / "validation.json").write_text(json.dumps({"errors": errs, "valid_alternatives": alts}, ensure_ascii=False, indent=1), encoding="utf-8")
    if errs:
        sys.exit(f"{key}: validation failed: {errs}")
    source = {k: src.get(k) for k in ("id", "author_or_institution", "title", "url", "locator", "accessed_original")}
    source.update({"level": sel["level"], "reason": sel.get("reason"), "numbering_note": j.get("numbering_note"),
                   "disagreements": j.get("disagreements"), "run": rid})
    save(key if key != "op60" else "op60_auto", build(j.get("work") or c["work"], j.get("short_name") or c["work"], total, segs, source,
                    "published_structure_select (gpt3 GPT-6 Max web research + script validation)", alts))


# ---------- rendering the segment clause for Thread prompts ----------

def clause(d, style):
    if style == "orig":   # exactly the user's original P0 wording style: boundary list incl. right edge
        return "按照小节数" + ", ".join(map(str, d["boundaries"])) + " 来分段"
    if style == "note":   # original list + one clarifying clause about the right edge
        return ("按照小节数" + ", ".join(map(str, d["boundaries"])) +
                f" 来分段（最后一个数{d['boundaries'][-1]}只是全曲结束的边界，不是一个小节；全曲共{d['total_measures']}小节）")
    if style == "ranges":  # unambiguous closed ranges; the final boundary is never presented as a bar
        rs = "、".join(f"第{s['start']}–{s['end']}小节" for s in d["segments"])
        return f"按照以下{len(d['segments'])}个小节区间分段（全曲共{d['total_measures']}小节）：{rs}"
    raise ValueError(style)


if __name__ == "__main__":
    if sys.argv[1] == "import-op60":
        import_op60()
    elif sys.argv[1] == "research":
        research(sys.argv[2])
    elif sys.argv[1] == "check-beads":   # bead STRUCT must sit exactly on the upstream segmentation
        d = load(sys.argv[2])
        st = json.loads((evo.PKG / "03_Bead机器可读" / "14段_STRUCT轻量版.json").read_text(encoding="utf-8"))["segments"]
        got = [(x["segment"], x["mm_start"], x["mm_end"]) for x in st]
        want = [(s["id"], s["start"], s["end"]) for s in d["segments"]]
        assert got == want, (got, want)
        print(f"beads aligned: {len(got)} segments, {sum(len(x['beads']) for x in st)} beads on {d['boundaries']}")
    elif sys.argv[1] == "show":
        d = load(sys.argv[2]); print(clause(d, "orig")); print(clause(d, "ranges"))
