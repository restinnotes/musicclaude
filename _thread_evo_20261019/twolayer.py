"""Two layers (my proposal after adv_r1 + CZ1/SK_chk2): the full structured line (st_, 85-97% skeleton coverage) stays
as an internal layer for video production; a show layer per segment = one natural headline + at most one link line
(prefer 'which earlier experience still acts now'). ids: tl_<t>_r<j>; pseudo-run tls_<t>_r<j> holds the rendered show layer.
outputs: evaluations/twolayer/<id>.json (both layers) + _show.md + _full.md"""
import json, re, sys
from pathlib import Path
import evo, fmt4, node2b, plain, stateinc, structured

OUT = evo.ROOT / "evaluations" / "twolayer"
TL = ("下面是一份完整的结构化线稿（内部层），保留了全部因果、前史和认识变化，供视频制作参考，它不会被改动。"
      "请为它写“显示层”——观众在视频里看到/听到的部分，要一眼就懂：\n"
      "- show_headline：一句话（不超过 30 字），点破他此刻怎么了：其实在怕什么、想要什么、在骗自己什么。用平常说话的语气，具体。\n"
      "- show_link（可选，不超过 35 字）：只写一条最关键的连接，让观众感到这是同一件事一路走来——优先写“哪件较早的经历此刻还在起作用、怎样起作用”"
      "（用自然语言说出那件经历，不要写段号）；没有就写直接前因。weight 为 1 的段落省略。\n"
      "内容只能来自内部层，不得新增。" + stateinc.RULES +
      "只输出一个 ```json 代码块：{\"center\": \"一句人话说清这件事（显示在片头）\", \"segments\": [{\"bars\": \"{FIRST}\", \"show_headline\": \"…\", \"show_link\": \"…\"}]}\n"
      "segments 按顺序覆盖：{BARS}。\n\n========== 内部层 ==========\n")


def threads():
    return [(t, w) for w, ts in plain.THREADS.items() for t in ts]


def build(rid, t, w):
    j = evo.parse_json(evo.output(rid)); full = json.loads((evo.ROOT / "evaluations" / "structured" / f"st_{t}_r1.json").read_text(encoding="utf-8"))
    segs = []
    for a, b in zip(j["segments"], full["segments"]):
        segs.append({"bars": b["bars"], "show": {"headline": a.get("show_headline"), "link": a.get("show_link") or ""},
                     "internal": {k: b.get(k) for k in ("headline", "because", "revises", "toward", "weight")}})
    doc = {"work": w, "center": j.get("center"), "internal_center": full.get("center"), "arc": full.get("arc"), "segments": segs,
           "segments_valid": [s["bars"] for s in j["segments"]] == structured.bars(w),
           "formula": sum(any(re.search(v, s["show"]["headline"] or "") for v in fmt4.PAT.values()) for s in segs)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{rid}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    show = [f"**{doc['center']}**", ""] + sum(([f"### {s['bars']}", "", f"**{s['show']['headline']}**"] + ([s["show"]["link"]] if s["show"]["link"] else []) + [""] for s in segs), [])
    (OUT / f"{rid}_show.md").write_text("\n".join(show), encoding="utf-8")
    (OUT / f"{rid}_full.md").write_text(structured.render(full, f"{rid} 内部层"), encoding="utf-8")
    d = evo.RUNS / f"{rid.split('_')[0]}s_{rid.split('_', 1)[1]}"; d.mkdir(exist_ok=True)
    (d / "output.txt").write_text("\n".join(show), encoding="utf-8")
    (d / "call.log").write_text(json.dumps({"note": f"show layer rendered from {rid}"}), encoding="utf-8")
    print(rid, "valid" if doc["segments_valid"] else "MISMATCH", "formula", doc["formula"], "show chars", len("\n".join(show)), flush=True)


TL2 = TL.replace("- show_link（可选，不超过 35 字）：只写一条最关键的连接", "- show_link（可选，每条不超过 35 字）：weight 为 3 的关键转折段可以写两条（用“；”隔开），其余至多一条。写最关键的连接")
TL2 = TL2.replace("内容只能来自内部层，不得新增。", "内容只能来自内部层，不得新增。尤其不要写成他“开口”“说”“告诉”“问”了谁——内部层的请求、愿望一律写成心理（他想知道、他盼着），除非内部层明确写了他说出口。")
TL3 = TL2.replace("内容只能来自内部层，不得新增。", "内容只能来自内部层，不得新增。显示层绝不能比内部层更确定：内部层里他还说不清、分不清、不确定的，显示层也要保持说不清；"
                  "后面段落才认清的东西，不能提前在前面的段落说出来——这件事是一步步被认清的，开头的“说不清”本身就是内容。")
V2 = len(sys.argv) > 1 and sys.argv[1] in ("v2", "v3")
V3 = len(sys.argv) > 1 and sys.argv[1] == "v3"
PFX = "tl3" if V3 else ("tl2" if V2 else "tl")

if __name__ == "__main__":
    jobs = []
    for t, w in threads():
        src = (evo.ROOT / "evaluations" / "structured" / f"st_{t}_r1.json").read_text(encoding="utf-8")
        for j in (1, 2):
            rid = f"{PFX}_{t}_r{j}"
            if not evo.done(rid):
                jobs.append(node2b.job(rid, stateinc.fill(TL3 if V3 else (TL2 if V2 else TL), w) + src, {"stage": "twolayer", "thread": t}))
    evo.run_parallel(jobs, 4)
    for t, w in threads():
        for j in (1, 2):
            if evo.done(f"{PFX}_{t}_r{j}"):
                build(f"{PFX}_{t}_r{j}", t, w)
