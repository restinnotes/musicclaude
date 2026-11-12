"""Bead graph fixes (user 10-21: "珠子那个修复一下"), on top of the by-kind view the user proposed.
1. kind audit: every item re-judged against written definitions (the build's labels were loose, e.g. "这股情绪一瞬间像是完整地
   打开了，可音乐一边往上争取……" as 声音);
2. alternative audit: each 另一种理解 bead checked against its segment's main bead — only truly incompatible ones stay in the
   alternatives block (e.g. Op.60 S09 B4 "抬头看见夜空" looked compatible);
3. display: verbatim spans that stop at "；" "：" "，" lose that trailing mark (text itself untouched in the JSON).
Inputs: evaluations/beadgraph/bg2_<w>.json. Outputs: bg2_<w>_fixed.json, deliverable/bead_graph/Op6x_珠子图_按种类.md
usage: python beadfix.py"""
import json, re
from collections import Counter
import beadgraph2 as bg, evo

KIND = ("下面是从音乐“珠子”里逐字摘出的条目。请按定义给每条重新标种类（只能选一个，选这一条最主要说的东西）：\n"
        "- 声音：音乐里实际发生了什么——旋律、和声、节奏、力度、音区、声部的变化，没有比喻；\n"
        "- 意象：用一个画面或比喻说声音像什么（水、光、烟花、说话的样子……）；\n"
        "- 身体：身体的感觉或动作（呼吸、心跳、喉咙发紧、握手、失重……）；\n"
        "- 处境：一个人所处的情境或正在做的事（对人说话、谈往事、坐在船上……）；\n"
        "- 心理：情绪、念头、心里的状态（舍不得、不安、想说又不敢……）。\n"
        "一条里既有声音又有“像……”的比喻，算意象；既有动作又有情绪，看哪一个是这句话的重心。\n"
        "只输出一个 ```json 代码块：{\"条目编号\": \"种类\", ...}，包括全部条目。\n\n")
ALT = ("下面是同一段音乐的珠子：先是这一段的主体验，然后是几颗被标成“另一种理解”的珠子。“另一种理解”的意思是：它和主体验不能同时成立，"
       "听者只能二选一（例如同一段材料被认成两种不同的东西，同一记和弦被听成决定或惊醒）。请逐颗判断：真的不能同时成立（互斥），"
       "还是其实可以和主体验同时感受到（可同时）？只输出一个 ```json 代码块：{\"B4\": \"互斥\", \"B5\": \"可同时\"}\n\n")


def tidy(t):
    return re.sub(r"[；;：:，,、]+$", "。", t.strip())


if __name__ == "__main__":
    jobs = []
    for w in bg.SRC:
        j = json.loads((bg.OUT / f"bg2_{w}.json").read_text(encoding="utf-8"))["items"]
        lst = [(f"{seg}-{bid}-{k + 1}", it["text"]) for seg, beads in j.items() for bid, its in beads.items() for k, it in enumerate(its)]
        if not evo.done(f"bfix_kind_{w}"):
            jobs.append((f"bfix_kind_{w}", (lambda w=w, lst=lst: evo.call(f"bfix_kind_{w}", KIND + "\n".join(f"{i}：{t}" for i, t in lst), prompt_text=KIND, model=evo.G56, meta={"stage": "bead_kind_audit"}))))
        for s in bg.struct(w):
            alts = [b for b in s["beads"] if b["role"] == "另一种理解"]; main = [b for b in s["beads"] if b["role"] == "主体验"]
            if alts and main and not evo.done(f"bfix_alt_{w}_{s['segment']}"):
                msg = ALT + f"主体验 {main[0]['id']}：{main[0]['text']}\n\n" + "\n\n".join(f"{b['id']}（另一种理解）：{b['text']}" for b in alts)
                jobs.append((f"bfix_alt_{w}_{s['segment']}", (lambda rid=f"bfix_alt_{w}_{s['segment']}", msg=msg: evo.call(rid, msg, prompt_text=ALT, model=evo.G56, meta={"stage": "bead_alt_audit"}))))
    evo.run_parallel(jobs, 6)
    for w in bg.SRC:
        j = json.loads((bg.OUT / f"bg2_{w}.json").read_text(encoding="utf-8"))["items"]
        kinds = evo.parse_json(evo.output(f"bfix_kind_{w}")); changed = Counter()
        for seg, beads in j.items():
            for bid, its in beads.items():
                for k, it in enumerate(its):
                    new = kinds.get(f"{seg}-{bid}-{k + 1}")
                    if new in bg.KINDS and new != it.get("kind"):
                        changed[f"{it.get('kind')}→{new}"] += 1; it["kind_before_audit"] = it.get("kind"); it["kind"] = new
                    it["text_display"] = tidy(it["text"])
        compatible = []
        for s in bg.struct(w):
            r = evo.output(f"bfix_alt_{w}_{s['segment']}")
            if r:
                for bid, v in evo.parse_json(r).items():
                    if v == "可同时":
                        compatible.append(f"{s['segment']} {bid}")
        (bg.OUT / f"bg2_{w}_fixed.json").write_text(json.dumps({"items": j, "alt_compatible": compatible}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(w, "kind changes", dict(changed), "| 另一种理解 judged compatible:", compatible, flush=True)
