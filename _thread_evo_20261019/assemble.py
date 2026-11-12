"""Node 4: assemble per segment = verbatim bead excerpts (whole sentences containing the alignment's bead quotes for
this segment's own beads) + the Thread's own text for the segment. Nothing is rewritten; a script check verifies that
every bead line is a verbatim substring of the bead and the Thread part equals segcheck's segment text.
usage: python assemble.py <work> <thread_run_id,...>  -> evaluations/assembled/<id>.md and .json
"""
import json, re, sys
import align, arts, evo, segcheck

OUT = evo.ROOT / "evaluations" / "assembled"
SENT = re.compile(r"[^。！？!?]*[。！？!?」”]*")


def sentences(t):
    return [s.strip() for s in SENT.findall(t) if s.strip()]


def run(work, name):
    _, beads = align.beads_text(work)
    thread = segcheck.to_json(arts.clean(evo.output(name)), work)
    assert thread, f"{name}: Thread headings do not match segmentation"
    aj = json.loads((evo.ROOT / "evaluations" / "align" / f"{name}.json").read_text(encoding="utf-8"))
    links = {s["segment"]: s.get("links", []) for s in aj["segments"]}
    out, md = [], [f"# 组装稿：{name}", "", "每段先列珠子原句（逐字节选），再接线的原文。", ""]
    for seg in thread["segments"]:
        sid = seg["id"]; picks = []
        for l in links.get(sid, []):
            b = l.get("bead", "")
            if not b.startswith(sid + "/") or b not in beads or l.get("type") == "冲突":
                continue       # only this segment's own beads, never conflicting ones
            q = align.norm(l.get("bead_quote"))
            for s in sentences(beads[b]):
                if q and q in align.norm(s) and s not in picks:
                    picks.append(s)
        for p in picks:
            assert any(p in t for t in beads.values()), p
        out.append({"id": sid, "start": seg["start"], "end": seg["end"], "bead_excerpts": picks, "thread": seg["text"]})
        md.append(f"### 第{seg['start']}–{seg['end']}小节")
        md += [f"> 【珠子】{p}" for p in picks] + ["", seg["text"], ""]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps({"thread": name, "segments": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / f"{name}.md").write_text("\n".join(md), encoding="utf-8")
    nb = sum(len(s["bead_excerpts"]) for s in out)
    print(name, "segments", len(out), "bead excerpts", nb, "chars", sum(len(s["thread"]) for s in out) + sum(len(p) for s in out for p in s["bead_excerpts"]))


if __name__ == "__main__":
    for n in sys.argv[2].split(","):
        run(sys.argv[1], n)
