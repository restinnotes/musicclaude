"""Assemble Op.61 Bead deliverables verbatim from the production-DAG outputs (no model calls, no text edits).

Per segment the final text is final2_b (after the whole-piece check) if it exists, else final_b.
Writes deliverable/:
  03_Bead机器可读/Sxx.json + 13段_STRUCT轻量版.json   (same fields as the Op.60 handoff package)
  02_Bead精简输入/D3_十三段reader.md
  struct/Sxx.json                                     (full STRUCT with quote_verified marks)
  checks.json                                         (script checks)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sat  # noqa: E402  (same A / structure / quote check)

OUT = ROOT / "deliverable"
WORK = "Frédéric Chopin: Polonaise-Fantaisie in A-flat major, Op.61"


def span(s):
    """First measure number or range in the field (fields may carry commentary after the range)."""
    m = re.search(r"(\d+)(?:\s*[–\-—~～至到]\s*(\d+))?", s or "")
    return (int(m.group(1)), int(m.group(2) or m.group(1))) if m else None


def found_in(q):
    nq = sat.norm(q)
    return sorted(k for k, v in sat.NA.items() if nq and nq in v)


def pick(seg):
    for st in ("final3_b", "final2_b", "final_b"):  # final3_b: S10 measures-only fix, text verified identical
        d = sat.load(st, seg)
        if d:
            return st, d
    return None, None


def main():
    for sub in ("03_Bead机器可读", "02_Bead精简输入", "struct"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    light, reader, checks, nb = [], [], {}, 0
    for seg, (rng, lab) in sat.SEGS.items():
        st, d = pick(seg)
        a, b = map(int, rng.split("-"))
        if not d:
            checks[seg] = {"missing": True}
            reader.append(f"## {seg} | mm.{a}–{b} |（缺失）\n")
            continue
        n, bad = sat.verify_quotes(d)
        ids = [x["id"] for x in d.get("beads", [])]
        out_of_seg = [f"{x['id']}:{x.get('measures')}" for x in d.get("beads", [])
                      if not (span(x.get("measures")) and a <= span(x["measures"])[0] <= span(x["measures"])[1] <= b)]
        tl_out = [t.get("measures") for t in d.get("timeline", [])
                  if not (span(t.get("measures")) and a <= span(t["measures"])[0] <= span(t["measures"])[1] <= b)]
        rel_bad = [f"{r.get('a')}-{r.get('b')}" for r in d.get("relations", []) if r.get("a") not in ids or r.get("b") not in ids]
        tl_bad = [x for t in d.get("timeline", []) for x in (t.get("beads") or []) if x not in ids]
        unverified = []
        def walk(x):
            if isinstance(x, dict):
                if x.get("quote_verified") is False:
                    x["quote_found_in"] = found_in(x.get("quote"))  # script mark only; model's src label kept as written
                    unverified.append({"src_label": x.get("src"), "quote": x.get("quote"), "verbatim_in": x["quote_found_in"]})
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d)
        checks[seg] = {"from": st, "beads": len(ids), "quotes": n, "quotes_unverified": unverified,
                       "bead_measures_outside_segment": out_of_seg, "timeline_outside_segment": tl_out,
                       "relation_unknown_ids": rel_bad, "timeline_unknown_ids": tl_bad,
                       "reader_unknown_ids": sorted(set(d.get("reader_uses", [])) - set(ids)),
                       "reader_chars": len(d.get("reader", ""))}
        nb += len(ids)
        (OUT / "struct" / f"{seg}.json").write_text(json.dumps(dict(d, _from=st), ensure_ascii=False, indent=1), encoding="utf-8")
        lt = {"segment": seg, "mm_start": a, "mm_end": b, "title": d.get("title"), "reader": d.get("reader"),
              "beads": [{k: x.get(k) for k in ("id", "role", "text", "measures", "placement", "performance_condition")} for x in d.get("beads", [])],
              "relations": d.get("relations", []), "timeline": d.get("timeline", [])}
        (OUT / "03_Bead机器可读" / f"{seg}.json").write_text(json.dumps(lt, ensure_ascii=False, indent=2), encoding="utf-8")
        light.append(lt)
        reader.append(f"## {seg} | mm.{a}–{b} | {d.get('title')}\n\n{(d.get('reader') or '').strip()}\n")
    (OUT / "03_Bead机器可读" / "13段_STRUCT轻量版.json").write_text(json.dumps(
        {"work": WORK, "segments": light, "segment_count": len(light), "bead_count": nb,
         "sources": "_bead_op61_20261020 production DAG (pool_v2 → gen_v1 → rev1_v1/rev2_v1 → final_v2 → piece_v1 → fix_v1), struct/S01.json ... struct/S13.json"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    head = ("# Bead 精简输入\n\n以下只提取原始 STRUCT 的正式文本，绝不是要求逐段复述的剧情提纲。Sxx 对应固定的小节区间（PTNA／塚田十三段，全曲 288 小节）。"
            "内容可能包含不同的感官或心理理解，允许不采用、调整和质疑，但不要把不相容的替代读法串成一个人接连发生的事件。\n\n")
    (OUT / "02_Bead精简输入" / "D3_十三段reader.md").write_text(head + "\n".join(reader), encoding="utf-8")
    (OUT / "checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in checks.items():
        print(k, v)
    print("beads total", nb)


if __name__ == "__main__":
    main()
