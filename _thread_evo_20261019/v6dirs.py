"""A2 whole-piece repair and B1 chained generation; prompts owned by v6dirs_prompts.

python v6dirs.py whole <op60|op61> [tag=w1]
python v6dirs.py rad   <op60|op61> [tag=s1]
python v6dirs.py dry   <op60|op61>       # no model calls
"""
import argparse
import json
import re
import sys

import covjudge
import draft10
import evo
import v6dirs_prompts as prompts
import v6fix


FIRST = "（这是第一段，前面还没有）"


def _target(w, tag):
    if w not in covjudge.NAME:
        raise ValueError(f"未知作品：{w}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", tag):
        raise ValueError("tag 只能包含英文字母、数字、下划线和连字符")
    if tag == "r2":
        raise ValueError("r2 属于正在运行的 A1，不能覆盖；请使用独立 tag")


def _record(errors, text):
    errors.append(text)
    print(f"WARNING: {text}", file=sys.stderr, flush=True)


def _ask(rid, message, model, stage, web=False):
    meta = {"stage": stage}
    if web:
        meta["web"] = True
    if not evo.done(rid):
        evo.call(rid, message, model=model, meta=meta)
    return v6fix.parse(rid)


def _whole_ok(result):
    return isinstance(result, dict) and isinstance(result.get("segments"), list)


def _segment_ok(result):
    return isinstance(result, dict) and isinstance(result.get("items"), list)


def _generate(rid, message, stage, valid):
    for run_id, model in ((rid, evo.G6), (rid + "b", evo.G56)):
        result = _ask(run_id, message, model, stage, web=True)
        if valid(result):
            return result
    raise RuntimeError(f"{rid}: G6 和 G56 均未返回可解析的结果，停")


def whole_message(w, g6=None):
    if g6 is None:
        g6 = v6fix.v6(w)
    diag = "\n\n".join(f"### {s['id']}\n" + v6fix.diag_for(w, s["id"])
                       for s in draft10.segs(w))
    return prompts.WHOLE.format(
        NAME=covjudge.NAME[w], WHAT=v6fix.WHAT, CENTER=g6["center"],
        V6=v6fix.view(g6, ids=True, center=False), BEADS=v6fix.beads(w), DIAG=diag)


def _assemble(w, result, center, errors):
    by_sec = {x.get("sec"): x for x in result["segments"] if isinstance(x, dict)}
    graph = {"center": center, "segments": []}
    edits = {}
    for s in draft10.segs(w):
        sec = s["id"]
        edit = by_sec.get(sec)
        if edit is None:
            _record(errors, f"{w} {sec}: 整首输出缺段，使用空 items")
            edit = {"sec": sec, "items": [], "because": [], "gaps": []}
        edits[sec] = edit
        graph["segments"].append(v6fix.seg_graph(edit, sec, s))
    return v6fix.tidy(graph), edits


def _save(w, tag, graph, rows, direction, errors, **extra):
    v6fix.OUT.mkdir(parents=True, exist_ok=True)
    data = {"graph": graph, "rows": rows, **extra}
    if errors:
        data["errors"] = list(errors)
    (v6fix.OUT / f"{w}_{tag}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    opus = "Op.60" if w == "op60" else "Op.61"
    (v6fix.OUT / f"{w}_{tag}.md").write_text(
        f"# {opus}｜关系图（{direction} {tag}）\n\n" + v6fix.view(graph), encoding="utf-8")


def whole(w, tag="w1", base=None):
    """base: an earlier A2 tag; then the first call is a refine of that round with the blind judges' notes (WHOLE_REFINE)"""
    _target(w, tag)
    g6 = v6fix.v6(w)
    message = whole_message(w, g6)
    if base:
        nt = v6fix.notes_from_blind(base).get(w) or {}
        order = [s["id"] for s in draft10.segs(w)]
        notes = "\n\n".join(f"### {sec}\n" + "\n".join(f"- {n}" for n in nt[sec]) for sec in order if nt.get(sec))
        message += prompts.WHOLE_REFINE.format(PREV=v6fix.view(v6fix.graph_of(w, base), ids=True, center=False), NOTES=notes or "（无）")
    errors = []
    result = _generate(f"v6w_{w}_{tag}", message, "v6-whole", _whole_ok)
    graph, edits = _assemble(w, result, g6["center"], errors)
    jobs = []
    for i, new in enumerate(graph["segments"]):
        sec = new["sec"]
        done = {"center": g6["center"], "segments": graph["segments"][:i]}
        cur = {"center": g6["center"], "segments": [x for x in g6["segments"] if x["sec"] == sec]}
        jobs.append((sec, lambda sec=sec, done=done, cur=cur, new=new:
                     v6fix.check(w, sec, tag, done, cur, new)))
    checks = evo.run_parallel(jobs, 4)
    rows = {}
    for new in graph["segments"]:
        sec = new["sec"]
        k = checks.get(sec)
        if not isinstance(k, dict) or not k:
            raise RuntimeError(f"{w} {sec}: 核对未返回可解析的结果，停")
        rows[sec] = {"edit": edits[sec], "check": k,
                     "notes": v6fix.review_notes(k, new, edits[sec]), "revised": False}
    if any(row["notes"] for row in rows.values()):
        notes = "\n\n".join(f"### {sec}\n" + "\n".join(row["notes"])
                            for sec, row in rows.items() if row["notes"])
        revision = _ask(
            f"v6wr_{w}_{tag}", message + prompts.WHOLE_REV.format(
                NOTES=notes, PREV=v6fix.view(graph, ids=True, center=False)),
            evo.G6, "v6-whole-rev", web=True)
        if _whole_ok(revision):
            result = revision
            graph, edits = _assemble(w, result, g6["center"], errors)
            for sec, row in rows.items():
                row.update(edit=edits[sec], revised=True)
        else:
            _record(errors, f"{w}: 整首退改解析失败，保留第一版")
    _save(w, tag, graph, rows, "A2 整首修补", errors, changes=result.get("changes") or [])
    old = {x["sec"]: x for x in g6["segments"]}
    for new in graph["segments"]:
        sec = new["sec"]
        row = rows[sec]
        print(f"{w} {sec}: v6 {len(old[sec]['items'])} 条 → {len(new['items'])} 条"
              f" | 意见 {len(row['notes'])} | 退改 {row['revised']}", flush=True)
    return graph


def _done(graph):
    return v6fix.view(graph, ids=True, center=False) if graph["segments"] else FIRST


def rad_message(w, s, graph):
    segs = "\n".join(f"{x['id']}｜{x['start']}–{x['end']} 小节" for x in draft10.segs(w))
    return prompts.RAD.format(NAME=covjudge.NAME[w], SEC=s["id"], A=s["start"], B=s["end"],
                              WHAT=prompts.WHAT_RAD, SEGS=segs, DONE=_done(graph),
                              BEADS=v6fix.beads(w, s["id"]))


def rad_check_message(w, sec, graph, new):
    return prompts.RAD_CHK.format(
        DONE=_done(graph), NEW=v6fix.view({"center": "", "segments": [new]}, ids=True, center=False)
        + v6fix._links(new), BEADS=v6fix.beads(w, sec))


def rad_center_message(w, graph):
    return prompts.RAD_CENTER.format(
        NAME=covjudge.NAME[w], LINE=v6fix.view(graph, ids=False, center=False))


def rad_notes(k, new, edit):
    # Reuse exactly the A1 criteria, except B1 has progression instead of lost-v6.
    notes = v6fix.review_notes({key: value for key, value in k.items() if key != "lost"}, new, edit)
    if k.get("progress") == "否":
        notes.append(f"- 递进不够：{k.get('progress_why', '')}")
    return notes


def _rad_segment(edit, s):
    new = v6fix.seg_graph(edit, s["id"], s)
    new["relation"] = ""
    return new


def rad(w, tag="s1"):
    _target(w, tag)
    graph = {"center": "", "segments": []}
    rows, errors = {}, []
    for s in draft10.segs(w):
        sec = s["id"]
        message = rad_message(w, s, graph)
        edit = _generate(f"v6s_{w}_{sec}_{tag}", message, "v6-rad", _segment_ok)
        new = _rad_segment(edit, s)
        k = _ask(f"v6sk_{w}_{sec}_{tag}", rad_check_message(w, sec, graph, new),
                 evo.G56, "v6-rad-check")
        if not isinstance(k, dict) or not k:
            raise RuntimeError(f"{w} {sec}: 核对未返回可解析的结果，停；已完成的段保留在进度文件")
        notes = rad_notes(k, new, edit)
        revised = False
        if notes:
            prev = v6fix.view({"center": "", "segments": [new]}, ids=True, center=False)
            revision = _ask(f"v6sr_{w}_{sec}_{tag}",
                            message + prompts.RAD_REV.format(NOTES="\n".join(notes), PREV=prev),
                            evo.G6, "v6-rad-rev", web=True)
            if _segment_ok(revision):
                edit, new, revised = revision, _rad_segment(revision, s), True
            else:
                _record(errors, f"{w} {sec}: 逐段退改解析失败，保留第一版")
        graph["segments"].append(new)
        v6fix.tidy(graph)
        rows[sec] = {"edit": edit, "check": k, "notes": notes, "revised": revised}
        _save(w, tag, graph, rows, "B1 激进逐段", errors)
        print(f"{w} {sec}: {len(new['items'])} 条 | 意见 {len(notes)} | 退改 {revised}"
              f" | gaps {[x.get('bead') for x in edit.get('gaps') or []]}", flush=True)
    result = _ask(f"v6sc_{w}_{tag}", rad_center_message(w, graph), evo.G6, "v6-rad-center")
    if not (isinstance(result, dict) and isinstance(result.get("center"), str)
            and result["center"].strip()
            and (result.get("relations") is None or isinstance(result["relations"], dict))):
        raise RuntimeError(f"{w}: Center 未返回可解析的结果，停；逐段进度已保存")
    graph["center"] = result["center"]
    relations = result.get("relations") or {}
    for seg in graph["segments"]:
        sec = seg["sec"]
        relation = relations.get(sec)
        if not relation:
            relation = "正在面对"
            _record(errors, f"{w} {sec}: Center 缺少 relation，填入正在面对")
        seg["relation"] = relation
    _save(w, tag, graph, rows, "B1 激进逐段", errors)
    return graph


def dry(w):
    segs = draft10.segs(w)
    graph = {"center": "", "segments": []}
    first = _rad_segment({"items": [{"id": f"{segs[0]['id']}-1", "text": "他还说不清自己的感受。",
                                    "key": "说不清", "explains": ["B1"]}], "because": [], "gaps": []}, segs[0])
    fake = {"center": "", "segments": [first]}
    second = _rad_segment({"items": [{"id": f"{segs[1]['id']}-1", "text": "刚才的犹豫让他多想了一会儿。",
                                     "key": "犹豫", "explains": ["B1"]}],
                           "because": [{"from": first["items"][0]["id"], "to": f"{segs[1]['id']}-1",
                                        "rel": "提供理由"}]}, segs[1])
    messages = {"whole": whole_message(w), "rad_first": rad_message(w, segs[0], graph),
                "rad_second": rad_message(w, segs[1], fake),
                "rad_check": rad_check_message(w, segs[1]["id"], fake, second),
                "rad_center": rad_center_message(w, {"center": "", "segments": [first, second]})}
    out = evo.ROOT / "_codex"
    out.mkdir(parents=True, exist_ok=True)
    for name, message in messages.items():
        path = out / f"dry_{w}_{name}.txt"
        path.write_text(message, encoding="utf-8")
        print(f"{path.name}: {len(message)} 字符", flush=True)
    return messages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direction", choices=("whole", "rad", "dry"))
    parser.add_argument("work", choices=("op60", "op61"))
    parser.add_argument("tag", nargs="?")
    parser.add_argument("--base", default=None, help="whole only: refine this earlier A2 tag with its blind notes")
    args = parser.parse_args()
    try:
        if args.direction == "dry":
            if args.tag is not None:
                parser.error("dry 不接受 tag")
            dry(args.work)
        elif args.direction == "whole":
            whole(args.work, args.tag or "w1", base=args.base)
        else:
            rad(args.work, args.tag or "s1")
    except (RuntimeError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
