"""10-28 evening (user: "最后版本应该要是 thread 和珠子都是关系图形式结合到一起的吧"): join the P11 line graph with the bead
graph (beadgraph2, verbatim bead items with bars and kind) per section, with join.py's prompt and check unchanged:
each screen state shows a line step and the bead items it explains together; every bead item once, verbatim; another
hearing goes to a separate "也可以听成" state. The line comes from seq_repair (P<T>): steps with follows (→) and from (the
earlier segments whose new change causes the step, shown as ← with that change).
ids: jn<T>_<work>_<sec>.  usage: THREAD_ROUTE=gpt3s python join11.py <T> <work> [dry] -> evaluations/seq8/join<T>_<work>.json/.md"""
import json, re, sys
import covjudge, draft10, evo, join as J, node2b

S = evo.ROOT / "evaluations" / "seq8"


def clean(t):
    """P11/P12 steps sometimes name the earlier segment in the text ("S06让他知道", "S05里，"); the reader has no segment ids."""
    t = re.sub(r"(?:在)?S\d\d(?:[、和与]S\d\d)*(?:里|中)，?", "先前，", t)
    return re.sub(r"S\d\d(?:[、和与]S\d\d)*", "先前", t)


def graph(T, w):
    rows = json.loads((S / f"P{T}_{w}.json").read_text(encoding="utf-8"))
    txt = (S / f"P{T}_{w}.txt")
    center = txt.read_text(encoding="utf-8").split("\n")[1].replace("Center：", "", 1) if txt.exists() else ""
    segs = []
    for s in draft10.segs(w):
        e = rows[s["id"]]["edit"]
        segs.append({"sec": s["id"], "bars": f"{s['start']}–{s['end']}", "new": e.get("new") or [],
                     "items": [{"id": f"{s['id']}-{k}", "text": clean(x.get("text") or f"{x.get('feel', '')} {x.get('why', '')}"),
                                "follows": bool(x.get("follows")), "from": x.get("from") or []} for k, x in enumerate(e.get("items") or [], 1)]})
    return center, segs


def back(segs, it):
    """← lines for a step: each earlier segment it names, with that segment's first new change (shortened)."""
    by = {g["sec"]: g for g in segs}
    return [f"（{f}）{(by[f]['new'] or [''])[0][:40]}" for f in it["from"] if f in by and f != it["id"].split("-")[0]]


def arrows(seg, segs):
    """step id -> its ← lines, each earlier segment shown once per segment (P11 hangs the same ← on most steps)"""
    secs, seen, out = {g["sec"] for g in segs}, set(), {}
    for it in seg["items"]:
        fs = [f for f in it["from"] if f in secs and f != seg["sec"]]
        out[it["id"]] = [b for f, b in zip(fs, back(segs, it)) if f not in seen]
        seen |= set(fs)
    return out


def line_block(seg, segs):
    out, ar = [], arrows(seg, segs)
    for i, it in enumerate(seg["items"]):
        out.append(f"- {it['id']}：{'→ ' if it['follows'] and i else ''}{it['text']}")
        out += [f"    ← 接在：{b}" for b in ar[it["id"]]]
    return "\n".join(out)


def render(T, w, center, segs, plans):
    md = [f"# 肖邦{covjudge.NAME[w]}｜线与珠子（P{T}）\n", f"**Center：**{center}\n",
          "每段若干屏：**线**（他为什么此刻会这样）和它所说明的**珠子**（此刻听到的是什么样，原文逐字）同屏出现；"
          "“← 接在”指回前面某段确立的变化；“也可以听成”是和某颗珠子不能同时成立的另一种听法。\n"]
    lt = {it["id"]: it for g in segs for it in g["items"]}
    for g in segs:
        items = {x["id"]: x for x in J.bead_items(w, g["sec"])}; plan = plans.get(g["sec"]) or {}; ar = arrows(g, segs)
        md.append(f"\n---\n\n## {g['sec']} ｜ {g['bars']} 小节\n")
        shown, last = set(), None
        for k, s in enumerate(plan.get("states") or []):
            md.append(f"**屏 {k + 1}{'　也可以听成' if s.get('alt') else ''}**\n")
            for l in (s.get("line") or ([] if s.get("alt") else [last] if last else [])):
                it = lt.get(l)
                if not it:
                    continue
                own = l.startswith(g["sec"] + "-")
                md.append(f"> **线**　{'→ ' if it['follows'] and l in shown or (it['follows'] and own) else ''}{it['text']}"
                          + ("　<small>(续)</small>" if l in shown else "" if own else "　<small>(承上段)</small>"))
                if l not in shown:
                    md += [f">　<small>← 接在{b}</small>" for b in ar.get(l, [])]
                shown.add(l); last = l
            if s.get("line") or (last and not s.get("alt")):
                md.append("")
            md += [f"- {items[b]['text']}　<small>{items[b]['bars']}</small>" for b in s.get("beads") or [] if b in items]
            md.append("")
    out = S / f"join{T}_{w}.md"
    out.write_text("\n".join(md), encoding="utf-8")
    return out


def main(T, w, dry=False):
    center, segs = graph(T, w); jobs = []
    for i, g in enumerate(segs):
        rid = f"jn{T}_{w}_{g['sec']}"
        prev = line_block(segs[i - 1], segs) if i else "（这是第一段）"
        m = (J.P.replace("{WORK}", f"肖邦{covjudge.NAME[w]}").replace("{BARS}", g["bars"]).replace("{PREV}", prev)
             .replace("{LINE}", line_block(g, segs)).replace("{BEADS}", J.bead_block(J.bead_items(w, g["sec"]))))
        if dry:
            (S / f"prompt_{rid}.txt").write_text(m, encoding="utf-8"); print(rid, len(m), "字", flush=True); continue
        if not evo.done(rid):
            jobs.append(node2b.job(rid, m, {"stage": "join11", "sec": g["sec"]}, w="g6"))
    if dry:
        return
    evo.run_parallel(jobs, 2)
    plans, checks = {}, {}
    for g in segs:
        r = evo.parse_json(evo.output(f"jn{T}_{w}_{g['sec']}")) if evo.done(f"jn{T}_{w}_{g['sec']}") else {}
        plans[g["sec"]] = r or {}; checks[g["sec"]] = J.check(r or {}, g, J.bead_items(w, g["sec"]))
    (S / f"join{T}_{w}.json").write_text(json.dumps({"plans": plans, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = {s: c for s, c in checks.items() if c["missing_beads"] or c["dup_beads"] or c["unknown_beads"] or c["missing_lines"] or not c["line_order_ok"]}
    print(w, "结合检查：有问题的段", len(bad), json.dumps(bad, ensure_ascii=False)[:800], flush=True)
    print(render(T, w, center, segs, plans), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "dry" in sys.argv[3:])
