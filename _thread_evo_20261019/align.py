"""Stage 2a: annotate how a full Thread connects to the beads (no rewriting). GPT-6 via gpt3; script verifies quotes.
usage: python align.py <work> <name,...>      (names: run ids or B0)
Outputs runs/a_<name>/ and evaluations/align/<name>.{json,md}
"""
import json, re, sys
import arts, evo, seg, segcheck

PKG_STRUCT = evo.PKG / "03_Bead机器可读" / "14段_STRUCT轻量版.json"
BEAD_STRUCT = {"op60": PKG_STRUCT,
               "op61": __import__("pathlib").Path("D:/musicclaude/_bead_op61_20261020/deliverable/03_Bead机器可读/13段_STRUCT轻量版.json")}
BEAD_READER = {"op60": evo.PKG / "02_Bead精简输入" / "D3_十四段reader.md",
               "op61": __import__("pathlib").Path("D:/musicclaude/_bead_op61_20261020/deliverable/02_Bead精简输入/D3_十三段reader.md")}
OUT = evo.ROOT / "evaluations" / "align"


def beads_text(work="op60"):
    st = json.loads(BEAD_STRUCT[work].read_text(encoding="utf-8"))["segments"]
    lines = []
    for s in st:
        lines.append(f"## {s['segment']} | mm.{s['mm_start']}–{s['mm_end']} | {s['title']}")
        for b in s["beads"]:
            lines.append(f"- {s['segment']}/{b['id']}［{b.get('role')}｜{b.get('measures')}］{b['text']}")
    return "\n".join(lines), {f"{s['segment']}/{b['id']}": b["text"] for s in st for b in s["beads"]}


def norm(s):
    return re.sub(r"[\s\*`“”\"'‘’「」『』《》，。、；：！？,.;:!?（）()\-—–…·]", "", s or "")


def verify(j, thread, beads):
    errs, nlinks = [], 0
    th = norm(thread)
    for s in j.get("segments", []):
        for l in s.get("links", []):
            nlinks += 1
            if norm(l.get("thread_quote")) not in th:
                errs.append(f"{s['segment']} thread quote not found: {l.get('thread_quote')}")
            b = l.get("bead", "")
            if b not in beads:
                errs.append(f"{s['segment']} unknown bead {b}")
            elif norm(l.get("bead_quote")) not in norm(beads[b]):
                errs.append(f"{s['segment']} bead quote not in {b}: {l.get('bead_quote')}")
    return errs, nlinks


def report(name, j, errs, nlinks, beads):
    segs = j.get("segments", [])
    types = {}
    for s in segs:
        for l in s.get("links", []):
            types[l.get("type")] = types.get(l.get("type"), 0) + 1
    main = [k for k in beads if k.endswith("/B1")]
    linked = {l.get("bead") for s in segs for l in s.get("links", [])}
    lines = [f"# 对接表：{name}", "", j.get("summary", ""), "",
             f"- 关系数：{nlinks}（" + "，".join(f"{k} {v}" for k, v in types.items()) + "）",
             f"- 主体验珠子（B1）被接住：{sum(m in linked for m in main)}/{len(main)}",
             f"- 主要在复述珠子的段：{sum(bool(s.get('retell')) for s in segs)}/{len(segs)}",
             f"- 引文核对失败：{len(errs)}", ""]
    for s in segs:
        lines.append(f"## {s['segment']}" + ("（复述）" if s.get("retell") else ""))
        for l in s.get("links", []):
            lines.append(f"- **{l.get('type')}** {l.get('bead')}：「{l.get('thread_quote')}」 ← 「{l.get('bead_quote')}」 — {l.get('note')}")
        if s.get("thread_only"):
            lines.append("- 线自己的话：" + " / ".join(f"「{t}」" for t in s["thread_only"]))
        if s.get("beads_unlinked"):
            lines.append("- 未接住：" + "、".join(s["beads_unlinked"]))
        lines.append("")
    if errs:
        lines += ["## 引文核对失败", *[f"- {e}" for e in errs]]
    return "\n".join(lines)


if __name__ == "__main__":
    work, names = sys.argv[1], sys.argv[2].split(",")
    OUT.mkdir(parents=True, exist_ok=True)
    btxt, beads = beads_text(work)
    d = seg.load(work)
    tpl = evo.rd(evo.ROOT / "prompts" / "align_v1.md")
    jobs = {}
    for n in names:
        thread = arts.b0() if n == "B0" else arts.clean(evo.output(n))
        msg = tpl.replace("{WORK}", d["work"]).replace("{NSEG}", str(len(d["segments"]))).replace("{THREAD}", thread).replace("{BEADS}", btxt)
        jobs[n] = (thread, msg)
    evo.run_parallel([(f"a_{n}", (lambda n=n: evo.call(f"a_{n}", jobs[n][1], prompt_text=tpl, meta={"stage": "align"}))) for n in names], 6)
    for n in names:
        r = evo.output(f"a_{n}")
        if not r:
            print(n, "no output"); continue
        j = evo.parse_json(r)
        errs, nl = verify(j, jobs[n][0], beads)
        (OUT / f"{n}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
        (OUT / f"{n}.md").write_text(report(n, j, errs, nl, beads), encoding="utf-8")
        print(n, "links", nl, "quote errors", len(errs))
