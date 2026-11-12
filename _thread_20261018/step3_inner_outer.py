"""Inner (1 per thread) -> Outer candidates (8 lanes per thread) -> Curator (1 per thread) -> clean Review (1 per thread)
-> Revise (resume inner session; resume curator session).

Selected threads come from runs/selected_threads.json (written by the research lead after reading the compare sessions):
  {"threads": [{"id": "TH1", "text": "<thread description in prose, incl. key moments>"} ...]}
"""
import json, random, sys
import thr, common

SEL = json.loads((thr.RUNS / "selected_threads.json").read_text(encoding="utf-8"))["threads"]
NT = str(len(thr.load_T()))
P = {k: (thr.ROOT / "prompts" / f"{k}.md").read_text(encoding="utf-8") for k in
     ("inner_v1", "outer_v1", "curate_v1", "review_v1", "revise_inner_v1", "revise_outer_v1")
     if (thr.ROOT / "prompts" / f"{k}.md").exists()}
OUTER_LANES = 8


def inner_text(tid, stage="inner"):
    d = thr.load(stage, tid)
    lines = [f"Thread：{next(t['text'] for t in SEL if t['id'] == tid)}", ""]
    for m in d["moments"]:
        lines.append(f"[{m['id']}｜{m.get('where')}｜{m.get('kind')}] 听到：{m.get('heard')}\n仍然活着：{m.get('alive')}\nInner：{m.get('inner')}")
    return "\n\n".join(lines)


def segs_of(tid, stage="inner"):
    d = thr.load(stage, tid)
    ss = sorted({m.get("segment") for m in d["moments"] if m.get("segment") in thr.SEGS})
    return "\n\n".join(common.bead_block(s) for s in ss)


def t_inner(tid):
    th = next(t for t in SEL if t["id"] == tid)
    p = (P["inner_v1"].replace("{THREAD}", th["text"]).replace("{TID}", tid).replace("{NT}", NT)
         .replace("{BEADS}", common.beads_text()))
    return thr.finish_json("inner", tid, thr.call("inner", tid, p, [common.t_zip()]))


def t_outer(tid, i):
    p = P["outer_v1"].replace("{INNER}", inner_text(tid))
    return thr.finish_json("outer", f"{tid}-{i}", thr.call("outer", f"{tid}-{i}", p))


def cands(tid):
    allc = []
    for i in range(1, OUTER_LANES + 1):
        d = thr.load("outer", f"{tid}-{i}") or {}
        allc += [c for c in d.get("candidates", []) if c.get("text")]
    random.Random(f"cur-{tid}").shuffle(allc)
    lab = {f"C{j+1:02d}": c for j, c in enumerate(allc)}
    (thr.RUNS / "outer" / f"{tid}.pool.json").write_text(json.dumps(lab, ensure_ascii=False, indent=1), encoding="utf-8")
    return "\n".join(f"- {k}［{c.get('moment')}］{c.get('text')}" for k, c in lab.items())


def t_curate(tid):
    p = (P["curate_v1"].replace("{INNER}", inner_text(tid)).replace("{CANDS}", cands(tid))
         .replace("{BEADS}", segs_of(tid)))
    return thr.finish_json("curate", tid, thr.call("curate", tid, p))


def package(tid, inner_stage="inner", cur_stage="curate"):
    d = thr.load(inner_stage, tid); c = thr.load(cur_stage, tid)
    out = [f"## Thread\n{next(t['text'] for t in SEL if t['id'] == tid)}", "## Inner（按时间）"]
    for m in d["moments"]:
        out.append(f"### {m['id']}｜{m.get('where')}\n听到：{m.get('heard')}\n仍然活着：{m.get('alive')}\n{m.get('inner')}")
    out.append(f"## 曲终回看\n{d.get('retrospective')}")
    out.append("## Outer")
    for j, s in enumerate(c.get("selected", []), 1):
        out.append(f"- O{j}［{s.get('moment')}］{s.get('text')}")
    return "\n\n".join(out)


def t_review(tid):
    p = (P["review_v1"].replace("{NT}", NT).replace("{PACKAGE}", package(tid)).replace("{BEADS}", common.beads_text()))
    return thr.finish_json("review", tid, thr.call("review", tid, p, [common.t_zip()]))


def t_rev_inner(tid):
    rv = {k: v for k, v in thr.load("review", tid).items() if k != "strongest"}
    cf = (thr.load("curate", tid) or {}).get("inner_feedback", [])
    p = (P["revise_inner_v1"].replace("{REVIEW}", json.dumps(rv, ensure_ascii=False, indent=0))
         .replace("{OUTER_FEEDBACK}", json.dumps(cf, ensure_ascii=False, indent=0)))
    return thr.finish_json("inner2", tid, thr.call("inner2", tid, p, session=thr.handle("inner", tid)))


def t_rev_outer(tid):
    rv = [i for i in thr.load("review", tid).get("issues", []) if i.get("type") in ("Outer", "时间", "套路", "其他")]
    p = (P["revise_outer_v1"].replace("{INNER}", inner_text(tid, "inner2"))
         .replace("{REVIEW}", json.dumps(rv, ensure_ascii=False, indent=0)))
    return thr.finish_json("curate2", tid, thr.call("curate2", tid, p, session=thr.handle("curate", tid)))


keys = []
for th in SEL:
    tid = th["id"]
    thr.task("inner", tid, lambda tid=tid: t_inner(tid)); keys.append(("inner", tid))
    for i in range(1, OUTER_LANES + 1):
        thr.task("outer", f"{tid}-{i}", lambda tid=tid, i=i: t_outer(tid, i), [("inner", tid)]); keys.append(("outer", f"{tid}-{i}"))
    thr.task("curate", tid, lambda tid=tid: t_curate(tid), [("outer", f"{tid}-{i}") for i in range(1, OUTER_LANES + 1)]); keys.append(("curate", tid))
    thr.task("review", tid, lambda tid=tid: t_review(tid), [("curate", tid)]); keys.append(("review", tid))
    thr.task("inner2", tid, lambda tid=tid: t_rev_inner(tid), [("review", tid)]); keys.append(("inner2", tid))
    thr.task("curate2", tid, lambda tid=tid: t_rev_outer(tid), [("inner2", tid)]); keys.append(("curate2", tid))

if __name__ == "__main__":
    stages = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    thr.run([k for k in keys if not stages or k[0] in stages])
