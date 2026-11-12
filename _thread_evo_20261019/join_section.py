"""10-29 (user: "为什么这么多分屏"): alternative layout of the joined product — one screen per segment. The whole line of the
segment on top (numbered steps), then the bead items in bead order, each bead marked with the steps that explain it; beads both
coverage judges call 没有/相反 are marked as not explained by the line; another hearing marked 也可以听成. No model calls.
usage: python join_section.py <tag> -> evaluations/v6fix/成品_按段一屏_<tag>.md"""
import sys
import covjudge, join as J, v6fix as V

NUM = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫"


def main(T):
    md = [f"# 成品（按段一屏）：线与珠子关系图结合", "",
          "每段一屏：上面是这一段的**线**（①②③… 是条目编号；→ 段内由上一条引出；← 指回前面某段；⟲ 前面仍在起作用），"
          "下面是这一段的**珠子**（逐字原文，右边是小节），每颗珠子标出是线的哪几条在说明它。", ""]
    for w in ("op60", "op61"):
        g = V.graph_of(w, T); I = V.index(g)
        notexp = set()
        for jj in V.JUDGES:
            for x in (V.parse(f"cov_{w}_{jj}_{T}") or {}).get("beads") or []:
                if x.get("status") in ("没有", "相反"):
                    notexp.add((x.get("sec"), str(x.get("bead")), jj))
        notexp = {(s_, b_) for s_, b_, _ in notexp if all((s_, b_, jj) in notexp for jj in V.JUDGES)}
        md += [f"## 肖邦{covjudge.NAME[w]}", "", f"**Center：**{g['center']}", ""]
        for s in g["segments"]:
            sec = s["sec"]; md += [f"### {sec} ｜ {s['bars']} 小节　（{s.get('relation')}）", ""]
            claim = {}
            for n, it in enumerate(s["items"]):
                links = [f"← {e['rel']}：（{I[e['from']][0]['bars']}）「{I[e['from']][1].get('key') or I[e['from']][1]['text'][:10]}」"
                         for e in s["because"] if e.get("to") == it["id"] and e.get("rel") != "仍在起作用" and e.get("from") in I]
                md.append(f"> {NUM[n] if n < len(NUM) else n + 1} {'→ ' if it.get('follows') and n else ''}{it['text']}")
                md += [f">　<small>{l}</small>" for l in links]
                for b in it.get("explains") or []:
                    claim.setdefault(b, []).append(NUM[n] if n < len(NUM) else str(n + 1))
            still = [f"（{I[e['from']][0]['bars']}）「{I[e['from']][1].get('key')}」" for e in s["because"] if e.get("rel") == "仍在起作用" and e.get("from") in I]
            if still:
                md.append(f">　<small>⟲ 仍在起作用：{'；'.join(dict.fromkeys(still))}</small>")
            md.append("")
            by = {}
            for x in J.bead_items(w, sec):
                if x["role"] != "演奏条件":
                    by.setdefault(x["bead"], []).append(x)
            for b, xs in by.items():
                r = xs[0]["role"]; alt = r == "另一种理解" or xs[0]["alt_of"]
                if alt:
                    tag = "也可以听成"
                elif (sec, b) in notexp or not claim.get(b):
                    tag = f"{r}｜线没有单独说明"
                else:
                    tag = f"{r}｜线 {''.join(dict.fromkeys(claim[b]))} 在说明"
                md.append(f"**{b}**　<small>{tag}</small>")
                md += [f"- {x['text']}　<small>{x['bars']}</small>" for x in xs] + [""]
    fn = V.OUT / f"成品_按段一屏_{T}.md"
    fn.write_text("\n".join(md), encoding="utf-8"); print("->", fn)


if __name__ == "__main__":
    main(sys.argv[1])
