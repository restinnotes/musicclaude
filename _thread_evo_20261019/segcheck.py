"""Thread output -> machine-readable segments, validated against the upstream segmentation.

The model writes free-form headings ("### 第1—3小节｜…", "**（1—23小节）**", "**4—16小节**"); this parser normalizes them,
checks they are exactly the upstream segments in order, and exports {work, boundaries, segments:[{id,start,end,text}]}.
usage: python segcheck.py <run-glob> [...]        report compliance
       python segcheck.py --export <run_id> <out.json>
"""
import glob, json, re, sys
import arts, evo, seg

HEAD = re.compile(r"^(?:(?:#{1,4}\s*|\*\*)\s*[（(]?\s*(?:第\s*|小节\s*|mm?\.?\s*)?(\d+)\s*[—–\-~至到]+\s*(?:第\s*)?(\d+)\s*(?:小节)?(?=[\s）)｜|:：*·—]|$)"
                  r"|[ 	]*(?:第\s*)?(\d+)\s*[—–\-~至到]+\s*(\d+)\s*(?:小节)?[ 	]*$)", re.M)   # 10-31: also a bare "1—3" line


def check(text, work):
    want = [(s["start"], s["end"]) for s in seg.load(work)["segments"]]
    got = [(int(a or c), int(b or d)) for a, b, c, d in HEAD.findall(text)]
    return got == want, got


def to_json(text, work):
    d = seg.load(work)
    ok, got = check(text, work)
    want = [(x["start"], x["end"]) for x in d["segments"]]
    if not ok and got[:len(want)] != want:
        return None
    ms = list(HEAD.finditer(text))   # if the segments appear twice (e.g. bullets, then an essay), keep the first pass only
    out = []
    for i, (m, s) in enumerate(zip(ms, d["segments"])):
        line_end = text.find("\n", m.start())   # the heading's own line (HEAD's \s* may run past its newline)
        start = len(text) if line_end < 0 else line_end + 1
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        rest = text[m.end():line_end].strip().lstrip("小节）)｜|:：·—- ").rstrip("*").strip() if 0 <= m.end() <= line_end else ""   # e.g. "**1–3｜<headline>**"
        body = ((f"**{rest}**\n" if rest else "") + text[start:end]).strip()
        if i == len(d["segments"]) - 1:   # drop trailing section titles / rules before a second pass
            body = re.split(r"\n(?:#{1,3}\s|---)", body)[0].strip()
        out.append({"id": s["id"], "start": s["start"], "end": s["end"], "text": body})
    return {"work": d["work"], "boundaries": d["boundaries"], "segments": out}


def work_of(name):
    return "op61" if "op61" in name else "op60"


if __name__ == "__main__":
    if sys.argv[1] == "--export":
        name, outp = sys.argv[2], sys.argv[3]
        j = to_json(arts.clean(evo.output(name)), work_of(name))
        assert j, f"{name}: headings do not match the upstream segmentation"
        open(outp, "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=1))
        sys.exit(0)
    for pat in sys.argv[1:]:
        ok = n = 0; bad = []
        for d in sorted(glob.glob(str(evo.RUNS / pat))):
            name = d.replace("\\", "/").split("/")[-1]
            t = evo.output(name)
            if not t:
                continue
            good, got = check(arts.clean(t), work_of(name))
            n += 1; ok += good
            if not good:
                bad.append((name, len(got), got[:2]))
        print(f"{pat}: {ok}/{n} articles carry exactly the upstream segments")
        for b in bad[:5]:
            print("   ", b)
