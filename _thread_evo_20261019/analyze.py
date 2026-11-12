"""Aggregate blind-judge rows into per-condition tables (per judge and pooled), relative to the B0 anchor in-block.
usage: python analyze.py <eval_id> [<eval_id> ...]
"""
import json, re, sys
from collections import defaultdict
from statistics import mean
import evo

DIMS = ["thread", "accumulation", "reasons", "alive", "local_moments", "music_credibility", "overall"]


def cond_of(name):
    if name == "B0":
        return "B0"
    m = re.match(r"r1_([A-Z]\w*?)_(\w+?)_(D\d)_\d", name)
    if m:
        return f"{m[1]}|orig|{m[3]}"
    m = re.match(r"g_([A-Z]\w*?)_(op\d+)_(\w+?)_(D\d)_r\d", name)
    if m:
        return f"{m[1]}|{m[3]}|{m[4]}"
    m = re.match(r"l_([A-Z]\w*?)_(op\d+)_(\w+?)_D(\d)_from-", name)
    if m:
        return f"{m[1]}|{m[3]}|L{m[4]}"
    return name


def num(x):
    try:
        return float(x)
    except Exception:
        return None


def table(rows, title):
    by = defaultdict(list)
    for r in rows:
        by[cond_of(r["name"])].append(r)
    lines = [f"### {title}", "", "| condition | n | " + " | ".join(DIMS) + " | Δoverall vs B0 | mean rank/size | FP top |", "|" + "---|" * (len(DIMS) + 5)]
    for c in sorted(by, key=lambda c: -mean([num(r.get("overall")) or 0 for r in by[c]])):
        rs = by[c]
        vals = [mean([v for v in (num(r.get(d)) for r in rs) if v is not None] or [0]) for d in DIMS]
        dl = [r["d_b0"] for r in rs if r.get("d_b0") is not None]
        rk = [r["rank"] / r["n"] for r in rs if r.get("rank")]
        fp = defaultdict(int)
        for r in rs:
            for f in r.get("false_positives") or []:
                fp[str(f)[:2]] += 1
        fps = " ".join(f"{k}:{v}" for k, v in sorted(fp.items(), key=lambda kv: -kv[1])[:4])
        lines.append(f"| {c} | {len(rs)} | " + " | ".join(f"{v:.2f}" for v in vals) +
                     f" | {mean(dl):+.2f} | {mean(rk):.2f} | {fps} |" if dl else
                     f"| {c} | {len(rs)} | " + " | ".join(f"{v:.2f}" for v in vals) + f" | — | {mean(rk) if rk else 0:.2f} | {fps} |")
    return "\n".join(lines) + "\n"


def main(ids):
    rows = []
    for e in ids:
        rr = json.loads((evo.ROOT / "evaluations" / e / "rows.json").read_text(encoding="utf-8"))
        for r in rr:
            r["eval"] = e
        rows += rr
    b0 = {(r["eval"], r["block"]): num(r.get("overall")) for r in rows if r["name"] == "B0"}
    for r in rows:
        ref = b0.get((r["eval"], r["block"]))
        r["d_b0"] = (num(r.get("overall")) - ref) if (ref is not None and r["name"] != "B0" and num(r.get("overall")) is not None) else None
    out = [table(rows, "All judges pooled")]
    for j in sorted({r["judge"] for r in rows}):
        out.append(table([r for r in rows if r["judge"] == j], f"Judge: {j}"))
    txt = "\n".join(out)
    (evo.ROOT / "evaluations" / f"summary_{'+'.join(ids)}.md").write_text(txt, encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main(sys.argv[1:])
