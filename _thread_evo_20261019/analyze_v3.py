"""Per-condition table for judge_v3 rows (pooled and per judge), with in-block delta vs the B0 anchor.
usage: python analyze_v3.py <eval_id>"""
import json, sys
from collections import defaultdict
from statistics import mean
import analyze, evo


def f(x):
    try:
        return float(x)
    except Exception:
        return None


def table(rows, title):
    b0 = {r["block"]: f(r["overall"]) for r in rows if r["name"] == "B0"}
    by = defaultdict(list)
    for r in rows:
        by[analyze.cond_of(r["name"])].append(r)
    cols = ["overall", "self_driven", "music_driven", "undriven", "why_now", "history", "connection", "alive", "plot", "retell"]
    out = [f"### {title}", "", "| 条件 | 评审数 | " + " | ".join(cols) + " | Δ vs B0 | 联系只在音乐 |", "|" + "---|" * (len(cols) + 4)]
    for c, rs in sorted(by.items(), key=lambda kv: -mean([f(r["overall"]) or 0 for r in kv[1]])):
        vals = []
        for k in cols:
            v = [f(r.get(k)) for r in rs if f(r.get(k)) is not None]
            vals.append(f"{mean(v):.2f}" if v else "—")
        d = [f(r["overall"]) - b0[r["block"]] for r in rs if r["name"] != "B0" and r["block"] in b0 and f(r["overall"]) is not None]
        mo = sum(bool(r.get("conn_musical_only")) for r in rs)
        out.append(f"| {c} | {len(rs)} | " + " | ".join(vals) + f" | {mean(d):+.2f} | {mo}/{len(rs)} |" if d else
                   f"| {c} | {len(rs)} | " + " | ".join(vals) + f" | — | {mo}/{len(rs)} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    eid = sys.argv[1]
    rows = json.loads((evo.ROOT / "evaluations" / eid / "rows.json").read_text(encoding="utf-8"))
    txt = [table(rows, "三位评委合并")] + [table([r for r in rows if r["judge"] == j], f"评委：{j}") for j in sorted({r["judge"] for r in rows})]
    (evo.ROOT / "evaluations" / f"summary_{eid}.md").write_text("\n".join(txt), encoding="utf-8")
    print("\n".join(txt))
