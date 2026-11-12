"""Render the per-segment marginal-gain curves as one static HTML page (small multiples, inline SVG)."""
import html, json
import sat

D = sat.ROOT / "deliverable"
cv = json.loads((D / "A_实验数据" / "curves.json").read_text(encoding="utf-8"))
cv2 = json.loads((D / "A_实验数据" / "curves_run2.json").read_text(encoding="utf-8"))
W, H, PL, PR, PT, PB = 320, 170, 34, 12, 14, 26
WORTH = {"值得": "●", "勉强": "◐", "不值得": "○"}


def chart(c):
    rows = c["rows"]; n = len(rows)
    x = lambda k: PL + (k - 1) * (W - PL - PR) / max(1, n - 1)
    y = lambda v: PT + (1 - v) * (H - PT - PB)
    g = []
    for v in (0, .5, 1):
        g.append(f'<line x1="{PL}" x2="{W-PR}" y1="{y(v):.1f}" y2="{y(v):.1f}" class="grid"/>'
                 f'<text x="{PL-6}" y="{y(v)+4:.1f}" class="tick" text-anchor="end">{int(v*100)}%</text>')
    for r in rows:
        g.append(f'<text x="{x(r["k"]):.1f}" y="{H-8}" class="tick" text-anchor="middle">{r["k"]}</text>')
    marks = [("gen_stop", "生成停", "m-gen"), ("rev_keep", "审稿留", "m-rev"), ("final_beads", "定稿", "m-fin")]
    for i, (key, lab, cls) in enumerate(marks):
        k = c.get(key)
        if k and 1 <= k <= n:
            g.append(f'<line x1="{x(k)+(i-1)*2:.1f}" x2="{x(k)+(i-1)*2:.1f}" y1="{PT}" y2="{H-PB}" class="{cls}"/>')
    for key, cls in (("cum_cov", "s1"), ("cum_core", "s2")):
        pts = " ".join(f"{x(r['k']):.1f},{y(r[key]):.1f}" for r in rows)
        g.append(f'<polyline points="{pts}" class="line {cls}"/>')
        for r in rows:
            tip = (f"k={r['k']} 加权涵盖 {r['cum_cov']:.0%} 核心 {r['cum_core']:.0%}｜生成者:{r['gen_gain']}｜审稿:{r['rev_case']}，{r['worth']}｜"
                   f"累计{r['cum_chars']}字\n{r['text']}")
            g.append(f'<circle cx="{x(r["k"]):.1f}" cy="{y(r[key]):.1f}" r="4" class="dot {cls}"><title>{html.escape(tip)}</title></circle>')
    svg = f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{c["seg"]} 累计涵盖曲线">{"".join(g)}</svg>'
    chips = "".join(f'<span title="{html.escape(r["rev_new"] or "")}">{r["k"]}{WORTH.get(r["worth"], "?")}{html.escape(r["rev_case"] or "")}</span>' for r in rows)
    return (f'<figure><figcaption><b>{c["seg"]}</b> 第{c["measures"]}小节 {html.escape(c["label"])} · 约{c["seconds"]}秒'
            f'<br><small>审稿清单 {c["n_rev_experiences"]} 条（核心 {c["n_core"]}）｜生成停 {c["gen_stop"]} · 审稿留 {c["rev_keep"]} · 定稿 {c["final_beads"]} 条</small></figcaption>{svg}<div class="chips">{chips}</div></figure>')


page = f"""<!doctype html><html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>语义增益曲线</title><style>
:root{{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--grid:#e4e3df;--s1:#2a78d6;--s2:#eb6834;--card:#ffffff}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#383836;--s1:#3987e5;--s2:#d95926;--card:#222220}}}}
:root[data-theme="dark"]{{--bg:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#383836;--s1:#3987e5;--s2:#d95926;--card:#222220}}
body{{background:var(--bg);color:var(--ink);font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;margin:0;padding:16px}}
main{{max-width:1100px;margin:auto}} .grid-wrap{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}}
figure{{margin:0;background:var(--card);border:1px solid var(--grid);border-radius:8px;padding:10px}}
figcaption{{font-size:13px}} small,.tick,.mlab{{color:var(--ink2);fill:var(--ink2);font-size:10px}}
svg{{width:100%;height:auto}} .grid{{stroke:var(--grid)}} .line{{fill:none;stroke-width:2}} .s1{{stroke:var(--s1)}} .s2{{stroke:var(--s2)}}
.dot{{stroke:var(--card);stroke-width:2}} .dot.s1{{fill:var(--s1)}} .dot.s2{{fill:var(--s2)}}
.m-gen{{stroke:var(--ink2);stroke-dasharray:4 3}} .m-rev{{stroke:var(--ink2);stroke-dasharray:1 3}} .m-fin{{stroke:var(--ink);stroke-width:1.5}}
.chips{{display:flex;flex-wrap:wrap;gap:4px;font-size:11px;color:var(--ink2)}} .chips span{{border:1px solid var(--grid);border-radius:4px;padding:0 4px}}
.legend span{{margin-right:14px}} .sw{{display:inline-block;width:14px;height:3px;vertical-align:middle;margin-right:4px}}
</style></head><body><main>
<h1>《船歌》十四段 · 语义增益曲线</h1>
<p>横轴 k＝按生成者边际价值排序选入的第 k 个侧面；纵轴＝独立审稿者自己从 24 份原稿列出的本段体验清单被累计涵盖的比例（核心 3／有价值 2／次要 1 加权；部分传达计一半）。这是有证据的相对判断，不是客观百分比。竖线：生成者建议停止点、审稿建议保留数、最终 STRUCT 条目数（定稿条目可能合并或改写阶梯候选，不一一对应）。每个点悬停可看候选全文。下方小标签：审稿判定与是否值得多占一次注意力（●值得 ◐勉强 ○不值得）。</p>
<p class="legend"><span><i class="sw" style="background:var(--s1)"></i>加权涵盖</span><span><i class="sw" style="background:var(--s2)"></i>核心体验涵盖</span><span>竖线：虚线＝生成停，点线＝审稿留，实线＝定稿条数</span></p>
<h2>第一次采样（实验链路：gen → rev1/rev2 → final）</h2>
<div class="grid-wrap">{''.join(chart(c) for c in cv)}</div>
<h2>第二次独立采样（生产链路：gen_b → rev1_b/rev2_b → final_b，定稿提示词 final_v2）</h2>
<p>同样的材料、同样的阶梯与审稿提示词，全新会话重跑。生成者停止点两次相差都不超过 1；审稿清单与审稿建议保留数波动更大。定稿条数由 final_v2 的注意力约束决定，全部落在 3–5 条。</p>
<div class="grid-wrap">{''.join(chart(c) for c in cv2)}</div>
<p><small>完整候选文字、来源与逐 k 审稿意见见《A_实验数据/阶梯全文.md》与《阶梯全文_第二次采样.md》。</small></p></main></body></html>"""
(D / "A_语义增益曲线.html").write_text(page, encoding="utf-8")
print("ok", len(page))
