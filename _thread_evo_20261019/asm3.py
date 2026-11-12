"""Bead assembly v3 (user 10-21: assembly collapsed the beads to the line's single reading). Beads are kept BY ROLE,
never filtered by fit with the line:
  P3 (condensed): every bead -> one short line keeping its own listening; main first, in-segment change with its bars,
                  alternatives as "也可以听成…"; only direct contradictions with the line are flagged.
  V3 (verbatim) : main bead's key sentence(s) + the whole in-segment-change bead + the alternative most DIFFERENT from the
                  main one (chosen for distinctness, not for fit).
usage: python asm3.py <work> <show_line_id>[,...]  -> evaluations/asm3/<P3|V3>_<line>.json/.md"""
import json, sys
import align, cmpasm, evo, segcheck, arts

OUT = evo.ROOT / "evaluations" / "asm3"
COND = ("下面每段有“线”（这件事此刻走到哪一步）和这一段的全部“当下体验”记录（珠子，标有角色）。珠子是另一位写作者对这段音乐的几种听法，"
        "它们的多样性本身就是内容，不要用线来筛选它们。\n"
        "请把每一颗珠子各压成一行（不超过 40 字）：用人话写此刻听到、感到的东西，保留它自己那种听法里最可感的画面或身体感；不讲乐理，不新编记录里没有的画面。"
        "段内变化类的珠子保留它的小节范围（如“9–17 小节……；18–23 小节……”）。\n"
        "只有当某颗珠子与线此刻的状态直接矛盾时，在 conflict 里写一句；不要因此删掉它。\n"
        "只输出一个 ```json 代码块：{\"segments\": {\"S01\": [{\"bead\": \"B1\", \"role\": \"主体验\", \"line\": \"…\"}], ...}, \"conflicts\": {\"S01\": \"…\"}}\n\n{L}")
PICK = ("下面每段有“线”和这一段的全部“当下体验”原句（B 开头编号，标有所属珠子和角色）。成品里，珠子要逐字照抄，不能改。请为每段挑句子："
        "1）主体验那颗珠子里最可感的 1–2 句；2）如果有段内变化的珠子，挑出能写清这一段内部怎样变化的句子（保留小节范围）；"
        "3）从其余“另一侧面”的珠子里，挑出与主体验差别最大的那一种听法的 1 句——按差别大来挑，不是按与线相合来挑。不挑只讲乐理的句子。\n"
        "只输出一个 ```json 代码块：{\"segments\": {\"S01\": [\"编号\", ...]}}\n\n{L}")


def segs_of(work, line):
    th = segcheck.to_json(arts.clean(evo.output(line)), work)
    st = {s["segment"]: s for s in json.loads(align.BEAD_STRUCT[work].read_text(encoding="utf-8"))["segments"]}
    out = []
    for s in th["segments"]:
        beads = st[s["id"]]["beads"]
        out.append({**s, "beads": beads,
                    "B": [(f"B{s['id'][1:]}.{b['id']}.{i}", x, b["id"], b.get("role")) for b in beads for i, x in enumerate(cmpasm.sents(b["text"]), 1)]})
    return out


def listing(segs, numbered):
    o = []
    for s in segs:
        o += [f"## {s['id']}｜第{s['start']}–{s['end']}小节", "【线】", s["text"].strip(), "【当下体验】"]
        if numbered:
            o += [f"[{i}]（{b}｜{r}）{x}" for i, x, b, r in s["B"]]
        else:
            o += [f"- {b['id']}（{b.get('role')}｜{b.get('measures')}）：{b['text']}" for b in s["beads"]]
    return "\n".join(o)


ORDER = {"主体验": 0, "段内变化": 1}


def render(name, line, work, segs, extra, kind, conflicts=None):
    md = [f"# {name}", "", f"线：{line}；珠子：{'逐字原句（按角色挑选）' if kind == 'V3' else '每颗珠子压成一行（按角色保留，不按线筛选）'}", ""]
    js = []
    for s in segs:
        e = extra.get(s["id"], [])
        md += [f"### 第{s['start']}–{s['end']}小节", "", s["text"].strip(), ""] + [f"> {x}" for x in e] + [""]
        js.append({"id": s["id"], "line": s["text"].strip(), "bead": e})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.md").write_text("\n".join(md), encoding="utf-8")
    (OUT / f"{name}.json").write_text(json.dumps({"line": line, "work": work, "kind": kind, "segments": js, "conflicts": conflicts or {}}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, "chars", sum(len(x["line"]) + sum(len(b) for b in x["bead"]) for x in js), "conflicts", len(conflicts or {}), flush=True)


def one(work, line):
    segs = segs_of(work, line)
    r = evo.call(f"a3c_{line}", COND.replace("{L}", listing(segs, False)), prompt_text=COND[:300], meta={"stage": "asm3_cond"})
    if r:
        j = evo.parse_json(r); P = {}
        for sid, items in j["segments"].items():
            items = sorted(items, key=lambda x: ORDER.get(x.get("role"), 2))
            P[sid] = [(("也可以听成：" if ORDER.get(x.get("role"), 2) == 2 and k > 0 else "") + x["line"]) for k, x in enumerate(items)]
        render(f"P3_{line}", line, work, segs, P, "P3", j.get("conflicts"))
    r = evo.call(f"a3v_{line}", PICK.replace("{L}", listing(segs, True)), prompt_text=PICK[:300], meta={"stage": "asm3_pick"})
    if r:
        idx = {i: x for s in segs for i, x, _, _ in s["B"]}
        V = {sid: [idx[k] for k in ids if k in idx] for sid, ids in evo.parse_json(r)["segments"].items()}
        render(f"V3_{line}", line, work, segs, V, "V3")


if __name__ == "__main__":
    w = sys.argv[1]
    evo.run_parallel([(l, (lambda l=l: one(w, l))) for l in sys.argv[2].split(",")], 4)
