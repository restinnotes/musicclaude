"""Nodes 3+4 for a bullet-form line (route A): per segment, the line's points + 1-2 verbatim bead sentences chosen to fit.
  V (main): bead sentences verbatim, selected by GPT for fit with the line's state; conflicts flagged.
  P (experimental, rewrites beads): each segment's beads condensed into 1-2 plain lines of present experience.
usage: python asm2.py <work> <line_id>[,<line_id>...]   -> evaluations/asm2/<V|P>_<line>.md/.json
"""
import json, sys
import align, arts, cmpasm, evo, segcheck

OUT = evo.ROOT / "evaluations" / "asm2"
PICK = ("下面每段有两部分：“线”（讲他此刻怎么了、为什么、背后的心理机制），以及这一段的“当下体验”原句（B 开头编号）。"
        "成品里，每段先放线，再放你挑的 1–2 句当下体验原句（逐字照抄，不改）。请为每段挑出最能让读者**感到**线此刻所说状态的原句："
        "优先挑可感的、身体化的、有画面的句子；不挑只讲乐理的句子；不挑和线此刻的状态相矛盾的句子——如果这一段没有合适的，就不挑，并说明原因。\n"
        "只输出一个 ```json 代码块：{\"segments\": {\"S01\": {\"keep\": [\"编号\"], \"conflict\": \"若有矛盾简述，否则空\"}}}\n\n{L}")
COND = ("下面每段有“线”和这一段的“当下体验”记录。请把每段的当下体验压成 1–2 行：用人话写此刻听到、感到的东西，保留记录里最可感的画面或身体感，"
        "并让它与线此刻说的状态相合；不讲乐理，不写过渡和修饰，不新编记录里没有的画面。\n"
        "只输出一个 ```json 代码块：{\"segments\": {\"S01\": [\"一行\", \"一行\"]}}\n\n{L}")


def segs_of(work, line):
    th = segcheck.to_json(arts.clean(evo.output(line)), work)
    _, beads = align.beads_text(work); out = []
    for s in th["segments"]:
        B = [(f"B{bid.replace('/', '.')[1:]}.{i}", x) for bid, txt in beads.items() if bid.startswith(s["id"] + "/")
             for i, x in enumerate(cmpasm.sents(txt), 1)]
        out.append({**s, "B": B})
    return out


def listing(segs, raw=False):
    o = []
    for s in segs:
        o += [f"## {s['id']}｜第{s['start']}–{s['end']}小节", "【线】", s["text"].strip(), "【当下体验】"]
        o += [x for _, x in s["B"]] if raw else [f"[{i}] {x}" for i, x in s["B"]]
    return "\n".join(o)


def render(name, line, work, segs, extra, kind):
    md = [f"# {name}", "", f"线：{line}；珠子：{'逐字原句（模型挑选）' if kind == 'V' else '实验：模型压缩改写的当下体验'}", ""]
    js = []
    for s in segs:
        e = extra.get(s["id"], [])
        md += [f"### 第{s['start']}–{s['end']}小节", "", s["text"].strip(), ""] + [f"> 【珠子】{x}" for x in e] + [""]
        js.append({"id": s["id"], "line": s["text"].strip(), "bead": e})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.md").write_text("\n".join(md), encoding="utf-8")
    (OUT / f"{name}.json").write_text(json.dumps({"line": line, "work": work, "kind": kind, "segments": js}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, "chars", sum(len(x["line"]) + sum(len(b) for b in x["bead"]) for x in js), flush=True)


def one(work, line):
    segs = segs_of(work, line)
    r = evo.call(f"apick_{line}", PICK.replace("{L}", listing(segs)), prompt_text=PICK[:300], meta={"stage": "asm2_pick"})
    if r:
        j = evo.parse_json(r)["segments"]; idx = {i: x for s in segs for i, x in s["B"]}
        v = {sid: [idx[k] for k in d.get("keep", []) if k in idx] for sid, d in j.items()}
        for p in (x for xs in v.values() for x in xs):
            assert any(p in t for t in align.beads_text(work)[1].values()), p
        render(f"V_{line}", line, work, segs, v, "V")
        (OUT / f"V_{line}.conflicts.json").write_text(json.dumps({k: d.get("conflict") for k, d in j.items() if d.get("conflict")}, ensure_ascii=False, indent=1), encoding="utf-8")
    r = evo.call(f"acond_{line}", COND.replace("{L}", listing(segs, raw=True)), prompt_text=COND[:300], meta={"stage": "asm2_cond"})
    if r:
        render(f"P_{line}", line, work, segs, evo.parse_json(r)["segments"], "P")


if __name__ == "__main__":
    w = sys.argv[1]
    evo.run_parallel([(l, (lambda l=l: one(w, l))) for l in sys.argv[2].split(",")], 4)
