"""10-30 night (user: "你这珠子和线合并不能动珠子和线本身的内容的啊"). The joined article is arrangement only: the line's items
verbatim as running text, each bead verbatim (whole text) as a quote placed right after the line item closest to it in meaning,
as named by the two coverage judges ("第N条", the item cited by most judges, ties -> earlier item); beads no judge tied to an
item go at the end of the segment. Another hearing is introduced with "也可以听成". Performance-condition beads are left out,
as in every joined product. No model calls; run after v6cov.py <tag>.
usage: python v6weave.py <tag>  -> evaluations/v6fix/合写_<w>_<tag>.md"""
import json, re, sys
from collections import Counter
import covjudge, evo, v6fix as V

CIRC = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"


CIRC_ALL = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮"


def item_nums(s, sec, texts=None):
    """10-30: judges cite items as "第2条" (same segment), "S01②" / "S01-2" (segment + item), or only by quoting fragments of
    the item text (mimicgate Op.60 f4) -> match each fragment to the item of <sec> that contains it; keep only items of <sec>."""
    s = str(s or ""); out = [int(n) for n in re.findall(r"第\s*(\d+)\s*条", s)]
    if not re.search(r"S\d\d", s):      # 11-02 (JV=2 judges): "①忽然发觉…；③怕对方…" means items of this segment
        out += [CIRC_ALL.index(c) + 1 for c in re.findall(r"[①-⑮]", s)]
    for sc, c in re.findall(r"(S\d\d)\s*([①-⑮])", s):
        if sc == sec:
            out.append(CIRC_ALL.index(c) + 1)
    for sc, n in re.findall(r"(S\d\d)-(\d+)", s):
        if sc == sec:
            out.append(int(n))
    if not out and texts:
        norm = lambda t: re.sub(r"[\s，。、；：“”「」]", "", t)
        frags = [f for f in re.split(r"[；;]|」|「", s) if len(norm(f)) >= 3]
        for f in frags:
            f = norm(f)
            hit = [k for k, t in enumerate(texts, 1) if f in norm(t)]
            if not hit:     # loose: most shared characters, at least 60% of the fragment
                sc = [(len(set(f) & set(norm(t))) / len(set(f)), k) for k, t in enumerate(texts, 1)]
                best = max(sc)
                hit = [best[1]] if best[0] >= 0.6 else []
            out += hit[:1]
    return out



def bars_only(m):
    """10-31: show only the bar numbers; the bead pipeline's placement notes ("原稿所述…", "跨段宽述…") are working notes"""
    import re
    m = re.sub(r"（[^（）]*）", "", re.sub(r"（[^（）]*）", "", str(m)))      # nested notes, two levels
    return re.sub(r"\s+", "", m).strip("；;，, ") or str(m)


def main(T):
    for w in ("op60", "op61"):
        g = V.graph_of(w, T); I = V.index(g)
        votes = {}; texts = {s["sec"]: [i["text"] for i in s["items"]] for s in g["segments"]}
        for j in V.JUDGES:
            # 10-31: a judge that never came back (gpt-6 incomplete_response) may be taken from the previous version
            # (WEAVE_FALLBACK=<tag>; only sensible when the two lines differ in a few items)
            fb = __import__("os").environ.get("WEAVE_FALLBACK")
            for x in (V.parse(f"cov2_{w}_{j}_{T}") or V.parse(f"cov_{w}_{j}_{T}") or (V.parse(f"cov_{w}_{j}_{fb}") if fb else None) or {}).get("beads") or []:
                if x.get("status") in ("说清", "偏弱"):
                    for n in item_nums(x.get("items"), x["sec"], texts.get(x["sec"])):
                        votes.setdefault((x["sec"], str(x["bead"]).split("-")[-1]), Counter())[n] += 1
        beads = [b for b in covjudge.beads(w) if b["role"] != "演奏条件"]
        cf = evo.ROOT / "evaluations" / "beads_clean" / f"{w}.json"     # DAG N03h: editorial sentences removed (bead_clean.py)
        if cf.exists():
            clean = json.loads(cf.read_text(encoding="utf-8")); beads = [dict(b, text=clean.get(b["id"], b["text"])) for b in beads]
        lf = evo.ROOT / "evaluations" / "beads_lang" / f"{w}.json"      # DAG N03i: language pass, content-checked (bead_lang.py)
        if lf.exists():
            lang = json.loads(lf.read_text(encoding="utf-8")); beads = [dict(b, text=lang.get(b["id"], b["text"])) for b in beads]
        md = [f"# {covjudge.NAME[w]}：线与珠子合写", "",
              "正文是线（逐字，未改动），引用框里是听感记录（珠子，逐字，未改动）。每颗珠子放在和它意思最接近的那条线后面（由两位覆盖评委判定）；"
              "线里〔〕是这句话提到的前文：小节和第几条。", "", f"**Center：**{g['center']}", ""]
        for s in g["segments"]:
            md += [f"### {s['bars']} 小节　（{s.get('relation')}）", ""]
            sb = [b for b in beads if b["sec"] == s["sec"]]
            place = {}
            for b in sb:
                c = votes.get((s["sec"], b["id"].split("-")[-1]))
                n = min(c, key=lambda k: (-c[k], k)) if c else None
                place.setdefault(n if n and n <= len(s["items"]) else None, []).append(b)

            def quote(b):
                lead = "也可以听成：" if b["role"] == "另一种理解" else ""
                return [f"> {lead}{b['text']}", f"> <small>（{bars_only(b['measures'])}）</small>", ""]
            for k, it in enumerate(s["items"], 1):
                cites = [f"〔{I[e['from']][0]['bars']} {CIRC[int(e['from'].split('-')[-1]) - 1]}〕"
                         for e in s["because"] if e.get("to") == it["id"] and e.get("rel") == "引用" and e.get("from") in I]
                md += [f"{it['text']}{' ' + ''.join(cites) if cites else ''}", ""]
                for b in place.get(k, []):
                    md += quote(b)
            for b in place.get(None, []):
                md += quote(b)
        (V.OUT / f"合写_{w}_{T}.md").write_text("\n".join(md), encoding="utf-8")
        print(w, T, "珠子", len(beads), "放在段末（没有评委对应到条）", sum(1 for b in beads if not votes.get((b["sec"], b["id"].split("-")[-1]))), flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
