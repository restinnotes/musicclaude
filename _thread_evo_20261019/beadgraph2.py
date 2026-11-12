"""Bead graph v2 (user 10-21: "你这哪里是新的珠子图 ... 不是 bullet ... 也没有标注 ... 应该还没做吧"). Source = the bead
pipeline's own STRUCT (all 51/55 beads with role, measures and pairwise relations), not the condensed reader D3.
Each bead is cut into short items: verbatim spans of that bead's text, one image or feeling each, tagged with bars and kind.
Bead roles and the pipeline's relations stay at bead level. No rewriting; no cross-segment relations.
ids: bg2_<w>  -> evaluations/beadgraph/bg2_<w>.json, deliverable/bead_graph/Op6x_珠子图.md
usage: python beadgraph2.py build | view"""
import glob, json, re, sys
from collections import Counter
import evo
from beadview import SRC, ORDER, REL

OUT = evo.ROOT / "evaluations" / "beadgraph"
KINDS = ("声音", "身体", "意象", "处境", "心理")
PB = ("下面是一首曲子每一段的珠子（另一位写作者写的当下体验），每颗珠子带 id、角色和原文。请把每颗珠子拆成几条短条目，便于之后做视频时按小节、种类取用。\n\n规则：\n"
      "- 条目的 text 必须从这颗珠子的原文里逐字摘出，一个字都不改、不加。只可以去掉开头的引导语（例如“也可以把……听成”“还有一种……”），"
      "去掉后的部分也必须是原文里连续的一段。\n"
      "- 一条只装一样东西：一个声音事实、一种身体感觉、一个意象、一个人的处境，或一种情绪或心理。原文一句里既有声音又有它像什么，算一个意象条目，不拆开。\n"
      "- 一条必须单独看也懂，一般 10 到 45 个字；意思离不开彼此的几个分句放在同一条里，不要按逗号切成半句。\n"
      "- bars：原文写了小节就照写（如“32”“20–21”），没写就用这颗珠子的小节范围。\n"
      "- kind：" + "、".join(KINDS) + " 之一。\n"
      "- 珠子里每一句实质内容都要落进某条；只有纯过渡、纯引导语、讲演奏者怎么弹的说明可以不要。\n\n"
      "只输出一个 ```json 代码块：{\"S01\": {\"B1\": [{\"text\": \"…\", \"bars\": \"1–3\", \"kind\": \"意象\"}], \"B2\": [...]}, \"S02\": {...}}\n\n")


def struct(w):
    return [json.loads(open(f, encoding="utf-8").read()) for f in sorted(glob.glob(str(SRC[w] / "S*.json")))]


def norm(s):
    return re.sub(r"\s+", "", s)


def check(j, w):
    res = {"items": 0, "not_verbatim": [], "kinds": Counter(), "uncovered": []}; cov = tot = 0
    for s in struct(w):
        for b in s["beads"]:
            src = norm(b["text"]); mask = [False] * len(src)
            for it in (j.get(s["segment"]) or {}).get(b["id"]) or []:
                res["items"] += 1; res["kinds"][it.get("kind")] += 1; t = norm(it.get("text", "")); k = src.find(t)
                if not t or k < 0:
                    res["not_verbatim"].append(f"{s['segment']} {b['id']}: {it.get('text', '')[:30]}"); continue
                for x in range(k, k + len(t)):
                    mask[x] = True
            content = [i for i, ch in enumerate(src) if re.match(r"\w", ch)]
            tot += len(content); cov += sum(mask[i] for i in content)
            gaps = re.findall(r"\w[^\n]{9,}?(?=[，。；：！？]|$)", "".join(ch if not mask[i] else "\n" for i, ch in enumerate(src)))
            res["uncovered"] += [f"{s['segment']} {b['id']}: {g}" for g in gaps if len(re.sub(r"\W", "", g)) >= 10]
    res["coverage"] = round(cov / max(1, tot), 3); res["kinds"] = dict(res["kinds"])
    return res


def view(j, w):
    md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜珠子图", "",
          "珠子来自珠子流程定稿（24 份来源稿 → 汇池 → 精选 → 两轮审稿 → 定稿）。每条都是该珠子原文逐字摘出，标（小节·种类）。",
          "珠子的角色和珠子之间的关系沿用原流程：→ 接着 ／ ＋ 在它上面多了 ／ ∥ 可同时成立 ／ ≠ 另一种理解（不能同时成立）。", ""]
    for s in struct(w):
        md += [f"### {s['segment']} · {s['mm_start']}–{s['mm_end']} · {s['title']}", ""]
        rel = {}
        for r in s.get("relations") or []:
            rel.setdefault(r["b"], []).append(f"{REL.get(r['type'], r['type'])} {r['a']}")
        for role in ORDER:
            for b in [b for b in s["beads"] if b["role"] == role]:
                m = (b.get("measures") or "").split("（")[0]
                md.append(f"**{b['id']}｜{role}（{m}）**" + (f"　{'；'.join(rel[b['id']])}" if b["id"] in rel else ""))
                md += [f"- （{it.get('bars')}·{it.get('kind')}）{it.get('text')}" for it in (j.get(s["segment"]) or {}).get(b["id"]) or []]
                md.append("")
    return "\n".join(md)


def bar_key(b):
    m = re.search(r"\d+", b or ""); return int(m.group()) if m else 9999


def view_by_kind(j, w, compat=()):
    """User 10-21: group by channel (声音 / 意象 / 身体 / 处境 / 心理), mutually exclusive readings in their own block;
    the pipeline's catch-all 另一侧面 and the performance-conditioned 演奏条件 roles are dropped. Each item keeps its bars and
    source bead, and every block runs in bar order, so things heard at the same moment still line up across blocks."""
    md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜珠子图（按种类）", "",
          "每条都是珠子原文逐字摘出，标（小节·来源珠子）。每段按种类分块，块内按小节排序；“另一种理解”是和主听法不能同时成立的听法，单独成块。", ""]
    for s in struct(w):
        alt = {b["id"] for b in s["beads"] if b["role"] == "另一种理解" and f"{s['segment']} {b['id']}" not in compat}
        md += [f"### {s['segment']} · {s['mm_start']}–{s['mm_end']} · {s['title']}", ""]
        its = [(bid, it) for bid, lst in ((j.get(s["segment"]) or {}).items()) for it in lst]
        for k in KINDS:
            sel = sorted([(bid, it) for bid, it in its if it.get("kind") == k and bid not in alt], key=lambda x: bar_key(x[1].get("bars")))
            if sel:
                md += [f"**{k}**"] + [f"- （{it.get('bars')}·{bid}）{it.get('text_display') or it.get('text')}" for bid, it in sel] + [""]
        sel = [(bid, it) for bid, it in its if bid in alt]
        if sel:   # the counterpart comes from the pipeline's own 另一种理解 relation (not from the main bead)
            vs = {}
            for r in s.get("relations") or []:
                if r["type"] == "另一种理解":
                    vs.setdefault(r["b"], []).append(r["a"]); vs.setdefault(r["a"], []).append(r["b"])
            md.append("**另一种理解（与所标的那颗珠子不能同时成立）**")
            for bid in dict.fromkeys(b for b, _ in sel):
                md.append(f"*{bid}　替代 {'、'.join(dict.fromkeys(vs.get(bid, []))) or '（原流程未标明替代哪一颗）'}*")
                md += [f"- （{it.get('bars')}·{bid}）{it.get('text_display') or it.get('text')}" for b, it in sel if b == bid]
            md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    if sys.argv[1] == "kindview":
        out = evo.ROOT / "deliverable" / "bead_graph"
        for w in SRC:
            fx = OUT / f"bg2_{w}_fixed.json"; d = json.loads((fx if fx.exists() else OUT / f"bg2_{w}.json").read_text(encoding="utf-8"))
            j, compat = d["items"], set()   # the alt audit compared against the main bead, which was the wrong counterpart; not used
            p = out / f"{'Op60' if w == 'op60' else 'Op61'}_珠子图_按种类.md"; p.write_text(view_by_kind(j, w, compat), encoding="utf-8"); print(p)
        sys.exit()
    ph = sys.argv[1]
    if ph == "build":
        jobs = []
        for w in SRC:
            body = "\n\n".join(f"## {s['segment']} · {s['mm_start']}–{s['mm_end']}\n" + "\n".join(f"{b['id']}｜{b['role']}｜{(b.get('measures') or '').split('（')[0]}：{b['text']}" for b in s["beads"])
                               for s in struct(w))
            if not evo.done(f"bg2_{w}"):
                jobs.append((f"bg2_{w}", (lambda w=w, body=body: evo.call(f"bg2_{w}", PB + body, prompt_text=PB, model=evo.G6, meta={"stage": "beadgraph2"}))))
        evo.run_parallel(jobs, 2)
    out = evo.ROOT / "deliverable" / "bead_graph"; out.mkdir(parents=True, exist_ok=True)
    for w in SRC:
        if evo.done(f"bg2_{w}"):
            j = evo.parse_json(evo.output(f"bg2_{w}")); c = check(j, w)
            (OUT / f"bg2_{w}.json").write_text(json.dumps({"items": j, "check": c}, ensure_ascii=False, indent=1), encoding="utf-8")
            (out / f"{'Op60' if w == 'op60' else 'Op61'}_珠子图.md").write_text(view(j, w), encoding="utf-8")
            print(w, {k: c[k] for k in ("items", "coverage", "kinds")}, "not_verbatim", len(c["not_verbatim"]), c["not_verbatim"][:4], "uncovered", c["uncovered"][:6], flush=True)
