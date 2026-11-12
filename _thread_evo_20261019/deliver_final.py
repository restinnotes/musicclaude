"""10-28 night (user: the finished version is the Thread graph and the bead graph joined). No model calls (gpt3 at ~3000 this
week, mimicgate paused by the user). Line = P8 (most first places in the blind core reviews of both pieces, bead alignment
level with package 3), shown as a graph: 感受 → 为什么, ← to the earlier segment whose new change it builds on (once per
segment). Join is mechanical from the line's own `explains`: each line item's screen shows the bead items of the beads it
explains; beads no item explains get their own screen; another hearing (STRUCT 另一种理解) goes to a "也可以听成" screen
next to the bead it replaces. Every bead item once, verbatim (beadgraph2). Segment ids written into a step are cleaned.
usage: python deliver_final.py [tag] -> deliver_20261028/成品_线与珠子关系图_Op60_Op61.md"""
import json, sys
import covjudge, draft10, evo, join as J, join11 as K

S = evo.ROOT / "evaluations" / "seq8"


def short(t, n=50):
    """an earlier segment's new change, cut at the first clause end that fits (not mid-word)"""
    for i, ch in enumerate(t):
        if ch in "；。" and i >= 12:
            return t[:i] if i <= n else t[:n] + "……"
    return t if len(t) <= n else t[:n] + "……"


def build(T, w):
    rows = json.loads((S / f"P{T}_{w}.json").read_text(encoding="utf-8"))
    center = (S / f"P{T}_{w}.txt").read_text(encoding="utf-8").split("\n")[1].replace("Center：", "", 1)
    cf = S / f"center{T}_{w}.json"            # center_fix.py: rewritten in THREAD_SPEC's format (minimal relation sentence)
    old_center, center = (center, json.loads(cf.read_text(encoding="utf-8"))["final"]) if cf.exists() else ("", center)
    news = {sec: (r["edit"].get("new") or [""])[0] for sec, r in rows.items()}
    gf = S / f"P{T}g_{w}.json"
    steps = {(s["sec"], it["i"]): it.get("steps") or [] for s in json.loads(gf.read_text(encoding="utf-8"))["graph"]["segments"]
             for it in s.get("items") or []} if gf.exists() else {}
    md = [f"## 肖邦{covjudge.NAME[w]}", "", f"**Center**：{center}", ""] + (
        [f"<small>（按规范的格式重写；原先这条线用的是：{old_center}）</small>", ""] if old_center else [])
    stat = {"items": 0, "screens": 0, "bead_items": 0, "unexplained_beads": 0}
    for s in draft10.segs(w):
        sec = s["id"]; its = rows[sec]["edit"].get("items") or []
        bi = J.bead_items(w, sec); by_bead = {}
        for x in bi:
            by_bead.setdefault(x["bead"], []).append(x)
        alt = {x["bead"]: x["alt_of"] for x in bi if x["role"] == "另一种理解" or x["alt_of"]}
        shown, seen_from, screens = set(), set(), []

        def beads_for(bids):
            out = []
            for b in bids:
                if b in by_bead and b not in shown and b not in alt:
                    shown.add(b); out.append(b)
            return out

        for it in its:
            ex = [e.split("-")[-1] for e in it.get("explains") or []]
            fr = [f for f in it.get("from") or [] if f in news and f != sec and f not in seen_from]; seen_from |= set(fr)
            screens.append({"line": it, "from": fr, "beads": beads_for(ex)})
        rest = beads_for([b for b in by_bead if b not in shown])
        if rest:
            screens.append({"line": None, "from": [], "beads": rest})
        out = [f"### {sec} ｜ {s['start']}–{s['end']} 小节", ""]
        for k, sc in enumerate(screens, 1):
            out.append(f"**屏 {k}**" + ("　线没有单独说明的听感" if sc["line"] is None else ""))
            out.append("")
            if sc["line"]:
                x = sc["line"]
                st = steps.get((sec, its.index(x) + 1))
                if st:   # graph steps (graph_split.py): first step carries the ←, the rest follow
                    out += [f"> **线**　{K.clean(st[0]['text'])}"] + [f"> {'→ ' if s2.get('follows') else '• '}{K.clean(s2['text'])}" for s2 in st[1:]]
                else:
                    out += [f"> **线**　{K.clean(x.get('feel', ''))}", f"> → {K.clean(x.get('why', ''))}"]
                out += [f">　<small>← 接在（{f}）{short(news[f])}</small>" for f in sc["from"]]
                out.append("")
                stat["items"] += 1
            for b in sc["beads"]:
                out += [f"- {x['text']}　<small>{x['bars']}</small>" for x in by_bead[b]]; stat["bead_items"] += len(by_bead[b])
                for a, of in alt.items():                         # another hearing right after the bead it replaces
                    if of == b and a not in shown:
                        shown.add(a); out += ["", "*也可以听成*", ""] + [f"- {x['text']}　<small>{x['bars']}</small>" for x in by_bead[a]]
                        stat["bead_items"] += len(by_bead[a])
            out.append("")
            stat["unexplained_beads"] += len(sc["beads"]) if sc["line"] is None else 0
        left = [a for a in alt if a not in shown]                 # alternatives whose bead was never shown
        if left:
            out += ["*也可以听成*", ""] + [f"- {x['text']}　<small>{x['bars']}</small>" for a in left for x in by_bead[a]] + [""]
            stat["bead_items"] += sum(len(by_bead[a]) for a in left)
        stat["screens"] += len(screens)
        total = sum(len(v) for v in by_bead.values())
        assert stat["bead_items"] <= sum(len(J.bead_items(w, x["id"])) for x in draft10.segs(w)), "bead item shown twice"
        md += out
    stat["bead_items_total"] = sum(len(J.bead_items(w, x["id"])) for x in draft10.segs(w))
    return md, stat


def main(T="8"):
    head = [f"# 成品（半成品）：线与珠子关系图结合（10-28 夜）", "",
            "每段若干屏：**线**说他此刻为什么会这样（感受 → 为什么；← 指回前面某段确立的变化），同一屏下面是线所说明的**珠子**条目（逐字原文，右边是小节）。"
            "“线没有单独说明的听感”是线没有对应到的珠子；“也可以听成”是和某颗珠子不能同时成立的另一种听法。每个珠子条目只出现一次。", "",
            f"- 线：P{T}（独立稿 + 逐段顺序综合，每段看这一段的珠子写，后一段接在前一段新确立的变化上）。匿名盲评里两首都不比包3 差，珠子对应持平；整首对照包3 仍判退步（见计划记录）。",
            "- 珠子：包3 的珠子图（逐字摘出，按小节和种类），一颗没改。",
            "- 线已经拆成关系图短步（每步不超过 45 字：Op.60 220 步、平均 22 字；Op.61 154 步、平均 28 字），内容不改；核对：Op.60 没有丢、加、拆碎，"
            "Op.61 还有几处语气小损（少一个“会”、“可以成为”写成“变成”）和 4 处拆得略断。",
            "- 线和珠子的对应用的是线自己标的“解释了哪几颗珠子”，没有再请模型排屏。", "{EVAL}", ""]
    sf = S / f"final_eval{T}_summary.md"                 # written by hand from final_eval.py's printout
    head = [x.replace("{EVAL}", sf.read_text(encoding="utf-8").strip() if sf.exists() else "- 终评：还在跑。") for x in head]
    body, stats = [], {}
    for w in ("op60", "op61"):
        md, st = build(T, w); body += md; stats[w] = st
        print(w, st, flush=True)
        assert st["bead_items"] == st["bead_items_total"], (w, st)
    out = evo.ROOT / "deliver_20261028" / "成品_线与珠子关系图_Op60_Op61.md"
    out.write_text("\n".join(head + body), encoding="utf-8")
    print(out, flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:2])
