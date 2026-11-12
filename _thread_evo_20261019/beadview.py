"""Bead graph view from the bead pipeline's own STRUCT (user 10-21: "bead 拆完了感觉好像也没有很多珠子？这是多少份稿子来搞出来的").
beadgraph.py had cut the condensed reader (D3), losing most beads, and guessed A/B/C readings that were mostly not exclusive.
The STRUCT (24 source drafts -> pool -> select -> 2 reviews -> final) already holds every bead with role, measures, placement
and pairwise relations (段内先后 / 重叠但新增 / 可同时成立 / 另一种理解). This only renders it — no model, no rewriting.
usage: python beadview.py   -> deliverable/bead_graph/Op60_珠子图.md, Op61_珠子图.md"""
import glob, json
import evo

SRC = {"op60": evo.ROOT / "inputs" / "pkg" / "03_Bead机器可读", "op61": evo.ROOT.parent / "_bead_op61_20261020" / "deliverable" / "03_Bead机器可读"}
ORDER = ("主体验", "段内变化", "另一侧面", "另一种理解", "演奏条件")
REL = {"段内先后": "→ 接着", "重叠但新增": "＋ 在它上面多了", "可同时成立": "∥ 可同时", "另一种理解": "≠ 另一种理解（不能同时成立）"}

if __name__ == "__main__":
    out = evo.ROOT / "deliverable" / "bead_graph"; out.mkdir(parents=True, exist_ok=True)
    for w, d in SRC.items():
        md = [f"# {'Op.60' if w == 'op60' else 'Op.61'}｜珠子图", "",
              "每颗珠子都是珠子流程定稿的原文（24 份来源稿 → 汇池 → 精选 → 两轮审稿 → 定稿），这里只排版，不改字。",
              "角色：主体验 / 段内变化 / 另一侧面（可与主体验同时成立）/ 另一种理解（与某颗不能同时成立）。下面列出原流程标注的两两关系。", ""]
        n = 0
        for f in sorted(glob.glob(str(d / "S*.json"))):
            s = json.loads(open(f, encoding="utf-8").read()); B = {b["id"]: b for b in s["beads"]}
            md += [f"### {s['segment']} · {s['mm_start']}–{s['mm_end']} · {s['title']}", ""]
            for role in ORDER:
                for b in [b for b in s["beads"] if b["role"] == role]:
                    n += 1; m = (b.get("measures") or "").split("（")[0]
                    md += [f"- **{b['id']}｜{role}**（{m}）{b['text']}"]
            rels = [f"{r['a']} {REL.get(r['type'], r['type'])} {r['b']}" for r in s.get("relations") or []]
            if rels:
                md += ["", "关系：" + "；".join(rels)]
            md.append("")
        p = out / f"{'Op60' if w == 'op60' else 'Op61'}_珠子图.md"; p.write_text("\n".join(md), encoding="utf-8"); print(w, n, "beads ->", p)
