"""10-28 user: "线的半成品目前最好的也给我一版本，和珠子合到一起，一个文件". No model calls; assembled from finished outputs.
Line = T0 P4d (Center and labels, drafted without beads) + bead-aware local repair per segment:
- the E2b edit where it passed (checker found nothing out of bounds, both judges 不差于 package 3);
- otherwise the P7 edit (same prompt, whole piece); items the P7 checker flagged are kept and marked 待改.
Beads = package 3 machine-readable beads, verbatim.  usage: python deliver_halfdone.py -> deliver_20261028/"""
import json, re
import covjudge, draft10, evo, precise as P

OUT = evo.ROOT / "deliver_20261028" / "半成品_线加珠子_Op60_Op61.md"
# The edits cite their basis (H = earlier history, M = pool candidate, 原解释 = T0's item) inside the text too. A reader has
# none of these, so ids are dropped or turned into "前面…", and sentences about the edit itself are dropped. No other change.
G = r"[HM]\d+(?:\s*[、和与及]\s*[HM]\d+)*"
REF = r"(?:" + G + r"|原解释第?\d+(?:[–-]\d+)?条?|原来的第\d+条)"
SUBS = [(r"[（(]\s*" + REF + r"(?:\s*[；;，,、]\s*" + REF + r")*\s*[）)]", ""),
        (r"原第\d+条所说的", ""), (r"按M\d+，", ""), (r"借M\d+来说，", ""),
        (r"M\d+(?:、M\d+)*所说的变化", "这里的变化"), (r"M\d+(?:、M\d+)*所说的", ""),
        (r"M\d+(?:准确抓住了这种同时性|提供的依据是)：", ""), (r"M\d+指出，", ""),
        (r"在" + G + r"所确立的", "在前面确立的"), (G + r"所确立的", "前面确立的"),
        (G + r"(?:已经确立|确立过|又确立|则确立)，", "前面已经说过，"),
        (G + r"(又|则|也)(?:说明|表明)，?", "前面也说过，"), (G + r"(?:说明|表明)，?", "前面说过，"),
        (G + r"里，", "在前面，"), (G + r"里", "前面"),
        (G + r"(又)?(让|使|把|留下)", r"前面的经历\1\2"), (G + r"的", "前面的")]
META = ("原解释", "这条解释", "前一条")


def clean(t):
    for a, b in SUBS:
        t = re.sub(a, b, t)
    t = "".join(s for s in re.split(r"(?<=。)", t) if not any(m in s for m in META))
    lead = r"(?:在前面|前面已经说过|前面也说过|前面说过)，"      # "前面说过，…；前面说过，…" -> "前面说过，…；还有，…"
    first = re.search(lead, t)
    return t if not first else t[:first.end()] + re.sub(lead, "还有，", t[first.end():])


def note(t):
    """Checker notes and gaps talk about the basis itself; leftover ids become plain words."""
    return re.sub(r"\s*" + G + r"(?:\s*及\s*[HM]\d+)*\s*",
                  lambda m: "前面的历史" if "H" in m.group(0) else "独立稿里的一种说法", clean(t))


def parse(rid):
    try:
        return evo.parse_json(evo.output(rid))
    except Exception:
        return None


def e2b_passed(w, sec):
    k, js = parse(f"pcE2b_{w}_{sec}"), [parse(f"pjE2b_{w}_{sec}_{j}") for j in ("g6", "g56")]
    return bool(k and all(x.get("label") == "ok" for x in k.get("items") or [])
                and all(j and "不差于" in (j.get("verdict") or "") for j in js))


def pick(w, sec):
    """-> (edit, check or None, source label, flags {item no: checker note}) for the segment's current best repair."""
    if e2b_passed(w, sec):
        return parse(f"peE2b_{w}_{sec}"), None, "修准实验版（已核对、已对照包 3）", {}
    e, k = parse(f"pe7_{w}_{sec}"), parse(f"pc7_{w}_{sec}")
    flags = {int(x["i"]): x.get("why", "") for x in (k or {}).get("items") or [] if x.get("label") != "ok"}
    return e, k, "整首修准版" + ("" if k else "（还没核对）"), flags


def main():
    out = ["# 半成品：线 + 珠子（10-28）", "",
           "- **珠子**：包 3 的珠子原样照录，一颗没改。",
           "- **线**：先由不看珠子的独立稿写成主线（Center 和每段标题都来自这一步），再看着珠子逐段做局部修准，"
           "让每段说清“此刻为什么会这样感受”。修准不许编前史和外部事件，也不许把音乐本身当原因。",
           "- 每段线的来源写在段标题下。“修准实验版”是核对没越界、两位评委都判不差于包 3 的版本；"
           "“整首修准版”还没退改，核对者认为越界的条目标了“待改”，有几段还没核对。",
           "- 线的每条后面括号里写它解释的是哪颗珠子。", ""]
    stat = []
    for w in ("op60", "op61"):
        fin, _ = P.t0(w); bs = covjudge.beads(w)
        segs = draft10.segs(w); n_e2b = n_flag = n_unchk = 0
        body = [f"## 肖邦{covjudge.NAME[w]}（{len(segs)} 段，{len(bs)} 颗珠子）", "", f"**这首的主线**：{fin.get('center', '')}", ""]
        for s in segs:
            sec = s["id"]
            lab = next((x.get("label", "") for x in fin["sections"] if x["sec"] == sec), "")
            e, k, src, flags = pick(w, sec)
            n_e2b += src.startswith("修准实验版"); n_unchk += src.endswith("（还没核对）"); n_flag += len(flags)
            body += [f"### {sec} ｜ {s['start']}–{s['end']} 小节 ｜ {lab}", "", f"*线的来源：{src}*", "", "**线**", ""]
            for i, x in enumerate(e.get("items") or [], 1):
                ex = "、".join(b.split("-")[-1] for b in x.get("explains") or [])
                body += [f"{i}. **感受**：{clean(x.get('feel', ''))}", f"   **为什么**：{clean(x.get('why', ''))}" + (f"（对应 {ex}）" if ex else "")]
                if i in flags:
                    body.append(f"   > 待改：{note(flags[i])}")
            gaps = e.get("gaps") or []
            if gaps:
                body += ["", "**这段还没解释到的珠子**", ""]
                body += [f"- {g.get('bead', '').split('-')[-1]}：{note(g.get('why', ''))}" for g in gaps]
            body += ["", "**珠子**", ""]
            body += [f"- **{b['id'].split('-')[-1]}**［{b['role']}］（{b['measures']} 小节）{b['text']}" for b in bs if b["sec"] == sec]
            body.append("")
        stat.append(f"| {covjudge.NAME[w]} | {len(segs)} | {n_e2b} | {len(segs) - n_e2b} | {n_flag} | {n_unchk} |")
        out += body
    table = ["| 曲子 | 段数 | 修准实验版 | 整首修准版 | 待改条目 | 没核对的段 |", "|---|---|---|---|---|---|"] + stat + [""]
    i = out.index("- 线的每条后面括号里写它解释的是哪颗珠子。") + 2
    OUT.write_text("\n".join(out[:i] + table + out[i:]), encoding="utf-8")
    print(OUT, "\n".join(stat), sep="\n")


if __name__ == "__main__":
    main()
