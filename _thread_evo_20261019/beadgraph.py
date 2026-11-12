"""Bead discretisation (user 10-21: "bead 的图化"). Beads stay the other author's words: each segment is cut into elements
that are verbatim spans of the bead text, tagged — no rewriting, no cross-segment relations (those belong to the Thread;
the bead file itself says alternative readings must not be chained into one story).
  element: {id, text (verbatim span), bars ("32", "20–21", or the segment range), kind: 声音|身体|意象|处境|心理, reading: A|B|C…}
  reading = which listening it belongs to (A = first/main; "另一个听法/也可以听成" opens B, C…); time order inside a reading is kept.
Checks: every text is a verbatim substring of its segment; share of the bead's characters covered; uncovered fragments.
ids: bg_<work>_<RUN> -> evaluations/beadgraph/ (r1: first prompt, chopped at commas; r2: + no half-sentence elements)
usage: python beadgraph.py build | check"""
import json, re, sys
from collections import Counter
import align, evo

OUT = evo.ROOT / "evaluations" / "beadgraph"
W = ("op60", "op61")
RUN = "r2"
KINDS = ("声音", "身体", "意象", "处境", "心理")
PB = ("下面是一首曲子每一段的“珠子”：另一位写作者写的每段当下体验，里面混着声音、身体感觉、意象、人的处境，还有几种不同的听法。"
      "请把每段拆成一个个元素，便于之后做视频时按小节、种类和听法取用。\n\n规则：\n"
      "- 元素的 text 必须从这一段的珠子原文里逐字摘出（一个分句或一句），一个字都不改、不加。只可以去掉开头的引导语"
      "（例如“也可以”“另一种听法是”“再把耳朵收进旋律里：”这类），去掉后的部分也必须是原文里连续的一段。\n"
      "- 一个元素只装一样东西：一个声音事实、一种身体感觉、一个意象、一个人的处境，或一种情绪或心理。"
      "原文一句里既有声音又有它像什么（例如“某个声音像某种画面”），算一个意象元素，不拆开。\n"
      "- 但一个元素必须是完整的一小件：单独拿出来也看得懂。意思离不开彼此的几个分句（例如“舒服归舒服，水仍把人往前送”）放在同一个元素里；"
      "不要按逗号把一句切成几个半句。\n"
      "- bars：原文写了小节就照写（如“32”“20–21”），没写就写这一段的范围。\n"
      "- kind：" + "、".join(KINDS) + " 之一。\n"
      "- reading：同一段里属于同一种听法的元素用同一个字母。原文最先写的、或明说的主听法是 A；原文明说“另一个听法”“也可以听成”“另一种”等，"
      "另起 B、C……；同一种听法里时间上的先后变化仍是同一个字母。\n"
      "- 原文里每一句实质内容都要落进某个元素；只有纯过渡、纯引导语可以不要。\n"
      "- 不要合并不同的听法，也不要把几种听法串成一件事。\n\n"
      "只输出一个 ```json 代码块：{\"segments\": [{\"id\": \"S01\", \"bars\": \"1–3\", \"elements\": "
      "[{\"id\": \"E1\", \"text\": \"…\", \"bars\": \"1–3\", \"kind\": \"意象\", \"reading\": \"A\"}]}]}\n\n========== 珠子 ==========\n")


def bead_segments(w):
    t = evo.rd(align.BEAD_READER[w]); out = {}
    for m in re.finditer(r"^## (S\d+) \| mm\.([\d–-]+) \| ([^\n]*)\n(.*?)(?=^## S|\Z)", t, re.M | re.S):
        out[m.group(1)] = {"bars": m.group(2), "title": m.group(3).strip(), "text": m.group(4).strip()}
    return out


def norm(s):
    return re.sub(r"\s+", "", s)


def check(j, w):
    segs = bead_segments(w); res = {"not_verbatim": [], "uncovered": [], "kinds": Counter(), "readings": {}, "elements": 0}
    covered_total = chars_total = 0
    for s in j["segments"]:
        src = norm(segs.get(s["id"], {}).get("text", "")); mask = [False] * len(src)
        for e in s.get("elements") or []:
            res["elements"] += 1; res["kinds"][e.get("kind")] += 1
            t = norm(e.get("text", "")); k = src.find(t)
            if not t or k < 0:
                res["not_verbatim"].append(f"{s['id']} {e.get('id')}: {e.get('text', '')[:30]}")
                continue
            for x in range(k, k + len(t)):
                mask[x] = True
        res["readings"][s["id"]] = "".join(sorted({e.get("reading", "?") for e in s.get("elements") or []}))
        content = [i for i, ch in enumerate(src) if re.match(r"\w", ch)]
        chars_total += len(content); covered_total += sum(mask[i] for i in content)
        gaps = re.findall(r"\w[^\n]{7,}?(?=[，。；：！？]|$)", "".join(ch if not mask[i] else "\n" for i, ch in enumerate(src)))
        res["uncovered"] += [f"{s['id']}: {g}" for g in gaps if len(re.sub(r"\W", "", g)) >= 8]
    res["coverage"] = round(covered_total / max(1, chars_total), 3); res["kinds"] = dict(res["kinds"])
    return res


def view(j, w):
    segs = bead_segments(w)
    md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜珠子元素", "", "每条都是珠子原文逐字摘出；（小节·种类）；同一段里 A、B、C 是不同的听法。", ""]
    for s in j["segments"]:
        info = segs.get(s["id"], {})
        md += [f"### {s['id']} · {info.get('bars', s.get('bars'))} · {info.get('title', '')}", ""]
        by = {}
        for e in s.get("elements") or []:
            by.setdefault(e.get("reading", "?"), []).append(e)
        for r in sorted(by):
            if len(by) > 1:
                md.append(f"**听法 {r}**")
            md += [f"- （{e.get('bars')}·{e.get('kind')}）{e.get('text')}" for e in by[r]]
            md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    ph = sys.argv[1]
    if ph == "build":
        evo.run_parallel([(f"bg_{w}_{RUN}", (lambda w=w: evo.call(f"bg_{w}_{RUN}", PB + evo.rd(align.BEAD_READER[w]), prompt_text=PB, model=evo.G6, meta={"stage": "beadgraph"})))
                          for w in W if not evo.done(f"bg_{w}_{RUN}")], 2)
    for w in W:
        if evo.done(f"bg_{w}_{RUN}"):
            j = evo.parse_json(evo.output(f"bg_{w}_{RUN}")); j["check"] = check(j, w); OUT.mkdir(parents=True, exist_ok=True)
            (OUT / f"bg_{w}_{RUN}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            (OUT / f"bg_{w}_{RUN}_view.md").write_text(view(j, w), encoding="utf-8")
            c = j["check"]; print(w, {k: c[k] for k in ("elements", "coverage", "kinds", "readings")}, "not_verbatim", len(c["not_verbatim"]), c["not_verbatim"][:5], "uncovered", c["uncovered"][:6], flush=True)
