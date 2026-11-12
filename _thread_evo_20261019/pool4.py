"""Pool P27 (PLAN_20261026.md, "10-27 起的做法" step 3). pool3's grouping and original-words rule, with two changes:
- only web drafts: a draft (or, for the per-segment chain drafts d10c/d11c, a segment) joins only if its call really ran
  web.run (job result.json toolsUsed); the 10-24..10-27 no-web drafts flipped directions too often;
- D21 drafts are split: every in-segment turn (change + why_now) becomes its own candidate next to the segment-level
  reason, so the path can pick moment-to-moment mechanisms (the gap the P3a line lost on). A turn carries no judge
  labels of its own (the judges read the whole segment), so the picker judges it from its words.
ids: pl3<tag>_<work>_<sec>.  usage: THREAD_ROUTE=gpt3s python pool4.py <tag> <work>"""
import fnmatch, json, sys
from pathlib import Path
import covjudge, draft10, evo, pool, pool3

PATS = ["d10*", "d11o*", "d12*", "d20*", "d21*", "d22*"]      # 10-28: P28 adds D22 (coping)


def tools(rid):
    f = evo.RUNS / rid / "call.log"
    if not f.exists():
        return None
    jd = json.loads(f.read_text(encoding="utf-8")).get("job_directory")
    r = Path(jd) / "result.json" if jd else None
    return (json.loads(r.read_text(encoding="utf-8")).get("toolsUsed") or []) if r and r.exists() else None


def web(src, sec):
    for rid in (f"{src}_{sec}", f"{src}_x", src):          # chain segment call, retried whole draft, whole draft
        if (evo.RUNS / rid / "call.log").exists():
            return "web.run" in (tools(rid) or [])
    return False


def drafts(w, pats):
    return sorted(p.stem for p in draft10.OUT.glob(f"d*_{w}_*.json") if any(fnmatch.fnmatch(p.stem, x) for x in pats))


def cands(w, names):
    beads = covjudge.beads(w); out = {}; skipped = []
    for n in names:
        rs = [covjudge.result(n, j) for j in covjudge.JUDGES]
        if not all(rs):
            continue
        d = json.loads((draft10.OUT / f"{n}.json").read_text(encoding="utf-8"))
        for x in d["sections"]:
            if not web(n, x["sec"]):
                skipped.append(f"{n}:{x['sec']}"); continue
            sb = [b["id"] for b in beads if b["sec"] == x["sec"]]
            lab = {b: [r.get(b, {}).get("label") for r in rs] for b in sb}
            exp = [b for b in sb if all(l == "解释了" for l in lab[b])]
            loose = [b for b in sb if any(l == "解释了" for l in lab[b]) and b not in exp]
            opp = [b for b in sb if all(l == "相反" for l in lab[b])]
            if len(opp) > len(exp):
                continue
            ts = [t for t in x.get("turns") or [] if t.get("change") and "没有明显转折" not in t["change"]]
            base = {"src": n, "used": x.get("used") or "无", "opposite": opp}
            out.setdefault(x["sec"], []).append(base | {"feel": x["feel"], "thread": x["thread"].split("整体上：", 1)[-1] if ts else x["thread"],
                                                        "new": x.get("new") or [], "explains": exp, "partly": loose})
            out[x["sec"]] += [base | {"src": f"{n}#t{k}", "feel": f"{t['change']}（{t.get('how', '')}）", "thread": t.get("why_now", ""),
                                      "new": [], "explains": [], "partly": []} for k, t in enumerate(ts, 1)]
            cs = [c for c in x.get("cope") or [] if c.get("how") and "没有在对付" not in c["how"]]        # D22 coping items
            out[x["sec"]] += [base | {"src": f"{n}#c{k}", "feel": f"他用{c['how']}来对付这份感受", "thread": f"{c.get('effect', '')}；反过来{c.get('backfire', '')}",
                                      "new": [], "explains": [], "partly": []} for k, c in enumerate(cs, 1)]
    print(w, "no-web segments left out:", len(skipped), sorted({s.split(":")[0] for s in skipped}), flush=True)
    return out


if __name__ == "__main__":
    pool.drafts, pool.cands = drafts, cands
    pool3.build(sys.argv[1], sys.argv[2], PATS)
